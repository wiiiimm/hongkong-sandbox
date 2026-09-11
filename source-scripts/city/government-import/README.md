# Local government-model validation batches — HKS-203

The first stage below prepares and validates candidates. The follow-up
[direct-import contract](DIRECT-IMPORT-POLICY.md) adds conservative scripted
acceptance and guarded publication for unchanged original sources, without
per-building AI architectural review. The first follow-up evaluates the 61 clear
forms from the initial 200-model batch; all failures stay pending.

Run bounded batches of original government meshes without per-model AI work or
full skip-screening. Reuse the existing current acceptance/hash plan, exact local
prepared assets and frozen Neon native-stage proof. The existing City loader checks
source identity, decoding, picking/collision and sampled rendered terrain. Results
are **mechanical validation**, not architectural acceptance or publication.

```sh
source-scripts/city/enhancement-screening/.venv/bin/python source-scripts/city/building-progress/export.py --refresh
source-scripts/city/enhancement-screening/.venv/bin/python source-scripts/city/enhancement-screening/screen.py plan --out source-scripts/city/government-import/local/plan
source-scripts/city/enhancement-screening/.venv/bin/python source-scripts/city/government-import/run.py --batch government-200-YYYYMMDD --count 200
```

The current cache adapter reads prepared assets/source metadata retained by the
previous two pilots. It never reads their comparison scores or decisions. Selection
is deterministic by source sheet/UID and excludes installed/embedded forms, current
accepted skips, changed identities and prior batch outcomes whose input/source
hashes still match. It currently stops if this local cache cannot supply the exact
requested count; source cache restoration/discovery remains in citywide-native.
This is a bounded adapter, not a whole-territory acquisition scheduler.

The batch claims every source UID atomically and runs under the existing supervised
reservation heartbeat/release wrapper. A separate shared job fences final results.
All selected outcomes, including exceptions, are saved in one transaction that
checks both job and source ownership. A new read-only connection then verifies the
entire stored JSON. Existing `astra_modelling.jobs` is reused under stage
`government-import-validation-v1`; no schema migration or acceptance writes.

Existing sampling flags retain models pending placement/context investigation;
clear CPU checks remain awaiting acceptance. The extra source gates require exact
recorded heights, footprint overlap at least 0.9 and centroid distance at most 2 m.
These gates do not certify architectural benefit or full foundation support.
Source meshes, heights and terrain are unchanged; no automatic AI review/fallback,
new good-to-go decisions, model publication or progress credit.

Outputs are under ignored `local/BATCH/`; committed reports live in
`docs/astra-city/government-import/BATCH/`. The report records original asset hashes,
frozen native result keys, complete outcomes and shared job identity. Local absolute
paths inside the capture describe the executing machine; restore by asset hash/native
cache key on another machine. The current 200-model handoff includes a verified
prepared-model archive for portable validation, separate from runtime publication.

Interrupted work: inspect the existing job and reservation before retrying. Reclaim
expired source ownership with a new receipt at the batch's reservation path, then
use `run.py --execute local/BATCH` under `reservations.py run`. Do not overwrite a
live owner's receipt. Completed jobs are evidence, not retryable work; use a new
explicit batch after input changes. A failed invocation can leave its job leased
until the bounded lease expires; it cannot overwrite another worker's result.

Tests: `python -m unittest discover -s source-scripts/city/government-import -v`.
The existing candidate validator also supports `--source-forms FILE`: exact current
tile bytes and selected records replace the legacy SQLite lookup. Its default
SQLite path remains supported. Missing/stale source records become explicit failures.

## Report stages for the user

Keep detailed Neon states unchanged; present the six-stage mapping in [.agents/skills/hong-kong-model-improvement/references/human-status.md](../../../.agents/skills/hong-kong-model-improvement/references/human-status.md). A failed placement/source check with known scripted follow-up is **In process — queued/running**. AI and human holds require a specific documented dependency. The completed 200-form batch is 11 Installed, 189 Held for unknown state and zero In process, with no established AI or human decision requirement; see [the human status report](../../../docs/astra-city/government-import/government-200-20260911/HUMAN-STATUS.md). This mapping changes no acceptance or installed counts.

## Completing the 198-form follow-up

The frozen resolution pass is in `resolve-pass.py`, `prepare-resolution.py`,
`check-support-sources.py`, `check-support-triangles.mjs`, `check-neighbours.mjs`,
`finalize-stage.py`, `resolution-browser.mjs` and `integrate-resolution.py`. These
are bounded to the recorded 200-form batch; they are not generic repeat commands.
Native-source checks cover every source vertex, triangle centre and low-rim edge.
Terrain corrections reuse original facets, split transitions on parent triangles,
retain the water mask and pass the existing publisher's coverage/overlap/seam
guards. Neighbour regressions retain the entire affected patch.

The final installation command runs under the shared reservation supervisor,
verifies staged and installed desktop/mobile day/night output and records terminal
results for all 198 forms. Unresolved cases keep their fallback and an explicit
technical hold. A zero-In-process report requires those checks to finish; it does
not come from renaming an unexecuted queue. AI and human holds still require a
confirmed decision requirement. See the batch's `resolution/README.md` and current
`HUMAN-STATUS.md` before any resume. Completed source jobs must not be overwritten.
