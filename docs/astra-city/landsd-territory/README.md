# Territory building coverage from reused government data

Produced by GPT-6 Astra on 6 September 2026. The original Lands Department public download was already present in the repository's comparison worktree cache. This work reuses those source bytes; no other model's importer, renderer, compressed building format or rendered output was copied.

## Published city coverage

The existing Astra city now uses **342,225 government polygon components from all 342,223 source records**, with **3,890 retained OSM forms**: **346,115 total forms across 452 tiles**. Government geometry replaces 113,172 overlapping OSM massings. The 275 verified detailed models and native Mui Wo geometry/terrain refinements are retained through the same tile pipeline. These are dataset-coverage counts, not a claim that every building is current, fully modelled or visible above the terrain.

The integration reads the frozen 117,062-form OSM baseline from commit `5ae3900`. It replaces an OSM form when government coverage occupies at least 15% of its footprint, or when that OSM form covers at least half a government footprint. Edge-only overlaps retain 853 OSM forms. Only at least 50% overlap on either side transfers identity/use evidence. Four invalid old OSM shapes are repaired solely for overlap calculations; source geometry remains untouched. Exact counts, repair IDs and removed OSM UIDs are in `integration.json`.

The shared publisher writes the existing geometry tiles, catalogue, overview and manifest. Repeated source links and height explanations use manifest metadata; picking reconstructs the official record URL and resolves the stored height-policy code. Government `BaseHeight` and `TopHeight` remain absolute HKPD elevations. Full raw source attributes remain in the retained archive. Names, recorded uses and research references survive OSM replacement as explicit related-source identities; where a broad mall overlaps a named tower, the official building name selects the matching OSM use before the largest overlap. Area-based activity remains an inference about occupancy.

Lighting now streams alongside each nearby geometry tile using the existing cache, cancellation and Retry lifecycle. Opening the map does not fetch the 37 MB territory-wide activity file. That file remains available for reproducibility and offline consistency checks. Facade schedules, terrain rendering, movement, building picking and controls reuse their existing implementations.

