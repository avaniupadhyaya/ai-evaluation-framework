# Provider-backed judge execution

The framework supports two judge modes:

## Offline mode

Default behavior. No secrets are required, so CI remains deterministic and safe.

```bash
python run_eval.py --config configs/sample_eval.yaml
```

## Provider-backed mode

Set the following environment variables:

```bash
export JUDGE_PROVIDER=openai_compatible
export JUDGE_API_KEY=...
export JUDGE_MODEL=gpt-5-mini
# optional
export JUDGE_BASE_URL=https://api.openai.com/v1
```

The adapter requests structured JSON with four fields:

- `passed`
- `score`
- `confidence`
- `reason`

Provider failures do not silently pass. They return a failed judge result with zero confidence and force human review.

## Why this boundary exists

The judge is treated as another model in the quality system, not as ground truth. That means provider calls are isolated behind a stable contract so teams can:

- swap judge providers
- compare judges on the same cases
- audit confidence and disagreement
- keep deterministic CI independent of external APIs
- escalate low-confidence or failed judge calls to humans

The framework deliberately separates **evaluation orchestration** from **provider invocation** so release policy does not depend on one vendor-specific API.
