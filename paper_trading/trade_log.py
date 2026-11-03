"""
Trade Log & Session Tracker Module
==================================
Har trade ko CSV mein persist karta hai with:
date, time, session (Asia, London, New York, Overlap), direction,
entry, sl, tp, exit, exit_reason, pnl_points, r_multiple.
"""

import os
import csv
from dataclasses import dataclass, asdict
from typing import List, Optional
import pandas as pd


@dataclass
class CompletedTrade:
    """Structure representing a completed paper trade record."""
    trade_id: str
    date: str           # YYYY-MM-DD
    time: str           # HH:MM:SS
    session: str        # 'Asia', 'London', 'New York', 'Overlap'
    direction: str      # 'BUY' ya 'SELL'
    entry: float        # Virtual fill price (after spread)
    sl: float           # Stop Loss
    tp: float           # Take Profit
    exit: float         # Exit fill price
    exit_reason: str    # 'TP', 'SL', 'MANUAL', 'KILL_SWITCH'
    pnl_points: float   # Net gold price points (exit - entry for BUY)
    r_multiple: float   # R-multiple realized (+2.0R for TP, -1.0R for SL)
    exit_time: str = "" # Exit timestamp

    @property
    def exit_price(self) -> float:
        return self.exit


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
    """Handles logging of completed virtual trades into CSV."""

    CSV_HEADER = [
        "trade_id", "date", "time", "session", "direction",
        "entry", "sl", "tp", "exit", "exit_time",
        "exit_reason", "pnl_points", "r_multiple"
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
            trade.time,
            trade.session,
            trade.direction,
            f"{trade.entry:.2f}",
            f"{trade.sl:.2f}",
            f"{trade.tp:.2f}",
            f"{trade.exit:.2f}",
            trade.exit_time,
            trade.exit_reason,
            f"{trade.pnl_points:.2f}",
            f"{trade.r_multiple:.2f}"
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
        """Load all logged trades as a list of CompletedTrade dataclass instances."""
        df = self.read_all_trades()
        if df.empty:
            return []
        trades = []
        for _, row in df.iterrows():
            trades.append(CompletedTrade(
                trade_id=str(row['trade_id']),
                date=str(row['date']),
                time=str(row['time']),
                session=str(row['session']),
                direction=str(row['direction']),
                entry=float(row['entry']),
                sl=float(row['sl']),
                tp=float(row['tp']),
                exit=float(row['exit']),
                exit_reason=str(row['exit_reason']),
                pnl_points=float(row['pnl_points']),
                r_multiple=float(row['r_multiple']),
                exit_time=str(row.get('exit_time', ''))
            ))
        return trades
