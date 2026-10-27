"""
Technical Indicators module for Forex Trading.
Calculates RSI, EMA, MACD, ATR, Support/Resistance, and Market Momentum.
Pure Python implementation with no heavy C-dependencies.
"""

from typing import List, Dict, Any, Optional


def calculate_ema(prices: List[float], period: int) -> List[Optional[float]]:
    """
    Exponential Moving Average (EMA).
    Returns a list of the same length as prices, with None for values before period - 1.
    """
    n = len(prices)
    if n < period or period <= 0:
        return [None] * n

    ema: List[Optional[float]] = [None] * n
    alpha = 2.0 / (period + 1.0)

    # Initial SMA for the first valid period
    sma = sum(prices[:period]) / period
    ema[period - 1] = sma

    for i in range(period, n):
        prev = ema[i - 1]
        assert prev is not None
        ema[i] = (prices[i] * alpha) + (prev * (1.0 - alpha))

    return ema


def calculate_rsi(prices: List[float], period: int = 14) -> List[Optional[float]]:
    """
    Wilder's Relative Strength Index (RSI).
    Standard period is 14.
    """
    n = len(prices)
    if n <= period or period <= 0:
        return [None] * n

    rsi_values: List[Optional[float]] = [None] * n
    deltas = [prices[i] - prices[i - 1] for i in range(1, n)]

    gains = [max(d, 0.0) for d in deltas]
    losses = [max(-d, 0.0) for d in deltas]

    # First average gain and loss
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    if avg_loss == 0.0:
        rsi_values[period] = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi_values[period] = 100.0 - (100.0 / (1.0 + rs))

    # Wilder's smoothing
    for i in range(period + 1, n):
        gain = gains[i - 1]
        loss = losses[i - 1]

        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

        if avg_loss == 0.0:
            rsi_values[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi_values[i] = round(100.0 - (100.0 / (1.0 + rs)), 2)

    return rsi_values


def calculate_macd(
    prices: List[float],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Dict[str, Any]:
    """
    Moving Average Convergence Divergence (MACD).
    Fast EMA (12) - Slow EMA (26), Signal Line (EMA 9 of MACD), Histogram.
    """
    n = len(prices)
    fast_ema = calculate_ema(prices, fast_period)
    slow_ema = calculate_ema(prices, slow_period)

    # Compute MACD line
    macd_line: List[Optional[float]] = [None] * n
    valid_macd_indices = []
    valid_macd_values = []

    for i in range(n):
        if fast_ema[i] is not None and slow_ema[i] is not None:
            val = fast_ema[i] - slow_ema[i]
            macd_line[i] = val
            valid_macd_indices.append(i)
            valid_macd_values.append(val)

    # Signal line is EMA of MACD values
    signal_line: List[Optional[float]] = [None] * n
    histogram: List[Optional[float]] = [None] * n

    if len(valid_macd_values) >= signal_period:
        signal_sub = calculate_ema(valid_macd_values, signal_period)
        for sub_idx, orig_idx in enumerate(valid_macd_indices):
            sig_val = signal_sub[sub_idx]
            signal_line[orig_idx] = sig_val
            if sig_val is not None and macd_line[orig_idx] is not None:
                histogram[orig_idx] = round(macd_line[orig_idx] - sig_val, 6)

    latest_macd = macd_line[-1] if macd_line and macd_line[-1] is not None else None
    latest_signal = signal_line[-1] if signal_line and signal_line[-1] is not None else None
    latest_hist = histogram[-1] if histogram and histogram[-1] is not None else None
    prev_hist = histogram[-2] if len(histogram) >= 2 and histogram[-2] is not None else None

    # Trend and crossover interpretation
    status = "NEUTRAL"
    if latest_hist is not None and prev_hist is not None:
        if prev_hist <= 0 and latest_hist > 0:
            status = "BULLISH_CROSSOVER"
        elif prev_hist >= 0 and latest_hist < 0:
            status = "BEARISH_CROSSOVER"
        elif latest_hist > 0:
            status = "BULLISH"
        elif latest_hist < 0:
            status = "BEARISH"

    return {
        "fast_period": fast_period,
        "slow_period": slow_period,
        "signal_period": signal_period,
        "latest": {
            "macd": round(latest_macd, 6) if latest_macd is not None else None,
            "signal": round(latest_signal, 6) if latest_signal is not None else None,
            "histogram": round(latest_hist, 6) if latest_hist is not None else None,
            "status": status
        },
        "history": {
            "macd": [round(x, 6) if x is not None else None for x in macd_line[-20:]],
            "signal": [round(x, 6) if x is not None else None for x in signal_line[-20:]],
            "histogram": [round(x, 6) if x is not None else None for x in histogram[-20:]]
        }
    }


def calculate_atr(candles: List[Dict[str, Any]], period: int = 14) -> Optional[float]:
    """
    Average True Range (ATR) for measuring volatility.
    """
    if len(candles) < period + 1:
        return None

    true_ranges = []
    for i in range(1, len(candles)):
        h = candles[i]["high"]
        l = candles[i]["low"]
        prev_close = candles[i - 1]["close"]
        tr = max(h - l, abs(h - prev_close), abs(l - prev_close))
        true_ranges.append(tr)

    if len(true_ranges) < period:
        return None

    # Initial ATR is simple average
    atr = sum(true_ranges[:period]) / period
    for i in range(period, len(true_ranges)):
        atr = (atr * (period - 1) + true_ranges[i]) / period

    return round(atr, 6)


def compute_indicators_bundle(
    candles: List[Dict[str, Any]],
    rsi_period: int = 14,
    ema_fast: int = 12,
    ema_slow: int = 26,
    macd_signal: int = 9
) -> Dict[str, Any]:
    """
    Takes OHLC candle list and calculates all major indicators in a single unified bundle.
    """
    if not candles:
        return {"error": "No candles provided"}

    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    latest_close = closes[-1]

    # RSI
    rsi_series = calculate_rsi(closes, period=rsi_period)
    latest_rsi = rsi_series[-1] if rsi_series else None
    
    rsi_condition = "NEUTRAL"
    if latest_rsi is not None:
        if latest_rsi >= 70:
            rsi_condition = "OVERBOUGHT"
        elif latest_rsi <= 30:
            rsi_condition = "OVERSOLD"
        elif latest_rsi >= 55:
            rsi_condition = "BULLISH_MOMENTUM"
        elif latest_rsi <= 45:
            rsi_condition = "BEARISH_MOMENTUM"

    # EMAs
    ema_fast_series = calculate_ema(closes, ema_fast)
    ema_slow_series = calculate_ema(closes, ema_slow)
    ema_50_series = calculate_ema(closes, 50)
    ema_200_series = calculate_ema(closes, 200)

    val_ema_fast = round(ema_fast_series[-1], 6) if ema_fast_series[-1] is not None else None
    val_ema_slow = round(ema_slow_series[-1], 6) if ema_slow_series[-1] is not None else None
    val_ema_50 = round(ema_50_series[-1], 6) if ema_50_series[-1] is not None else None
    val_ema_200 = round(ema_200_series[-1], 6) if ema_200_series[-1] is not None else None

    # MACD
    macd_data = calculate_macd(
        closes,
        fast_period=ema_fast,
        slow_period=ema_slow,
        signal_period=macd_signal
    )

    # ATR
    atr_val = calculate_atr(candles, 14)

    # Support & Resistance (Last 30 periods high & low)
    window_30 = candles[-30:] if len(candles) >= 30 else candles
    resistance_30 = max(c["high"] for c in window_30)
    support_30 = min(c["low"] for c in window_30)

    return {
        "latest_close": latest_close,
        "rsi": {
            "period": rsi_period,
            "value": latest_rsi,
            "condition": rsi_condition
        },
        "ema": {
            f"ema_{ema_fast}": val_ema_fast,
            f"ema_{ema_slow}": val_ema_slow,
            "ema_50": val_ema_50,
            "ema_200": val_ema_200,
            "fast_above_slow": (val_ema_fast > val_ema_slow) if (val_ema_fast and val_ema_slow) else None,
            "price_above_slow": (latest_close > val_ema_slow) if val_ema_slow else None
        },
        "macd": macd_data["latest"],
        "volatility": {
            "atr_14": atr_val
        },
        "levels": {
            "resistance_recent": resistance_30,
            "support_recent": support_30
        }
    }
