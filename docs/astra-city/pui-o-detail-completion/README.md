# Pui O detailed-model completion audit · HKS-171

**Staged source package; live coverage remains 681/919 (74.10%) until root publication.** The later terrain-correction pass below now makes all four recovered models candidates for integration together with two nested terrain patches and one guarded estimated-base update. The original availability/terrain findings are retained as before-state evidence. This pass audits the existing four-sheet, 35 m buffer selection; it does not enlarge the denominator or imply that all Pui O, wetlands, village routes or south Lantau are ready.

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


## Source-backed terrain correction for all-four integration

The two source-model roof conflicts are now resolved in the **staged** corrections. Three exact adjoining terrain sheets (`14-NW-6B`, `13-NE-5D` and `13-NE-5B`) were needed: the northern end of `landsd/182169:0` crosses the 5B/5D source-sheet boundary. The existing range downloader retained only the original TERRAIN glTF and buffer members, transferring **5,089,160 bytes**. Their original archives, source hashes and the derived photograph-free terrain descriptors are retained. Existing government building heights are unchanged.

`terrain-refinements.json` contains two disjoint child grids, **4,002 vertices and 85,380 bytes**, attached to the existing `city/data/terrain-pui-o.json` parent. Its guarded SHA-256 is `9080c264dfa64eaaf9c1164a6806a98b05960c6247fb86840948eef2b1ad027e`. Child `coarseCells` address that parent's **5 m** lattice. Native TIN heights are sampled barycentrically at 1 m intervals; this is sampling spacing, not claimed survey accuracy. A 7.5 m outer transition exactly matches existing rendered parent triangles. Raw water classifications and rendered water heights are preserved, with zero water-node changes.

| Target UID | Highest original roof | Previous footprint terrain | Corrected footprint terrain |
|---|---:|---:|---:|
| landsd/11179:0 | 9.692 m | 11.441–15.374 m | 4.664–8.363 m |
| landsd/182169:0 | 79.754 m | 78.000–81.365 m | 75.547–78.069 m |

Heights use HKPD. All four new models pass exact full-footprint terrain/roof screening after these corrections. The neighbour check also covers every live building intersecting the two child grids: **six forms including the four models**, with no new roof or floating-base flags after the dependent update below. The maximum error across **708 half-metre boundary samples** is below 0.000001 m.

One existing derived estimate must move with the corrected terrain: open-sided structure `landsd/182182:0` has both official vertical fields null and an existing terrain-estimated base of 78 m. `building-estimate-updates.json` guards its UID, CSUID, previous base, null source elevations, absence of a detailed model and unchanged **3 m estimated height**, then changes only its derived base to **75.849 m**. Without that paired correction the old estimate would float above the corrected source ground. `diagnostic-updates.json` records only derived flags after models, patches and the dependent estimate are applied together.

Root should now use the **full four-model `compact/catalogue.json`**, together with `terrain-refinements.json`, `building-estimate-updates.json` and `diagnostic-updates.json`. The earlier two-model `catalogue-integration-candidate.json` remains a before-terrain staging option, not the final atomic package. The shared nested renderer must exclude the corresponding parent cells and draw each child exactly once. No live file has been changed by this subtask.

The actual shared renderer/sampler checks passed for all 4,002 child vertices, 350 boundary nodes and 18 interior rays: maximum ray/height error was 0.0000034 m, no duplicate parent ground remained and water classification stayed unchanged. All four actual source models were loaded into collision records. The retained **555.066 m public beach route** passed forward and reverse with 8,546 real Navigation update frames each and zero waypoint resets. These are CPU/runtime checks, not new browser screenshots or device performance measurements. Browser day/night/mobile acceptance and publication remain with root.

Reproduce the additional pass:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/pui-o-detail-completion/terrain.py fetch
/tmp/astra-city-venv/bin/python source-scripts/city/pui-o-detail-completion/terrain.py
/tmp/astra-city-venv/bin/python source-scripts/city/pui-o-detail-completion/terrain_verify.py
node source-scripts/city/pui-o-detail-completion/terrain_runtime.mjs
/tmp/astra-city-venv/bin/python source-scripts/city/pui-o-detail-completion/test_terrain.py
```

Six additional terrain checks pass alongside the six original source-audit checks. Evidence: [native preparation](terrain-preparation.json), [full-footprint/neighbour/seam review](terrain-verification.json) and [actual nested renderer/route checks](terrain-runtime.json). Original 232 unavailable forms and two strict source-match failures remain unchanged; the package raises attainable checked-slice detail to 685/919 only after root integration, not 100%.
