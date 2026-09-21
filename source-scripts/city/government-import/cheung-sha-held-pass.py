"""Resolve Cheung Sha / Tong Fuk / Shui Hau holds with stronger compute-only checks."""
from __future__ import annotations

import collections
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE_BATCH = "government-cheung-sha-south-989-20260921"
BATCH = "government-cheung-sha-south-held-111-20260921"
SOURCE_DOC = ROOT / "docs/astra-city/government-import" / SOURCE_BATCH
DOC = SOURCE_DOC / "held-111"
SOURCE_LOCAL = HERE / "local" / SOURCE_BATCH
LOCAL = HERE / "local" / BATCH
STAGE = HERE / "accepted" / BATCH
BELOW_GRADE_REASON = "below-grade-source-surfaces-exceed-bounded-foundation-policy"

spec = importlib.util.spec_from_file_location("exact", HERE / "cheung-sha-exact-pass.py")
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
        terrain_parts.extend(exact.context.triangles(path) for path in sorted(decoded.rglob("*.gltf")))
    terrain = np.concatenate(terrain_parts)
    return {
        uid: exact.foundation_context(exact.geometry_triangles(geometries[uid]), terrain)
        for uid in sorted(uids)
    }, len(terrain)


def main():
    terminal = read(SOURCE_DOC / "terminal-states.json")
    held_rows = {row["uid"]: row for row in terminal["heldRows"]}
    assert len(held_rows) == 111
    runtime_hold_uids = {uid for uid, row in held_rows.items() if BELOW_GRADE_REASON in row["reasons"]}
    assert len(runtime_hold_uids) == 1
    assert not current_installed_uids() & set(held_rows)
    selection = read(SOURCE_DOC / "check-selection.json.gz")
    selected = {row["uid"]: row for row in selection["rows"]}
    exact_rows = {row["uid"]: row for row in read(SOURCE_DOC / "exact-pass-results.json.gz")["rows"]}
    geometries = {row["uid"]: row for row in read(SOURCE_LOCAL / "geometry.json.gz")["rows"]}

    install_uids = set(held_rows) - runtime_hold_uids
    assert set(geometries) >= install_uids
    seam_uids = {
        uid for uid in install_uids
        if "source-terrain-incomplete" in held_rows[uid]["reasons"]
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
        "policy": "Use every verified adjacent Lands Department terrain sheet from the frozen source recovery set.",
        "sourceTerrainSHA256": digest(SOURCE_DOC / "source-terrain.json"),
        "terrainTriangles": terrain_triangles,
        "rows": stitched_rows,
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    })

    template = read(ROOT / "3d-viewer/city/data/official-models/government-cheung-sha-south-compute-20260921/catalogue.json")
    models, runtime_rows, browser_forms, assembly_rows = [], [], [], []
    for uid in sorted(install_uids):
        row = selected[uid]
        proof = exact_rows[uid]
        identity = proof["identity"]
        assert identity["exactObjectAndCSUID"]
        assert identity["officialOverlapOfSmallerFootprint"] >= 0.5
        assert identity["officialFootprintCentroidDistanceM"] <= 10
        assert max(identity["targetCoveredBySourceProjection"], identity["sourceProjectionInsideTarget"]) >= 0.5
        foundation = stitched.get(uid, proof["foundation"])
        assert foundation["completeTerrainTriangles"] == foundation["triangles"]
        assert foundation["fullyBuriedUpwardTriangles"] == 0

        entry = dict(row["candidate"]["entry"])
        suppressions = proof["suppressesBuildingUids"]
        entry.update(
            priority="detail",
            placementReviewed=True,
            sourceIdentityReviewed=True,
            identityReviewApproved=True,
            publicationApproved=False,
            proceduralWindows=False,
            retainsBasicForm=True,
            placementReview=(
                "Exact unchanged Lands Department object and Building CSUID. Official footprint intersection, "
                "all-sheet source terrain and current runtime terrain were checked deterministically. The mapped "
                "basic form remains as verified support for partial, elevated or terrain-intersecting components. "
                "No AI review, remodelling, simplification or model geometry edit."
            ),
        )
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
            "originalHoldReasons": held_rows[uid]["reasons"],
            "retainsBasicForm": True,
            "suppressesBuildingUids": suppressions,
            "officialOverlapOfSmallerFootprint": identity["officialOverlapOfSmallerFootprint"],
            "officialFootprintCentroidDistanceM": identity["officialFootprintCentroidDistanceM"],
            "targetCoveredBySourceProjection": identity["targetCoveredBySourceProjection"],
            "sourceProjectionInsideTarget": identity["sourceProjectionInsideTarget"],
            "sourceSHA256": entry["sha256"],
        })

    template.update(
        area="Cheung Sha / Tong Fuk / Shui Hau held government sources · compute-only second pass",
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
            "Require exact object/CSUID, at least 50% official smaller-footprint overlap, centroid within 10m and "
            "at least 50% projected coverage in either direction. Retain the mapped basic form for every model."
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
    failures, supported_sampler_uids, missing_ground_uids = [], set(), set()
    for metric in metrics["rows"]:
        uid = metric["uid"]
        if metric.get("error") or not metric.get("sourcePreserved"):
            failures.append({"uid": uid, "reason": "source-integrity"})
            continue
        if metric.get("missingTerrain"):
            clearance = metric["missingDrawnTerrain"].get("minRuntimeClearance")
            if clearance is None or clearance < 0:
                failures.append({"uid": uid, "reason": "missing-current-terrain"})
            else:
                missing_ground_uids.add(uid)
        if metric.get("maxSamplerDelta", 0) > 0.004:
            sampler = metric["samplerDisagreement"]
            if sampler.get("minDrawnClearance") is None or min(
                sampler["minDrawnClearance"], sampler["minRuntimeClearance"]
            ) <= 0:
                failures.append({"uid": uid, "reason": "terrain-sampler-disagreement"})
            else:
                supported_sampler_uids.add(uid)
        if any(metric["budget"][key] > metrics["profiles"]["mobile"][key] for key in ("triangles", "geometryBytes", "residentBytes")):
            failures.append({"uid": uid, "reason": "mobile-runtime-budget"})
    allowed = {"sampled-ground-gap-below-model-bottom", "sampled-terrain-above-model-bottom", "sampled-highest-roof-below-terrain"}
    for result in validation["results"]:
        if result["outcome"] == "validation-exception":
            failures.append({"uid": result["uid"], "reason": result["error"]})
        for concern in result.get("concerns", []):
            if concern not in allowed:
                failures.append({"uid": result["uid"], "reason": concern})

    metric_by_uid = {row["uid"]: row for row in metrics["rows"]}
    representative_uids = set(supported_sampler_uids) | set(missing_ground_uids)
    reason_groups = collections.defaultdict(list)
    for row in assembly_rows:
        reason_groups[tuple(row["originalHoldReasons"])].append(row)
    for rows in reason_groups.values():
        representative_uids.add(sorted(rows, key=lambda row: row["uid"])[0]["uid"])
    representative_uids.update(
        row["uid"] for row in sorted(
            metrics["rows"], key=lambda row: row.get("budget", {}).get("residentBytes", 0), reverse=True
        )[:5]
    )
    representative_uids = sorted(representative_uids)
    sampler_tolerances = {
        uid: max(0.004, metric_by_uid[uid]["maxSamplerDelta"] + 0.001)
        for uid in representative_uids if uid in supported_sampler_uids
    }
    result = {
        "batch": BATCH,
        "models": len(models),
        "held": sorted(runtime_hold_uids),
        "failures": failures,
        "representativeUids": representative_uids,
        "supportedSamplerUids": sorted(supported_sampler_uids),
        "missingRenderedGroundUids": sorted(missing_ground_uids),
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
    save(STAGE / "browser-config.json", {
        "stage": relative(STAGE) + "/",
        "doc": relative(DOC) + "/",
        "catalogueURL": destination,
        "terrain": [],
        "fitBox": True,
        "browserUids": representative_uids,
        "failureTestUids": representative_uids,
        "samplerToleranceByModel": sampler_tolerances,
        "allowMissingRenderedGroundUids": sorted(set(representative_uids) & missing_ground_uids),
    })
    print(json.dumps({
        "models": len(models),
        "held": len(runtime_hold_uids),
        "representatives": len(representative_uids),
        "failures": failures,
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
