"""
========================================================================================
QUANTITATIVE SMC BACKTEST ENGINE FOR XAUUSD (GOLD)
Dataset: Hugging Face 'ZombitX64/xauusd-gold-price-historical-data-2004-2025'
Timeframe: 15-Minute Candles (Resampled to 4H for Macro Alignment)
Friction: Spread ($0.30) + Slippage ($0.10) = $0.40 per trade
Validation: 70% In-Sample Calibration / 30% Out-of-Sample Forward Walk Test
========================================================================================
"""

import sys
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

def load_clean_data(csv_path='XAUUSD_15M_all.csv', start_year=2021):
    print(f"[*] Loading historical Gold candles from {csv_path} (from {start_year})...")
    df = pd.read_csv(csv_path)
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)
    if start_year:
        df = df[df['time'].dt.year >= start_year].reset_index(drop=True)
    
    # Filter for institutional liquid trading hours (London + NY: 07:00 to 18:00 UTC)
    df['hour'] = df['time'].dt.hour
    df = df[(df['hour'] >= 7) & (df['hour'] <= 18)].reset_index(drop=True)
    print(f"[+] Loaded {len(df):,} liquid 15M bars ({df['time'].min().strftime('%Y-%m-%d')} to {df['time'].max().strftime('%Y-%m-%d')})")
    return df

def apply_institutional_indicators(df):
    # 1. 14-period ATR
    hl = df['high'] - df['low']
    hc = (df['high'] - df['close'].shift(1)).abs()
    lc = (df['low'] - df['close'].shift(1)).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    df['atr'] = tr.rolling(14).mean().bfill()

    # 2. Resample to 4H for Macro Bias (4H EMA 50)
    df_indexed = df.set_index('time')
    df_4h = df_indexed.resample('4h').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    }).dropna()
    df_4h['ema50_4h'] = df_4h['close'].ewm(span=50, adjust=False).mean()
    df_4h['macro_bias_4h'] = np.where(df_4h['close'] > df_4h['ema50_4h'], 1, -1)
    # Shift by 1 bar to guarantee zero lookahead leakage
    df_4h_shifted = df_4h[['macro_bias_4h']].shift(1)
    
    df = df.merge(df_4h_shifted, on='time', how='left')
    df['macro_bias_4h'] = df['macro_bias_4h'].ffill().fillna(0).astype(int)

    # 3. Market Structure Shift (MSS) Swing High/Low (15-bar lookback)
    df['swing_high'] = df['high'].shift(1).rolling(15).max()
    df['swing_low'] = df['low'].shift(1).rolling(15).min()

    return df

def scan_smc_signals(df, min_gap_atr_mult=0.4):
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

        # Bullish FVG
        if l[i] > h[i-2] and (l[i] - h[i-2]) >= min_gap:
            gap_low = h[i-2]
            gap_high = l[i]
            mid = (gap_low + gap_high) / 2.0
            has_ob = (c[i-1] > o[i-1]) and (c[i-2] < o[i-2])
            ob_low = l[i-2] if has_ob else gap_low
            has_mss = (c[i] > swing_hi[i]) or (c[i-1] > swing_hi[i-1])
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

        # Bearish FVG
        elif h[i] < l[i-2] and (l[i-2] - h[i]) >= min_gap:
            gap_low = h[i]
            gap_high = l[i-2]
            mid = (gap_low + gap_high) / 2.0
            has_ob = (c[i-1] < o[i-1]) and (c[i-2] > o[i-2])
            ob_high = h[i-2] if has_ob else gap_high
            has_mss = (c[i] < swing_lo[i]) or (c[i-1] < swing_lo[i-1])
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

def execute_backtest(df, signals, filter_type='trend_fvg', rr=2.0, spread=0.30, slippage=0.10, risk_buffer=1.5):
    total_friction = spread + slippage
    trades = []
    n_bars = len(df)
    h = df['high'].values
    l = df['low'].values
    time_arr = df['time'].values
    last_exit_bar = -1

    for s in signals:
        if filter_type == 'baseline':
            pass
        elif filter_type == 'trend_fvg':
            if not s['macro_ok']:
                continue
        elif filter_type == 'ob':
            if not (s['has_ob'] and s['macro_ok']):
                continue
        elif filter_type == 'full_mtf':
            if not (s['has_ob'] and s['has_mss'] and s['macro_ok']):
                continue

        fvg_bar = s['idx']
        if fvg_bar <= last_exit_bar:
            continue

        is_bull = (s['type'] == 'BULL')
        mid = s['mid']

        # Retest within 50 bars
        entry_bar = -1
        max_search = min(fvg_bar + 50, n_bars)
        for j in range(fvg_bar + 1, max_search):
            if l[j] <= mid <= h[j]:
                entry_bar = j
                break

        if entry_bar == -1:
            continue

        if is_bull:
            entry = mid + total_friction
            sl = (s['ob_low'] if s['has_ob'] else s['gap_low']) - risk_buffer
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
                if lo <= sl and hi >= tp:
                    outcome = -1; pnl_r = -1.0; pnl_usd = -risk; break
                elif lo <= sl:
                    outcome = -1; pnl_r = -1.0; pnl_usd = -risk; break
                elif hi >= tp:
                    outcome = 1; pnl_r = rr; pnl_usd = rr * risk; break
            else:
                if hi >= sl and lo <= tp:
                    outcome = -1; pnl_r = -1.0; pnl_usd = -risk; break
                elif hi >= sl:
                    outcome = -1; pnl_r = -1.0; pnl_usd = -risk; break
                elif lo <= tp:
                    outcome = 1; pnl_r = rr; pnl_usd = rr * risk; break

        if outcome != 0:
            trades.append({
                'entry_time': time_arr[entry_bar],
                'exit_time': time_arr[exit_bar],
                'type': s['type'],
                'entry': round(entry, 2),
                'sl': round(sl, 2),
                'tp': round(tp, 2),
                'risk': round(risk, 2),
                'outcome': outcome,
                'pnl_r': pnl_r,
                'pnl_usd': round(pnl_usd, 2)
            })
            last_exit_bar = exit_bar

    return pd.DataFrame(trades)

