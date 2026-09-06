# Central and Victoria Harbour city import

Produced by GPT-6 Astra for the isolated `codex/astra-hong-kong-city` comparison.

The committed `central-osm.json.gz` is an unmodified Overpass response, compressed
with a deterministic gzip timestamp. Its OpenStreetMap base timestamp is
**2026-09-06 04:30:21 UTC**. The query and bounding box live in `build_city.py`.
The source snapshot and derived OSM database are **ODbL 1.0**, attributed to
[OpenStreetMap contributors](https://www.openstreetmap.org/copyright).

From the repository root:

```sh
python3 -m venv /tmp/hk-city-import
/tmp/hk-city-import/bin/pip install -r source-scripts/city/requirements.txt
/tmp/hk-city-import/bin/python source-scripts/city/build_city.py
/tmp/hk-city-import/bin/python source-scripts/city/test_import.py
```

Use `--fetch` to replace the snapshot with a fresh bounded Overpass response and
rebuild, or `--input /path/to/overpass.json` to import a downloaded response.
A normal build uses the committed snapshot and performs no network requests.

The importer:

- Projects WGS84 coordinates to **EPSG:2326** using PROJ, then subtracts a local
  origin, E 834500 / N 816500. World x is east, z is south, y is metres above datum.
- Preserves irregular footprints and multipolygon courtyard holes; repairs invalid
  polygons with Shapely, removes tiny features, and clips to the requested district.
- Replaces building outlines substantially covered by detailed building parts and
  carries parent names into unnamed parts. The renderer does not interpret roof
  profiles, façade textures or individual roof equipment from OSM.
- Excludes underground structures and tunnels. Above-ground roads/footways remain;
  their widths and bridge clearances are illustrative class-based estimates.
- Uses `height` where present. Otherwise uses `building:levels × 3.2 m`.
  Untagged fallback: 24 m; footprints over 8,000 m²: 9 m; service/shed/garage: 6 m.
  `heightSource` distinguishes `tagged`, `levels` and `estimated` on every feature.
  A mapped height is not a claim that the source was surveyed or independently verified.
- Keeps the existing Lands Department 70 m terrain grid and B50K landcover in the
  same CRS. The source product was 5 m; this committed mesh is **70 m**, with no
  vertical exaggeration. Coastlines therefore inherit that terrain resolution.

Outputs live in `3d-viewer/city/data/`. Their provenance manifest includes counts,
origin, CRS, bounds, snapshot and height policy. Building form counts include parts;
**9,743 forms is not a count of 9,743 distinct addresses or whole buildings**.

Terrain inputs are `3d-viewer/data/hk-dtm5m.json`, `hk-georef.json`,
`hk-texbb.json` and `hk-b50k-landcover.json`. See the existing terrain pipeline for
original source provenance. No archival images in `references/lantau-maps/` were
used or modified for this feature.

References:

- [OSM height semantics and units](https://wiki.openstreetmap.org/wiki/Key:height)
- [OSM building floor counts](https://wiki.openstreetmap.org/wiki/Key:building:levels)
- [OSM copyright and ODbL attribution](https://www.openstreetmap.org/copyright)
