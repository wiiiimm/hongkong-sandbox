# Installed-model Meshopt follow-up — 13 October 2026

Executor Codex, using `hong-kong-model-optimisation`. The user authorised continuing compression after the latest Astra inventory check. The new committed installed snapshot contains 6,650 unique UIDs under `installed-v1`, with zero review-based exclusions. Nam Fung Court (`landsd/79099:0`) is the sole new source; all previous 6,649 revisions are unchanged. Preserve the previous immutable 12 October evidence.

Four unchanged pinned recipes produce lossless/original, high, balanced and lightweight candidates. The existing leased pipeline reuses all 26,596 completed same-source/same-recipe variants, processes the four additional candidates and independently re-audits all 26,600 current outputs. Processing results remain staged/unreviewed; original sources, reviews and runtime catalogues remain unchanged by compression. No historical-map reference images used.

## Reproducible commands

Set `MODELLING_ENV_FILE` to the existing pinned modelling credentials without using the application database. With the established Python environment:

```sh
python source-scripts/city/model-optimisation/run_installed_batch.py \
  --folder docs/astra-city/model-optimisation/installed-enhanced-meshopt-followup-v2-20261013 \
  --staging source-scripts/city/model-optimisation/staging/installed-enhanced-meshopt-followup-v2-20261013 \
  --workers 16
python source-scripts/city/model-optimisation/summarise_installed_batch.py \
  --folder docs/astra-city/model-optimisation/installed-enhanced-meshopt-followup-v2-20261013 --apply
```

A completed run must have all four independent audit checkpoints with exact Neon readback, then a final verified summary. No approval/publication is inferred from processing. Source error estimates are offline Float64/quadric diagnostics; rendered Float32 placement/terrain/support, visual/collision, physical-device memory/frame time and runtime publication require separate validation. These candidates establish download measurements, not FPS or resident-memory improvements; UInt32 index repacking can increase accessor estimates.

## Verified delivery

All 6,650 installed models have four complete variants (26,600 results), with zero exclusions/failures. This follow-up reused 26,596 earlier results and generated four new Nam Fung Court candidates. All four full-cohort source/output/derived-decoder/receipt/Neon audits passed and their checkpoint receipts have exact readback. The final Neon summary also has exact readback and zero active owned reservations.

Nam Fung Court’s source is 147,127 gzip bytes.

| Candidate | Gzip bytes | Reduction | Triangles |
| --- | ---: | ---: | ---: |
| original | 141,960 | 3.51% | 13,061 |
| high | 98,899 | 32.78% | 13,061 |
| balanced | 91,587 | 37.75% | 13,061 |
| lightweight | 76,558 | 47.96% | 13,061 |

All four candidates are smaller. The lossy tiers retain all 13,061 source triangles: seam/border locks and bounded error prevent simplification for this model. Transfer reductions do not establish a triangle or resident-memory reduction.

Current complete corpus, selecting smaller candidates and retaining originals elsewhere:

| Candidate | Smaller models | Potential transfer savings |
| --- | ---: | ---: |
| original | 505 | 12.46 MB / 7.28% |
| high | 1,795 | 63.11 MB / 36.89% |
| balanced | 2,343 | 73.95 MB / 43.22% |
| lightweight | 3,134 | 85.06 MB / 49.72% |

Source corpus: 171,084,124 gzip bytes. Final Neon checkpoint `1ef8ffdd367ae6619facce5ab99dc38096149a7a3cfa21261fd80a9b558e5152`; summary SHA-256 `3ecefcff2229d68a42824e70da157be8a7c40947dc009eeaa11cd38fc131fe18`.

- [All four new-model receipts and measurements](new-model-results.json)
- [Complete current-inventory summary](summary.json)
- [Verified final Neon readback](neon-sync.json)
- [Exact finished worker log archives](../../../../source-scripts/city/model-optimisation/staging/installed-enhanced-meshopt-followup-v2-20261013/log-archives.json)

No codec or processing code changed in this follow-up. The earlier verification baseline remains 58 tests passed and 15 isolated-database fixture skips; tests were not rerun solely for new data. All 26,600 current outputs were independently audited during this run. Placement/visual/collision/device approval and runtime publication remain separate work; originals and review records are preserved.
