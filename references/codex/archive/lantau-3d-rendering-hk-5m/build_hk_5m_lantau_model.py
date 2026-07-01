#!/usr/bin/env python3
"""
Build an enhanced Lantau 3D model from the Hong Kong Lands Department 5 m DTM.

Input:
  data/Whole_HK_DTM_5m.zip containing Whole_HK_DTM_5m.asc

Outputs:
  output/lantau-hk-5m-terrain-mesh.json
  output/lantau-hk-5m-terrain.obj
  output/lantau-hk-5m-3d-viewer.html
"""

from __future__ import annotations

import json
import math
import shutil
import zipfile
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
ZIP_PATH = DATA / "Whole_HK_DTM_5m.zip"
ASC_NAME = "Whole_HK_DTM_5m.asc"

# CSDI metadata geographic extent for the LandsD DTM.
HK_BBOX = {
    "west": 113.815,
    "south": 22.135,
    "east": 114.5,
    "north": 22.565,
}

# Lantau working extent. Kept close to the previous model for comparison.
LANTAU_BBOX = {
    "west": 113.825,
    "south": 22.185,
    "east": 114.055,
    "north": 22.325,
}

LANTAU_POLYGON = [
    (113.835, 22.255),
    (113.842, 22.235),
    (113.850, 22.214),
    (113.862, 22.194),
    (113.889, 22.198),
    (113.918, 22.210),
    (113.946, 22.220),
    (113.982, 22.229),
    (114.017, 22.232),
    (114.047, 22.251),
    (114.035, 22.275),
    (114.021, 22.301),
    (113.995, 22.312),
    (113.964, 22.307),
    (113.938, 22.303),
    (113.915, 22.290),
    (113.892, 22.282),
    (113.866, 22.276),
    (113.846, 22.266),
]

GRID_X = 360
GRID_Z = 220
VERTICAL_EXAGGERATION = 1.7


