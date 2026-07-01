# Hong Kong 3D Model Package

This is the consolidated 3D terrain package for Hong Kong and Lantau Island.

It contains the whole-Hong-Kong terrain sources, the isolated Lantau terrain sources, B50K skins, and browser viewers with source pickers.

## View

Run the local server from the project root:

```sh
/Users/williamli/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m http.server 4173 --directory codex
```

Open:

```text
http://127.0.0.1:4173/hongkong-3d-model/index.html
```

Whole-Hong-Kong viewer:

```text
http://127.0.0.1:4173/hongkong-3d-model/hong-kong-3d-viewer.html
```

This is now the combined viewer. Its terrain source dropdown contains:

- `Hong Kong LandsD 5 m DTM`
- `AWS Terrarium Terrain Tiles`
- `Lantau LandsD 5 m DTM`
- `Lantau AWS Terrarium Terrain Tiles`

The two Lantau-only sources reuse the original Lantau model geometry, scale, camera, and isolated island presentation. They also support a Lantau-clipped B50K skin transformed from Hong Kong Grid coordinates into the local Lantau mesh coordinates.

The whole-Hong-Kong viewer has three mesh quality modes:

- `Adaptive detail` - starts with the standard mesh and swaps to detail when the camera is close.
- `Detail mesh` - default; always uses the higher-resolution mesh.
- `Standard mesh` - always uses the lighter mesh.

Quality mode applies only to the whole-Hong-Kong sources. The Lantau-only sources use their original single-resolution meshes.

## Data Sources

### Whole Hong Kong LandsD 5 m DTM

Folder:

```text
data/hong-kong-hk-landsd-5m/
```

Files:

- `terrain-mesh.json`
- `terrain.obj`

Current mesh:

- Standard: `137,600` vertices, `106,510` triangles
- Detail: `550,400` vertices, `413,510` triangles
- Vertical exaggeration: `1.45x`

### Whole Hong Kong AWS Terrarium Terrain Tiles

Folder:

```text
data/hong-kong-aws-terrarium/
```

Files:

- `terrain-mesh.json`
- `terrain.obj`
- `dem_tiles/`

Current mesh:

- Standard: `137,600` vertices, `121,672` triangles, Terrarium zoom `12`
- Detail: `550,400` vertices, `472,110` triangles, Terrarium zoom `13`
- Vertical exaggeration: `1.45x`

### B50K Topographic GML Skin

Folder:

```text
data/hk-b50k-gml/
```

Files:

- `iB50000GML.zip`
- `skin-lines.json`

Source:

`https://data.gov.hk/en-data/dataset/hk-landsd-openmap-b50k-topographic-map-of-hong-kong`

Direct download:

`https://www.landsd.gov.hk/landsd_psi_data/SMO/data/iB50000GML.zip`

The viewer currently uses simplified B50K line layers:

- transport
- hydro
- contours
- boundaries
- terrain

The original B50K GML is retained for rebuilds. `skin-lines.json` is a lightweight browser overlay derived from the original GML.

`skin-lines-lantau.json` is the Lantau-local version of the same B50K skin, clipped to the Lantau working extent and transformed into the original Lantau mesh coordinate system.

### Hong Kong LandsD 5 m DTM

Folder:

```text
data/hk-landsd-5m/
```

Files:

- `terrain-mesh.json`
- `terrain.obj`
- `Whole_HK_DTM_5m.zip`

Source:

`https://data.gov.hk/en-data/dataset/hk-landsd-openmap-5m-grid-dtm/resource/620c4f4f-eac4-472f-9074-dffa2ad596fd`

Direct download:

`https://www.landsd.gov.hk/landsd_psi_data/SMO/data/Whole_HK_DTM_5m.zip`

Current mesh:

- `36,698` vertices
- `72,368` triangles
- Viewer peak readout: `925 m`
- Vertical exaggeration: `1.7x`

### AWS Terrarium Terrain Tiles

Folder:

```text
data/aws-terrarium/
```

Files:

- `terrain-mesh.json`
- `terrain.obj`
- `dem_tiles/`

Source:

`https://registry.opendata.aws/terrain-tiles/`

Tile URL pattern:

```text
https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png
```

Current mesh:

- `14,219` vertices
- `27,802` triangles
- Viewer peak readout: `883 m`
- Vertical exaggeration: `2.0x`

## Which Source To Use

Use `Hong Kong LandsD 5 m DTM` for the best current terrain fidelity.

Use `AWS Terrarium Terrain Tiles` only as a fallback or for comparing the older global-data model.

## Scripts

Scripts are grouped in:

```text
scripts/
```

Important scripts:

- `build_hong_kong_3d_model.py` - builds the whole-Hong-Kong HK 5 m model, AWS Terrarium model, and B50K overlay skin.
- `build_hk_5m_lantau_model.py` - builds the HK 5 m model from the LandsD ASC grid ZIP.
- `generate_lantau_3d.py` - older AWS terrain tile model builder.
- `generate_lantau_skyline.py` - shared DEM/tile helpers and approximate Lantau mask.
- `verify_lantau_3d_model.cjs` - verifies the consolidated dropdown viewer.

## B200K

Do not use the B200K GML in the active terrain skin for this project right now.

B200K is useful for small-scale overview maps, thumbnails, or a territory-level inset, but it is too coarse for a 3D model where B50K linework can sit on a 5 m DTM. If the project later needs a very lightweight overview mode, B200K can be added as an optional low-detail skin.

## Caveats

- The coastline mask is still approximate and hand-coded.
- The HK 5 m build samples the ASC grid using a metadata-bounding-box affine mapping because GDAL/pyproj are not installed in the bundled runtime. This is suitable for visual work but not survey-grade analysis.
- Both models use vertical exaggeration for visual legibility.
- The B50K GML line overlay is simplified for browser performance. It should be treated as a visual skin, not a cartographic source export.
- The whole-Hong-Kong model is still a browser-friendly sampled mesh, not the full native 5 m grid. Rendering the complete LandsD DTM directly would require a tiled terrain LOD engine rather than one monolithic JSON mesh.
