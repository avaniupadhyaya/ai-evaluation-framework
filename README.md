# AI Evaluation Framework

A lightweight, extensible framework for designing and running automated evaluations for LLM and GenAI systems.

This repository is intentionally structured around a practical principle:

> Start with how the system can fail, then design the evaluation pipeline around those failure modes.

The framework supports:

- failure taxonomies
- evaluation slices
- golden sets
- grader routing
- rule-based graders
- LLM-as-a-judge graders
- human-review fallbacks
- regression thresholds
- release gating
- production feedback loops

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
  └─ hybrid
      ↓
Slice-level metrics
      ↓
Regression thresholds
      ↓
Release decision
      ↓
Production observability
      ↺ feeds new failures back into the taxonomy
```

## Why this exists

A benchmark tells you how a model scored on a dataset.

An eval pipeline should help answer a harder question:

> Can we trust the next model or prompt change without reintroducing failures we have already paid to discover?

This framework treats production failures as reusable evaluation assets. A meaningful production failure should become one or more of:

- a new failure mode
- a targeted slice
- a golden test case
- a permanent regression gate
- a grader calibration example

Over time, the eval pipeline becomes institutional memory for model quality.

## Quick start

```bash
python -m pip install -r requirements.txt
python run_eval.py --config configs/sample_eval.yaml
```

Example output:

```text
Overall pass rate: 91.4%

Slice results
--------------------------------
Groundedness         94.1%   PASS
Instruction Follow   96.8%   PASS
Safety               99.2%   PASS
Tool Use             84.7%   FAIL

Release decision: BLOCK
Reason: Tool-use regression exceeded allowed threshold (-5.8% vs baseline)
```

## Repository structure

```text
.
├── analysis/              # metrics, slice summaries, regression analysis
├── configs/               # YAML-driven eval definitions
├── data/                  # sample and golden evaluation sets
├── graders/               # grader implementations and routing
├── pipeline/              # orchestration, thresholds, release gating
├── taxonomy/              # failure-mode definitions
├── tests/                 # framework tests
├── run_eval.py            # CLI entry point
└── requirements.txt
```

## Design principles

1. **Failure-first, not benchmark-first**  
   Define what can go wrong before choosing how to measure it.

2. **Preserve diagnostic resolution**  
   Aggregate metrics are useful only after slice-level behavior is visible.

3. **Route evaluation by risk and judgment type**  
   Deterministic checks, LLM judges, human review, and hybrid strategies all have different failure modes.

4. **Make release decisions explicit**  
   Evaluation should connect to thresholds, regression tolerance, and launch gates.

5. **Feed production back into evaluation**  
   New failures should strengthen the framework rather than disappear after incident resolution.

## Status

This is a starter framework intended to demonstrate evaluation-system design patterns. The sample graders and datasets are deliberately lightweight and easy to extend.
