"""
Trade Log & Session Tracker Module
==================================
Persists completed paper trades to CSV with institutional telemetry matching demo_trades.csv:
trade_id,date,time_pkt,session,direction,timeframe,entry_price,sl_price,tp_price,
lot,exit_price,exit_time_pkt,exit_reason,pnl_usd,r_multiple,entry_reason,filters_passed,notes
"""

import os
import csv
from typing import List, Optional, Any, Dict
import pandas as pd


class CompletedTrade:
    """Structure representing a completed trade record (matching demo_trades.csv)."""

    def __init__(
        self,
        trade_id: str,
        date: str,
        time_pkt: str = "",
        session: str = "London",
        direction: str = "BUY",
        timeframe: str = "15m",
        entry_price: float = 0.0,
        sl_price: float = 0.0,
        tp_price: float = 0.0,
        lot: float = 0.01,
        exit_price: float = 0.0,
        exit_time_pkt: str = "",
        exit_reason: str = "TP",
        pnl_usd: float = 0.0,
        r_multiple: float = 0.0,
        entry_reason: str = "",
        filters_passed: str = "",
        notes: str = "",
        **kwargs
    ):
        self.trade_id = str(trade_id)
        self.date = str(date)
        self.time_pkt = str(time_pkt or kwargs.get("time", ""))
        self.session = str(session)
        self.direction = str(direction)
        self.timeframe = str(timeframe)
        self.entry_price = float(entry_price or kwargs.get("entry", 0.0))
        self.sl_price = float(sl_price or kwargs.get("sl", 0.0))
        self.tp_price = float(tp_price or kwargs.get("tp", 0.0))
        self.lot = float(lot)
        self.exit_price = float(exit_price or kwargs.get("exit", 0.0))
        self.exit_time_pkt = str(exit_time_pkt or kwargs.get("exit_time", ""))
        self.exit_reason = str(exit_reason)
        # If pnl_usd not explicitly given, fallback to pnl_points
        self.pnl_usd = float(pnl_usd if pnl_usd != 0.0 else kwargs.get("pnl_points", 0.0))
        self.r_multiple = float(r_multiple)
        self.entry_reason = str(entry_reason)
        self.filters_passed = str(filters_passed)
        self.notes = str(notes)

    # Backwards-compatibility properties
    @property
    def entry(self) -> float:
        return self.entry_price

    @property
    def sl(self) -> float:
        return self.sl_price

    @property
    def tp(self) -> float:
        return self.tp_price

    @property
    def exit(self) -> float:
        return self.exit_price

    @property
    def time(self) -> str:
        return self.time_pkt

    @property
    def exit_time(self) -> str:
        return self.exit_time_pkt

    @property
    def pnl_points(self) -> float:
        # 1 lot on Gold = 100 oz. For 0.01 lot, 1 point = $1.00 USD
        if self.lot > 0:
            return round(self.pnl_usd / (self.lot * 100.0), 2)
        return self.pnl_usd


def to_pkt_time(val: Any) -> str:
    """Convert timestamp/datetime to Pakistan Standard Time (PKT, UTC+5) formatted as HH:MM."""
    if val is None or val == "":
        return ""
    try:
        dt = pd.to_datetime(val)
        if dt.tzinfo is None:
            pkt = dt + pd.Timedelta(hours=5)
        else:
            pkt = dt.tz_convert("Asia/Karachi")
        return pkt.strftime("%H:%M")
    except Exception:
        return str(val)[:5]


def to_pkt_date(val: Any) -> str:
    """Convert timestamp/datetime to PKT date formatted as YYYY-MM-DD."""
    if val is None or val == "":
        return ""
    try:
        dt = pd.to_datetime(val)
        if dt.tzinfo is None:
            pkt = dt + pd.Timedelta(hours=5)
        else:
            pkt = dt.tz_convert("Asia/Karachi")
        return pkt.strftime("%Y-%m-%d")
    except Exception:
        return str(val)[:10]


def determine_market_session(dt: pd.Timestamp) -> str:
    """
    Classify trade entry time into institutional market session (UTC):
    - Overlap (London + New York): 12:00 - 16:00 UTC (Maximum liquidity)
    - London: 07:00 - 12:00 UTC
    - New York: 16:00 - 21:00 UTC
    - Asia: 00:00 - 07:00 UTC or 21:00 - 24:00 UTC
    """
    hour = dt.hour + (dt.minute / 60.0)

    if 12.0 <= hour < 16.0:
        return "Overlap"
    elif 7.0 <= hour < 12.0:
        return "London"
    elif 16.0 <= hour < 21.0:
        return "New York"
    else:
        return "Asia"


