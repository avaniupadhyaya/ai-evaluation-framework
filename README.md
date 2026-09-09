# AI Evaluation Framework

A lightweight, extensible framework for designing and running automated evaluations for LLM and GenAI systems.

The core operating principle is simple:

> Start with how the system can fail, then design the evaluation pipeline around those failure modes.

The framework now supports:

- failure taxonomies and evaluation slices
- golden sets and regression protection
- rule-based, LLM-as-a-judge, hybrid, and human-review paths
- provider-backed LLM judge execution with offline-safe fallback behavior
- confidence-aware human escalation
- severity-weighted release policy
- `SHIP` / `REVIEW` / `BLOCK` decisions
- production-feedback ingestion
- structured JSON artifacts
- Markdown and HTML release reports
- CI validation through GitHub Actions

## Architecture

```text
Failure discovery
      ↓
Failure taxonomy
      ↓
Evaluation slices
      ↓
Test cases / golden sets
      ↓
Grader routing
  ├─ rule-based
  ├─ LLM-as-a-judge
  ├─ human review
  └─ hybrid / multi-signal
      ↓
Confidence + slice metrics
      ↓
Regression + severity policy
      ↓
SHIP / REVIEW / BLOCK
      ↓
Production observability
      ↺ feeds new failures back into the taxonomy
```

## Why this exists

A benchmark tells you how a model scored on a dataset.

An eval pipeline should answer a harder question:

> Can we trust the next model, prompt, or policy change without reintroducing failures we have already paid to discover?

This framework treats production failures as reusable evaluation assets. A meaningful production failure should become one or more of:

- a new failure mode
- a targeted slice
- a golden test case
- a permanent regression gate
- a grader calibration example

Over time, the pipeline becomes **institutional memory for model quality**.

## Quick start

```bash
python -m pip install -r requirements.txt
python run_eval.py \
  --config configs/sample_eval.yaml \
  --output artifacts/eval_results.json \
  --report-dir artifacts/reports
```

A run produces:

```text
artifacts/
├── eval_results.json
└── reports/
    ├── eval_report.md
    └── eval_report.html
```

The console report surfaces the release decision, overall pass rate, weighted risk, pending human review, and slice-level regressions.

## Release policy

The framework does not treat all failures as equivalent.

Each slice can define:

- pass threshold
- maximum tolerated regression
- blocker behavior
- severity weight

The release layer then combines frequency, severity, regression, and pending human-review state into an explicit decision:

- **SHIP** — configured quality and risk policies pass
- **REVIEW** — no blocking failure, but unresolved human judgment remains
- **BLOCK** — a release policy or blocker condition fails

This avoids compressing heterogeneous model behavior into one aggregate score.

## Evaluation observability

Reporting is part of the architecture, not an afterthought.

Every run can generate:

1. **JSON** for CI/CD and downstream automation
2. **Markdown** for pull-request and release review
3. **HTML** for a portable stakeholder-facing release report

Reports preserve slice-level pass rate, regression, severity weight, weighted risk, release rationale, and human-review state.

See [`docs/observability.md`](docs/observability.md).

## Provider-backed judge

The LLM judge layer supports an OpenAI-compatible provider adapter while preserving an offline-safe mode for CI and local development.

A provider failure does not silently become a positive evaluation. The framework fails safely by surfacing uncertainty and escalating to human review when necessary.

See the provider architecture documentation in `docs/`.

## Repository structure

```text
.
├── analysis/              # reports and regression diagnostics
├── configs/               # YAML-driven eval and release policies
├── data/                  # sample cases, golden sets, baseline metrics
├── docs/                  # architecture and operating-model notes
├── graders/               # grader implementations and routing
├── pipeline/              # orchestration, artifacts, gating, feedback loop
├── taxonomy/              # failure-mode definitions
├── tests/                 # unit and integration tests
├── run_eval.py            # CLI entry point
└── requirements.txt
```

## Design principles

1. **Failure-first, not benchmark-first**  
   Define what can go wrong before choosing how to measure it.

2. **Preserve diagnostic resolution**  
   Aggregate metrics are useful only after slice-level behavior is visible.

3. **Route evaluation by risk and judgment type**  
   Deterministic checks, LLM judges, human review, and hybrid strategies have different failure modes.

4. **Treat evaluator confidence as a policy input**  
   Low-confidence or high-impact judgments should not be forced into binary automation.

5. **Make release decisions explicit**  
   Evaluation should connect directly to regression tolerance, severity, and launch gates.

6. **Feed production back into evaluation**  
   New failures should strengthen the framework rather than disappear after incident resolution.

7. **Make every decision auditable**  
   Reports should explain why a release shipped, paused for review, or was blocked.

## Status

This repository is a reference implementation intended to demonstrate evaluation-system design patterns. The sample dataset is deliberately small; the architecture is structured so teams can replace the data, provider adapter, graders, and release policy without rewriting the full pipeline.
