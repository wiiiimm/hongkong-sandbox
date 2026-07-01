#!/usr/bin/env python3
"""
Build whole-Hong-Kong 3D terrain meshes and B50K GML overlay skins.

Outputs are written into ../data:
- hong-kong-hk-landsd-5m/terrain-mesh.json
- hong-kong-hk-landsd-5m/terrain.obj
- hong-kong-aws-terrarium/terrain-mesh.json
- hk-b50k-gml/skin-lines.json
"""

from __future__ import annotations

import json
import math
import time
import urllib.request
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
HK_DTM_ZIP = DATA / "hk-landsd-5m" / "Whole_HK_DTM_5m.zip"
HK_ASC_NAME = "Whole_HK_DTM_5m.asc"
B50K_ZIP = DATA / "hk-b50k-gml" / "iB50000GML.zip"

HK_OUT = DATA / "hong-kong-hk-landsd-5m"
AWS_OUT = DATA / "hong-kong-aws-terrarium"
B50K_OUT = DATA / "hk-b50k-gml"
AWS_TILE_DIR = AWS_OUT / "dem_tiles"

MESH_PROFILES = [
    {"name": "standard", "grid_x": 430, "grid_z": 320, "aws_zoom": 12},
    {"name": "detail", "grid_x": 860, "grid_z": 640, "aws_zoom": 13},
]
VERTICAL_EXAGGERATION = 1.45
TILE_SIZE = 256

# CSDI metadata geographic extent for the LandsD DTM, used only to place
# AWS lon/lat terrain into the same Hong Kong 1980 Grid metre space.
HK_LON_LAT_BBOX = {
    "west": 113.815,
    "south": 22.135,
    "east": 114.5,
    "north": 22.565,
}

LANTAU_BBOX = {
    "west": 113.825,
    "south": 22.185,
    "east": 114.055,
    "north": 22.325,
}

B50K_LAYERS = {
    "transport": {
        "member": "TSPTLINE.gml",
        "epsilon_m": 35.0,
        "max_features": 2200,
        "colour": "#44382f",
    },
    "hydro": {
        "member": "HYDRLINE.gml",
        "epsilon_m": 45.0,
        "max_features": 1400,
        "colour": "#3f6f82",
    },
    "contours": {
        "member": "ELEVLINE.gml",
        "epsilon_m": 90.0,
        "max_features": 1600,
        "colour": "#8c6f49",
    },
    "boundaries": {
        "member": "BDRYLINE.gml",
        "epsilon_m": 60.0,
        "max_features": 500,
        "colour": "#6d5f55",
    },
    "terrain": {
        "member": "TERRLINE.gml",
        "epsilon_m": 50.0,
        "max_features": 700,
        "colour": "#6d7759",
    },
}


def read_hk_header() -> dict[str, float]:
    with zipfile.ZipFile(HK_DTM_ZIP) as archive:
        with archive.open(HK_ASC_NAME) as f:
            header: dict[str, float] = {}
            for _ in range(6):
                key, value = f.readline().decode("ascii").split()[:2]
                header[key.lower()] = float(value)
    header["xmax"] = header["xllcorner"] + header["ncols"] * header["cellsize"]
    header["ymax"] = header["yllcorner"] + header["nrows"] * header["cellsize"]
    return header


