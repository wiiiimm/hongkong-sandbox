# Hong Kong & Lantau — Interactive 3D Terrain Viewer

Open **`index.html`**. One self-contained file (~7.9 MB) with a **4-way View dropdown**:

| View | Extent | Mesh | Skin |
|------|--------|------|------|
| Lantau — 5 m LiDAR | island | 560×362 (36 m) | Lantau B50K |
| Lantau — SRTM ~30 m | island | 360×270 (62 m) | Lantau B50K |
| Hong Kong — 5 m LiDAR | whole territory | 910×685 (70 m) | HK B50K |
| Hong Kong — SRTM ~30 m | whole territory | 910×685 (70 m) | HK B50K |

Switching the View swaps the terrain mesh, the peak labels, the B50K topographic skin
(each region has its own georeferenced texture + overlay) and a sensible default vertical
exaggeration (2.6× island / 4.5× territory). **Surface** dropdown = shaded relief or the
draped B50K map; **Contours+trails** = vector overlay. Drag/scroll/right-drag to navigate.

Built by `scripts/make_combined.py` (template `scripts/template_combined.html`) from the
data in `data/` (lantau-* and hk-* heightmaps, B50K textures, overlays, georefs).
The per-region pipelines live in `scripts/` (fetch_dem/assemble_dem/build_heightmap_srtm,
extract_b50k/render_skin for Lantau; hk_dtm/hk_srtm/hk_build/render_hk_skin/hk_overlay for HK).

---

## NEW: B50K topographic skin (Lands Dept 1:50 000)
The viewer now also drapes the official **B50K topographic map** over the terrain:
- **Surface** dropdown → *Shaded relief* or *Topographic map (B50K)* — contours (50 m), coastline,
  streams, roads, trails and place names (English + Chinese) rendered as a texture wrapped on the 3D surface.
- **Trails+contours** checkbox → toggles a crisp **vector overlay** of index contours, coastline and
  hiking trails drawn directly on the terrain.

Both are derived from the B50K GML (EPSG:2326), clipped to the island and georeferenced to the mesh
(`data/lantau-b50k-topo-texture.png`, `data/lantau-b50k-overlay.json`, `data/lantau-georefs.json`).
Build scripts: `scripts/extract_b50k.py` → `scripts/render_skin.py` → `scripts/make_viewer_skin.py`.
