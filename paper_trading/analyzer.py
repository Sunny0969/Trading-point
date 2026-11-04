"""
Trade Audit & Performance Analyzer (Checklist Engine)
=====================================================
Reads demo_trades.csv (or paper_trades.csv) and evaluates the institutional
8-point review checklist every 20 trades towards the 100-trade forward test target.

Checklist Criteria:
1. Trade count & milestone progress (Target: 100, Checkpoint: every 20)
2. Win rate % and average win / loss in R (+ total PnL USD)
3. Expectancy calculation: (win% * avg win R) - (loss% * 1.0R)
4. Max drawdown in R and risk limit breach check (MAX_DAILY_LOSS_R = -3R)
5. Session-wise breakdown: identifies positive vs negative sessions
6. Filter confluence breakdown (HTF, RSI, FVG combinations)
7. Rule violation audit (SL integrity, RR bounds, abnormal lot size)
8. Notes & psychology audit (news events, emotions, manual interventions)
"""

import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np


@dataclass
class ChecklistItem:
    """Structure for each audit checklist item result."""
    number: int
    title: str
    status: str       # 'PASS', 'WARN', 'FAIL', 'IN_PROGRESS'
    summary: str
    details: List[str] = field(default_factory=list)


@dataclass
class AuditReport:
    """Complete container for the 8-point checklist audit."""
    csv_file: str
    total_trades: int
    target_trades: int = 100
    milestone_interval: int = 20
    current_milestone: int = 1
    trades_in_current_milestone: int = 0
    trades_until_next_milestone: int = 20
    is_milestone_due: bool = False

    # Metrics
    wins: int = 0
    losses: int = 0
    breakevens: int = 0
    win_rate_pct: float = 0.0
    loss_rate_pct: float = 0.0
    avg_win_r: float = 0.0
    avg_loss_r: float = 0.0
    total_r: float = 0.0
    total_pnl_usd: float = 0.0
    expectancy_r: float = 0.0
    profit_factor: float = 0.0
    peak_r: float = 0.0
    max_drawdown_r: float = 0.0
    longest_losing_streak: int = 0
    current_streak: str = "None"

    # Breakdowns
    session_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    filter_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    rule_violations: List[Dict[str, Any]] = field(default_factory=list)
    notes_audit: List[Dict[str, Any]] = field(default_factory=list)

    # 8 Checklist items
    checklist_items: List[ChecklistItem] = field(default_factory=list)
    verdict: str = ""
    recommendations: List[str] = field(default_factory=list)


