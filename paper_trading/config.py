"""
Paper Trading Configuration Module (XAUUSD Gold Engine)
======================================================
Tamam settings aur parameters yahan configure hotay hain.
Koi bhi hardcoded API key ya real broker account number shamil nahi hai.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PaperTradingConfig:
    """Central configuration class for XAUUSD Paper Trading Engine."""

    # Symbol & Timeframes
    symbol: str = "XAUUSD"
    signal_timeframe: str = "15m"   # Signal calculation timeframe (15m bars)
    htf_timeframe: str = "1h"       # Higher timeframe trend filter (1H bars)

    # Indicator Parameters
    fast_ema_period: int = 20       # Fast EMA
    slow_ema_period: int = 50       # Slow EMA
    rsi_period: int = 14            # RSI Period
    rsi_buy_min: float = 50.0       # RSI filter for BUY: must be > 50
    rsi_buy_max: float = 70.0       # RSI filter for BUY: must be < 70
    rsi_sell_min: float = 30.0      # RSI filter for SELL: must be > 30
    rsi_sell_max: float = 50.0      # RSI filter for SELL: must be < 50
    htf_ema_period: int = 50        # 1-Hour Trend Filter EMA (50)

    # ATR Stop Loss & Take Profit Multipliers
    atr_period: int = 14            # ATR Period
    sl_atr_mult: float = 1.5        # Stop Loss = 1.5 * ATR (1.5R initial risk)
    tp_atr_mult: float = 3.0        # Take Profit = 3.0 * ATR (3.0R reward, RR 1:2)

    # Confluence Requirements
    require_fvg: bool = True        # Require 3-candle Fair Value Gap confluence
    fvg_lookback_bars: int = 3      # Check for FVG in the last 3 closed bars

    # Execution & Spread Settings (Virtual Fills)
    spread_usd: float = 0.40        # Spread/slippage in USD ($0.30 - $0.50 range, default $0.40)
    fill_on_next_open: bool = True  # Entry strictly on next candle OPEN (never signal close)

    # Hard Risk Limits
    max_daily_loss_r: float = -3.0  # Max daily loss in R-multiples (default -3.0R)
    max_open_trades: int = 1        # Maximum concurrent open paper trades (default 1)

    # Emergency Kill Switch
    kill_switch: bool = False       # Set to True to immediately halt all new signal processing

    # File Paths
    data_dir: str = "data"
    trade_log_csv: str = os.path.join("data", "paper_trades.csv")
    report_html: str = os.path.join("data", "performance_report.html")
    report_csv: str = os.path.join("data", "performance_summary.csv")

    @property
    def summary_csv(self) -> str:
        return self.report_csv

    def __post_init__(self):
        """Ensure directories exist."""
        os.makedirs(self.data_dir, exist_ok=True)
        # Ensure log directory exists if nested
        log_dir = os.path.dirname(self.trade_log_csv)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)


# Default global configuration instance
DEFAULT_CONFIG = PaperTradingConfig()
