# Hong Kong Island, Kowloon and Lantau city import

Produced by GPT-6 Astra for the isolated `codex/astra-hong-kong-city` comparison.

## Current streaming dataset (v2)

`regions.json` defines four bounded regional queries. `snapshots/` contains their
unmodified Overpass responses in deterministic gzip files, alongside the exact
queries. The existing `central-osm.json.gz` is a fifth source. The OSM base
snapshots range from **2026-09-06 04:30:21 to 04:58:51 UTC**. Source timestamps,
query bounds and SHA-256 hashes of the uncompressed responses are recorded in
`3d-viewer/city/data/manifest.json`.

The source snapshots and derived OSM database are **ODbL 1.0**, attributed to
[OpenStreetMap contributors](https://www.openstreetmap.org/copyright).

From the repository root:

```sh
python3 -m venv /tmp/hk-city-import
/tmp/hk-city-import/bin/pip install -r source-scripts/city/requirements.txt
# Rebuild entirely from the committed snapshots, without network requests.
/tmp/hk-city-import/bin/python source-scripts/city/build_tiles.py
/tmp/hk-city-import/bin/python source-scripts/city/test_import.py

# Optional source refresh: bounded queries, performed sequentially.
/tmp/hk-city-import/bin/python source-scripts/city/fetch_regions.py --region lantau --refresh
# Omit --region to process all four. Without --refresh, cached snapshots are reused.
```

V2 merges overlapping sources by OSM type/id, with newer snapshot records winning.
Building outlines substantially covered by mapped parts are suppressed; parent
names are inherited. A building belongs to exactly one 2 km tile but keeps its
complete footprint. Tile bounds expand to include it, so streaming and collision
queries also find geometry crossing a cell edge. Roads and parks are clipped to
cells. The global catalogue keeps named forms and their owning tile IDs; the
minimap overview stores compact building centres. Runtime never calls Overpass.

The current output contains **42,892 building forms**, **90,912 road/path
fragments**, and **668 park fragments** in **167 tiles** (34,383,986 bytes of tile
JSON). There are **1,836 tagged heights**, **18,742 level-derived heights**, and
**22,314 fallback estimates**. The importer suppressed 773 outlines covered by
building parts. Form counts include constituent parts, not unique addresses.

Query rectangles cover Hong Kong Island, urban Kowloon and Lantau approximately;
they do not follow administrative boundaries. Neither the source nor this import
is assumed complete. The mainland New Territories still needs deliberate import.

## Original Central fixture (v1)

`build_city.py`, `central-osm.json.gz`, `data/central.json` and
`data/provenance.json` remain as the original reproducible Central fixture and
import-test baseline. The viewer now uses the v2 manifest and tiles. Run
`build_city.py` to rebuild v1 and the reused terrain dataset; `--fetch` refreshes
its original bounded query and `--input /path/to/overpass.json` uses a supplied
response. Follow with `build_tiles.py` when updating the runtime dataset.

The importer:

- Projects WGS84 coordinates to **EPSG:2326** using PROJ, then subtracts a local
  origin, E 834500 / N 816500. World x is east, z is south, y is metres above datum.
- Preserves irregular footprints and multipolygon courtyard holes; repairs invalid
  polygons with Shapely and removes tiny features. V1 clips to its query polygon;
  v2 retains full buildings intersecting regional coverage.
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

Outputs live in `3d-viewer/city/data/`. Their manifests include counts, origin,
CRS, bounds, snapshots and height policy. Tree placement is a deterministic,
illustrative runtime layer based on mapped landcover/parks, not surveyed trees.
Recent reclamation and small tidal creeks can disagree with the existing terrain;
see `docs/astra-city/SECTION-CHECKLIST.md` for the pending local accuracy reviews.

Terrain inputs are `3d-viewer/data/hk-dtm5m.json`, `hk-georef.json`,
`hk-texbb.json` and `hk-b50k-landcover.json`. See the existing terrain pipeline for
original source provenance. No archival images in `references/lantau-maps/` were
used or modified for this feature.

References:

- [OSM height semantics and units](https://wiki.openstreetmap.org/wiki/Key:height)
- [OSM building floor counts](https://wiki.openstreetmap.org/wiki/Key:building:levels)
- [OSM copyright and ODbL attribution](https://www.openstreetmap.org/copyright)
