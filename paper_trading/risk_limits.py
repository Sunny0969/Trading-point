"""
Risk Limits & Kill Switch Guard Module
======================================
Implements institutional capital protection:
1. MAX_DAILY_LOSS_R (default -3R): stops trading when daily loss limit is hit.
2. MAX_OPEN_TRADES (default 1): strictly prevents concurrent over-exposure.
3. Automatic daily loss reset at date rollover.
4. Emergency Kill Switch: halts engine immediately when activated.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional
import pandas as pd

from paper_trading.config import PaperTradingConfig, DEFAULT_CONFIG

logger = logging.getLogger("PaperEngine.Risk")


class RiskManager:
    """Manages daily loss boundaries, open position limits, and kill switch."""

    def __init__(self, config: PaperTradingConfig = DEFAULT_CONFIG):
        self.config = config
        self.current_date: Optional[str] = None
        self.daily_realized_r: float = 0.0
        self.daily_trades_count: int = 0
        self.kill_switch_active: bool = config.kill_switch

    def check_date_rollover(self, candle_date: str) -> None:
        """
        Check if the trading day has changed.
        If date changes, reset daily loss counter.
        """
        if self.current_date is None:
            self.current_date = candle_date
            self.daily_realized_r = 0.0
            self.daily_trades_count = 0
        elif self.current_date != candle_date:
            logger.info(
                f"[DAILY ROLLOVER] Date changed from {self.current_date} to {candle_date}. "
                f"Resetting daily PnL (Previous Day: {self.daily_realized_r:.2f}R, {self.daily_trades_count} trades)."
            )
            self.current_date = candle_date
            self.daily_realized_r = 0.0
            self.daily_trades_count = 0

    def record_closed_trade_r(self, r_multiple: float, candle_date: str) -> None:
        """Add completed trade's R-multiple to daily tally."""
        self.check_date_rollover(candle_date)
        self.daily_realized_r += r_multiple
        self.daily_trades_count += 1
        logger.info(
            f"[TRADE RECORDED] R: {r_multiple:+.2f}R | Today Total: {self.daily_realized_r:+.2f}R"
        )

    def can_open_new_trade(self, current_open_count: int, candle_date: str) -> tuple[bool, str]:
        """
        Evaluate if a new virtual trade is permitted under hard risk constraints.

        Returns:
        --------
        (is_allowed: bool, reason: str)
        """
        # 1. Kill Switch Check
        if self.config.kill_switch or self.kill_switch_active:
            msg = "[KILL SWITCH ACTIVE] Engine is halted. No new trades permitted."
            logger.warning(msg)
            return False, msg

        # 2. Check Date Rollover
        self.check_date_rollover(candle_date)

        # 3. Maximum Open Trades Check
        if current_open_count >= self.config.max_open_trades:
            msg = f"[RISK LIMIT] Max open trades limit reached ({current_open_count}/{self.config.max_open_trades})."
            logger.warning(msg)
            return False, msg

        # 4. Maximum Daily Loss Limit Check (-3.0R)
        if self.daily_realized_r <= self.config.max_daily_loss_r:
            msg = (
                f"[DAILY LOSS LIMIT] Today loss reached {self.daily_realized_r:.2f}R "
                f"(Max allowed: {self.config.max_daily_loss_r:.2f}R). "
                f"Trading halted for today ({self.current_date}) until next day rollover."
            )
            logger.warning(msg)
            return False, msg

        return True, "Risk checks passed"

    def set_kill_switch(self, state: bool) -> None:
        """Dynamically toggle the kill switch flag."""
        self.kill_switch_active = state
        self.config.kill_switch = state
        if state:
            logger.critical("[KILL SWITCH ENGAGED] All trading activities immediately halted.")
        else:
            logger.info("[KILL SWITCH DISENGAGED] Trading engine resumed.")
