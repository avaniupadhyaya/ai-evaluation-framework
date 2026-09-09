# Advanced Evaluation Architecture

This layer extends the starter framework with risk-aware release decisions and confidence-based escalation.

## Why this layer exists

Two evaluation failures with the same frequency should not necessarily carry the same release consequence.

A formatting regression and a safety regression can both reduce pass rate by 2%, but the operational risk is very different. The advanced policy layer therefore preserves slice-level metrics while adding severity weighting and confidence-aware human escalation.

## Decision flow

```text
Test case
  ↓
Grader routing
  ↓
Grade + confidence
  ↓
Risk-aware escalation
  ├─ low confidence → human review
  ├─ high/critical severity → higher confidence floor
  └─ confident automated decision → continue
  ↓
Slice metrics
  ↓
Severity weighting
  ↓
Regression + threshold checks
  ↓
Release policy
  ├─ SHIP
  ├─ REVIEW
  └─ BLOCK
```

## Key design choices

### Confidence is part of the result contract
Every grader returns confidence alongside pass/fail and score, so escalation is consistent across grader types.

### Severity belongs in release policy
Each slice carries a severity weight, allowing release gating to account for impact rather than treating every failure equally.

### High-risk cases use a stricter confidence floor
The same confidence can be acceptable for low-risk formatting checks and insufficient for safety- or groundedness-sensitive cases.

### Human review is a first-class release state
The release decision can be `SHIP`, `REVIEW`, or `BLOCK`, avoiding false certainty when judgment remains unresolved.

## Example policy

```yaml
human_escalation:
  confidence_floor: 0.70
  high_risk_confidence_floor: 0.90

release_policy:
  minimum_overall_pass_rate: 0.90
  max_weighted_risk_score: 0.08
  max_pending_human_reviews: 0
```

These thresholds are illustrative. In production they should be calibrated to product risk, evaluator reliability, and business impact.