def load_sampled_hk_grid(header: dict[str, float], grid_x: int, grid_z: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows = np.linspace(0, int(header["nrows"]) - 1, grid_z).round().astype(int)
    cols = np.linspace(0, int(header["ncols"]) - 1, grid_x).round().astype(int)
    wanted_rows = {int(row): idx for idx, row in enumerate(rows)}
    sampled = np.zeros((grid_z, grid_x), dtype=np.float32)

    with zipfile.ZipFile(HK_DTM_ZIP) as archive:
        with archive.open(HK_ASC_NAME) as f:
            for _ in range(6):
                f.readline()
            for row_idx in range(int(header["nrows"])):
                line = f.readline()
                out_idx = wanted_rows.get(row_idx)
                if out_idx is None:
                    continue
                values = np.fromstring(line.decode("ascii"), sep=" ", dtype=np.float32)
                sampled[out_idx, :] = values[cols]

    sampled[sampled == header["nodata_value"]] = 0
    sampled[sampled < 0] = 0
    eastings = header["xllcorner"] + cols * header["cellsize"]
    northings = header["ymax"] - rows * header["cellsize"]
    return sampled, eastings.astype(np.float32), northings.astype(np.float32)


def sample_regular_grid(
    elevations: np.ndarray,
    eastings: np.ndarray,
    northings: np.ndarray,
    easting: float,
    northing: float,
) -> float:
    if easting < eastings[0] or easting > eastings[-1]:
        return 0.0
    if northing < northings[-1] or northing > northings[0]:
        return 0.0
    x = (easting - eastings[0]) / (eastings[-1] - eastings[0]) * (len(eastings) - 1)
    y = (northings[0] - northing) / (northings[0] - northings[-1]) * (len(northings) - 1)
    x0 = int(np.clip(math.floor(x), 0, len(eastings) - 2))
    y0 = int(np.clip(math.floor(y), 0, len(northings) - 2))
    dx = x - x0
    dy = y - y0
    a = elevations[y0, x0]
    b = elevations[y0, x0 + 1]
    c = elevations[y0 + 1, x0]
    d = elevations[y0 + 1, x0 + 1]
    return float((a * (1 - dx) + b * dx) * (1 - dy) + (c * (1 - dx) + d * dx) * dy)


def build_mesh_from_grid(
    elevations: np.ndarray,
    eastings: np.ndarray,
    northings: np.ndarray,
    source: str,
    source_url: str,
    profile_name: str,
) -> dict[str, object]:
    grid_z, grid_x = elevations.shape
    centre_e = float((eastings[0] + eastings[-1]) / 2.0)
    centre_n = float((northings[0] + northings[-1]) / 2.0)
    vertices: list[float] = []
    heights: list[float] = []

    for z_idx, northing in enumerate(northings):
        for x_idx, easting in enumerate(eastings):
            elev = max(0.0, float(elevations[z_idx, x_idx]))
            vertices.extend([
                round(float(easting - centre_e), 3),
                round(elev * VERTICAL_EXAGGERATION, 3),
                round(float(-(northing - centre_n)), 3),
            ])
            heights.append(round(elev, 3))

    indices: list[int] = []
    for z_idx in range(grid_z - 1):
        for x_idx in range(grid_x - 1):
            if max(
                float(elevations[z_idx, x_idx]),
                float(elevations[z_idx, x_idx + 1]),
                float(elevations[z_idx + 1, x_idx]),
                float(elevations[z_idx + 1, x_idx + 1]),
            ) <= 1.0:
                continue
            a = z_idx * grid_x + x_idx
            b = a + 1
            c = (z_idx + 1) * grid_x + x_idx
            d = c + 1
            indices.extend([a, c, b, b, c, d])

    x_vals = vertices[0::3]
    y_vals = vertices[1::3]
    z_vals = vertices[2::3]
    return {
        "metadata": {
            "agent": "Codex",
            "terrain_source": source,
            "source_url": source_url,
            "mesh_profile": profile_name,
            "projection": "Hong Kong 1980 Grid / EPSG:2326 metres; x=easting, z=northing, y=elevation.",
            "vertical_exaggeration": VERTICAL_EXAGGERATION,
            "grid": {"x_samples": grid_x, "z_samples": grid_z},
            "vertex_count": len(heights),
            "triangle_count": len(indices) // 3,
            "bounds_grid": {
                "easting_min": float(eastings[0]),
                "easting_max": float(eastings[-1]),
                "northing_min": float(northings[-1]),
                "northing_max": float(northings[0]),
            },
            "centre_grid": {"easting": centre_e, "northing": centre_n},
            "bounds_m": {
                "x_min": min(x_vals),
                "x_max": max(x_vals),
                "y_min": min(y_vals),
                "y_max": max(y_vals),
                "z_min": min(z_vals),
                "z_max": max(z_vals),
            },
        },
        "vertices": vertices,
        "indices": indices,
        "heights_m": heights,
    }


def write_mesh(folder: Path, mesh: dict[str, object], obj_title: str, profile_name: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    mesh_name = "terrain-mesh.json" if profile_name == "standard" else f"terrain-mesh-{profile_name}.json"
    obj_name = "terrain.obj" if profile_name == "standard" else f"terrain-{profile_name}.obj"
    (folder / mesh_name).write_text(json.dumps(mesh, separators=(",", ":")), encoding="utf-8")

    vertices = mesh["vertices"]
    indices = mesh["indices"]
    assert isinstance(vertices, list)
    assert isinstance(indices, list)
    lines = [
        f"# {obj_title}",
        "# Generated by build_hong_kong_3d_model.py",
        f"# Vertical exaggeration: {VERTICAL_EXAGGERATION}",
    ]
    for i in range(0, len(vertices), 3):
        lines.append(f"v {vertices[i]} {vertices[i + 1]} {vertices[i + 2]}")
    for i in range(0, len(indices), 3):
        lines.append(f"f {indices[i] + 1} {indices[i + 1] + 1} {indices[i + 2] + 1}")
    (folder / obj_name).write_text("\n".join(lines) + "\n", encoding="utf-8")


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


def terrarium_to_elevation_m(rgb: np.ndarray) -> np.ndarray:
    r = rgb[:, :, 0].astype(np.float32)
    g = rgb[:, :, 1].astype(np.float32)
    b = rgb[:, :, 2].astype(np.float32)
    return (r * 256.0 + g + b / 256.0) - 32768.0


def fetch_tile(tile_dir: Path, z: int, x: int, y: int) -> Image.Image:
    tile_dir.mkdir(parents=True, exist_ok=True)
    path = tile_dir / f"{z}-{x}-{y}.png"
    if not path.exists():
        url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
        last_error: Exception | None = None
        for attempt in range(4):
            try:
                with urllib.request.urlopen(url, timeout=45) as response:
                    path.write_bytes(response.read())
                break
            except Exception as error:
                last_error = error
                time.sleep(1.5 * (attempt + 1))
        else:
            raise RuntimeError(f"Failed to download {url}") from last_error
    return Image.open(path).convert("RGB")


def lon_to_easting(lon: float, header: dict[str, float]) -> float:
    return header["xllcorner"] + (lon - HK_LON_LAT_BBOX["west"]) / (HK_LON_LAT_BBOX["east"] - HK_LON_LAT_BBOX["west"]) * (header["xmax"] - header["xllcorner"])


def lat_to_northing(lat: float, header: dict[str, float]) -> float:
    return header["yllcorner"] + (lat - HK_LON_LAT_BBOX["south"]) / (HK_LON_LAT_BBOX["north"] - HK_LON_LAT_BBOX["south"]) * (header["ymax"] - header["yllcorner"])


def easting_to_lon(easting: float, header: dict[str, float]) -> float:
    return HK_LON_LAT_BBOX["west"] + (easting - header["xllcorner"]) / (header["xmax"] - header["xllcorner"]) * (HK_LON_LAT_BBOX["east"] - HK_LON_LAT_BBOX["west"])


def northing_to_lat(northing: float, header: dict[str, float]) -> float:
    return HK_LON_LAT_BBOX["south"] + (northing - header["yllcorner"]) / (header["ymax"] - header["yllcorner"]) * (HK_LON_LAT_BBOX["north"] - HK_LON_LAT_BBOX["south"])


def build_aws_grid(header: dict[str, float], eastings: np.ndarray, northings: np.ndarray, zoom: int) -> np.ndarray:
    bbox = HK_LON_LAT_BBOX
    tile_dir = AWS_OUT / f"dem_tiles_z{zoom}"
    x0 = lon_to_tile_x(bbox["west"], zoom)
    x1 = lon_to_tile_x(bbox["east"], zoom)
    y0 = lat_to_tile_y(bbox["north"], zoom)
    y1 = lat_to_tile_y(bbox["south"], zoom)
    rows = []
    for ty in range(y0, y1 + 1):
        rows.append(np.concatenate([np.asarray(fetch_tile(tile_dir, zoom, tx, ty)) for tx in range(x0, x1 + 1)], axis=1))
    elevation = terrarium_to_elevation_m(np.concatenate(rows, axis=0))
    extent = {
        "west": tile_x_to_lon(x0, zoom),
        "east": tile_x_to_lon(x1 + 1, zoom),
        "north": tile_y_to_lat(y0, zoom),
        "south": tile_y_to_lat(y1 + 1, zoom),
    }

    grid = np.zeros((len(northings), len(eastings)), dtype=np.float32)
    for z_idx, northing in enumerate(northings):
        lat = HK_LON_LAT_BBOX["south"] + (northing - header["yllcorner"]) / (header["ymax"] - header["yllcorner"]) * (HK_LON_LAT_BBOX["north"] - HK_LON_LAT_BBOX["south"])
        for x_idx, easting in enumerate(eastings):
            lon = HK_LON_LAT_BBOX["west"] + (easting - header["xllcorner"]) / (header["xmax"] - header["xllcorner"]) * (HK_LON_LAT_BBOX["east"] - HK_LON_LAT_BBOX["west"])
            x = (lon - extent["west"]) / (extent["east"] - extent["west"]) * (elevation.shape[1] - 1)
            y = (extent["north"] - lat) / (extent["north"] - extent["south"]) * (elevation.shape[0] - 1)
            if x < 0 or y < 0 or x >= elevation.shape[1] - 1 or y >= elevation.shape[0] - 1:
                continue
            x_i = int(math.floor(x))
            y_i = int(math.floor(y))
            dx = x - x_i
            dy = y - y_i
            a = elevation[y_i, x_i]
            b = elevation[y_i, x_i + 1]
            c = elevation[y_i + 1, x_i]
            d = elevation[y_i + 1, x_i + 1]
            grid[z_idx, x_idx] = max(0.0, float((a * (1 - dx) + b * dx) * (1 - dy) + (c * (1 - dx) + d * dx) * dy))
    return grid


def rdp(points: list[tuple[float, float, float]], epsilon: float) -> list[tuple[float, float, float]]:
    if len(points) < 3:
        return points
    start = np.array(points[0][:2], dtype=float)
    end = np.array(points[-1][:2], dtype=float)
    line = end - start
    length = np.linalg.norm(line)
    if length == 0:
        distances = [np.linalg.norm(np.array(p[:2]) - start) for p in points]
    else:
        distances = [abs(line[0] * (start[1] - p[1]) - line[1] * (start[0] - p[0])) / length for p in points]
    idx = int(np.argmax(distances))
    if distances[idx] > epsilon:
        return rdp(points[: idx + 1], epsilon)[:-1] + rdp(points[idx:], epsilon)
    return [points[0], points[-1]]


def find_zip_member(archive: zipfile.ZipFile, suffix: str) -> str:
    for name in archive.namelist():
        if name.endswith(suffix):
            return name
    raise FileNotFoundError(suffix)


def parse_b50k_lines(
    header: dict[str, float],
    hk_grid: np.ndarray,
    eastings: np.ndarray,
    northings: np.ndarray,
) -> dict[str, object]:
    centre_e = float((eastings[0] + eastings[-1]) / 2.0)
    centre_n = float((northings[0] + northings[-1]) / 2.0)
    layers: dict[str, object] = {}
    namespace_pos = "{http://www.opengis.net/gml}posList"

    with zipfile.ZipFile(B50K_ZIP) as archive:
        for layer_name, layer in B50K_LAYERS.items():
            member = find_zip_member(archive, str(layer["member"]))
            lines: list[list[float]] = []
            feature_count = 0
            with archive.open(member) as f:
                for _, elem in ET.iterparse(f, events=("end",)):
                    if elem.tag != namespace_pos or not elem.text:
                        continue
                    values = [float(v) for v in elem.text.split()]
                    points: list[tuple[float, float, float]] = []
                    # LandsD B50K GML stores line posList pairs as northing/easting.
                    for i in range(0, len(values) - 1, 2):
                        northing = values[i]
                        easting = values[i + 1]
                        if easting < eastings[0] or easting > eastings[-1] or northing < northings[-1] or northing > northings[0]:
                            continue
                        elev = sample_regular_grid(hk_grid, eastings, northings, easting, northing)
                        points.append((easting - centre_e, -(northing - centre_n), elev))
                    elem.clear()
                    if len(points) < 2:
                        continue
                    simplified = rdp(points, float(layer["epsilon_m"]))
                    if len(simplified) < 2:
                        continue
                    packed: list[float] = []
                    for x, z, elev in simplified:
                        packed.extend([round(x, 2), round(z, 2), round(elev, 2)])
                    lines.append(packed)
                    feature_count += 1
                    if feature_count >= int(layer["max_features"]):
                        break
            layers[layer_name] = {
                "colour": layer["colour"],
                "lines": lines,
                "feature_count": len(lines),
            }

    return {
        "metadata": {
            "agent": "Codex",
            "source": "Hong Kong Lands Department 1:50 000 Topographic Map of Hong Kong GML",
            "source_url": "https://data.gov.hk/en-data/dataset/hk-landsd-openmap-b50k-topographic-map-of-hong-kong",
            "download_url": "https://www.landsd.gov.hk/landsd_psi_data/SMO/data/iB50000GML.zip",
            "projection": "Source GML is EPSG:2326; posList is parsed as northing/easting for this LandsD package.",
            "vertical_exaggeration_reference": VERTICAL_EXAGGERATION,
        },
        "layers": layers,
    }


def parse_lantau_b50k_lines(
    header: dict[str, float],
    hk_grid: np.ndarray,
    eastings: np.ndarray,
    northings: np.ndarray,
) -> dict[str, object]:
    mean_lat = (LANTAU_BBOX["south"] + LANTAU_BBOX["north"]) / 2.0
    metres_per_degree_lon = 111_320.0 * math.cos(math.radians(mean_lat))
    metres_per_degree_lat = 110_540.0
    centre_lon = (LANTAU_BBOX["west"] + LANTAU_BBOX["east"]) / 2.0
    centre_lat = (LANTAU_BBOX["south"] + LANTAU_BBOX["north"]) / 2.0
    layers: dict[str, object] = {}
    namespace_pos = "{http://www.opengis.net/gml}posList"

    with zipfile.ZipFile(B50K_ZIP) as archive:
        for layer_name, layer in B50K_LAYERS.items():
            member = find_zip_member(archive, str(layer["member"]))
            lines: list[list[float]] = []
            feature_count = 0
            with archive.open(member) as f:
                for _, elem in ET.iterparse(f, events=("end",)):
                    if elem.tag != namespace_pos or not elem.text:
                        continue
                    values = [float(v) for v in elem.text.split()]
                    points: list[tuple[float, float, float]] = []
                    # LandsD B50K GML stores line posList pairs as northing/easting.
                    for i in range(0, len(values) - 1, 2):
                        northing = values[i]
                        easting = values[i + 1]
                        lon = easting_to_lon(easting, header)
                        lat = northing_to_lat(northing, header)
                        if lon < LANTAU_BBOX["west"] or lon > LANTAU_BBOX["east"] or lat < LANTAU_BBOX["south"] or lat > LANTAU_BBOX["north"]:
                            continue
                        elev = sample_regular_grid(hk_grid, eastings, northings, easting, northing)
                        x = (lon - centre_lon) * metres_per_degree_lon
                        z = -(lat - centre_lat) * metres_per_degree_lat
                        points.append((x, z, elev))
                    elem.clear()
                    if len(points) < 2:
                        continue
                    simplified = rdp(points, float(layer["epsilon_m"]) * 0.6)
                    if len(simplified) < 2:
                        continue
                    packed: list[float] = []
                    for x, z, elev in simplified:
                        packed.extend([round(x, 2), round(z, 2), round(elev, 2)])
                    lines.append(packed)
                    feature_count += 1
                    if feature_count >= int(layer["max_features"]):
                        break
            layers[layer_name] = {
                "colour": layer["colour"],
                "lines": lines,
                "feature_count": len(lines),
            }

    return {
        "metadata": {
            "agent": "Codex",
            "source": "Hong Kong Lands Department 1:50 000 Topographic Map of Hong Kong GML, clipped and transformed for the local Lantau mesh.",
            "source_url": "https://data.gov.hk/en-data/dataset/hk-landsd-openmap-b50k-topographic-map-of-hong-kong",
            "download_url": "https://www.landsd.gov.hk/landsd_psi_data/SMO/data/iB50000GML.zip",
            "projection": "Source GML is EPSG:2326; output is local Lantau mesh x/z metres derived through the project affine lon/lat mapping.",
            "vertical_exaggeration_reference": VERTICAL_EXAGGERATION,
            "bbox_lon_lat": LANTAU_BBOX,
        },
        "layers": layers,
    }


def main() -> None:
    header = read_hk_header()

    skin_grid = None
    skin_eastings = None
    skin_northings = None

    for profile in MESH_PROFILES:
        profile_name = str(profile["name"])
        grid_x = int(profile["grid_x"])
        grid_z = int(profile["grid_z"])
        aws_zoom = int(profile["aws_zoom"])
        hk_grid, eastings, northings = load_sampled_hk_grid(header, grid_x, grid_z)

        hk_mesh = build_mesh_from_grid(
            hk_grid,
            eastings,
            northings,
            "Hong Kong Lands Department 5 m Digital Terrain Model from data.gov.hk",
            "https://data.gov.hk/en-data/dataset/hk-landsd-openmap-5m-grid-dtm/resource/620c4f4f-eac4-472f-9074-dffa2ad596fd",
            profile_name,
        )
        write_mesh(HK_OUT, hk_mesh, "Whole Hong Kong terrain mesh from LandsD 5 m DTM", profile_name)

        aws_grid = build_aws_grid(header, eastings, northings, aws_zoom)
        aws_mesh = build_mesh_from_grid(
            aws_grid,
            eastings,
            northings,
            f"AWS elevation-tiles-prod Terrarium DEM tiles, zoom {aws_zoom}",
            "https://registry.opendata.aws/terrain-tiles/",
            profile_name,
        )
        write_mesh(AWS_OUT, aws_mesh, "Whole Hong Kong terrain mesh from AWS Terrarium DEM", profile_name)

        print(f"{profile_name} HK 5 m mesh: {hk_mesh['metadata']['vertex_count']} vertices, {hk_mesh['metadata']['triangle_count']} triangles")
        print(f"{profile_name} AWS mesh: {aws_mesh['metadata']['vertex_count']} vertices, {aws_mesh['metadata']['triangle_count']} triangles")

        if profile_name == "detail":
            skin_grid = hk_grid
            skin_eastings = eastings
            skin_northings = northings

    assert skin_grid is not None and skin_eastings is not None and skin_northings is not None
    skin = parse_b50k_lines(header, skin_grid, skin_eastings, skin_northings)
    lantau_skin = parse_lantau_b50k_lines(header, skin_grid, skin_eastings, skin_northings)
    B50K_OUT.mkdir(parents=True, exist_ok=True)
    (B50K_OUT / "skin-lines.json").write_text(json.dumps(skin, separators=(",", ":")), encoding="utf-8")
    (B50K_OUT / "skin-lines-lantau.json").write_text(json.dumps(lantau_skin, separators=(",", ":")), encoding="utf-8")

    print("B50K skin layers:", ", ".join(skin["layers"].keys()))
    print("Lantau B50K skin layers:", ", ".join(lantau_skin["layers"].keys()))


if __name__ == "__main__":
    main()
