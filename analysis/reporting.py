from __future__ import annotations

from pipeline.models import ReleaseDecision


def render_console_report(decision: ReleaseDecision) -> str:
    lines = [
        f"Overall pass rate: {decision.overall_pass_rate:.1%}",
        "",
        "Slice results",
        "-----------------------------------------------",
    ]

    for name, metric in decision.slice_metrics.items():
        regression = "n/a" if metric.regression is None else f"{metric.regression:+.1%}"
        lines.append(
            f"{name:<24} {metric.pass_rate:>6.1%}   {metric.status:<6}   regression={regression}"
        )

    lines.extend(["", f"Release decision: {decision.decision}"])
    if decision.reasons:
        lines.append("Reasons:")
        lines.extend(f"- {reason}" for reason in decision.reasons)
    else:
        lines.append("Reasons: all blocking slices and overall policy passed")

    return "\n".join(lines)
