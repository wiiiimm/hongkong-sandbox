# Tai O detailed-model completion audit · HKS-170

Astra audited **all 498 remaining basic forms** in the existing **1,030-form Tai O slice**, without changing its boundary, live assets or existing 532 detailed models. Eleven complete neighbouring official archive directories cover every whole selected footprint. The source index was re-read on 7 September 2026 and checked for truncation. This is an expansion audit, not a change to the previously reviewed HKS-170 village acceptance or a claim that all north-west Lantau is complete.

## Result

| Classification | Forms |
|---|---:|
| Previously delivered detailed models | 532 |
| Newly source-matched and packed models, staged only | 7 |
| Exact-identity candidates rejected by existing footprint matching screen | 3 |
| No matching building-model entry in the inspected product/sheets | 488 |
| **Retained selection** | **1,030** |

The seven additions would move source-model availability from **51.65% to 52.33% (539/1,030)** after safe integration. This does **not** achieve 100%. The 488 directory-absent records consist of **427 Temporary Structures, 59 Open-sided Structures and two Towers**. They remain real government footprint records and must stay rendered; missing detailed geometry is not permission to drop them. This audit establishes absence of an exact GeoRef model in the inspected non-textured product, not absence from every government dataset or survey.

The two Tower records with no directory candidate are `landsd/286951:0` and `landsd/286952:0`. The three rejected candidates have smaller-footprint overlaps of **0%, 10.94% and 4.03%**, below the existing 50% threshold. Their centres are nearby but that alone does not prove a safe replacement. [Per-model mismatch metrics](match-failures.json). No threshold was relaxed and no inferred geometry was labelled government detail.

[Complete per-UID ledger](audit.json) includes all 1,030 forms, exact source IDs, classification, candidates and terminal reason. Existing source building outlines, null/recorded heights, model IDs, origins and vertical datums are unchanged.

## Seven staged source models

| UID | Source sheet | Note |
|---|---|---|
| landsd/14899:0 | 9-SW-18D | Terrain conflict below |
| landsd/58930:0 | 9-SW-18D | Source match and loader checks pass |
| landsd/94903:0 | 9-SW-18D | Source match and loader checks pass |
| landsd/162085:0 | 9-SW-18D | Source match and loader checks pass |
| landsd/211618:0 | 9-SW-22B | Tai O Heritage Hotel; terrain conflict below |
| landsd/96188:0 | 9-SW-23D | Source match and loader checks pass |
| landsd/211900:0 | 9-SW-23D | Buddhist Fat Ho Memorial College |

Compact payload: **29,564 gzip bytes**, **164,256 decoded GLB bytes**, **2,358 original triangles**. The existing shared packer indexes only bit-identical full vertex tuples; no simplification, height shifts, new material interpretation or source geometry invention. Original node/material metadata and expanded position/normal/colour bits survive the actual app GLTFLoader. Shared runtime/picking/collision tests pass for all seven. [Packing evidence](staged-additions.json), [decoder evidence](compact-verification.json), [runtime evidence](runtime-verification.json).

**These assets are staged, not live, and not yet browser/terrain accepted.** Two roofs are below current terrain sampled at their footprint centres: `landsd/14899:0` roof 15.9005 m HKPD vs terrain 16.2067 m, and Tai O Heritage Hotel roof 26.0448 m vs terrain 28.9878 m. Do not raise their source geometry. The retained adjacent-sheet terrain TINs are available for a later terrain correction; the other five centre samples are not proof of whole-footprint/foundation acceptance either. Actual source TIN samples put the ground at **11.7084 m** and **17.6761 m** respectively, below those roofs, identifying a live terrain discrepancy rather than a reason to lift the buildings. All seven roofs clear their own TIN at these centre samples. [Source terrain diagnostics](source-terrain-probes.json). All `placementReviewed` flags remain false. No GPU, day/night, mobile or frame-rate claim is made for this package.

## Provenance and efficiency

Sources: [official non-textured dataset](https://portal.csdi.gov.hk/geoportal/?datasetId=landsd_rcd_1742809441342_98380), [sheet index](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0), [LandsD overview](https://www.landsd.gov.hk/en/survey-mapping/mapping/3d-mapping.html), [CSDI terms](https://portal.csdi.gov.hk/csdi-webpage/doc/TNC). Footprints reuse the retained **19 August 2026** territory snapshot and original Tai O selection. No archival reference image was used or modified.

All two existing source caches and staged manifests were reused. Complete ZIP directories for nine neighbouring sheets transferred **589,824 bytes**. Only the seven candidate building models and terrain required by the existing shared staging interface were subsequently fetched from three sheets (**2,326,354 transferred bytes**, **2,066,791 bytes of derived source ZIP caches**). Original glTF/bin entry CRCs and SHA-256, source URL, revision, HTTP ranges, ETag and Last-Modified are retained. Derived ZIP hashes are explicitly not complete original archive hashes. No textures or imagery were extracted or requested for live use.

`source-scripts/city/tai-o-detail-completion/compact/catalogue.json` is compatible with the existing progressive model loader. Root must integrate through that loader after placement review; do not modify broad live tile geometry or republish the old Mui Wo-only pipeline. No live manifest, runtime, tile or terrain was changed here.

## Reproduce

From the isolated Astra worktree:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-detail-completion/audit.py
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-detail-completion/stage_additions.py
node source-scripts/city/tai-o-detail-completion/compact-test.mjs
node source-scripts/city/tai-o-detail-completion/runtime-test.mjs
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-detail-completion/terrain_probe.py
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-detail-completion/test_audit.py
```

Audit refresh resets intermediate candidate classifications; run staging afterwards to restore the final reason ledger. Cached original entries are reused on reruns. Six coverage/provenance/identity tests and both actual-loader verification scripts pass. Terrain-conflict assertions deliberately keep the two outstanding cases visible; revise only with a documented terrain fix.
