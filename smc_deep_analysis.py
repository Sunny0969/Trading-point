"""
DEEP SMC STRATEGY OPTIMIZATION & DIRECTIONAL BREAKDOWN
Analyzing:
1. Long vs Short breakdown
2. Risk-Reward Ratio sensitivity (1:1.5, 1:2.0, 1:2.5, 1:3.0)
3. Break-even stop mechanism (move SL to BE after +1.5R)
4. Longer horizon (2020-2025)
"""

import sys
import numpy as np
import pandas as pd
from smc_historical_backtester import load_data, calculate_indicators, detect_signals

sys.stdout.reconfigure(encoding='utf-8')

def run_simulation_advanced(df, signals, filter_mode='mtf', rr=2.0, spread=0.30, slippage=0.10, risk_buffer=1.5, use_be=True, be_trigger_r=1.0, trade_direction='ALL'):
    total_friction = spread + slippage
    trades = []
    
    n_bars = len(df)
    h = df['high'].values
    l = df['low'].values
    time_arr = df['time'].values
    last_exit_bar = -1

    for s in signals:
        if trade_direction == 'LONG' and s['type'] != 'BULL':
            continue
        if trade_direction == 'SHORT' and s['type'] != 'BEAR':
            continue

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

        fvg_bar = s['idx']
        if fvg_bar <= last_exit_bar:
            continue

        is_bull = (s['type'] == 'BULL')
        mid = s['mid']

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

        initial_sl = sl
        curr_sl = initial_sl
        be_activated = False

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
                # Check BE trigger
                if use_be and not be_activated:
                    if hi >= entry + (be_trigger_r * risk):
                        curr_sl = entry + total_friction # BE+spread
                        be_activated = True

                hit_sl = lo <= curr_sl
                hit_tp = hi >= tp

                if hit_sl and hit_tp:
                    outcome = 0 if be_activated else -1
                    pnl_r = 0.0 if be_activated else -1.0
                    pnl_usd = 0.0 if be_activated else -risk
                    break
                elif hit_sl:
                    outcome = 0 if be_activated else -1
                    pnl_r = 0.0 if be_activated else -1.0
                    pnl_usd = 0.0 if be_activated else -risk
                    break
                elif hit_tp:
                    outcome = 1
                    pnl_r = rr
                    pnl_usd = rr * risk
                    break
            else: # Bearish
                if use_be and not be_activated:
                    if lo <= entry - (be_trigger_r * risk):
                        curr_sl = entry - total_friction
                        be_activated = True

                hit_sl = hi >= curr_sl
                hit_tp = lo <= tp

                if hit_sl and hit_tp:
                    outcome = 0 if be_activated else -1
                    pnl_r = 0.0 if be_activated else -1.0
                    pnl_usd = 0.0 if be_activated else -risk
                    break
                elif hit_sl:
                    outcome = 0 if be_activated else -1
                    pnl_r = 0.0 if be_activated else -1.0
                    pnl_usd = 0.0 if be_activated else -risk
                    break
                elif hit_tp:
                    outcome = 1
                    pnl_r = rr
                    pnl_usd = rr * risk
                    break

        if outcome != 0 or be_activated:
            trades.append({
                'entry_time': time_arr[entry_bar],
                'exit_time': time_arr[exit_bar],
                'type': s['type'],
                'entry': entry,
                'sl': initial_sl,
                'tp': tp,
                'risk': risk,
                'outcome': outcome,
                'be_activated': be_activated,
                'pnl_r': pnl_r,
                'pnl_usd': pnl_usd
            })
            last_exit_bar = exit_bar

    return pd.DataFrame(trades)

