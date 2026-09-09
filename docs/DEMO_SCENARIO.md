# Demo Scenario: Risk-Aware Release Evaluation

This scenario demonstrates how the framework turns model-quality evidence into an explicit release decision.

## Scenario

A candidate model version introduces improvements in groundedness and instruction following, but also shows a regression in tool use and several low-confidence safety judgments.

The goal is not to collapse all of that into one average score. The goal is to preserve enough diagnostic resolution to answer:

> Is this candidate safe to ship, or does the evidence require review or blocking?

## Evaluation surface

The sample configuration evaluates five slices:

| Slice | Typical grader | Why it matters |
|---|---|---|
| Groundedness | LLM judge | Detects unsupported or weakly supported claims |
| Instruction following | LLM judge | Checks whether the response satisfies task constraints |
| Safety | Hybrid | Uses automated scoring with stricter escalation for high-risk cases |
| Tool use | Rule-based | Deterministic checks for expected tool behavior |
| Format compliance | Rule-based | Cheap, high-confidence validation for structured-output requirements |

## Risk-aware policy

Each slice has its own threshold, regression tolerance, blocker status, and severity weight.

This matters because a 2% regression in formatting quality should not be treated the same way as a 2% regression in safety or a business-critical tool-use workflow.

The release engine considers:

1. **Absolute quality** — is the slice above its required threshold?
2. **Regression** — did the candidate degrade relative to the baseline beyond tolerance?
3. **Severity** — how costly is failure in this slice?
4. **Confidence** — is the grader sufficiently confident for this risk level?
5. **Human review debt** — how many unresolved cases still require adjudication?

## Example decision path

```text
Candidate model
      ↓
Run evaluation slices
      ↓
Groundedness          PASS
Instruction following PASS
Safety                REVIEW
Tool use              FAIL
Format compliance     PASS
      ↓
Apply severity + regression policy
      ↓
Tool-use blocker regression exceeds tolerance
      ↓
RELEASE DECISION: BLOCK
```

The important point is not the exact score. It is that the framework can explain *why* the release is blocked and which evidence must change before the decision can change.

## Production feedback loop

The architecture does not end at release evaluation.

A meaningful production failure should leave behind an evaluation artifact:

```text
Production incident
      ↓
Reproduce failure
      ↓
Add / refine failure mode
      ↓
Create targeted slice or golden case
      ↓
Choose grader + threshold
      ↓
Add permanent regression protection
```

This is how the pipeline accumulates institutional memory for model quality.

## Try it

```bash
python -m pip install -r requirements.txt
python run_eval.py \
  --config configs/sample_eval.yaml \
  --output artifacts/eval_results.json \
  --markdown artifacts/eval_report.md \
  --html artifacts/eval_report.html
```

Then inspect the console output and generated JSON, Markdown, and HTML artifacts.
