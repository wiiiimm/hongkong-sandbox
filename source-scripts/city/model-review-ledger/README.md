# Shared model-review results — HKS-214

`ledger.py seed` idempotently records the pinned preflight's 459 source parts in the existing `astra-modelling` Neon branch. It does not replace the source inventory or rerun downloads. `model_review_status` joins live resource reservations to show work in progress and its owner. Initial existing detail, source absence and identity gaps remain separate from pending candidates.

`ledger.py status` reports the selected snapshot (default 3887f2f23fbad306). To record a reviewed part, use `record --receipt PATH --uid landsd/ID:PART --state held|approved-for-integration|installed-verified --evidence REPO_FILE --observation TEXT [--commit SHA]`. Source-unavailable and identity-unresolved outcomes are also supported. Results record evidence paths/hashes and append an event. The same database transaction checks that the whole source reservation remains live and owns the selected UID; stale or taken-over workers cannot write a review result. Source snapshots are not overwritten by reseeding.

The ledger records review decisions; it does not establish their architectural correctness. Only record approval after inspecting source/terrain/browser evidence and checking the guarded publication plan. Installed-verified means the feature-branch viewer, not production. No row implies a complete landmark or region. Normal source/workflow reports remain in Git; working files remain in R2. Live reservation ownership can expire independently of retained results.

Tests: `python -m unittest discover -s source-scripts/city/model-review-ledger -v`; set MODELLING_INTEGRATION_TEST=1 for an isolated, uniquely named Neon fixture. Fixture evidence is retained under its own review-test snapshot.

`record_many(snapshot, receipt_path, entries)` synchronises a verified batch in one fenced database transaction. Every member must have live source ownership and valid source evidence; an invalid member rejects the entire batch. Existing per-part `record` uses the same path. Live-Neon tests verify atomic rejection and stale-owner fencing.
