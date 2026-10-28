"""
SMC QUANTITATIVE HISTORICAL BACKTEST ENGINE (XAUUSD Gold)
Deterministic mathematical implementation of:
1. Fair Value Gap (FVG)
2. Order Block (OB)
3. Market Structure Shift (MSS / CHoCH)
4. Multi-Timeframe Trend Gate (4H Macro Filter)
5. Out-of-Sample (70/30) Split & Expectancy Metrics
"""

import sys
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

def load_data(filepath='XAUUSD_15M_all.csv', start_year=2022):
    print(f"Loading data from {filepath} (from year {start_year})...")
    df = pd.read_csv(filepath)
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)
    if start_year:
        df = df[df['time'].dt.year >= start_year].reset_index(drop=True)
    print(f"Loaded {len(df):,} bars from {df['time'].min()} to {df['time'].max()}")
    return df

def calculate_indicators(df):
    """Calculate ATR, EMA, and Macro 4H trend"""
    # 1. 15M ATR
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift(1)).abs()
    low_close = (df['low'] - df['close'].shift(1)).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = tr.rolling(14).mean().bfill()

    # 2. Resample to 4H for Macro Bias
    df_indexed = df.set_index('time')
    df_4h = df_indexed.resample('4h').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    }).dropna()
    df_4h['ema50_4h'] = df_4h['close'].ewm(span=50, adjust=False).mean()
    df_4h['macro_bias_4h'] = np.where(df_4h['close'] > df_4h['ema50_4h'], 1, -1)
    # Shift 4h by 1 bar to prevent lookahead leakage into 15m
    df_4h_shifted = df_4h[['macro_bias_4h']].shift(1)
    
    # Merge back to 15M bars
    df = df.merge(df_4h_shifted, on='time', how='left')
    df['macro_bias_4h'] = df['macro_bias_4h'].ffill().fillna(0).astype(int)

    # 3. Rolling Swing Highs and Lows for MSS (Market Structure Shift)
    # 15 bars lookback swing high/low (excluding current candle)
    df['swing_high'] = df['high'].shift(1).rolling(15).max()
    df['swing_low'] = df['low'].shift(1).rolling(15).min()

    return df

def detect_signals(df, min_gap_atr_mult=0.4):
    """
    Deterministic rule scanner:
    - Bullish FVG: low[i] > high[i-2] with gap >= min_gap_atr_mult * ATR
    - Bearish FVG: high[i] < low[i-2] with gap >= min_gap_atr_mult * ATR
    - Order Block (OB): Candle before displacement candle is opposing (bearish for bull OB, bullish for bear OB)
    - Market Structure Shift (MSS): Close breaks prior 15-bar swing high/low
    - Macro 4H Filter: macro_bias_4h == 1 for long, -1 for short
    """
    signals = []
    h = df['high'].values
    l = df['low'].values
    o = df['open'].values
    c = df['close'].values
    atr = df['atr'].values
    macro = df['macro_bias_4h'].values
    swing_hi = df['swing_high'].values
    swing_lo = df['swing_low'].values

    n = len(df)
    for i in range(2, n):
        curr_atr = atr[i]
        min_gap = min_gap_atr_mult * curr_atr

        # --- 1. Bullish FVG ---
        if l[i] > h[i-2] and (l[i] - h[i-2]) >= min_gap:
            gap_low = h[i-2]
            gap_high = l[i]
            mid = (gap_low + gap_high) / 2.0
            
            # Check OB confluence at bar i-1 (the displacement candle origin)
            # Bullish displacement at i-1: candle body was bullish and candle i-2 was bearish
            has_ob = (c[i-1] > o[i-1]) and (c[i-2] < o[i-2])
            ob_low = l[i-2] if has_ob else gap_low

            # Check MSS confluence: close broke swing high recently
            has_mss = (c[i] > swing_hi[i]) or (c[i-1] > swing_hi[i-1])

            # Check MTF Trend Filter
            macro_ok = (macro[i] == 1)

            signals.append({
                'idx': i,
                'time': df['time'].iloc[i],
                'type': 'BULL',
                'gap_low': gap_low,
                'gap_high': gap_high,
                'mid': mid,
                'ob_low': ob_low,
                'has_ob': has_ob,
                'has_mss': has_mss,
                'macro_ok': macro_ok,
                'atr': curr_atr
            })

        # --- 2. Bearish FVG ---
        elif h[i] < l[i-2] and (l[i-2] - h[i]) >= min_gap:
            gap_low = h[i]
            gap_high = l[i-2]
            mid = (gap_low + gap_high) / 2.0

            # Check OB confluence
            has_ob = (c[i-1] < o[i-1]) and (c[i-2] > o[i-2])
            ob_high = h[i-2] if has_ob else gap_high

            # Check MSS confluence: close broke swing low
            has_mss = (c[i] < swing_lo[i]) or (c[i-1] < swing_lo[i-1])

            # Check MTF Trend Filter
            macro_ok = (macro[i] == -1)

            signals.append({
                'idx': i,
                'time': df['time'].iloc[i],
                'type': 'BEAR',
                'gap_low': gap_low,
                'gap_high': gap_high,
                'mid': mid,
                'ob_high': ob_high,
                'has_ob': has_ob,
                'has_mss': has_mss,
                'macro_ok': macro_ok,
                'atr': curr_atr
            })

    return signals

