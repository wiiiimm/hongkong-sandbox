# Buildings layer — the 3D city (HKS-114)

Every building block in Hong Kong, extruded onto the terrain in the viewer, so the
city reads as a city: you can orbit the skyline, walk the streets between towers,
stand on a roof you air-dropped onto, and fly between (or into) skyscrapers.

Files: `3d-viewer/buildings.js` (renderer + movement queries), `3d-viewer/data/hk-buildings.bin`
(+ `hk-buildings.json` metadata, `hk-buildings-names.json` tower names),
`source-scripts/hk-buildings/build_hk_buildings.mjs` (the reproducible pipeline).

## Source data

| | |
|---|---|
| Dataset | Lands Department **"Building"** layer (`Building_Outline_Public`), via the CSDI portal — dataset id `landsd_rcd_1637211194312_35158` |
| Version used | `v20260819` (CSDI metadata date 2026-08-20) |
| Records | 342,223 polygons → 342,224 blocks (one multipolygon split) |
| Attributes used | `BaseHeight`, `TopHeight` (metres above **HK Principal Datum** — the same vertical datum as the LandsD 5 m DTM the viewer renders), `BuildingBlockType` (Tower 213k · Temporary Structure 75k · Open-sided Structure 45k · Podium 9k), `BuildingNameEN/TC`, `Status` (all Active) |
| Licence | [DATA.GOV.HK Terms of Use](https://data.gov.hk/en/terms-and-conditions) — free re-use with attribution to the Lands Department. Attribution is in the app's Credits drawer (en + 繁中) and the README data table. |
| Download | `https://portal.csdi.gov.hk/csdi-webpage/file-api?dataset_id=landsd_rcd_1637211194312_35158&format=geojson&layer_name=Building` (397 MB GeoJSON, WGS84). Cached under `source-scripts/hk-buildings/cache/` — git-ignored. |

A "building" in this layer is a **block**: a tower, its podium and the plant room on its
roof are separate polygons, each with its own absolute base and top. That is why the
viewer places every block at its true mPD height rather than draping each footprint
onto the ground (which would collapse rooftop structures onto the street).

About 31% of blocks (106,464 — almost all temporary or open-sided structures: sheds,
canopies, huts; only 7 towers) carry no height. They get a default (3.0 m temporary,
3.5 m open-sided), are flagged as estimated, and are draped on the ground.

## Coordinate reference

The CSDI GeoJSON export is WGS84 lon/lat; the viewer works in the **HK1980 grid
(EPSG:2326)**. The pipeline reprojects with the official 7-parameter Helmert
(the inverse of EPSG:1825 "Hong Kong 1980 to WGS 84 (1)": ΔX −162.619, ΔY −276.959,
ΔZ −161.764 m, rotations 0.067753″ / −2.243649″ / −1.158827″, scale −1.094246 ppm,
position-vector convention) followed by the HK1980 Transverse Mercator (International
1924 ellipsoid, same series as `llToEN` in `main.js`).

Verified against the CSDI FeatureServer's native `outSR=2326` geometry on 360 sampled
vertices across the territory: **0.000 m** residual. For comparison, the viewer's
eyeballed Web-Mercator datum shift used by the satellite/OSM drape and GPS
(`gpsToEN`) differs from this by ~19–21 m — a pre-existing calibration to fix
separately (noted on HKS-114).

## Binary format (`hk-buildings.bin`, "HKBL" v1, gzipped)

Little-endian. The file is stored gzipped and inflated client-side with
`DecompressionStream` (hosts do not compress `application/octet-stream`; the R2
mirror serves it as-is).

```
'HKBL'  u8 version=1  u8 reserved  u16 reserved  u32 count
f64 originE  f64 originN  f32 quant (0.25 m)
count × {
  u8 flags   bits0–1 type (0 Tower, 1 Podium, 2 Open-sided, 3 Temporary)
             bit2 height estimated · bit3 base unknown (drape on the ground)
             bits4–6 land use (0 residential / unclassified · 1 office & commercial · 2 retail
             podium · 3 industrial · 4 institutional · 5 rural village · 6 other)
  varint nRings
  per ring: varint nVerts, then nVerts × (zigzag ΔE, zigzag ΔN) in quanta,
            delta-coded from the previous vertex; ring 0's first vertex is a delta
            from the previous record's first vertex (records are 2 km-tile sorted);
            hole rings start as a delta from ring 0's first vertex
  zigzag base (dm)   varint height (dm)
}
```

Rings are Douglas–Peucker simplified at 0.3 m (3.97 M → 2.47 M vertices), outer
rings counter-clockwise in E/N, holes clockwise. Output: 6.95 MB raw → **5.21 MB
gzip** (with the land-use bits). Parses in ~180 ms in the browser.

## Land use — who is awake when

The night lighting needs to know what each block *is*. The schedule (share of window
bays lit, Hong Kong clock; `AWAKE` in `buildings.js`, piecewise-linear between keyframes):

| HKT | homes | offices | shops |
|---|---|---|---|
| 18:00 | 55 % | 78 % — people start leaving | 92 % |
| 20:00 | 76 % | 38 % — the late shift | 92 % |
| 21:00 | 86 % — the big wave home | 24 % | 88 % — first shutters down |
| 22:00 | **93 % — peak** | 16 % | 68 % |
| 23:00 | 80 % — turning in | 11 % | 38 % — mostly closed |
| 00:00 | 52 % | 7 % — all-nighters, cleaners | 18 % — the late traders |
| 02:00 | 22 % | 5 % | 8 % |
| 04:00 | 11 % — the city sleeps | 4 % | 6 % |

Villages turn in earlier still; industrial and institutional blocks (stations, utilities,
hospitals) keep a skeleton of lights. Switch-on is staggered by a `uDusk` ramp: shopfronts
glow as soon as the light fades, offices shortly after, homes only once it is properly dark.

Source: Planning Department **"2023 Raster Grids on Land Utilization"** (LUHK, 10 m grid),
CSDI dataset `pland_rcd_1696577406166_85973`, DATA.GOV.HK Terms of Use. The GeoTIFF
download is gated behind the portal's CDN, so the pipeline reads the raster through the
dataset's public ArcGIS MapServer instead: four native-resolution BMP exports
(uncompressed — each class value renders as one exact grey), with the grey→value table
established by `identify` queries and cross-checked against the raster attribute table's
per-value pixel counts (exact match for every code).

The service's stretch renders values 1–3 (Private Residential, Public Residential, Rural
Settlement) as black, indistinguishable from no-data — confirmed by sampling 43k named
towers: 96% of public estates and 95% of the large private estates fall on black, 68% of
Central's office towers on 11 (Commercial), 92% of "… Industrial Building" on 21, 90% of
hospitals / schools / police stations on 31 (G/IC). So black under a footprint means
residential, which is the default class. Mapping used:

