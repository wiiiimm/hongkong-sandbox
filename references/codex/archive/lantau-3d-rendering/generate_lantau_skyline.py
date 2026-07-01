#!/usr/bin/env python3
"""
Generate a south-facing Lantau skyline from public Terrarium DEM tiles.

Outputs are written beside this script. The DEM-derived skyline is computed as
the maximum land elevation for each west-east column inside an approximate
Lantau island mask, viewed from due south with orthographic projection.
"""

from __future__ import annotations

import csv
import io
import json
import math
import os
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


OUT = Path(__file__).resolve().parent
TILE_DIR = OUT / "dem_tiles"
ZOOM = 13
TILE_SIZE = 256

# Tight working extent around Lantau. The island mask below removes sea,
# Chek Lap Kok, and nearby smaller islands from the skyline computation.
BBOX = {
    "west": 113.825,
    "south": 22.185,
    "east": 114.055,
    "north": 22.325,
}

# Approximate Lantau coastline polygon in lon/lat, clockwise from Tai O.
# This is used only as the land mask; the elevation source supplies heights.
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

LANDMARKS = [
    {"name": "Tai O", "lon": 113.862, "expected_m": 0},
    {"name": "Lantau Peak", "lon": 113.921, "expected_m": 934},
    {"name": "Sunset Peak", "lon": 113.958, "expected_m": 869},
    {"name": "Yi Tung Shan", "lon": 113.974, "expected_m": 747},
    {"name": "Lin Fa Shan", "lon": 113.995, "expected_m": 766},
    {"name": "Mui Wo", "lon": 114.002, "expected_m": 0},
    {"name": "Lo Fu Tau", "lon": 114.021, "expected_m": 465},
    {"name": "Discovery Bay", "lon": 114.016, "expected_m": 0},
]


@dataclass
class Skyline:
    lon: np.ndarray
    elevation_m: np.ndarray
    x_m: np.ndarray


def lon_to_tile_x(lon: float, z: int) -> int:
    return int((lon + 180.0) / 360.0 * (2**z))


def lat_to_tile_y(lat: float, z: int) -> int:
    lat_rad = math.radians(lat)
    return int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * (2**z))


def tile_x_to_lon(x: float, z: int) -> float:
    return x / (2**z) * 360.0 - 180.0


def tile_y_to_lat(y: float, z: int) -> float:
    n = math.pi - 2.0 * math.pi * y / (2**z)
    return math.degrees(math.atan(math.sinh(n)))


def fetch_tile(z: int, x: int, y: int) -> Image.Image:
    TILE_DIR.mkdir(exist_ok=True)
    path = TILE_DIR / f"{z}-{x}-{y}.png"
    if not path.exists():
        url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
        with urllib.request.urlopen(url, timeout=30) as response:
            path.write_bytes(response.read())
    return Image.open(path).convert("RGB")


def terrarium_to_elevation_m(rgb: np.ndarray) -> np.ndarray:
    r = rgb[:, :, 0].astype(np.float32)
    g = rgb[:, :, 1].astype(np.float32)
    b = rgb[:, :, 2].astype(np.float32)
    return (r * 256.0 + g + b / 256.0) - 32768.0


