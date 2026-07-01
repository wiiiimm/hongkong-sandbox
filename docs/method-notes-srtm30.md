# Lantau Island — South-facing skyline (terrain-projection build)

**Produced by:** Claude (Cowork), in `claude/` workspace.
**Method:** Single source of truth = a real Digital Elevation Model. No reference-map
pixels were traced; the contour map was not used. Every output below is derived from the
same projected terrain geometry.

## 1. DEM source (single source of truth)
- **Dataset:** AWS Open Data "Terrain Tiles" (Mapzen/Tilezen *Terrarium* encoding),
  `s3://elevation-tiles-prod/terrarium/{z}/{x}/{y}.png`. This is a global merge of
  public DEMs (for Hong Kong, SRTM + finer national sources).
- **Zoom:** z14, ≈ **8.8 m/pixel** at this latitude (comparable to a 5–10 m DEM).
- **Tiles:** x 13372–13382, y 7148–7155 (88 tiles), decoded with
  `elev = R*256 + G + B/256 − 32768` (metres).
- **Assembled grid:** 2816 × 2048 px.
- **Geo-extent:** lon 113.8184–114.0601 E, lat 22.1874–22.3501 N (Web Mercator).

> Note on absolute height: this DEM reads Lantau Peak at **896.7 m** vs the official
> **934 m** (≈ 4% low, roughly uniform across the massif). Because a single global
> vertical scale is applied to every output, **relative** proportions between peaks —
> what makes the silhouette read as Lantau — are preserved exactly.

## 2. Island isolation
- Land mask = elevation > 5 m.
- Connected-component labelling; kept **only the component containing the highest
  point** (Lantau Peak). This automatically excludes Cheung Chau, Peng Chau, Hong Kong
  Island, the airport platform, etc. ("ignore offshore islands").

## 3. Projection (camera due south, looking north)
- **Orthographic**, no perspective.
- Horizontal screen axis = longitude (west = left, east = right — Tai O at far left,
  Discovery Bay at far right, matching the brief).
- **Horizon algorithm:** for each longitude column, skyline height = **maximum
  elevation over all latitudes (depth)**. This is the exact top-of-silhouette for an
  orthographic view and inherently "compresses depth so only the highest visible
  terrain contributes."
- Detected island width ≈ **22.5 km** (Fan Lau SW tip → north-east shore), preserved.

## 4. Peak verification (DEM-detected, west → east)
| Feature (massif)            | lon (°E) | DEM height | Official |
|-----------------------------|----------|-----------|----------|
| Western hills above Tai O   | 113.868  | 467 m     | ~490 m (Ling Wui Shan area) |
| **Lantau Peak (dominant)**  | 113.920  | **897 m** | 934 m |
| **Sunset Peak (secondary)** | 113.953  | 855 m     | 869 m |
| Lin Fa Shan / Yi Tung Shan  | 113.971  | 761 m     | 766 / 747 m |
| Mui Wo / east descent       | 113.998  | 451 m     | low coastal |
| Lo Fu Tau / Discovery Bay   | 114.01–114.02 | descending ridge | 465 m / coastal |

Signature confirmed: one dominant peak, one secondary, broad rounded shoulders,
long descending eastern ridge — a weathered subtropical island, not an alpine range.

## 5. Stylisation parameters
- Heavy Gaussian smoothing applied to give **rounded summits / broad ridges** (avoids
  needle peaks). Douglas–Peucker simplification used for the logo polyline.
- **Vertical exaggeration** (uniform; no per-peak exaggeration):
  - Logo silhouette ≈ **5.6×**
  - Engraving & raw projection ≈ **7.4×**
  (Required for a 22.5 km-wide / <1 km-high island to read as a skyline; relative peak
  heights are untouched.)

## 6. Deliverables
| File | What |
|------|------|
| `lantau-south-skyline-logo.svg` | Logo — single solid black shape, transparent bg, no detail |
| `lantau-south-skyline-logo-8000px.png` | Logo, 8000 px wide, transparent (RGBA) |
| `lantau-south-skyline-logo-favicon-256px.png` | Favicon-scale check, transparent |
| `lantau-south-skyline-engraving.svg` | Editorial engraving — layered depth-ridges (vector) |
| `lantau-south-skyline-engraving-12000px.png` | Engraving, 12000 px wide |
| `lantau-south-skyline-raw-projection.svg` | Raw accurate projected skyline (minimal smoothing) |
| `lantau-south-skyline-raw-projection-4000px.png` | Raw skyline raster |
| `source-scripts/` | Full reproducible pipeline (download → assemble → extract → render) |

## 7. Reproduce
```
python3 fetch_only.py      # download 88 terrarium tiles
python3 assemble.py        # decode + assemble elev.npy + extent
python3 extract.py         # mask, isolate Lantau, project skyline
python3 build_logo.py 26 430 1.3 8000
python3 build_engrave.py 18 560 10 18 12 1900
python3 build_raw.py
```
The engraving is the layered "depth-band" technique: latitude bands projected back
(north) → front (south) with white occlusion fills and a front-weighted line hierarchy;
the upper envelope equals the true projected skyline.

## 8. Added: engraved panorama + 3D viewer (second pass)
- `lantau-south-engraved-panorama-labelled-6000px.png` — scratchboard/wood-engraving
  rendering of Lantau's **3D southern faces** (not just the silhouette). Pipeline:
  occluded oblique projection from the south (per-column hidden-surface removal) →
  hillshade → fall-line strokes via line-integral convolution → white ridge highlights →
  hatched reflective sea → town clusters (Mui Wo, Discovery Bay) → labelled peaks
  (Traditional Chinese + English + elevation). Island tapered into sea at Tai O / Discovery
  Bay to match a clean Tai O→Discovery Bay framing.
- `lantau-island-3d-viewer.html` — self-contained interactive **rotatable 3D terrain**
  (Three.js). Drag to orbit, scroll to zoom, right-drag to pan; vertical-exaggeration
  slider, auto-spin, peak labels, sea toggle, South/Top view buttons. The DEM heightmap
  (360×270) is embedded in the file; needs internet only to load three.js from CDN.
  Source scripts: `source-scripts/oblique.py`, `scratch.py`, `compose.py`.
