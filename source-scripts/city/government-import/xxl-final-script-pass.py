"""Exhaust deterministic geometry checks for every uninstalled XXL source.

This pass is deliberately read-only: it neither edits model geometry nor publishes
assets.  It explains source overhangs, current-form assembly overlap and buried
source-face components so every remaining item has a reproducible terminal script
state before any architectural review is considered.
"""
from collections import defaultdict, deque
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import Polygon, box

sys.path.insert(0, str(Path(__file__).resolve().parent))
spec = importlib.util.spec_from_file_location("xxl_second", Path(__file__).with_name("xxl-second-pass.py"))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)

ROOT, HERE, DOC = s.ROOT, s.HERE, s.DOC
OUT = DOC / "final-script-pass"
INSTALLED_STATES = {"installed", "installed-verified"}


def form_polygon(building):
    rings = building["rings"]
    polygon = Polygon(rings[0], rings[1:])
    if not polygon.is_valid:
        polygon = shapely.make_valid(polygon)
    return polygon


def installed_source_hashes():
    manifest = s.read(ROOT / "3d-viewer/city/data/manifest.json")
    hashes = set()
    for url in manifest.get("officialModelCatalogues", []):
        for model in s.read(ROOT / "3d-viewer" / url).get("models", []):
            hashes.add(model["sha256"])
    return hashes


def remaining_rows():
    original = s.read(s.BASE / "selection.json.gz")["rows"]
    installed = installed_source_hashes()
    rows = [row for row in original if row["sourceSHA256"] not in installed]
    assert len(rows) == 10, f"Expected ten uninstalled XXL sources, found {len(rows)}"
    diagnostics = {row["modelId"]: row for row in s.read(DOC / "diagnostics.json")["rows"]}
    for row in rows:
        candidates = diagnostics[row["modelId"]]["projectionCandidates"]
        if not row.get("uid"):
            assert len(candidates) == 1
            row = row.copy()
            row["uid"] = candidates[0]["uid"]
            row["name"] = candidates[0].get("name") or row.get("name")
        yield row, diagnostics[row["modelId"]]


def load_forms(bounds):
    manifest = s.read(ROOT / "3d-viewer/city/data/manifest.json")
    query = box(*bounds)
    forms = []
    for tile in manifest["tiles"]:
        for building in s.read(ROOT / "3d-viewer" / tile["url"])["buildings"]:
            rings = building.get("rings")
            if not rings:
                continue
            polygon = form_polygon(building)
            if polygon.intersects(query):
                forms.append((building, polygon, tile["url"]))
    return forms


def projection(triangles):
    polygons = shapely.polygons(triangles[:, :, [0, 2]])
    polygons = polygons[shapely.area(polygons) > 1e-10]
    return shapely.union_all(polygons)


def vertical_overlap(triangles, polygon):
    face_polygons = shapely.polygons(triangles[:, :, [0, 2]])
    valid = shapely.area(face_polygons) > 1e-10
    hits = valid & shapely.intersects(face_polygons, polygon)
    if not hits.any():
        return None
    selected = triangles[hits]
    return {
        "sourceFaceCount": int(hits.sum()),
        "sourceYRange": [float(selected[:, :, 1].min()), float(selected[:, :, 1].max())],
    }


