# Next 200 government models — 11 September 2026

This records the initial mechanical batch. See [scripted acceptance follow-up](acceptance/README.md) for subsequent import outcomes; the original batch evidence remains unchanged.

Executor: Codex root; HKS-203 / HKS-199 / HKS-222. Batch
`government-200-20260911`, shared job
`afc082d1dcf6b7f991450a5f80e9391a205c31ea45afcea0dcb1f4d6fdefdfe3`.

| Result | Model parts |
| --- | ---: |
| Exact original cached assets staged and loaded | 200 |
| Runtime and conservative source/placement gates clear; acceptance pending | 61 |
| Retained pending source/placement/runtime investigation | 139 |
| Newly published / accepted | 0 |

The selected forms were not installed, embedded or currently accepted. Selection
uses source sheet/UID order among locally available exact prepared assets, independent
of old comparison outcomes. All 200 original geometry hashes match the frozen native
results checked against live Neon. Across 70 source sheets, 1,225,337 compressed asset
bytes were reused. Zero new source downloads, zero AI modelling/review calls and no
geometry, surveyed-height, terrain or viewer-model edits.

The existing City loader accepted all 200; picking/collision/rendered-terrain checks
completed for 199. Validation took 7.915 seconds and peak process RSS was 659,705,856
bytes; this is CPU processing, not a browser FPS benchmark. Of 72 without CPU concerns,
11 still fail the stricter source match gate, leaving 61 awaiting acceptance.
Overlapping reasons: terrain above model bottom 103; footprint match investigation
31; ground gap 24; highest roof below terrain 19; terrain validation exception 1.
Sampling flags are not proof a source is wrong: support, overhangs and foundations
need context. Original detail remains unchanged and all current fallbacks are retained.

## Exception diagnosis

`landsd/339566:0` / `B386092129901063C1` decoded correctly. At source roof point
(4120.2096354, -4812.3671875), the City terrain sampler reports 1.2 m HKPD while the
rendered 70 m terrain triangle is -4 m, a 5.2 m disagreement. The isolated repeat in
`terrain-exception.json` reproduces this. This is a terrain/runtime discrepancy,
not a corrupt government download. It remains held; no elevations were changed.

## Evidence and handoff

- `results.json.gz`: complete per-model outcomes, source and input hashes.
- `validation.json`: existing loader, real source picking/collision and terrain checks.
- `selection.json.gz`: frozen current source records and native result provenance.
- `prepared-models.tar.gz` / `prepared-manifest.json`: all 200 exact staged meshes
  and catalogue; every archived asset hash/length was verified after packaging.
- `neon-sync.json`: all 200 full outcomes read back exactly from the pinned Neon
  branch after a job/source-fenced commit. Source reservation released successfully.

Public enhancement totals stay at 281 because this pass does not grant acceptance.
The existing review workflow requires architectural acceptance before integration;
AI architectural review was not run under the user's zero-AI-modelling constraint.
No claim is made that these 61 are safe automatic imports or visually complete.
Further script development/validated acceptance rules and source/terrain exception
work remain separate. The user is not asked to approve individual buildings.

Three deterministic selection tests pass; the actual 200-model execution exercises
the current-tile validator path and complete fenced Neon result sync. Existing
SQLite-based validation remains available. No Lantau map-reference images were used.

Follow-up: [full 200-form funnel and scripted context for all 198 pending forms](pending-context/README.md). The batch remains two installed and 198 pending; 61 was an intermediate subset.

For user-facing progress use the [six-stage human report](HUMAN-STATUS.md): two Installed and 198 In process — queued scripted investigation. Historical held/pending labels below remain technical acceptance guards, not proof that AI or a user decision is required.