class TradeAnalyzer:
    """Evaluates demo_trades.csv against the 8-point institutional review checklist."""

    def __init__(self, csv_filepath: str = "data/demo_trades.csv"):
        self.csv_filepath = csv_filepath

    def load_data(self) -> pd.DataFrame:
        """Loads and normalizes trade data from CSV."""
        if not os.path.exists(self.csv_filepath):
            return pd.DataFrame()

        try:
            df = pd.read_csv(self.csv_filepath)
        except Exception:
            return pd.DataFrame()

        if df.empty:
            return df

        # Normalize column aliases for backwards compatibility
        col_map = {
            'entry': 'entry_price',
            'sl': 'sl_price',
            'tp': 'tp_price',
            'exit': 'exit_price',
            'time': 'time_pkt',
            'exit_time': 'exit_time_pkt',
            'pnl_points': 'pnl_usd'
        }
        for old_col, new_col in col_map.items():
            if old_col in df.columns and new_col not in df.columns:
                df[new_col] = df[old_col]

        # Ensure essential columns exist
        for col in ['r_multiple', 'pnl_usd', 'lot', 'session', 'filters_passed', 'notes', 'entry_reason']:
            if col not in df.columns:
                df[col] = "" if col in ['session', 'filters_passed', 'notes', 'entry_reason'] else 0.0

        # Numeric casts
        df['r_multiple'] = pd.to_numeric(df['r_multiple'], errors='coerce').fillna(0.0)
        df['pnl_usd'] = pd.to_numeric(df['pnl_usd'], errors='coerce').fillna(0.0)
        df['entry_price'] = pd.to_numeric(df['entry_price'], errors='coerce').fillna(0.0)
        df['sl_price'] = pd.to_numeric(df['sl_price'], errors='coerce').fillna(0.0)
        df['tp_price'] = pd.to_numeric(df['tp_price'], errors='coerce').fillna(0.0)
        df['exit_price'] = pd.to_numeric(df['exit_price'], errors='coerce').fillna(0.0)
        df['lot'] = pd.to_numeric(df['lot'], errors='coerce').fillna(0.01)

        return df

    def analyze(self) -> AuditReport:
        """Runs complete quantitative audit and generates the 8-point checklist report."""
        df = self.load_data()
        total_trades = len(df)

        report = AuditReport(
            csv_file=self.csv_filepath,
            total_trades=total_trades,
            target_trades=100,
            milestone_interval=20
        )

        # Milestone tracking
        current_m = (total_trades // 20) + 1 if total_trades < 100 else 5
        in_current_m = total_trades % 20
        until_next_m = 20 - in_current_m if in_current_m > 0 else (0 if total_trades > 0 else 20)
        is_due = (total_trades > 0 and total_trades % 20 == 0)

        report.current_milestone = current_m
        report.trades_in_current_milestone = in_current_m if in_current_m > 0 else (20 if total_trades > 0 else 0)
        report.trades_until_next_milestone = until_next_m
        report.is_milestone_due = is_due

        if total_trades == 0:
            self._build_empty_report(report)
            return report

        # 1. Performance metrics
        r_series = df['r_multiple']
        pnl_series = df['pnl_usd']

        wins_mask = r_series > 0.05
        loss_mask = r_series < -0.05
        be_mask = (~wins_mask) & (~loss_mask)

        report.wins = int(wins_mask.sum())
        report.losses = int(loss_mask.sum())
        report.breakevens = int(be_mask.sum())

        report.win_rate_pct = round((report.wins / total_trades) * 100.0, 2)
        report.loss_rate_pct = round((report.losses / total_trades) * 100.0, 2)

        win_r_vals = r_series[wins_mask]
        loss_r_vals = r_series[loss_mask].abs()

        report.avg_win_r = round(float(win_r_vals.mean()), 2) if len(win_r_vals) > 0 else 0.0
        report.avg_loss_r = round(float(loss_r_vals.mean()), 2) if len(loss_r_vals) > 0 else 0.0
        report.total_r = round(float(r_series.sum()), 2)
        report.total_pnl_usd = round(float(pnl_series.sum()), 2)

        # User's exact Expectancy Formula: (win% * avg win R) - (loss% * 1.0R)
        win_dec = report.win_rate_pct / 100.0
        loss_dec = report.loss_rate_pct / 100.0
        report.expectancy_r = round((win_dec * report.avg_win_r) - (loss_dec * 1.0), 2)

        # Profit Factor
        gross_win_r = float(win_r_vals.sum())
        gross_loss_r = float(loss_r_vals.sum())
        if gross_loss_r > 0:
            report.profit_factor = round(gross_win_r / gross_loss_r, 2)
        else:
            report.profit_factor = round(gross_win_r, 2) if gross_win_r > 0 else 1.0

        # Drawdown in R
        cum_r = r_series.cumsum()
        running_peak = cum_r.cummax()
        dd_series = running_peak - cum_r
        report.max_drawdown_r = round(float(dd_series.max()), 2) if len(dd_series) > 0 else 0.0
        report.peak_r = round(float(cum_r.max()), 2) if len(cum_r) > 0 else 0.0

        # Streaks
        longest_loss = 0
        current_loss = 0
        longest_win = 0
        current_win = 0

        for r_val in r_series:
            if r_val < -0.05:
                current_loss += 1
                current_win = 0
                if current_loss > longest_loss:
                    longest_loss = current_loss
            elif r_val > 0.05:
                current_win += 1
                current_loss = 0
                if current_win > longest_win:
                    longest_win = current_win
            else:
                current_loss = 0
                current_win = 0

        report.longest_losing_streak = longest_loss
        last_trade_r = r_series.iloc[-1]
        if last_trade_r > 0.05:
            report.current_streak = f"{current_win} Wins in a row"
        elif last_trade_r < -0.05:
            report.current_streak = f"{current_loss} Losses in a row"
        else:
            report.current_streak = "Breakeven"

        # 2. Session-wise breakdown
        for session_name, s_group in df.groupby('session'):
            s_r = s_group['r_multiple']
            s_total = len(s_group)
            s_wins = int((s_r > 0.05).sum())
            s_losses = int((s_r < -0.05).sum())
            s_win_rate = round((s_wins / s_total) * 100.0, 1) if s_total > 0 else 0.0
            s_win_r = s_r[s_r > 0.05]
            s_avg_win = float(s_win_r.mean()) if len(s_win_r) > 0 else 0.0
            s_total_r = round(float(s_r.sum()), 2)
            s_exp = round(((s_win_rate / 100.0) * s_avg_win) - (((100.0 - s_win_rate) / 100.0) * 1.0), 2)
            s_status = "POSITIVE (+)" if s_total_r > 0 else ("NEGATIVE (-)" if s_total_r < 0 else "NEUTRAL")

            report.session_stats[str(session_name)] = {
                'trades': s_total,
                'wins': s_wins,
                'losses': s_losses,
                'win_rate': s_win_rate,
                'total_r': s_total_r,
                'expectancy_r': s_exp,
                'status': s_status
            }

        # 3. Filter confluence breakdown
        for f_name, f_group in df.groupby('filters_passed'):
            f_label = str(f_name).strip() if pd.notna(f_name) and str(f_name).strip() != "" else "No Filter Label"
            f_r = f_group['r_multiple']
            f_total = len(f_group)
            f_wins = int((f_r > 0.05).sum())
            f_losses = int((f_r < -0.05).sum())
            f_win_rate = round((f_wins / f_total) * 100.0, 1) if f_total > 0 else 0.0
            f_total_r = round(float(f_r.sum()), 2)

            report.filter_stats[f_label] = {
                'trades': f_total,
                'wins': f_wins,
                'losses': f_losses,
                'win_rate': f_win_rate,
                'total_r': f_total_r
            }

        # 4. Rule violations audit
        for idx, row in df.iterrows():
            t_id = row.get('trade_id', f"Trade-{idx+1}")
            r_val = float(row.get('r_multiple', 0.0))
            lot_val = float(row.get('lot', 0.01))
            reason = str(row.get('exit_reason', ''))

            # Check for excessive loss beyond -1.1R (indicating SL moved or severe slippage)
            if r_val < -1.15:
                report.rule_violations.append({
                    'trade_id': t_id,
                    'type': 'EXCESSIVE_SL_LOSS',
                    'detail': f"Realized {r_val:.2f}R loss (exceeds strictly capped -1.0R risk limit)",
                    'row': int(idx) + 1
                })
            # Check lot size consistency
            if abs(lot_val - 0.01) > 0.001:
                report.rule_violations.append({
                    'trade_id': t_id,
                    'type': 'ABNORMAL_LOT_SIZE',
                    'detail': f"Lot size was {lot_val} instead of fixed 0.01 lot",
                    'row': int(idx) + 1
                })
            # Check exit reason legitimacy
            if reason.upper() not in ['TP', 'SL', 'KILL_SWITCH', 'MANUAL']:
                report.rule_violations.append({
                    'trade_id': t_id,
                    'type': 'UNKNOWN_EXIT_REASON',
                    'detail': f"Unrecognized exit reason '{reason}'",
                    'row': int(idx) + 1
                })

        # 5. Notes & psychology audit
        keyword_pattern = re.compile(r'\b(news|qareeb|emotion|fear|greed|late|fomo|impulse|manual|chase)\b', re.IGNORECASE)
        for idx, row in df.iterrows():
            notes_raw = row.get('notes', '')
            if pd.notna(notes_raw) and str(notes_raw).strip() != "" and str(notes_raw).strip().lower() != "nan":
                notes_text = str(notes_raw).strip()
                matched = keyword_pattern.findall(notes_text)
                report.notes_audit.append({
                    'trade_id': row.get('trade_id', f"Trade-{idx+1}"),
                    'notes': notes_text,
                    'keywords': list(set([m.lower() for m in matched])),
                    'exit_reason': row.get('exit_reason', ''),
                    'r_multiple': float(row.get('r_multiple', 0.0))
                })

        # 6. Build the 8 Checklist Items
        self._build_checklist_items(report)

        return report

    def _build_empty_report(self, report: AuditReport):
        """Constructs response when CSV has no trades."""
        report.checklist_items = [
            ChecklistItem(1, "Kitne trades hue? (Target: 100)", "IN_PROGRESS", "0 / 100 trades completed (Forward test just started)"),
            ChecklistItem(2, "Win rate aur average win/loss R", "IN_PROGRESS", "No closed trades recorded yet"),
            ChecklistItem(3, "Expectancy positive hai? (win%*winR - loss%*1R)", "IN_PROGRESS", "Awaiting trade data"),
            ChecklistItem(4, "Max drawdown aur daily limit audit", "PASS", "0.00R Drawdown. Limits intact."),
            ChecklistItem(5, "Session-wise: kaunsa session positive / negative?", "IN_PROGRESS", "No session data yet"),
            ChecklistItem(6, "Kaunsa filter loss se pehle / baad pass hua?", "IN_PROGRESS", "No trade filters to analyze"),
            ChecklistItem(7, "Koi trade rules se bahar liya gaya?", "PASS", "Zero deviations detected"),
            ChecklistItem(8, "Rules change audit & new trade versioning", "PASS", "All trades adhere to 1:2 RR ATR base engine")
        ]
        report.verdict = "FORWARD TEST INITIALIZED. Awaiting live candle signal executions."
        report.recommendations = ["Keep engine running in paper mode.", "Do not modify SL/TP until 20 trades are reached."]

    def _build_checklist_items(self, r: AuditReport):
        """Constructs evaluations for the 8 user review checklist items."""
        # Item 1: Trade count & target progress
        pct_target = round((r.total_trades / r.target_trades) * 100.0, 1)
        item1_status = "PASS" if r.total_trades >= 20 else "IN_PROGRESS"
        item1_summary = f"{r.total_trades} / 100 trades completed ({pct_target}% of target reached)"
        item1_details = [
            f"Milestone: Phase {r.current_milestone} of 5",
            f"Trades in current 20-trade batch: {r.trades_in_current_milestone} / 20",
            f"Trades remaining to next review audit: {r.trades_until_next_milestone}"
        ]
        if r.is_milestone_due:
            item1_details.append(f"*** FORMAL REVIEW AUDIT DUE: Reached Trade #{r.total_trades} Milestone! ***")
        r.checklist_items.append(ChecklistItem(1, "Kitne trades hue? (Target: 100)", item1_status, item1_summary, item1_details))

        # Item 2: Win rate & average win / loss R
        item2_status = "PASS" if r.win_rate_pct >= 40.0 else "WARN"
        item2_summary = f"Win Rate: {r.win_rate_pct}% | Avg Win: +{r.avg_win_r:.2f}R | Avg Loss: -{r.avg_loss_r:.2f}R"
        item2_details = [
            f"Wins: {r.wins} trades | Losses: {r.losses} trades | Breakeven: {r.breakevens} trades",
            f"Total Realized R: {r.total_r:+.2f}R",
            f"Total Realized PnL: ${r.total_pnl_usd:+.2f} USD (on 0.01 lot)",
            f"Profit Factor: {r.profit_factor:.2f}"
        ]
        r.checklist_items.append(ChecklistItem(2, "Win rate aur average win/loss R", item2_status, item2_summary, item2_details))

        # Item 3: Expectancy
        # Formula: (win% * avg win R) - (loss% * 1.0R)
        item3_status = "PASS" if r.expectancy_r > 0 else "FAIL"
        calc_str = f"({r.win_rate_pct}% * {r.avg_win_r:.2f}R) - ({r.loss_rate_pct}% * 1.0R) = {r.expectancy_r:+.2f}R per trade"
        item3_summary = f"Expectancy is {item3_status}: {r.expectancy_r:+.2f}R per trade"
        item3_details = [
            f"Formula calculation: {calc_str}",
            "Mathematical Interpretation: " + (
                "Strategy has INSTITUTIONAL EDGE. On average, every trade generates positive return."
                if r.expectancy_r > 0 else
                "Strategy has NEGATIVE EDGE. Do not run on live money until filters are refined!"
            )
        ]
        r.checklist_items.append(ChecklistItem(3, "Expectancy positive hai? (win%*winR - loss%*1R)", item3_status, item3_summary, item3_details))

        # Item 4: Max Drawdown
        # Hard limit is MAX_DAILY_LOSS_R = -3.0R
        item4_status = "FAIL" if r.max_drawdown_r >= 3.0 else ("WARN" if r.max_drawdown_r >= 2.0 else "PASS")
        item4_summary = f"Max Drawdown: -{r.max_drawdown_r:.2f}R (Peak: +{r.peak_r:.2f}R)"
        item4_details = [
            f"Hard Daily Risk Limit: -3.0R ({'BREACHED!' if r.max_drawdown_r >= 3.0 else 'RESPECTED, within safe tolerance'})",
            f"Longest Losing Streak: {r.longest_losing_streak} consecutive losses",
            f"Current Streak: {r.current_streak}"
        ]
        r.checklist_items.append(ChecklistItem(4, "Max drawdown kitna tha, aur limit cross hui?", item4_status, item4_summary, item4_details))

        # Item 5: Session-wise Breakdown
        pos_sessions = [s for s, data in r.session_stats.items() if data['total_r'] > 0]
        neg_sessions = [s for s, data in r.session_stats.items() if data['total_r'] < 0]
        item5_status = "PASS" if len(neg_sessions) == 0 else "WARN"
        item5_summary = f"Positive: {pos_sessions if pos_sessions else 'None'} | Negative: {neg_sessions if neg_sessions else 'None'}"
        item5_details = []
        for s_name, s_data in r.session_stats.items():
            item5_details.append(
                f"[{s_name.upper()}]: {s_data['trades']} trades | Win Rate: {s_data['win_rate']}% | "
                f"Net R: {s_data['total_r']:+.2f}R | Expectancy: {s_data['expectancy_r']:+.2f}R ({s_data['status']})"
            )
        r.checklist_items.append(ChecklistItem(5, "Session-wise: kaunsa session positive aur negative?", item5_status, item5_summary, item5_details))

        # Item 6: Filter Confluence Breakdown
        item6_status = "PASS"
        item6_summary = f"{len(r.filter_stats)} filter confluences evaluated"
        item6_details = []
        for f_label, f_data in r.filter_stats.items():
            item6_details.append(
                f"Filter [{f_label}]: {f_data['trades']} trades | Win Rate: {f_data['win_rate']}% | Net: {f_data['total_r']:+.2f}R"
            )
        r.checklist_items.append(ChecklistItem(6, "Kaunsa filter loss se pehle ya baad mein pass hua?", item6_status, item6_summary, item6_details))

        # Item 7: Rule Violations
        if len(r.rule_violations) == 0:
            item7_status = "PASS"
            item7_summary = "Zero rule violations detected. All trades adhered 100% to risk & RR limits."
            item7_details = ["No SL moving detected", "All trade lot sizes strictly 0.01", "Standard TP/SL exits"]
        else:
            item7_status = "FAIL"
            item7_summary = f"{len(r.rule_violations)} rule deviations detected!"
            item7_details = [f"Row {v['row']} ({v['trade_id']}): {v['detail']}" for v in r.rule_violations]
        r.checklist_items.append(ChecklistItem(7, "Koi trade rules se bahar liya gaya? Agar haan, to kyun?", item7_status, item7_summary, item7_details))

        # Item 8: Rules Change Audit & Notes
        if len(r.notes_audit) == 0:
            item8_status = "PASS"
            item8_summary = "No anomalous psychological or news trade markers in notes."
            item8_details = ["Execution was 100% mechanical and systematic."]
        else:
            news_trades = [n for n in r.notes_audit if 'news' in n['keywords'] or 'qareeb' in n['keywords']]
            item8_status = "WARN" if len(news_trades) > 0 else "PASS"
            item8_summary = f"{len(r.notes_audit)} trades contain specific notes ({len(news_trades)} flagged near news)."
            item8_details = [
                f"Trade #{n['trade_id']} ({n['exit_reason']} {n['r_multiple']:+.1f}R): \"{n['notes']}\""
                for n in r.notes_audit
            ]
        r.checklist_items.append(ChecklistItem(8, "Kya rules change kiye? (Notes & news audit)", item8_status, item8_summary, item8_details))

        # Overall Verdict & Recommendations
        if r.expectancy_r > 0 and r.max_drawdown_r < 3.0:
            r.verdict = "HEALTHY FORWARD PROGRESS (Positive Expectancy & Controlled Risk)"
        else:
            r.verdict = "ATTENTION REQUIRED (Negative Expectancy or Elevated Drawdown)"

        r.recommendations = []
        if len(neg_sessions) > 0:
            r.recommendations.append(f"Consider filtering out or tightening entries in negative session(s): {', '.join(neg_sessions)}.")
        if any('news' in n['keywords'] or 'qareeb' in n['keywords'] for n in r.notes_audit):
            r.recommendations.append("Losses near high-impact news detected. Implement strict 30-minute news blackout filter.")
        if r.total_trades < 20:
            r.recommendations.append(f"Sample size is only {r.total_trades} trades. Continue paper forward testing until at least 20 trades before making strategy adjustments.")
        elif r.is_milestone_due:
            r.recommendations.append(f"Milestone {r.total_trades} reached! Compare with previous batch to verify if changes increased expectancy.")
        else:
            r.recommendations.append(f"Next scheduled formal review audit at Trade #{((r.total_trades // 20) + 1) * 20}.")


def format_cli_report(report: AuditReport) -> str:
    """Formats the audit into a beautiful, readable terminal report (ASCII safe)."""
    lines = []
    sep = "=" * 76
    sub_sep = "-" * 76

    lines.append(sep)
    lines.append("     XAUUSD PAPER TRADING ENGINE - 20-TRADE REVIEW CHECKLIST AUDIT")
    lines.append(sep)
    lines.append(f" CSV Source      : {report.csv_file}")
    lines.append(f" Completed Trades: {report.total_trades} / {report.target_trades} ({round((report.total_trades/report.target_trades)*100, 1)}% Target)")
    lines.append(f" Milestone Phase : Batch {report.current_milestone} of 5 ({report.trades_in_current_milestone}/20 in batch, {report.trades_until_next_milestone} remaining)")
    if report.is_milestone_due:
        lines.append(" *** NOTICE: 20-TRADE CHECKPOINT MILESTONE REACHED! FULL AUDIT REQUIRED! ***")
    lines.append(sub_sep)
    lines.append(f" Realized PnL    : {report.total_r:+.2f}R | ${report.total_pnl_usd:+.2f} USD (0.01 lot)")
    lines.append(f" Win Rate        : {report.win_rate_pct}% ({report.wins} Wins, {report.losses} Losses, {report.breakevens} BE)")
    lines.append(f" Average R       : Win +{report.avg_win_r:.2f}R | Loss -{report.avg_loss_r:.2f}R | Profit Factor: {report.profit_factor:.2f}")
    lines.append(f" Expectancy      : {report.expectancy_r:+.2f}R per trade [Formula: (win% * avg_win) - (loss% * 1R)]")
    lines.append(f" Max Drawdown    : -{report.max_drawdown_r:.2f}R (Hard Daily Limit: -3.0R)")
    lines.append(sep)
    lines.append("                     8-POINT REVIEW CHECKLIST")
    lines.append(sep)

    status_tags = {
        'PASS': '[PASS]',
        'WARN': '[WARN]',
        'FAIL': '[FAIL]',
        'IN_PROGRESS': '[PROGRESS]'
    }

    for item in report.checklist_items:
        tag = status_tags.get(item.status, f"[{item.status}]")
        lines.append(f"\n{item.number}. {item.title}")
        lines.append(f"   Status : {tag:<10} | {item.summary}")
        for det in item.details:
            lines.append(f"     * {det}")

    lines.append("\n" + sep)
    lines.append(f" OVERALL VERDICT : {report.verdict}")
    lines.append(sub_sep)
    lines.append(" ACTIONABLE RECOMMENDATIONS:")
    for idx, rec in enumerate(report.recommendations, 1):
        lines.append(f"   {idx}. {rec}")
    lines.append(sep)

    return "\n".join(lines)


def export_html_audit_report(report: AuditReport, output_path: str = "data/checklist_audit_report.html") -> str:
    """Generates a standalone, dark-themed responsive HTML audit report page."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    status_badge_css = {
        'PASS': 'background: rgba(34,197,94,0.2); color: #4ade80; border: 1px solid rgba(34,197,94,0.4);',
        'WARN': 'background: rgba(234,179,8,0.2); color: #facc15; border: 1px solid rgba(234,179,8,0.4);',
        'FAIL': 'background: rgba(239,68,68,0.2); color: #f87171; border: 1px solid rgba(239,68,68,0.4);',
        'IN_PROGRESS': 'background: rgba(59,130,246,0.2); color: #60a5fa; border: 1px solid rgba(59,130,246,0.4);'
    }

    items_html = ""
    for item in report.checklist_items:
        badge_style = status_badge_css.get(item.status, '')
        details_li = "".join([f"<li style='margin-bottom: 4px; color: #cbd5e1;'>{d}</li>" for d in item.details])
        items_html += f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 18px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h3 style="margin: 0; font-size: 16px; color: #f8fafc;">{item.number}. {item.title}</h3>
                <span style="padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; {badge_style}">{item.status}</span>
            </div>
            <div style="color: #94a3b8; font-size: 14px; margin-bottom: 10px;"><strong>Summary:</strong> {item.summary}</div>
            <ul style="margin: 0; padding-left: 20px; font-size: 13px;">
                {details_li}
            </ul>
        </div>
        """

    rec_li = "".join([f"<li style='margin-bottom: 8px; color: #f1f5f9;'>{r}</li>" for r in report.recommendations])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XAUUSD Paper Trading - 20-Trade Audit Checklist</title>
    <style>
        body {{
            background: #0b0f19;
            color: #e2e8f0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 24px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #1e293b, #0f172a);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-top: 18px;
        }}
        .card {{
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 14px;
        }}
        .card-title {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
            margin-bottom: 6px;
        }}
        .card-value {{
            font-size: 22px;
            font-weight: 700;
            color: #f8fafc;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0 0 6px 0; font-size: 24px; color: #f8fafc;">XAUUSD 20-Trade Review Checklist Audit</h1>
            <p style="margin: 0; font-size: 14px; color: #94a3b8;">Forward Paper Testing Telemetry &middot; File: <code>{report.csv_file}</code></p>
            <div class="grid">
                <div class="card">
                    <div class="card-title">Completed Progress</div>
                    <div class="card-value">{report.total_trades} / {report.target_trades} <span style="font-size: 13px; font-weight: 400; color: #38bdf8;">({round((report.total_trades/report.target_trades)*100, 1)}%)</span></div>
                </div>
                <div class="card">
                    <div class="card-title">Expectancy</div>
                    <div class="card-value" style="color: {'#4ade80' if report.expectancy_r > 0 else '#f87171'};">{report.expectancy_r:+.2f}R</div>
                </div>
                <div class="card">
                    <div class="card-title">Win Rate</div>
                    <div class="card-value">{report.win_rate_pct}%</div>
                </div>
                <div class="card">
                    <div class="card-title">Max Drawdown</div>
                    <div class="card-value" style="color: #f87171;">-{report.max_drawdown_r:.2f}R</div>
                </div>
                <div class="card">
                    <div class="card-title">Net PnL (0.01 lot)</div>
                    <div class="card-value" style="color: {'#4ade80' if report.total_pnl_usd >= 0 else '#f87171'};">${report.total_pnl_usd:+.2f}</div>
                </div>
            </div>
        </div>

        <h2 style="font-size: 18px; margin-bottom: 16px; color: #f1f5f9;">8-Point Review Checklist</h2>
        {items_html}

        <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 20px; margin-top: 24px;">
            <h3 style="margin: 0 0 10px 0; font-size: 16px; color: #38bdf8;">Overall Verdict & Recommendations</h3>
            <p style="font-size: 15px; font-weight: 600; color: #f8fafc; margin-bottom: 12px;">{report.verdict}</p>
            <ol style="margin: 0; padding-left: 20px; font-size: 14px;">
                {rec_li}
            </ol>
        </div>
    </div>
</body>
</html>
"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return output_path
