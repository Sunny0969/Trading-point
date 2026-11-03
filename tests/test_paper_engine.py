"""
Unit Tests for Paper Execution Engine (paper_engine.py)
======================================================
Khaas taur par cover karta hai:
1. SL/TP same candle conflict resolution (SL declared first - conservative).
2. Spread adjustment ($0.40 added to BUY open, subtracted from SELL open).
3. Next candle OPEN virtual fills.
4. Normal TP / SL hit detection.
"""

import pytest
import pandas as pd
from paper_trading.config import PaperTradingConfig
from paper_trading.paper_engine import PaperTradingEngine, PendingSignal, VirtualTrade
from paper_trading.risk_limits import RiskManager
from paper_trading.trade_log import TradeLogger


@pytest.fixture
def clean_engine(tmp_path):
    """Fixture providing a fresh isolated PaperTradingEngine instance."""
    log_file = str(tmp_path / "test_trades.csv")
    config = PaperTradingConfig(
        spread_usd=0.40,
        sl_atr_mult=1.5,
        tp_atr_mult=3.0,
        trade_log_csv=log_file
    )
    risk_mgr = RiskManager(config)
    logger = TradeLogger(log_file)
    return PaperTradingEngine(config=config, risk_manager=risk_mgr, trade_logger=logger)


class TestVirtualFillsAndSpreadAdjustment:
    """Test next candle OPEN execution and spread adjustment."""

    def test_buy_entry_spread_adjustment(self, clean_engine):
        # Queued BUY signal from closed bar at $2650.00
        clean_engine.pending_signal = PendingSignal(
            signal_id="SIG-BUY-1",
            direction="BUY",
            signal_time=pd.Timestamp("2026-02-01 10:00:00"),
            signal_close=2650.00,
            raw_sl=2635.00,  # 15.00 risk
            raw_tp=2680.00,  # 30.00 reward
            atr=10.0
        )

        # Next candle opens at $2652.00
        next_candle = pd.Series({
            "time": pd.Timestamp("2026-02-01 10:15:00"),
            "open": 2652.00,
            "high": 2654.00,
            "low": 2651.00,
            "close": 2653.00
        })

        events = clean_engine.on_new_candle(next_candle)

        # Pending signal should be cleared and filled trade active
        assert clean_engine.pending_signal is None
        assert clean_engine.active_trade is not None
        trade = clean_engine.active_trade

        # BUY entry MUST be candle_open + spread (2652.00 + 0.40 = 2652.40)
        assert trade.entry_price == 2652.40
        assert trade.direction == "BUY"
        # SL and TP dynamic adjustment preserving 15.00 risk and 30.00 reward
        assert trade.sl_price == round(2652.40 - 15.00, 2)  # 2637.40
        assert trade.tp_price == round(2652.40 + 30.00, 2)  # 2682.40

    def test_sell_entry_spread_adjustment(self, clean_engine):
        # Queued SELL signal from closed bar at $2700.00
        clean_engine.pending_signal = PendingSignal(
            signal_id="SIG-SELL-1",
            direction="SELL",
            signal_time=pd.Timestamp("2026-02-01 10:00:00"),
            signal_close=2700.00,
            raw_sl=2715.00,  # 15.00 risk
            raw_tp=2670.00,  # 30.00 reward
            atr=10.0
        )

        # Next candle opens at $2698.00
        next_candle = pd.Series({
            "time": pd.Timestamp("2026-02-01 10:15:00"),
            "open": 2698.00,
            "high": 2699.00,
            "low": 2695.00,
            "close": 2696.00
        })

        events = clean_engine.on_new_candle(next_candle)

        assert clean_engine.pending_signal is None
        assert clean_engine.active_trade is not None
        trade = clean_engine.active_trade

        # SELL entry MUST be candle_open - spread (2698.00 - 0.40 = 2697.60)
        assert trade.entry_price == 2697.60
        assert trade.direction == "SELL"
        # SL and TP dynamic adjustment preserving 15.00 risk and 30.00 reward
        assert trade.sl_price == round(2697.60 + 15.00, 2)  # 2712.60
        assert trade.tp_price == round(2697.60 - 30.00, 2)  # 2667.60