def identity_context(row, triangles, forms):
    source_projection = projection(triangles)
    target_building, target_polygon, _ = next(item for item in forms if item[0]["uid"] == row["uid"])
    intersecting = []
    for building, polygon, tile in forms:
        area = float(source_projection.intersection(polygon).area)
        if area <= 0.01:
            continue
        vertical = vertical_overlap(triangles, polygon)
        parent_match = bool(target_building.get("parent") and building.get("parent") == target_building.get("parent"))
        osm_match = bool(set(target_building.get("osmRefs", [])) & set(building.get("osmRefs", [])))
        intersecting.append({
            "uid": building["uid"],
            "name": building.get("name") or None,
            "parent": building.get("parent"),
            "structureType": building.get("structureType"),
            "base": building.get("base"),
            "top": (building.get("base") or 0) + (building.get("height") or 0),
            "intersectionAreaM2": area,
            "fractionOfForm": area / polygon.area if polygon.area else None,
            "sameParent": parent_match,
            "sharedOsmReference": osm_match,
            "tile": tile,
            **(vertical or {}),
        })
    intersecting.sort(key=lambda item: (-item["intersectionAreaM2"], item["uid"]))
    excess = source_projection.difference(target_polygon)
    other_union = shapely.union_all([polygon for building, polygon, _ in forms if building["uid"] != row["uid"]])
    unrelated_union = shapely.union_all([
        polygon for building, polygon, _ in forms
        if building["uid"] != row["uid"]
        and building.get("parent") != target_building.get("parent")
        and not (set(building.get("osmRefs", [])) & set(target_building.get("osmRefs", [])))
    ])
    excess_coordinates = shapely.get_coordinates(excess)
    distance = (
        float(shapely.distance(shapely.points(excess_coordinates), target_polygon).max())
        if len(excess_coordinates)
        else 0.0
    )
    source_model = row["native"]["model"]
    source_candidate = source_model.get("candidate")
    if source_candidate is None:
        candidates = source_model["matching"]["officialCandidates"]
        source_candidate = candidates[0] if len(candidates) == 1 else {}
    exact_source_identity = (
        target_building.get("objectId") == source_candidate.get("objectId")
        and target_building.get("buildingCSUID") == source_candidate.get("buildingCSUID")
    )
    return {
        "target": {k: target_building.get(k) for k in ("uid", "name", "objectId", "buildingCSUID", "parent", "structureType", "base", "height")},
        "exactObjectAndCSUID": exact_source_identity,
        "sourceProjectionAreaM2": float(source_projection.area),
        "targetIntersectionAreaM2": float(source_projection.intersection(target_polygon).area),
        "sourceProjectionInsideTarget": float(source_projection.intersection(target_polygon).area / source_projection.area),
        "targetCoveredBySourceProjection": float(source_projection.intersection(target_polygon).area / target_polygon.area),
        "sourceExcessAreaM2": float(excess.area),
        "sourceExcessFraction": float(excess.area / source_projection.area),
        "sourceExcessMaximumDistanceFromTargetM": distance,
        "sourceExcessCoveredByAnyOtherFormM2": float(excess.intersection(other_union).area),
        "sourceExcessCoveredByUnrelatedFormsM2": float(excess.intersection(unrelated_union).area),
        "intersectingForms": intersecting,
        "sameParentIntersectingForms": sum(item["sameParent"] for item in intersecting if item["uid"] != row["uid"]),
        "unrelatedIntersectingForms": sum(not item["sameParent"] and not item["sharedOsmReference"] for item in intersecting if item["uid"] != row["uid"]),
    }


def native_terrain():
    sources = s.read(DOC / "recovery.json")["sheets"] + s.read(DOC / "adjacent-terrain-results.json")["sources"]
    pieces = [s.context.triangles(ROOT / path) for source in sources for path in source["terrainPaths"]]
    return np.concatenate(pieces)


def connected_components(triangles, selected):
    indices = np.flatnonzero(selected)
    vertex_to_faces = defaultdict(list)
    for local, face in enumerate(triangles[indices]):
        for vertex in face:
            vertex_to_faces[tuple(np.round(vertex, 4))].append(local)
    adjacency = defaultdict(set)
    for face_ids in vertex_to_faces.values():
        for face_id in face_ids:
            adjacency[face_id].update(face_ids)
    components, unseen = [], set(range(len(indices)))
    while unseen:
        start = unseen.pop()
        queue, component = deque([start]), [start]
        while queue:
            current = queue.popleft()
            for neighbour in adjacency[current]:
                if neighbour in unseen:
                    unseen.remove(neighbour)
                    queue.append(neighbour)
                    component.append(neighbour)
        components.append(indices[np.asarray(component)])
    return components


