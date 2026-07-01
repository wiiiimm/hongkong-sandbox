# Hong Kong 3D Model — terrain-derived 3D viewer & artwork

*Lantau Island & all of Hong Kong, rendered from real elevation data.*

An interactive 3D terrain viewer for Hong Kong, built from real Digital Elevation
Models and layered with live open data. Pure static HTML + ES modules + Three.js —
**no build step, no framework** — so it runs by opening a file (via any static
server) and deploys as plain files.

![viewer](docs/) <!-- add a screenshot here -->

## Features

- **Real terrain** — official **HK 5 m LiDAR** (Lands Dept) and **SRTM ~30 m**, for
  both **Lantau** and **all of Hong Kong** (4-way source dropdown).
- **Surfaces** — shaded relief, elevation tint, matte, solid, the **B50K topographic
  skin**, and draped **web maps**: OpenStreetMap and Esri satellite (UVs reprojected
  from the HK1980 grid to Web Mercator so imagery lands exactly on the coast).
- **Vector layers** — contours, roads, trails, hydro, coastline, boundaries, cliffs.
- **Vertical exaggeration**, adjustable **mesh density**, auto-spin, dark/paper themes.
- **Weather simulation** — rain, clouds, fog, lightning, tides + waves, and Hong Kong
  **tropical-cyclone signals T1/T3/T8/T9/T10** with escalating wind, surge, sky and shake.
- **Live weather** — one click syncs to the HKO bulletin (temp/humidity/wind/status,
  HKT clock, tide-prediction waveform), and drives the effects from real conditions.
- **Live weather stations** — all ~50 HKO automatic weather stations plotted as TV-style
  cards (temp / humidity / wind, bilingual names), fed by the per-station feeds.
- **Bilingual** — English (HK) / 繁體中文（香港）, with `/en-hk/` `/zh-hk/` routing on
  Cloudflare and `?locale=` / browser-detection fallback everywhere else.
- **Shareable** — every control, the camera, and the locale serialise to the URL.

## Run locally

The app is static, but ES modules + `fetch()` need to be *served* (not opened as a
`file://`). Any static server works:

```bash
# option A — the included zero-dep dev server (live-reload on file change)
node tools/dev-server.mjs           # → http://127.0.0.1:8777/

# option B — anything else
python3 -m http.server -d 3d-viewer 8777
```

To exercise the **`/en-hk/` `/zh-hk/` locale routing** (the Cloudflare Pages Function),
run it through Wrangler, which emulates Pages Functions locally:

```bash
npx wrangler pages dev 3d-viewer    # → http://localhost:8788/  (redirects / → /en-hk/)
```

Without Wrangler the routing simply falls back to `?locale=` + `localStorage` +
`navigator.languages`, so the plain dev server is fine for everything except the
path-based URLs.

## Deploy (Cloudflare Pages)

Pushing to `main` deploys `3d-viewer/` via GitHub Actions
(`.github/workflows/deploy-cloudflare-pages.yml`). It needs two repo secrets:
`CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. The locale middleware lives in
`3d-viewer/functions/_middleware.js` and ships automatically with the deploy.

## Folders

| Folder | What's inside |
|--------|---------------|
| **`3d-viewer/`** | The deployable app: `index.html`, `main.js`, vendored Three.js, `data/` (meshes, georefs, B50K vectors, station coords), and `functions/` (the locale middleware). |
| **`source-scripts/`** | Reproducible pipelines — DEM slicing/projection (`srtm-30m/`, `hk-5m/`), B50K vector/land-cover extraction, DEM despiking, and HKO station coordinates. |
| **`docs/`** | Method & provenance notes. |
| **`references/`** | Read-only source references and prior work (not required to run). |

## Data sources & attribution

- **HK 5 m DTM** — Lands Department / CSDI, 2020 LiDAR, via DATA.GOV.HK
  (`Whole_HK_DTM_5m.zip`). HK1980 grid (EPSG:2326), ±5 m. *Lantau Peak 933 m (true ≈ 934).*
- **SRTM ~30 m** — AWS Open Data "Terrain Tiles" (Mapzen/Tilezen Terrarium). *Lantau Peak ~897 m.*
- **B50K** — 1:50 000 topographic vectors, Lands Department.
- **Live weather / tides / warnings** — Hong Kong Observatory via DATA.GOV.HK
  (per-station feeds routed through the `api.data.gov.hk` historical archive for CORS).
- **Web-map surfaces** — © OpenStreetMap contributors; Esri World Imagery
  (Esri, Maxar, Earthstar Geographics). *(Google tiles are intentionally not used — their
  ToS forbids draping onto a custom 3D surface.)*

All terrain artwork is derived purely from the DEMs (no reference-map tracing).

## Note on B200K
The 1:200 000 map (B200K) was **not used** — it's a coarser version of the same product;
the 1:50 000 (B50K) supersedes it for our skins.