| LUHK value | class | viewer use |
|---|---|---|
| 0 (1–3 clipped) | Private / Public Residential, Rural Settlement | residential |
| 11 | Commercial | office (podium → retail) |
| 21 · 22 · 23 | Industrial land · Industrial estates/science parks · Warehouse & open storage | industrial |
| 31 | Government, Institution & Community | institutional |
| 32 | Open space & recreation | other |
| 41–44 | Roads · Railways · Airport · Port | other |
| 51–54 | Cemeteries · Utilities · Vacant/construction · Other urban | other |
| 61 · 62 | Agriculture · Fish ponds | village |
| 71–74 | Woodland · Shrubland · Grassland · Mangrove/swamp | village (hillside huts) |
| 81 · 83 · 91 · 92 | Badland · other · reservoirs · streams | other |

Podium blocks in commercial or residential zones are shopping floors → retail hours.
In the shader, the two lowest floors of any urban block are shopfronts and follow retail
hours too. Per-class curves live in `buildings.js` (`AWAKE`).

## Rendering (`buildings.js`)

- **Placement**: bottom/top per block on the current terrain: ground blocks get a
  skirt from their base down to the lowest rendered-DEM point under the footprint
  (nothing floats on the 70 m mesh); blocks that sit on another block's roof
  (base within 1.5 m of a containing block's top — detected once with the spatial
  hash) start exactly at their base; height-less blocks sit on the ground. Blocks
  whose top is under the lowest DEM point beneath them are skipped as buried.
- **Two disjoint tiers**: *big* (≥ 10 m tall or ≥ 300 m² — ~65k blocks; 16 m / 600 m²
  on coarse-pointer devices) in 4 km chunks, built progressively after load and kept;
  *small* (everything else) in 1 km chunks streamed within 4.5 km of the focus
  (walker / plane / orbit target) and evicted beyond 8 km, capped at 110 chunks.
