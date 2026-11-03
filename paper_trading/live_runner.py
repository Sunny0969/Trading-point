"""
Live Forward-Testing Runner for Gold (XAUUSD)
============================================
Paper trading forward test runner for strategy verification.
Zero broker interaction. Zero real money execution.

Usage:
------
1. Forward Replay Simulation (Historical closed bars forward test):
   python paper_trading/live_runner.py --mode replay

2. Continuous Live Paper Forward Test (Monitors live 15m closed bars):
   python paper_trading/live_runner.py --mode live --poll-interval 30

3. Generate Performance Report:
   python paper_trading/live_runner.py --report-only
"""

import os
import sys

# Ensure root directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import time
import argparse
import logging
from typing import Optional, Tuple, List, Dict, Any
import requests
import pandas as pd

from paper_trading.config import PaperTradingConfig, DEFAULT_CONFIG
from paper_trading.paper_engine import PaperTradingEngine
from paper_trading.risk_limits import RiskManager
from paper_trading.trade_log import TradeLogger
from paper_trading.report import PerformanceReporter

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ForwardTest.Runner")


def fetch_live_candles(
    interval: str = "15m",
    limit: int = 350,
    base_url: str = "http://127.0.0.1:8080"
) -> pd.DataFrame:
    """
    Fetch Gold (XAUUSD) candles from local server or public fallback feed.
    Returns DataFrame with columns: ['time', 'open', 'high', 'low', 'close']
    """
    # 1. Primary: Local TradingPoint Terminal API
    try:
        url = f"{base_url}/api/gold/candles?tf={interval}&limit={limit}"
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                df['time'] = pd.to_datetime(df['time'], unit='s' if df['time'].iloc[0] > 1e9 else 'ms')
                for col in ['open', 'high', 'low', 'close']:
                    df[col] = df[col].astype(float)
                df = df.sort_values('time').reset_index(drop=True)
                return df
    except Exception as e:
        logger.debug(f"Local server endpoint unavailable ({e}), trying public fallback...")

    # 2. Secondary Public Fallback: Coinbase PAXG-USD
    try:
        granularity = 900 if interval == "15m" else 3600
        url = f"https://api.exchange.coinbase.com/products/PAXG-USD/candles?granularity={granularity}"
        resp = requests.get(url, headers={"User-Agent": "ForwardTester/1.0"}, timeout=4)
        if resp.status_code == 200:
            raw = resp.json()
            if isinstance(raw, list) and len(raw) > 10:
                raw.reverse()
                rows = []
                for bar in raw:
                    rows.append({
                        "time": pd.to_datetime(bar[0], unit='s'),
                        "open": float(bar[3]),
                        "high": float(bar[2]),
                        "low": float(bar[1]),
                        "close": float(bar[4])
                    })
                df = pd.DataFrame(rows)
                df = df.sort_values('time').reset_index(drop=True)
                return df
    except Exception as e:
        logger.warning(f"Public fallback feed error: {e}")

    # 3. Empty fallback
    return pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close'])


