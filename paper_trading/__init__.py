"""
Paper Trading Engine for XAUUSD (Gold)
=====================================
Pure paper trading & forward-testing engine for Gold algorithmic trading.
Zero broker interaction. Zero real money execution. MT5/broker order_send bilkul nahi hai.

Modules:
- config: Central configuration parameters
- signals: Strategy signal generation (EMA cross, RSI, 1H trend, FVG confluence)
- paper_engine: Virtual execution engine with spread and conservative SL/TP checks
- risk_limits: Hard risk limits (daily loss in R, max open trades, kill switch)
- trade_log: Trade recording with session tagging and R-multiple accounting
- report: Comprehensive statistical analytics and HTML/CSV performance reporting
- live_runner: Live forward testing loop (paper mode only)
"""

from paper_trading.config import PaperTradingConfig, DEFAULT_CONFIG
from paper_trading.signals import (
    SignalResult,
    evaluate_signal,
    calculate_ema,
    calculate_rsi,
    calculate_atr,
    detect_fvg_confluence
)
from paper_trading.trade_log import (
    CompletedTrade,
    TradeLogger,
    determine_market_session,
    calculate_r_multiple,
    calculate_pnl_points
)
from paper_trading.risk_limits import RiskManager
from paper_trading.paper_engine import (
    PaperTradingEngine,
    PendingSignal,
    VirtualTrade
)
from paper_trading.report import (
    PerformanceReporter,
    SessionMetrics,
    StrategyReport
)

__all__ = [
    "PaperTradingConfig",
    "DEFAULT_CONFIG",
    "SignalResult",
    "evaluate_signal",
    "calculate_ema",
    "calculate_rsi",
    "calculate_atr",
    "detect_fvg_confluence",
    "CompletedTrade",
    "TradeLogger",
    "determine_market_session",
    "calculate_r_multiple",
    "calculate_pnl_points",
    "RiskManager",
    "PaperTradingEngine",
    "PendingSignal",
    "VirtualTrade",
    "PerformanceReporter",
    "SessionMetrics",
    "StrategyReport",
]
