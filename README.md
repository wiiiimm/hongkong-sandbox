# Hong Kong Sandbox · 香港沙盤

*An interactive 3D Hong Kong you can play with — real LiDAR terrain, live Hong Kong
Observatory weather & tides, a full typhoon simulator (signals No.1–10), live weather
stations, and OSM / satellite skins. Bilingual (EN / 繁中).*

Built from real Digital Elevation Models and layered with live open data. Pure static
HTML + ES modules + Three.js — **no build step, no framework** — so it runs by opening a
file (via any static server) and deploys as plain files.

<!-- TODO: hero screenshot / GIF (tracked as HKS-10) -->

**Live:** https://hongkong-sandbox.pages.dev

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
- **Landmarks & peaks** — a curated landmarks layer (iconic hiking peaks + key towns) plus a full named-peaks layer from OSM, both terrain-occluded (labels hide behind mountains) and decluttered.
- **Shareable** — every control, the camera, and the locale serialise to the URL.

## Design & constraints

The whole thing is deliberately **static and dependency-light** — this is a design goal, not a limitation:

- **Zero build, no framework.** Plain `index.html` + ES-module JavaScript + a *vendored* copy of Three.js. No React/Vue/Svelte, no bundler, no `npm install`, no build step. Open it through any static file server and it runs; "deploying" is just copying files.
- **Why:** longevity and hackability. Anyone can read the source, change a number, and hit refresh — no toolchain to learn or keep alive, and it'll still run years from now. Ideal for "here, go fuck around with it."
- **Precomputed offline, rendered client-side.** DEMs are sliced and georeferenced by small Python scripts (`source-scripts/`) into compact JSON the browser loads directly; all projections (HK1980 grid ↔ WGS84 ↔ Web Mercator) run in plain JS in the browser. No server, no database, no API keys.
- **Live data from open, CORS-friendly endpoints.** Weather/tides/lightning come straight from HKO / data.gov.hk (per-station feeds routed through data.gov.hk's archive for CORS). The *only* server-side code is a ~40-line Cloudflare Pages Function for `/en-hk/` `/zh-hk/` locale routing — and the app degrades gracefully to `?locale=` + browser detection when it isn't running.
- **State lives in the URL.** Every control, the camera, and the locale serialise to the query string, so any view is shareable and bookmarkable with no backend.
- **Trade-offs, honestly:** hand-written WebGL + DOM instead of a scene-graph/UI framework, a fairly large vendored Three.js, and plenty of hand-tuned magic numbers. All accepted in exchange for the no-dependency, no-build simplicity.

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

## Data sources

Everything is built on open data. Each source keeps its own licence/terms; attribution is shown in-app and listed here.

| Source | Used for | Licence / terms |
|---|---|---|
| **Hong Kong Observatory (HKO)** via DATA.GOV.HK | live temperature, humidity, wind, rainfall; tide predictions (HHOT); warnings (warnsum); past-hour lightning counts (LHL); forecast (flw) | [DATA.GOV.HK Terms of Use](https://data.gov.hk/en/terms-and-conditions) — free to use with attribution |
| **Lands Department 5 m DTM** (2020 LiDAR) via DATA.GOV.HK / CSDI | HK & Lantau terrain meshes — HK1980 grid (EPSG:2326), ±5 m | DATA.GOV.HK Terms of Use |
| **Lands Department B50K** (1:50 000) | topographic skin + vector layers (contours, roads, trails, hydro, coastline, boundaries, cliffs) | DATA.GOV.HK Terms of Use |
| **NASA SRTM / Mapzen "Terrarium"** via AWS Open Data | ~30 m fallback terrain | public domain / [AWS Open Data](https://registry.opendata.aws/terrain-tiles/) |
| **OpenStreetMap** | street-map skin (live tiles); named peaks & landmarks baked into `data/hk-peaks.json` + `data/hk-landmarks.json` | © OpenStreetMap contributors, **[ODbL](https://opendatacommons.org/licenses/odbl/)** |
| **Esri World Imagery** | satellite skin (live tiles) | © Esri, Maxar, Earthstar Geographics — [Esri Terms of Use](https://www.esri.com/en-us/legal/terms/full-master-agreement) |
| **Three.js** (vendored in `3d-viewer/vendor/`) | 3D rendering | MIT |

Notes:
- OSM-derived data files bundled here are © OpenStreetMap contributors under the **Open Database License (ODbL)** — keep the attribution if you reuse them.
- Esri and OSM basemap **tiles are fetched live at runtime** and shown with attribution; none are redistributed in this repo. Google Maps/Satellite tiles are intentionally **not** used — their ToS forbids draping onto a custom 3D surface.
- All terrain is derived purely from the DEMs (no reference-map tracing).

## Licence

- **Code:** [GNU AGPL-3.0](LICENSE) — free to use, modify, and self-host, **as long as your
  version stays open under the AGPL** (including when served over a network). Contributions
  are covered by a light CLA — see [`CONTRIBUTING.md`](CONTRIBUTING.md).
- **Commercial / closed-source use:** available separately — the AGPL doesn't allow closed
  forks or unshared hosted modifications, so if you need that, see [`COMMERCIAL.md`](COMMERCIAL.md).
- **Data:** third-party, under the licences in the table above (notably OSM data is ODbL).
  The code licence covers this project's *code* only — it does not relicense the data.

© 2026 William Li. Made for Hong Kongers to fork and mess around with. 🇭🇰
