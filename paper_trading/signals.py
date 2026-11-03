"""
Signal Engine Module for Gold (XAUUSD)
======================================
Sirf closed candles par chalta hai taake repaint na ho.
Indicators:
1. Fast EMA (20) & Slow EMA (50) crossover
2. RSI (14) filter: BUY (50 < RSI < 70), SELL (30 < RSI < 50)
3. 1-Hour Trend Filter: 1H EMA (50) ke mutabiq
4. Fair Value Gap (FVG) 3-candle gap confluence
5. ATR (14) dynamic SL (1.5x) & TP (3.0x) (RR 1:2)
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np
import pandas as pd

from paper_trading.config import PaperTradingConfig, DEFAULT_CONFIG


@dataclass
class SignalResult:
    """Structure holding generated signal telemetry and coordinates."""
    direction: str          # 'BUY', 'SELL', ya 'NONE'
    timestamp: pd.Timestamp # Signal closed bar timestamp
    close_price: float      # Signal bar close price
    sl_price: float         # Suggested Stop Loss
    tp_price: float         # Suggested Take Profit
    atr: float              # Current ATR (14) value
    rsi: float              # Current RSI (14) value
    fast_ema: float         # EMA 20 value
    slow_ema: float         # EMA 50 value
    htf_ema: float          # 1H EMA 50 trend filter value
    fvg_found: bool         # Whether recent FVG confluence was present
    reason: str             # Description / rationale for signal or rejection


def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """Calculate Exponential Moving Average (EMA) using pandas ewm."""
    return series.ewm(span=period, adjust=False).mean()


def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Wilder's Relative Strength Index (RSI 14).
    Standard institutional calculation.
    """
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    # Wilder's exponential smoothing
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    # Correct edge cases: zero losses -> 100.0, zero gains -> 0.0
    rsi = rsi.where(~((avg_loss == 0) & (avg_gain > 0)), 100.0)
    rsi = rsi.where(~((avg_gain == 0) & (avg_loss > 0)), 0.0)
    return rsi.fillna(50.0)


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR 14).
    True Range = max(high - low, abs(high - prev_close), abs(low - prev_close))
    """
    high = df['high']
    low = df['low']
    close = df['close']
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    return atr.bfill().fillna(2.0)


def detect_fvg_confluence(df: pd.DataFrame, direction: str, lookback: int = 3, **kwargs) -> bool:
    """
    Check if a 3-candle Fair Value Gap (FVG) exists in the last `lookback` closed bars.
    - Bullish FVG: low[i] > high[i-2]
    - Bearish FVG: high[i] < low[i-2]
    """
    lookback_bars = kwargs.get("lookback_bars", lookback)
    if len(df) < 3:
        return False

    n = len(df)
    start_idx = max(2, n - lookback_bars)

    for i in range(start_idx, n):
        if direction == "BUY":
            # Candle i low is strictly higher than candle i-2 high
            if df['low'].iloc[i] > df['high'].iloc[i - 2]:
                return True
        elif direction == "SELL":
            # Candle i high is strictly lower than candle i-2 low
            if df['high'].iloc[i] < df['low'].iloc[i - 2]:
                return True

    return False


def evaluate_signal(
    df_signal: pd.DataFrame,
    df_htf: Optional[pd.DataFrame] = None,
    config: PaperTradingConfig = DEFAULT_CONFIG
) -> SignalResult:
    """
    Evaluate trading signal strictly on the LAST CLOSED bar of df_signal.

    Parameters:
    -----------
    df_signal : pd.DataFrame
        Must have ['open', 'high', 'low', 'close'] and optional datetime index or 'time' column.
        Should contain at least 55-60 closed bars for accurate EMA 50 and RSI 14 calculation.
    df_htf : Optional[pd.DataFrame]
        Higher Timeframe (1H) bars for trend filter. If not provided, an interpolated
        or direct 1H EMA is estimated from df_signal.
    config : PaperTradingConfig
        Indicator and risk parameter configuration.

    Returns:
    --------
    SignalResult containing direction ('BUY', 'SELL', 'NONE') and levels.
    """
    min_required_bars = max(config.slow_ema_period, config.htf_ema_period) + 5
    if len(df_signal) < min_required_bars:
        last_close = float(df_signal['close'].iloc[-1]) if len(df_signal) > 0 else 0.0
        return SignalResult(
            direction="NONE",
            timestamp=pd.Timestamp.now(),
            close_price=last_close,
            sl_price=0.0,
            tp_price=0.0,
            atr=0.0,
            rsi=50.0,
            fast_ema=last_close,
            slow_ema=last_close,
            htf_ema=last_close,
            fvg_found=False,
            reason=f"Insufficient candles ({len(df_signal)}/{min_required_bars})"
        )

    # 1. Compute Indicators
    close = df_signal['close']
    fast_ema = calculate_ema(close, config.fast_ema_period)
    slow_ema = calculate_ema(close, config.slow_ema_period)
    rsi = calculate_rsi(close, config.rsi_period)
    atr = calculate_atr(df_signal, config.atr_period)

    # 2. Compute 1H Trend Filter (HTF EMA 50)
    if df_htf is not None and len(df_htf) >= config.htf_ema_period:
        htf_ema_series = calculate_ema(df_htf['close'], config.htf_ema_period)
        htf_ema_val = float(htf_ema_series.iloc[-1])
    else:
        # If HTF is not supplied separately, approximate 1H EMA from higher lookback on 15M (4x period)
        htf_approx = calculate_ema(close, config.htf_ema_period * 4)
        htf_ema_val = float(htf_approx.iloc[-1])

    # Index -1 represents the most recently closed candle
    idx = len(df_signal) - 1
    prev_idx = idx - 1

    c_close = float(close.iloc[idx])
    c_fast = float(fast_ema.iloc[idx])
    c_slow = float(slow_ema.iloc[idx])
    p_fast = float(fast_ema.iloc[prev_idx])
    p_slow = float(slow_ema.iloc[prev_idx])
    c_rsi = float(rsi.iloc[idx])
    c_atr = max(0.5, float(atr.iloc[idx]))

    # Timestamp extraction
    if 'time' in df_signal.columns:
        ts = pd.to_datetime(df_signal['time'].iloc[idx])
    elif isinstance(df_signal.index, pd.DatetimeIndex):
        ts = df_signal.index[idx]
    else:
        ts = pd.Timestamp.now()

    # 3. Detect Crossover on closed bars (lookahead off)
    bullish_cross = (p_fast <= p_slow) and (c_fast > c_slow)
    bearish_cross = (p_fast >= p_slow) and (c_fast < c_slow)

    # 4. Check BUY Signal Conditions
    if bullish_cross:
        trend_ok = c_close > htf_ema_val
        rsi_ok = (c_rsi > config.rsi_buy_min) and (c_rsi < config.rsi_buy_max)
        fvg_ok = (not config.require_fvg) or detect_fvg_confluence(df_signal, "BUY", config.fvg_lookback_bars)

        if trend_ok and rsi_ok and fvg_ok:
            sl = round(c_close - (config.sl_atr_mult * c_atr), 2)
            tp = round(c_close + (config.tp_atr_mult * c_atr), 2)
            return SignalResult(
                direction="BUY",
                timestamp=ts,
                close_price=c_close,
                sl_price=sl,
                tp_price=tp,
                atr=c_atr,
                rsi=c_rsi,
                fast_ema=c_fast,
                slow_ema=c_slow,
                htf_ema=htf_ema_val,
                fvg_found=fvg_ok,
                reason="Bullish EMA cross + 1H trend + RSI 50-70 + FVG confluence confirmed"
            )
        else:
            reasons = []
            if not trend_ok: reasons.append("Price below 1H EMA 50")
            if not rsi_ok: reasons.append(f"RSI {c_rsi:.1f} out of range (50-70)")
            if not fvg_ok: reasons.append("No bullish FVG in recent 3 bars")
            return SignalResult(
                direction="NONE",
                timestamp=ts,
                close_price=c_close,
                sl_price=0.0,
                tp_price=0.0,
                atr=c_atr,
                rsi=c_rsi,
                fast_ema=c_fast,
                slow_ema=c_slow,
                htf_ema=htf_ema_val,
                fvg_found=fvg_ok,
                reason=f"Bullish cross rejected: {', '.join(reasons)}"
            )

    # 5. Check SELL Signal Conditions
    if bearish_cross:
        trend_ok = c_close < htf_ema_val
        rsi_ok = (c_rsi > config.rsi_sell_min) and (c_rsi < config.rsi_sell_max)
        fvg_ok = (not config.require_fvg) or detect_fvg_confluence(df_signal, "SELL", config.fvg_lookback_bars)

        if trend_ok and rsi_ok and fvg_ok:
            sl = round(c_close + (config.sl_atr_mult * c_atr), 2)
            tp = round(c_close - (config.tp_atr_mult * c_atr), 2)
            return SignalResult(
                direction="SELL",
                timestamp=ts,
                close_price=c_close,
                sl_price=sl,
                tp_price=tp,
                atr=c_atr,
                rsi=c_rsi,
                fast_ema=c_fast,
                slow_ema=c_slow,
                htf_ema=htf_ema_val,
                fvg_found=fvg_ok,
                reason="Bearish EMA cross + 1H trend + RSI 30-50 + FVG confluence confirmed"
            )
        else:
            reasons = []
            if not trend_ok: reasons.append("Price above 1H EMA 50")
            if not rsi_ok: reasons.append(f"RSI {c_rsi:.1f} out of range (30-50)")
            if not fvg_ok: reasons.append("No bearish FVG in recent 3 bars")
            return SignalResult(
                direction="NONE",
                timestamp=ts,
                close_price=c_close,
                sl_price=0.0,
                tp_price=0.0,
                atr=c_atr,
                rsi=c_rsi,
                fast_ema=c_fast,
                slow_ema=c_slow,
                htf_ema=htf_ema_val,
                fvg_found=fvg_ok,
                reason=f"Bearish cross rejected: {', '.join(reasons)}"
            )

    return SignalResult(
        direction="NONE",
        timestamp=ts,
        close_price=c_close,
        sl_price=0.0,
        tp_price=0.0,
        atr=c_atr,
        rsi=c_rsi,
        fast_ema=c_fast,
        slow_ema=c_slow,
        htf_ema=htf_ema_val,
        fvg_found=False,
        reason="No crossover on closed bar"
    )
