"""
Unit Tests for Risk Limits & Kill Switch (risk_limits.py)
=========================================================
Tests:
1. MAX_DAILY_LOSS_R (-3.0R) limit blocking new trades
2. Date rollover resetting daily loss back to 0.0R
3. MAX_OPEN_TRADES (1) limiting concurrent trades
4. KILL_SWITCH halting engine immediately
"""

import pytest
from paper_trading.config import PaperTradingConfig
from paper_trading.risk_limits import RiskManager


class TestRiskLimits:
    """Test hard risk limits compliance."""

    def test_max_open_trades_limit(self):
        config = PaperTradingConfig(max_open_trades=1)
        mgr = RiskManager(config)

        # 0 open trades -> allowed
        allowed, reason = mgr.can_open_new_trade(current_open_count=0, candle_date="2026-02-01")
        assert allowed is True
        assert reason == "Risk checks passed"

        # 1 open trade -> blocked
        allowed, reason = mgr.can_open_new_trade(current_open_count=1, candle_date="2026-02-01")
        assert allowed is False
        assert "Max open trades" in reason

    def test_max_daily_loss_limit_blocks_trading(self):
        config = PaperTradingConfig(max_daily_loss_r=-3.0)
        mgr = RiskManager(config)
        date = "2026-02-01"

        # Trade 1: -1R loss
        mgr.record_closed_trade_r(-1.0, candle_date=date)
        assert mgr.daily_realized_r == -1.0
        allowed, _ = mgr.can_open_new_trade(current_open_count=0, candle_date=date)
        assert allowed is True

        # Trade 2: -1R loss (Cumulative -2R)
        mgr.record_closed_trade_r(-1.0, candle_date=date)
        assert mgr.daily_realized_r == -2.0
        allowed, _ = mgr.can_open_new_trade(current_open_count=0, candle_date=date)
        assert allowed is True

        # Trade 3: -1R loss (Cumulative -3R = hit hard limit)
        mgr.record_closed_trade_r(-1.0, candle_date=date)
        assert mgr.daily_realized_r == -3.0

        # Now any further trade on the same date MUST be rejected
        allowed, reason = mgr.can_open_new_trade(current_open_count=0, candle_date=date)
        assert allowed is False
        assert "DAILY LOSS LIMIT" in reason

    def test_daily_loss_resets_on_new_date(self):
        config = PaperTradingConfig(max_daily_loss_r=-3.0)
        mgr = RiskManager(config)

        # Day 1: Max loss hit (-3R)
        day1 = "2026-02-01"
        mgr.record_closed_trade_r(-3.0, candle_date=day1)
        allowed, _ = mgr.can_open_new_trade(current_open_count=0, candle_date=day1)
        assert allowed is False

        # Day 2: Date rollover
        day2 = "2026-02-02"
        allowed, reason = mgr.can_open_new_trade(current_open_count=0, candle_date=day2)
        # Should reset and allow trading
        assert allowed is True
        assert reason == "Risk checks passed"
        assert mgr.daily_realized_r == 0.0

    def test_kill_switch_activation(self):
        config = PaperTradingConfig(kill_switch=False)
        mgr = RiskManager(config)

        # Normal operation
        allowed, _ = mgr.can_open_new_trade(current_open_count=0, candle_date="2026-02-01")
        assert allowed is True

        # Activate kill switch
        mgr.set_kill_switch(True)
        assert mgr.kill_switch_active is True

        # All trades blocked
        allowed, reason = mgr.can_open_new_trade(current_open_count=0, candle_date="2026-02-01")
        assert allowed is False
        assert "KILL SWITCH" in reason

    def test_config_kill_switch_precedence(self):
        # Initialized directly with kill_switch=True in config
        config = PaperTradingConfig(kill_switch=True)
        mgr = RiskManager(config)

        allowed, reason = mgr.can_open_new_trade(current_open_count=0, candle_date="2026-02-01")
        assert allowed is False
        assert "KILL SWITCH" in reason
