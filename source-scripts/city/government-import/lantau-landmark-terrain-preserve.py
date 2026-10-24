"""Preserve current terrain beneath ordinary neighbours of Lantau landmarks."""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import shapely
from shapely.geometry import Polygon

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "docs/astra-city/government-import/government-lantau-landmarks-16-20260916/second-pass"
LOCAL_BASE = HERE / "local/government-lantau-landmarks-16-second-20260916"
CONFIGS = {
    "peaceful-mansion": {
        "uids": ["landsd/108805:0"],
        "retained": ["landsd/176915:0"],
    },
    "disney-hotel-west": {
        "uids": ["landsd/72608:0", "landsd/76821:0"],
        "retained": [],
    },
}

spec = importlib.util.spec_from_file_location("preserve", HERE / "xl-held-terrain-preserve.py")
preserve = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preserve)
b = preserve.b


def main(key):
    config = CONFIGS[key]
    doc = BASE / "third-pass" / ("terrain-" + key)
    local = LOCAL_BASE / ("third-pass-terrain-" + key)
    candidates = preserve.read(doc / "terrain-candidates.json")
    inputs = preserve.read(doc / "neighbour-inputs.json.gz")
    checks = preserve.read(doc / "neighbour-checks.json")
    if key == "disney-hotel-west":
        east = LOCAL_BASE / "third-pass-terrain-disney-hotel-east"
        selection = preserve.read(BASE / "runtime-selection.json.gz")
        selection["rows"] = [
            row for row in selection["rows"] if row["uid"] in set(config["uids"])
        ]
        selection["manifestSHA256"] = preserve.digest(ROOT / "3d-viewer/city/data/manifest.json")
        preserve.save(doc / "selection.json.gz", selection)
        west_catalogue = preserve.read(local / "candidates/catalogue.json")
        east_catalogue = preserve.read(east / "candidates/catalogue.json")
        west_catalogue["models"] = list({model["uid"]: model for model in west_catalogue["models"] + east_catalogue["models"]}.values())
        west_catalogue["counts"]["packedModels"] = len(west_catalogue["models"])
        preserve.save(local / "candidates/catalogue.json", west_catalogue)
        preserve.save(
            local / "candidates/catalogue-index.json",
            {"models": len(west_catalogue["models"]), "catalogues": ["catalogue.json"]},
        )
        east_model = east_catalogue["models"][0]
        shutil.copy2(
            east / "candidates" / east_model["asset"],
            local / "candidates" / east_model["asset"],
        )
        source_forms = preserve.read(local / "source-forms.json")
        source_forms.update(preserve.read(east / "source-forms.json"))
        preserve.save(local / "source-forms.json", source_forms)
    targets = set(config["uids"] + config["retained"])
    blocked = {
        row["uid"]
        for row in checks["rows"]
        if row.get("reasons") and row["uid"] not in targets
    }
    buildings = {row["building"]["uid"]: row["building"] for row in inputs["rows"]}
    existing_preservation = (
        preserve.read(doc / "parent-preservation.json")
        if (doc / "parent-preservation.json").exists()
        else None
    )
    reuse_preservation = not blocked and existing_preservation is not None
    if reuse_preservation:
        blocked = {
            uid
            for patch in existing_preservation["patches"]
            for uid in patch["uids"]
        }
    assert blocked and blocked <= buildings.keys()

    parent = preserve.read(ROOT / "3d-viewer/city/data/terrain.json")
    parent_sampler = b.resolution.terrain.fine.DemSampler(parent, rendered=True)
    proofs = []
    for index, candidate in enumerate(candidates):
        path = ROOT / candidate["path"]
        patch = preserve.read(path)
        if reuse_preservation:
            proofs.extend(existing_preservation["patches"])
            break
        sampler = parent_sampler
        if candidate.get("replaces"):
            old = preserve.read(ROOT / "3d-viewer" / candidate["replaces"]["url"])
            sampler = preserve.ReplacementSampler(old, parent_sampler)
        protected = shapely.union_all([
            Polygon(buildings[uid]["rings"][0], buildings[uid]["rings"][1:]).buffer(
                0.01, join_style="mitre"
            )
            for uid in sorted(blocked)
        ])
        proof = b.patches.preserve_parent_under_projection(
            patch,
            candidate["bounds"],
            protected,
            sampler,
            edge_sampler=parent_sampler,
        )
        patch["nativeMesh"]["source"].pop("numericalCoverageGap", None)
        fills = []
        for _ in range(6):
            missing = b.patches.projected_context(patch, candidate["bounds"])[2]
            if missing.area <= 1e-8:
                break
            try:
                fills.append(
                    b.patches.fill_parent_only_holes(
                        patch,
                        parent,
                        candidate["bounds"],
                        shapely.GeometryCollection(),
                        sampler,
                    )
                )
            except AssertionError as error:
                if str(error) != "no-parent-hole-fill":
                    raise
                break
        remaining = float(b.patches.projected_context(patch, candidate["bounds"])[2].area)
        if remaining > 1e-8:
            area = (candidate["bounds"][2] - candidate["bounds"][0]) * (
                candidate["bounds"][3] - candidate["bounds"][1]
            )
            maximum = max(0.25, area * 1e-3)
            assert remaining <= maximum, ("numerical-parent-gap-too-large", remaining, maximum)
            patch["nativeMesh"]["source"]["numericalCoverageGap"] = {
                "policy": "parent-grid-fallback",
                "measuredAreaM2": remaining,
                "maximumAreaM2": maximum,
                "maximumFraction": 1e-3,
                "qualification": "Bounded clipping slivers use the current parent grid.",
            }
        patch["nativeMesh"]["source"]["finalBoundarySnap"] = b.patches.snap_boundary_to_parent(
            patch, candidate["bounds"], parent_sampler
        )
        preserve.rebind_overlap(patch, path)
        preserve.save(path, patch)
        b.resolution.validate_patch(patch, parent)
        candidate.update(
            sha256=preserve.digest(path), triangles=len(patch["nativeMesh"]["index"]) // 3
        )
        proofs.append(
            {
                "patchIndex": index,
                "patchId": patch["id"],
                "uids": sorted(blocked),
                "proof": proof,
                "parentHoleFill": {"passes": fills, "remainingAreaM2": remaining},
                "sha256": candidate["sha256"],
            }
        )

    preserve.save(
        doc / "parent-preservation.json",
        {
            "patches": proofs,
            "ordinaryForms": len(blocked),
            "policy": "Retain current rendered terrain beneath ordinary neighbouring forms flagged by the before/after regression guard.",
            "aiCalls": 0,
            "modelGeometryChanges": 0,
        },
    )
    if candidates[0].get("replaces"):
        review_path = doc / "native-replacement-review.json"
        assert review_path.exists()
        candidates[0]["nativeReview"] = {
            "path": preserve.rel(review_path),
            "sha256": preserve.digest(review_path),
        }
    preserve.save(doc / "terrain-candidates.json", candidates)
    inputs["patches"] = candidates
    preserve.save(doc / "neighbour-inputs.json.gz", inputs)

    preserve.call([
        "node", str(HERE / "acceptance-metrics.mjs"),
        "--selection", preserve.rel(doc / "selection.json.gz"),
        "--candidates", preserve.rel(local / "candidates"),
        "--terrain-candidates", preserve.rel(doc / "terrain-candidates.json"),
        "--out", preserve.rel(doc / "metrics.json"),
    ])
    preserve.call([
        "node", str(HERE.parent / "building-batch/validate_candidates.mjs"),
        "--candidates", preserve.rel(local / "candidates"),
        "--source-forms", preserve.rel(local / "source-forms.json"),
        "--terrain-candidates", preserve.rel(doc / "terrain-candidates.json"),
        "--out", preserve.rel(doc / "validation.json"),
    ], allowed=(0, 1))
    preserve.call(["node", str(HERE / "check-neighbours.mjs"), preserve.rel(doc) + "/"])
    preserve.call(["node", str(HERE / "check-native-neighbours.mjs"), preserve.rel(doc) + "/"])

    after = preserve.read(doc / "neighbour-checks.json")
    unresolved = sorted({uid for row in after["patches"] for uid in row["blockedBy"]} - targets)
    native = preserve.read(doc / "native-neighbour-checks.json")
    failed_native = sorted(row["uid"] for row in native["rows"] if not row.get("passed"))
    metrics = preserve.read(doc / "metrics.json")
    validation = preserve.read(doc / "validation.json")
    by_metric = {row["uid"]: row for row in metrics["rows"]}
    by_validation = {row["uid"]: row for row in validation["results"]}
    failures = []
    for uid in config["uids"]:
        metric = by_metric[uid]
        check = by_validation[uid]
        if metric.get("error") or not metric.get("sourcePreserved") or metric.get("missingTerrain"):
            failures.append({"uid": uid, "reason": "terrain-or-source-integrity"})
        if metric.get("maxSamplerDelta", 1) > 0.004:
            failures.append({"uid": uid, "reason": "terrain-sampler-disagreement"})
        concerns = set(check.get("concerns", [])) - {
            "sampled-ground-gap-below-model-bottom",
            "sampled-terrain-above-model-bottom",
        }
        if check.get("outcome") == "validation-exception" or concerns:
            failures.append({"uid": uid, "reason": "runtime-validation", "concerns": sorted(concerns), "error": check.get("error")})
    if unresolved:
        failures.append({"uids": unresolved, "reason": "terrain-correction-regresses-neighbours"})
    if failed_native:
        failures.append({"uids": failed_native, "reason": "installed-native-neighbour-regression"})
    result = {
        "key": key,
        "models": len(config["uids"]),
        "passed": not failures,
        "failures": failures,
        "preservedOrdinaryForms": len(blocked),
        "aiCalls": 0,
        "modelGeometryChanges": 0,
        "publication": False,
    }
    preserve.save(doc / "preservation-result.json", result)
    publication_result = {
        "uid": config["uids"][0],
        "passed": result["passed"],
        "patch": candidates[0],
        "reasons": [] if result["passed"] else [failure["reason"] for failure in failures],
        "aiCalls": 0,
        "modelGeometryChanges": 0,
        "publication": False,
    }
    preserve.save(doc / "result.json", publication_result)
    if len(config["uids"]) == 1 and result["passed"]:
        uid = config["uids"][0]
        validation_row = next(row for row in validation["results"] if row["uid"] == uid)
        coarse = set(validation_row.get("concerns", [])) & {
            "sampled-ground-gap-below-model-bottom",
            "sampled-terrain-above-model-bottom",
        }
        if coarse:
            assert len(coarse) == 1
            preserve.save(doc / "contact-resolution.json", {
                "accepted": True,
                "uid": uid,
                "coarseConcern": next(iter(coarse)),
                "metricsSHA256": preserve.digest(doc / "metrics.json"),
                "validationSHA256": preserve.digest(doc / "validation.json"),
                "policy": "Complete unchanged source faces and exact native terrain pass the detailed foundation envelope; the coarse sampled bottom diagnostic is retained as evidence.",
                "aiCalls": 0,
                "modelGeometryChanges": 0,
            })
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    assert len(sys.argv) == 2 and sys.argv[1] in CONFIGS
    main(sys.argv[1])