class LiveForwardTester:
    """
    Manager class coordinating data ingestion, paper engine execution,
    and automatic performance report rendering.
    """

    def __init__(self, config: PaperTradingConfig = DEFAULT_CONFIG):
        self.config = config
        self.risk_manager = RiskManager(config)
        self.trade_logger = TradeLogger(config.trade_log_csv)
        self.engine = PaperTradingEngine(
            config=config,
            risk_manager=self.risk_manager,
            trade_logger=self.trade_logger
        )
        self.reporter = PerformanceReporter(config)
        self.last_processed_candle_time: Optional[pd.Timestamp] = None

    def run_replay(self, max_bars: int = 350):
        """
        Run forward simulation over available historical closed candles bar-by-bar.
        Yeh simulation bilkul usi order mein chalti hai jaise live market bars aatay hain.
        """
        logger.info("==================================================")
        logger.info("Starting Paper Trading Forward Test Replay")
        logger.info(f"Symbol: {self.config.symbol} | Signal TF: {self.config.signal_timeframe} | HTF: {self.config.htf_timeframe}")
        logger.info(f"Spread Adjustment: ${self.config.spread_usd:.2f} | Daily Limit: {self.config.max_daily_loss_r}R")
        logger.info("==================================================")

        df_15m = fetch_live_candles(self.config.signal_timeframe, limit=max_bars)
        df_1h = fetch_live_candles(self.config.htf_timeframe, limit=max_bars)

        if len(df_15m) < 60:
            logger.error("Insufficient candle history to perform forward test replay.")
            return

        logger.info(f"Fetched {len(df_15m)} 15m candles and {len(df_1h)} 1H candles for forward replay.")

        # Minimum warmup period for EMA 50 & RSI 14
        warmup = 55
        for i in range(warmup, len(df_15m)):
            current_bar = df_15m.iloc[i]
            history_df = df_15m.iloc[:i]

            # Match HTF slice up to current bar timestamp
            c_time = current_bar['time']
            htf_slice = df_1h[df_1h['time'] <= c_time] if len(df_1h) > 0 else None

            events = self.engine.on_new_candle(
                current_candle=current_bar,
                signal_history_df=history_df,
                htf_df=htf_slice
            )

            if events["filled_trade"]:
                t = events["filled_trade"]
                logger.info(
                    f"[VIRTUAL FILL] #{t.trade_id} {t.direction} at ${t.entry_price:.2f} "
                    f"(Spread: ${self.config.spread_usd:.2f}) | SL: ${t.sl_price:.2f} | TP: ${t.tp_price:.2f}"
                )

            if events["closed_trade"]:
                c = events["closed_trade"]
                status_tag = "[WIN]" if c.r_multiple > 0 else "[LOSS]"
                logger.info(
                    f"{status_tag} [TRADE CLOSED] #{c.trade_id} {c.direction} Exit: ${c.exit_price:.2f} "
                    f"Reason: {c.exit_reason} | PnL: ${c.pnl_points:.2f} | R: {c.r_multiple:+.2f}R"
                )

        # Generate final performance report
        logger.info("Forward replay complete. Compiling performance analytics...")
        report = self.reporter.generate_report()
        print(self.reporter.print_summary(report))
        self.reporter.export_csv(report)
        self.reporter.export_html(report)
        logger.info(f"[SUCCESS] HTML Report written to: {self.config.report_html}")
        logger.info(f"[SUCCESS] Trade Log written to: {self.config.trade_log_csv}")

    def run_live(self, poll_interval_sec: int = 30):
        """
        Continuous live paper forward-testing loop.
        Polls live market every poll_interval_sec, detects new 15m closed candle,
        and executes paper trading logic with zero real money risk.
        """
        logger.info("==================================================")
        logger.info("Starting Continuous Live Forward Testing Loop")
        logger.info("STATUS: 100% PAPER MODE - ZERO BROKER ORDERS")
        logger.info(f"Poll Interval: {poll_interval_sec}s | Press Ctrl+C to stop")
        logger.info("==================================================")

        try:
            while True:
                df_15m = fetch_live_candles(self.config.signal_timeframe, limit=100)
                df_1h = fetch_live_candles(self.config.htf_timeframe, limit=100)

                if len(df_15m) >= 60:
                    latest_bar = df_15m.iloc[-1]
                    bar_time = latest_bar['time']

                    if self.last_processed_candle_time != bar_time:
                        logger.info(f"[NEW CANDLE] Bar time: {bar_time} | Close: ${latest_bar['close']:.2f}")
                        history_df = df_15m.iloc[:-1]  # closed bars only

                        events = self.engine.on_new_candle(
                            current_candle=latest_bar,
                            signal_history_df=history_df,
                            htf_df=df_1h
                        )

                        self.last_processed_candle_time = bar_time

                        if events["filled_trade"]:
                            t = events["filled_trade"]
                            logger.info(f"🟢 [VIRTUAL FILL] #{t.trade_id} {t.direction} @ ${t.entry_price:.2f}")

                        if events["closed_trade"]:
                            c = events["closed_trade"]
                            logger.info(
                                f"🏁 [CLOSED] #{c.trade_id} {c.exit_reason} "
                                f"PnL: ${c.pnl_points:.2f} ({c.r_multiple:+.2f}R)"
                            )
                            # Update HTML report on trade close
                            self.reporter.export_html()

                time.sleep(poll_interval_sec)

        except KeyboardInterrupt:
            logger.info("Live forward testing loop stopped by user.")
            self.reporter.export_html()
            logger.info(f"HTML report updated: {self.config.report_html}")


def main():
    parser = argparse.ArgumentParser(description="XAUUSD Gold Paper Trading Engine")
    parser.add_argument(
        "--mode",
        choices=["replay", "live"],
        default="replay",
        help="Run historical replay forward test or continuous live polling"
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=30,
        help="Seconds between polls in live mode"
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Only compile and print performance report from existing log"
    )
    args = parser.parse_args()

    config = PaperTradingConfig()
    runner = LiveForwardTester(config)

    if args.report_only:
        report = runner.reporter.generate_report()
        print(runner.reporter.print_summary(report))
        runner.reporter.export_csv(report)
        runner.reporter.export_html(report)
        return

    if args.mode == "replay":
        runner.run_replay(max_bars=350)
    elif args.mode == "live":
        runner.run_live(poll_interval_sec=args.poll_interval)


if __name__ == "__main__":
    main()
