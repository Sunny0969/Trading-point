"""
Unit Tests for Trade Audit & Checklist Analyzer (analyzer.py)
============================================================
Tests:
1. 8-Point Review Checklist calculation accuracy
2. Expectancy formula: (win% * avg_win) - (loss% * 1.0R)
3. Milestone tracking (target 100, checkpoints every 20)
4. Session-wise positive vs negative categorization
5. Filter confluence audit
6. Rule violation and news/notes keyword auditing
7. Real demo_trades.csv parsing
"""

import os
import pytest
import pandas as pd
from paper_trading.analyzer import TradeAnalyzer, format_cli_report, export_html_audit_report
from paper_trading.trade_log import CompletedTrade, TradeLogger


@pytest.fixture
def sample_20_trades_csv(tmp_path):
    """Generates a synthetic 20-trade CSV milestone batch with known outcomes."""
    csv_file = str(tmp_path / "milestone_20_trades.csv")
    logger = TradeLogger(csv_file)

    # 12 Wins (+2.0R), 8 Losses (-1.0R) -> 60% win rate
    # Expectancy: (0.60 * 2.0) - (0.40 * 1.0) = 1.20 - 0.40 = +0.80R
    # Interleave wins and losses so max drawdown stays controlled at 2.0R
    loss_indices = {3, 5, 8, 10, 13, 15, 17, 20}
    for i in range(1, 21):
        is_win = (i not in loss_indices)
        direction = "BUY" if i % 2 == 1 else "SELL"
        session = "London" if i <= 10 else "New York"
        r_mult = 2.0 if is_win else -1.0
        exit_r = "TP" if is_win else "SL"
        pnl = 5.0 if is_win else -2.5
        notes = "CPI news release" if (not is_win and i == 15) else ""
        filters = "HTF,RSI,FVG" if is_win else "HTF,RSI"

        trade = CompletedTrade(
            trade_id=f"T-{i}",
            date="2026-11-04",
            time_pkt="13:00",
            session=session,
            direction=direction,
            timeframe="15m",
            entry_price=4020.0,
            sl_price=4015.0 if direction == "BUY" else 4025.0,
            tp_price=4030.0 if direction == "BUY" else 4010.0,
            lot=0.01,
            exit_price=4030.0 if is_win else 4015.0,
            exit_time_pkt="14:00",
            exit_reason=exit_r,
            pnl_usd=pnl,
            r_multiple=r_mult,
            entry_reason="EMA cross",
            filters_passed=filters,
            notes=notes
        )
        logger.log_trade(trade)

    return csv_file, tmp_path


class TestChecklistAnalyzer:
    """Test suite for 8-point checklist calculations."""

    def test_milestone_20_trades_complete(self, sample_20_trades_csv):
        csv_file, tmp_dir = sample_20_trades_csv
        analyzer = TradeAnalyzer(csv_file)
        report = analyzer.analyze()

        # Item 1: Exactly 20 trades -> Milestone 1 reached
        assert report.total_trades == 20
        assert report.target_trades == 100
        assert report.is_milestone_due is True
        assert report.trades_until_next_milestone == 0

        # Item 2: Win rate & Average R
        assert report.wins == 12
        assert report.losses == 8
        assert report.win_rate_pct == 60.0
        assert report.avg_win_r == 2.0
        assert report.avg_loss_r == 1.0

        # Item 3: Expectancy formula
        # (0.60 * 2.0) - (0.40 * 1.0) = 1.20 - 0.40 = +0.80R
        assert pytest.approx(report.expectancy_r, 0.01) == 0.80
        assert report.checklist_items[2].status == "PASS"

        # Item 4: Max Drawdown within safe limits
        assert report.max_drawdown_r < 3.0
        assert report.checklist_items[3].status == "PASS"

        # Item 5: Session breakdown
        assert "London" in report.session_stats
        assert "New York" in report.session_stats

        # Item 6: Filter breakdown
        assert "HTF,RSI,FVG" in report.filter_stats
        assert "HTF,RSI" in report.filter_stats
        assert report.filter_stats["HTF,RSI,FVG"]["win_rate"] == 100.0

        # Item 7: Zero rule violations
        assert len(report.rule_violations) == 0
        assert report.checklist_items[6].status == "PASS"

        # Item 8: Notes audit flagged the news trade
        assert len(report.notes_audit) == 1
        assert "news" in report.notes_audit[0]["keywords"]

    def test_live_demo_trades_csv_sample(self):
        """Validates analyzer against actual data/demo_trades.csv provided by user."""
        csv_path = "data/demo_trades.csv"
        if not os.path.exists(csv_path):
            pytest.skip("data/demo_trades.csv not found")

        analyzer = TradeAnalyzer(csv_path)
        report = analyzer.analyze()

        assert report.total_trades >= 2
        assert report.wins >= 1
        assert report.losses >= 1
        # Trade 1 (+2.0R) and Trade 2 (-1.0R) -> net +1.0R
        assert report.total_r == 1.0
        # Win rate: 50.0%
        assert report.win_rate_pct == 50.0
        # Expectancy: (0.50 * 2.0) - (0.50 * 1.0) = +0.50R
        assert report.expectancy_r == 0.50

        # Verify CLI and HTML output functions run without error
        cli_out = format_cli_report(report)
        assert "8-POINT REVIEW CHECKLIST" in cli_out
        assert "London" in cli_out

    def test_rule_violation_triggers(self, tmp_path):
        """Verifies that unauthorized risk or lot deviations trigger FAIL status in Item 7."""
        csv_file = str(tmp_path / "violation_trades.csv")
        logger = TradeLogger(csv_file)

        # Trade with excessive SL loss (-2.5R due to moved SL) and abnormal lot size (0.10)
        bad_trade = CompletedTrade(
            trade_id="DEV-001",
            date="2026-11-04",
            time_pkt="16:00",
            session="New York",
            direction="BUY",
            timeframe="15m",
            entry_price=4020.0,
            sl_price=4010.0,
            tp_price=4040.0,
            lot=0.10,  # Abnormal lot size (should be 0.01)
            exit_price=3995.0,  # Exit far below SL
            exit_time_pkt="16:30",
            exit_reason="SL",
            pnl_usd=-25.0,
            r_multiple=-2.5,  # Exceeds strictly capped -1.0R
            entry_reason="FOMO manual entry",
            filters_passed="NONE",
            notes="SL shifted down during news spike"
        )
        logger.log_trade(bad_trade)

        analyzer = TradeAnalyzer(csv_file)
        report = analyzer.analyze()

        # Must flag rule violations
        assert len(report.rule_violations) >= 2
        assert report.checklist_items[6].status == "FAIL"

    def test_html_export(self, sample_20_trades_csv):
        csv_file, tmp_dir = sample_20_trades_csv
        analyzer = TradeAnalyzer(csv_file)
        report = analyzer.analyze()

        out_html = str(tmp_dir / "audit.html")
        path = export_html_audit_report(report, out_html)

        assert os.path.exists(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "XAUUSD 20-Trade Review Checklist Audit" in content
            assert "8-Point Review Checklist" in content
