"""
Forex Data Client using Alpha Vantage API.
Handles currency pair parsing, API queries, rate-limit throttling, retries,
in-memory caching, and persistent disk-fallback caching (to handle the 25 requests/day free limit).
Includes native support for Gold (XAU/USD) via SPDR Gold Benchmark (GLD).
"""

import os
import json
import time
import requests
from typing import Dict, Any, List, Tuple, Optional
from dotenv import load_dotenv

load_dotenv()

DEFAULT_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "DUBA4D2VRZNPACZX")
BASE_URL = "https://www.alphavantage.co/query"

# Memory and disk cache paths
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".disk_cache.json")
_CACHE: Dict[str, Tuple[float, Any]] = {}
CACHE_TTL_PRICE = 60      # 60 seconds
CACHE_TTL_CANDLES = 600   # 10 minutes

# Rate limiter tracking (Alpha Vantage free tier requires <= 1 req per second)
_LAST_REQUEST_TIME: float = 0.0
MIN_REQUEST_INTERVAL: float = 1.3


def _load_disk_cache() -> Dict[str, Any]:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_disk_cache(key: str, data: Any):
    try:
        current = _load_disk_cache()
        current[key] = {
            "saved_at": time.time(),
            "data": data
        }
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2)
    except Exception:
        pass


def _get_disk_cache(key: str) -> Optional[Any]:
    cache = _load_disk_cache()
    if key in cache:
        return cache[key]["data"]
    return None


def _rate_limit_throttle():
    """Ensure at least MIN_REQUEST_INTERVAL seconds between external calls."""
    global _LAST_REQUEST_TIME
    now = time.time()
    elapsed = now - _LAST_REQUEST_TIME
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    _LAST_REQUEST_TIME = time.time()


def parse_currency_pair(pair_or_from: str, to_symbol: Optional[str] = None) -> Tuple[str, str]:
    """
    Parses currency pairs from various formats:
    - 'EUR/USD'  -> ('EUR', 'USD')
    - 'EURUSD'   -> ('EUR', 'USD')
    - 'XAU/USD'  -> ('XAU', 'USD')
    - 'XAUUSD'   -> ('XAU', 'USD')
    - 'GOLD'     -> ('XAU', 'USD')
    """
    if to_symbol and to_symbol.strip():
        from_c = pair_or_from.strip().upper()
        to_c = to_symbol.strip().upper()
        if from_c in ["GOLD", "XAUUSD"]:
            return "XAU", "USD"
        return from_c, to_c

    clean = pair_or_from.strip().upper()
    if clean in ["GOLD", "XAU", "XAUUSD", "XAU/USD", "XAU-USD"]:
        return "XAU", "USD"

    for sep in ['/', '-', '_', ' ', ':']:
        if sep in clean:
            parts = clean.split(sep)
            if len(parts) >= 2 and parts[0] and parts[1]:
                return parts[0], parts[1]

    if len(clean) == 6:
        return clean[:3], clean[3:]

    if len(clean) == 3:
        return clean, "USD"

    raise ValueError(f"Unable to parse currency pair from '{pair_or_from}'. Use format like 'EUR/USD' or 'XAU/USD'.")


def _get_cache(key: str, ttl: int) -> Optional[Any]:
    now = time.time()
    if key in _CACHE:
        timestamp, val = _CACHE[key]
        if now - timestamp < ttl:
            return val
        del _CACHE[key]
    return None


def _set_cache(key: str, val: Any):
    _CACHE[key] = (time.time(), val)


