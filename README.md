# Hong Kong 3D Model — terrain-derived 3D viewer & artwork

*Lantau Island & all of Hong Kong, rendered from real elevation data.*

Everything here is generated from **real elevation data** (a Digital Elevation Model of
Lantau Island, Hong Kong), seen three ways: a skyline **logo**, an **engraved panorama**,
and an interactive **3D viewer**. Two DEMs were used — the official **HK 5 m LiDAR** (best)
and **SRTM ~30 m** (the first pass). The 5 m versions are the primary deliverables.

## Folders

| Folder | What's inside |
|--------|---------------|
| **`3d-viewer/`** | The interactive 3D terrain. Open `3d-viewer/index.html`; a **4-way dropdown** covers **Lantau** and **whole Hong Kong**, each in **5 m** and **~30 m**, with the **B50K topographic skin**. Self-contained + documented. |
| **`source-scripts/`** | The reproducible pipelines. `srtm-30m/` (download Terrarium tiles → project → render) and `hk-5m/` (slice the Lands Dept ASC → project → render). |
| **`docs/`** | Method & provenance notes: `method-notes-srtm30.md`, `hk-5m-rebuild-notes.md`, `3d-viewer-original-readme.md`. |

## Quick start
- **See the island in 3D:** open `3d-viewer/index.html`, try the data-source dropdown.

## Data sources
- **HK 5 m DTM** — Lands Department / CSDI, 2020 LiDAR, via DATA.GOV.HK
  (`Whole_HK_DTM_5m.zip`). HK1980 grid (EPSG:2326), ±5 m. *Lantau Peak 933 m (true ≈934).*
- **SRTM ~30 m** — AWS Open Data “Terrain Tiles” (Mapzen/Tilezen Terrarium).
  *Lantau Peak ~897 m (~4% low).*

All artwork is derived purely from these DEMs (no reference-map tracing). Built by Claude (Cowork).


## Note on B200K
The 1:200 000 map (B200K) was **not used** — it's a coarser version of the same product; the 1:50 000 (B50K) supersedes it for our skins.
