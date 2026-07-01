# Hong Kong Sandbox · 香港沙盤
<a id="top"></a>

**English** · [繁體中文](#繁體中文)

*An interactive 3D Hong Kong you can play with — real LiDAR terrain, live Hong Kong
Observatory weather & tides, a full typhoon simulator (signals No.1–10), live weather
stations, and OSM / satellite skins. Bilingual (EN / 繁中).*

Built from real Digital Elevation Models and layered with live open data. Pure static
HTML + ES modules + Three.js — **no build step, no framework** — so it runs by opening a
file (via any static server) and deploys as plain files.

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

---

## 繁體中文

[English ↑](#top)

*一個可以任你把玩的互動 3D 香港 —— 真實光學雷達（LiDAR）地形、香港天文台實時天氣及潮汐、完整颱風模擬（一號至十號風球）、實時氣象站，以及 OSM／衛星圖層。中英雙語。*

以真實數碼高程模型（DEM）建構，疊加實時開放數據。純靜態 HTML + ES modules + Three.js —— **零建置、無框架** —— 只要用任何靜態伺服器開啟檔案即可運行，部署就是複製檔案。

**線上版：** https://hongkong-sandbox.pages.dev

### 功能

- **真實地形** —— 官方 **香港 5 米 LiDAR**（地政總署）及 **SRTM ~30 米**，涵蓋 **大嶼山** 與 **全香港**（四款資料來源）。
- **表面樣式** —— 陰影地貌、高程著色、霧面、純色、**B50K 地形圖皮膚**，以及可披覆的 **網上地圖**：OpenStreetMap 與 Esri 衛星圖（UV 由 HK1980 格網重新投影至 Web Mercator，令影像準確貼合海岸線）。
- **向量圖層** —— 等高線、道路、山徑、水系、海岸線、界線、懸崖。
- **垂直誇張**、可調 **網格密度**、自動旋轉、深色／紙本主題。
- **天氣模擬** —— 雨、雲、霧、閃電、潮汐與波浪，以及香港 **熱帶氣旋警告信號 T1/T3/T8/T9/T10**，隨信號增強風力、風暴潮、天色與震動。
- **實時天氣** —— 一鍵同步香港天文台報告（氣溫／濕度／風／天氣狀況、香港時間、潮汐預報波形圖），並以實況驅動特效。
- **實時氣象站** —— 約 50 個香港天文台自動氣象站，以電視天氣報告式資訊卡顯示（氣溫／濕度／風，中英名稱），資料來自各站數據。
- **雙語** —— 英文（香港）／繁體中文（香港），在 Cloudflare 以 `/en-hk/`、`/zh-hk/` 路由，其他環境則以 `?locale=`／瀏覽器偵測作後備。
- **地標與山峰** —— 精選地標圖層（著名行山山峰＋主要市鎮），以及來自 OSM 的完整命名山峰圖層；兩者均有地形遮擋（標籤會被山體遮住）並自動避免重疊。
- **可分享** —— 所有控制項、鏡頭與語言都會寫入網址。

### 設計與取捨

整個專案刻意保持 **靜態、少依賴** —— 這是設計目標，並非限制：

- **零建置、無框架。** 純 `index.html` + ES module JavaScript + 內附（vendored）的 Three.js。沒有 React／Vue／Svelte、沒有打包工具、無需 `npm install`、沒有建置步驟。用任何靜態伺服器開啟即可運行，「部署」不過是複製檔案。
- **原因：** 長壽與可玩性。任何人都能讀原始碼、改個數字、重新整理就見效 —— 不用學或維護工具鏈，多年後仍然跑得動。正好適合「喏，拿去玩」。
- **離線預先計算、瀏覽器端渲染。** DEM 由小型 Python 腳本（`source-scripts/`）切割與地理配準成精簡 JSON，瀏覽器直接載入；所有投影（HK1980 格網 ↔ WGS84 ↔ Web Mercator）都在瀏覽器以純 JS 計算。沒有伺服器、沒有資料庫、不需 API 金鑰。
- **實時數據來自開放且支援 CORS 的端點。** 天氣／潮汐／閃電直接取自香港天文台／data.gov.hk（各站數據經 data.gov.hk 封存代理以解決 CORS）。唯一的伺服器端程式，是約 40 行的 Cloudflare Pages Function 用作 `/en-hk/`、`/zh-hk/` 語言路由 —— 若它未運行，程式會優雅地退回 `?locale=` ＋瀏覽器偵測。
- **狀態存於網址。** 所有控制項、鏡頭與語言都序列化到查詢字串，任何畫面都可分享、可加書籤，毋須後端。
- **老實說的取捨：** 手寫 WebGL + DOM 而非場景圖／UI 框架、內附的 Three.js 體積不小、以及大量人手調校的魔術數字 —— 全為換取無依賴、零建置的簡潔。

### 本機運行

程式是靜態的，但 ES module 與 `fetch()` 需要經伺服器提供（不能直接以 `file://` 開啟）。任何靜態伺服器皆可：

```bash
# 方法 A —— 內附的零依賴開發伺服器（改檔即時重載）
node tools/dev-server.mjs           # → http://127.0.0.1:8777/

# 方法 B —— 其他任何工具
python3 -m http.server -d 3d-viewer 8777
```

要測試 **`/en-hk/`、`/zh-hk/` 語言路由**（Cloudflare Pages Function），用 Wrangler 在本機模擬 Pages Functions：

```bash
npx wrangler pages dev 3d-viewer    # → http://localhost:8788/（會將 / 導向 /en-hk/）
```

沒有 Wrangler 時，路由會退回 `?locale=` + `localStorage` + `navigator.languages`，所以除路徑式網址外，普通開發伺服器已足夠。

### 部署（Cloudflare Pages）

推送到 `main` 會經 GitHub Actions（`.github/workflows/deploy-cloudflare-pages.yml`）部署 `3d-viewer/`。需要兩個 repo secrets：`CLOUDFLARE_API_TOKEN` 與 `CLOUDFLARE_ACCOUNT_ID`。語言中介程式位於 `3d-viewer/functions/_middleware.js`，會隨部署一併上載。

### 資料夾

| 資料夾 | 內容 |
|--------|------|
| **`3d-viewer/`** | 可部署的程式：`index.html`、`main.js`、內附 Three.js、`data/`（網格、地理配準、B50K 向量、氣象站座標）及 `functions/`（語言中介程式）。 |
| **`source-scripts/`** | 可重現的流程 —— DEM 切割／投影（`srtm-30m/`、`hk-5m/`）、B50K 向量／土地覆蓋擷取、DEM 去尖峰，以及香港天文台氣象站座標。 |
| **`docs/`** | 方法與出處說明。 |
| **`references/`** | 唯讀來源參考與早期作品（運行時不需要）。 |

### 資料來源

一切建基於開放數據。每個來源保留其自身授權／條款；程式內已標示出處，此處亦一併列出。

| 來源 | 用途 | 授權／條款 |
|---|---|---|
| **香港天文台（HKO）** 經 DATA.GOV.HK | 實時氣溫、濕度、風、雨量；潮汐預報（HHOT）；警告（warnsum）；過去一小時閃電次數（LHL）；天氣預報（flw） | [DATA.GOV.HK 使用條款](https://data.gov.hk/tc/terms-and-conditions) —— 可免費使用，須註明出處 |
| **地政總署 5 米數碼地形模型**（2020 LiDAR）經 DATA.GOV.HK／CSDI | 香港及大嶼山地形網格 —— HK1980 格網（EPSG:2326），±5 米 | DATA.GOV.HK 使用條款 |
| **地政總署 B50K**（1:50 000） | 地形圖皮膚＋向量圖層（等高線、道路、山徑、水系、海岸線、界線、懸崖） | DATA.GOV.HK 使用條款 |
| **NASA SRTM／Mapzen「Terrarium」** 經 AWS Open Data | ~30 米後備地形 | 公有領域／[AWS Open Data](https://registry.opendata.aws/terrain-tiles/) |
| **OpenStreetMap** | 街道圖皮膚（實時圖磚）；命名山峰及地標（已封裝於 `data/hk-peaks.json`、`data/hk-landmarks.json`） | © OpenStreetMap 貢獻者，**[ODbL](https://opendatacommons.org/licenses/odbl/)** |
| **Esri World Imagery** | 衛星圖皮膚（實時圖磚） | © Esri、Maxar、Earthstar Geographics —— [Esri 使用條款](https://www.esri.com/en-us/legal/terms/full-master-agreement) |
| **Three.js**（內附於 `3d-viewer/vendor/`） | 3D 渲染 | MIT |

備註：

- 本 repo 內源自 OSM 的資料檔案為 © OpenStreetMap 貢獻者，採用 **開放資料庫授權（ODbL）** —— 如再使用請保留出處標示。
- Esri 與 OSM 的底圖 **圖磚為執行時實時取得** 並顯示出處；本 repo 不會轉存任何圖磚。有意不使用 Google 地圖／衛星圖磚 —— 其條款禁止披覆到自訂 3D 表面。
- 所有地形純由 DEM 生成（沒有描摹參考地圖）。

### 授權

- **程式碼：** [GNU AGPL-3.0](LICENSE) —— 可自由使用、修改與自行架設，**惟你的版本須依 AGPL 保持開源**（包括經網絡提供服務時）。貢獻受一份輕量 CLA 規範，見 [`CONTRIBUTING.md`](CONTRIBUTING.md)。
- **商業／閉源用途：** 另行提供 —— AGPL 不允許閉源分支或不公開原始碼的託管修改版，如有需要請見 [`COMMERCIAL.md`](COMMERCIAL.md)。
- **資料：** 屬第三方，依上表授權（尤其 OSM 資料為 ODbL）。程式授權僅涵蓋本專案的*程式碼*，不會重新授權該等資料。

© 2026 William Li。為香港人而做，隨便 fork 隨便玩。🇭🇰