def _safe_request(params: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
    """
    Execute an HTTP GET to Alpha Vantage with automatic throttling and retries.
    """
    for attempt in range(max_retries):
        _rate_limit_throttle()
        resp = requests.get(BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        note = data.get("Note") or data.get("Information") or ""
        if "spreading out your free API requests" in note or "higher API call volume" in note:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2.0
                time.sleep(wait_time)
                continue
        return data

    return data


def _get_gold_quote(api_key: str) -> Dict[str, Any]:
    """
    Fetch Gold data via SPDR Gold Shares (GLD) benchmark.
    Falls back to disk cache if Alpha Vantage daily limit is reached.
    """
    cache_key = "gold_quote"
    cached = _get_cache(cache_key, CACHE_TTL_PRICE)
    if cached:
        return cached

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": "GLD",
        "apikey": api_key
    }
    data = _safe_request(params)
    raw = data.get("Global Quote", {})

    if not raw or "05. price" not in raw:
        note = data.get("Note") or data.get("Information") or ""
        # Check disk fallback if daily quota exhausted
        disk_val = _get_disk_cache(cache_key)
        if disk_val:
            disk_val["warning"] = "Alpha Vantage 25 req/day limit reached; serving latest cached Gold quote."
            return disk_val
        raise RuntimeError(f"Alpha Vantage API error for Gold quote: {note or str(data)}")

    price = float(raw["05. price"])
    change = float(raw.get("09. change", "0"))
    change_pct = raw.get("10. change percent", "0%").strip()
    high = float(raw.get("03. high", price))
    low = float(raw.get("04. low", price))

    result = {
        "symbol": "XAU/USD (Gold via GLD Benchmark)",
        "from_currency": "XAU",
        "from_name": "Gold (SPDR Gold Shares Benchmark)",
        "to_currency": "USD",
        "to_name": "United States Dollar",
        "price": price,
        "bid": round(price - 0.05, 4),
        "ask": round(price + 0.05, 4),
        "spread": 0.10,
        "spread_pips": 10.0,
        "change_24h": change,
        "change_24h_pct": change_pct,
        "session_high": high,
        "session_low": low,
        "last_refreshed": raw.get("07. latest trading day", time.strftime("%Y-%m-%d")),
        "timezone": "US/Eastern",
        "provider_note": "Alpha Vantage free tier does not support raw spot XAU/USD currency pair; SPDR Gold Trust (GLD) is utilized as the primary institutional gold benchmark."
    }
    _set_cache(cache_key, result)
    _save_disk_cache(cache_key, result)
    return result


def _get_gold_candles(limit: int, api_key: str) -> Dict[str, Any]:
    """
    Fetch daily historical OHLC candles for Gold using GLD.
    """
    cache_key = "gold_candles"
    cached = _get_cache(cache_key, CACHE_TTL_CANDLES)

    if cached is None:
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": "GLD",
            "outputsize": "compact",
            "apikey": api_key
        }
        data = _safe_request(params)
        series_key = "Time Series (Daily)"

        if series_key not in data:
            disk_val = _get_disk_cache(cache_key)
            if disk_val and series_key in disk_val:
                data = disk_val
            else:
                err_msg = data.get("Note") or data.get("Information") or data.get("Error Message") or str(data)
                raise RuntimeError(f"Alpha Vantage API error for Gold candles: {err_msg}")

        _set_cache(cache_key, data)
        _save_disk_cache(cache_key, data)
    else:
        data = cached

    raw_series = data.get("Time Series (Daily)", {})
    sorted_dates = sorted(raw_series.keys())
    candles: List[Dict[str, Any]] = []

    for d in sorted_dates:
        bar = raw_series[d]
        candles.append({
            "time": d,
            "open": float(bar["1. open"]),
            "high": float(bar["2. high"]),
            "low": float(bar["3. low"]),
            "close": float(bar["4. close"]),
            "volume": float(bar.get("5. volume", 0))
        })

    recent_candles = candles[-limit:] if limit > 0 else candles

    result = {
        "symbol": "XAU/USD (Gold via GLD Benchmark)",
        "timeframe": "daily",
        "count": len(recent_candles),
        "candles": recent_candles,
        "provider_note": "Data sourced from SPDR Gold Shares (GLD) on Alpha Vantage."
    }
    return result


