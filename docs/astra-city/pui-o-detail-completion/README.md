# Pui O detailed-model completion audit · HKS-171

**Staged source package; live coverage remains 681/919 (74.10%).** This pass audits the existing four-sheet, 35 m buffer selection; it does not enlarge the denominator or imply that all Pui O, wetlands, village routes or south Lantau are ready.

The 238 fallback forms are 136 temporary structures, 91 open-sided structures and 11 towers. Both current official source families were checked: [non-textured models](https://portal.csdi.gov.hk/geoportal/?datasetId=landsd_rcd_1742809441342_98380) and [individualised models](https://portal.csdi.gov.hk/geoportal/?datasetId=landsd_rcd_1671676915450_88604). Object-ID queries verify that every one of the 15 sheets intersecting the original selection plus buffer was retrieved. Their complete original ZIP directories were inspected, including all glTF categories, rather than assuming that unrequested adjacent sheets are empty. The four already-imported sheets remain at 11 May 2026 HKT revisions. Neighbours include September 2025 non-textured and June 2024 individualised revisions, recorded per sheet.

The [per-UID completion ledger](completion.json) accounts for all 238 forms:

| Outcome | Forms | Action |
|---|---:|---|
| No exact-reference model in either current local source family | 232 | Retain government footprint/height fallback |
| Original adjacent-sheet model found; current terrain screen passes | 2 | Staged for browser review and integration |
| Original adjacent-sheet model found; current terrain conflict | 2 | Retain fallback until source terrain is reviewed |
| Existing exact-reference model fails unchanged geometry screen | 2 | Retain fallback; no relaxed matching |

Thus 100% detailed government coverage is not attainable merely by downloading more models from these checked sources. These results do not rule out future source updates or another official dataset. They also do not mean those 232 footprint records disappear: their basic source forms remain present.

## Four recovered original models

| Source UID | Model | Sheet | Current terrain result |
|---|---|---|---|
| landsd/75329:0 | B149721157701062G0 | 13-NE-5B | Roof above sampled terrain |
| landsd/77662:0 | B149931139601062G0 | 13-NE-5D | Roof above sampled terrain |
| landsd/11179:0 | B162141077501062G0 | 14-NW-6B | Source roof 9.692 m HKPD; current terrain 9.941–15.166 m |
| landsd/182169:0 | B149801139701062G0 | 13-NE-5D | Source roof 79.754 m HKPD; current terrain 78.000–82.156 m |

All four pass the unchanged exact GeoRefNo, at least 50% smaller-footprint overlap and at most 10 m centroid-distance screen against the retained source UID/BuildingCSUID. The two terrain conflicts were already flagged in the original Pui O buffer audit. Model heights are preserved; raising them to hide a terrain error is not part of this package. The [rejected-match diagnostics](rejected-matches.json) retain numerical evidence for the other two source models that still fail the screen.

The full staged catalogue is `source-scripts/city/pui-o-detail-completion/compact/catalogue.json`. The conservative `catalogue-integration-candidate.json` contains only the two assets without a roof/terrain conflict; their `placementReviewed` flags remain false until browser/architectural review. If those two are integrated, the same selection reaches **683/919 (74.32%)**. If all four are subsequently accepted after terrain work, it reaches **685/919 (74.54%)**. Neither number is claimed as currently live.

Original glTF nodes, material/vertex-colour facts, binary attributes and HKPD transforms are retained. The existing Central packer creates four gzip GLBs totalling **10,702 bytes and 688 triangles**. It verifies expanded attributes bit-for-bit. Source caches, original glTF/buffers and source/packed hashes remain alongside this package. No source photo is required by these four non-textured models; no geometry is procedurally invented.

## Verification and transfer accounting

Six focused Python checks pass: exact fallback coverage, complete index ID sets, complete classic/ZIP64 directories, unchanged match thresholds, source/packed hashes and exclusion of terrain-conflicted assets. The [runtime record](runtime-verification.json) uses the actual shared compact loader, verifies source UID ray picking, exact model triangle collision and clear space above the roof for all four assets, then samples the current Pui O terrain across all source mesh vertices. These are CPU checks; no new browser screenshot, GPU frame-time or architectural acceptance is claimed.

Successful source-directory ranges total **2,201,990 bytes** across both families; the four model candidates required **210,017 bytes** of additional range requests. This is not the entire investigation's traffic: an initial ZIP64 offset bug read **264,427,785 unnecessary bytes**, plus its tail, before a directory-format error. Those bytes were discarded without importing assets. [The incident record](download-incident.json) documents it and the diagnostic/cancelled retry. The corrected reader handles ZIP64 offsets and rejects directory/range responses above 4 MiB before reading, avoiding that failure on a rebuild. Retained directory bytes are original source slices, not altered ZIP archives.

## Reproduce and integrate

From the Astra worktree:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/pui-o-detail-completion/index.py
/tmp/astra-city-venv/bin/python source-scripts/city/pui-o-detail-completion/audit.py
/tmp/astra-city-venv/bin/python source-scripts/city/pui-o-detail-completion/audit.py --individual
/tmp/astra-city-venv/bin/python source-scripts/city/pui-o-detail-completion/prepare.py
node source-scripts/city/pui-o-detail-completion/runtime_verify.mjs
/tmp/astra-city-venv/bin/python source-scripts/city/pui-o-detail-completion/finalise.py
/tmp/astra-city-venv/bin/python source-scripts/city/pui-o-detail-completion/test_audit.py
```

The audit reuses retained directories on ordinary rebuilds. A source refresh must invalidate a directory cache when the index revision/download URL changes; source updates should be reviewed rather than overwriting the previous provenance silently. Root integration should first inspect the two terrain-safe candidates in the browser, then use the existing progressive catalogue loader without duplicate footprint geometry. The two conflicted models require adjacent-sheet source terrain work before promotion. Shared runtime, live tiles, manifest, source elevations, existing 681 models and region-readiness trackers have not been modified by this subtask. Root owns the HKS-171/parent/milestone update and live integration.

Produced by the Astra Pui O detail-completion subagent. No archived Lantau map imagery was used as precise current geography.
