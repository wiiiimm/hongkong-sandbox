"""Test preserving current terrain beneath the shared-footprint XL neighbours.

This writes only local candidate patches and diagnostic reports. Passing the
neighbour guard is insufficient: the unchanged government model must also
retain valid full-triangle terrain contact before any publication.
"""

import importlib.util
import json
import subprocess

import shapely
from shapely.geometry import Polygon

from run import ROOT, HERE, read, save, digest


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


second = module("xl_second_shared_eval", HERE / "xl-second-pass.py")
patches = module("xl_patch_shared_eval", HERE / "native_patch_resolution.py")
BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
SOURCE = BASE / "disjoint-neighbour-mask-eval-20260927.json"
LOCAL = HERE / "local/government-xl-shared-mask-eval-20260927"


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def run():
    parent = read(ROOT / "3d-viewer/city/data/terrain.json")
    rows = []
    for previous in read(SOURCE)["rows"]:
        uid, name = previous["uid"], previous["site"]
        doc = BASE / f"{name}-terrain-diagnostic-20260927"
        path = ROOT / previous["candidatePatch"]["path"]
        assert ref(path)["sha256"] == previous["candidatePatch"]["sha256"]
        original_result = read(doc / "result.json")
        bounds = second.resolution.extent(original_result["cells"], parent)
        neighbours = read(doc / "neighbour-inputs.json.gz")
        by_uid = {row["building"]["uid"]: row["building"] for row in neighbours["rows"]}
        shared = [row["uid"] for row in previous["sharedFootprintUids"]]
        protected = shapely.union_all([
            Polygon(by_uid[item]["rings"][0], by_uid[item]["rings"][1:]).buffer(.01, join_style="mitre")
            for item in shared
        ])
        candidate = read(path)
        sampler = second.resolution.terrain.fine.DemSampler(parent, rendered=True)
        proof = patches.preserve_parent_under_projection(candidate, bounds, protected, sampler)
        proof.update(uids=shared, boundaryFringeM=.01)
        candidate["nativeMesh"]["source"]["finalBoundarySnap"] = patches.snap_boundary_to_parent(candidate, bounds, sampler)
        _, _, missing, excess = patches.projected_context(candidate, bounds)
        maximum_gap = max(.25, (bounds[2] - bounds[0]) * (bounds[3] - bounds[1]) * 1e-3)
        assert missing.area <= maximum_gap, (uid, missing.area, maximum_gap)
        candidate["nativeMesh"]["source"]["numericalCoverageGap"] = {
            "policy": "parent-grid-fallback", "measuredAreaM2": missing.area,
            "maximumAreaM2": maximum_gap, "maximumFraction": 1e-3,
        }
        assert 0 <= excess <= .25, (uid, excess)
        candidate["nativeMesh"].pop("sourceOverlap", None)
        candidate["nativeMesh"]["source"]["numericalProjectionOverlap"] = {
            "policy": "highest-float32-surface", "measuredAreaM2": excess,
            "maximumAreaM2": .25,
            "cause": "Float32 source/parent seam after shared neighbour preservation",
        }
        second.resolution.validate_patch(candidate, parent)
        folder = LOCAL / name
        folder.mkdir(parents=True, exist_ok=True)
        candidate_path = folder / path.name
        save(candidate_path, candidate)
        test_inputs = dict(neighbours)
        test_inputs["patches"] = [{**patch, **ref(candidate_path)} for patch in neighbours["patches"]]
        save(folder / "neighbour-inputs.json.gz", test_inputs)
        subprocess.run(["node", str(HERE / "check-neighbours.mjs"),
                        str(folder.relative_to(ROOT)) + "/"], cwd=ROOT, check=True)
        checks = read(folder / "neighbour-checks.json")
        blocked = sorted({item for patch in checks["patches"] for item in patch["blockedBy"]})
        patch_row = {**neighbours["patches"][0], **ref(candidate_path)}
        save(folder / "terrain-candidates.json", [patch_row])
        source_assets = HERE / "local" / f"government-xl-{name}-terrain-20260927" / "candidates"
        subprocess.run(["node", str(HERE / "acceptance-metrics.mjs"),
                        "--selection", str((doc / "selection.json.gz").relative_to(ROOT)),
                        "--candidates", str(source_assets.relative_to(ROOT)),
                        "--terrain-candidates", str((folder / "terrain-candidates.json").relative_to(ROOT)),
                        "--out", str((folder / "metrics.json").relative_to(ROOT))], cwd=ROOT, check=True)
        metrics = read(folder / "metrics.json")["rows"][0]
        row = {"uid": uid, "site": name, "inputPatch": previous["candidatePatch"],
               "candidatePatch": ref(candidate_path), "sharedProtectedUids": shared,
               "parentPreservation": proof, "numericalProjectedOverlapM2": excess,
               "numericalCoverageGapM2": missing.area,
               "remainingBlockedUids": blocked,
               "minLowRimGapM": metrics["minLowGap"],
               "maxLowRimGapM": metrics["maxLowGap"],
               "missingTerrainSamples": metrics["missingTerrain"],
               "sourcePreserved": metrics["sourcePreserved"],
               "neighbourCheck": ref(folder / "neighbour-checks.json"),
               "metrics": ref(folder / "metrics.json"),
               "aiCalls": 0, "modelGeometryChanges": 0, "publication": False}
        rows.append(row)
        print(json.dumps({"uid": uid, "remainingBlocked": blocked,
                          "minLowRimGapM": metrics["minLowGap"],
                          "maxLowRimGapM": metrics["maxLowGap"]}), flush=True)
        save(BASE / "shared-neighbour-mask-eval-20260927.json",
             {"stage": "shared-parent-terrain-mask-evaluation-v1", "rows": rows,
              "aiCalls": 0, "modelGeometryChanges": 0, "publication": False})


if __name__ == "__main__":
    run()
