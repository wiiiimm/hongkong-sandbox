# Scripted shape-screening pilot — 10 September 2026

Codex root implemented this diagnostic pass for HKS-203, following the user's
instruction to use AI only for code and non-modelling work. No AI geometry,
architectural assessment or reconstruction was performed. No viewer models,
screening acceptance decisions or model-review approvals changed.

## Result

The original deterministic sample of **1,000 source forms** was recaptured against
current viewer inputs. Kai Tak Stadium remains a separate control.

| Proposed action | Sample forms |
| --- | ---: |
| Existing verified form — skip | 1 |
| Keep-current candidate | 4 |
| Original-detail import candidate | 38 |
| Retain current and leave pending | 957 |

These are **dry-run candidates**, not new good-to-go credit or publication jobs.
Automatic acceptance is disabled. Public enhanced progress remains 281.

There are 591 complete shape comparisons in the random sample: 581 show material
geometric differences, nine negligible differences, and one a positional offset
without added shape detail. Another 409 lack an unambiguous, loadable comparison
pair. Including Kai Tak, all 592 recovered pairs load successfully and compare
without errors. The current enhanced Kai Tak form correctly routes to existing
verified skip. Its historical fallback versus installed original is a separate
positive regression control.

The old pilot's 59 likely skips all show differences under the new multi-view
geometry criteria. That does **not** establish that all 59 need an upgrade or that
the old rule had 59 false skips: geometric change and worthwhile improvement are
different questions. It demonstrates why metadata/triangle count alone is weak
evidence for equivalence.

Overlapping pending reasons include 521 native support/terrain diagnostics, 146
current source/terrain flags and 110 footprint-match concerns. These counts overlap;
do not add them together. Ground gaps may be legitimate podiums; below-ground
vertices may be foundations. The script preserves the sources and reports those
cases. It neither lowers models nor calls AI to interpret them.

## What runs automatically

- Recover exact pinned government assets using existing acquisition/packing tools.
  Four assets were already local; 588 were recovered from checked government members
  because R2 credentials were not configured here. All asset SHA values match the
  prior completed native stage. Source-member transfer was 5,585,691 bytes, plus
  directory/network overhead. Packed assets total 5,130,656 bytes.
- Export current geometry through City's real building builder, and native geometry
  through its real official loader, including source identity, checksum, count and
  bounds checks. Use current terrain for every low-rim triangle vertex diagnostic.
- Compare 17 fixed orthographic views at 96 and 192 pixel object scales. Both meshes
  share one world frame. Measure silhouette, depth, roof profile and bounds; classify
  rigid offsets separately without moving either source.
- Route through separate source/placement/individual mobile-budget gates. Retain
  uncertain cases and existing acceptance. No AI fallback or modelling queue.
- Store content-addressed metrics in the existing shared Neon audit cache under a
  separate shape-comparison namespace. No schema migration or changes to existing
  territory-audit membership. Source/context, geometry, policy and engine changes
  invalidate reuse; payload hashes and immutable conflicts are checked.

First comparison run: **33.1 seconds**, 592 computed results. Shared-cache replay:
**3.234 seconds**, 592 cache hits, zero computations and zero new writes. Every
replayed result exactly equals its original. Clean offline replay from the checked
archive also matches all results. Source recovery replay uses 592 exact local
assets, makes no downloads and completes in 0.353 seconds. Source recovery took **95.917 seconds**;
fresh metadata capture took **99.663 seconds**. These are local script timings,
not end-to-end agent time or a viewer FPS benchmark. All pipeline AI-call counts
are zero; AI-assisted code development is not a zero-token claim for this session.

## Validation and limits

The screening suite passes 31 tests with one existing opt-in live acceptance test
skipped; nine existing public-progress tests also pass. New regressions cover roofs
with identical outer bounds, courtyard holes, changed wings, winding/order,
translation-only changes, disjoint projections, invalid geometry, rework precedence,
source/terrain/resource holds and cache corruption/invalidation.

Seven existing landmark components (Kai Tak, IFC, HSBC, Cultural Centre and three
Space Museum components) all produce a measurable fallback/native difference. The
prior user-approved Kai Tak port is a labelled positive control. Other landmarks
are regression diagnostics; no new architectural judgement is inferred from them.

This validates the implementation, **not a citywide false-skip rate**. There is no
new independently labelled real-building acceptance set. Fine features below the
sampled pixel scale, materials/facades, real neighbourhood occlusion, assembly
completeness and present-day source accuracy are not established by these metrics.
Do not enable automatic good-to-go credit or publication from this pilot alone.
Further architectural judgement remains paused under the user's instruction; the
script does not require the user to approve individual buildings.

The three contact sheets show geometry/depth and overlays, not final city styling.
They were checked for output framing, labels and overlay correctness as code/report
QA, not used for AI architectural acceptance. Original government geometry and
`references/` files remain unchanged.

## Evidence and replay

- `summary.json`, `actions.json`, `results.json.gz`: complete routes, metrics and gates.
- `inputs.json.gz`: frozen current source records and exact native/audit references.
- `geometry.tar.gz`, `replay-manifest.json`: 592 exact triangle pairs, checksums and
  current terrain diagnostics; only required members are retained.
- `acquisition.json`, `replay.json`, `old-rule-comparison.json`: measured provenance.
- `landmark-controls.json`: seven diagnostic controls.
- `comparison-1.jpg` through `comparison-3.jpg`: deterministic sample contact sheets.

From the worktree root with the existing modelling environment and dependencies in
`source-scripts/city/enhancement-screening/shape-requirements.txt`:

```sh
python -m tarfile -e docs/astra-city/enhancement-screening/shape-pilot-1000/geometry.tar.gz /tmp/hks-shape-replay
python source-scripts/city/enhancement-screening/screen.py compare \
  --evidence docs/astra-city/enhancement-screening/shape-pilot-1000/inputs.json.gz \
  --geometry /tmp/hks-shape-replay --out /tmp/hks-shape-report
```

Verify the archive SHA against `replay-manifest.json` before extraction. The replay
is offline and makes no database writes unless `--shared-cache` is explicitly used.
Its results remain historical, non-authoritative evidence. Fresh processing commands
are in the screening script README. No production deployment accompanies this pass.

## Complete Neon outcome sync — 10 September 2026

The subsequent 5,000-form work added complete diagnostic run persistence. All
1,000 sample outcomes plus the separate Kai Tak control have been backfilled,
including all 957 pending cases. Every stored JSON result and sample/control
membership passed a separate post-commit read-back. See `neon-sync.json`.
Run: `4c5c464837e01d3201d73987c910b9ea46ca8008d645e5646cce275dba399278`.
This extends the earlier metric-only cache; it grants no new skip/acceptance credit.