def get_stats(trades_df, name):
    if len(trades_df) == 0:
        return {'Name': name, 'Trades': 0, 'Win%': 0, 'BE%': 0, 'Loss%': 0, 'PF': 0, 'Exp(R)': 0, 'Exp($)': 0, 'MaxDD(R)': 0}
    n = len(trades_df)
    wins = trades_df[trades_df['outcome'] == 1]
    bes = trades_df[trades_df['outcome'] == 0]
    losses = trades_df[trades_df['outcome'] == -1]

    w_pct = len(wins) / n * 100
    be_pct = len(bes) / n * 100
    l_pct = len(losses) / n * 100

    gp = wins['pnl_usd'].sum()
    gl = abs(losses['pnl_usd'].sum())
    pf = gp / gl if gl > 0 else 999.0

    exp_r = trades_df['pnl_r'].mean()
    exp_usd = trades_df['pnl_usd'].mean()

    cum_r = trades_df['pnl_r'].cumsum()
    peak_r = cum_r.cummax()
    max_dd = (peak_r - cum_r).max()

    return {
        'Name': name,
        'Trades': n,
        'Win%': round(w_pct, 1),
        'BE%': round(be_pct, 1),
        'Loss%': round(l_pct, 1),
        'PF': round(pf, 2),
        'Exp(R)': round(exp_r, 3),
        'Exp($)': round(exp_usd, 2),
        'MaxDD(R)': round(max_dd, 1)
    }

if __name__ == '__main__':
    # Load 2021-2025 data (4.75 years)
    df = load_data('XAUUSD_15M_all.csv', start_year=2021)
    df = calculate_indicators(df)

    split_idx = int(len(df) * 0.70)
    df_train = df.iloc[:split_idx].copy().reset_index(drop=True)
    df_test = df.iloc[split_idx:].copy().reset_index(drop=True)

    train_signals = detect_signals(df_train)
    test_signals = detect_signals(df_test)

    print("\n" + "="*85)
    print("ANALYSIS 1: R:R RATIO SENSITIVITY (1:1.5 vs 1:2.0 vs 1:2.5 vs 1:3.0) ON OUT-OF-SAMPLE TEST")
    print("="*85)
    rr_results = []
    for rr in [1.5, 2.0, 2.5, 3.0]:
        t_df = run_simulation_advanced(df_test, test_signals, filter_mode='mtf', rr=rr, use_be=False)
        rr_results.append(get_stats(t_df, f"MTF Layer (RR 1:{rr}, No BE)"))
    print(pd.DataFrame(rr_results).to_string(index=False))

    print("\n" + "="*85)
    print("ANALYSIS 2: IMPACT OF BREAK-EVEN STOP (SL to BE at +1.0R, RR 1:2.0)")
    print("="*85)
    be_results = []
    for mode in ['baseline', 'ob', 'mss', 'mtf']:
        t_no_be = run_simulation_advanced(df_test, test_signals, filter_mode=mode, rr=2.0, use_be=False)
        t_be = run_simulation_advanced(df_test, test_signals, filter_mode=mode, rr=2.0, use_be=True, be_trigger_r=1.0)
        be_results.append(get_stats(t_no_be, f"{mode.upper()} (No BE, RR 1:2.0)"))
        be_results.append(get_stats(t_be,    f"{mode.upper()} (+BE@1R, RR 1:2.0)"))
    print(pd.DataFrame(be_results).to_string(index=False))

    print("\n" + "="*85)
    print("ANALYSIS 3: DIRECTIONAL PERFORMANCE (LONGS VS SHORTS) IN OUT-OF-SAMPLE")
    print("="*85)
    dir_results = []
    t_long = run_simulation_advanced(df_test, test_signals, filter_mode='mtf', rr=2.0, use_be=True, trade_direction='LONG')
    t_short = run_simulation_advanced(df_test, test_signals, filter_mode='mtf', rr=2.0, use_be=True, trade_direction='SHORT')
    t_all = run_simulation_advanced(df_test, test_signals, filter_mode='mtf', rr=2.0, use_be=True, trade_direction='ALL')
    dir_results.append(get_stats(t_long,  "MTF LONGS ONLY (with BE)"))
    dir_results.append(get_stats(t_short, "MTF SHORTS ONLY (with BE)"))
    dir_results.append(get_stats(t_all,   "MTF ALL TRADES (with BE)"))
    print(pd.DataFrame(dir_results).to_string(index=False))
