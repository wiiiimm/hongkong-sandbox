# Lantau and outlying-island detail — HKS-122 / HKS-123

Produced by the GPT-6 Astra geography agent in the comparison worktree. This pass adds **31 source-grounded visit points and 412 mapped surface polygons across all 19 assigned sections**. It supplies 29 checked walking arrivals and two explicitly aerial-only island views. Existing village destinations and building-height policies are preserved.

The deployable package is `3d-viewer/city/data/regional/islands.json`: 107 beach polygons, 94 pier polygons, 154 sports pitches, 18 pedestrian areas and 39 apron polygon parts. Its 5,035 encoded vertices occupy approximately 206 kB. Three source holes are preserved. These are full mapped footprints, not rectangles drawn around place labels.

## Source and interpretation

Two retained OpenStreetMap queries supply the additional footprints and island polygons. Both snapshots report a database time of **6 September 2026, 06:55:36 UTC**. The queries are bounded to Hong Kong's mapped area and the island regions; their gzip snapshots and exact Overpass queries are in `source-scripts/city/regional/islands/snapshots/`. Existing city snapshots supply additional locality anchors and walking paths. `provenance.json` records every input, date, uncompressed SHA-256 and the generated package hash. Data attribution is **© OpenStreetMap contributors, ODbL 1.0**; see [OpenStreetMap's licence](https://www.openstreetmap.org/copyright).

Source island polygons select complete features for Lantau, Chek Lap Kok, Peng Chau, Hei Ling Chau, Cheung Chau, Lamma, Po Toi, the Soko group and smaller assigned islets, Tap Mun and Tung Ping Chau. A 25 m mask buffer retains attached waterfront footprints. These masks do not alter the rendered coastline. Within a larger island, the nearest configured locality anchor assigns a browsing-section label; these labels are not official boundaries.

Coordinates are projected to EPSG:2326 using the existing origin `[834500,816500]`. Complete polygons retain holes and use at most 0.5 m simplification, followed by 0.1 m coordinate rounding. The validator measures the resulting displacement against the retained source. Those tolerances describe encoding, **not survey accuracy**. Open pier lines are omitted because they have no sourced closed width. An explicitly mapped rooftop court and a pier carrying construction tags are also omitted.

[CEDD's public-pier inventory](https://www.cedd.gov.hk/eng/about-us/organisation/ceo/pwd/port-main/public_piers/nti/index.html) provides an authoritative naming and function cross-check for the island landings. [LCSD's beach information](https://www.lcsd.gov.hk/en/beach/) supplies official beach context. The [CEDD Mui Wo improvement project](https://sslo.cedd.gov.hk/en/our-projects/local-improvement-works/mui-wo/index.html) confirms the waterfront/promenade context, and [AsiaWorld-Expo's transport information](https://www.asiaworld-expo.com/en-us/visiting/getting-here/in-hong-kong/bus/) supports the airport-city public approach context. These references do not supply the package's polygon geometry or establish current transport services, opening hours or swimming conditions.

## Model additions by section

| Section | Area | New visits | Surface polygons |
| --- | --- | ---: | ---: |
| 10.1 | Tung Chung town and waterfront | 1 | 55 |
| 10.2 | Tung Chung valley, rural west and North Lantau | 1 | 3 |
| 10.3 | Chek Lap Kok terminals, aprons and runways | 1 | 42 |
| 10.4 | Airport east, north and boundary-crossing island | 1 | 5 |
| 10.5 | Discovery Bay and Nim Shue Wan | 1 | 56 |
| 10.6 | Mui Wo, Silvermine Bay and surrounding villages | 1 | 14 |
| 10.7 | Pui O and Chi Ma Wan | 2 | 17 |
| 10.8 | Cheung Sha, Tong Fuk and Shui Hau | 3 | 16 |
| 10.9 | Shek Pik, Fan Lau and southwest Lantau | 2 | 21 |
| 10.10 | Tai O and northwestern villages | 2 | 14 |
| 10.11 | Ngong Ping and Lantau mountain approaches | 1 | 2 |
| 10.12 | Peng Chau and Hei Ling Chau | 2 | 26 |
| 10.13 | Cheung Chau | 2 | 33 |
| 10.14 | Northern Lamma | 1 | 24 |
| 10.15 | Southern Lamma | 2 | 31 |
| 10.16 | Po Toi, Soko Islands and offshore islets | 2 | 18 |
| 11.6 | Sunny Bay, Yam O and northeast Lantau | 2 | 5 |
| 11.7 | Penny's Bay and Disneyland coast | 2 | 18 |
| 14.8 | Tap Mun and Tung Ping Chau | 2 | 12 |

Priority villages receive distinct visible source detail: Silvermine Bay's beach, pedestrian area and sports grounds around Mui Wo; Tai O's promenade footprint and sports areas; Peng Chau's ferry/public piers, beaches and mini-soccer pitch; and Cheung Chau's harbour pier, Tung Wan/Kwun Yam beaches, pedestrian areas and courts. Large apron polygons make the airport's functional areas legible. The shared regional renderer integrates these surfaces; this data pass does not claim a completed architectural reconstruction.

## Arrival verification

Every walking arrival is on a retained OSM footway, pedestrian way, path or living street with no explicit private/no-foot restriction. The search excludes bridges, tunnels, underground routes and non-zero layers. Rounded arrival coordinates must pass the actual terrain-triangle and building-clearance checks: all terrain vertices beneath the arrival and its four 2 m neighbours are dry; local elevation change stays below 1.5 m; and a 1.2 m character disc clears vertically overlapping buildings. Rendered and raw terrain heights are both checked. The encoded spawn remains within 7.1 cm of the source path.

The maximum source-centre-to-arrival offset is 381 m at Terminal 1. Chi Ma Wan's pier approach requires 307 m and Upper Cheung Sha 358 m because nearer candidates do not satisfy these terrain/path checks. All other arrivals are within 125 m of their source centre. Village locality anchors may use a mapped public facility footprint (Pak Mong and Fan Lau); the walking spawn is on a checked path outside that footprint. Camera centres and arrival positions are approximate browsing locations, not surveyed entrances.

Hei Ling Chau and the Soko Islands are explicitly aerial-only: this pass supplies no checked public walking arrival. A local clearance check does not prove a complete walking route, public accessibility at the time of a real visit, or detailed section acceptance.

## Reproduction and evidence

From the worktree root, with `pyproj` and `shapely` installed:

```sh
python source-scripts/city/regional/islands/fetch.py
python source-scripts/city/regional/islands/build.py
python source-scripts/city/regional/islands/validate.py
```

`fetch.py` reuses retained files. `build.py` makes no live requests and only writes this package and island evidence. The shared `source-scripts/city/build_regional.py` independently audits these arrivals when assembling all regional packages.

- `provenance.json`: sources, input hashes, output hash, counts, omissions and per-arrival source offsets.
- `validation.json`: source-boundary displacement, preserved holes, terrain/manifest hashes, and all 29 checked arrivals.
- `source-scripts/city/regional/islands/config.json`: the explicit section, island and destination source assignments.

## Remaining limitations

Piers are visual mapped footprints with no newly surveyed deck elevation or walking collision. The retained 70 m terrain can smooth small islands, beach edges and narrow channels. **Tai O's tidal channels remain unresolved**, and its promenade source (`way/115584709`) explicitly notes imagery distortion; that note is preserved in the package. Shui Hau and other sparsely mapped settlements still need architectural data. No invented buildings, roofs, heights, channel cuts or coastline corrections are introduced. Existing reference archives and historical Lantau images were not used or modified. Detailed village architecture, shoreline alignment and continuous walking-route review remain pending.