- **Geometry**: one indexed `BufferGeometry` per chunk, two groups (walls, roofs),
  positions + metre-scaled UVs + `Uint8` vertex colours; no normals (`flatShading`
  derives face normals in the shader). Roofs are earcut via `ShapeUtils.triangulateShape`.
- **Look**: per-block tint by type and height (glass for ≥ 160 m and a minority of
  100–160 m towers — the data has no use class; pale concrete, tong-lau warmth,
  village creams, grey podia, sheet-metal sheds), a procedural 3.6 m window-bay
  texture, and a lit-window `emissiveMap` whose intensity follows the sky
  simulation's luminance so the city lights up through dusk; which windows are lit is
  a per-bay random bedtime against the land-use class's awake curve for the sky sim's
  Hong Kong clock (see *Land use* above). Cloud shadows and
  height fog come from the shared `attachTerrainFX` hook; the Matrix look swaps to
  a phosphor wireframe.
- **Exaggeration**: the group is authored in real metres and `scale.y = VE`, exactly
  like the terrain, so Walk (VE pinned to 1) is true to life.
- **Labels**: the ~60 tallest distinctly-named towers (ICC, Two IFC, Central Plaza,
  Bank of China Tower …) as landmark-style cards anchored at roof height, within 12 km.

## Movement

- **Walk**: the ground is `max(DEM, standAt)` where `standAt` is the highest block top
  at or below your feet (+0.6 m step); `solidAt` blocks a move into any block spanning
  body height. So towers are obstacles, roofs you drop onto are floors, stepping off a
  roof is a fall, and canopies above head height can be walked under.
- **Fly**: rooftops count as ground — land on one, and flying into a facade (AGL < 0)
  parks you on that roof, arcade-style.

## Urban-core terrain (Victoria Harbour · 20 m)

`source-scripts/hk-5m/build_urban_mesh.mjs` cuts a 22 × 22 km window (E 826 000–848 000,
N 806 000–828 000: HK Island, Kowloon, Kwai Tsing / Tsuen Wan, Sha Tin's south, Tseung
Kwan O) from the LandsD 5 m DTM at 20 m cells (4 × 4 LiDAR cells averaged) →
`3d-viewer/data/hk-harbour-dtm20m.json` (1100 × 1100, 1.21 M vertices, 3.1 MB) +
`hk-harbour-georef.json`, in the same HK1980 grid, selectable as **Victoria Harbour ·
LandsD 5 m @ 20 m** (default exaggeration 1.6×). 3.5× finer than the territory mesh, so
reclamation edges, the Mid-Levels terraces and street-scale slopes carry the buildings
properly. The territory-wide B50K vectors are clipped to the mesh in `buildSkin`.

## Lantau · Terrarium source: georef corrected

The **Lantau · AWS Terrarium ~30 m** mesh (360 × 270, drawn at 62.46 m cells) shipped with a
georef of 60.84 × 30.91 m cells anchored at N 818 469 — it described an area half as tall as the
mesh, so anything placed by easting/northing (buildings, roads, coast, landmarks, GPS) landed up
to 800 m off and Tung Chung's towers stood in the sea. Fitting the mesh's elevations against the
territory mesh (3 000 land samples, isotropic-cell constraint) gives **63.0 m square cells, origin
E 801 390 / N 823 260** with a 9 m mean absolute residual (139 m before). The Web Mercator z14
tiles it was cut from are conformal, so square cells are what the mesh actually has; the 0.9 %
difference from the drawn 62.46 m is below the terrain's own resolution. The LandsD 5 m Lantau
mesh was checked the same way and is right to within one cell (best shift −20 m, no rotation).

## Known limits / follow-ups

- Only the harbour core has the 20 m mesh; elsewhere the 70 m-averaged DEM can still
  sit above true base levels on steep slopes and bury lower floors.
- LOD1 boxes only: no roof shapes, no textures from imagery. LandsD's 3D Visualisation
  Map (glTF tiles) could supply LOD2 for the Central core later.
- The satellite/OSM drape's datum shift should move to the exact Helmert above.

Built by Claude (Claude Code) for HKS-114, 2026-09-06.
