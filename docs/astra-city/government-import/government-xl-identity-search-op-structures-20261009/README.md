# Explicit government occupation-structure investigation

This follow-up uses fresh LandsD provider table queries to extend the 190-source identity research. It does not modify source geometry, source poses, viewer forms, live catalogues or prior receipts.

Neon job: `82104b45021078cccc85dd53bd1faa9e62659d608a5f7a138651654392db36b1`, exact result readback verified by `neon-sync.json`.

The [government Building service](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer) exposes an explicit `BuildingRelateOPStructure` table (1002): `BuildingCSUID` links to `BuildingStructureID`. Table 1003 provides structure details including occupation permit `OPNo`. This is stronger component-context evidence than proximity, name equality or shared generic building IDs. It is still not approval to combine unrelated bodies, suppress forms, or waive identity bounds.

Fresh queries cover 186 exact current CSUIDs (including the two type-conflict records), return 110 source relationships across 108 structure IDs, and 125 complete relationship rows. They identify 12 sources with additional current forms beyond their existing direct shared-OSM group:

| Source UID | Current name/context | Additional form UIDs |
|---|---|---|
| landsd/309823:0 | Academic Building | 31202, 26949 |
| landsd/283036:0 | The Pacifica Mall | 265478 |
| landsd/239351:0 | Olympian City 2 | 239350, 72277 |
| landsd/147996:0 | Unnamed tower; OP K30/60 | 147734 |
| landsd/285139:0 | The Arcade Cyberport | 320304 |
| landsd/239350:0 | Olympian City 2 | 239351, 72277 |
| landsd/232526:0 | Block 2 | 263221 |
| landsd/118003:0 | Unnamed tower; OP K300/63 | 118128 |
| landsd/232089:0 | Tower 1 | 259038 |
| landsd/322573:0 | Opus Hong Kong | 322822 |
| landsd/236138:0 | CityU Yeung Kin Man Academic Building | 253260, 253461 |
| landsd/258419:0 | Greenfield Shopping Arcade | 228599 |

All twelve complete original source projections were measured against their complete provider relationship group. None passes all existing 95% target coverage, 10 m maximum extent, 1 m² unrelated excess overlap and whole GeoRef cell rules. All current neighbour forms remain present; complete linked groups were retained even outside original mesh bounds.

Two paired structures had promising single-source results: no significant extent/unrelated overlap problem, but their government source is delivered in two files. Their missing counterparts were recovered from fresh current government ZIP range downloads and verified against the **exact previously indexed SHA and byte count**, with pinned ETag and directory SHA. No mesh was edited or composite mesh created. Full projections of both original files were then measured:

| Official structure | Complete original pair | Coverage | Maximum extent | Unrelated excess overlap | Remaining reasons |
|---|---|---:|---:|---:|---|
| 5216458, OP K30/60 | 147996 + 147734 | 94.818965% | 3.411513 m | 0.536054 m² | Coverage below 95% |
| 1645937, OP K300/63 | 118003 + 118128 | 94.598802% | 2.407634 m | 1.901111 m² | Coverage below 95%; unrelated overlap above 1 m² |

These are concrete source-specific follow-up leads, not installed models. The first pair needs positive source evidence for its uncovered areas or a genuinely more complete original government source format/revision. The second also needs ownership or corrected source evidence for its excess intersection with retained neighbours. Threshold relaxation, GIS polygon inflation and component suppression are not approved routes.

Exact old GeoRef prefixes for the four unmapped sources were queried against `BuildingWorksHistory` (1000), `BuildingName` (1001) and `BuildingRelateOPStructure` (1002): all returned zero records. This does not prove demolition or obsolescence; the documented previous-CSUID reassignment/merge/split history is not exposed in these public tables. The four remain source-version-specific GIS lineage investigations, with their originals still available in current government packages.

`actionable-findings.json.gz` and `result.json` preserve all 190 relationship outcomes, the twelve detailed measurements, both recovered source pairs, raw query/request receipts and exact evidence references. No permanent rejections or installation credit were recorded. AI was used for research interpretation and coding; no AI geometry modelling or script AI-service calls occurred.
