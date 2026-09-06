# Mui Wo building coverage and official 3D sample review

Produced by GPT-6 Astra, 6 September 2026, in `codex/astra-hong-kong-city`. This independent review distinguishes the original OSM coverage from subsequent official-data integration. It does not declare every village, building, coastline or pedestrian route fully reviewed.

## The original missing-building report was substantiated

The user supplied the study envelope `[113.97922444961371, 22.249711576500182, 114.0180525556901, 22.28564402349982]` (west, south, east, north). This is a study rectangle, not an administrative or village boundary.

The frozen baseline in `current-building-diagnostic.json` contains **318 generated building forms** in that envelope, derived from **330 retained OSM building objects**. All 12 differences are accounted for by the previous importer: eight roof-only objects, three construction objects and one footprint below its former 8 m² threshold. There were no unexplained source-to-tile omissions. The baseline territory manifest held 117,062 forms and has SHA256 `c16adcfc87621fb8cd6dd826697b3d897ee087b734dcf7514950c051fc657552`.

The baseline browser loaded all 13 requested Mui Wo neighbourhood tiles, with zero pending or failed tiles and zero page errors. Buildings were enabled. Its wider camera view contained 1,834 forms. Thus the large missing village clusters were primarily a source-coverage problem, rather than a failure to request or display the original tiles. `browser-current.json` and `mui-wo-current-1600x1000.png` retain this **before-integration** evidence; these figures must not be presented as the current post-integration inventory.

The independently retained [official Building Outline service](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0) returns **2,408 records** for the exact envelope: 1,648 towers, 522 temporary structures, 227 open-sided structures and 11 podiums. The source is `Building_Outline_Public_v20260819`. Full IDs and a separate count query were checked by the acquisition agent. All types are included in this comparison; 441 records lack at least one source height.

A conservative gap screen finds **1,894 official footprints with no original generated footprint within 3 m**. This is a diagnostic, not the production overlap/deduplication rule. It deliberately leaves nearby or overlapping ambiguous cases out of the clear-gap count.

| Source settlement point, 250 m review circle | Original forms | Official forms | Clear gaps |
| --- | ---: | ---: | ---: |
| Pak Ngan Heung / 白銀鄉 | 3 | 166 | 163 |
| Wang Tong / 橫塘 | 0 | 166 | 166 |
| Tai Tei Tong / 大地塘 | 35 | 459 | 396 |
| Luk Tei Tong / 鹿地塘 | 80 | 195 | 67 |
| Tsoi Yuen / 菜園 | 3 | 270 | 266 |
| Mui Wo Kau Tsuen / 梅窩舊墟 | 2 | 198 | 195 |

The circles use retained OSM settlement nodes and overlap. They are not village boundaries; do not add their counts. `official-comparison.json` retains all 19 review circles, source IDs and each clear-gap BuildingCSUID. `mui-wo-village-source-gaps-2520x1980.png` and its SVG show four representative clusters at a consistent scale. Their geometry comes from retained vector sources, not traced satellite photographs.

## Heights and terrain require separate treatment