def run_simulation(df, signals, filter_mode='baseline', rr=3.0, spread=0.30, slippage=0.10, risk_buffer=1.5):
    """
    filter_mode:
      - 'baseline': pure FVG
      - 'ob': FVG + Order Block
      - 'mss': FVG + OB + MSS
      - 'mtf': FVG + OB + MSS + Macro 4H Filter
    """
    total_friction = spread + slippage
    trades = []
    
    n_bars = len(df)
    h = df['high'].values
    l = df['low'].values
    time_arr = df['time'].values

    # To avoid overlapping re-entries on same candle
    last_exit_bar = -1

    for s in signals:
        # Filter condition based on mode
        if filter_mode == 'baseline':
            pass
        elif filter_mode == 'ob':
            if not s['has_ob']:
                continue
        elif filter_mode == 'mss':
            if not (s['has_ob'] and s['has_mss']):
                continue
        elif filter_mode == 'mtf':
            if not (s['has_ob'] and s['has_mss'] and s['macro_ok']):
                continue

        # Look for retest of gap midpoint within next 50 bars
        fvg_bar = s['idx']
        if fvg_bar <= last_exit_bar:
            continue

        is_bull = (s['type'] == 'BULL')
        mid = s['mid']
        atr = s['atr']

        entry_bar = -1
        # Check retest window
        max_search = min(fvg_bar + 50, n_bars)
        for j in range(fvg_bar + 1, max_search):
            if l[j] <= mid <= h[j]:
                entry_bar = j
                break

        if entry_bar == -1:
            continue

        # Setup entry, SL, TP
        if is_bull:
            entry = mid + total_friction
            sl = (s['ob_low'] if s['has_ob'] else s['gap_low']) - risk_buffer
            # Ensure minimum SL distance (at least $1.50)
            if entry - sl < 1.50:
                sl = entry - 1.50
            risk = entry - sl
            tp = entry + (rr * risk)
        else:
            entry = mid - total_friction
            sl = (s['ob_high'] if s['has_ob'] else s['gap_high']) + risk_buffer
            if sl - entry < 1.50:
                sl = entry + 1.50
            risk = sl - entry
            tp = entry - (rr * risk)

        # Walk forward through subsequent bars to find outcome
        outcome = 0
        pnl_r = 0.0
        pnl_usd = 0.0
        exit_bar = entry_bar
        max_hold = min(entry_bar + 200, n_bars)

        for k in range(entry_bar + 1, max_hold):
            lo = l[k]
            hi = h[k]
            exit_bar = k

            if is_bull:
                hit_sl = lo <= sl
                hit_tp = hi >= tp
                if hit_sl and hit_tp:
                    # Conservative: worst-case assumption
                    outcome = -1
                    pnl_r = -1.0
                    pnl_usd = -risk
                    break
                elif hit_sl:
                    outcome = -1
                    pnl_r = -1.0
                    pnl_usd = -risk
                    break
                elif hit_tp:
                    outcome = 1
                    pnl_r = rr
                    pnl_usd = rr * risk
                    break
            else: # Bearish
                hit_sl = hi >= sl
                hit_tp = lo <= tp
                if hit_sl and hit_tp:
                    outcome = -1
                    pnl_r = -1.0
                    pnl_usd = -risk
                    break
                elif hit_sl:
                    outcome = -1
                    pnl_r = -1.0
                    pnl_usd = -risk
                    break
                elif hit_tp:
                    outcome = 1
                    pnl_r = rr
                    pnl_usd = rr * risk
                    break

        if outcome != 0:
            trades.append({
                'entry_time': time_arr[entry_bar],
                'exit_time': time_arr[exit_bar],
                'entry_bar': entry_bar,
                'exit_bar': exit_bar,
                'type': s['type'],
                'entry': entry,
                'sl': sl,
                'tp': tp,
                'risk': risk,
                'outcome': outcome,
                'pnl_r': pnl_r,
                'pnl_usd': pnl_usd,
                'bars_held': exit_bar - entry_bar
            })
            last_exit_bar = exit_bar

    return pd.DataFrame(trades)

