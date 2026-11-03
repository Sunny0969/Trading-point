"""
Unit Tests for Trade Logger Module (trade_log.py)
=================================================
Tests:
1. R-multiple calculation for BUY and SELL
2. PnL points calculation
3. Session categorization (Asia, London, New York, Overlap)
4. CSV logging and reading persistence
"""

import os
import pytest
import pandas as pd
from paper_trading.trade_log import (
    CompletedTrade,
    TradeLogger,
    calculate_r_multiple,
    calculate_pnl_points,
    determine_market_session
)


class TestRMultipleAndPnL:
    """Test mathematical accuracy of R-multiple and point calculations."""

    def test_buy_win_r_multiple(self):
        # Entry = 2600.0, SL = 2590.0 (risk = 10.0), Exit at TP = 2620.0
        r = calculate_r_multiple("BUY", entry=2600.0, exit_p=2620.0, sl=2590.0)
        assert r == 2.0  # +2R gain
        pnl = calculate_pnl_points("BUY", entry=2600.0, exit_p=2620.0)
        assert pnl == 20.0

    def test_buy_loss_r_multiple(self):
        # Entry = 2600.0, SL = 2590.0 (risk = 10.0), Exit at SL = 2590.0
        r = calculate_r_multiple("BUY", entry=2600.0, exit_p=2590.0, sl=2590.0)
        assert r == -1.0  # -1R loss
        pnl = calculate_pnl_points("BUY", entry=2600.0, exit_p=2590.0)
        assert pnl == -10.0

    def test_sell_win_r_multiple(self):
        # Entry = 2700.0, SL = 2715.0 (risk = 15.0), Exit at TP = 2670.0
        r = calculate_r_multiple("SELL", entry=2700.0, exit_p=2670.0, sl=2715.0)
        assert r == 2.0  # +2R gain
        pnl = calculate_pnl_points("SELL", entry=2700.0, exit_p=2670.0)
        assert pnl == 30.0

    def test_sell_loss_r_multiple(self):
        # Entry = 2700.0, SL = 2715.0 (risk = 15.0), Exit at SL = 2715.0
        r = calculate_r_multiple("SELL", entry=2700.0, exit_p=2715.0, sl=2715.0)
        assert r == -1.0  # -1R loss
        pnl = calculate_pnl_points("SELL", entry=2700.0, exit_p=2715.0)
        assert pnl == -15.0


class TestSessionClassification:
    """Test market session assignment based on UTC timestamp."""

    def test_asia_session(self):
        # UTC 03:00 is during Asia session (00:00 - 07:00)
        ts = pd.Timestamp("2026-02-01 03:30:00")
        assert determine_market_session(ts) == "Asia"

    def test_london_session(self):
        # UTC 09:00 is London (07:00 - 13:00)
        ts = pd.Timestamp("2026-02-01 09:15:00")
        assert determine_market_session(ts) == "London"

    def test_overlap_session(self):
        # UTC 14:00 is London / NY Overlap (12:00 - 16:00 UTC)
        ts = pd.Timestamp("2026-02-01 14:30:00")
        assert determine_market_session(ts) == "Overlap"

    def test_new_york_session(self):
        # UTC 18:00 is New York afternoon (16:00 - 21:00)
        ts = pd.Timestamp("2026-02-01 18:00:00")
        assert determine_market_session(ts) == "New York"


class TestCSVLogging:
    """Test CSV persistence of trade log."""

    def test_log_and_read_trades(self, tmp_path):
        csv_file = str(tmp_path / "trades_test.csv")
        logger = TradeLogger(csv_file)

        trade = CompletedTrade(
            trade_id="TRD-001",
            date="2026-02-01",
            time="10:30:00",
            session="London",
            direction="BUY",
            entry=2650.40,
            sl=2635.40,
            tp=2680.40,
            exit=2680.40,
            exit_reason="TP",
            pnl_points=30.00,
            r_multiple=2.0
        )

        logger.log_trade(trade)
        assert os.path.exists(csv_file)

        trades = logger.load_trades()
        assert len(trades) == 1
        t = trades[0]
        assert t.trade_id == "TRD-001"
        assert t.direction == "BUY"
        assert t.session == "London"
        assert t.r_multiple == 2.0
        assert t.exit_reason == "TP"
