"""
Audit & Review Checklist CLI Tool
=================================
Usage:
    python analyze_trades.py
    python analyze_trades.py --csv data/demo_trades.csv
    python analyze_trades.py --html

Automatically reads demo_trades.csv, parses all 18 telemetry columns,
and executes the 8-point institutional review checklist every 20 trades.
"""

import sys
import argparse
from paper_trading.analyzer import TradeAnalyzer, format_cli_report, export_html_audit_report


def main():
    parser = argparse.ArgumentParser(description="Evaluate 8-point review checklist for XAUUSD paper trades.")
    parser.add_argument(
        "--csv",
        type=str,
        default="data/demo_trades.csv",
        help="Path to demo_trades.csv log file (default: data/demo_trades.csv)"
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate standalone HTML audit report in data/checklist_audit_report.html"
    )
    parser.add_argument(
        "--out",
        type=str,
        default="data/checklist_audit_report.html",
        help="Path for exported HTML audit report"
    )

    args = parser.parse_args()

    analyzer = TradeAnalyzer(csv_filepath=args.csv)
    report = analyzer.analyze()

    # Terminal output
    cli_text = format_cli_report(report)
    print(cli_text)

    # HTML export if requested or default
    html_path = export_html_audit_report(report, args.out)
    print(f"\n[HTML Report Saved]: {html_path}")


if __name__ == "__main__":
    main()
