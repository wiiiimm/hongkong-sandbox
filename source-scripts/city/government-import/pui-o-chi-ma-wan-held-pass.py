"""Resolve the 64 Pui O / Chi Ma Wan holds with stronger compute-only checks."""
from __future__ import annotations

import collections
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE_BATCH = "government-pui-o-chi-ma-wan-362-20260916"
BATCH = "government-pui-o-chi-ma-wan-held-64-20260917"
DOC = ROOT / "docs/astra-city/government-import" / SOURCE_BATCH / "held-64"
SOURCE_DOC = ROOT / "docs/astra-city/government-import" / SOURCE_BATCH
SOURCE_LOCAL = HERE / "local" / SOURCE_BATCH
LOCAL = HERE / "local" / BATCH
STAGE = HERE / "accepted" / BATCH
GOOD_TO_GO_UIDS = {"landsd/195308:0", "landsd/196549:0"}
SHORELINE_UID = "landsd/74941:0"

sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("exact", HERE / "pui-o-chi-ma-wan-exact-pass.py")
exact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exact)


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == ".gz" else raw)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return str(Path(path).relative_to(ROOT))


def call(args, allowed=(0,)):
    result = subprocess.run(args, cwd=ROOT)
    assert result.returncode in allowed, (args, result.returncode)


def current_installed_uids():
    manifest = read(ROOT / "3d-viewer/city/data/manifest.json")
    return {
        model["uid"]
        for url in manifest["officialModelCatalogues"]
        for model in read(ROOT / "3d-viewer" / url)["models"]
    }


def stitched_foundations(uids, geometries):
    terrain_parts = []
    for decoded in sorted((SOURCE_LOCAL / "source-terrain").glob("*/decoded")):
        files = sorted(decoded.rglob("*.gltf"))
        terrain_parts.extend(exact.context.triangles(path) for path in files)
    terrain = np.concatenate(terrain_parts)
    rows = {}
    for uid in sorted(uids):
        rows[uid] = exact.foundation_context(exact.geometry_triangles(geometries[uid]), terrain)
    return rows, len(terrain)


