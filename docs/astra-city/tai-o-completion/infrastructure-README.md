# Tai O infrastructure and stilt evidence · HKS-170

This slice restores the five original infrastructure meshes omitted from the earlier Tai O building pass. It preserves their 2,806 triangles, 8,418 expanded vertices, source colours, normals and absolute HKPD placement. Two public bridges receive 51 selected source deck triangles for walking; two **estimated** public approaches connect Tai Chung Bridge to the lower game terrain. This is a bounded infrastructure improvement, not a complete survey of Tai O's private decks or house piles.

## Source geometry and identity

The input is the already retained Lands Department **3D Visualisation Map (Non-textured models)**, dataset `landsd_rcd_1742809441342_98380`, sheets `9-SW-23A/B`. Both source revisions are `2026-05-10T16:00:00Z` (11 May HKT). All five infrastructure entries are in 23B; 23A has none. The cache ZIPs retain original unmodified glTF/bin entries, rather than the original archive photographs. Per-entry and cache SHA-256 values are in the staged payload and existing source download manifests.

[Official dataset metadata](https://portal.csdi.gov.hk/csdi-webpage/metadata/landsd_rcd_1742809441342_98380/html) identifies the source. The existing verified glTF parser/baker is reused, with the original node hierarchy followed by `x = E − 834500`, `y = HKPD`, `z = 816500 − N`. No source vertex is lifted, simplified or rescaled. The city uses the retained vertex colours with a matte presentation material.

| Source model | Identified structure | Source triangles | Generic OSM proxies replaced |
| --- | --- | ---: | --- |
| `I038171281003063C1` | Tai Chung Bridge | 451 | `way/507688251` |
| `I039851299803063C0` | Sun Ki Bridge | 254 | `way/244106712` |
| `I041061300803063C0` | Small surveyed link east of Sun Ki Bridge; individual access unverified | 36 | None |
| `I043291261802063C0` | Tai O Road bridge near Lung Tin | 44 | `way/820104877`, `way/1337775937` |
| `I044891273603063C0` | Eastern Tai O footbridge; full approach access unverified | 2,021 | `way/307417765` |

Replacement is local and explicit. Three bridge paths lie entirely inside the projected source mesh. The road/sidewalk pair has approximately 86.6%–86.7% exact coverage and full coverage with a stated 1.5 m map-alignment tolerance. Source geometry remains unmoved. The renderer suppresses a proxy only after the whole replacement package validates and loads; failed loads retain existing bridges. Source-first and proxy-first arrival orders are tested.

## Walking surfaces and approach

The [official Tai Chung guide](https://www.islands.gov.hk/en/explores-tai-o-tai-chung-bridge-tai-o-creek-pedestrian-bridge.php) confirms the pedestrian connection between Market Street and Wing On Street. Its 43 reviewed deck triangles cover the full mapped bridge centreline and retain elevations of 2.629–4.520 m HKPD. The Wing On landing is 4.058 m; rail caps, drawbridge towers, undersides and vertical walls are excluded from floor selection.

The [official Sun Ki guide](https://www.islands.gov.hk/en/explores-tai-o-sun-ki-bridge.php) confirms the Kat Hing Street–Sun Ki Street connection. Its eight deck triangles retain 2.923–4.453 m HKPD. The retained OSM record has `access=no` with the more specific `foot=yes`; only pedestrian use is accepted. The mapped centreline comes within 0.168 m of a deck edge, so it is not automatically a safe guided route for a 0.55 m actor. The other three source meshes render with their original supports but do not acquire public walking approval from their geometry alone.

The original OSM Wing On shortcut crosses a solid source-mesh railing. Nearby iB1000 `STP` 1109131981/1109131982 and `PA` 1109097753/1810305569 locate public access northeast of the bridge, but the 3D source retains railing across that exact plan strip. The two sources disagree. The final connector uses the existing southeast mesh opening at `[-30659.7580, 3685.2581]`, preserving every source railing and original OSM node. Its intermediate horizontal alignment is explicitly estimated, at most 1.7284 m from the original shortcut; full source IDs, linework and hashes are in `route-entry.json`.

The visible Wing On approach has four estimated 0.2145 m risers, approximately 0.6047 m treads and a 0.8 m level landing at 3.2 m HKPD. It joins the original 4.058 m deck and the current public-street terrain. The short Market Street landing follows the unchanged public source edge `way/377823160`, joining the 2.629 m deck to terrain. Neither approach provides surveyed stair dimensions or an accessible-ramp specification. Both are explicitly identified as estimates in the source card and evidence inventory.

`walkingSurfaceFor(record)` derives approach support directly from the existing `geometryFor(record)` Float32 deck triangles. Rendering and collision share those vertices. Up to 2 mm edge tolerance handles Float32 coordinate rounding; it does not open private paths or relax building collision. Source models, public source decks and the estimated approaches have separate diagnostic counts.

Two canopy roofs over the entry are retained: `landsd/169618:0` and `landsd/182398:0`. Current iB1000 `Building.gml` confirms their exact building IDs, `OS` type, existing status and `LASTUPDATEDATE=20260729`; both raw base and roof levels are NULL. Their footprints overlap the corresponding official building records by more than 99.9996%. The shared visual/collision descriptor sets only their **estimated** base to the verified 4.058 m deck, retaining the existing 3 m illustrative clearance. The original records, footprint geometry and NULL measured heights remain unchanged. The estimate is disabled if a later record contains measured heights, a different identity or a detailed model; `describeBuilding(...).placementNote` exposes the explanation.

## Waterfront and stilt limitations

The current central selection contains 1,030 official forms: 544 Tower, 427 Temporary Structure and 59 Open-sided Structure. There are 532 detailed building models, all matched to Tower records. The [official Islands stilt-house guide](https://www.islands.gov.hk/en/explores-tai-o-tai-o-stilt-houses.php) documents timber-pile houses, platforms and connecting boardwalks generally; it does not supply individual pile coordinates, bed levels or public access for each private platform.

The validated mapped-water mask intersects 106 selected footprints by more than 1 m²: **99 Temporary, six Open-sided, one Tower**. Only one has detailed source geometry; 63 are more than 99% covered by mapped water. All 106 have rendered geometry above the illustrative −4 m bed; 102 are above a diagnostic 0.3 m water plane. These figures identify remaining unsupported/hovering presentations, rather than proving exact stilt construction. The one detailed model includes some geometry below its recorded building base, but that alone does not identify surveyed piles. Full IDs and measured/rendered distinctions are in [the evidence inventory](infrastructure-evidence.json).

The five infrastructure meshes already retain their source supports, including eastern bridge piers extending to −5.509 m HKPD. **No new house piles were invented.** Per-house pile positions and dimensions remain unverified, and mapped-water overlap does not justify adding timber posts beneath every canopy or overhang. Channel opening and source placement improve the waterfront; surveyed house-pile architecture is still a limit.

The [government opening notice](https://www.info.gov.hk/gia/general/202605/03/P2026050300320.htm) confirms that Yim Tin and Po Chue Tam bridges opened on 4 May 2026. They are not among these five retained 3D meshes. Their existing mapped geometry remains separate. The [iB1000 feature codebook](https://www.landsd.gov.hk/doc/en/mapping/digital-map/common/feature/ib1_gml_mf.pdf) defines `FBR` footbridge linework, `PA` pavement margins and `STP` steps. Source GML zero Z values must not be treated as surveyed HKPD elevations. A multipart FBR feature has a 90.141 m gap between components; concatenating it incorrectly creates three apparent closed bridge polygons. Strict parsing retains 102 separate line segments and **zero** closed polygons. The false outlines are not published.

## Reproduction and acceptance

From the Astra worktree:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-completion/route_entry.py
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-completion/infrastructure.py --publish
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-completion/infrastructure-test.py
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-completion/infrastructure-evidence.py
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-completion/infrastructure-plans.py
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-completion/infrastructure-plot.py
node --test 3d-viewer/city/tests/infrastructure.test.js 3d-viewer/city/tests/bridges-render.test.js 3d-viewer/city/tests/building-geometry.test.js
```

The publisher reuses the original cache, verifies reviewed glTF hashes, writes `city/data/bridges-tai-o.json`, adds the `manifest.bridgeModels` entry, rebuilds the estimated approach from source floor/current terrain and generates the guarded `tai-o-estimates.js`. It changes no canonical building tile or source-reference file. The source-only payload is `infrastructure-models.json.gz` (96,013 bytes); the published package also contains approach and estimate metadata.

Five independent Python source checks pass, including every transformed native vertex and original colour. Nine focused JavaScript checks plus the existing bridge/building checks pass: source geometry, floor eligibility, below/above slab collision, both load orders, atomic malformed rejection, exact approach geometry reuse, camera dimensions and scoped canopy estimates. The [2,700 × 2,100 source contact sheet](infrastructure-model-contact-sheet-2700x2100.png) was inspected; green faces are the selected source floors. The full 607 m public route now passes actual Navigation replay in both directions and the independent browser replay. See [route acceptance](route-README.md) for the exact counts, water-rejection cases and explicit connector limitations.