class TestSameCandleSLTPConflictResolution:
    """
    CRITICAL TEST: When both SL and TP boundaries are touched within the exact
    same candle, the conservative paper-trading engine MUST assume Stop-Loss
    was hit first. This prevents optimistic bias in backtesting/paper trading.
    """

    def test_buy_trade_same_candle_conflict_favors_sl(self, clean_engine):
        # Active BUY Trade: Entry = 2650.00, SL = 2640.00, TP = 2670.00
        clean_engine.active_trade = VirtualTrade(
            trade_id="TRD-CONFLICT-BUY",
            direction="BUY",
            entry_time=pd.Timestamp("2026-02-01 10:00:00"),
            entry_price=2650.00,
            sl_price=2640.00,
            tp_price=2670.00,
            initial_risk_dist=10.00,
            session="London"
        )

        # Wild candle touching BOTH SL (low=2635 <= 2640) and TP (high=2675 >= 2670)
        volatile_candle = pd.Series({
            "time": pd.Timestamp("2026-02-01 10:15:00"),
            "open": 2650.00,
            "high": 2675.00,  # TP breached!
            "low": 2635.00,   # SL breached!
            "close": 2660.00
        })

        events = clean_engine.on_new_candle(volatile_candle)

        # Active trade must be closed
        assert clean_engine.active_trade is None
        closed = events["closed_trade"]
        assert closed is not None

        # Conservative Rule: Must declare SL hit, NEVER TP
        assert closed.exit_reason == "SL"
        assert closed.exit_price == 2640.00  # SL price
        assert closed.r_multiple == -1.0  # Loss of 1R

    def test_sell_trade_same_candle_conflict_favors_sl(self, clean_engine):
        # Active SELL Trade: Entry = 2700.00, SL = 2710.00, TP = 2680.00
        clean_engine.active_trade = VirtualTrade(
            trade_id="TRD-CONFLICT-SELL",
            direction="SELL",
            entry_time=pd.Timestamp("2026-02-01 10:00:00"),
            entry_price=2700.00,
            sl_price=2710.00,
            tp_price=2680.00,
            initial_risk_dist=10.00,
            session="New York"
        )

        # Wild candle touching BOTH SL (high=2712 >= 2710) and TP (low=2675 <= 2680)
        volatile_candle = pd.Series({
            "time": pd.Timestamp("2026-02-01 10:15:00"),
            "open": 2700.00,
            "high": 2712.00,  # SL breached!
            "low": 2675.00,   # TP breached!
            "close": 2685.00
        })

        events = clean_engine.on_new_candle(volatile_candle)

        assert clean_engine.active_trade is None
        closed = events["closed_trade"]
        assert closed is not None

        # Conservative Rule: Must declare SL hit
        assert closed.exit_reason == "SL"
        assert closed.exit_price == 2710.00
        assert closed.r_multiple == -1.0


class TestNormalExitExecution:
    """Test normal standard TP and SL hits."""

    def test_normal_take_profit_hit(self, clean_engine):
        clean_engine.active_trade = VirtualTrade(
            trade_id="TRD-TP",
            direction="BUY",
            entry_time=pd.Timestamp("2026-02-01 10:00:00"),
            entry_price=2650.00,
            sl_price=2640.00,
            tp_price=2670.00,
            initial_risk_dist=10.00,
            session="London"
        )

        # Candle reaches TP but nowhere near SL
        tp_candle = pd.Series({
            "time": pd.Timestamp("2026-02-01 10:15:00"),
            "open": 2655.00,
            "high": 2672.00,  # > 2670.00
            "low": 2652.00,   # well above 2640.00
            "close": 2671.00
        })

        events = clean_engine.on_new_candle(tp_candle)
        assert clean_engine.active_trade is None
        closed = events["closed_trade"]
        assert closed is not None
        assert closed.exit_reason == "TP"
        assert closed.exit_price == 2670.00
        assert closed.r_multiple == 2.0  # +2R target
        assert closed.pnl_points == 20.00

    def test_normal_stop_loss_hit(self, clean_engine):
        clean_engine.active_trade = VirtualTrade(
            trade_id="TRD-SL",
            direction="BUY",
            entry_time=pd.Timestamp("2026-02-01 10:00:00"),
            entry_price=2650.00,
            sl_price=2640.00,
            tp_price=2670.00,
            initial_risk_dist=10.00,
            session="London"
        )

        # Candle dips to SL
        sl_candle = pd.Series({
            "time": pd.Timestamp("2026-02-01 10:15:00"),
            "open": 2645.00,
            "high": 2646.00,
            "low": 2638.00,   # < 2640.00
            "close": 2639.00
        })

        events = clean_engine.on_new_candle(sl_candle)
        assert clean_engine.active_trade is None
        closed = events["closed_trade"]
        assert closed is not None
        assert closed.exit_reason == "SL"
        assert closed.exit_price == 2640.00
        assert closed.r_multiple == -1.0
        assert closed.pnl_points == -10.00