def calculate_r_multiple(direction: str, entry: float, sl: float, exit_price: Optional[float] = None, **kwargs) -> float:
    """
    Calculate realized R-Multiple:
    - BUY:  (exit - entry) / (entry - SL)
    - SELL: (entry - exit) / (SL - entry)
    """
    if exit_price is None:
        exit_price = kwargs.get("exit_p", kwargs.get("exit", 0.0))

    initial_risk = abs(entry - sl)
    if initial_risk <= 1e-6:
        return 0.0

    if direction == "BUY":
        return round((exit_price - entry) / initial_risk, 2)
    elif direction == "SELL":
        return round((entry - exit_price) / initial_risk, 2)
    return 0.0


def calculate_pnl_points(direction: str, entry: float, exit_price: Optional[float] = None, **kwargs) -> float:
    """
    Calculate net price points gained or lost on the trade.
    - BUY:  exit - entry
    - SELL: entry - exit
    """
    if exit_price is None:
        exit_price = kwargs.get("exit_p", kwargs.get("exit", 0.0))

    if direction == "BUY":
        return round(exit_price - entry, 2)
    elif direction == "SELL":
        return round(entry - exit_price, 2)
    return 0.0


class TradeLogger:
    """Handles logging of completed virtual trades into CSV matching demo_trades.csv."""

    CSV_HEADER = [
        "trade_id", "date", "time_pkt", "session", "direction",
        "timeframe", "entry_price", "sl_price", "tp_price", "lot",
        "exit_price", "exit_time_pkt", "exit_reason", "pnl_usd",
        "r_multiple", "entry_reason", "filters_passed", "notes"
    ]

    def __init__(self, csv_filepath: str):
        self.csv_filepath = csv_filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create CSV and write header if file does not exist."""
        dirname = os.path.dirname(self.csv_filepath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        if not os.path.exists(self.csv_filepath) or os.path.getsize(self.csv_filepath) == 0:
            with open(self.csv_filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.CSV_HEADER)

    def log_trade(self, trade: CompletedTrade) -> None:
        """Append a completed trade record to the CSV file."""
        self._ensure_file_exists()
        row = [
            trade.trade_id,
            trade.date,
            trade.time_pkt,
            trade.session,
            trade.direction,
            trade.timeframe,
            f"{trade.entry_price:.2f}",
            f"{trade.sl_price:.2f}",
            f"{trade.tp_price:.2f}",
            f"{trade.lot:.2f}",
            f"{trade.exit_price:.2f}",
            trade.exit_time_pkt,
            trade.exit_reason,
            f"{trade.pnl_usd:.2f}",
            f"{trade.r_multiple:.2f}",
            trade.entry_reason,
            trade.filters_passed,
            trade.notes
        ]
        with open(self.csv_filepath, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    def read_all_trades(self) -> pd.DataFrame:
        """Load all logged trades from CSV into a pandas DataFrame."""
        self._ensure_file_exists()
        try:
            df = pd.read_csv(self.csv_filepath)
            if df.empty:
                return pd.DataFrame(columns=self.CSV_HEADER)
            return df
        except Exception:
            return pd.DataFrame(columns=self.CSV_HEADER)

    def load_trades(self) -> List[CompletedTrade]:
        """Load all logged trades as a list of CompletedTrade instances."""
        df = self.read_all_trades()
        if df.empty:
            return []
        trades = []
        for _, row in df.iterrows():
            time_pkt = str(row.get('time_pkt', row.get('time', '')))
            entry_p = float(row.get('entry_price', row.get('entry', 0.0)))
            sl_p = float(row.get('sl_price', row.get('sl', 0.0)))
            tp_p = float(row.get('tp_price', row.get('tp', 0.0)))
            exit_p = float(row.get('exit_price', row.get('exit', 0.0)))
            exit_time_pkt = str(row.get('exit_time_pkt', row.get('exit_time', '')))
            pnl_u = float(row.get('pnl_usd', row.get('pnl_points', 0.0)))
            lot_v = float(row.get('lot', 0.01))
            tf_v = str(row.get('timeframe', '15m'))
            e_reason = str(row.get('entry_reason', '')) if pd.notna(row.get('entry_reason')) else ''
            f_passed = str(row.get('filters_passed', '')) if pd.notna(row.get('filters_passed')) else ''
            notes_v = str(row.get('notes', '')) if pd.notna(row.get('notes')) else ''

            trades.append(CompletedTrade(
                trade_id=str(row['trade_id']),
                date=str(row['date']),
                time_pkt=time_pkt,
                session=str(row['session']),
                direction=str(row['direction']),
                timeframe=tf_v,
                entry_price=entry_p,
                sl_price=sl_p,
                tp_price=tp_p,
                lot=lot_v,
                exit_price=exit_p,
                exit_time_pkt=exit_time_pkt,
                exit_reason=str(row['exit_reason']),
                pnl_usd=pnl_u,
                r_multiple=float(row['r_multiple']),
                entry_reason=e_reason,
                filters_passed=f_passed,
                notes=notes_v
            ))
        return trades
