# Mui Wo detailed-model extension · HKS-167

Astra extended the existing government-model importer from Pak Ngan Heung into Wang Tong, Tai Tei Tong, Luk Tei Tong, the town waterfront and the ferry-pier area. It reuses the original glTF transforms, geometry baker, TIN resampler, shared tile publisher, building geometry/collision helper and public-path arrival validator. There is no second runtime model loader or viewer.

| Source sheet | Area covered in this pass | Source revision, Hong Kong date | Source building models | Verified replacements |
|---|---|---|---:|---:|
| 10-SW-12C, retained | Pak Ngan Heung | 11 May 2026 | 279 | 275 |
| 10-SW-12D | Wang Tong | 11 May 2026 | 210 | 208 |
| 10-SW-17A | Tai Tei Tong | 11 May 2026 | 376 | 375 |
| 10-SW-17B | Town waterfront | 29 September 2025 | 296 | 293 |
| 10-SW-17C | Luk Tei Tong | 11 May 2026 | 73 | 71 |
| 10-SW-17D | Southern village surroundings | 11 May 2026 | 55 | 54 |
| 10-SW-18A | Ferry pier and eastern waterfront | 17 July 2026 | 51 | 51 |
| **Total** | | | **1,340** | **1,327** |

This adds **1,052** detailed models and retains all 275 previous matches. The source geometry contains 196,808 displayed model triangles, up from 26,164. Thirteen models fail the conservative official-record matching screen; there are no ambiguous UID groups or duplicated source model IDs. Ten infrastructure models are retained in the source caches and explicitly excluded from this building/terrain pass. These are source-complete counts for the selected sheets, not complete detailed architecture for all 2,408 official forms in the user’s Mui Wo envelope. **1,081 forms retain their outline-based fallback.** Full per-model accounting is in [build.json](build.json).

All **346,115 city forms**, including exactly **342,223 official source IDs / 342,225 official polygon components**, remain present. The comparison against `ff68cf1` checks every UID, owner tile, footprint vertex/ring, centre, structure type, BuildingCSUID, original BaseHeight/TopHeight and height classification. There are zero changes to recorded elevations and zero added duplicate extrusions. Only 202 bases whose two source elevations were absent were re-estimated from the improved terrain; these remain explicitly labelled `terrain-estimated`. See [live-preservation.json](live-preservation.json).

## Source and placement