To publish a regenerated stage after the Mui Wo integration has been prepared:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/landsd-territory/integrate.py
/tmp/astra-city-venv/bin/python source-scripts/city/build_activity.py
/tmp/astra-city-venv/bin/python source-scripts/city/landsd-territory/verify_live.py
```

Run the local Mui Wo integration **before** this territory publisher when rebuilding both; its deliberately local baseline is not the final whole-territory output. The native Mui Wo records are retained as preferred replacements during territory publication. Rebuild arrival validation after geometry changes; its report and source-backed repairs live in `../arrival-repairs/`.

## Reused source and completeness

The retained file is `source-scripts/city/landsd-territory/landsd-hong-kong-source.geojson.gz`. Decompression reproduces all **397,110,838 bytes** of the existing official `Building_Outline_Public_v20260819_Building_converted.geojson`. The gzip is **64,036,960 bytes**. The locally calculated original-byte SHA-256 is:

`bafe780408444ad4f7493b1539b5a4a39958d30558c978be64e0db88ffb5b1af`

This is a local integrity fingerprint, not a publisher-signed checksum. The original cache's download timestamp was not recorded; its filesystem time is retained separately and is not presented as the retrieval time. Current verification requests include UTC times, URLs, parameters, response headers and response hashes beside each response.

All **342,223 unique OBJECTIDs** exactly match the live service's `returnIdsOnly` result and `returnCountOnly` total. Metadata advertises the same 19 August 2026 revision. The layer reports `maxRecordCount: 3000`. The planned full API download was stopped before feature batches were fetched once the reusable source was found; only metadata, ID/count and small coordinate-verification requests were needed.

The source retains 342,224 polygon components, 3,966,251 vertices and 2,787 holes. No type, name, height or size filters are applied:

| Source type | Records |
| --- | ---: |
| Tower | 213,328 |
| Podium | 9,026 |
| Temporary Structure | 75,117 |
| Open-sided Structure | 44,752 |

106,319 records have null `BaseHeight`; 104,917 have null `TopHeight`. All records have finite, closed polygon coordinates and none has missing geometry. Shapely identifies 83 invalid source geometries; the raw snapshot preserves them unmodified, while the shared Astra converter applies its documented validity repair during staging. Completeness here means the entire advertised dataset, not a claim that every real-world structure has been surveyed.

## Coordinates, elevations and source evidence

The retained GeoJSON uses longitude/latitude coordinates. Existing PROJ transforms it into the city's Hong Kong 1980 grid: `x = E − 834500`, `z = 816500 − N`. Twenty-three source features, comprising 466 vertices, were compared with native EPSG:2326 REST geometry and identity/type/name/height attributes. Twenty-two ordinary shapes agree within **0.000475 m**. One multipolygon, OBJECTID 335513, has native `curveRings`; the official GeoJSON and default REST polygon response linearise its curves differently, giving a measured **0.5483 m** maximum boundary difference. Both native responses are retained. This distinction is recorded explicitly rather than presented as projection precision.

The [official dataset metadata](https://portal.csdi.gov.hk/csdi-webpage/metadata/landsd_rcd_1637211194312_35158/html) identifies the dataset, revision, provider, native EPSG:2326 CRS and [GeoJSON file API](https://portal.csdi.gov.hk/csdi-webpage/file-api?dataset_id=landsd_rcd_1637211194312_35158&format=geojson&layer_name=Building). The [source specification](https://static.csdi.gov.hk/csdi-webpage/view/common/6eda6a766520bcffe13206378c060a59bdb54a3c6f92480b1f01174d25fd7194) defines `BaseHeight` and `TopHeight` as approximate metres above Hong Kong Principal Datum. Recorded values remain unchanged. [ArcGIS query documentation](https://developers.arcgis.com/rest/services-reference/enterprise/query-map-service-layer/) explains unrestricted ID-array results and native curve output. Attribution: Lands Department, Hong Kong SAR Government; [CSDI terms](https://portal.csdi.gov.hk/csdi-webpage/doc/TNC).

## Staging and reproduction

```sh
/private/tmp/astra-city-venv/bin/python source-scripts/city/landsd-territory/test_source.py
/private/tmp/astra-city-venv/bin/python source-scripts/city/landsd-territory/stage.py
/private/tmp/astra-city-venv/bin/python source-scripts/city/landsd-territory/verify_stage.py
```

To repeat current source verification from an existing original GeoJSON:

```sh
/private/tmp/astra-city-venv/bin/python source-scripts/city/landsd-territory/retain.py --source /path/to/Building_Outline_Public_v20260819_Building_converted.geojson
```

`retain.iter_features()` reads the retained gzip incrementally; it does not load the 397 MB feature collection into memory. `stage.py` adapts coordinate format only, then calls the existing `source-scripts/city/mui-wo-buildings/build.py::stage_feature()` for component, geometry and elevation policy. The shared `DemSampler.ground()` supplies existing 70 m terrain outside Mui Wo and the current 5 m Mui Wo patch inside it. Vertex-and-centroid terrain statistics are explicitly sample-based; they are not exhaustive intersection extrema. Recorded buildings are not lifted to fit terrain. Only missing elevation values receive labelled rendering estimates.

Staged output is isolated under `3d-viewer/city/data/landsd-territory/`: complete polygon components assigned to 2 km tiles and a small manifest. Each record preserves source IDs, CSUID, structure type, recorded base/top, source URL and height policy. Full original attributes remain in the source archive rather than being repeated in every tile. The staging pass does not edit live city tiles or merge OpenStreetMap buildings.

The completed stage contains **342,225 valid components from all 342,223 source records in 403 tiles**, totalling **418,917,794 bytes** of plain JSON. The largest tile is 10,633,178 bytes. These are isolated staging artefacts; live publication can compact repeated metadata and apply the existing city overlap policy. There are 235,761 components using recorded heights and 106,464 using labelled estimates. Geometry repair changes the component count slightly; the retained source remains unmodified. A valid tiny shelter (OBJECTID 4795) exposed a self-intersection introduced by millimetre rounding. The shared converter now uses finer coordinates when needed to preserve topology; both original GeoJSON and native service geometry are retained as regression fixtures.

The independent audit passes over **every component and source ID**: tile hashes/sizes/counts, unique IDs, closed and valid polygons, bounds, finite positive render heights, exact advertised-ID coverage, immutable CSUID/type/base/top attributes, and unchanged recorded render elevations. See `staging-independent-verification.json`. Terrain diagnostics flag 21,722 components whose sampled ground minimum exceeds the roof, 37,994 whose sampled ground range crosses the roof, and 24,330 whose base is above the sampled ground maximum. These are diagnostics of approximate source elevations against the currently rendered terrain; they neither alter source heights nor establish exhaustive footprint intersections. They require local terrain refinement or source review, not automatic lifting.

Four focused offline source tests pass: large/Unicode feature streaming, malformed-footer rejection, advertised ID/count preservation, and compressed-byte round trip. Native coordinate and property comparisons are recorded in `verification.json`. Final staging counts and diagnostics are recorded separately in `staging-verification.json`, `geometry-repairs.json` and `terrain-conflicts.json`.

## Reuse audit

The original main checkout already retains `references/codex/hongkong-3d-model/data/hk-b50k-gml/iB50000GML.zip` (SHA-256 `cfdf696b51a3eda4682b63b84d0a1bfc231c6ab43cc3e26928ccee41eb19270a`). Its BLDGPOLY layer contains 45,541 cartographic blocks with GRAPHICID/type/update fields, without `BaseHeight`, `TopHeight` or the Building FSDT identifiers. Existing B50K extractors provide topographic vectors and land cover, so that archive cannot substitute for the full contemporary building dataset. HKS-114 history led to the existing complete official download in the comparison cache, which was reused as data. Reference archives and historical Lantau maps remain untouched; no reference image was used.

## Final integration checks

The complete city JavaScript suite passes **102 tests/subtests** after territory publication, per-tile lighting, model-aware bounds and the six sourced arrival repairs. It covers lighting schedules/classification, geometry and holes, source provenance, movement readiness, collision, arrival dryness, terrain seams, cache cancellation/Retry/disposal, bridge geometry, original aircraft options, sky/time and weather behaviours. Run `npm test` from `3d-viewer/city/`.

The independent published-data audit (`live-verification.json`) verifies all IDs/components, all tile counts and bounds, all 275 detailed models, immutable government attributes and the complete 117,062-form OSM baseline. It finds zero OSM forms that violate the documented replacement threshold. Minor retained edge overlaps remain explicitly counted. The final publisher includes detailed model eaves in X/Z bounds; only a 10.65 cm extension in tile `-9_1` was needed, with all feature payloads proven unchanged.

All **190 walking arrivals** pass the shared live terrain/collision validator. Six needed small sourced path relocations (4.965–74.444 m); the other 184 and six existing aerial-only destinations remain unchanged. See [arrival repair evidence](../arrival-repairs/README.md). Browser measurements and images are retained separately under `browser/`; they are local desktop observations rather than performance guarantees for every device.

The final browser pass succeeds in Central, Kowloon, Tai O, Peng Chau, Cheung Chau, Sha Tin, Yuen Long and Mui Wo, including actual source picking, government attribute lookups, collision-aware walking, night/layer behaviour and a 390 px mobile layout. It reports zero browser errors. On the local Apple M4 Pro at 1440×1000, frame medians are 16.6–16.7 ms and p95 18.1–19.0 ms; startup readiness is 0.595 s and all initial sections settle in 3.832 s. The uncompressed local server completes 92.1 MB of startup transfers (34.1 MB geometry and 2.94 MB activity included). These timings do not represent slower networks or mobile hardware. Final browser commands and per-view evidence are in [browser/README.md](browser/README.md).
