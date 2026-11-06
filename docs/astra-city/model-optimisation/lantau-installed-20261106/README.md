# Installed Lantau compression — HKS-229

Executor: Codex, 6 November 2026. Working branch: `feature/islands-model-enhancement-and-compression`.

**COMPLETE:** all 6,787 installed enhanced Lantau sources have four independently verified candidates: **27,148 complete / 0 failed / 27,148 unreviewed / 0 published**. Reused 19,688 pre-existing variants and generated 7,460 additional ones. Mui Wo is complete at 1,597 models / 6,388 variants; Tai O and northwest villages at 1,144 models / 4,576 variants. Other acquisition/enhancement work remains paused.

Current user instruction: pause all other model processing and compress **existing enhanced Lantau models first**. Peng Chau/Cheung Chau/Tung Chung acquisition and original-model installation workers are stopped; completed/partial evidence is retained in `docs/astra-city/government-import/islands-peng-cheung-tung-20261106/`. The interrupted Tung Chung job was fenced back to pending with the user's pause reason; all five remaining owned source leases were explicitly released. The older fixed-521 XL goal remains paused.

## Exact scope

`scope.json` selects internal project review sections 10.1–10.11 and 11.6–11.7, including Tung Chung, Chek Lap Kok airport and northeast Lantau. It excludes Peng Chau, Hei Ling Chau, Cheung Chau and all basic-only shapes. Region ownership uses the retained building footprint centroid and project review polygons, not an official surveyed island boundary.

- 14,580 existing building forms in these project areas.
- **6,787 installed enhanced sources:** 4,928 progressive GLBs + 1,859 embedded rendered meshes.
- 7,793 basic-only forms counted but excluded from compression.
- Four separately identified candidate tiers per source: original/lossless, high, balanced, lightweight.
- Expected total: **27,148 source/recipe variants**.

The existing compression branch already holds **19,688 complete matching variants** for 4,922 unchanged progressive sources. Those artifacts and receipts were restored byte-for-byte into ignored private staging and compared to the exact Neon results. Six newer progressive sources and 1,859 embedded meshes need four candidates each: **7,460 additional variants**. Completed matching work will be independently decoded/verified before reuse, rather than re-encoded.

The source freeze is `source-scripts/city/model-optimisation/staging/regional-lantau-installed-20261106-v2/sources.json`, SHA-256 `3f19a7ac3078cf1cecdf6a49c6235746db50434dd63040ec694b2c15d714947c`. It binds the current committed original assets, catalogue entries, tile records, coordinate metadata and actual renderer modules. Source commit is recorded inside the snapshot; unrelated later code/evidence commits do not change source identity. Original assets and live catalogues remain unchanged.

## Processing and evidence

Use the exact four recipes under `../regional-islands-20261106/recipes/`. `regional_batch.py` reuses the established codecs and pinned Neon source/variant/job/reservation machinery. `restore_completed_variants.py` is read-only in Neon and restores only hash-bound, Git-ignored private staging paths; it never overwrites differing bytes or grants review/publication status. Its bulk ignore-policy check uses `--no-index`, avoiding an expensive traversal of the large historical Git index. The initial interrupted ignore-check attempt copied no files or database records and is retained in the session log.

```sh
python source-scripts/city/model-optimisation/regional_batch.py launch \
  --snapshot source-scripts/city/model-optimisation/staging/regional-lantau-installed-20261106-v2/sources.json \
  --recipes docs/astra-city/model-optimisation/regional-islands-20261106/recipes \
  --output source-scripts/city/model-optimisation/staging/regional-lantau-installed-20261106-v2 \
  --batch lantau-installed-20261106 --workers 8
```

The actual committed renderer exports embedded meshes, including its existing foundations, normalized normals, UVs and window masks. These exports have identity scene pose in the existing local-world metre/HKPD coordinates. Source government geometry remains immutable. The gzip size of an embedded-mesh GLB export is a **new export baseline**, not the byte cost of its existing combined JSON tile. Report progressive GLB transfer measurements separately from embedded export measurements; do not claim whole-viewer network savings by summing them.