def foundation_context(triangles, terrain, target_polygon):
    lo, hi = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
    native = terrain[
        (terrain[:, :, 0].max(axis=1) >= lo[0] - 1)
        & (terrain[:, :, 0].min(axis=1) <= hi[0] + 1)
        & (terrain[:, :, 2].max(axis=1) >= lo[2] - 1)
        & (terrain[:, :, 2].min(axis=1) <= hi[2] + 1)
    ]
    polygons = shapely.polygons(native[:, :, [0, 2]])
    valid = shapely.area(polygons) > 1e-10
    native, polygons = native[valid], polygons[valid]
    points = np.concatenate([triangles, triangles.mean(axis=1)[:, None, :]], axis=1)
    heights = s.context.shared.samples(points[:, :, [0, 2]].reshape(-1, 2), native, shapely.STRtree(polygons)).reshape(-1, 4)
    gaps = points[:, :, 1] - heights
    complete = np.isfinite(heights).all(axis=1)
    buried = complete & (gaps < -0.5).all(axis=1)
    cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    area = np.linalg.norm(cross, axis=1) / 2
    upward = cross[:, 1] > 0.25 * np.linalg.norm(cross, axis=1)
    components = []
    boundary = target_polygon.boundary
    for component in connected_components(triangles, buried):
        component_triangles = triangles[component]
        component_centres = component_triangles.mean(axis=1)
        centres_2d = shapely.points(component_centres[:, [0, 2]])
        component_area = float(area[component].sum())
        components.append({
            "triangles": len(component),
            "areaM2": component_area,
            "areaFraction": component_area / float(area.sum()),
            "upwardTriangles": int(upward[component].sum()),
            "upwardAreaM2": float(area[component][upward[component]].sum()),
            "gapRangeM": [float(gaps[component].min()), float(gaps[component].max())],
            "yRange": [float(component_triangles[:, :, 1].min()), float(component_triangles[:, :, 1].max())],
            "centroidDistanceToTargetBoundaryM": [float(shapely.distance(centres_2d, boundary).min()), float(shapely.distance(centres_2d, boundary).max())],
            "centroidsInsideTarget": int(shapely.contains(target_polygon, centres_2d).sum()),
        })
    components.sort(key=lambda item: -item["areaM2"])
    return {
        "triangles": len(triangles),
        "completeTerrainTriangles": int(complete.sum()),
        "fullyBuriedTriangles": int(buried.sum()),
        "fullyBuriedAreaM2": float(area[buried].sum()),
        "fullyBuriedAreaFraction": float(area[buried].sum() / area.sum()),
        "fullyBuriedUpwardTriangles": int((buried & upward).sum()),
        "fullyBuriedUpwardAreaM2": float(area[buried & upward].sum()),
        "minimumGapM": float(gaps[complete].min()) if complete.any() else None,
        "components": components,
    }


def route(identity, foundation):
    identity_clear = identity["exactObjectAndCSUID"] and (
        identity["sourceProjectionInsideTarget"] >= 0.98
        or (
            identity["sourceExcessFraction"] <= 0.10
            and identity["sourceExcessCoveredByUnrelatedFormsM2"] <= 1.0
            and identity["sourceExcessMaximumDistanceFromTargetM"] <= 10.0
        )
    )
    foundation_clear = (
        foundation["completeTerrainTriangles"] == foundation["triangles"]
        and foundation["fullyBuriedUpwardTriangles"] == 0
        and foundation["fullyBuriedAreaFraction"] <= 0.001
    )
    reasons = []
    if not identity_clear:
        reasons.append("source-assembly-suppression-map-unresolved")
    if not foundation_clear:
        reasons.append("below-grade-source-surfaces-require-exception-or-terrain-resolution")
    return {
        "identityScriptAccepted": identity_clear,
        "foundationScriptAccepted": foundation_clear,
        "publicationCandidate": not reasons,
        "reasons": reasons,
    }