def compute_metrics(trades_df, title="Strategy"):
    if len(trades_df) == 0:
        return {'Strategy': title, 'Trades': 0, 'Win Rate': '0%', 'Profit Factor': 0, 'Expectancy (R)': 0, 'Expectancy ($)': 0, 'Max Drawdown (R)': 0}

    n = len(trades_df)
    wins = trades_df[trades_df['outcome'] == 1]
    losses = trades_df[trades_df['outcome'] == -1]

    win_rate = len(wins) / n * 100
    loss_rate = len(losses) / n * 100

    gross_profit = wins['pnl_usd'].sum()
    gross_loss = abs(losses['pnl_usd'].sum())
    pf = gross_profit / gross_loss if gross_loss > 0 else 999.0

    exp_r = trades_df['pnl_r'].mean()
    exp_usd = trades_df['pnl_usd'].mean()

    cum_r = trades_df['pnl_r'].cumsum()
    peak_r = cum_r.cummax()
    max_dd = (peak_r - cum_r).max()

    return {
        'Strategy': title,
        'Trades': n,
        'Wins': len(wins),
        'Losses': len(losses),
        'Win Rate (%)': round(win_rate, 2),
        'Profit Factor': round(pf, 2),
        'Avg Win ($)': round(wins['pnl_usd'].mean(), 2) if len(wins) > 0 else 0,
        'Avg Loss ($)': round(abs(losses['pnl_usd'].mean()), 2) if len(losses) > 0 else 0,
        'Expectancy (R)': round(exp_r, 3),
        'Expectancy ($)': round(exp_usd, 2),
        'Max DD (R)': round(max_dd, 1)
    }

if __name__ == '__main__':
    df = load_clean_data('XAUUSD_15M_all.csv', start_year=2021)
    df = apply_institutional_indicators(df)

    # 70% In-Sample / 30% Out-of-Sample Split (Strict Time-Series Order)
    split_idx = int(len(df) * 0.70)
    df_train = df.iloc[:split_idx].copy().reset_index(drop=True)
    df_test = df.iloc[split_idx:].copy().reset_index(drop=True)

    print("\n" + "="*95)
    print("PHASE 1: 70% IN-SAMPLE CALIBRATION DATA (2021 to May 2024)")
    print("="*95)
    train_signals = scan_smc_signals(df_train)
    m1_train = execute_backtest(df_train, train_signals, filter_type='baseline', rr=2.0)
    m2_train = execute_backtest(df_train, train_signals, filter_type='trend_fvg', rr=2.0)
    m3_train = execute_backtest(df_train, train_signals, filter_type='trend_fvg', rr=2.5)
    m4_train = execute_backtest(df_train, train_signals, filter_type='trend_fvg', rr=3.0)

    train_summary = pd.DataFrame([
        compute_metrics(m1_train, '1. Pure FVG Retest (RR 1:2.0)'),
        compute_metrics(m2_train, '2. 4H Trend-Aligned FVG (RR 1:2.0) [RECOMMENDED]'),
        compute_metrics(m3_train, '3. 4H Trend-Aligned FVG (RR 1:2.5)'),
        compute_metrics(m4_train, '4. 4H Trend-Aligned FVG (RR 1:3.0)')
    ])
    print(train_summary.to_string(index=False))

    print("\n" + "="*95)
    print("PHASE 2: 30% OUT-OF-SAMPLE FORWARD WALK TEST (May 2024 to September 2025) - ZERO LEAKAGE")
    print("="*95)
    test_signals = scan_smc_signals(df_test)
    m1_test = execute_backtest(df_test, test_signals, filter_type='baseline', rr=2.0)
    m2_test = execute_backtest(df_test, test_signals, filter_type='trend_fvg', rr=2.0)
    m3_test = execute_backtest(df_test, test_signals, filter_type='trend_fvg', rr=2.5)
    m4_test = execute_backtest(df_test, test_signals, filter_type='trend_fvg', rr=3.0)

    test_summary = pd.DataFrame([
        compute_metrics(m1_test, '1. Pure FVG Retest (RR 1:2.0)'),
        compute_metrics(m2_test, '2. 4H Trend-Aligned FVG (RR 1:2.0) [RECOMMENDED]'),
        compute_metrics(m3_test, '3. 4H Trend-Aligned FVG (RR 1:2.5)'),
        compute_metrics(m4_test, '4. 4H Trend-Aligned FVG (RR 1:3.0)')
    ])
    print(test_summary.to_string(index=False))
