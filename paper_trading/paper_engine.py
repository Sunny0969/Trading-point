"""
Paper Trading Virtual Execution Engine
======================================
1. Virtual Fills:
   - Entry strictly on next candle OPEN (never on signal close).
   - Spread Adjustment: default $0.40 added (BUY: open + spread, SELL: open - spread).
2. SL / TP Check:
   - Evaluated against each new candle's High and Low.
   - Conservative Same-Candle Conflict Resolution: If both SL and TP are touched
     in the same candle, SL is considered hit first.
3. Completely isolated: ZERO broker order_send calls, 100% paper trading.
"""

import uuid
import logging
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import pandas as pd

from paper_trading.config import PaperTradingConfig, DEFAULT_CONFIG
from paper_trading.signals import SignalResult, evaluate_signal
from paper_trading.risk_limits import RiskManager
from paper_trading.trade_log import (
    TradeLogger,
    CompletedTrade,
    determine_market_session,
    calculate_r_multiple,
    calculate_pnl_points,
    to_pkt_time,
    to_pkt_date
)

logger = logging.getLogger("PaperEngine.Execution")


@dataclass
class PendingSignal:
    """Queued signal waiting for the next candle OPEN to fill."""
    signal_id: str
    direction: str          # 'BUY' ya 'SELL'
    signal_time: pd.Timestamp
    signal_close: float
    raw_sl: float
    raw_tp: float
    atr: float
    entry_reason: str = ""
    filters_passed: str = ""
    timeframe: str = "15m"
    lot: float = 0.01
    notes: str = ""


@dataclass
class VirtualTrade:
    """Active open paper trade."""
    trade_id: str
    direction: str          # 'BUY' ya 'SELL'
    entry_time: pd.Timestamp
    entry_price: float      # Adjusted with spread
    sl_price: float
    tp_price: float
    initial_risk_dist: float
    session: str
    status: str = "OPEN"    # 'OPEN', 'CLOSED'
    entry_reason: str = ""
    filters_passed: str = ""
    timeframe: str = "15m"
    lot: float = 0.01
    notes: str = ""


