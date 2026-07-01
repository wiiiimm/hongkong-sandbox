# Lantau Island — Interactive 3D Terrain Viewer

A self-contained, rotatable 3D model of **Lantau Island, Hong Kong (大嶼山)**, built
from real elevation data. Open `index.html` in any modern browser — drag to orbit,
scroll to zoom, right-drag to pan.

---

## 1. What this is

`index.html` is a single file with **no build step and no server required**. The
terrain heightmap (a 360 × 270 grid of real elevations) is embedded directly inside
the HTML as JSON, and the page renders it as a true 3D mesh with [Three.js]. The only
external dependency is the Three.js library itself, loaded from a CDN — so the file
needs an internet connection the first time you open it, but the terrain data is local.

Controls in the page:

- **Drag** = orbit · **scroll** = zoom · **right-drag** = pan (one-finger / two-finger on touch)
- **Vertical ×** slider — exaggerate the relief (1× true-to-scale … 6×)
- **Spin** — toggle slow auto-rotation
- **Labels** — peak/town markers (Traditional Chinese + English + elevation)
- **Water** — show/hide the sea plane
- **South view / Top-down** — preset camera angles

---

## 2. Where the elevation data comes from

The raw Digital Elevation Model (DEM) is the **AWS Open Data “Terrain Tiles”** dataset
(Mapzen / Tilezen *Terrarium* encoding), served free and without authentication from:

```
https://elevation-tiles-prod.s3.amazonaws.com/terrarium/{z}/{x}/{y}.png
```

Each tile is a 256×256 PNG where elevation is encoded in the pixel colour. We download
the 88 tiles at zoom **z14** that cover Lantau (x 13372–13382, y 7148–7155) and decode
every pixel to metres with the Terrarium formula:

```
elevation_metres = R * 256 + G + B / 256 − 32768
```

**Resolution caveat:** these tiles are a global composite of public DEMs. Over Hong Kong
the underlying source is essentially **SRTM (~30 m)** resampled onto the finer z14 grid
(~8.8 m/pixel). So the shape and relative proportions are accurate, but absolute heights
read slightly low — this DEM puts Lantau Peak at ~892 m vs the official **934 m**. For a
sharper model, swap in the Hong Kong Lands Department / CSDI **5 m DEM** or Copernicus
GLO-30; only `fetch_dem.py` / `assemble_dem.py` would need to change.

---

## 3. How it’s built (pipeline)

```
fetch_dem.py  ─▶  assemble_dem.py  ─▶  build_heightmap.py  ─▶  build_viewer.py  ─▶  index.html
   (tiles)          (elev.npy)          (data/heightmap.json)      (embed JSON)
```

1. **`scripts/fetch_dem.py`** — downloads the 88 Terrarium tiles into `tiles/`,
   validating each one (re-fetches truncated downloads).
2. **`scripts/assemble_dem.py`** — decodes + stitches the tiles into a single
   2816 × 2048 elevation grid `elev.npy`, and writes the geo-extent to `extent.txt`.
3. **`scripts/build_heightmap.py`** — the geographic processing:
   - builds a land mask (`elevation > 5 m`);
   - keeps **only the connected component containing the highest point**, which
     isolates Lantau and automatically drops Cheung Chau, Peng Chau, Hong Kong Island,
     the airport platform, etc.;
   - crops to the island, smooths lightly, and **downsamples to ~360 columns**
     (≈ 62.5 m per cell — small enough for the web, detailed enough to read);
   - maps eight labelled features from longitude to grid column;
   - writes `data/heightmap.json`.
4. **`scripts/build_viewer.py`** — substitutes `data/heightmap.json` into the
   `__DATA__` placeholder in `template.html` and writes the final self-contained
   `index.html`.

### Rebuild from scratch
```bash
pip install numpy scipy pillow
cd scripts
python3 fetch_dem.py            # -> tiles/        (needs internet)
python3 assemble_dem.py         # -> elev.npy, extent.txt
python3 build_heightmap.py      # -> data/heightmap.json
python3 build_viewer.py         # -> index.html
```
(`fetch_dem.py` / `assemble_dem.py` expect to run in a working dir; they write
`elev.npy` + `extent.txt` next to themselves. `build_heightmap.py` reads those two
files. If you keep the layout here, run them from a scratch folder and copy
`data/heightmap.json` back into this directory before `build_viewer.py`.)

---

## 4. How the viewer renders the terrain (inside `index.html`)

- **Mesh** — a Three.js `BufferGeometry` with one vertex per grid cell:
  `x = east`, `z = north` (in real metres, using the 62.5 m cell size so the island
  keeps true horizontal proportions), `y = elevation`. Two triangles per cell via an
  index buffer. It is a literal 3D surface, not a shading trick.
- **Colour** — a hypsometric ramp by elevation (greens → tan → brown → pale summits).
- **Relief / shading** — `computeVertexNormals()` + a directional “sun” light produce
  the hillshading live as you rotate, with a soft blue fill light and ambient term.
- **Sea** — a translucent plane at `y = 0`.
- **Vertical exaggeration** — the slider rescales every vertex’s `y` and recomputes the
  normals so the shading stays correct.
- **Controls** — a small hand-written orbit controller (spherical coords: azimuth,
  polar angle, radius) rather than Three’s OrbitControls, to keep dependencies minimal.
- **Labels** — plain HTML `<div>`s repositioned each frame by projecting each summit’s
  3D coordinate to screen space.

---

## 5. Files

```
.
├── index.html              ← open this (self-contained viewer + embedded data)
├── template.html           ← viewer with a __DATA__ placeholder (for rebuilding)
├── README.md
├── data/
│   └── heightmap.json      ← the 360×270 elevation grid + peak list
└── scripts/
    ├── fetch_dem.py        ← download Terrarium DEM tiles
    ├── assemble_dem.py     ← decode + stitch -> elev.npy, extent.txt
    ├── build_heightmap.py  ← isolate Lantau, downsample, find peaks -> heightmap.json
    └── build_viewer.py     ← embed JSON into template -> index.html
```

## 6. Provenance & licence notes

- Elevation: AWS Open Data Terrain Tiles (Mapzen/Tilezen Terrarium), which composite
  SRTM, ASTER, NED and other open DEMs. Check the dataset’s attribution terms before
  redistributing the data itself.
- Three.js is MIT-licensed (loaded from cdnjs at runtime).
- Built by Claude (Cowork) from the same DEM that drives the Lantau skyline logo and the
  engraved panorama in the sibling `lantau-skyline/` folder — the 3D model, the skyline
  silhouette, and the engraving are all the **same terrain** seen three ways.