The [Building dataset metadata](https://portal.csdi.gov.hk/csdi-webpage/metadata/landsd_rcd_1637211194312_35158/html) and the retained source specification identify EPSG:2326 and approximate source BaseHeight/TopHeight above Hong Kong Principal Datum (HKPD). These are not floor counts or exact new surveys.

On the original 70 m terrain, 686 source tops were below the rendered surface at the footprint representative point, and 715 source bases differed from the surface by over 5 m. These numbers are preserved in `terrain-comparison.json`; they are **source-versus-terrain conflicts**, not evidence of underground buildings. No source elevations were moved by this review. Root's newer full-footprint and 5 m audits supersede this initial single-point terrain screen for live acceptance.

## A real official 3D tile is available and verified

The requested [Lands Department 3D Mapping page](https://www.landsd.gov.hk/en/survey-mapping/mapping/3d-mapping.html) links to the 3D Visualisation Map. The requested CSDI ID, `landsd_rcd_1742809441342_98380`, is specifically the **Non-textured models** dataset. The [official catalogue](https://data.gov.hk/en-data/dataset/hk-landsd-openmap-3d-visualisation-map-non-textured-models) offers GLTF, MAX and FBX. The metadata revision inspected was 28 August 2026. Model coordinates use EPSG:2326 and heights above HKPD; the tile-index polygons themselves are EPSG:4326.

A point query at a retained mapped public toilet near Pak Ngan Heung returned tile **10-SW-12C**. `model-index-request.txt`, `model-pak-ngan-heung-index.json`, `model-index-layer.json` and `model-service-metadata.json` retain that discovery. The tile revision timestamp is 10 May 2026 16:00 UTC, equivalent to **11 May 2026 in Hong Kong**. It is a different revision from the August 2D building outline dataset.

`official-10-SW-12C.zip` is the untouched 46,656,068-byte official download, SHA256 `33471c681feee798b3bd38285e3ece4b9b1e64190bd0bd31d27684b80f547757`. `model-download.json` records the public download URL, response headers and every archive member. The 43,996,910-byte terrain photograph remains inside that source archive and is not extracted, requested by the fixture, or shipped in the geometry-only sample.

`prepare_model_sample.py` stages 279 original building glTF/bin pairs plus a **derived terrain glTF with its photograph dependency removed**. Building binaries, materials and vertex colours are untouched. The original terrain material facts and all source hashes are retained in `model-sample/manifest.json`. The original terrain glTF remains in the archive. Staged glTF/bin geometry assets total 11,857,089 bytes before the separate baked JSON and manifest.

Source node matrices produce `[E, HKPD height, -N]`. The only scene translation is `[-834500, 0, 816500]`, yielding the existing city axes `x=E−834500`, `y=HKPD height`, `z=816500−N`. There is no additional rotation, scale or altitude correction.

**Replacement matching uses exact GeoRefNo plus projected model-hull overlap of at least 50% of the smaller footprint and at most 10 m centroid separation.** It then carries the matched official BuildingCSUID/OBJECTID directly. It does not match on a building name. There are 275 one-to-one verified source matches; four unmatched 3D models remain excluded from automatic replacement. This screen is conservative evidence for a geometry substitution, not architectural acceptance of every face.

## Reusable city payloads

The integration uses the existing city building tile and geometry path. It does not need a new viewer or a new runtime GLTF loader.

- `model-sample/model-geometries.json`: `byBuildingUid` map of 275 records keyed by the exact generated official UID, e.g. `landsd/OBJECTID:0`. Each carries BuildingCSUID, model ID, unindexed `position` and `normal` arrays, original `colour` arrays, world bounds, material facts and source hashes. Total 26,164 triangles / 78,492 vertices; 10,466,839 bytes of JSON, 548,814 bytes with gzip. `bake_model_geometry.py` preserves the exact source node hierarchy and triangle order. The city's facade palette/windows may intentionally replace the source display material; that is presentation, not a change to source geometry.
- `model-sample/terrain-source-5m.json`: 150 × 120 source-TIN samples aligned to the existing city 5 m lattice. Georeference `aE=5,bE=816502.5,aN=-5,bN=814997.5`. Inclusive source-grid crop `[158,294,307,413]` relative to `bE=815712.5,bN=816467.5`. World sample bounds `[-17997.5,1502.5,-17252.5,2097.5]`. All 18,000 nodes have actual source triangle coverage; `elev:null` plus a `valid` mask would preserve gaps if present. No extrapolation, gap fill or vertical offset is applied.
- `model-sample/manifest.json`: every original model's precise transformed bounds, source entries and hashes, matched identities, coordinate interpretation and source revision. The source terrain spans world bounds `[[-18000,4.529858589172363,1500],[-17250,105.79035568237305,2100]]`, a 750 × 600 m tile.

The 5 m grid is a **resampling** of the official triangular surface. It cannot reproduce every original triangle edge. At 273 model centres wholly inside the output grid, median absolute departure from the original TIN is 0.023 m and maximum departure is 0.827 m. No model roof falls below that resampled surface in this bounded screen, versus 18 below the previous 5 m terrain at the same covered centres. Blending and complete footprint checks belong to root's live integration.

## Actual browser verification

`model_browser.mjs` serves only an ephemeral verification fixture through Playwright request routes. It reuses the existing vendored GLTFLoader, Three.js, `world.makeTerrain` and `geo.makeTerrainSampler`. It is not a second product viewer.

The retained `model-browser-proof.json` records:

- 279 original glTFs and 275 baked building geometries rendered successfully.
- Original browser bounds agree with independently decoded source bounds to 3.6e−15 m at the checked extrema; baked Float32 bounds agree exactly at those extrema.
- Zero page/network errors and no terrain-photo requests.
- 277 source-terrain centre raycasts, independently reproduced by barycentric sampling to 1.5e−13 m.
- Two unhit source-terrain rays: one model centre exactly on the southern tile edge, one outside it. Whole building geometry is preserved across tile boundaries.
- Zero model roofs below source terrain, versus 19 below the compared existing 5 m terrain, at model-bound centres. The corresponding matched source 2D TopHeight screen gives zero versus 21. These are centre-point diagnostics, not complete footprint checks.

The four exported 1600 × 1000 captures were opened and visually inspected: `official-models-source-terrain-1600x1000.png`, `official-models-existing-5m-1600x1000.png`, `official-models-source-close-1600x1000.png`, and `official-models-baked-close-1600x1000.png`. Roof parapets, stepped volumes and source facade relief remain visible after baking. The terrain uses an explicitly neutral display material because the photograph is omitted. The 5 m comparison terrain hash is in the proof; later live terrain changes do not retroactively change these captures.

## Reproduction

Run from the feature worktree with the existing geospatial Python environment (NumPy, Shapely, pyproj) and city browser dependencies. The source archive and snapshots are inputs; none of these scripts rewrites archival references.

```sh
/tmp/astra-city-venv/bin/python docs/astra-city/mui-wo-buildings/review/prepare_model_sample.py
/tmp/astra-city-venv/bin/python docs/astra-city/mui-wo-buildings/review/bake_model_geometry.py
node docs/astra-city/mui-wo-buildings/review/model_browser.mjs
/tmp/astra-city-venv/bin/python docs/astra-city/mui-wo-buildings/review/resample_model_terrain.py
/tmp/astra-city-venv/bin/python docs/astra-city/mui-wo-buildings/review/check_resampled_terrain.py
```

The browser fixture expects the existing app at `http://127.0.0.1:4176` and accepts `CITY_ORIGIN`. It uses the installed Chrome executable. The frozen original coverage JSON intentionally remains evidence of the pre-integration state; rerunning `building_diagnostic.py` after source augmentation creates a different baseline.

No `references/lantau-maps/` images were used to derive these modern building geometries. The [recognised village list, September 2009 edition](https://www.landsd.gov.hk/en/images/doc/rv0909.pdf) was used only to cross-check historical settlement naming, not current boundaries or building placement. Government source attribution and dataset terms remain applicable. Online satellite/reference screenshots are review evidence, never model textures or traced building geometry.
