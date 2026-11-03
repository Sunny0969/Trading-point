"""
Unit Tests for Performance Reporter (report.py)
==============================================
Tests statistical analytics, expectancy, profit factor, max drawdown,
streaks, session breakdowns, and CSV / HTML export.
"""

import os
import pytest
from paper_trading.trade_log import CompletedTrade, TradeLogger
from paper_trading.report import PerformanceReporter, StrategyReport


@pytest.fixture
def sample_trade_log(tmp_path):
    """Creates a sample CSV trade log with known statistical distributions."""
    csv_file = str(tmp_path / "sample_trades.csv")
    logger = TradeLogger(csv_file)

    trades = [
        # Win (+2R) in London
        CompletedTrade(
            trade_id="T1", date="2026-02-01", time="08:00:00", session="London",
            direction="BUY", entry=2600.0, sl=2590.0, tp=2620.0, exit=2620.0,
            exit_reason="TP", pnl_points=20.0, r_multiple=2.0
        ),
        # Loss (-1R) in London
        CompletedTrade(
            trade_id="T2", date="2026-02-01", time="11:00:00", session="London",
            direction="SELL", entry=2620.0, sl=2630.0, tp=2600.0, exit=2630.0,
            exit_reason="SL", pnl_points=-10.0, r_multiple=-1.0
        ),
        # Win (+2R) in Overlap
        CompletedTrade(
            trade_id="T3", date="2026-02-02", time="14:00:00", session="Overlap",
            direction="BUY", entry=2615.0, sl=2605.0, tp=2635.0, exit=2635.0,
            exit_reason="TP", pnl_points=20.0, r_multiple=2.0
        ),
        # Loss (-1R) in Overlap
        CompletedTrade(
            trade_id="T4", date="2026-02-02", time="15:30:00", session="Overlap",
            direction="BUY", entry=2635.0, sl=2625.0, tp=2655.0, exit=2625.0,
            exit_reason="SL", pnl_points=-10.0, r_multiple=-1.0
        ),
        # Loss (-1R) in New York
        CompletedTrade(
            trade_id="T5", date="2026-02-03", time="17:00:00", session="New York",
            direction="SELL", entry=2620.0, sl=2630.0, tp=2600.0, exit=2630.0,
            exit_reason="SL", pnl_points=-10.0, r_multiple=-1.0
        ),
    ]

    for t in trades:
        logger.log_trade(t)

    return csv_file, tmp_path


class TestPerformanceMetrics:
    """Test performance statistics calculations."""

    def test_metrics_accuracy(self, sample_trade_log):
        csv_file, out_dir = sample_trade_log
        html_file = str(out_dir / "report.html")
        summary_csv = str(out_dir / "summary.csv")

        reporter = PerformanceReporter(csv_file, html_file, summary_csv)
        report = reporter.generate_report()

        assert report.total_trades == 5
        assert report.winning_trades == 2
        assert report.losing_trades == 3
        # Win rate: 2 / 5 = 40.0%
        assert report.win_rate_pct == 40.0
        # Average win R: 2.0R
        assert report.avg_win_r == 2.0
        # Average loss R: 1.0R
        assert report.avg_loss_r == 1.0
        # Expectancy: (0.40 * 2.0) - (0.60 * 1.0) = 0.80 - 0.60 = +0.20R
        assert pytest.approx(report.expectancy_r, 0.01) == 0.20
        # Total profit R: (2 * 2.0) = 4.0; Total loss R: 3.0 -> Profit factor = 4.0 / 3.0 = 1.33
        assert pytest.approx(report.profit_factor, 0.01) == 1.33
        # Longest losing streak: T4, T5 = 2 trades
        assert report.longest_losing_streak == 2

    def test_session_breakdown(self, sample_trade_log):
        csv_file, out_dir = sample_trade_log
        reporter = PerformanceReporter(csv_file)
        report = reporter.generate_report()

        sessions = report.sessions
        assert "London" in sessions
        assert "Overlap" in sessions
        assert "New York" in sessions

        # London: 2 trades, 1 win, 1 loss -> 50% win rate
        assert sessions["London"].total_trades == 2
        assert sessions["London"].win_rate_pct == 50.0

        # New York: 1 trade, 0 wins, 1 loss -> 0% win rate
        assert sessions["New York"].total_trades == 1
        assert sessions["New York"].win_rate_pct == 0.0

    def test_export_html_and_csv(self, sample_trade_log):
        csv_file, out_dir = sample_trade_log
        html_file = str(out_dir / "test_report.html")
        summary_csv = str(out_dir / "test_summary.csv")

        reporter = PerformanceReporter(csv_file, html_file, summary_csv)
        report = reporter.generate_report()

        html_out = reporter.export_html(report, filepath=html_file)
        assert os.path.exists(html_out)
        with open(html_out, "r", encoding="utf-8") as f:
            content = f.read()
            assert "XAUUSD Paper Trading Strategy Report" in content
            assert "Expectancy" in content

        csv_out = reporter.export_csv(report, filepath=summary_csv)
        assert os.path.exists(csv_out)
        with open(csv_out, "r", encoding="utf-8") as f:
            csv_content = f.read()
            assert "Win Rate" in csv_content
            assert "Expectancy" in csv_content
