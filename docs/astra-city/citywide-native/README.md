# HKS-222 — whole-territory native source preparation

The scripted preparation and exception audit are complete for the pinned government source snapshot. Architectural modelling remains paused. These are model parts and prepared assets, not approved landmarks, finished regions or newly published viewer content.

| Result | Count |
| --- | ---: |
| Indexed sheets accounted for | 3,456 / 3,456 |
| Building model outcomes | 216,976 / 216,976 |
| Packed building assets | 216,969 |
| Conservative source/viewer candidates | 212,675 |
| Source/identity matching holds, with geometry retained | 4,294 |
| Confirmed corrupt government JSON sources | 7 |
| Prepared native terrain models, after repair | 3,357 |
| Verified empty terrain scenes | 101 |
| Unexplained mechanical failures | 0 |
| Cross-sheet candidate UID collisions | 0 |

The seven corrupt glTF files contain only NUL bytes and a trailing CRLF, verified against pinned government ETags, ranges, original ZIP CRCs and file lengths. No JSON can be recovered. Among matching holds, 1,650 native references are absent even from the complete retained footprint dataset; exact and normalised comparisons found no partition/filtering omission.

All 216,969 packed building models received diagnostics against the actual viewer terrain sampler. Terrain intersections and elevated support samples are diagnostic observations, not automatic rejection, placement approval or reasons to lift geometry. Original coordinates, surveyed elevation and native source transforms are retained. No artificial vertical multiplier was introduced.

The separate terrain repair pass accounts for all 284 initial terrain failures: 183 were repaired and 101 are genuinely empty. It preserves 14,430,834 source vertices and 8,316,402 triangles; repairs normals, removes unused invalid UV/material data, and represents native transforms equivalently. One source declares an exact 0.02539999969303608 unit scale, which is preserved. Original failures remain in the immutable first-pass ledger; the final audit applies source-bound repair results.

## Shared state and recovery

- Original run: `e98f84fdaeb489b229af3910d80d765bb87dbbdc565ec1794836b04909f370ec`.
- Authoritative terrain repair: `0a8235777721aadedb888af5bebf62403f0b6bcd71cbbea3879d4bb42b541054`.
- Original/prepared sheet bundles: **19,995,567,007 bytes** in the R2 working prefix.
- Terrain repair bundles: **274,795,963 bytes**, separately retained.
- Neon holds fenced job completion, per-model outcomes and immutable R2 references.
- `R2-CHECKPOINT.json` identifies the verified final ledger snapshot and its Neon checkpoint record. It contains complete original and repair references, frozen inputs, exception evidence and recovery proofs.

Read `final-run.json`, `final-audit.json` and `terrain-repair-verification.json` for measured evidence. `source-restore-pilot.json` proves fresh R2 recovery followed by zero government requests; `shared-cache-reuse.json` proves a later batch reuses completed stages with zero new processing jobs. All bulk scripts make zero AI API calls; AI was used to implement and investigate the pipeline.

For another machine, use `.agents/skills/hong-kong-model-improvement/SKILL.md` and `source-scripts/city/citywide-native/README.md`. Reuse the shared results and original sources before running any conversion. Never place credentials in Git. R2 working snapshots are separate from production viewer assets.

## What remains

The next pass needs architectural identity/assembly decisions, terrain support and visual review, followed by guarded integration and browser validation for selected models. Source-corrupt objects need a usable alternate source or reconstruction. Basic forms remain for held/unavailable geometry. Use High effort for those decisions; no immediate user action is needed to preserve this completed mechanical pass.

HKS-222 is the reviewable mechanical deliverable under the Astra milestone; HKS-199 remains the broader parent. Review of this work is review of the pipeline, accounting and evidence, not acceptance of all models on the live map.
