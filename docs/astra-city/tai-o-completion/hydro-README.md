# Tai O tidal channels — HKS-170

The central Tai O channels now cut through the existing terrain along current government map boundaries. The ordinary water shader fills those openings at the selected tide level. This pass preserves every original terrain elevation, building footprint and detailed building model.

[Live day view](browser/channels-day-1440x1000.png) · [Live night view](browser/channels-night-1440x1000.png) · [Live mobile view](browser/channels-mobile-390x844.png) · [Browser measurements](browser/geometry-verification.json)

[Source village comparison](hydro-source-village-1960x1400.png) · [Wider source comparison](hydro-source-overview-1960x1400.png) · [Source and triangle validation](hydro-validation.json) · [Whole-territory preservation](hydro-preservation.json) · [Arrival repair and fresh-process checks](hydro-arrival-repairs/repairs.json)

## Sources and interpretation

The source extent is E802700–804650 / N812300–813750 in EPSG:2326, covering Tai O village, Fu Shan shoreline and nearby approaches. City coordinates are x=E−834500, z=816500−N.

- Lands Department [iB5000 index](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637224243141_96556/MapServer/0) selects 9-SW-C and 9-SW-D. Their index revisions are 3 July and 13 August 2026. Fifteen original closed `ContourPoly` land features define the bounded sea complement: one water polygon with holes, 1,735 vertices and 1,132,166.793 m². Original GML coordinate values are retained; decimal precision does not imply survey accuracy. Individual feature updates range from September 2023 to June 2026, so the index date is not described as a fresh survey of every bank.
- Eleven bounded [iB1000 sheets](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637223748322_25497/MapServer/0) retain independent HWM/seawall linework and mapped hydro polygons. Open line segments have gaps under structures; we did not join those gaps by hand. Of 1,266 samples spaced 5 m along current shoreline segments, 1,226 are within 1 m of the iB5000 water boundary; median distance is 0.067 m and p95 is 0.435 m. Differences remain visible in the source comparison.
- The Lands Department's current [Tai O GeoPDF](https://www.landsd.gov.hk/doc/en/mapping/ehkg/MapPages/GeoPDF/IS08_TaiO.pdf), distributed with the [2026 e-HongKongGuide](https://www.landsd.gov.hk/en/resources/mapping-information/ehkg.html), was visually checked for channel topology. No archival shoreline image or manual image tracing supplied geometry.

Only explicit iB1000 river/channel/nullah polygons that intersect the sea would supplement the coast. None met that exact connection test here; no gap was guessed. Culverts, ponds, catchwaters and source zero-Z placeholders are not treated as tidal water or surveyed depth.

The mapped water intersects 106 of the 1,030 retained Tai O source footprints by more than 1 m², including central waterfront buildings. Their footprints/models remain intact above water. Some other waterfront buildings remain inside the source's cartographic land extent: this pass does not invent under-house channels or claim every waterfront building has verified stilts.

## Terrain and arrival behaviour

Optional `terrain.json.hydro` contains source rings, bounded cut-cell geometry, bank faces and an explicitly illustrative −4 m bed. The existing renderer replaces affected coarse and fine terrain triangles; it does not round channel edges to the 5 m grid. The existing sampler exposes `mappedWater(x,z)` and returns the illustrative bed from `height()` inside mapped water; `raw()` is unchanged. This adds no new runtime request or parallel terrain renderer.

The source audit checks all 7,425 replacement land triangles. Maximum overlap into water after coordinate rounding is 0.000076 m², and maximum height difference from the original triangle interpolation is 0.000011 m. The full coarse terrain object, excluding its new optional hydro field, and the entire Tai O fine patch equal baseline `7757ee6`. The payload is 2,017,256 bytes within the existing terrain request; full terrain JSON is 4,804,872 bytes. It adds 1,735 bed and 10,320 bank triangles; all depths are illustrative, not bathymetry.

All 190 walking arrivals pass the shared source-data validator, including mapped-water and 1.2 m shore clearance. Only `taiopromenade` moved: 8.302 m to `[-30779.0,3820.8]` on retained [OSM way 1187601819](https://www.openstreetmap.org/way/1187601819), ground 3.607 m. Its sampled 2 m public-path walk and fresh generated-module import pass. The other 189 walking arrivals and six aerial-only destinations are unchanged. A short arrival check is distinct from the separately reviewed continuous village route.

Five focused live terrain tests pass, including actual mesh raycasts, dry-land sampling, both Tai O chunks and the fine/coarse seam. The parent integrated browser check also passed day/night/mobile, source bridge picking and all 532 Tai O detailed models, with median frame time about 16.7 ms, p95 ≤16.8 ms and no page errors. The final day export was also inspected against the source village plot: the connected branches and waterfront openings agree. The parent owns continuous route acceptance.

## Rebuild and evidence

Run from the Astra worktree, using the existing Python environment with NumPy, Shapely, pyproj and Matplotlib:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-completion/hydro_fetch.py
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-completion/hydro_build.py
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-completion/hydro_terrain.py --publish
MPLCONFIGDIR=/tmp/hks170-matplotlib /tmp/astra-city-venv/bin/python source-scripts/city/tai-o-completion/hydro_audit.py
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-completion/hydro_preservation.py
node --test 3d-viewer/city/tests/hydro-terrain.test.js 3d-viewer/city/tests/terrain-detail.test.js
```

`hydro_terrain.py` without `--publish` stages an ignored `hydro-terrain.json`. It reads current live patches, preserves existing coarse fields and replaces only its own optional hydro metadata. It never rewrites city building tiles or the shared manifest. Use the existing `repair_arrivals.py` after any later terrain or footprint changes; its validator now distinguishes mapped tidal water and shore-clearance failures.

Fifty-six compact original GML files (1,250,809 bytes), source indices, per-file hashes and download URLs live under `source-scripts/city/tai-o-completion/`. Thirteen original ZIPs total 43,715,585 bytes (41.7 MiB) and are ignored cache, as is the staged terrain duplicate. They can be reacquired from the recorded public direct-download URLs. Python decoding uses the source GML axis order N,E,Z; separate curves and polygon rings remain separate. Source archives and archived reference folders are untouched. Lands Department / HKSAR Government retains ownership of the government mapping; OpenStreetMap source paths retain their existing ODbL attribution.