def main():
    terrain = native_terrain()
    metrics_report = s.read(DOC / "metrics.json")
    runtime = {row["sourceSHA256"]: row for row in metrics_report["rows"]}
    mobile = metrics_report["profiles"]["mobile"]
    results = []
    for source, diagnostic in remaining_rows():
        triangles = s.glb_triangles(source)
        lo, hi = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
        forms = load_forms([lo[0] - 2, lo[2] - 2, hi[0] + 2, hi[2] + 2])
        target = next(form_polygon(building) for building, _, _ in forms if building["uid"] == source["uid"])
        identity = identity_context(source, triangles, forms)
        foundation = foundation_context(triangles, terrain, target)
        decision = route(identity, foundation)
        metric = runtime.get(source["sourceSHA256"])
        if metric:
            runtime_context = {
                "completed": True,
                "sourcePreserved": metric["sourcePreserved"],
                "sourceSHA256": metric["sourceSHA256"],
                "missingTerrain": metric["missingTerrain"],
                "minimumCurrentViewerSurfaceGapM": metric["minSurfaceGap"],
                "minimumCurrentViewerLowRimGapM": metric["minLowGap"],
                "maximumCurrentViewerLowRimGapM": metric["maxLowGap"],
                "maxSamplerDelta": metric["maxSamplerDelta"],
                "budget": metric["budget"],
                "mobileBudgetPassed": all(metric["budget"][key] <= mobile[key] for key in ("triangles", "geometryBytes", "residentBytes")),
            }
        else:
            assert decision["reasons"], "A publication candidate must receive runtime checks"
            asset = source["native"]["model"]["asset"]
            runtime_context = {
                "completed": False,
                "skippedBecause": "earlier identity or foundation gate failed",
                "sourcePreserved": True,
                "sourceSHA256": source["sourceSHA256"],
                "budget": {
                    "triangles": source["triangles"],
                    "geometryBytes": asset["decodedGeometryBytes"],
                    "residentBytes": asset["decodedGeometryBytes"] + asset["glbBytes"],
                },
                "mobileBudgetPassed": source["triangles"] <= mobile["triangles"] and asset["decodedGeometryBytes"] <= mobile["geometryBytes"] and asset["decodedGeometryBytes"] + asset["glbBytes"] <= mobile["residentBytes"],
            }
        result = {
            "modelId": source["modelId"],
            "uid": source["uid"],
            "name": source.get("name") or identity["target"].get("name"),
            "sourceSHA256": source["sourceSHA256"],
            "sourceSheet": source["native"]["sheet"],
            "scriptedWorkComplete": True,
            "humanStatus": "held-unknown" if decision["reasons"] else "to-do",
            "actionableState": "ready-for-publication-gates" if not decision["reasons"] else "held-after-complete-script-pass",
            "requiresAI": False,
            "requiresUserDecision": False,
            "needsMoreCompute": False,
            "identity": identity,
            "foundation": foundation,
            "runtime": runtime_context,
            **decision,
            "aiCalls": 0,
            "modelGeometryChanges": 0,
            "publication": False,
        }
        results.append(result)
        print(json.dumps({
            "uid": result["uid"],
            "identity": decision["identityScriptAccepted"],
            "foundation": decision["foundationScriptAccepted"],
            "publicationCandidate": decision["publicationCandidate"],
            "reasons": decision["reasons"],
        }), flush=True)
    report = {
        "batch": "government-xxl-final-script-pass-20260913",
        "stage": "deterministic-geometry-exhaustion-v1",
        "models": len(results),
        "rows": results,
        "aiCalls": 0,
        "modelGeometryChanges": 0,
        "publication": False,
        "inputHashes": {
            s.rel(DOC / "selection.json.gz"): s.h(DOC / "selection.json.gz"),
            s.rel(DOC / "diagnostics.json"): s.h(DOC / "diagnostics.json"),
            s.rel(DOC / "metrics.json"): s.h(DOC / "metrics.json"),
            s.rel(DOC / "third-pass/source-surface-context.json"): s.h(DOC / "third-pass/source-surface-context.json"),
        },
        "qualification": "All uninstalled XXL sources received exact identifier, projected assembly, vertical neighbour and connected below-grade source-face checks. Results are diagnostic only until normal runtime, neighbour and browser publication gates pass.",
    }
    s.save(OUT / "results.json.gz", report)
    s.save(OUT / "summary.json", {
        "batch": report["batch"],
        "stage": report["stage"],
        "models": len(results),
        "publicationCandidates": sum(row["publicationCandidate"] for row in results),
        "scriptedWorkComplete": sum(row["scriptedWorkComplete"] for row in results),
        "held": sum(bool(row["reasons"]) for row in results),
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    })


if __name__ == "__main__":
    main()
