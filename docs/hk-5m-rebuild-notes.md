# Lantau outputs — rebuilt on the HK Lands Department 5 m LiDAR DTM

This folder re-creates the Lantau skyline logo, the engraved panorama, and the
interactive 3D viewer from the **official Hong Kong 5 m terrain model** instead of the
~30 m SRTM/Terrarium tiles used in the sibling `lantau-skyline/` and `lantau-3d-viewer/`
folders. Same techniques, much sharper and geometrically truer terrain.

## Data source
- **Dataset:** Digital Terrain Model (DTM), 5 m grid — Lands Department / CSDI, via
  DATA.GOV.HK. Single file `Whole_HK_DTM_5m.zip` (28.7 MB) →
  `Whole_HK_DTM_5m.asc` (ESRI ASCII grid, 12751 × 9601, 5 m cells).
  Download: `https://www.landsd.gov.hk/landsd_psi_data/SMO/data/Whole_HK_DTM_5m.zip`
- **CRS:** HK1980 Grid (EPSG:2326), metric — so eastings/northings are already in
  metres (no reprojection needed for the geometry; `pyproj` is used only to place the
  eight labels).
- **Accuracy:** ±5 m, derived from the 2020 territory-wide LiDAR survey.

## Why it's better than the SRTM build
| | SRTM/Terrarium (~30 m) | **HK 5 m DTM** |
|---|---|---|
| Lantau Peak height | 897 m (≈4% low) | **933 m** (true ≈934 m) |
| Summit positions | ~1 km offset on some peaks | on the real summits |
| Ridge/spur detail | soft | crisp LiDAR detail |
| Lo Fu Tau, Lin Fa Shan | mislocated/low | correct height & position |

The peak labels were re-pinned to the DEM's actual summits after we found the textbook
lat/long for several peaks were imprecise (e.g. the 749 m bump west of Lantau Peak is
**Nei Lak Shan**, not Lantau Peak).

## Deliverables
| File | What |
|------|------|
| `lantau-island-3d-viewer-5m.html` | Rotatable 3D terrain (Three.js), 560×362 heightmap @ ~36 m, true heights. Open in a browser; drag/scroll/right-drag. |
| `lantau-south-engraved-panorama-5m-labelled-5000px.png` | Scratchboard engraving of the 3D southern faces, labelled peaks (TC + EN + elevation), sea + town clusters. 5000 px wide. |
| `lantau-skyline-logo-5m.svg` / `…-8000px.png` | Single-shape skyline silhouette logo (transparent). |
| `scripts/` | The 5 m pipeline (see below). |

(Files beginning `_` or `c5_`/`oblique5m_`/`logo5m_prev` are working previews — ignore.)

## Pipeline (scripts/)
1. `extract_lantau.py` — read the 302 MB ASC header, slice only the Lantau window
   (HK1980 E 801000–821800, N 805500–819500) → `lantau5m.npy` (+ `extent`-style meta).
2. `build5m.py` — isolate the Lantau connected component (keep the one containing the
   summit), save `l5_elev.npy` + `l5_mask.npy`, and map the labelled features to grid
   columns with `pyproj`.
3. `oblique5m.py` — occluded oblique projection from the south (per-column hidden-surface
   removal) at 5 m, with east/west taper into the sea → `oblique_tone/E/meta`.
4. `compose5m.py` — scratchboard engraving (fall-line LIC strokes, ridge highlights),
   hatched sea, town clusters, labels → the panorama PNG.  Usage: `python3 compose5m.py 5000`.
5. `build_hm5.py` — downsample to a 560-wide heightmap JSON for the web viewer.
6. `logo5m.py` — smoothed + Douglas–Peucker silhouette → logo SVG/PNG.

Requires: numpy, scipy, pillow, pyproj, cairosvg. Rendering >5000 px wide needs more
RAM/time than the sandbox allowed; 5000 px is the delivered size.

## Provenance / licence
HK DTM is open data under the DATA.GOV.HK Terms & Conditions (free re-use, attribution to
the Lands Department / CSDI). Three.js is MIT. Built by Claude (Cowork).