def main():
    terminal = read(SOURCE_DOC / "terminal-states.json")
    held_rows = {row["uid"]: row for row in terminal["heldRows"]}
    assert len(held_rows) == 64
    assert not current_installed_uids() & set(held_rows)
    selection = read(SOURCE_DOC / "check-selection.json.gz")
    selected = {row["uid"]: row for row in selection["rows"]}
    exact_rows = {row["uid"]: row for row in read(SOURCE_DOC / "exact-pass-results.json.gz")["rows"]}
    geometries = {row["uid"]: row for row in read(SOURCE_LOCAL / "geometry.json.gz")["rows"]}

    seam_uids = {
        uid for uid, row in held_rows.items()
        if "source-terrain-incomplete" in row["reasons"]
    }
    stitched, terrain_triangles = stitched_foundations(seam_uids, geometries)
    stitched_rows = []
    for uid in sorted(seam_uids):
        foundation = stitched[uid]
        assert foundation["completeTerrainTriangles"] == foundation["triangles"]
        assert foundation["fullyBuriedUpwardTriangles"] == 0
        assert foundation["minimumGapM"] >= -10
        stitched_rows.append({"uid": uid, **foundation})
    save(DOC / "stitched-terrain-proof.json", {
        "policy": "Use every verified adjacent Lands Department terrain sheet from the same frozen recovery set.",
        "sourceTerrainSHA256": digest(SOURCE_DOC / "source-terrain.json"),
        "terrainTriangles": terrain_triangles,
        "rows": stitched_rows,
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    })

    below = exact_rows["landsd/196549:0"]
    identity = below["identity"]
    foundation = below["foundation"]
    assert identity["exactObjectAndCSUID"]
    assert identity["sourceMaximumHKPD"] < identity["targetTopHKPD"] - 5
    assert identity["sourceMaximumHKPD"] < selected["landsd/196549:0"]["source"]["building"]["base"]
    assert foundation["fullyBuriedAreaFraction"] > 0.5
    assert foundation["fullyBuriedUpwardTriangles"] > 0
    prior_metrics = {row["uid"]: row for row in read(SOURCE_DOC / "exact-metrics.json")["rows"]}
    substation = prior_metrics["landsd/195308:0"]
    assert substation["missingTerrain"] == 0
    assert substation["checks"] == substation["samplerDisagreement"]["count"]
    assert substation["samplerDisagreement"]["minDrawnClearance"] < -0.5
    assert substation["maxLowGap"] < -0.5
    save(DOC / "good-to-go-proof.json", {
        "rows": [
            {
                "uid": "landsd/196549:0",
                "decision": "good-to-go",
                "reason": (
                    "The unchanged government source is wholly below the current mapped building base and mostly below "
                    "same-revision terrain, including an upward face. It cannot add visible detail; retain the current form."
                ),
                "sourceSHA256": below["sourceSHA256"],
                "sourceMaximumHKPD": identity["sourceMaximumHKPD"],
                "currentBuildingBaseHKPD": selected["landsd/196549:0"]["source"]["building"]["base"],
                "currentBuildingTopHKPD": identity["targetTopHKPD"],
                "fullyBuriedAreaFraction": foundation["fullyBuriedAreaFraction"],
                "fullyBuriedUpwardTriangles": foundation["fullyBuriedUpwardTriangles"],
            },
            {
                "uid": "landsd/195308:0",
                "decision": "good-to-go",
                "reason": (
                    "Every unchanged government source sample is below the current rendered terrain. The highest low-rim "
                    "clearance remains below -0.5m, so the source would add no visible detail; retain the current form."
                ),
                "sourceSHA256": substation["sourceSHA256"],
                "checks": substation["checks"],
                "missingTerrain": substation["missingTerrain"],
                "minimumDrawnClearanceM": substation["samplerDisagreement"]["minDrawnClearance"],
                "maximumLowRimClearanceM": substation["maxLowGap"],
            },
        ],
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    })

    install_uids = set(held_rows) - GOOD_TO_GO_UIDS
    template = read(ROOT / "3d-viewer/city/data/official-models/government-pui-o-chi-ma-wan-compute-20260916/catalogue.json")
    models, runtime_rows, browser_forms = [], [], []
    assembly_rows = []
    for uid in sorted(install_uids):
        row = selected[uid]
        proof = exact_rows[uid]
        identity = proof["identity"]
        assert identity["exactObjectAndCSUID"]
        assert identity["officialOverlapOfSmallerFootprint"] >= 0.5
        assert identity["officialFootprintCentroidDistanceM"] <= 6
        assert max(identity["targetCoveredBySourceProjection"], identity["sourceProjectionInsideTarget"]) >= 0.5
        if uid not in seam_uids:
            foundation = proof["foundation"]
            assert foundation["completeTerrainTriangles"] == foundation["triangles"]
            assert foundation["fullyBuriedUpwardTriangles"] == 0

        entry = dict(row["candidate"]["entry"])
        reasons = held_rows[uid]["reasons"]
        retain_basic = bool(
            "native-source-support-not-found" in reasons
            or "source-identity-fit-below-script-policy" in reasons
            or identity["targetCoveredBySourceProjection"] < 0.95
            or identity["sourceProjectionInsideTarget"] < 0.65
        )
        suppressions = proof["suppressesBuildingUids"]
        entry.update(
            priority="detail",
            placementReviewed=True,
            sourceIdentityReviewed=True,
            identityReviewApproved=True,
            publicationApproved=False,
            proceduralWindows=False,
            placementReview=(
                "Exact unchanged Lands Department object and Building CSUID. Official footprint match, projected "
                "intersection, all-sheet source terrain and current runtime terrain were checked deterministically. "
                + ("The mapped basic form remains as the verified partial/elevated component support. " if retain_basic else "")
                + "No AI review, remodelling, simplification or model geometry edit."
            ),
        )
        if retain_basic:
            entry["retainsBasicForm"] = True
        if suppressions:
            entry["suppressesBuildingUids"] = suppressions
        source_asset = Path(row["candidate"]["path"])
        target_asset = STAGE / entry["asset"]
        target_asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_asset, target_asset)
        assert digest(target_asset) == entry["sha256"]
        runtime = json.loads(json.dumps(row))
        runtime["candidate"]["path"] = str(target_asset)
        runtime["candidate"]["entry"] = entry
        runtime_rows.append(runtime)
        form = dict(row["source"]["building"])
        form["tile"] = Path(row["source"]["tile"]).stem
        browser_forms.append(form)
        models.append(entry)
        assembly_rows.append({
            "uid": uid,
            "originalHoldReasons": reasons,
            "retainsBasicForm": retain_basic,
            "suppressesBuildingUids": suppressions,
            "officialOverlapOfSmallerFootprint": identity["officialOverlapOfSmallerFootprint"],
            "officialFootprintCentroidDistanceM": identity["officialFootprintCentroidDistanceM"],
            "targetCoveredBySourceProjection": identity["targetCoveredBySourceProjection"],
            "sourceProjectionInsideTarget": identity["sourceProjectionInsideTarget"],
            "sourceSHA256": entry["sha256"],
        })

    template.update(
        area="Pui O / Chi Ma Wan held government sources · compute-only second pass",
        loadingPolicy="Unchanged sources accepted after stitched-terrain, retained-support, runtime and browser checks",
        counts={"packedModels": len(models)},
        models=models,
    )
    save(STAGE / "catalogue.json", template)
    save(STAGE / "catalogue-index.json", {"models": len(models), "catalogues": ["catalogue.json"]})
    save(STAGE / "source-forms.json", browser_forms)
    save(LOCAL / "source-forms.json", {row["uid"]: row["source"] for row in runtime_rows})
    save(DOC / "assembly-proof.json", {
        "policy": (
            "Require exact object/CSUID, at least 50% official smaller-footprint overlap, centroid within 6m and "
            "at least 50% projected coverage in either direction. Retain the mapped basic form for every partial, "
            "oversized or elevated component. Suppress only forms already proven wholly covered by the exact source."
        ),
        "rows": assembly_rows,
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    })
    runtime_selection = dict(selection)
    runtime_selection.update(
        batch=BATCH,
        rows=runtime_rows,
        manifestSHA256=digest(ROOT / "3d-viewer/city/data/manifest.json"),
        aiCalls=0,
    )
    save(DOC / "selection.json.gz", runtime_selection)
    save(DOC / "terrain-candidates.json", [])
    call([
        "node", str(HERE / "acceptance-metrics.mjs"),
        "--selection", relative(DOC / "selection.json.gz"),
        "--candidates", relative(STAGE),
        "--terrain-candidates", relative(DOC / "terrain-candidates.json"),
        "--out", relative(DOC / "metrics.json"),
    ])
    call([
        "node", str(HERE.parent / "building-batch/validate_candidates.mjs"),
        "--candidates", relative(STAGE),
        "--source-forms", relative(LOCAL / "source-forms.json"),
        "--out", relative(DOC / "validation.json"),
    ], allowed=(0, 1))
    metrics = read(DOC / "metrics.json")
    validation = read(DOC / "validation.json")
    shoreline_metric = next(row for row in metrics["rows"] if row["uid"] == SHORELINE_UID)
    shoreline_entry = next(row for row in assembly_rows if row["uid"] == SHORELINE_UID)
    shoreline_patch_path = ROOT / "3d-viewer/city/data/government-pui-chi-006.json"
    shoreline_patch = read(shoreline_patch_path)
    shoreline_bounds = next(model for model in models if model["uid"] == SHORELINE_UID)["worldBounds"]
    georef = shoreline_patch["meta"]["georef"]
    cols = range(
        max(0, int(np.floor((shoreline_bounds[0][0] + 834500 - georef["bE"]) / georef["aE"]))),
        min(shoreline_patch["w"], int(np.ceil((shoreline_bounds[1][0] + 834500 - georef["bE"]) / georef["aE"])) + 1),
    )
    grid_rows = range(
        max(0, int(np.floor((shoreline_bounds[0][2] - 816500 + georef["bN"]) / -georef["aN"]))),
        min(shoreline_patch["h"], int(np.ceil((shoreline_bounds[1][2] - 816500 + georef["bN"]) / -georef["aN"])) + 1),
    )
    samples = [
        {
            "col": col,
            "row": row,
            "elevation": shoreline_patch["elev"][row * shoreline_patch["w"] + col],
            "renderedElevation": shoreline_patch["renderedElev"][row * shoreline_patch["w"] + col],
        }
        for row in grid_rows for col in cols
    ]
    assert shoreline_entry["retainsBasicForm"]
    assert shoreline_metric["missingDrawnTerrain"]["count"] > 0
    assert shoreline_metric["missingDrawnTerrain"]["minRuntimeClearance"] >= 0
    assert any(sample["elevation"] == 0 and sample["renderedElevation"] < 0 for sample in samples)
    save(DOC / "shoreline-support-proof.json", {
        "uid": SHORELINE_UID,
        "accepted": True,
        "policy": (
            "The exact source crosses the shoreline. Water cells intentionally have no rendered terrain surface; the "
            "runtime sampler still places the unchanged source above terrain and the mapped basic support remains visible."
        ),
        "terrainPatch": "city/data/government-pui-chi-006.json",
        "terrainPatchSHA256": digest(shoreline_patch_path),
        "gridSamples": samples,
        "missingDrawnChecks": shoreline_metric["missingDrawnTerrain"]["count"],
        "minimumRuntimeClearanceM": shoreline_metric["missingDrawnTerrain"]["minRuntimeClearance"],
        "retainsBasicForm": True,
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    })
    failures = []
    for metric in metrics["rows"]:
        shoreline_exception = metric["uid"] == SHORELINE_UID
        if metric.get("error") or not metric.get("sourcePreserved") or (metric.get("missingTerrain") and not shoreline_exception):
            failures.append({"uid": metric["uid"], "reason": "source-integrity-or-current-terrain"})
        if metric.get("maxSamplerDelta", 0) > 0.004 and not shoreline_exception:
            failures.append({"uid": metric["uid"], "reason": "terrain-sampler-disagreement"})
        if any(metric["budget"][key] > metrics["profiles"]["mobile"][key] for key in ("triangles", "geometryBytes", "residentBytes")):
            failures.append({"uid": metric["uid"], "reason": "mobile-runtime-budget"})
    allowed = {"sampled-ground-gap-below-model-bottom", "sampled-terrain-above-model-bottom", "sampled-highest-roof-below-terrain"}
    for result in validation["results"]:
        shoreline_exception = (
            result["uid"] == SHORELINE_UID
            and result.get("error") == "Expected a rendered terrain surface"
        )
        if result["outcome"] == "validation-exception" and not shoreline_exception:
            failures.append({"uid": result["uid"], "reason": result["error"]})
        for concern in result.get("concerns", []):
            if concern not in allowed:
                failures.append({"uid": result["uid"], "reason": concern})
    result = {
        "batch": BATCH,
        "models": len(models),
        "goodToGo": sorted(GOOD_TO_GO_UIDS),
        "failures": failures,
        "metricsSHA256": digest(DOC / "metrics.json"),
        "validationSHA256": digest(DOC / "validation.json"),
        "stitchedTerrainSHA256": digest(DOC / "stitched-terrain-proof.json"),
        "assemblyProofSHA256": digest(DOC / "assembly-proof.json"),
        "aiCalls": 0,
        "modelGeometryChanges": 0,
        "publication": False,
    }
    save(DOC / "result.json", result)
    destination = f"city/data/official-models/{BATCH}/catalogue.json"
    save(STAGE / "plan.json", {"areas": [{
        "area": template["area"],
        "catalogue": relative(STAGE / "catalogue.json"),
        "destination": destination,
    }]})
    browser_uids = sorted(install_uids)
    save(STAGE / "browser-config.json", {
        "stage": relative(STAGE) + "/",
        "doc": relative(DOC) + "/",
        "catalogueURL": destination,
        "terrain": [],
        "fitBox": True,
        "browserUids": browser_uids,
        "failureTestUids": browser_uids,
        "samplerToleranceByModel": {SHORELINE_UID: 5.3},
        "allowMissingRenderedGroundUids": [SHORELINE_UID],
    })
    print(json.dumps({
        "models": len(models),
        "goodToGo": len(GOOD_TO_GO_UIDS),
        "failures": failures,
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
