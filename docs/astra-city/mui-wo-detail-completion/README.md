# Mui Wo detailed-source completion · HKS-192

Astra's bounded source audit found **312 additional exact government building models** beyond the existing 1,327. The compact additions total **495,196 bytes**, 24,871 triangles and 1,708,206 decoded geometry bytes. They are staged and validated with the existing runtime loader, **not yet published or accepted against final rendered terrain**.

| Coverage inside the unchanged Mui Wo envelope | Before | Potential after integration |
|---|---:|---:|
| All 2,408 footprint forms | 1,327 (55.1%) | 1,639 (68.1%) |
| Government `Tower` category, 1,648 forms | 1,322 (80.2%) | 1,628 (98.8%) |
| Government `Podium` category, 11 forms | 5 | 11 (100%) |
| Temporary structures, 522 forms | 0 | 0 |
| Open-sided structures, 227 forms | 0 | 0 |

`Tower` is the source dataset category, including ordinary small village buildings; it does not mean all these buildings are skyscrapers. “Potential” means safely matched and packaged, not live or region complete.

The earlier extension intentionally covered seven populous source sheets. This pass intersects **every unchanged footprint**, including its boundary, against all official sheet polygons. That identifies 31 relevant sheets: seven existing sheets reused, 24 additional sheets inspected. It therefore includes the small surrounding settlements within the original 4 × 4 km envelope instead of stopping at town-centre sheets.

## Exact remaining ledger

[ledger.json](ledger.json) contains one outcome for every one of the 2,408 source UIDs. After the staged additions, 769 remain:

- **757 have no same-GeoRef building model in any inspected sheet:** all 522 temporary structures, all 227 open-sided structures, and eight `Tower` records.
- **12 `Tower` records have same-GeoRef source geometry but fail the existing conservative spatial screen.** [Measurements](rejected-match-measurements.json) retain overlap, centroid distance and footprint/model areas. Ten fail 50% overlap; two exceed 10 m centroid separation and have much larger model hulls than the selected footprint.

The source model ID alone is not enough to suppress a footprint. This pass keeps the established exact GeoRefNo + ≥50% overlap of the smaller footprint + ≤10 m centroid distance + one unambiguous BuildingCSUID/component rule unchanged. No procedural building, estimated roof or rejected source geometry is counted as a detailed government replacement. Absence in this inspected non-textured product does not prove absence from every other government 3D product or future revision.

## Sources and reproducibility

The footprint denominator remains the retained government Building selection in `source-scripts/city/mui-wo-buildings/landsd-mui-wo.json.gz`. The detailed source is the [Lands Department non-textured 3D Visualisation Map](https://portal.csdi.gov.hk/geoportal/?datasetId=landsd_rcd_1742809441342_98380), using its [official sheet index](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0).

The current index was retrieved on **7 September 2026 Hong Kong time**. Its 46 returned sheet records match the independent service count; sheet membership and revisions are unchanged from the retained index. The explicit index query, response, count request and hashes are retained in the source package. Source sheet revisions for the additions are 29 September 2025 and 11 May 2026 Hong Kong time. Government content remains subject to [CSDI terms](https://portal.csdi.gov.hk/csdi-webpage/doc/TNC).

The unchanged shared downloader fetched only original BUILDING/TERRAIN glTF/bin members using validated HTTP byte ranges. Additional transfer was **49,411,509 bytes**, including ZIP directories and terrain companions required by the existing stage adapter. Compact source caches are **47,566,480 bytes**. They are explicitly derived caches rather than falsely labelled complete original archives. Per-entry hashes, ZIP CRC, ETag and range records are retained; all original extracted entries remain available. Terrain companions are not published or used to modify current terrain in this pass. No reference imagery was used or modified.

The existing packer indexes only bit-identical complete vertex tuples. It preserves original expanded attributes, normals, colours, materials and native node transforms; coordinates remain EPSG:2326 / HKPD, translated once by `[-834500, 0, 816500]`. The 1,327 embedded models remain unchanged. New assets use the existing progressive catalogue schema; no second renderer, physics implementation or new decoder is introduced.

From the Astra worktree:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-detail-completion/run.py verify_index
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-detail-completion/run.py fetch
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-detail-completion/run.py build
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-detail-completion/audit_rejections.py
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-detail-completion/test_completion.py
/Users/williamli/.nvm/versions/node/v24.17.0/bin/node source-scripts/city/mui-wo-detail-completion/runtime_verify.mjs
```

## Validation and integration boundary

Five focused tests pass: exhaustive UID accounting/preservation; source identity and matching; original node/material/GLB integrity; count reconciliation; and all relevant sheets inspected. The actual shared `prepareModelCatalogue` and `loadOfficialModel` accept **all 312 assets**, validating source identity, recorded elevations, SHA/bytes and native bounds. Every model passes source-UID ray picking, actual triangle collision and empty space above the roof. Expanded source attributes are checked bit-for-bit by the shared packer. See [runtime-verification.json](runtime-verification.json) and [compact-assets.json](compact-assets.json).

All-model resident budget measured through the runtime adapter is **27,986,968 bytes**; normal progressive loading must still enforce its existing per-device budget. This is a CPU correctness check, not a mobile frame-rate or GPU visual acceptance claim.

Root integration must preserve the original form/height attributes, copy `compact/` to a separate `official-models/mui-wo-completion/` path and append its catalogue to the shared manifest registry. It must load/test representative clusters against current terrain before suppressing fallback geometry, preserve existing model budgets and terrain/hydro, and record actual browser evidence. The separately staged `b90c15f5` terrain corrections are not included here. HKS-192 stays open; this hand-off does not claim 100% detailed coverage or full Mui Wo completion.
