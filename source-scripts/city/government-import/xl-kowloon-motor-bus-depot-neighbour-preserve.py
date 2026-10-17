"""Retain parent terrain under two disjoint depot neighbours without model edits."""

import importlib.util
import json
from pathlib import Path

import shapely
from shapely.geometry import Polygon

from run import ROOT, HERE, read, save, digest


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


second = module("xl_second_depot_protect", HERE / "xl-second-pass.py")
patches = module("patch_depot_protect", HERE / "native_patch_resolution.py")
DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/kowloon-motor-bus-depot-terrain-diagnostic-20260927"
BASE = DOC.parent
UID = "landsd/207445:0"
NEIGHBOURS = ("landsd/214035:0", "landsd/310873:0")


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def run():
    result_path = DOC / "result.json"
    result = read(result_path)
    assert result["uids"] == [UID] and "parentPreservation" not in result
    original_path = ROOT / result["patchPath"]
    assert digest(original_path.read_bytes()) == result["patchSHA256"]
    patch = read(original_path)
    parent = read(ROOT / "3d-viewer/city/data/terrain.json")
    bounds = second.resolution.extent(result["cells"], parent)
    selection = next(row for row in read(BASE / "selection.json.gz")["rows"] if row["uid"] == UID)
    triangles = second.glb_triangles(selection)
    model_projection = shapely.union_all(shapely.polygons(triangles[:, :, [0, 2]]))
    neighbour_rows = read(DOC / "neighbour-inputs.json.gz")["rows"]
    by_uid = {row["building"]["uid"]: row["building"] for row in neighbour_rows}
    protected = shapely.union_all([
        Polygon(by_uid[uid]["rings"][0], by_uid[uid]["rings"][1:]).buffer(.01, join_style="mitre")
        for uid in NEIGHBOURS
    ])
    distances = {uid: Polygon(by_uid[uid]["rings"][0], by_uid[uid]["rings"][1:]).distance(model_projection)
                 for uid in NEIGHBOURS}
    assert min(distances.values()) > 70
    assert protected.intersection(model_projection).area < 1e-8
    sampler = second.resolution.terrain.fine.DemSampler(parent, rendered=True)
    proof = patches.preserve_parent_under_projection(patch, bounds, protected, sampler)
    proof["uids"] = list(NEIGHBOURS)
    proof["boundaryFringeM"] = .01
    proof["distancesFromModelM"] = distances
    fill = patches.fill_parent_only_holes(patch, parent, bounds, model_projection, sampler)
    boundary = patches.snap_boundary_to_parent(patch, bounds, sampler)
    patch["nativeMesh"]["source"]["finalBoundarySnap"] = boundary
    second.resolution.validate_patch(patch, parent)
    target = original_path.parent / "neighbour-protected" / original_path.name
    save(target, patch)
    assert read(target) == patch
    save(DOC / "neighbour-preservation.json", {
        "uid": UID, "protectedNeighbours": list(NEIGHBOURS),
        "originalPatch": ref(original_path), "finalPatch": ref(target),
        "parentPreservation": proof, "parentHoleFill": fill,
        "sourceProjectionIntersectionM2": float(protected.intersection(model_projection).area),
        "modelGeometryChanges": 0, "aiCalls": 0, "publication": False,
    })
    result.update(patchPath=str(target.relative_to(ROOT)), patchSHA256=digest(target.read_bytes()),
                  patchTriangles=len(patch["nativeMesh"]["index"]) // 3,
                  parentPreservation=ref(DOC / "neighbour-preservation.json"))
    save(result_path, result)
    print(json.dumps({"protectedNeighbours": len(NEIGHBOURS),
                      "patchTriangles": result["patchTriangles"], "aiCalls": 0}), flush=True)


if __name__ == "__main__":
    run()
