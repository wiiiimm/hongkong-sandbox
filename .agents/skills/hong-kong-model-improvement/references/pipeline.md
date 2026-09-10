# Existing pipeline routes

Run from the selected repository root with an available Python environment and Node 24+ on PATH. The inventory uses Python's standard library; geometry tools also use NumPy, Shapely and pyproj. Inspect the relevant existing script/dependency files instead of recreating a runtime or relying on a previous `/tmp` environment. Browser tools use the project's Playwright dependency and an available browser.

## Current import order — 11 September 2026

1. Reuse current acceptance records and input hashes to skip unchanged verified forms; preserve rework and dependency requirements.
2. For remaining forms, look up exact cached government assets, then run local identity/component, placement/support and runtime checks. No preliminary good-enough or shape-comparison pass is required.
3. Integrate validated original detail through the existing fenced acceptance/publisher flow. Leave unresolved or unavailable sources on their current fallback and queue scripted investigation.

All per-model work runs in local scripts with zero AI calls. Data transfers to government sources, Neon and R2 remain supported. Do not launch AI geometry generation, simplification or architectural review for failures; report any need for that work before proceeding with it. Historical screening reports are retained for diagnostics and do not schedule imports or grant acceptance.

| Work | Existing entry points and evidence |
| --- | --- |
| Validate the next cached government batch | `source-scripts/city/government-import/run.py --batch NAME --count 200`; read its README. Reuses exact sources and current acceptance; saves all outcomes to Neon. Mechanical validation only, no automatic acceptance/publication or AI review. |
| Read current job state | `python3 source-scripts/city/building-batch/status.py`; excludes superseded historical job rows |
| Rebuild/refresh inventory | `python3 source-scripts/city/building-batch/inventory.py`; read `source-scripts/city/building-batch/README.md` first |
| Resolve supported landmark identities | `source-scripts/city/landmark-identity/resolve.py`, `validate.py`, `verify_determinism.py`; documentation in `docs/astra-city/landmark-identity/README.md` |
| Acquire exact native model sources | `source-scripts/city/landmark-acquisition/acquire.py` and `verify.py`; named batches, pinned inputs and complete intersecting-sheet coverage |
| Acquire terrain prerequisites | `source-scripts/city/landmark-acquisition/terrain.py`; native geometry only, not a terrain edit |
| Prepare combined candidates | `source-scripts/city/landmark-identity/stage_proposals.py`; reuse `building-batch/cached_models.py` and the established decoder/packer |
| Update source/landmark accounting | `source-scripts/city/landmark-progress/report.py`; explicit `reviews.json` controls whole-landmark readiness |
| Prepare the validation queue (no AI jobs) | `source-scripts/city/landmark-preflight/preflight.py`, `terrain_inputs.py`; read `docs/astra-city/landmark-preflight/README.md` |
| Capture review evidence | `landmark-preflight/gallery.mjs`, `merge_gallery.py`, `contact.mjs`; bounded automatic reframing and explicit inactive/unresolved outcomes |
| Integrate a reviewed subset | Existing `source-scripts/city/island-detail-integration/publish.py` and the `landmark-visual-review/` review/guard pattern; use a fresh plan/evidence set |

Useful invocations after verifying local prerequisites:

```sh
python3 source-scripts/city/landmark-identity/stage_proposals.py check
# Only after source writers stop and this process owns SQLite writes:
python3 source-scripts/city/landmark-identity/stage_proposals.py run --sources-stable --node "$(command -v node)"
python3 source-scripts/city/landmark-progress/report.py
```

`--node` avoids the staging adapter's historical machine-specific default. Use `--help` and the current README for optional paths and browser settings.

## Downloads and retries

Read `source-scripts/city/landmark-acquisition/README.md` before changing a batch. A new UID set or source revision gets a new batch ID, pinned target input and recorded byte allowance. Reuse verified complete directories and native members. Keep partial coverage deferred even if one intersecting sheet already contains a model. Verification must account for the entire plan, not merely the files found locally.

Run one process per batch; its sheet workers share a locked cumulative transfer ledger. Do not reset charged bytes or overwrite earlier source snapshots to force a retry. A repacked archive can retain geometry while changing offsets: revalidate its directory in a new batch before range requests. Current source/terrain verification and restart tests are in `landmark-acquisition/test_acquire.py`.

Do not blindly rerun old completed acquisition commands on a cold clone. The tracked plan and ledger can exist while ignored native payloads, `official-selection.json.gz` and derived manifests are missing. Restore working material first, or perform an explicit source rebuild with retained evidence and a new plan when necessary.

## Review and publication

CPU validation uses the actual loader, source picking/collision and rendered terrain sampler. Interpret its diagnostics; do not automatically lower models or reject all elevated parts. Inspect neighbouring/supporting components at native elevations and compare source geometry with the final drawn terrain.

The current gallery can use disjoint workers, but merge only results from the same stable snapshot; reject duplicate/missing groups. Inspect representative exports and keep camera clarity, candidate activity and architectural acceptance separate. A target hidden in both views needs an explicit follow-up even when screenshots were successfully written.

Do not rerun the old three-model Asia Society publication script as a general publisher: those IDs are already installed. Adapt the existing guarded publisher to a newly reviewed selection, checking asset/source hashes, duplicate UIDs, fresh before/after evidence and fallback behaviour. Refresh inventory/readiness only after publishing the approved subset, then update Linear. Never infer a complete region from its component count.
