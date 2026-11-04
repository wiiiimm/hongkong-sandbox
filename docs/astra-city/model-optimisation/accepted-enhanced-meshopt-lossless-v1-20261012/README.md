# Accepted enhanced-model lossless compression — 12 October 2026

Executor: Codex. Branch `feature/astra-hong-kong-city-compressed`, stacked on `codex/astra-hong-kong-city`. Source snapshot: `113625f3fe156b04453814d2cbcb33b78feaeafe`. All selected source/output bytes, bufferViews, immutable receipts and Neon result identities passed independent readback. Original government assets, source catalogues and viewer manifest are unchanged. No historical-map reference images were used.

| Result | Count / bytes |
| --- | ---: |
| Installed native source UIDs inventoried | 6,649 |
| Explicitly accepted sources processed | 4,272 |
| Smaller lossless variants | 323 |
| Non-beneficial outputs retained | 3,949 |
| Missing/negative source acceptance held | 2,377 |
| Codec failures | 0 |
| Existing selected gzip sources | 80,011,445 bytes (80.01 MB) |
| All generated gzip outputs, including larger files | 76,319,119 bytes (76.32 MB) |
| Use smaller outputs; retain original for non-beneficial files | 73,943,644 bytes (73.94 MB) |
| Potential transfer savings with that selection | 6,067,801 bytes (6.07 MB / 7.58%) |

Most small original files already compress efficiently with gzip. The complete set of generated variants saves 3,692,326 bytes; selecting only the 323 smaller outputs improves potential savings to 6,067,801 bytes. These are offline file measurements, not deployed transfer savings, phone FPS or resident-memory improvements. Quantisation, simplification, cleanup and reordering were disabled. Complete Float32 attributes, original corner/index order, unused vertices and zero-area faces remain exact. Source poses/materials/assembly metadata and fixed 1x HKPD scale are preserved.

**Neon is updated and verified:** project `billowing-surf-67227217`, branch `br-icy-silence-b3wjwz0q`, schema `astra_modelling`. All 4,272 variant jobs are complete/unreviewed. Their results contain source/revision/recipe/output hashes, immutable artifact/receipt paths, transfer bytes, geometry/accessor counts and warm Node encoding/decoding timings. Final checkpoint `c4356a162ba2b7e10442613cc1f799687eba309e7c119680ffbb245ba4295703` binds report SHA-256 `89c8f0dd432f372f9bc5e9f2bc64dbcf0ef2cbc46feec0e895f9e484db8010bd`; its exact readback passed. Held source UIDs/reasons/revisit conditions are captured by the same immutable inventory/report references. Original installation/inventory/acceptance records were preserved.

Only sourceIdentity and geometry gates pass offline. Placement, visual, collision and devicePerformance remain untested; peak memory and physical-device frame time remain null. Variants are private staging artifacts, with zero published/approved runtime descriptors. Current source/terrain/support/runtime/device review remains required before any live variant catalogue export.

- [Full UID/source acceptance inventory](sources.json)
- [Pinned ready processing recipe](recipe.json)
- [Independent complete output/Neon readback](readback-20261012.json)
- [Neon checkpoint receipt](neon-sync.json)
- [Method, source provenance and limits](METHOD.md)
- [Verification: 52 tests passed, 15 isolated fixture tests skipped](verification.json)
- [Content-addressed artifacts and per-variant receipts](../../../../source-scripts/city/model-optimisation/staging/accepted-enhanced-meshopt-lossless-v1-20261012/)
- [Reproducible adapter and audit commands](../../../../source-scripts/city/model-optimisation/README.md)

A later batch must explicitly select newly accepted sources/current revisions and freeze new hashes. The 2,377 held entries are not a permanent non-installability claim and did not receive variant plans merely from historical visibility.
