"""
Local Forex MCP Server
Provides real-time forex quotes, OHLC candle history, technical indicators (RSI, EMA, MACD),
and structured market analysis for Gemini and other LLMs.

Powered by Alpha Vantage and Model Context Protocol (MCP).
"""

import sys
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

# Load environment variables
load_dotenv()

# Import internal modules
from forex_client import get_forex_quote, get_forex_ohlc, parse_currency_pair
from indicators import compute_indicators_bundle
from analyzer import generate_market_analysis

# Initialize the MCP Server
mcp_server = MCPServer(
    name="forex-mcp-server",
    version="1.0.0",
    description="Local Forex MCP Server providing quotes, candles, technical indicators, and Gemini market analysis."
)


@mcp_server.tool(
    name="get_forex_price",
    description="Fetch current live exchange rate, bid price, ask price, and spread for a currency pair (e.g. 'EUR/USD', 'GBPUSD', 'USD/JPY')."
)
def get_forex_price(
    pair: str,
    to_symbol: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get live quote for a forex currency pair.

    Args:
        pair: Currency pair string (e.g., 'EUR/USD', 'EURUSD', or base currency 'EUR').
        to_symbol: Optional quote currency if not supplied in pair (e.g., 'USD').
        api_key: Optional custom Alpha Vantage API key override.
    """
    try:
        from_curr, to_curr = parse_currency_pair(pair, to_symbol)
        quote = get_forex_quote(from_curr, to_curr, api_key=api_key)
        return {
            "status": "success",
            "data": quote
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "pair": pair
        }


@mcp_server.tool(
    name="get_forex_candles",
    description="Fetch OHLC (open, high, low, close) candlestick history for a forex pair. Supports timeframes: 'daily', 'weekly', 'monthly'."
)
def get_forex_candles(
    pair: str,
    to_symbol: Optional[str] = None,
    timeframe: str = "daily",
    limit: int = 50,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get historical candles for a forex pair.

    Args:
        pair: Currency pair string (e.g., 'EUR/USD' or 'USDJPY').
        to_symbol: Optional quote currency if not supplied in pair.
        timeframe: 'daily' (default), 'weekly', or 'monthly'.
        limit: Number of recent candles to retrieve (default: 50).
        api_key: Optional custom Alpha Vantage API key override.
    """
    try:
        from_curr, to_curr = parse_currency_pair(pair, to_symbol)
        data = get_forex_ohlc(
            from_curr=from_curr,
            to_curr=to_curr,
            timeframe=timeframe,
            limit=limit,
            api_key=api_key
        )
        return {
            "status": "success",
            "data": data
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "pair": pair
        }


@mcp_server.tool(
    name="calculate_indicators",
    description="Calculate key technical indicators (RSI, EMA 12/26/50/200, and MACD line/signal/histogram) from historical forex candles."
)
def calculate_indicators(
    pair: str,
    to_symbol: Optional[str] = None,
    rsi_period: int = 14,
    ema_fast: int = 12,
    ema_slow: int = 26,
    macd_signal: int = 9,
    limit: int = 100,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate RSI, EMA, and MACD indicators for a forex pair.

    Args:
        pair: Currency pair string (e.g. 'EUR/USD' or 'GBPUSD').
        to_symbol: Optional quote currency.
        rsi_period: Period for RSI calculation (default: 14).
        ema_fast: Fast EMA period (default: 12).
        ema_slow: Slow EMA period (default: 26).
        macd_signal: MACD signal line period (default: 9).
        limit: Number of candles to use for indicator lookback (default: 100).
        api_key: Optional custom Alpha Vantage API key override.
    """
    try:
        from_curr, to_curr = parse_currency_pair(pair, to_symbol)
        ohlc = get_forex_ohlc(
            from_curr=from_curr,
            to_curr=to_curr,
            timeframe="daily",
            limit=limit,
            api_key=api_key
        )
        candles = ohlc["candles"]
        indicators = compute_indicators_bundle(
            candles=candles,
            rsi_period=rsi_period,
            ema_fast=ema_fast,
            ema_slow=ema_slow,
            macd_signal=macd_signal
        )
        return {
            "status": "success",
            "symbol": f"{from_curr}/{to_curr}",
            "indicators": indicators
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "pair": pair
        }


@mcp_server.tool(
    name="analyze_market",
    description="Generate comprehensive structured forex market analysis designed for Gemini/LLM reasoning, including trends, bias, technical signals (BUY/SELL/NEUTRAL), key support/resistance levels, and bullish/bearish factor breakdowns."
)
def analyze_market(
    pair: str,
    to_symbol: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate deep market analysis for Gemini LLM.

    Args:
        pair: Currency pair string (e.g. 'EUR/USD' or 'USDJPY').
        to_symbol: Optional quote currency.
        api_key: Optional custom Alpha Vantage API key override.
    """
    try:
        analysis = generate_market_analysis(
            pair_or_from=pair,
            to_symbol=to_symbol,
            api_key=api_key
        )
        return {
            "status": "success",
            "analysis": analysis
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "pair": pair
        }


def main():
    """Run the server using stdio transport (standard for MCP clients)."""
    # Force utf-8 encoding on standard streams to avoid Windows cp1252 issues
    if sys.platform == "win32":
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    mcp_server.run(transport="stdio")


if __name__ == "__main__":
    main()