def point_in_polygon(x: float, y: float, polygon: list[tuple[float, float]]) -> bool:
    inside = False
    j = len(polygon) - 1
    for i, (xi, yi) in enumerate(polygon):
        xj, yj = polygon[j]
        if (yi > y) != (yj > y):
            x_cross = (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
            if x < x_cross:
                inside = not inside
        j = i
    return inside


def read_header() -> dict[str, float]:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Missing {ZIP_PATH}. Download it from data.gov.hk first.")
    with zipfile.ZipFile(ZIP_PATH) as archive:
        with archive.open(ASC_NAME) as f:
            header = {}
            for _ in range(6):
                key, value = f.readline().decode("ascii").split()[:2]
                header[key.lower()] = float(value)
    return header


def lon_to_col(lon: float, header: dict[str, float]) -> int:
    x_min = header["xllcorner"]
    x_max = x_min + header["ncols"] * header["cellsize"]
    x = x_min + (lon - HK_BBOX["west"]) / (HK_BBOX["east"] - HK_BBOX["west"]) * (x_max - x_min)
    return int((x - x_min) / header["cellsize"])


def lat_to_row(lat: float, header: dict[str, float]) -> int:
    y_min = header["yllcorner"]
    y_max = y_min + header["nrows"] * header["cellsize"]
    y = y_min + (lat - HK_BBOX["south"]) / (HK_BBOX["north"] - HK_BBOX["south"]) * (y_max - y_min)
    return int((y_max - y) / header["cellsize"])


def col_to_lon(col: float, header: dict[str, float]) -> float:
    return HK_BBOX["west"] + (col / header["ncols"]) * (HK_BBOX["east"] - HK_BBOX["west"])


def row_to_lat(row: float, header: dict[str, float]) -> float:
    return HK_BBOX["north"] - (row / header["nrows"]) * (HK_BBOX["north"] - HK_BBOX["south"])


def load_lantau_crop(header: dict[str, float]) -> tuple[np.ndarray, dict[str, int]]:
    col0 = max(0, lon_to_col(LANTAU_BBOX["west"], header) - 16)
    col1 = min(int(header["ncols"]) - 1, lon_to_col(LANTAU_BBOX["east"], header) + 16)
    row0 = max(0, lat_to_row(LANTAU_BBOX["north"], header) - 16)
    row1 = min(int(header["nrows"]) - 1, lat_to_row(LANTAU_BBOX["south"], header) + 16)
    wanted_rows = row1 - row0 + 1
    wanted_cols = col1 - col0 + 1
    crop = np.zeros((wanted_rows, wanted_cols), dtype=np.float32)

    with zipfile.ZipFile(ZIP_PATH) as archive:
        with archive.open(ASC_NAME) as f:
            for _ in range(6):
                f.readline()
            for row in range(int(header["nrows"])):
                line = f.readline()
                if row < row0:
                    continue
                if row > row1:
                    break
                values = np.fromstring(line.decode("ascii"), sep=" ", dtype=np.float32)
                crop[row - row0, :] = values[col0 : col1 + 1]

    crop[crop == header["nodata_value"]] = 0
    crop[crop < 0] = 0
    return crop, {"row0": row0, "row1": row1, "col0": col0, "col1": col1}


def bilinear(crop: np.ndarray, x: float, y: float) -> float:
    h, w = crop.shape
    if x < 0 or y < 0 or x >= w - 1 or y >= h - 1:
        return 0.0
    x0 = int(math.floor(x))
    y0 = int(math.floor(y))
    dx = x - x0
    dy = y - y0
    a = crop[y0, x0]
    b = crop[y0, x0 + 1]
    c = crop[y0 + 1, x0]
    d = crop[y0 + 1, x0 + 1]
    return float((a * (1 - dx) + b * dx) * (1 - dy) + (c * (1 - dx) + d * dx) * dy)


def build_mesh(header: dict[str, float], crop: np.ndarray, window: dict[str, int]) -> dict[str, object]:
    lon_values = np.linspace(LANTAU_BBOX["west"], LANTAU_BBOX["east"], GRID_X)
    lat_values = np.linspace(LANTAU_BBOX["south"], LANTAU_BBOX["north"], GRID_Z)
    mean_lat = (LANTAU_BBOX["south"] + LANTAU_BBOX["north"]) / 2.0
    metres_per_degree_lon = 111_320.0 * math.cos(math.radians(mean_lat))
    metres_per_degree_lat = 110_540.0
    centre_lon = (LANTAU_BBOX["west"] + LANTAU_BBOX["east"]) / 2.0
    centre_lat = (LANTAU_BBOX["south"] + LANTAU_BBOX["north"]) / 2.0

    index_grid: list[list[int | None]] = []
    vertices: list[float] = []
    heights: list[float] = []
    lon_lat: list[list[float]] = []

    for lat in lat_values:
        row: list[int | None] = []
        for lon in lon_values:
            if point_in_polygon(float(lon), float(lat), LANTAU_POLYGON):
                global_col = lon_to_col(float(lon), header)
                global_row = lat_to_row(float(lat), header)
                elev = bilinear(crop, global_col - window["col0"], global_row - window["row0"])
                x = (lon - centre_lon) * metres_per_degree_lon
                z = -(lat - centre_lat) * metres_per_degree_lat
                y = elev * VERTICAL_EXAGGERATION
                row.append(len(heights))
                vertices.extend([round(x, 3), round(y, 3), round(z, 3)])
                heights.append(round(elev, 3))
                lon_lat.append([round(float(lon), 7), round(float(lat), 7)])
            else:
                row.append(None)
        index_grid.append(row)

    indices: list[int] = []
    for zi in range(GRID_Z - 1):
        for xi in range(GRID_X - 1):
            a = index_grid[zi][xi]
            b = index_grid[zi][xi + 1]
            c = index_grid[zi + 1][xi]
            d = index_grid[zi + 1][xi + 1]
            if a is not None and b is not None and c is not None and d is not None:
                indices.extend([a, c, b, b, c, d])

    x_vals = vertices[0::3]
    y_vals = vertices[1::3]
    z_vals = vertices[2::3]
    metadata = {
        "agent": "Codex",
        "terrain_source": "Hong Kong Lands Department 5 m Digital Terrain Model from data.gov.hk",
        "source_url": "https://data.gov.hk/en-data/dataset/hk-landsd-openmap-5m-grid-dtm/resource/620c4f4f-eac4-472f-9074-dffa2ad596fd",
        "download_url": "https://www.landsd.gov.hk/landsd_psi_data/SMO/data/Whole_HK_DTM_5m.zip",
        "format": "ESRI ASCII grid in ZIP",
        "source_grid": {
            "ncols": int(header["ncols"]),
            "nrows": int(header["nrows"]),
            "cellsize_m": header["cellsize"],
            "xllcorner": header["xllcorner"],
            "yllcorner": header["yllcorner"],
        },
        "crop_window": window,
        "coordinate_note": "The ASC grid is sampled through a metadata-bbox affine mapping because GDAL/pyproj are not available in this runtime.",
        "vertical_exaggeration": VERTICAL_EXAGGERATION,
        "grid": {"x_samples": GRID_X, "z_samples": GRID_Z},
        "vertex_count": len(heights),
        "triangle_count": len(indices) // 3,
        "bbox_lon_lat": LANTAU_BBOX,
        "bounds_m": {
            "x_min": min(x_vals),
            "x_max": max(x_vals),
            "y_min": min(y_vals),
            "y_max": max(y_vals),
            "z_min": min(z_vals),
            "z_max": max(z_vals),
        },
    }
    return {
        "metadata": metadata,
        "vertices": vertices,
        "indices": indices,
        "heights_m": heights,
        "lon_lat": lon_lat,
    }


def write_obj(mesh: dict[str, object]) -> None:
    vertices = mesh["vertices"]
    indices = mesh["indices"]
    assert isinstance(vertices, list)
    assert isinstance(indices, list)
    lines = [
        "# Lantau Island terrain mesh from HK LandsD 5 m DTM",
        "# Generated by build_hk_5m_lantau_model.py",
        f"# Vertical exaggeration: {VERTICAL_EXAGGERATION}",
    ]
    for i in range(0, len(vertices), 3):
        lines.append(f"v {vertices[i]} {vertices[i + 1]} {vertices[i + 2]}")
    for i in range(0, len(indices), 3):
        lines.append(f"f {indices[i] + 1} {indices[i + 1] + 1} {indices[i + 2] + 1}")
    (OUTPUT / "lantau-hk-5m-terrain.obj").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_viewer() -> None:
    html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Lantau Island 3D Terrain - HK 5 m DTM</title>
  <link rel="icon" href="data:,">
  <style>
    :root { color-scheme: light; --ink: #141414; --muted: #68645d; --paper: #f7f4ec; --panel: rgba(247,244,236,.88); }
    * { box-sizing: border-box; }
    html, body { width: 100%; height: 100%; margin: 0; overflow: hidden; background: var(--paper); color: var(--ink); font: 14px/1.4 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    #scene { position: fixed; inset: 0; width: 100vw; height: 100vh; display: block; }
    .toolbar { position: fixed; top: 16px; left: 16px; display: flex; gap: 8px; align-items: center; padding: 8px; background: var(--panel); border: 1px solid rgba(20,20,20,.14); backdrop-filter: blur(10px); }
    button { width: 38px; height: 34px; border: 1px solid rgba(20,20,20,.22); background: #fffdf7; color: var(--ink); cursor: pointer; display: grid; place-items: center; padding: 0; }
    button:hover { background: #eee8db; }
    .readout { min-width: 188px; color: var(--muted); font-size: 12px; padding: 0 4px; white-space: nowrap; }
    @media (max-width: 720px) { .toolbar { top: 10px; left: 10px; right: 10px; justify-content: center; } .readout { min-width: 0; font-size: 11px; } }
  </style>
</head>
<body>
  <canvas id="scene" aria-label="Rotatable 3D terrain model of Lantau Island from HK 5 m DTM"></canvas>
  <div class="toolbar" aria-label="3D view controls">
    <button id="reset" title="Reset view" aria-label="Reset view"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v6h6"/></svg></button>
    <button id="spin" title="Toggle rotation" aria-label="Toggle rotation"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 1l4 4-4 4"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><path d="M7 23l-4-4 4-4"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg></button>
    <div class="readout" id="readout">Loading HK 5 m terrain</div>
  </div>
  <script type="module">
    import * as THREE from './vendor/three.module.js';
    import { OrbitControls } from './vendor/OrbitControls.js';

    const canvas = document.querySelector('#scene');
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0xf7f4ec, 1);
    renderer.outputColorSpace = THREE.SRGBColorSpace;

    const scene = new THREE.Scene();
    scene.fog = new THREE.Fog(0xf7f4ec, 17000, 43000);
    const camera = new THREE.PerspectiveCamera(34, 1, 50, 65000);
    camera.position.set(0, 9800, 21800);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.minDistance = 8500;
    controls.maxDistance = 39000;
    controls.maxPolarAngle = Math.PI * 0.49;
    controls.target.set(0, 1050, 0);

    scene.add(new THREE.HemisphereLight(0xffffff, 0xb5aa98, 2.4));
    const sun = new THREE.DirectionalLight(0xffffff, 2.8);
    sun.position.set(-9000, 18000, 12000);
    scene.add(sun);

    const material = new THREE.MeshStandardMaterial({ color: 0x2f5b43, roughness: 0.92, metalness: 0, flatShading: false });
    const wireMaterial = new THREE.LineBasicMaterial({ color: 0xf1eadb, transparent: true, opacity: 0.14 });
    const response = await fetch('./lantau-hk-5m-terrain-mesh.json');
    const meshData = await response.json();
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(meshData.vertices, 3));
    geometry.setIndex(meshData.indices);
    geometry.computeVertexNormals();
    geometry.computeBoundingSphere();
    geometry.computeBoundingBox();

    const terrain = new THREE.Mesh(geometry, material);
    terrain.rotation.y = Math.PI;
    terrain.scale.setScalar(0.82);
    scene.add(terrain);
    const wire = new THREE.LineSegments(new THREE.WireframeGeometry(geometry), wireMaterial);
    wire.rotation.copy(terrain.rotation);
    wire.scale.copy(terrain.scale);
    scene.add(wire);

    const base = new THREE.Mesh(new THREE.CircleGeometry(12500, 96), new THREE.MeshBasicMaterial({ color: 0xe8e0d0, transparent: true, opacity: 0.55 }));
    base.rotation.x = -Math.PI / 2;
    base.position.y = -90;
    scene.add(base);

    const peak = Math.round(meshData.metadata.bounds_m.y_max / meshData.metadata.vertical_exaggeration);
    document.querySelector('#readout').textContent = `${meshData.metadata.vertex_count.toLocaleString()} vertices · HK 5 m DTM · peak ${peak} m`;

    let spinning = true;
    document.querySelector('#spin').addEventListener('click', () => { spinning = !spinning; });
    document.querySelector('#reset').addEventListener('click', () => { camera.position.set(0, 9800, 21800); controls.target.set(0, 1050, 0); controls.update(); });
    function resize() { renderer.setSize(window.innerWidth, window.innerHeight, false); camera.aspect = window.innerWidth / window.innerHeight; camera.updateProjectionMatrix(); }
    window.addEventListener('resize', resize);
    resize();
    function animate() { requestAnimationFrame(animate); if (spinning) { terrain.rotation.y += 0.0018; wire.rotation.y = terrain.rotation.y; } controls.update(); renderer.render(scene, camera); }
    animate();
  </script>
</body>
</html>
"""
    (OUTPUT / "lantau-hk-5m-3d-viewer.html").write_text(html, encoding="utf-8")


def copy_vendor() -> None:
    vendor_src = ROOT.parent / "lantau-3d-rendering" / "vendor"
    vendor_dst = OUTPUT / "vendor"
    if vendor_dst.exists():
        shutil.rmtree(vendor_dst)
    shutil.copytree(vendor_src, vendor_dst)


def main() -> None:
    OUTPUT.mkdir(exist_ok=True)
    header = read_header()
    crop, window = load_lantau_crop(header)
    mesh = build_mesh(header, crop, window)
    (OUTPUT / "lantau-hk-5m-terrain-mesh.json").write_text(json.dumps(mesh, separators=(",", ":")), encoding="utf-8")
    write_obj(mesh)
    write_viewer()
    copy_vendor()
    print(json.dumps(mesh["metadata"], indent=2))


if __name__ == "__main__":
    main()
