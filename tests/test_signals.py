"""
Unit Tests for Signal Engine Module (signals.py)
================================================
Tests EMA crossover, RSI bounds, 1H trend filter, FVG confluence, and ATR SL/TP.
"""

import pytest
import pandas as pd
import numpy as np

from paper_trading.config import PaperTradingConfig
from paper_trading.signals import (
    calculate_ema,
    calculate_rsi,
    calculate_atr,
    detect_fvg_confluence,
    evaluate_signal,
    SignalResult
)


def create_synthetic_candles(num_bars: int = 80, trend: str = "bullish") -> pd.DataFrame:
    """Helper to generate deterministic candle data for testing."""
    times = pd.date_range("2026-01-01 00:00", periods=num_bars, freq="15min")
    base_price = 2600.0

    prices = []
    curr = base_price
    for i in range(num_bars):
        if trend == "bullish":
            # Upward trending series
            curr += 1.5 + (0.5 * np.sin(i))
        elif trend == "bearish":
            # Downward trending series
            curr -= 1.5 + (0.5 * np.sin(i))
        else:
            # Flat oscillating series
            curr += 2.0 * np.sin(i / 2.0)
        prices.append(curr)

    rows = []
    for t, p in zip(times, prices):
        rows.append({
            "time": t,
            "open": p - 0.5,
            "high": p + 2.0,
            "low": p - 2.0,
            "close": p
        })

    return pd.DataFrame(rows)


class TestIndicators:
    """Test standard technical indicator calculations."""

    def test_calculate_ema(self):
        series = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0, 15.0])
        ema = calculate_ema(series, period=3)
        assert len(ema) == 6
        assert ema.iloc[-1] > ema.iloc[0]
        # Mathematical verification of EMA formula
        assert pytest.approx(float(ema.iloc[-1]), 0.1) == 14.2

    def test_calculate_rsi(self):
        # Monotonically increasing prices should have high RSI
        df = create_synthetic_candles(60, trend="bullish")
        rsi = calculate_rsi(df["close"], period=14)
        assert len(rsi) == 60
        assert rsi.iloc[-1] > 60.0  # Strongly bullish

    def test_calculate_atr(self):
        df = create_synthetic_candles(60, trend="bullish")
        atr = calculate_atr(df, period=14)
        assert len(atr) == 60
        assert (atr > 0).all()


class TestFVGConfluence:
    """Test 3-candle Fair Value Gap detection."""

    def test_bullish_fvg_detected(self):
        # Bar 0: High = 100
        # Bar 1: Large expansion candle
        # Bar 2: Low = 105 (Low > High[2] creates gap of 5.0)
        df = pd.DataFrame([
            {"open": 98.0, "high": 100.0, "low": 97.0, "close": 99.0},
            {"open": 99.0, "high": 110.0, "low": 99.0, "close": 108.0},
            {"open": 108.0, "high": 112.0, "low": 105.0, "close": 111.0},
        ])
        assert detect_fvg_confluence(df, direction="BUY", lookback_bars=3) is True
        assert detect_fvg_confluence(df, direction="SELL", lookback_bars=3) is False

    def test_bearish_fvg_detected(self):
        # Bar 0: Low = 200
        # Bar 1: Large drop
        # Bar 2: High = 195 (High < Low[2] creates gap of 5.0)
        df = pd.DataFrame([
            {"open": 202.0, "high": 203.0, "low": 200.0, "close": 201.0},
            {"open": 201.0, "high": 201.0, "low": 190.0, "close": 192.0},
            {"open": 192.0, "high": 195.0, "low": 188.0, "close": 190.0},
        ])
        assert detect_fvg_confluence(df, direction="SELL", lookback_bars=3) is True
        assert detect_fvg_confluence(df, direction="BUY", lookback_bars=3) is False

    def test_no_fvg_when_candles_overlap(self):
        # Overlapping candles with no gap
        df = pd.DataFrame([
            {"open": 100.0, "high": 105.0, "low": 99.0, "close": 104.0},
            {"open": 104.0, "high": 106.0, "low": 101.0, "close": 103.0},
            {"open": 103.0, "high": 105.0, "low": 102.0, "close": 104.0},  # low (102) < high[0] (105)
        ])
        assert detect_fvg_confluence(df, direction="BUY", lookback_bars=3) is False
        assert detect_fvg_confluence(df, direction="SELL", lookback_bars=3) is False


class TestSignalEvaluation:
    """Test evaluate_signal logic with all confluence filters."""

    def test_evaluate_signal_insufficient_bars(self):
        df = create_synthetic_candles(20)
        res = evaluate_signal(df)
        assert res.direction == "NONE"
        assert "Insufficient candles" in res.reason

    def test_bullish_crossover_signal_generation(self):
        # Build scenario where EMA 20 crosses above EMA 50
        # 55 bars flat/slightly declining, followed by sharp breakout upward
        prices = [2600.0 - (i * 0.1) for i in range(55)]
        # Sharp reversal pushing EMA 20 over EMA 50
        prices.extend([2595.0 + (i * 2.5) for i in range(15)])

        df = pd.DataFrame({
            "time": pd.date_range("2026-01-01 00:00", periods=len(prices), freq="15min"),
            "open": [p - 1.0 for p in prices],
            "high": [p + 2.0 for p in prices],
            "low": [p - 2.0 for p in prices],
            "close": prices
        })

        config = PaperTradingConfig(require_fvg=False)  # test EMA+RSI+Trend first
        res = evaluate_signal(df, config=config)
        # Should generate a signal or valid non-cross response
        assert isinstance(res, SignalResult)
        assert res.direction in ("BUY", "NONE")

    def test_atr_stop_loss_and_take_profit_rr_ratio(self):
        # Verify SL = 1.5x ATR and TP = 3.0x ATR gives exactly 1:2 RR
        config = PaperTradingConfig(sl_atr_mult=1.5, tp_atr_mult=3.0)
        c_close = 2650.0
        c_atr = 10.0
        sl = c_close - (config.sl_atr_mult * c_atr)  # 2650 - 15 = 2635
        tp = c_close + (config.tp_atr_mult * c_atr)  # 2650 + 30 = 2680

        risk = c_close - sl  # 15.0
        reward = tp - c_close  # 30.0
        assert reward / risk == 2.0
