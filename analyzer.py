"""
Market Analyzer module for Forex Pairs.
Aggregates live quotes, OHLC history, and indicators into a rich, structured payload
specifically crafted for Gemini / LLM trading agents.
"""

from typing import Dict, Any, Optional
from forex_client import get_forex_quote, get_forex_ohlc, parse_currency_pair
from indicators import compute_indicators_bundle


def generate_market_analysis(
    pair_or_from: str,
    to_symbol: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Performs full multi-dimensional market analysis on a forex pair.
    Returns clean, structured data designed for Gemini prompts and reasoning.
    """
    from_curr, to_curr = parse_currency_pair(pair_or_from, to_symbol)
    symbol = f"{from_curr}/{to_curr}"

    # 1. Fetch live quote
    quote = get_forex_quote(from_curr, to_curr, api_key=api_key)

    # 2. Fetch daily OHLC candles (compact = ~100 days)
    ohlc = get_forex_ohlc(from_curr, to_curr, timeframe="daily", limit=100, api_key=api_key)
    candles = ohlc["candles"]

    if not candles:
        raise ValueError(f"No candle data available for pair {symbol}")

    # 3. Compute indicators
    indicators = compute_indicators_bundle(candles)

    # 4. Extract price dynamics
    current_price = quote["price"]
    prev_close = candles[-2]["close"] if len(candles) >= 2 else candles[-1]["open"]
    change_points = round(current_price - prev_close, 6)
    change_pct = round((change_points / prev_close) * 100.0, 3) if prev_close else 0.0

    today_candle = candles[-1]
    today_high = max(today_candle["high"], current_price)
    today_low = min(today_candle["low"], current_price)

    # 5. Formulate Bullish / Bearish evidence score
    bullish_signals = []
    bearish_signals = []

    # RSI checks
    rsi_val = indicators["rsi"]["value"]
    if rsi_val is not None:
        if rsi_val >= 70:
            bearish_signals.append(f"RSI is overbought at {rsi_val} (risk of exhaustion or pullback)")
        elif rsi_val <= 30:
            bullish_signals.append(f"RSI is oversold at {rsi_val} (potential value bounce)")
        elif rsi_val > 52:
            bullish_signals.append(f"RSI shows positive momentum at {rsi_val}")
        elif rsi_val < 48:
            bearish_signals.append(f"RSI shows bearish momentum at {rsi_val}")

    # EMA checks
    ema_info = indicators["ema"]
    ema_fast = ema_info.get("ema_12")
    ema_slow = ema_info.get("ema_26")
    ema_50 = ema_info.get("ema_50")

    if ema_fast and ema_slow:
        if ema_fast > ema_slow:
            bullish_signals.append(f"EMA 12 ({ema_fast}) is above EMA 26 ({ema_slow}) [Bullish alignment]")
        else:
            bearish_signals.append(f"EMA 12 ({ema_fast}) is below EMA 26 ({ema_slow}) [Bearish alignment]")

    if ema_slow:
        if current_price > ema_slow:
            bullish_signals.append(f"Current price ({current_price}) is trading above 26-day EMA ({ema_slow})")
        else:
            bearish_signals.append(f"Current price ({current_price}) is trading below 26-day EMA ({ema_slow})")

    if ema_50:
        if current_price > ema_50:
            bullish_signals.append(f"Price is above medium-term EMA 50 ({ema_50})")
        else:
            bearish_signals.append(f"Price is below medium-term EMA 50 ({ema_50})")

    # MACD checks
    macd_info = indicators["macd"]
    macd_stat = macd_info.get("status", "NEUTRAL")
    macd_hist = macd_info.get("histogram")

    if "BULLISH_CROSSOVER" in macd_stat:
        bullish_signals.append("MACD just formed a fresh BULLISH Crossover")
    elif "BEARISH_CROSSOVER" in macd_stat:
        bearish_signals.append("MACD just formed a fresh BEARISH Crossover")
    elif macd_hist is not None and macd_hist > 0:
        bullish_signals.append(f"MACD Histogram is positive (+{macd_hist})")
    elif macd_hist is not None and macd_hist < 0:
        bearish_signals.append(f"MACD Histogram is negative ({macd_hist})")

    # Scoring & Signal determination
    score = len(bullish_signals) - len(bearish_signals)
    total_factors = len(bullish_signals) + len(bearish_signals)

    if score >= 3:
        signal = "STRONG_BUY"
        bias = "Bullish"
        confidence = min(90, 60 + score * 8)
    elif score in (1, 2):
        signal = "BUY"
        bias = "Moderately Bullish"
        confidence = 65
    elif score in (-1, -2):
        signal = "SELL"
        bias = "Moderately Bearish"
        confidence = 65
    elif score <= -3:
        signal = "STRONG_SELL"
        bias = "Bearish"
        confidence = min(90, 60 + abs(score) * 8)
    else:
        signal = "NEUTRAL"
        bias = "Sideways / Range-bound"
        confidence = 50

    return {
        "symbol": symbol,
        "timestamp_utc": quote["last_refreshed"],
        "market_status": {
            "current_price": current_price,
            "bid": quote["bid"],
            "ask": quote["ask"],
            "spread_pips": quote["spread_pips"],
            "change_24h": change_points,
            "change_24h_pct": f"{change_pct:+.2f}%",
            "session_high": today_high,
            "session_low": today_low
        },
        "technical_summary": {
            "signal": signal,
            "bias": bias,
            "confidence_percent": confidence,
            "rsi_14": {
                "value": rsi_val,
                "condition": indicators["rsi"]["condition"]
            },
            "macd": macd_info,
            "emas": {
                "ema_12": ema_fast,
                "ema_26": ema_slow,
                "ema_50": ema_50,
                "ema_200": ema_info.get("ema_200")
            },
            "key_levels": {
                "recent_resistance": indicators["levels"]["resistance_recent"],
                "recent_support": indicators["levels"]["support_recent"],
                "volatility_atr_14": indicators["volatility"]["atr_14"]
            }
        },
        "analysis_factors": {
            "bullish_factors": bullish_signals,
            "bearish_factors": bearish_signals
        },
        "gemini_context": (
            f"Forex pair {symbol} is currently priced at {current_price} ({change_pct:+.2f}%). "
            f"Overall technical stance is {signal} with {confidence}% confidence. "
            f"RSI is {rsi_val} ({indicators['rsi']['condition']}), and MACD histogram is {macd_hist} ({macd_stat}). "
            f"Key support sits near {indicators['levels']['support_recent']} and resistance near {indicators['levels']['resistance_recent']}."
        )
    }
