"""
Performance Analytics & Reporting Engine
========================================
Calculates institutional performance metrics from trade logs:
- Total trades, Win rate, Average win R, Average loss R
- Expectancy: (win% * avg_win) - (loss% * avg_loss)
- Profit Factor: sum(positive R) / abs(sum(negative R))
- Max Drawdown (in R multiples)
- Longest losing streak
- Session-wise breakdown (Asia, London, New York, Overlap)
- Export to CLI summary, CSV, and standalone HTML report page.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from paper_trading.config import PaperTradingConfig, DEFAULT_CONFIG


@dataclass
class SessionMetrics:
    """Performance statistics for a specific trading session."""
    session: str
    total_trades: int
    wins: int
    losses: int
    win_rate: float
    avg_win_r: float
    avg_loss_r: float
    expectancy_r: float
    total_r: float

    @property
    def session_name(self) -> str:
        return self.session

    @property
    def win_rate_pct(self) -> float:
        return self.win_rate


@dataclass
class StrategyReport:
    """Aggregated strategy performance statistics."""
    total_trades: int
    wins: int
    losses: int
    breakevens: int
    win_rate: float
    loss_rate: float
    avg_win_r: float
    avg_loss_r: float
    expectancy_r: float
    profit_factor: float
    total_r: float
    max_drawdown_r: float
    longest_losing_streak: int
    longest_winning_streak: int
    sessions: Dict[str, SessionMetrics] = field(default_factory=dict)

    @property
    def winning_trades(self) -> int:
        return self.wins

    @property
    def losing_trades(self) -> int:
        return self.losses

    @property
    def win_rate_pct(self) -> float:
        return self.win_rate


class PerformanceReporter:
    """Computes quantitative metrics and generates CSV and HTML reports."""

    def __init__(
        self,
        config: Optional[Any] = None,
        report_html_path: Optional[str] = None,
        summary_csv_path: Optional[str] = None
    ):
        if isinstance(config, str):
            self.config = PaperTradingConfig(
                trade_log_csv=config,
                report_html=report_html_path or "data/paper_trading_report.html",
                report_csv=summary_csv_path or "data/performance_summary.csv"
            )
        elif isinstance(config, PaperTradingConfig):
            self.config = config
        else:
            self.config = DEFAULT_CONFIG

    def generate_report(self, df_trades: Optional[pd.DataFrame] = None) -> StrategyReport:
        """
        Compute full statistical report from trades DataFrame or configured trade log CSV.
        Expected columns: ['trade_id', 'date', 'session', 'r_multiple', ...]
        """
        if df_trades is None:
            if os.path.exists(self.config.trade_log_csv):
                try:
                    df_trades = pd.read_csv(self.config.trade_log_csv)
                except Exception:
                    df_trades = pd.DataFrame()
            else:
                df_trades = pd.DataFrame()

        if df_trades.empty or 'r_multiple' not in df_trades.columns:
            return StrategyReport(
                total_trades=0, wins=0, losses=0, breakevens=0,
                win_rate=0.0, loss_rate=0.0, avg_win_r=0.0, avg_loss_r=0.0,
                expectancy_r=0.0, profit_factor=0.0, total_r=0.0,
                max_drawdown_r=0.0, longest_losing_streak=0, longest_winning_streak=0
            )

        r_series = pd.to_numeric(df_trades['r_multiple'], errors='coerce').fillna(0.0)

        total_trades = len(r_series)
        wins = int((r_series > 0.05).sum())
        losses = int((r_series < -0.05).sum())
        breakevens = total_trades - (wins + losses)

        win_rate = round((wins / total_trades) * 100.0, 2) if total_trades > 0 else 0.0
        loss_rate = round((losses / total_trades) * 100.0, 2) if total_trades > 0 else 0.0

        win_r_list = r_series[r_series > 0.05]
        loss_r_list = r_series[r_series < -0.05].abs()

        avg_win_r = round(float(win_r_list.mean()), 2) if len(win_r_list) > 0 else 0.0
        avg_loss_r = round(float(loss_r_list.mean()), 2) if len(loss_r_list) > 0 else 0.0

        # Expectancy formula: (Win_Rate_Dec * Avg_Win_R) - (Loss_Rate_Dec * Avg_Loss_R)
        win_dec = win_rate / 100.0
        loss_dec = loss_rate / 100.0
        expectancy_r = round((win_dec * avg_win_r) - (loss_dec * avg_loss_r), 2)

        # Profit Factor
        gross_profit_r = float(win_r_list.sum())
        gross_loss_r = float(loss_r_list.sum())
        if gross_loss_r > 0:
            profit_factor = round(gross_profit_r / gross_loss_r, 2)
        else:
            profit_factor = round(gross_profit_r, 2) if gross_profit_r > 0 else 1.0

        total_r = round(float(r_series.sum()), 2)

        # Max Drawdown in R
        cumulative_r = r_series.cumsum()
        running_peak = cumulative_r.cummax()
        drawdown_series = running_peak - cumulative_r
        max_drawdown_r = round(float(drawdown_series.max()), 2) if len(drawdown_series) > 0 else 0.0

        # Streaks
        longest_loss_streak = 0
        longest_win_streak = 0
        curr_loss = 0
        curr_win = 0

        for r in r_series:
            if r < -0.05:
                curr_loss += 1
                curr_win = 0
                longest_loss_streak = max(longest_loss_streak, curr_loss)
            elif r > 0.05:
                curr_win += 1
                curr_loss = 0
                longest_win_streak = max(longest_win_streak, curr_win)
            else:
                curr_loss = 0
                curr_win = 0

        # Session Breakdown
        sessions_dict = {}
        if 'session' in df_trades.columns:
            for sess_name in ["Asia", "London", "New York", "Overlap"]:
                sub = df_trades[df_trades['session'] == sess_name]
                s_tot = len(sub)
                if s_tot == 0:
                    sessions_dict[sess_name] = SessionMetrics(
                        session=sess_name, total_trades=0, wins=0, losses=0,
                        win_rate=0.0, avg_win_r=0.0, avg_loss_r=0.0,
                        expectancy_r=0.0, total_r=0.0
                    )
                    continue

                s_r = pd.to_numeric(sub['r_multiple'], errors='coerce').fillna(0.0)
                s_wins = int((s_r > 0.05).sum())
                s_losses = int((s_r < -0.05).sum())
                s_wr = round((s_wins / s_tot) * 100.0, 2)
                s_lr = round((s_losses / s_tot) * 100.0, 2)

                s_w_list = s_r[s_r > 0.05]
                s_l_list = s_r[s_r < -0.05].abs()
                s_avg_w = round(float(s_w_list.mean()), 2) if len(s_w_list) > 0 else 0.0
                s_avg_l = round(float(s_l_list.mean()), 2) if len(s_l_list) > 0 else 0.0
                s_exp = round(((s_wr / 100.0) * s_avg_w) - ((s_lr / 100.0) * s_avg_l), 2)
                s_tot_r = round(float(s_r.sum()), 2)

                sessions_dict[sess_name] = SessionMetrics(
                    session=sess_name, total_trades=s_tot, wins=s_wins, losses=s_losses,
                    win_rate=s_wr, avg_win_r=s_avg_w, avg_loss_r=s_avg_l,
                    expectancy_r=s_exp, total_r=s_tot_r
                )

        return StrategyReport(
            total_trades=total_trades,
            wins=wins,
            losses=losses,
            breakevens=breakevens,
            win_rate=win_rate,
            loss_rate=loss_rate,
            avg_win_r=avg_win_r,
            avg_loss_r=avg_loss_r,
            expectancy_r=expectancy_r,
            profit_factor=profit_factor,
            total_r=total_r,
            max_drawdown_r=max_drawdown_r,
            longest_losing_streak=longest_loss_streak,
            longest_winning_streak=longest_win_streak,
            sessions=sessions_dict
        )

    def print_summary(self, report: StrategyReport) -> str:
        """Format strategy report into a human-readable CLI table."""
        lines = [
            "=" * 60,
            "--- XAUUSD PAPER TRADING PERFORMANCE REPORT (ZERO BROKER) ---",
            "=" * 60,
            f"Total Completed Trades:     {report.total_trades}",
            f"Win Rate:                   {report.win_rate:.1f}% ({report.wins} Wins / {report.losses} Losses / {report.breakevens} BE)",
            f"Average Win R:              +{report.avg_win_r:.2f} R",
            f"Average Loss R:             -{report.avg_loss_r:.2f} R",
            f"Expectancy:                 {report.expectancy_r:+.2f} R per trade",
            f"Profit Factor:              {report.profit_factor:.2f}",
            f"Total Net Performance:      {report.total_r:+.2f} R",
            f"Max Drawdown (in R):        -{report.max_drawdown_r:.2f} R",
            f"Longest Losing Streak:      {report.longest_losing_streak} trades",
            f"Longest Winning Streak:     {report.longest_winning_streak} trades",
            "-" * 60,
            "SESSION-WISE BREAKDOWN:",
            f"{'Session':<12} | {'Trades':<6} | {'Win Rate':<9} | {'Expectancy':<10} | {'Total R':<8}",
            "-" * 60,
        ]

        for s_name, s in report.sessions.items():
            lines.append(
                f"{s_name:<12} | {s.total_trades:<6} | {s.win_rate:>6.1f}%  | {s.expectancy_r:>+7.2f} R  | {s.total_r:>+6.2f} R"
            )

        lines.append("=" * 60)
        output = "\n".join(lines)
        return output

    def export_csv(self, report: StrategyReport, filepath: Optional[str] = None) -> str:
        """Export metrics to CSV file."""
        target_path = filepath or self.config.report_csv
        os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)

        data = {
            "Metric": [
                "Total Trades", "Wins", "Losses", "Breakevens",
                "Win Rate %", "Average Win R", "Average Loss R",
                "Expectancy R", "Profit Factor", "Total R",
                "Max Drawdown R", "Longest Losing Streak", "Longest Winning Streak"
            ],
            "Value": [
                report.total_trades, report.wins, report.losses, report.breakevens,
                report.win_rate, report.avg_win_r, report.avg_loss_r,
                report.expectancy_r, report.profit_factor, report.total_r,
                report.max_drawdown_r, report.longest_losing_streak, report.longest_winning_streak
            ]
        }
        df_summary = pd.DataFrame(data)
        df_summary.to_csv(target_path, index=False)
        return target_path

    def export_html(self, report: StrategyReport, filepath: Optional[str] = None) -> str:
        """Generate a clean, standalone, dark-themed HTML performance dashboard."""
        target_path = filepath or self.config.report_html
        os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)

        session_rows = ""
        for s_name, s in report.sessions.items():
            color = "#3fb950" if s.expectancy_r >= 0 else "#ef5350"
            session_rows += f"""
            <tr>
              <td style="font-weight: 700;">{s_name}</td>
              <td>{s.total_trades}</td>
              <td>{s.win_rate:.1f}%</td>
              <td style="color: {color}; font-weight: 700;">{s.expectancy_r:+.2f} R</td>
              <td style="color: {color}; font-weight: 700;">{s.total_r:+.2f} R</td>
            </tr>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>XAUUSD Paper Trading Strategy Report</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{
      background: #0d1117;
      color: #c9d1d9;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 24px;
    }}
    .container {{
      max-width: 960px;
      margin: 0 auto;
    }}
    .header {{
      border-bottom: 1px solid #30363d;
      padding-bottom: 16px;
      margin-bottom: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .header h1 {{
      margin: 0;
      color: #ffd700;
      font-size: 22px;
      letter-spacing: 0.5px;
    }}
    .badge {{
      background: rgba(88, 166, 255, 0.15);
      color: #58a6ff;
      border: 1px solid rgba(88, 166, 255, 0.3);
      padding: 4px 10px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .card {{
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 8px;
      padding: 16px;
    }}
    .card-title {{
      font-size: 11px;
      color: #8b949e;
      text-transform: uppercase;
      font-weight: 700;
      margin-bottom: 6px;
    }}
    .card-value {{
      font-size: 24px;
      font-weight: 800;
      color: #f0f6fc;
      font-family: monospace;
    }}
    .green {{ color: #3fb950 !important; }}
    .red {{ color: #ef5350 !important; }}
    .table-container {{
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 24px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 13px;
    }}
    th {{
      color: #8b949e;
      padding: 10px 12px;
      border-bottom: 1px solid #30363d;
      font-size: 11px;
      text-transform: uppercase;
    }}
    td {{
      padding: 12px;
      border-bottom: 1px solid rgba(48, 54, 61, 0.5);
    }}
    .footer {{
      text-align: center;
      color: #8b949e;
      font-size: 11px;
      margin-top: 32px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <h1>⚡ XAUUSD Paper Trading Strategy Report</h1>
        <div style="font-size: 12px; color: #8b949e; margin-top: 4px;">Zero-Broker Simulation & Forward Test Analysis</div>
      </div>
      <span class="badge">FORWARD TEST MODE (0 REAL RISK)</span>
    </div>

    <div class="grid">
      <div class="card">
        <div class="card-title">Total Trades</div>
        <div class="card-value">{report.total_trades}</div>
      </div>
      <div class="card">
        <div class="card-title">Win Rate</div>
        <div class="card-value {'green' if report.win_rate >= 50 else 'red'}">{report.win_rate:.1f}%</div>
      </div>
      <div class="card">
        <div class="card-title">Expectancy per Trade</div>
        <div class="card-value {'green' if report.expectancy_r >= 0 else 'red'}">{report.expectancy_r:+.2f} R</div>
      </div>
      <div class="card">
        <div class="card-title">Profit Factor</div>
        <div class="card-value {'green' if report.profit_factor >= 1.5 else ''}">{report.profit_factor:.2f}</div>
      </div>
      <div class="card">
        <div class="card-title">Total Net R-Multiple</div>
        <div class="card-value {'green' if report.total_r >= 0 else 'red'}">{report.total_r:+.2f} R</div>
      </div>
      <div class="card">
        <div class="card-title">Max Drawdown</div>
        <div class="card-value red">-{report.max_drawdown_r:.2f} R</div>
      </div>
      <div class="card">
        <div class="card-title">Avg Win / Avg Loss</div>
        <div class="card-value">+{report.avg_win_r:.2f}R / -{report.avg_loss_r:.2f}R</div>
      </div>
      <div class="card">
        <div class="card-title">Max Loss Streak</div>
        <div class="card-value red">{report.longest_losing_streak} trades</div>
      </div>
    </div>

    <div class="table-container">
      <h3 style="margin-top: 0; color: #f0f6fc; font-size: 15px;">🏛️ Session-Wise Breakdown</h3>
      <table>
        <thead>
          <tr>
            <th>Session</th>
            <th>Trades</th>
            <th>Win Rate</th>
            <th>Expectancy</th>
            <th>Total R</th>
          </tr>
        </thead>
        <tbody>
          {session_rows}
        </tbody>
      </table>
    </div>

    <div class="footer">
      Generated automatically by TradingPoint Paper Engine • Forward test minimum recommended duration: 2-4 weeks before live consideration.
    </div>
  </div>
</body>
</html>
"""
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return target_path
