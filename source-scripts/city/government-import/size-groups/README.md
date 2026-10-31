# Government model size groups — HKS-222 / HKS-203

The size-classification command only stores quickly queryable groups in Neon.
**It must not create import queues or start new batches.** The later explicit user
request separately authorises the bounded 22-model XXL first pass; general queue
construction remains deferred.
No per-model AI, downloads, geometry edits, review-state updates or installations.

`native_model_sizes` is an indexed projection of immutable government preparation
metadata already stored in `astra_modelling.native_stage_results`. Every source
model has one row per frozen run, including sources without a viewer match and
sources whose measurements are unavailable. The source run/cache key/model ID and
result hash preserve provenance. `native_model_size_runs` stores the verified
coverage, source fingerprint and policy summary; no processing jobs are enqueued.

## Stable brackets

Policy `government-size-v1` groups **triangle count**, not visual quality, physical
building size, architectural value, likely AI effort or probability of installation.
There is no implication that a simpler model should be skipped. Fixed boundaries
keep the groups comparable as the inventory changes.

| Group | Triangles |
| --- | ---: |
| XS (`xs`) | 0–99 |
| Small (`small`) | 100–499 |
| Medium (`medium`) | 500–1,999 |
| Large (`large`) | 2,000–9,999 |
| XL (`xl`) | 10,000–49,999 |
| XXL (`xxl`) | 50,000+ |
| Unmeasured (`unmeasured`) | Unknown; never treated as zero |

Raw triangle/source-vertex/indexed-vertex counts, compressed download bytes,
uncompressed GLB bytes and decoded geometry bytes remain separate sortable fields.
Decoded geometry bytes are an existing packer measurement, not total resident
browser/GPU memory or an FPS prediction. Native bounding-box width (X), height (Y)
and depth (Z) are in metres at 1×; they describe the source component envelope,
not necessarily an entire physical building. Source state and source holds are
retained. `viewer_uid` is populated only for the original unique candidate match;
it does not certify a current deployed match or acceptance.

## Commands

Use the repository's existing private `.env.modelling` and pinned shared modelling
branch. No application `DATABASE_URL` fallback. Commands run from the checkout root:

```sh
# Test additive migration and full-source projection, then roll back.
source-scripts/city/enhancement-screening/.venv/bin/python source-scripts/city/government-import/size-groups/sizes.py sync --dry-run
# Atomically store/verify all metadata; repeated unchanged sync inserts zero rows.
source-scripts/city/enhancement-screening/.venv/bin/python source-scripts/city/government-import/size-groups/sizes.py sync --out docs/astra-city/government-model-sizes/summary.json
# Read-only queries; these create no queues.
source-scripts/city/enhancement-screening/.venv/bin/python source-scripts/city/government-import/size-groups/sizes.py summary
source-scripts/city/enhancement-screening/.venv/bin/python source-scripts/city/government-import/size-groups/sizes.py list --group xxl --limit 20
source-scripts/city/enhancement-screening/.venv/bin/python source-scripts/city/government-import/size-groups/sizes.py list --group small --sheet 10-NE-14B --limit 100
source-scripts/city/enhancement-screening/.venv/bin/python source-scripts/city/government-import/size-groups/sizes.py list --sort download --limit 20
source-scripts/city/enhancement-screening/.venv/bin/python source-scripts/city/government-import/size-groups/sizes.py list --sort memory --limit 20
```

Use global `--run-id RUN` before the subcommand for another completed frozen run.
A new source revision belongs to its new run/cache key. Sync refuses incomplete
runs or changed projections instead of overwriting source-bound metadata. Changing
classification boundaries requires a versioned policy/schema migration, not a
silent edit to the existing groups.

Direct SQL example:

```sql
SELECT model_id, viewer_uid, sheet, triangles, compressed_bytes, geometry_bytes
FROM astra_modelling.native_model_sizes
WHERE run_id = 'e98f84fdaeb489b229af3910d80d765bb87dbbdc565ec1794836b04909f370ec'
  AND size_group = 'xxl'
ORDER BY triangles DESC NULLS LAST, cache_key, model_id
LIMIT 20;
```

Indexes cover group/complexity, overall complexity, download size, geometry size
and viewer UID. Size-group queries read normal indexed columns, without expanding
216,976 nested JSON outcomes. The sync checks actual EXPLAIN ANALYZE plans; its
reported database times exclude connection/network/cold-start overhead.

## Resume held work later

The size table is a classification index, not another review ledger. The existing
Neon review ledger retains current state, observations and immutable evidence
references. Completed `astra_modelling.jobs.result` records hold reasons and
per-model check results across the validation/context/resolution passes. The
source run/cache key links to original metadata and content-addressed R2 bundles;
viewer UID links to the import reviews. Preserve these histories when resuming.

For the first 200 models, see
`docs/astra-city/government-import/government-200-20260911/resolution/README.md`.
The 189 holds and their previous work remain available. Full-resolution PNGs,
portable plans and other larger evidence are repository artifacts rather than
Postgres blobs. Newly restored local terrain/support caches were not backed up to
R2 in that pass; restore from existing source bundles or the pinned government
revision if those local files are absent.

For future import work, the user's preferred strategy is a broad scripted first
pass: install unchanged sources that meet all existing gates, persist exceptions,
and address related blocker groups in a second pass. Preserve exact checks, input
hashes, policy/code revisions and what was tried; avoid repeated unchanged holds.
Complexity groups can later guide batch sizing, while source-sheet grouping can
reuse cache/terrain work. A small mesh can still have a difficult placement issue.
That future workflow is not started or queued by these metadata commands.