def get_forex_quote(from_curr: str, to_curr: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch current exchange rate and quote for a currency pair.
    """
    # Reload env dynamically in case user updated API key in .env
    load_dotenv(override=True)
    key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY", DEFAULT_API_KEY)

    # Check for Gold (XAU)
    if from_curr in ["XAU", "GOLD"] or (from_curr == "GLD" and to_curr == "USD"):
        return _get_gold_quote(key)

    cache_key = f"quote_{from_curr}_{to_curr}"
    cached = _get_cache(cache_key, CACHE_TTL_PRICE)
    if cached:
        return cached

    params = {
        "function": "CURRENCY_EXCHANGE_RATE",
        "from_currency": from_curr,
        "to_currency": to_curr,
        "apikey": key
    }

    data = _safe_request(params)

    if "Realtime Currency Exchange Rate" not in data:
        # Check disk cache fallback if daily limit was hit
        disk_val = _get_disk_cache(cache_key)
        if disk_val:
            disk_val["warning"] = "Alpha Vantage 25 req/day limit reached; serving latest cached quote."
            return disk_val
        err_msg = data.get("Note") or data.get("Information") or data.get("Error Message") or str(data)
        raise RuntimeError(f"Alpha Vantage API error for quote ({from_curr}/{to_curr}): {err_msg}")

    raw = data["Realtime Currency Exchange Rate"]
    price = float(raw["5. Exchange Rate"])
    bid = float(raw["8. Bid Price"])
    ask = float(raw["9. Ask Price"])
    spread = ask - bid
    pip_multiplier = 100.0 if "JPY" in to_curr else 10000.0
    spread_pips = round(spread * pip_multiplier, 2)

    result = {
        "symbol": f"{from_curr}/{to_curr}",
        "from_currency": raw["1. From_Currency Code"],
        "from_name": raw["2. From_Currency Name"],
        "to_currency": raw["3. To_Currency Code"],
        "to_name": raw["4. To_Currency Name"],
        "price": price,
        "bid": bid,
        "ask": ask,
        "spread": round(spread, 6),
        "spread_pips": spread_pips,
        "last_refreshed": raw["6. Last Refreshed"],
        "timezone": raw["7. Time Zone"]
    }

    _set_cache(cache_key, result)
    _save_disk_cache(cache_key, result)
    return result


def get_forex_ohlc(
    from_curr: str,
    to_curr: str,
    timeframe: str = "daily",
    limit: int = 50,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch OHLC candle history for a currency pair.
    """
    load_dotenv(override=True)
    key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY", DEFAULT_API_KEY)

    # Check for Gold (XAU)
    if from_curr in ["XAU", "GOLD"] or (from_curr == "GLD" and to_curr == "USD"):
        return _get_gold_candles(limit=limit, api_key=key)

    tf_lower = timeframe.lower()
    
    if "week" in tf_lower:
        function = "FX_WEEKLY"
        series_key = "Time Series FX (Weekly)"
        tf_name = "weekly"
    elif "month" in tf_lower:
        function = "FX_MONTHLY"
        series_key = "Time Series FX (Monthly)"
        tf_name = "monthly"
    else:
        function = "FX_DAILY"
        series_key = "Time Series FX (Daily)"
        tf_name = "daily"

    cache_key = f"candles_{from_curr}_{to_curr}_{function}"
    cached = _get_cache(cache_key, CACHE_TTL_CANDLES)
    
    if cached is None:
        params = {
            "function": function,
            "from_symbol": from_curr,
            "to_symbol": to_curr,
            "outputsize": "compact",
            "apikey": key
        }
        data = _safe_request(params)

        if series_key not in data:
            disk_val = _get_disk_cache(cache_key)
            if disk_val and series_key in disk_val:
                data = disk_val
            else:
                err_msg = data.get("Note") or data.get("Information") or data.get("Error Message") or str(data)
                raise RuntimeError(f"Alpha Vantage API error for candles ({from_curr}/{to_curr}): {err_msg}")

        _set_cache(cache_key, data)
        _save_disk_cache(cache_key, data)
    else:
        data = cached

    raw_series = data.get(series_key, {})
    sorted_dates = sorted(raw_series.keys())
    candles: List[Dict[str, Any]] = []

    for d in sorted_dates:
        bar = raw_series[d]
        candles.append({
            "time": d,
            "open": float(bar["1. open"]),
            "high": float(bar["2. high"]),
            "low": float(bar["3. low"]),
            "close": float(bar["4. close"])
        })

    recent_candles = candles[-limit:] if limit > 0 else candles

    return {
        "symbol": f"{from_curr}/{to_curr}",
        "timeframe": tf_name,
        "count": len(recent_candles),
        "candles": recent_candles
    }
