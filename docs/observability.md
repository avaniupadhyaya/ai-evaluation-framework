# Evaluation Observability

A release decision is only useful if teams can understand **why** it happened and **where** risk is concentrated.

This framework therefore treats reporting as part of the evaluation architecture rather than as a presentation layer added at the end.

## Outputs

Each evaluation run produces three artifacts:

1. **JSON** — machine-readable output for CI/CD, dashboards, and downstream automation.
2. **Markdown** — review-friendly summary for pull requests, release notes, and incident analysis.
3. **HTML** — portable visual report for stakeholders who need slice-level context without opening raw artifacts.

## What the reports preserve

The reports intentionally keep the following visible:

- overall pass rate
- release decision (`SHIP`, `REVIEW`, `BLOCK`)
- weighted risk score
- pending human-review count
- slice-level pass rates
- slice-level regression vs. baseline
- severity weight
- weighted risk contribution
- explicit release rationale

The objective is to avoid a common failure mode in evaluation systems: compressing heterogeneous model behavior into one aggregate quality score.

## Design principle

> Observability should preserve the information needed to explain a release decision, not merely display the final score.

A high aggregate pass rate can still coexist with a severe regression in a critical slice. The reporting layer keeps that diagnostic resolution visible so the release policy can be audited and challenged.

## CI/CD use

The GitHub Actions workflow runs the sample evaluation and uploads all three report formats as build artifacts. This makes each CI run self-contained and reviewable without requiring an external dashboard.

Future extensions can persist JSON artifacts to a data store and build longitudinal trend views across model, prompt, and policy versions.
