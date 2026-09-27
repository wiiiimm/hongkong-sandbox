"""Evaluate retaining current terrain beneath disjoint XL neighbour forms.

The original government model and its two-sheet TIN remain untouched. Candidate
patches live in local/ until their contact and neighbour checks pass.
"""

import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import shapely
from shapely.geometry import Polygon

from run import ROOT, HERE, read, save, digest


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


second = module("xl_second_mask_eval", HERE / "xl-second-pass.py")
patches = module("xl_patch_mask_eval", HERE / "native_patch_resolution.py")
BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
LOCAL = HERE / "local/government-xl-disjoint-mask-eval-20260927"
SITES = (("diocesan-girls-school", "landsd/257352:0"),
         ("yoho-mall-ii", "landsd/273672:0"))


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def run():
    selection = {row["uid"]: row for row in read(BASE / "selection.json.gz")["rows"]}
    parent = read(ROOT / "3d-viewer/city/data/terrain.json")
    rows = []
    for name, uid in SITES:
        doc = BASE / f"{name}-terrain-diagnostic-20260927"
        original_result = read(doc / "result.json")
        original_path = ROOT / original_result["patchPath"]
        assert ref(original_path)["sha256"] == original_result["patchSHA256"]
        original = read(original_path)
        bounds = second.resolution.extent(original_result["cells"], parent)
        triangles = second.glb_triangles(selection[uid])
        model_projection = shapely.union_all(shapely.polygons(triangles[:, :, [0, 2]]))
        neighbours = read(doc / "neighbour-inputs.json.gz")
        by_uid = {row["building"]["uid"]: row["building"] for row in neighbours["rows"]}
        blocked = sorted({item for patch in read(doc / "neighbour-checks.json")["patches"]
                          for item in patch["blockedBy"]})
        disjoint, shared, forms = [], [], []
        for item in blocked:
            building = by_uid[item]
            footprint = Polygon(building["rings"][0], building["rings"][1:])
            intersection = footprint.intersection(model_projection).area
            if intersection < 1e-8 and footprint.distance(model_projection) > 1:
                disjoint.append(item)
                forms.append(footprint.buffer(.01, join_style="mitre"))
            else:
                shared.append({"uid": item, "targetOverlapM2": intersection})
        assert disjoint and shared
        protected = shapely.union_all(forms)
        assert protected.intersection(model_projection).area < 1e-8
        candidate = read(original_path)
        sampler = second.resolution.terrain.fine.DemSampler(parent, rendered=True)
        proof = patches.preserve_parent_under_projection(candidate, bounds, protected, sampler)
        proof.update(uids=disjoint, boundaryFringeM=.01)
        fill = patches.fill_parent_only_holes(candidate, parent, bounds, model_projection, sampler)
        candidate["nativeMesh"]["source"]["finalBoundarySnap"] = patches.snap_boundary_to_parent(candidate, bounds, sampler)
        excess = patches.projected_context(candidate, bounds)[3]
        assert 0 <= excess <= .25, (uid, excess)
        # The original source-overlap hash binds the unmasked TIN and cannot
        # certify this candidate. The clipped Float32 surface is independently
        # bounded here; the viewer samples its highest surface.
        candidate["nativeMesh"].pop("sourceOverlap", None)
        candidate["nativeMesh"]["source"]["numericalProjectionOverlap"] = {
            "policy": "highest-float32-surface", "measuredAreaM2": excess,
            "maximumAreaM2": .25,
            "cause": "Float32 source/parent seam after disjoint neighbour preservation",
        }
        print(json.dumps({"uid": uid, "candidateProjectedExcessM2":
                          excess}), flush=True)
        second.resolution.validate_patch(candidate, parent)
        folder = LOCAL / name
        folder.mkdir(parents=True, exist_ok=True)
        candidate_path = folder / original_path.name
        save(candidate_path, candidate)
        test_inputs = dict(neighbours)
        test_inputs["patches"] = [{**patch, **ref(candidate_path)} for patch in neighbours["patches"]]
        save(folder / "neighbour-inputs.json.gz", test_inputs)
        subprocess.run(["node", str(HERE / "check-neighbours.mjs"),
                        str(folder.relative_to(ROOT)) + "/"], cwd=ROOT, check=True)
        checks = read(folder / "neighbour-checks.json")
        still_blocked = sorted({item for patch in checks["patches"] for item in patch["blockedBy"]})
        row = {"uid": uid, "site": name, "originalPatch": ref(original_path),
               "candidatePatch": ref(candidate_path), "disjointProtectedUids": disjoint,
               "sharedFootprintUids": shared, "parentPreservation": proof,
               "parentHoleFill": fill, "remainingBlockedUids": still_blocked,
               "numericalProjectedOverlapM2": excess,
               "neighbourCheck": ref(folder / "neighbour-checks.json"),
               "aiCalls": 0, "modelGeometryChanges": 0, "publication": False}
        rows.append(row)
        print(json.dumps({"uid": uid, "protected": len(disjoint),
                          "remainingBlocked": still_blocked}), flush=True)
        save(BASE / "disjoint-neighbour-mask-eval-20260927.json",
             {"stage": "disjoint-parent-terrain-mask-evaluation-v1", "rows": rows,
              "aiCalls": 0, "modelGeometryChanges": 0, "publication": False})


if __name__ == "__main__":
    run()