The [Lands Department 3D mapping description](https://www.landsd.gov.hk/en/survey-mapping/mapping/3d-mapping.html) identifies the non-textured model product. The retained [CSDI dataset metadata](https://portal.csdi.gov.hk/csdi-webpage/metadata/landsd_rcd_1742809441342_98380/html), [official tile index](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0), original index response/request, per-sheet revision and download records are preserved. Government data remain subject to [CSDI terms](https://portal.csdi.gov.hk/csdi-webpage/doc/TNC); supplementary OpenStreetMap attribution remains ODbL.

Original glTF matrices produce `[E, HKPD height, -N]`. The only city transformation is translation `[-834500, 0, 816500]`. There is no invented height offset, mesh simplification, building clipping or fitted roof. Replacement requires the original model GeoRefNo and an official footprint with at least 50% overlap of the smaller footprint and at most 10 m centroid separation, then an unambiguous BuildingCSUID/component match. Source bounds, triangles, normals, vertex colours and material facts are retained. Five source models have 102 zero-normal vertices; these remain finite zero vectors, rather than generating NaN or inventing normals.

The 3D roof and the 2D outline are separate source products. Model top and outline TopHeight differ by more than 2 m in 451 matched forms. Both remain unchanged and the existing source card labels its numeric value **OUTLINE HEIGHT**. The city’s facade palette, window layout, foundations and sparse open-sided supports remain illustrative.

Two full ZIPs had already downloaded when the byte-range optimisation completed. They remain ignored local caches with complete archive hashes. For the other four sheets, the server’s ordinary HTTP 206 range support retained the ZIP directory and only original glTF/bin entries, verified by ZIP CRC plus per-entry SHA-256. The compact derived ZIP hashes are explicitly distinguished from a complete original-archive hash, which is null where the full archive was not acquired. Those four downloads transferred 9,573,651 bytes including directories. No photographs were extracted or used at runtime. Source URLs, ETags, Last-Modified dates, byte ranges and hashes are recorded under `source-scripts/city/mui-wo-models/sources/`. Large caches and extracted geometry are ignored; the reproducible combined payload is **3,643,217 bytes gzip**, with source metadata and original numeric precision retained.

The existing Google satellite and Open3Dhk comparisons for these same neighbourhoods remain in [the preceding online-reference review](../review/ONLINE-REFERENCE-REVIEW.md). Those are contextual visual evidence; this extension’s precise geometry comes from the retained government model entries. No historical Lantau reference images were used or modified.

## Terrain joins and remaining conflicts

Seven actual source TINs were resampled on the existing 5 m lattice, retaining missing samples as null. Their 126,000 source grid nodes form one mosaic, with a 15 m blend only at the union’s exterior and holes. Internal sheet edges do not blend back into the old DTM. Because this visualisation product also contains positive-HKPD water surfaces, the source TIN alone cannot determine land. The renderer integration therefore retains the existing official DTM water mask: 15,302 water nodes are excluded from land-detail blending. Original source grids remain untouched. This fixes the initially detected rectangular infill of Silvermine Bay without inventing a shoreline.

All eight adjoining sheet edges were audited at 5 m intervals against the original TINs. A documented 1 cm nearest-source-point tolerance handles original Float32 boundary differences of up to 5 mm. The largest same-location disagreement is **1.676 m** between May 2026 sheet 12D and September 2025 sheet 17B; 12 of its 150 samples differ by more than 1 m. The other edges range from 0.0003 to 0.566 m maximum difference. The shared grid connects these samples without a mesh crack, but does not erase differing source revisions. See [source-audit.json](source-audit.json) and [terrain-mosaic.json](terrain-mosaic.json).

The identical before/after diagnostic compares the highest displayed roof elevation with exact terrain-triangle extrema across each unchanged official footprint, using 0.1 m tolerance:

| Diagnostic, 2,408 Mui Wo forms | `ff68cf1` | Current |
|---|---:|---:|
| Highest roof wholly below terrain | 194 | 114 |
| Highest roof below some terrain in footprint | 373 | 214 |
| Newly wholly-buried forms | — | 0 |

The 114 wholly-below cases comprise 112 recorded outline/terrain conflicts and two estimated-height fallbacks. Of 214 partial cases, 185 involve recorded outlines, 28 involve estimated fallbacks and one involves a detailed model. These classes describe source/render mismatch; they do not prove which source is correct. Source model `B176651437301062G0` / `landsd/340232:0` already has its roof maximum about 0.324 m below its own tile terrain at its centre. Three whole model centres extend outside their owner tile’s terrain, so the own-tile check correctly returns no hit. No source roof was silently raised. See [terrain-comparison.json](terrain-comparison.json) and [integration.json](integration.json).

The shoreline still follows the existing DTM mask, including its resolution limitations. Small lanes, channels, vegetation, foundations, waterfront decks and detailed architectural acceptance need further source review. A bounded 5 m grid does not reproduce every original TIN edge or demonstrate complete pedestrian accessibility.

## Arrival, picking and rendering evidence

One new conservative model-eave collision invalidated `silverminebaybeach`. The shared repairer moved it **39.996 m**, from `[-16593.1,1933.3]` to `[-16577.2,1896.6]`, along retained public path [OSM way 204797330](https://www.openstreetmap.org/way/204797330), sourced from `source-scripts/city/snapshots/outlying-west.json.gz`. Its sampled 2 m path walk passes the exact runtime terrain and collision rules. All 190 walking arrivals now pass; the other 189 walking arrivals and all six aerial destinations are unchanged. The previous six-repair report remains intact. [Repair evidence](arrival-repairs/repairs.json) and [idempotent final verification](arrival-repairs/verification.json) are retained.

The final Chrome run loaded all 1,327 models through 13 ordinary city tiles. Actual roof picking, source cards and collision checks passed in all six newly covered sheets. The ferry view selects the real Silvermine Bay Ferry Pier (`landsd/291920:0`). The existing Mui Wo walking entry moved 2.015 m without collision. Zero page or tile errors occurred.

At the same 1440×1000 overview camera as the verified `ff68cf1` baseline, a 180-frame local sample measured median **16.6 ms**, p95 **17.5 ms**, **91 draw calls**, and **2,378,853 rendered triangles**. The earlier baseline measured 16.6 / 19.0 ms, 91 calls and 2,227,021 triangles. These are bounded local Chrome observations, not a production-network or cross-device frame-rate guarantee. Runtime still uses the existing tile stream, palette batching, picking, lighting and collision code. [Browser results](browser/verification.json) include per-view measurements.

All seven saved final screenshots were inspected. The overview retains an open Silvermine Bay; village close-ups show sourced roof terraces and forms; the ferry-pier roof is visibly distinct. Final evidence:

- Mui Wo overview: [before, ff68cf1](../../landsd-territory/browser/muiwo-overview-1440x1000.png) · [after, HKS-167](browser/muiwo-overview-1440x1000.png)
- [Wang Tong](browser/wang-tong-source-card-1440x1000.png)
- [Tai Tei Tong](browser/tai-tei-tong-source-card-1440x1000.png)
- [Luk Tei Tong](browser/luk-tei-tong-source-card-1440x1000.png)
- [Town waterfront](browser/waterfront-source-card-1440x1000.png)
- [Southern village surroundings](browser/southern-villages-source-card-1440x1000.png)
- [Silvermine Bay Ferry Pier](browser/ferry-pier-source-card-1440x1000.png)

## Rebuild and checks

Run from the authorised Astra worktree using its existing Python/Node runtimes. Cached source geometry is reused before any network transfer. The pipeline preserves the current territory dataset; **do not run the obsolete Mui Wo-only `mui-wo-buildings/integrate.py` after whole-territory publication**.

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-models/fetch.py
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-models/build.py
/tmp/astra-city-venv/bin/python source-scripts/city/terrain-detail/build.py
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-models/publish.py
CITY_NODE=/Users/williamli/.nvm/versions/node/v24.17.0/bin/node /tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-models/repair_arrivals.py
CITY_NODE=/Users/williamli/.nvm/versions/node/v24.17.0/bin/node /tmp/astra-city-venv/bin/python source-scripts/city/build_regional.py
```

Focused validation passed:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-models/test_models.py
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-models/audit_sources.py
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-models/compare_baseline.py
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-models/verify_live.py
/Users/williamli/.nvm/versions/node/v24.17.0/bin/node --test 3d-viewer/city/tests/mui-wo-models.test.js 3d-viewer/city/tests/terrain-detail.test.js
/Users/williamli/.nvm/versions/node/v24.17.0/bin/node 3d-viewer/city/tests/mui-wo-models-browser.mjs
```

The Python checks compare every baked model against its original glTF transform and triangle count, verify source-cache claims and protect terrain union/water behaviour. The Node test sends every detailed model through the existing geometry/collision helper. The live preservation audit checks every territory form against the baseline. Existing arrival repairs are reapplied on rebuild; a second repair run has zero changes.
