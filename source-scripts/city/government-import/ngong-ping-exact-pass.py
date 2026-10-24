"""Exact source-terrain pass for the Ngong Ping / Lantau peaks government batch.

The pass uses only immutable Lands Department building and terrain members.
It never generates, edits, simplifies, or semantically reviews geometry.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

import numpy as np
import shapely
from shapely.geometry import Polygon, box

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BATCH = "government-ngong-ping-peaks-473-20260918"
DOC = ROOT / "docs/astra-city/government-import" / BATCH
LOCAL = HERE / "local" / BATCH
RECOVERED = LOCAL / "recovered"
TERRAIN = LOCAL / "source-terrain"

spec = importlib.util.spec_from_file_location("resolve", HERE / "resolve-pass.py")
resolve = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resolve)
context = resolve.context

spec = importlib.util.spec_from_file_location(
    "native_download", HERE.parent / "citywide-native/download.py"
)
native_download = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native_download)


def read(path: Path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def save(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == ".gz" else raw)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def polygon(building):
    value = Polygon(building["rings"][0], building["rings"][1:])
    return shapely.make_valid(value) if not value.is_valid else value


def geometry_triangles(row):
    positions = np.asarray(row["position"], dtype=float).reshape(-1, 3)
    indices = np.asarray(row["index"], dtype=int).reshape(-1, 3)
    return positions[indices]


def projected(triangles):
    faces = shapely.polygons(triangles[:, :, [0, 2]])
    return shapely.union_all(faces[shapely.area(faces) > 1e-10])


def fetch_sheet(sheet: str):
    source = RECOVERED / "sheets" / sheet
    row = read(source / "directory/result.json")
    row["models"] = []
    out = TERRAIN / sheet
    record = native_download.acquire(
        row,
        source / "directory/zip-directory.bin",
        out,
        include_terrain=True,
    )
    decoded = out / "decoded"
    members = []
    with zipfile.ZipFile(out / f"{sheet}.zip") as archive:
        terrain_names = [
            name for name in archive.namelist()
            if name.startswith("TERRAIN") and name.endswith((".gltf", ".bin"))
        ]
        if not terrain_names:
            raise ValueError(f"{sheet}: no source terrain geometry")
        for name in terrain_names:
            target = decoded / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(name))
            members.append({
                "path": str(target.relative_to(ROOT)),
                "sha256": digest(target),
                "bytes": target.stat().st_size,
            })
    return {
        "sheet": sheet,
        "revisionDate": record["revisionDate"],
        "sourceETag": record["sourceETag"],
        "directorySHA256": record["directorySHA256"],
        "compactArchiveSHA256": record["sha256"],
        "compactArchiveBytes": record["bytes"],
        "sourceArchiveBytes": record["sourceArchiveBytes"],
        "receivedBytes": record["receivedBytes"],
        "newThisInvocationBytes": record["newThisInvocationBytes"],
        "members": members,
    }


def fetch():
    selection = read(DOC / "check-selection.json.gz")
    sheets = sorted({row["native"]["sheet"] for row in selection["rows"]})
    results = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fetch_sheet, sheet): sheet for sheet in sheets}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps({
                "terrainSheets": len(results), "totalSheets": len(sheets),
                "sheet": result["sheet"], "newBytes": result["newThisInvocationBytes"],
            }), flush=True)
    results.sort(key=lambda row: row["sheet"])
    report = {
        "batch": BATCH,
        "sheets": results,
        "sourceSheets": len(results),
        "compactBytes": sum(row["compactArchiveBytes"] for row in results),
        "receivedBytes": sum(row["receivedBytes"] for row in results),
        "newThisInvocationBytes": sum(row["newThisInvocationBytes"] for row in results),
        "sourceArchiveBytesAvoided": sum(row["sourceArchiveBytes"] for row in results),
        "aiCalls": 0,
        "modelGeometryChanges": 0,
        "publication": False,
    }
    save(DOC / "source-terrain.json", report)
    print(json.dumps({key: value for key, value in report.items() if key != "sheets"}), flush=True)


def load_forms():
    manifest = read(ROOT / "3d-viewer/city/data/manifest.json")
    forms = []
    for tile in manifest["tiles"]:
        for building in read(ROOT / "3d-viewer" / tile["url"])["buildings"]:
            if building.get("rings"):
                forms.append((building, polygon(building), tile["url"]))
    return forms


def identity_context(selection, triangles, nearby):
    source = projected(triangles)
    target, target_shape, _ = next(item for item in nearby if item[0]["uid"] == selection["uid"])
    entry = selection["candidate"]["entry"]
    intersecting = []
    for building, shape, tile in nearby:
        area = float(source.intersection(shape).area)
        if area <= 0.01:
            continue
        intersecting.append({
            "uid": building["uid"], "name": building.get("name"), "tile": tile,
            "base": building.get("base"),
            "top": (building.get("base") or 0) + (building.get("height") or 0),
            "intersectionAreaM2": area,
            "fractionOfForm": area / shape.area if shape.area else None,
            "sameParent": bool(target.get("parent") and building.get("parent") == target.get("parent")),
            "sharedOsmReference": bool(set(target.get("osmRefs", [])) & set(building.get("osmRefs", []))),
        })
    intersecting.sort(key=lambda item: (-item["intersectionAreaM2"], item["uid"]))
    inside = float(source.intersection(target_shape).area)
    return {
        "exactObjectAndCSUID": (
            target.get("objectId") == entry.get("objectId")
            and target.get("buildingCSUID") == entry.get("buildingCSUID")
        ),
        "officialOverlapOfSmallerFootprint": entry.get("overlapOfSmallerFootprint"),
        "officialFootprintCentroidDistanceM": entry.get("footprintCentroidDistanceMetres"),
        "targetTopHKPD": (target.get("base") or 0) + (target.get("height") or 0),
        "sourceMinimumHKPD": float(triangles[:, :, 1].min()),
        "sourceMaximumHKPD": float(triangles[:, :, 1].max()),
        "sourceProjectionAreaM2": float(source.area),
        "targetCoveredBySourceProjection": inside / target_shape.area,
        "sourceProjectionInsideTarget": inside / source.area,
        "intersectingForms": intersecting,
    }, target_shape


def connected_components(triangles, selected):
    indices = np.flatnonzero(selected)
    by_vertex = defaultdict(list)
    for local, face in enumerate(triangles[indices]):
        for vertex in face:
            by_vertex[tuple(np.round(vertex, 4))].append(local)
    adjacent = defaultdict(set)
    for faces in by_vertex.values():
        for face in faces:
            adjacent[face].update(faces)
    unseen = set(range(len(indices)))
    result = []
    while unseen:
        start = unseen.pop()
        queue = deque([start])
        component = [start]
        while queue:
            for neighbour in adjacent[queue.popleft()]:
                if neighbour in unseen:
                    unseen.remove(neighbour)
                    queue.append(neighbour)
                    component.append(neighbour)
        result.append(indices[np.asarray(component)])
    return result


def foundation_context(triangles, terrain):
    lo, hi = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
    nearby = terrain[
        (terrain[:, :, 0].max(axis=1) >= lo[0] - 1)
        & (terrain[:, :, 0].min(axis=1) <= hi[0] + 1)
        & (terrain[:, :, 2].max(axis=1) >= lo[2] - 1)
        & (terrain[:, :, 2].min(axis=1) <= hi[2] + 1)
    ]
    terrain_polygons = shapely.polygons(nearby[:, :, [0, 2]])
    valid = shapely.area(terrain_polygons) > 1e-10
    nearby, terrain_polygons = nearby[valid], terrain_polygons[valid]
    points = np.concatenate([triangles, triangles.mean(axis=1)[:, None, :]], axis=1)
    heights = context.shared.samples(
        points[:, :, [0, 2]].reshape(-1, 2),
        nearby,
        shapely.STRtree(terrain_polygons),
    ).reshape(-1, 4)
    gaps = points[:, :, 1] - heights
    complete = np.isfinite(heights).all(axis=1)
    buried = complete & (gaps < -0.5).all(axis=1)
    cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    area = np.linalg.norm(cross, axis=1) / 2
    upward = cross[:, 1] > 0.25 * np.linalg.norm(cross, axis=1)
    components = []
    for component in connected_components(triangles, buried):
        components.append({
            "triangles": len(component),
            "areaM2": float(area[component].sum()),
            "areaFraction": float(area[component].sum() / area.sum()),
            "upwardTriangles": int(upward[component].sum()),
            "upwardAreaM2": float(area[component][upward[component]].sum()),
            "gapRangeM": [float(gaps[component].min()), float(gaps[component].max())],
        })
    return {
        "triangles": len(triangles),
        "completeTerrainTriangles": int(complete.sum()),
        "fullyBuriedTriangles": int(buried.sum()),
        "fullyBuriedAreaM2": float(area[buried].sum()),
        "fullyBuriedAreaFraction": float(area[buried].sum() / area.sum()),
        "fullyBuriedUpwardTriangles": int((buried & upward).sum()),
        "fullyBuriedUpwardAreaM2": float(area[buried & upward].sum()),
        "minimumGapM": float(gaps[complete].min()) if complete.any() else None,
        "maximumGapM": float(gaps[complete].max()) if complete.any() else None,
        "components": sorted(components, key=lambda item: -item["areaM2"]),
    }


def exact():
    selection = {row["uid"]: row for row in read(DOC / "check-selection.json.gz")["rows"]}
    geometries = {row["uid"]: row for row in read(LOCAL / "geometry.json.gz")["rows"]}
    validation = {row["uid"]: row for row in read(DOC / "validation.json")["results"]}
    missing = set(selection) - set(geometries)
    assert set(geometries) <= set(selection) and len(selection) == 473
    assert missing and all(validation[uid]["outcome"] == "validation-exception" for uid in missing)
    terrain_proof = {row["sheet"]: row for row in read(DOC / "source-terrain.json")["sheets"]}
    terrains = {}
    for sheet, proof in terrain_proof.items():
        files = sorted((TERRAIN / sheet / "decoded").rglob("*.gltf"))
        assert files
        for member in proof["members"]:
            assert digest(ROOT / member["path"]) == member["sha256"]
        terrains[sheet] = np.concatenate([context.triangles(path) for path in files])
    forms = load_forms()
    tree = shapely.STRtree([shape for _, shape, _ in forms])
    results = []
    for uid in sorted(missing):
        row = selection[uid]
        results.append({
            "uid": uid,
            "modelId": row["candidate"]["entry"]["modelId"],
            "name": row["candidate"]["entry"].get("label"),
            "sizeGroup": row["native"]["model"].get("sizeGroup"),
            "sourceSheet": row["native"]["sheet"],
            "sourceSHA256": row["candidate"]["entry"]["sha256"],
            "identity": None,
            "foundation": None,
            "identityScriptAccepted": False,
            "boundedFoundationAccepted": False,
            "floatingAboveTerrain": False,
            "retainsBasicForm": False,
            "basicSupportGapM": None,
            "suppressesBuildingUids": [],
            "publicationCandidate": False,
            "reasons": ["runtime-validation-exception"],
            "validationError": validation[uid]["error"],
            "humanStatus": "held-unknown",
            "requiresAI": False,
            "requiresUserDecision": False,
            "needsMoreCompute": False,
            "scriptedWorkComplete": True,
            "aiCalls": 0,
            "modelGeometryChanges": 0,
            "publication": False,
        })
    for number, uid in enumerate(sorted(geometries), 1):
        row = selection[uid]
        triangles = geometry_triangles(geometries[uid])
        lo, hi = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
        indices = tree.query(box(lo[0] - 2, lo[2] - 2, hi[0] + 2, hi[2] + 2))
        nearby = [forms[int(index)] for index in indices]
        identity, target = identity_context(row, triangles, nearby)
        foundation = foundation_context(triangles, terrains[row["native"]["sheet"]])
        identity_clear = (
            identity["exactObjectAndCSUID"]
            and identity["officialOverlapOfSmallerFootprint"] >= 0.75
            and identity["officialFootprintCentroidDistanceM"] <= 3
            and identity["targetCoveredBySourceProjection"] >= 0.65
        )
        complete = foundation["completeTerrainTriangles"] == foundation["triangles"]
        bounded_foundation = (
            complete
            and foundation["fullyBuriedAreaFraction"] <= 0.10
            and foundation["minimumGapM"] is not None
            and foundation["minimumGapM"] >= -10
        )
        floating = foundation["minimumGapM"] is not None and foundation["minimumGapM"] > 0.5
        basic_support_gap = identity["sourceMinimumHKPD"] - identity["targetTopHKPD"]
        retained_basic_support = floating and -1.5 <= basic_support_gap <= 1.0
        suppressions = sorted({
            form["uid"] for form in identity["intersectingForms"]
            if form["uid"] != uid
            and form["fractionOfForm"] >= 0.95
            and identity["sourceMaximumHKPD"] >= form["top"] - 0.25
        })
        reasons = []
        if not identity_clear:
            reasons.append("source-identity-fit-below-script-policy")
        if not complete:
            reasons.append("source-terrain-incomplete")
        elif floating and not retained_basic_support:
            reasons.append("native-source-support-not-found")
        elif not floating and not bounded_foundation:
            reasons.append("below-grade-source-surfaces-exceed-bounded-foundation-policy")
        publication_candidate = not reasons
        results.append({
            "uid": uid,
            "modelId": row["candidate"]["entry"]["modelId"],
            "name": row["candidate"]["entry"].get("label"),
            "sizeGroup": row["native"]["model"].get("sizeGroup"),
            "sourceSheet": row["native"]["sheet"],
            "sourceSHA256": row["candidate"]["entry"]["sha256"],
            "identity": identity,
            "foundation": foundation,
            "identityScriptAccepted": identity_clear,
            "boundedFoundationAccepted": bounded_foundation,
            "floatingAboveTerrain": floating,
            "retainsBasicForm": retained_basic_support,
            "basicSupportGapM": basic_support_gap,
            "suppressesBuildingUids": suppressions,
            "publicationCandidate": publication_candidate,
            "reasons": reasons,
            "humanStatus": "to-do" if publication_candidate else "held-unknown",
            "requiresAI": False,
            "requiresUserDecision": False,
            "needsMoreCompute": False,
            "scriptedWorkComplete": True,
            "aiCalls": 0,
            "modelGeometryChanges": 0,
            "publication": False,
        })
        if number % 50 == 0:
            print(json.dumps({
                "checked": number,
                "candidates": sum(item["publicationCandidate"] for item in results),
            }), flush=True)
    reason_counts = Counter(reason for row in results for reason in row["reasons"])
    report = {
        "batch": BATCH,
        "models": len(results),
        "rows": results,
        "publicationCandidates": sum(row["publicationCandidate"] for row in results),
        "heldAfterCompleteScriptPass": sum(not row["publicationCandidate"] for row in results),
        "reasonCounts": dict(reason_counts),
        "sourceSheets": len(terrains),
        "aiCalls": 0,
        "modelGeometryChanges": 0,
        "publication": False,
        "inputHashes": {
            str((DOC / "check-selection.json.gz").relative_to(ROOT)): digest(DOC / "check-selection.json.gz"),
            str((LOCAL / "geometry.json.gz").relative_to(ROOT)): digest(LOCAL / "geometry.json.gz"),
            str((DOC / "source-terrain.json").relative_to(ROOT)): digest(DOC / "source-terrain.json"),
        },
        "qualification": (
            f"{len(geometries)} decoded sources received exact identifier, projected assembly, and full-face "
            f"same-sheet source-TIN checks; {len(missing)} runtime-rejected source remained held. Source geometry remains unchanged."
        ),
    }
    save(DOC / "exact-pass-results.json.gz", report)
    save(DOC / "exact-pass-summary.json", {key: value for key, value in report.items() if key != "rows"})
    print(json.dumps({key: value for key, value in report.items() if key not in ("rows", "inputHashes", "qualification")}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("fetch", "exact"))
    globals()[parser.parse_args().phase]()