class PaperTradingEngine:
    """
    Core virtual execution engine for XAUUSD forward testing.
    Processes live closed candles, queues pending fills, adjusts spreads,
    monitors SL/TP boundaries, and logs completed trades.
    """

    def __init__(
        self,
        config: PaperTradingConfig = DEFAULT_CONFIG,
        risk_manager: Optional[RiskManager] = None,
        trade_logger: Optional[TradeLogger] = None
    ):
        self.config = config
        self.risk_manager = risk_manager or RiskManager(config)
        self.trade_logger = trade_logger or TradeLogger(config.trade_log_csv)

        self.pending_signal: Optional[PendingSignal] = None
        self.active_trade: Optional[VirtualTrade] = None
        self.completed_trades: List[CompletedTrade] = []

    def on_new_candle(
        self,
        current_candle: pd.Series,
        signal_history_df: Optional[pd.DataFrame] = None,
        htf_df: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Event handler called whenever a new candle opens or arrives.

        Execution Sequence:
        -------------------
        1. Fill any pending signal at current_candle.open (with spread adjustment).
        2. Evaluate active trade against current_candle.high and current_candle.low for SL/TP.
        3. If no active trade or pending signal, evaluate signal_history_df for new signal on closed bar.
        """
        # Ensure timestamp parsing
        if 'time' in current_candle:
            c_time = pd.to_datetime(current_candle['time'])
        elif current_candle.name is not None and isinstance(current_candle.name, (pd.Timestamp, str)):
            c_time = pd.to_datetime(current_candle.name)
        else:
            c_time = pd.Timestamp.now()

        c_open = float(current_candle['open'])
        c_high = float(current_candle['high'])
        c_low = float(current_candle['low'])
        c_close = float(current_candle['close'])
        c_date_str = c_time.strftime("%Y-%m-%d")

        events = {
            "candle_time": c_time,
            "filled_trade": None,
            "closed_trade": None,
            "new_signal": None,
            "risk_status": "OK"
        }

        # ---------------------------------------------------------------------
        # STEP 1: Process Pending Fill on Current Candle OPEN
        # ---------------------------------------------------------------------
        if self.pending_signal is not None and self.active_trade is None:
            # Check risk limits before executing fill
            allowed, reason = self.risk_manager.can_open_new_trade(
                current_open_count=0,
                candle_date=c_date_str
            )

            if not allowed:
                logger.warning(f"[PENDING CANCELLED] Signal discarded: {reason}")
                self.pending_signal = None
                events["risk_status"] = reason
            else:
                filled_trade = self._execute_virtual_fill(self.pending_signal, c_open, c_time)
                self.active_trade = filled_trade
                self.pending_signal = None
                events["filled_trade"] = filled_trade

        # ---------------------------------------------------------------------
        # STEP 2: Evaluate SL / TP on Active Trade
        # ---------------------------------------------------------------------
        if self.active_trade is not None:
            closed_record = self._check_trade_exit(self.active_trade, c_high, c_low, c_time)
            if closed_record is not None:
                self.active_trade = None
                self.completed_trades.append(closed_record)
                self.trade_logger.log_trade(closed_record)
                self.risk_manager.record_closed_trade_r(closed_record.r_multiple, closed_record.date)
                events["closed_trade"] = closed_record

        # ---------------------------------------------------------------------
        # STEP 3: Check for Kill Switch
        # ---------------------------------------------------------------------
        if self.config.kill_switch or self.risk_manager.kill_switch_active:
            if self.active_trade is not None:
                # Close active trade under kill switch emergency exit
                close_rec = self._force_close_active_trade(c_close, c_time, "KILL_SWITCH")
                self.active_trade = None
                events["closed_trade"] = close_rec
            self.pending_signal = None
            events["risk_status"] = "KILL_SWITCH_ACTIVE"
            return events

        # ---------------------------------------------------------------------
        # STEP 4: Evaluate New Signal on Closed Candles History
        # ---------------------------------------------------------------------
        if self.active_trade is None and self.pending_signal is None and signal_history_df is not None:
            allowed, reason = self.risk_manager.can_open_new_trade(
                current_open_count=0,
                candle_date=c_date_str
            )
            if allowed:
                sig_result = evaluate_signal(signal_history_df, htf_df, self.config)
                events["new_signal"] = sig_result

                if sig_result.direction in ("BUY", "SELL"):
                    # Build filters_passed string
                    filters_list = ["HTF", "RSI"]
                    if sig_result.fvg_found:
                        filters_list.append("FVG")
                    filters_str = ",".join(filters_list)

                    # Queue for next candle OPEN fill
                    self.pending_signal = PendingSignal(
                        signal_id=f"SIG-{c_time.strftime('%Y%m%d%H%M')}-{uuid.uuid4().hex[:4]}",
                        direction=sig_result.direction,
                        signal_time=sig_result.timestamp,
                        signal_close=sig_result.close_price,
                        raw_sl=sig_result.sl_price,
                        raw_tp=sig_result.tp_price,
                        atr=sig_result.atr,
                        entry_reason=sig_result.reason,
                        filters_passed=filters_str,
                        timeframe=self.config.signal_timeframe,
                        lot=0.01,
                        notes=""
                    )
                    logger.info(
                        f"[SIGNAL QUEUED] {sig_result.direction} at closed price ${sig_result.close_price:.2f}. "
                        f"Will enter on next candle OPEN with ${self.config.spread_usd:.2f} spread adjustment."
                    )
            else:
                events["risk_status"] = reason

        return events

    def _execute_virtual_fill(
        self,
        pending: PendingSignal,
        candle_open: float,
        fill_time: pd.Timestamp
    ) -> VirtualTrade:
        """
        Execute virtual fill at next candle OPEN with spread adjustment.
        - BUY:  entry = open + spread
        - SELL: entry = open - spread
        """
        spread = self.config.spread_usd
        initial_risk_dist = abs(pending.signal_close - pending.raw_sl)
        session = determine_market_session(fill_time)

        if pending.direction == "BUY":
            entry_price = round(candle_open + spread, 2)
            sl_price = round(entry_price - initial_risk_dist, 2)
            tp_price = round(entry_price + (2.0 * initial_risk_dist), 2)
        else:  # SELL
            entry_price = round(candle_open - spread, 2)
            sl_price = round(entry_price + initial_risk_dist, 2)
            tp_price = round(entry_price - (2.0 * initial_risk_dist), 2)

        trade_id = f"TRD-{fill_time.strftime('%m%d%H%M')}-{uuid.uuid4().hex[:4]}"

        trade = VirtualTrade(
            trade_id=trade_id,
            direction=pending.direction,
            entry_time=fill_time,
            entry_price=entry_price,
            sl_price=sl_price,
            tp_price=tp_price,
            initial_risk_dist=initial_risk_dist,
            session=session,
            status="OPEN",
            entry_reason=pending.entry_reason,
            filters_passed=pending.filters_passed,
            timeframe=pending.timeframe,
            lot=pending.lot,
            notes=pending.notes
        )

        logger.info(
            f"[VIRTUAL FILL] #{trade.trade_id} {trade.direction} @ ${trade.entry_price:.2f} "
            f"(Open: ${candle_open:.2f} + Spread: ${spread:.2f}) | "
            f"SL: ${trade.sl_price:.2f} | TP: ${trade.tp_price:.2f} | Session: {session}"
        )
        return trade

    def _check_trade_exit(
        self,
        trade: VirtualTrade,
        candle_high: float,
        candle_low: float,
        candle_time: pd.Timestamp
    ) -> Optional[CompletedTrade]:
        """
        Check if active trade triggered Stop Loss or Take Profit on the current candle.

        CONSERVATIVE CONFLICT RULE:
        If both SL and TP are touched in the SAME candle, SL is considered hit first!
        """
        is_buy = (trade.direction == "BUY")

        sl_touched = (candle_low <= trade.sl_price) if is_buy else (candle_high >= trade.sl_price)
        tp_touched = (candle_high >= trade.tp_price) if is_buy else (candle_low <= trade.tp_price)

        # ---------------------------------------------------------------------
        # CONSERVATIVE RULE: Both touched in same candle -> SL wins (conservative fill)
        # ---------------------------------------------------------------------
        if sl_touched and tp_touched:
            logger.warning(
                f"[SAME-CANDLE CONFLICT] Both SL (${trade.sl_price:.2f}) and TP (${trade.tp_price:.2f}) "
                f"touched on candle [{candle_low:.2f} - {candle_high:.2f}]. "
                f"Applying conservative rule: DECLARING STOP LOSS HIT FIRST."
            )
            return self._build_completed_trade(trade, trade.sl_price, candle_time, "SL")

        # Regular Stop Loss Hit
        if sl_touched:
            logger.info(f"[STOP LOSS HIT] Trade #{trade.trade_id} stopped out @ ${trade.sl_price:.2f}")
            return self._build_completed_trade(trade, trade.sl_price, candle_time, "SL")

        # Regular Take Profit Hit
        if tp_touched:
            logger.info(f"[TAKE PROFIT HIT] Trade #{trade.trade_id} target hit @ ${trade.tp_price:.2f}")
            return self._build_completed_trade(trade, trade.tp_price, candle_time, "TP")

        return None

    def _build_completed_trade(
        self,
        trade: VirtualTrade,
        exit_price: float,
        exit_time: pd.Timestamp,
        reason: str
    ) -> CompletedTrade:
        """Construct a finalized CompletedTrade object matching demo_trades.csv."""
        pnl_points = calculate_pnl_points(trade.direction, trade.entry_price, exit_price)
        r_mult = calculate_r_multiple(trade.direction, trade.entry_price, trade.sl_price, exit_price)
        # Gold 1 lot = 100 oz; 0.01 lot * 100 = $1.00 USD per price point
        pnl_usd = round(pnl_points * (trade.lot * 100.0), 2)

        trade.status = "CLOSED"

        return CompletedTrade(
            trade_id=trade.trade_id,
            date=to_pkt_date(trade.entry_time),
            time_pkt=to_pkt_time(trade.entry_time),
            session=trade.session,
            direction=trade.direction,
            timeframe=trade.timeframe,
            entry_price=round(trade.entry_price, 2),
            sl_price=round(trade.sl_price, 2),
            tp_price=round(trade.tp_price, 2),
            lot=trade.lot,
            exit_price=round(exit_price, 2),
            exit_time_pkt=to_pkt_time(exit_time),
            exit_reason=reason,
            pnl_usd=pnl_usd,
            r_multiple=r_mult,
            entry_reason=trade.entry_reason,
            filters_passed=trade.filters_passed,
            notes=trade.notes
        )

    def _force_close_active_trade(
        self,
        current_price: float,
        exit_time: pd.Timestamp,
        reason: str
    ) -> CompletedTrade:
        """Emergency manual or kill-switch close of active trade at market price."""
        trade = self.active_trade
        completed = self._build_completed_trade(trade, current_price, exit_time, reason)
        self.completed_trades.append(completed)
        self.trade_logger.log_trade(completed)
        self.risk_manager.record_closed_trade_r(completed.r_multiple, completed.date)
        logger.warning(f"[FORCE CLOSE] Trade #{trade.trade_id} closed @ ${current_price:.2f} ({reason})")
        return completed
