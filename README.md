# High-Performance Forex & Gold MCP Server (Model Context Protocol)

A fully-functional, institutional-grade local MCP Server that streams real-time Forex and Gold (XAU/USD) market data, computes quantitative technical indicators, and provides structured multi-factor market intelligence for AI models (including **Google Gemini**).

---

## 🛠️ Available MCP Tools

This MCP server provides 4 high-performance quantitative tools for AI agents and automated workflows:

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `get_forex_price` | `pair` (e.g., `"EUR/USD"`, `"XAU/USD"`, `"USDJPY"`), `to_symbol` (optional), `api_key` (optional) | Real-time live exchange rate, bid price, ask price, spread in pips, and synchronized timestamp. |
| `get_forex_candles` | `pair`, `timeframe` (`"daily"`, `"weekly"`, `"monthly"`), `limit` (default: 50) | Historical OHLC (Open, High, Low, Close) candlestick series sorted in chronological order. |
| `calculate_indicators` | `pair`, `rsi_period` (14), `ema_fast` (12), `ema_slow` (26), `macd_signal` (9) | Mathematical quantitative indicators: Wilder's RSI (14), Exponential Moving Averages (EMA 12/26/50/200), MACD line, signal line, histogram, and crossover detection. |
| `analyze_market` | `pair`, `to_symbol` (optional) | Structured market analysis payload: Directional bias (`STRONG_BUY`, `BUY`, `NEUTRAL`, `SELL`, `STRONG_SELL`), algorithmic confidence score, key dynamic support/resistance, ATR volatility, and LLM reasoning summary. |

---

## 📁 Project Architecture

```text
d:\trading code try\
├── server.py                 # Primary MCP Server entry point (Stdio transport)
├── web_server.py             # High-concurrency local HTTP/API server (Port 8080)
├── gold_dashboard.html       # Institutional XAU/USD Terminal & Research Homepage
├── deep_analysis_gold.html   # Dedicated Interactive Technical Terminal view
├── forex_client.py           # Alpha Vantage & TradingView CFD scanner client
├── indicators.py             # Mathematical indicator engines (RSI, EMA, MACD, ATR, Pivots)
├── analyzer.py               # Multi-factor confluence analysis engine
├── test_forex.py             # Automated unit and integration test suite
├── verify_seo_audit.py       # Comprehensive 35-check SEO / AEO / GEO verification suite
├── mcp_config.json           # MCP host configuration specification
├── .env                      # API keys and environment configuration
├── requirements.txt          # Python dependencies
└── run_server.bat            # Quick launch script
```

---

## ⚙️ Configuration & Installation

### 1. Environment Setup
Configure your Alpha Vantage API key in the [`.env`](file:///d:/trading code try/.env) file:
```env
ALPHA_VANTAGE_API_KEY=DUBA4D2VRZNPACZX
```

### 2. Dependency Installation
Install required dependencies into your Python environment:
```powershell
python -m pip install -r requirements.txt
```

---

## 🧪 Automated Testing & Verification

Run the comprehensive test suite to verify all modules and MCP endpoints:

```powershell
python test_forex.py
```

### Verification Coverage:
- **Test 1**: Multi-format Currency Pair Parsing (`EUR/USD`, `gbpusd`, `USD_JPY`, `XAU/USD`) -> **PASSED**
- **Test 2**: Live Price Quote Engine (`get_forex_price`) -> **PASSED**
- **Test 3**: Historical Candlestick Retrieval (`get_forex_candles`) -> **PASSED**
- **Test 4**: Technical Indicator Math (`calculate_indicators`: RSI, EMA, MACD) -> **PASSED**
- **Test 5**: Multi-factor Market Analysis (`analyze_market` for Gemini) -> **PASSED**
- **Test 6**: MCP Server Protocol Handshake (`list_tools` & `call_tool` execution) -> **PASSED**

---

## 🔌 MCP Client Configuration (Gemini / Antigravity / Claude)

Add the following block to your MCP client configuration JSON:

```json
{
  "mcpServers": {
    "forex": {
      "command": "C:\\Users\\SP\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
      "args": [
        "d:\\trading code try\\server.py"
      ],
      "env": {
        "ALPHA_VANTAGE_API_KEY": "DUBA4D2VRZNPACZX"
      }
    }
  }
}
```

---

## ⚡ Core Performance Optimizations

1. **Intelligent Rate Limiter**: Automatically throttles requests and executes exponential backoff to respect free-tier API quotas.
2. **Dual-Tier Caching**: Uses in-memory and persistent disk caching for quotes (60 seconds) and daily candles (10 minutes) to eliminate redundant outbound calls.
3. **Flexible Pair Normalization**: Seamlessly normalizes all input variations (`EUR/USD`, `EURUSD`, `eur_usd`, `GOLD`, `XAUUSD`).
4. **Zero-Latency Terminal Feeds**: Provides direct integration with TradingView CFD feeds for sub-second spot gold pricing.