def point_in_polygon(x: float, y: float, polygon: list[tuple[float, float]]) -> bool:
    inside = False
    j = len(polygon) - 1
    for i, (xi, yi) in enumerate(polygon):
        xj, yj = polygon[j]
        intersects = (yi > y) != (yj > y)
        if intersects:
            x_cross = (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
            if x < x_cross:
                inside = not inside
        j = i
    return inside


def rdp(points: list[tuple[float, float]], epsilon: float) -> list[tuple[float, float]]:
    if len(points) < 3:
        return points
    start = np.array(points[0], dtype=float)
    end = np.array(points[-1], dtype=float)
    line = end - start
    length = np.linalg.norm(line)
    if length == 0:
        distances = [np.linalg.norm(np.array(p) - start) for p in points]
    else:
        distances = [
            abs(
                line[0] * (start[1] - p[1])
                - line[1] * (start[0] - p[0])
            )
            / length
            for p in points
        ]
    index = int(np.argmax(distances))
    max_distance = distances[index]
    if max_distance > epsilon:
        return rdp(points[: index + 1], epsilon)[:-1] + rdp(points[index:], epsilon)
    return [points[0], points[-1]]


def smooth(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return values.copy()
    kernel = np.hanning(window)
    kernel = kernel / kernel.sum()
    padded = np.pad(values, (window // 2, window // 2), mode="edge")
    return np.convolve(padded, kernel, mode="valid")[: len(values)]


def resmooth_skyline(skyline: Skyline, window: int) -> Skyline:
    return Skyline(
        lon=skyline.lon,
        elevation_m=smooth(skyline.elevation_m, window),
        x_m=skyline.x_m,
    )


def build_dem_mosaic() -> tuple[np.ndarray, dict[str, float]]:
    x0 = lon_to_tile_x(BBOX["west"], ZOOM)
    x1 = lon_to_tile_x(BBOX["east"], ZOOM)
    y0 = lat_to_tile_y(BBOX["north"], ZOOM)
    y1 = lat_to_tile_y(BBOX["south"], ZOOM)
    rows = []
    for ty in range(y0, y1 + 1):
        row_tiles = []
        for tx in range(x0, x1 + 1):
            row_tiles.append(np.asarray(fetch_tile(ZOOM, tx, ty)))
        rows.append(np.concatenate(row_tiles, axis=1))
    rgb = np.concatenate(rows, axis=0)
    elevation = terrarium_to_elevation_m(rgb)
    extent = {
        "west": tile_x_to_lon(x0, ZOOM),
        "east": tile_x_to_lon(x1 + 1, ZOOM),
        "north": tile_y_to_lat(y0, ZOOM),
        "south": tile_y_to_lat(y1 + 1, ZOOM),
    }
    return elevation, extent


def extract_skyline(elevation: np.ndarray, extent: dict[str, float]) -> Skyline:
    height, width = elevation.shape
    lon_values = np.linspace(extent["west"], extent["east"], width)
    lat_values = np.linspace(extent["north"], extent["south"], height)
    skyline = np.zeros(width, dtype=np.float32)
    for xi, lon in enumerate(lon_values):
        max_elevation = 0.0
        for yi, lat in enumerate(lat_values):
            if point_in_polygon(float(lon), float(lat), LANTAU_POLYGON):
                max_elevation = max(max_elevation, float(elevation[yi, xi]))
        skyline[xi] = max(0.0, max_elevation)

    west_idx = np.searchsorted(lon_values, BBOX["west"])
    east_idx = np.searchsorted(lon_values, BBOX["east"])
    lon = lon_values[west_idx:east_idx]
    elev = skyline[west_idx:east_idx]
    elev = smooth(elev, 77)
    mean_lat = (BBOX["south"] + BBOX["north"]) / 2.0
    metres_per_degree_lon = 111_320.0 * math.cos(math.radians(mean_lat))
    x_m = (lon - lon[0]) * metres_per_degree_lon
    return Skyline(lon=lon, elevation_m=elev, x_m=x_m)


def normalised_points(
    skyline: Skyline,
    width_px: int,
    height_px: int,
    top_margin: int,
    bottom_margin: int,
    simplify_epsilon_px: float | None = None,
) -> list[tuple[float, float]]:
    x = (skyline.x_m - skyline.x_m.min()) / (skyline.x_m.max() - skyline.x_m.min()) * width_px
    usable_h = height_px - top_margin - bottom_margin
    y = height_px - bottom_margin - (skyline.elevation_m / skyline.elevation_m.max()) * usable_h
    points = list(zip(x.tolist(), y.tolist()))
    if simplify_epsilon_px is not None:
        points = rdp(points, simplify_epsilon_px)
    return points


def svg_path(points: list[tuple[float, float]]) -> str:
    if not points:
        return ""
    first = points[0]
    parts = [f"M {first[0]:.2f} {first[1]:.2f}"]
    parts.extend(f"L {x:.2f} {y:.2f}" for x, y in points[1:])
    return " ".join(parts)


def svg_smooth_path(points: list[tuple[float, float]]) -> str:
    if not points:
        return ""
    if len(points) < 3:
        return svg_path(points)
    parts = [f"M {points[0][0]:.2f} {points[0][1]:.2f}"]
    for i in range(1, len(points) - 1):
        x_mid = (points[i][0] + points[i + 1][0]) / 2.0
        y_mid = (points[i][1] + points[i + 1][1]) / 2.0
        parts.append(f"Q {points[i][0]:.2f} {points[i][1]:.2f} {x_mid:.2f} {y_mid:.2f}")
    parts.append(f"T {points[-1][0]:.2f} {points[-1][1]:.2f}")
    return " ".join(parts)


def write_logo_svg(skyline: Skyline) -> None:
    width, height = 8000, 2400
    baseline = height - 240
    skyline = resmooth_skyline(skyline, 91)
    points = normalised_points(skyline, width, height, 300, 240, simplify_epsilon_px=42)
    # Preserve named peak positions by reinserting nearest raw points after simplification.
    raw_points = normalised_points(skyline, width, height, 300, 240, simplify_epsilon_px=None)
    for landmark in LANDMARKS:
        idx = int(np.argmin(np.abs(skyline.lon - landmark["lon"])))
        points.append(raw_points[idx])
    points = sorted(points, key=lambda p: p[0])
    path = svg_smooth_path(points) + f" L {width:.2f} {baseline:.2f} L 0.00 {baseline:.2f} Z"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <path d="{path}" fill="#000"/>
</svg>
'''
    (OUT / "lantau-logo-silhouette.svg").write_text(svg, encoding="utf-8")


def write_raw_svg(skyline: Skyline) -> None:
    width, height = 8000, 2200
    points = normalised_points(skyline, width, height, 180, 220, simplify_epsilon_px=10)
    path = svg_smooth_path(points)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <path d="{path}" fill="none" stroke="#000" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
'''
    (OUT / "lantau-raw-projected-skyline.svg").write_text(svg, encoding="utf-8")


def write_engraving_svg(skyline: Skyline) -> None:
    width, height = 12000, 7000
    skyline = resmooth_skyline(skyline, 71)
    points = normalised_points(skyline, width, height, 1050, 2050, simplify_epsilon_px=16)
    top_path = svg_smooth_path(points)
    line_paths = []
    for i, offset in enumerate(range(260, 1650, 210)):
        ratio = i / 7.0
        lower = []
        for x, y in points:
            centre_pull = abs((x / width) - 0.5) * 2.0
            sag = offset + 60 * math.sin((x / width) * math.pi) * (1.0 - ratio * 0.25)
            yy = y + sag + centre_pull * 45
            if 180 < x < width - 180 and yy < height - 820:
                lower.append((x, yy))
        if len(lower) > 4:
            line_paths.append(svg_smooth_path(lower))

    strokes = "\n".join(
        f'  <path d="{p}" fill="none" stroke="#000" stroke-width="{max(5, 10 - i * 0.4):.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="{max(0.28, 0.72 - i * 0.04):.2f}"/>'
        for i, p in enumerate(line_paths)
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#fff"/>
  <path d="{top_path}" fill="none" stroke="#000" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/>
{strokes}
</svg>
'''
    (OUT / "lantau-engraved-illustration.svg").write_text(svg, encoding="utf-8")


def render_png_from_svg_geometry(skyline: Skyline) -> None:
    # Logo PNG with transparent background.
    logo_w, logo_h = 8000, 2400
    logo_skyline = resmooth_skyline(skyline, 91)
    logo = Image.new("RGBA", (logo_w, logo_h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(logo)
    logo_points = normalised_points(logo_skyline, logo_w, logo_h, 300, 240, simplify_epsilon_px=None)
    polygon = logo_points + [(logo_w, logo_h - 240), (0, logo_h - 240)]
    draw.polygon([(round(x), round(y)) for x, y in polygon], fill=(0, 0, 0, 255))
    logo.save(OUT / "lantau-logo-silhouette-8000.png")

    # Engraving PNG with white background.
    engrave_w, engrave_h = 12000, 7000
    engrave_skyline = resmooth_skyline(skyline, 71)
    img = Image.new("RGB", (engrave_w, engrave_h), "white")
    draw = ImageDraw.Draw(img)
    points = normalised_points(engrave_skyline, engrave_w, engrave_h, 1050, 2050, simplify_epsilon_px=None)
    draw.line([(round(x), round(y)) for x, y in points], fill="black", width=24, joint="curve")
    for i, offset in enumerate(range(260, 1650, 210)):
        ratio = i / 7.0
        line = []
        for x, y in points:
            centre_pull = abs((x / engrave_w) - 0.5) * 2.0
            yy = y + offset + 60 * math.sin((x / engrave_w) * math.pi) * (1.0 - ratio * 0.25) + centre_pull * 45
            if 180 < x < engrave_w - 180 and yy < engrave_h - 820:
                line.append((round(x), round(yy)))
        if len(line) > 4:
            draw.line(line, fill=(0, 0, 0), width=max(4, int(10 - i * 0.5)), joint="curve")
    img.save(OUT / "lantau-engraved-illustration-12000.png")


def write_data_and_notes(skyline: Skyline, extent: dict[str, float]) -> None:
    with (OUT / "lantau-projected-skyline.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["lon", "x_m_from_west", "skyline_elevation_m"])
        for lon, x_m, elev in zip(skyline.lon, skyline.x_m, skyline.elevation_m):
            writer.writerow([f"{lon:.8f}", f"{x_m:.3f}", f"{elev:.3f}"])

    checks = []
    for landmark in LANDMARKS:
        idx = int(np.argmin(np.abs(skyline.lon - landmark["lon"])))
        checks.append(
            {
                "name": landmark["name"],
                "lon": landmark["lon"],
                "expected_elevation_m": landmark["expected_m"],
                "projected_skyline_elevation_m_at_lon": round(float(skyline.elevation_m[idx]), 1),
            }
        )
    metadata = {
        "agent": "Codex",
        "projection": "South-facing orthographic skyline; camera offshore south, looking north.",
        "terrain_source": "AWS public elevation-tiles-prod Terrarium tiles, zoom 13.",
        "terrain_tile_url_template": "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png",
        "bbox_lon_lat": BBOX,
        "dem_tile_extent_lon_lat": extent,
        "island_mask": "Approximate Lantau coastline polygon embedded in generate_lantau_skyline.py.",
        "method": [
            "Decode Terrarium DEM tiles to metres.",
            "Mask points outside approximate Lantau island polygon.",
            "For each west-east column, take maximum elevation over north-south depth.",
            "Smooth and simplify exported artwork paths using Douglas-Peucker while keeping the raw skyline CSV in metres.",
        ],
        "vertical_export_note": "CSV retains DEM elevations in metres. SVG/PNG exports normalise vertical height for graphic legibility while preserving relative terrain geometry.",
        "landmark_checks": checks,
        "outputs": [
            "lantau-projected-skyline.csv",
            "lantau-raw-projected-skyline.svg",
            "lantau-logo-silhouette.svg",
            "lantau-logo-silhouette-8000.png",
            "lantau-engraved-illustration.svg",
            "lantau-engraved-illustration-12000.png",
        ],
    }
    (OUT / "lantau-skyline-generation-notes.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main() -> None:
    elevation, extent = build_dem_mosaic()
    skyline = extract_skyline(elevation, extent)
    write_data_and_notes(skyline, extent)
    write_raw_svg(skyline)
    write_logo_svg(skyline)
    write_engraving_svg(skyline)
    render_png_from_svg_geometry(skyline)


if __name__ == "__main__":
    main()
