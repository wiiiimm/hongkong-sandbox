# Lantau 3D Rendering - HK LandsD 5 m DTM Upgrade

This folder contains a higher-resolution version of the Lantau terrain model using the official Hong Kong Lands Department / data.gov.hk 5 m Digital Terrain Model.

The older viewer in `../lantau-3d-rendering/` uses public AWS Terrarium elevation tiles. This version uses the official LandsD 5 m grid and should be the preferred terrain source.

## Official Dataset

Dataset name:

`Digital Terrain Model (DTM)`

Traditional Chinese:

`數碼地形模型 (DTM)`

Provider:

`Lands Department`

data.gov.hk resource:

`https://data.gov.hk/en-data/dataset/hk-landsd-openmap-5m-grid-dtm/resource/620c4f4f-eac4-472f-9074-dffa2ad596fd`

Direct data download:

`https://www.landsd.gov.hk/landsd_psi_data/SMO/data/Whole_HK_DTM_5m.zip`

CSDI dataset id:

`landsd_rcd_1638158088368_93806`

Metadata page:

`https://portal.csdi.gov.hk/geoportal/rest/metadata/item/landsd_rcd_1638158088368_93806/html`

CSDI portal:

`https://portal.csdi.gov.hk/`

## Dataset Details Verified From CSDI Metadata

- Coverage: whole Hong Kong
- Spatial representation: grid
- Format from data.gov.hk: ASC / ESRI ASCII grid in ZIP
- Format listed in CSDI metadata: GeoTIFF
- Grid spacing: 5 m
- Vertical accuracy: +/- 5 m
- Height reference system: HKPD height, EPSG:5738
- Publication date: 2025-02-18
- Creation/revision dates in metadata: 2017 / 2019
- Note in metadata: includes some non-ground information such as elevated roads and bridges
- Note in metadata: if land is covered by vegetation, terrain may be depicted by vegetation height

## Downloaded Input

The official data.gov.hk ZIP has been downloaded into:

```text
data/Whole_HK_DTM_5m.zip
```

The ZIP contains one file:

```text
Whole_HK_DTM_5m.asc
```

## Generated Output

Generated files are in `output/`:

- `output/lantau-hk-5m-terrain-mesh.json`
- `output/lantau-hk-5m-terrain.obj`
- `output/lantau-hk-5m-3d-viewer.html`
- `output/lantau-hk-5m-3d-viewer-desktop.png`
- `output/lantau-hk-5m-3d-viewer-mobile.png`
- `output/vendor/`

## Build Script

The build script is:

```text
build_hk_5m_lantau_model.py
```

It streams the ASC grid from the ZIP, crops to a Lantau working extent, applies an approximate island mask, samples a `360 x 220` mesh, and writes the viewer/OBJ/JSON outputs.

Run from the project root:

```sh
/Users/williamli/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 codex/lantau-3d-rendering-hk-5m/build_hk_5m_lantau_model.py
```

## View

With the local server running from the project root:

```sh
/Users/williamli/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m http.server 4173 --directory codex
```

Open:

```text
http://127.0.0.1:4173/lantau-3d-rendering-hk-5m/output/lantau-hk-5m-3d-viewer.html
```

## Verify

Run:

```sh
/Users/williamli/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node codex/lantau-3d-rendering-hk-5m/verify_hk_5m_viewer.cjs
```

Verified output:

- Desktop screenshot: `1440 x 960`
- Mobile screenshot: `390 x 844`
- Vertex count: `36,698`
- Triangle count: `72,368`
- Viewer peak readout: `925 m`
- Vertical exaggeration: `1.7x`

## Caveats

- This is more detailed than the AWS terrain-tile version, but still not perfect bare-earth terrain in all places because the metadata says vegetation, elevated roads, and bridges may appear.
- The current build samples the ASC grid using a metadata-bounding-box affine mapping because GDAL/pyproj are not installed in the bundled runtime. This is good enough for a visual model, but a future survey-grade build should use the official projection transform.
- For Lantau branding, the mesh should still be art-directed after terrain extraction: preserve true peak relationships, then simplify and smooth for visual use.
- The coastline mask should be improved with an official land boundary if we want a cleaner shoreline than the current hand-coded polygon.