Smaller meshes can grow because of codec/container overhead. Preserve non-beneficial candidates and retain original bytes where smaller. Four tier labels do not promise four triangle counts. Offline byte/geometry checks are not visual, collision, physical-device or runtime publication approval. Outputs stay private and unreviewed; no compressed Lantau variants are served by the viewer yet. Embedded variants additionally need a compatible runtime routing path before publication.

Large generated GLBs and raw receipts are ignored and kept out of Git/Vercel. Final source/variant indexes, hashes and measured summaries belong here; durable object-storage delivery remains separate from local generation. No R2 migration or deployment is performed by this batch.

Validation before launch: 22 optimisation Python tests (18 passed, 4 dedicated-database skips), plus the previously passing shared-worker and Node codec/export suites. No AI geometry modelling or per-model AI call is used.

## Runner performance correction

The first lossless run exposed redundant per-model lease renewals. Its successful immutable results remain reusable; three interrupted own jobs were fenced back to pending. The runner now uses the existing 60-second renewal cadence and the compression branch’s single-snapshot ownership query. Every member must still belong to the exact active owner/token; ordinary claim, renewal, release, group-boundary ownership and job stale-token checks remain. Four actual pinned-database comparisons (active group, wrong owner, unknown token, released group) match the ordinary ownership checker; only two unique private test keys were used. See `ownership-readback.json`. A fresh source freeze will bind the corrected producer; source/recipe identities must compare identical before resuming.

## Final delivery and measurements

All 32 completed worker reports cover the exact frozen cohort and recipes. Final readback checked all 27,148 complete Neon rows, independent decoder-verified worker coverage, every immutable JSON receipt and 54,296 artifact/receipt file hashes. Checkpoint `613e74b1a2a9e574e54ecfad96639bebe66bee7568b141ca777ae18ae97cdb89` was read back exactly; summary SHA-256 `f99f784edfaf6d0699a5b27b734d84a8189547ce93a5250b0e5c8a8e34a435e3`. Zero active processing leases or running model jobs remained at completion. Original source assets, live model catalogues and model-review history are unchanged.

| Progressive GLB tier | Models | Smaller candidates | Potential gzip transfer saving, keeping original when smaller |
|---|---:|---:|---:|
| original | 4,928 | 179 | 6.12% |
| high | 4,928 | 787 | 20.21% |
| balanced | 4,928 | 1,085 | 24.66% |
| lightweight | 4,928 | 1,728 | 30.69% |

The progressive baseline is 17,797,559 gzip bytes. Embedded render exports are a separate 3,491,699-byte baseline, **not the transfer size of their existing combined map tiles**. Most tiny embedded candidates are larger: only 33/1,859 lightweight exports are smaller, yielding 2.68% potential savings against the export baseline when larger candidates retain their original export. Every non-beneficial outcome remains indexed; generation does not mean every model became smaller. Four tier labels do not guarantee different triangle counts or device-speed gains.

`variants.json.gz` contains all exact source/recipe/output identities, hashes, local asset/receipt paths and measured bytes/triangles/benefit flags. `sources.json.gz` preserves the exact original snapshot bytes. `summary.json` and `neon-sync.json` bind the completed cohort and checkpoint.

A portable data bundle (111,933,760 bytes) contains all 33,923 unique original/candidate geometry objects, the source/variant metadata and four recipes. See `portable-bundle.json` for its ignored local path and SHA-256, and `portable-bundle-readback.json` for full object and metadata readback. Binary assets are intentionally absent from Git; another machine needs that bundle or a separately configured asset sync. This is geometry/source/variant data, not a viewer/terrain package or approved runtime release.

Validation: **66 unit/codec tests passed, 15 dedicated-database tests skipped**, plus four actual ownership-equivalence cases. Both source/recipe identities remained identical across the bounded runner correction; no completed variant was re-encoded after that correction. No AI geometry modelling or per-model AI call.
