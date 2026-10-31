"""Diagnose a shared exact-source terrain patch for YHA Mei Ho House XL building."""

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import shapely

from run import ROOT, HERE, read, save, digest

spec = importlib.util.spec_from_file_location("xl_second_bauhinia", HERE / "xl-second-pass.py")
second = importlib.util.module_from_spec(spec)
spec.loader.exec_module(second)
spec = importlib.util.spec_from_file_location("patch_bauhinia", HERE / "native_patch_resolution.py")
patches = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patches)

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "mei-ho-house-terrain-diagnostic-20260925"
LOCAL = HERE / "local/government-xl-mei-ho-house-terrain-20260925"
SHEET = "11-NW-9C"
SOURCE_ROOT = HERE / "local/government-xl-terrain-sources-20260924/sheets"
TERRAIN_SHEETS = (SHEET,)


def sha(path):
    return digest(Path(path).read_bytes())


def rel(path):
    return str(Path(path).resolve().relative_to(ROOT))


def run():
    rows = [row for row in read(BASE / "reconciliation.json.gz")["rows"]
            if row["primaryHold"] == "terrain-contact" and row["sourceSheet"] == SHEET]
    assert len(rows) == 1
    uids = [row["uid"] for row in rows]
    selected = {row["uid"]: row for row in read(BASE / "selection.json.gz")["rows"]}
    first = {row["uid"]: row for row in read(BASE / "results.json.gz")["rows"]}
    assert all(first[uid]["humanStatus"] == "held-unknown" for uid in uids)
    parent = read(ROOT / "3d-viewer/city/data/terrain.json")
    rectangles = [second.resolution.rectangle_for(selected[uid]["native"]["model"]["worldBounds"], parent)
                  for uid in uids]
    cells = [min(row[0] for row in rectangles), min(row[1] for row in rectangles),
             max(row[2] for row in rectangles), max(row[3] for row in rectangles)]
    bounds = second.resolution.extent(cells, parent)
    manifest = read(ROOT / "3d-viewer/city/data/manifest.json")
    overlap = [item["url"] for item in manifest["terrainPatches"]
               if second.resolution.terrain.overlap(cells, read(ROOT / "3d-viewer" / item["url"])["coarseCells"])]
    assert not overlap, overlap

    source_files = []
    fragments = []
    used = []
    for sheet in TERRAIN_SHEETS:
        source_dir = SOURCE_ROOT / sheet
        source = read(source_dir / "original/download.json")
        assert source["directorySHA256"] == read(source_dir / "directory/result.json")["directorySHA256"]
        files = []
        for entry in source["entries"]:
            if entry["name"].startswith("TERRAIN") and entry["name"].endswith((".gltf", ".bin")):
                file = source_dir / "terrain" / entry["name"]
                assert sha(file) == entry["sha256"]
                files.append({"path": rel(file), "sha256": entry["sha256"]})
        source_files.extend(files)
        used.append({"sheet": sheet, "revision": source["revisionDate"],
                     "sourceETag": source["sourceETag"],
                     "directorySHA256": source["directorySHA256"], "sourceFiles": files})
        for file in sorted((source_dir / "terrain").rglob("*.gltf")):
            triangles = second.terrain_triangles(file)
            fragments.append(triangles[(triangles[:, :, 0].max(axis=1) >= bounds[0]) &
                                       (triangles[:, :, 0].min(axis=1) <= bounds[2]) &
                                       (triangles[:, :, 2].max(axis=1) >= bounds[1]) &
                                       (triangles[:, :, 2].min(axis=1) <= bounds[3])])
    native = np.concatenate(fragments)
    low = native[:, :, 1].min(axis=1) < 1.2
    native = native[~low]
    assert len(native) and not low.any()

    model_fragments = []
    input_paths = [HERE / "local/government-xl-remaining-20260923/recovered/geometry-inputs.json",
                   HERE / "local/government-xl-remaining-held-20260923/recovered/geometry-inputs.json"]
    by_uid = {row["uid"]: row for path in input_paths for row in read(path)["rows"]}
    for uid in uids:
        row = selected[uid]
        source_path = Path(by_uid[uid]["candidate"]["path"])
        assert sha(source_path) == row["sourceSHA256"]
        target = second.LOCAL / "assets" / (row["sourceSHA256"] + ".glb.gz")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copyfile(source_path, target)
        assert sha(target) == row["sourceSHA256"]
        model_fragments.append(second.glb_triangles(row))
    model_triangles = np.concatenate(model_fragments)
    model_projection = shapely.union_all(shapely.polygons(model_triangles[:, :, [0, 2]]))
    world = [selected[uid]["native"]["model"]["worldBounds"] for uid in uids]
    core = [min(item[0][0] for item in world) - 1, min(item[0][2] for item in world) - 1,
            max(item[1][0] for item in world) + 1, max(item[1][2] for item in world) + 1]
    validator = second.resolution.validate_patch
    second.resolution.validate_patch = lambda candidate, parent_terrain: None
    try:
        patch = second.resolution.make_patch({"uids": uids, "cells": cells}, parent, native, used,
                                             native_core=core, terrain_triangle_budget=100000)
    finally:
        second.resolution.validate_patch = validator
    LOCAL.mkdir(parents=True, exist_ok=True)
    path = LOCAL / (patch["id"] + ".json")
    save(path, patch)
    original_overlap = patches.projected_context(patch, bounds)[3]
    sampler = second.resolution.terrain.fine.DemSampler(parent, rendered=True)
    protected_gap = patches.projected_context(patch, bounds)[2].intersection(model_projection)
    if protected_gap.area > 1e-6:
        fill = patches.fill_narrow_source_seam(patch, bounds, model_projection, sampler,
                                               tolerance=.02)
    else:
        fill = patches.fill_parent_only_holes(patch, parent, bounds, model_projection, sampler)
    remaining = float(patches.projected_context(patch, bounds)[2].area)
    if remaining > 1e-8:
        maximum = max(.25, (bounds[2] - bounds[0]) * (bounds[3] - bounds[1]) * 1e-3)
        assert remaining <= maximum, ("numerical-parent-gap-too-large", remaining, maximum)
        patch["nativeMesh"]["source"]["numericalCoverageGap"] = {
            "policy": "parent-grid-fallback", "measuredAreaM2": remaining,
            "maximumAreaM2": maximum, "maximumFraction": 1e-3}
    patch["nativeMesh"]["source"]["finalBoundarySnap"] = patches.snap_boundary_to_parent(patch, bounds, sampler)
    final_overlap = patches.projected_context(patch, bounds)[3]
    overlap_delta = final_overlap - original_overlap
    assert abs(overlap_delta) <= .001, ("source-seam-numerical-overlap-too-large", overlap_delta)
    patch["nativeMesh"]["source"]["sourceSeamNumericalOverlap"] = {
        "originalExcessM2": original_overlap, "finalExcessM2": final_overlap,
        "differenceM2": overlap_delta, "maximumDifferenceM2": .001,
        "policy": "Float32 source-edge seam repair may change projected overlap by at most 0.001 m2; final overlap receives its own independent highest-surface audit."}
    if final_overlap > 1e-8:
        save(path, patch)
        patches.approve_original_overlap(patch, path, DOC / "native-overlap.json", source_files)
        audit = read(DOC / "native-overlap.json")
        audit["originalSourceExcessM2"] = original_overlap
        audit["seamNumericalDifferenceM2"] = overlap_delta
        audit["policy"] = "Exact original source facets plus a bounded 2 cm source-edge sheet seam; highest audited surface is retained."
        save(DOC / "native-overlap.json", audit)
        patch["nativeMesh"]["sourceOverlap"]["evidenceSHA256"] = sha(DOC / "native-overlap.json")
        patches.finalize_overlap_evidence(patch, DOC / "native-overlap.json")
    save(path, patch)
    validator(patch, parent)
    save(path, patch)
    result = {"uids": uids, "sourceSheet": SHEET, "terrainSheets": list(TERRAIN_SHEETS),
              "sourceDirectorySHA256s": {row["sheet"]: row["directorySHA256"] for row in used},
              "cells": cells, "sourceTerrainTriangles": len(native), "modelTriangles": len(model_triangles),
              "patchTriangles": len(patch["nativeMesh"]["index"]) // 3,
              "parentHoleFill": fill, "patchPath": rel(path), "patchSHA256": sha(path),
              "state": "terrain-patch-validated-awaiting-model-and-neighbour-checks",
              "aiCalls": 0, "modelGeometryChanges": 0, "publication": False}
    save(DOC / "result.json", result)
    print(json.dumps({"state": result["state"], "models": len(uids),
                      "patchTriangles": result["patchTriangles"]}), flush=True)


if __name__ == "__main__":
    run()
