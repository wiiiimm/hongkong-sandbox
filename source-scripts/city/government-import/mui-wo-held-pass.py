"""Exhaust deterministic checks for the 16 held Mui Wo government sources.

This pass is read-only. It preserves the source meshes and reports full-face
terrain contact, exact identity/assembly overlap, and native source supports.
"""
from __future__ import annotations

from collections import defaultdict, deque
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import shapely
from shapely.geometry import Polygon, box

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BATCH = "government-mui-wo-23-20260914"
BASE = ROOT / "docs/astra-city/government-import" / BATCH
LOCAL = HERE / "local" / BATCH
OUT = ROOT / "docs/astra-city/government-import/government-mui-wo-16-20260915"
HELD = {
    "landsd/121912:0", "landsd/172460:0", "landsd/179822:0", "landsd/201705:0",
    "landsd/206975:0", "landsd/207849:0", "landsd/207855:0", "landsd/207859:0",
    "landsd/207860:0", "landsd/208036:0", "landsd/208958:0", "landsd/254783:0",
    "landsd/262466:0", "landsd/299366:0", "landsd/299369:0", "landsd/299383:0",
}

spec = importlib.util.spec_from_file_location("resolve", HERE / "resolve-pass.py")
resolve = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resolve)
context = resolve.context
spec = importlib.util.spec_from_file_location("terrain", HERE / "mui-wo-terrain-resolve.py")
terrain_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(terrain_module)


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
    result = Polygon(building["rings"][0], building["rings"][1:])
    return shapely.make_valid(result) if not result.is_valid else result


def geometry_triangles(row):
    positions = np.asarray(row["position"], dtype=float).reshape(-1, 3)
    indices = np.asarray(row["index"], dtype=int).reshape(-1, 3)
    return positions[indices]


def projected(triangles):
    faces = shapely.polygons(triangles[:, :, [0, 2]])
    return shapely.union_all(faces[shapely.area(faces) > 1e-10])


def load_forms(bounds):
    query = box(*bounds)
    manifest = read(ROOT / "3d-viewer/city/data/manifest.json")
    result = []
    for tile in manifest["tiles"]:
        if not box(*tile["bounds"]).intersects(query):
            continue
        for building in read(ROOT / "3d-viewer" / tile["url"])["buildings"]:
            if building.get("rings"):
                shape = polygon(building)
                if shape.intersects(query):
                    result.append((building, shape, tile["url"]))
    return result


