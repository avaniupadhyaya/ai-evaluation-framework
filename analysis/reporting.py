from __future__ import annotations

from html import escape
from pathlib import Path

from pipeline.models import ReleaseDecision


def _regression_text(value: float | None) -> str:
    return "n/a" if value is None else f"{value:+.1%}"


def render_console_report(decision: ReleaseDecision) -> str:
    lines = [
        f"Overall pass rate: {decision.overall_pass_rate:.1%}",
        f"Weighted risk score: {decision.weighted_risk_score:.3f}",
        f"Pending human review: {decision.human_review_count}",
        "",
        "Slice results",
        "---------------------------------------------------------------",
    ]

    for name, metric in decision.slice_metrics.items():
        lines.append(
            f"{name:<24} {metric.pass_rate:>6.1%}   {metric.status:<6}   "
            f"regression={_regression_text(metric.regression):>7}   risk={metric.weighted_risk:.3f}"
        )

    lines.extend(["", f"Release decision: {decision.decision}"])
    if decision.reasons:
        lines.append("Reasons:")
        lines.extend(f"- {reason}" for reason in decision.reasons)
    else:
        lines.append("Reasons: all release policies passed")

    return "\n".join(lines)


def render_markdown_report(decision: ReleaseDecision) -> str:
    lines = [
        "# Evaluation Release Report",
        "",
        f"**Decision:** `{decision.decision}`  ",
        f"**Overall pass rate:** {decision.overall_pass_rate:.1%}  ",
        f"**Weighted risk score:** {decision.weighted_risk_score:.3f}  ",
        f"**Pending human review:** {decision.human_review_count}",
        "",
        "## Slice-level results",
        "",
        "| Slice | Pass rate | Status | Regression | Severity weight | Weighted risk |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for name, metric in decision.slice_metrics.items():
        lines.append(
            f"| {name} | {metric.pass_rate:.1%} | {metric.status} | "
            f"{_regression_text(metric.regression)} | {metric.severity_weight:.1f} | {metric.weighted_risk:.3f} |"
        )

    lines.extend(["", "## Release rationale", ""])
    if decision.reasons:
        lines.extend(f"- {reason}" for reason in decision.reasons)
    else:
        lines.append("- All configured release policies passed.")

    lines.extend(
        [
            "",
            "## Operating interpretation",
            "",
            "This report preserves slice-level diagnostic resolution so an aggregate score cannot hide a high-severity regression.",
        ]
    )
    return "\n".join(lines)


def render_html_report(decision: ReleaseDecision) -> str:
    rows = []
    for name, metric in decision.slice_metrics.items():
        rows.append(
            "<tr>"
            f"<td>{escape(name)}</td>"
            f"<td>{metric.pass_rate:.1%}</td>"
            f"<td>{escape(metric.status)}</td>"
            f"<td>{escape(_regression_text(metric.regression))}</td>"
            f"<td>{metric.severity_weight:.1f}</td>"
            f"<td>{metric.weighted_risk:.3f}</td>"
            "</tr>"
        )

    reasons = "".join(f"<li>{escape(reason)}</li>" for reason in decision.reasons)
    if not reasons:
        reasons = "<li>All configured release policies passed.</li>"

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Evaluation Release Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 24px; color: #172033; }}
    .summary {{ display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 12px; margin: 24px 0; }}
    .card {{ border: 1px solid #d9e1ee; border-radius: 12px; padding: 16px; background: #f8fafc; }}
    .label {{ font-size: 12px; text-transform: uppercase; letter-spacing: .06em; color: #65748b; }}
    .value {{ font-size: 24px; font-weight: 700; margin-top: 6px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
    th, td {{ border-bottom: 1px solid #e4e9f0; padding: 10px; text-align: left; }}
    th {{ background: #f3f6fa; }}
    code {{ background: #eef2f7; padding: 2px 6px; border-radius: 6px; }}
  </style>
</head>
<body>
  <h1>Evaluation Release Report</h1>
  <p>Risk-aware summary for automated model release evaluation.</p>
  <div class=\"summary\">
    <div class=\"card\"><div class=\"label\">Decision</div><div class=\"value\">{escape(decision.decision)}</div></div>
    <div class=\"card\"><div class=\"label\">Pass rate</div><div class=\"value\">{decision.overall_pass_rate:.1%}</div></div>
    <div class=\"card\"><div class=\"label\">Weighted risk</div><div class=\"value\">{decision.weighted_risk_score:.3f}</div></div>
    <div class=\"card\"><div class=\"label\">Human review</div><div class=\"value\">{decision.human_review_count}</div></div>
  </div>
  <h2>Slice-level results</h2>
  <table>
    <thead><tr><th>Slice</th><th>Pass rate</th><th>Status</th><th>Regression</th><th>Severity</th><th>Weighted risk</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  <h2>Release rationale</h2>
  <ul>{reasons}</ul>
  <h2>Interpretation</h2>
  <p>This report keeps slice-level behavior visible so aggregate quality does not conceal high-severity failures or pending human review.</p>
</body>
</html>"""


def write_report(path: str, content: str) -> str:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    return str(output)