def evaluate_metrics(trades_df, title="Strategy"):
    if len(trades_df) == 0:
        return {
            'Title': title,
            'Total Trades': 0,
            'Win Rate (%)': 0.0,
            'Profit Factor': 0.0,
            'Expectancy (R)': 0.0,
            'Avg Win ($)': 0.0,
            'Avg Loss ($)': 0.0,
            'Max Drawdown (R)': 0.0
        }

    wins = trades_df[trades_df['outcome'] == 1]
    losses = trades_df[trades_df['outcome'] == -1]
    n_trades = len(trades_df)
    n_wins = len(wins)
    n_losses = len(losses)

    win_rate = (n_wins / n_trades) * 100.0
    loss_rate = (n_losses / n_trades) * 100.0

    gross_profit = wins['pnl_usd'].sum() if n_wins > 0 else 0.0
    gross_loss = abs(losses['pnl_usd'].sum()) if n_losses > 0 else 0.0001
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0

    avg_win_usd = wins['pnl_usd'].mean() if n_wins > 0 else 0.0
    avg_loss_usd = abs(losses['pnl_usd'].mean()) if n_losses > 0 else 0.0

    # Expectancy in R: (Win_Rate * RR) - (Loss_Rate * 1.0)
    # Or mean of pnl_r
    expectancy_r = trades_df['pnl_r'].mean()
    expectancy_usd = trades_df['pnl_usd'].mean()

    # Calculate Max Drawdown in R
    cumulative_r = trades_df['pnl_r'].cumsum()
    peak_r = cumulative_r.cummax()
    drawdown_r = peak_r - cumulative_r
    max_dd_r = drawdown_r.max()

    return {
        'Title': title,
        'Total Trades': n_trades,
        'Wins': n_wins,
        'Losses': n_losses,
        'Win Rate (%)': round(win_rate, 2),
        'Loss Rate (%)': round(loss_rate, 2),
        'Profit Factor': round(profit_factor, 2),
        'Avg Win ($)': round(avg_win_usd, 2),
        'Avg Loss ($)': round(avg_loss_usd, 2),
        'Expectancy (R)': round(expectancy_r, 3),
        'Expectancy ($)': round(expectancy_usd, 2),
        'Max Drawdown (R)': round(max_dd_r, 2)
    }

if __name__ == '__main__':
    df = load_data('XAUUSD_15M_all.csv', start_year=2022)
    df = calculate_indicators(df)
    
    # 70% In-Sample / 30% Out-of-Sample Split (Strict Time-Series Order)
    split_idx = int(len(df) * 0.70)
    df_train = df.iloc[:split_idx].copy().reset_index(drop=True)
    df_test = df.iloc[split_idx:].copy().reset_index(drop=True)

    print(f"\n--- Data Split ---")
    print(f"Total Bars: {len(df):,}")
    print(f"In-Sample (70%):  {len(df_train):,} bars ({df_train['time'].min()} to {df_train['time'].max()})")
    print(f"Out-of-Sample (30%): {len(df_test):,} bars ({df_test['time'].min()} to {df_test['time'].max()})")

    modes = [
        ('baseline', 'Layer 1: Pure FVG Retest'),
        ('ob',       'Layer 2: FVG + Order Block (OB)'),
        ('mss',      'Layer 3: FVG + OB + MSS (Structure Shift)'),
        ('mtf',      'Layer 4: Full MTF (4H Trend + OB + MSS)')
    ]

    print("\n" + "="*80)
    print("IN-SAMPLE RESULTS (70% Calibration Data)")
    print("="*80)
    train_signals = detect_signals(df_train)
    train_results = []
    for mode, name in modes:
        t_df = run_simulation(df_train, train_signals, filter_mode=mode, rr=3.0, spread=0.30, slippage=0.10)
        res = evaluate_metrics(t_df, title=name)
        train_results.append(res)
    print(pd.DataFrame(train_results).to_string(index=False))

    print("\n" + "="*80)
    print("OUT-OF-SAMPLE FORWARD TEST RESULTS (30% Unseen Forward Test - ZERO LEAKAGE)")
    print("="*80)
    test_signals = detect_signals(df_test)
    test_results = []
    for mode, name in modes:
        t_df = run_simulation(df_test, test_signals, filter_mode=mode, rr=3.0, spread=0.30, slippage=0.10)
        res = evaluate_metrics(t_df, title=name)
        test_results.append(res)
    print(pd.DataFrame(test_results).to_string(index=False))