def identity_context(selection, triangles, forms):
    source = projected(triangles)
    target, target_shape, _ = next(item for item in forms if item[0]["uid"] == selection["uid"])
    entry = selection["candidate"]["entry"]
    intersecting = []
    for building, shape, tile in forms:
        area = float(source.intersection(shape).area)
        if area <= 0.01:
            continue
        intersecting.append({
            "uid": building["uid"], "name": building.get("name"), "tile": tile,
            "base": building.get("base"), "top": (building.get("base") or 0) + (building.get("height") or 0),
            "intersectionAreaM2": area, "fractionOfForm": area / shape.area if shape.area else None,
            "sameParent": bool(target.get("parent") and building.get("parent") == target.get("parent")),
            "sharedOsmReference": bool(set(target.get("osmRefs", [])) & set(building.get("osmRefs", []))),
        })
    intersecting.sort(key=lambda item: (-item["intersectionAreaM2"], item["uid"]))
    excess = source.difference(target_shape)
    unrelated = shapely.union_all([
        shape for building, shape, _ in forms
        if building["uid"] != target["uid"]
        and building.get("parent") != target.get("parent")
        and not (set(building.get("osmRefs", [])) & set(target.get("osmRefs", [])))
    ])
    coordinates = shapely.get_coordinates(excess)
    distance = float(shapely.distance(shapely.points(coordinates), target_shape).max()) if len(coordinates) else 0.0
    inside = float(source.intersection(target_shape).area)
    return {
        "exactObjectAndCSUID": target.get("objectId") == entry.get("objectId") and target.get("buildingCSUID") == entry.get("buildingCSUID"),
        "officialOverlapOfSmallerFootprint": entry.get("overlapOfSmallerFootprint"),
        "officialFootprintCentroidDistanceM": entry.get("footprintCentroidDistanceMetres"),
        "targetTopHKPD": (target.get("base") or 0) + (target.get("height") or 0),
        "sourceMinimumHKPD": float(triangles[:, :, 1].min()),
        "sourceMaximumHKPD": float(triangles[:, :, 1].max()),
        "sourceProjectionAreaM2": float(source.area),
        "targetCoveredBySourceProjection": inside / target_shape.area,
        "sourceProjectionInsideTarget": inside / source.area,
        "sourceExcessFraction": float(excess.area / source.area),
        "sourceExcessMaximumDistanceFromTargetM": distance,
        "sourceExcessCoveredByUnrelatedFormsM2": float(excess.intersection(unrelated).area),
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
        start = unseen.pop(); queue = deque([start]); component = [start]
        while queue:
            for neighbour in adjacent[queue.popleft()]:
                if neighbour in unseen:
                    unseen.remove(neighbour); queue.append(neighbour); component.append(neighbour)
        result.append(indices[np.asarray(component)])
    return result


def foundation_context(triangles, terrain, target):
    lo, hi = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
    nearby = terrain[
        (terrain[:, :, 0].max(axis=1) >= lo[0] - 1) & (terrain[:, :, 0].min(axis=1) <= hi[0] + 1)
        & (terrain[:, :, 2].max(axis=1) >= lo[2] - 1) & (terrain[:, :, 2].min(axis=1) <= hi[2] + 1)
    ]
    terrain_polygons = shapely.polygons(nearby[:, :, [0, 2]])
    valid = shapely.area(terrain_polygons) > 1e-10
    nearby, terrain_polygons = nearby[valid], terrain_polygons[valid]
    points = np.concatenate([triangles, triangles.mean(axis=1)[:, None, :]], axis=1)
    heights = context.shared.samples(points[:, :, [0, 2]].reshape(-1, 2), nearby, shapely.STRtree(terrain_polygons)).reshape(-1, 4)
    gaps = points[:, :, 1] - heights
    complete = np.isfinite(heights).all(axis=1)
    buried = complete & (gaps < -0.5).all(axis=1)
    cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    area = np.linalg.norm(cross, axis=1) / 2
    upward = cross[:, 1] > 0.25 * np.linalg.norm(cross, axis=1)
    components = []
    for component in connected_components(triangles, buried):
        components.append({
            "triangles": len(component), "areaM2": float(area[component].sum()),
            "areaFraction": float(area[component].sum() / area.sum()),
            "upwardTriangles": int(upward[component].sum()),
            "upwardAreaM2": float(area[component][upward[component]].sum()),
            "gapRangeM": [float(gaps[component].min()), float(gaps[component].max())],
            "yRange": [float(triangles[component, :, 1].min()), float(triangles[component, :, 1].max())],
        })
    return {
        "triangles": len(triangles), "completeTerrainTriangles": int(complete.sum()),
        "fullyBuriedTriangles": int(buried.sum()), "fullyBuriedAreaM2": float(area[buried].sum()),
        "fullyBuriedAreaFraction": float(area[buried].sum() / area.sum()),
        "fullyBuriedUpwardTriangles": int((buried & upward).sum()),
        "fullyBuriedUpwardAreaM2": float(area[buried & upward].sum()),
        "minimumGapM": float(gaps[complete].min()) if complete.any() else None,
        "maximumGapM": float(gaps[complete].max()) if complete.any() else None,
        "components": sorted(components, key=lambda item: -item["areaM2"]),
    }


def source_supports(sheet, model_id, triangles):
    roots = [HERE.parent / "mui-wo-detail-completion/staged" / sheet / "BUILDING"]
    if sheet in {"10-SW-19A", "10-SW-14C"}:
        roots = [LOCAL / "recovered/sheets" / sheet / "decoded/BUILDING"]
    target_projection = projected(triangles)
    target_minimum = float(triangles[:, :, 1].min())
    result = []
    for root in roots:
        for path in root.glob("*/*.gltf") if root.exists() else []:
            if path.stem == model_id:
                continue
            try:
                other = context.triangles(path)
            except (ValueError, OSError, KeyError):
                continue
            if other[:, :, 1].max() < target_minimum - 3 or other[:, :, 1].min() > target_minimum + 3:
                continue
            overlap = float(target_projection.intersection(projected(other)).area)
            if overlap > 0.01:
                result.append({"modelId": path.stem, "overlapM2": overlap, "topHKPD": float(other[:, :, 1].max()), "gapToTargetMinimumM": target_minimum - float(other[:, :, 1].max())})
    return sorted(result, key=lambda item: (abs(item["gapToTargetMinimumM"]), -item["overlapM2"]))


def main():
    selection = {row["uid"]: row for row in read(BASE / "check-selection.json.gz")["rows"] if row["uid"] in HELD}
    geometries = {row["uid"]: row for row in read(LOCAL / "geometry.json.gz")["rows"] if row["uid"] in HELD}
    assert set(selection) == set(geometries) == HELD
    terrains = terrain_module.sources()
    results = []
    for uid in sorted(HELD):
        row = selection[uid]; triangles = geometry_triangles(geometries[uid])
        lo, hi = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
        forms = load_forms([lo[0] - 2, lo[2] - 2, hi[0] + 2, hi[2] + 2])
        identity, target = identity_context(row, triangles, forms)
        foundation = foundation_context(triangles, terrains[row["native"]["sheet"]]["triangles"], target)
        supports = source_supports(row["native"]["sheet"], row["candidate"]["entry"]["modelId"], triangles)
        identity_clear = (
            identity["exactObjectAndCSUID"]
            and identity["officialOverlapOfSmallerFootprint"] >= .75
            and identity["officialFootprintCentroidDistanceM"] <= 3
            and identity["targetCoveredBySourceProjection"] >= .65
        )
        strict_foundation = foundation["completeTerrainTriangles"] == foundation["triangles"] and foundation["fullyBuriedUpwardTriangles"] == 0 and foundation["fullyBuriedAreaFraction"] <= .001
        bounded_foundation = foundation["completeTerrainTriangles"] == foundation["triangles"] and foundation["fullyBuriedAreaFraction"] <= .10 and foundation["minimumGapM"] >= -10
        floating = foundation["minimumGapM"] is not None and foundation["minimumGapM"] > .5
        basic_support_gap = identity["sourceMinimumHKPD"] - identity["targetTopHKPD"]
        retained_basic_support = floating and -1.5 <= basic_support_gap <= 1.0
        suppressions = sorted({
            form["uid"] for form in identity["intersectingForms"]
            if form["uid"] != uid and form["fractionOfForm"] >= .95
            and identity["sourceMaximumHKPD"] >= form["top"] - .25
        })
        reasons = []
        if not identity_clear: reasons.append("source-identity-fit-below-script-policy")
        if floating and not retained_basic_support: reasons.append("native-source-support-not-found")
        elif not floating and not bounded_foundation: reasons.append("below-grade-source-surfaces-exceed-bounded-foundation-policy")
        publication_candidate = not reasons
        result = {
            "uid": uid, "modelId": row["candidate"]["entry"]["modelId"], "name": row["candidate"]["entry"].get("label"),
            "sourceSheet": row["native"]["sheet"], "sourceSHA256": row["candidate"]["entry"]["sha256"],
            "identity": identity, "foundation": foundation, "nativeSourceSupports": supports,
            "identityScriptAccepted": identity_clear, "strictFoundationAccepted": strict_foundation,
            "boundedFoundationAccepted": bounded_foundation, "floatingAboveTerrain": floating,
            "retainsBasicForm": retained_basic_support, "basicSupportGapM": basic_support_gap,
            "suppressesBuildingUids": suppressions,
            "publicationCandidate": publication_candidate, "reasons": reasons,
            "humanStatus": "to-do" if publication_candidate else "held-unknown", "requiresAI": False,
            "requiresUserDecision": False, "needsMoreCompute": False, "scriptedWorkComplete": True,
            "aiCalls": 0, "modelGeometryChanges": 0, "publication": False,
        }
        results.append(result)
        print(json.dumps({"uid": uid, "candidate": publication_candidate, "floating": floating, "retainedBasicSupport": retained_basic_support, "supports": len(supports), "buriedFraction": round(foundation["fullyBuriedAreaFraction"], 5), "reasons": reasons}), flush=True)
    report = {
        "batch": "government-mui-wo-16-20260915", "models": len(results), "rows": results,
        "publicationCandidates": sum(row["publicationCandidate"] for row in results),
        "heldAfterCompleteScriptPass": sum(not row["publicationCandidate"] for row in results),
        "aiCalls": 0, "modelGeometryChanges": 0, "publication": False,
        "inputHashes": {str((BASE / "check-selection.json.gz").relative_to(ROOT)): digest(BASE / "check-selection.json.gz"), str((LOCAL / "geometry.json.gz").relative_to(ROOT)): digest(LOCAL / "geometry.json.gz")},
        "qualification": "All 16 held Mui Wo sources received exact identifier, projected assembly, full-face source-TIN and native support checks. Source geometry remains unchanged.",
    }
    save(OUT / "script-pass-results.json.gz", report)
    save(OUT / "summary.json", {key: value for key, value in report.items() if key != "rows"})


if __name__ == "__main__":
    main()
