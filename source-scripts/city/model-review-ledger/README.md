# Shared model-review results — HKS-214

`ledger.py seed` idempotently records the pinned preflight's 459 source parts in the existing `astra-modelling` Neon branch. It does not replace the source inventory or rerun downloads. `model_review_status` joins live resource reservations to show work in progress and its owner. Initial existing detail, source absence and identity gaps remain separate from pending candidates.

`ledger.py status` reports the selected snapshot (default 3887f2f23fbad306). To record a reviewed part, use `record --receipt PATH --uid landsd/ID:PART --state held|approved-for-integration|installed-verified --evidence REPO_FILE --observation TEXT [--commit SHA]`. Source-unavailable and identity-unresolved outcomes are also supported. Results record evidence paths/hashes and append an event. The same database transaction checks that the whole source reservation remains live and owns the selected UID; stale or taken-over workers cannot write a review result. Source snapshots are not overwritten by reseeding.

The ledger records review decisions; it does not establish their architectural correctness. Only record approval after inspecting source/terrain/browser evidence and checking the guarded publication plan. Installed-verified means the feature-branch viewer, not production. No row implies a complete landmark or region. Normal source/workflow reports remain in Git; working files remain in R2. Live reservation ownership can expire independently of retained results.

Tests: `python -m unittest discover -s source-scripts/city/model-review-ledger -v`; set MODELLING_INTEGRATION_TEST=1 for an isolated, uniquely named Neon fixture. Fixture evidence is retained under its own review-test snapshot.

`record_many(snapshot, receipt_path, entries)` synchronises a verified batch in one fenced database transaction. Every member must have live source ownership and valid source evidence; an invalid member rejects the entire batch. Existing per-part `record` uses the same path. Live-Neon tests verify atomic rejection and stale-owner fencing.

## Modelling method and effort — HKS-224

The existing review history now stores effort separately from quality/acceptance. Each event retains its method (`scripted`, `lightweight`, `detailed`, `manual`, or `unknown`), AI model, reasoning effort, source SHA, evidence digest, commit, owner and timestamp. Optional fields are `run_id`, `job_id`, `issue`, `output_ref`, measured integer `input_tokens`, `output_tokens` and `duration_seconds`. Method describes how geometry was made; reasoning effort describes the AI setting. A lightweight model can still involve High reasoning. Neither field implies visual approval. Token counts must be attributable to this work; omit them for shared/unmeasured usage. Never put credentials in metadata.

Supply `--effort-json FILE --request-id STABLE_OPERATION_ID` alongside the existing `record` arguments. Example metadata:

```json
{
  "method": "lightweight",
  "ai_model": "gpt-6-astra",
  "reasoning_effort": "medium",
  "issue": "HKS-224",
  "output_ref": "repository-relative/path-or-immutable-R2-key"
}
```

For entirely scripted generation use `method: scripted`, `ai_model: null`, `reasoning_effort: not-applicable`. That describes execution, not whether AI helped author the script. Use `unknown` when no reliable record exists. `record_many(..., effort=metadata, request_id=stable_id)` applies one metadata object to a homogeneous batch; split batches when their effort differs. Existing callers remain compatible and explicitly record unknown effort.

```sh
python source-scripts/city/model-review-ledger/ledger.py history --uid landsd/123456:0
```

History looks across review snapshots by complete canonical UID, retaining all previous events. New records include source hashes; historical events whose source hashes were not embedded still identify their original snapshot. The current review result includes the latest effort; pending models have no recorded effort. Unreviewed mechanical preparation stays in its existing run ledger and is not falsely backfilled as AI modelling.

The additive `migrate-effort` migration was applied to the pinned replacement Neon database on 9 September 2026. New `seed` operations also install the fields. It defaults legacy events to unknown without guessing. Existing reservation checks and transaction locks cover metadata and review writes together; retries with the same ID reuse identical data, while changed data is rejected. Use a new ID for an actual revision. Retry reuse also requires current source ownership. The history does not reserve work or publish geometry.

Validation: three metadata tests and a real-Neon rollback-only test cover prior revision retention, retry deduplication/conflicts, source provenance and missing-reservation rejection. No test model records remain. Run with `MODELLING_EFFORT_LIVE_TEST=1 python -m unittest discover -s source-scripts/city/model-review-ledger -p test_effort.py -v`.
