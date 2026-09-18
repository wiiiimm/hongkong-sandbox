"""Install the remaining Lantau landmarks on verified existing terrain; never AI."""
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
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BATCH = "government-lantau-remaining-11-20260916"
BASE = ROOT / "docs/astra-city/government-import/government-lantau-landmarks-16-20260916/second-pass"
DOC = BASE / "remaining-11-install"
STAGE = HERE / "accepted" / BATCH
LOCAL = HERE / "local" / BATCH / "install"
UIDS = (
    "landsd/107386:0", "landsd/108265:0", "landsd/108736:0",
    "landsd/108741:0", "landsd/178555:0", "landsd/187251:0",
    "landsd/246229:0", "landsd/246471:0", "landsd/271137:0",
    "landsd/296766:0", "landsd/337237:0",
)
FOUNDATION_LIMITS = {"landsd/246471:0": 0.0013}

sys.path.insert(0, str(HERE.parent / "shared-modelling"))
from db import connect  # noqa: E402
import jobs  # noqa: E402
import reservations  # noqa: E402

sys.path.insert(0, str(HERE.parent / "model-review-ledger"))
import ledger  # noqa: E402

direct_spec = importlib.util.spec_from_file_location("direct", HERE / "integrate.py")
direct = importlib.util.module_from_spec(direct_spec)
direct_spec.loader.exec_module(direct)


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


def start():
    claim = reservations.claim(
        "codex-lantau-remaining-import-" + str(uuid.uuid4()),
        ["building:" + uid for uid in UIDS],
        batch=BATCH,
        ttl=3600,
    )
    assert claim["ok"], claim
    save(LOCAL / "reservation.json", json.loads(json.dumps(claim["reservation"], default=str)))
    call([
        sys.executable, str(HERE.parent / "shared-modelling/reservations.py"), "run",
        "--lease-file", str(LOCAL / "reservation.json"), "--",
        sys.executable, __file__, "owned",
    ])


def owned():
    receipt = LOCAL / "reservation.json"
    assert reservations.owns(read(receipt))
    source_selection = read(BASE / "runtime-selection.json.gz")
    source_rows = {row["uid"]: row for row in source_selection["rows"]}
    proofs = {row["uid"]: row for row in read(BASE / "final-script-pass/results.json.gz")["rows"]}
    assemblies = {row["uid"]: row for row in read(BASE / "assembly-map.json")["rows"]}
    catalogue = read(STAGE / "catalogue.json")
    models = {model["uid"]: model for model in catalogue["models"]}
    assert set(models) == set(UIDS)

    foundation_rows = []
    for uid in UIDS:
        model, source, proof, assembly = models[uid], source_rows[uid], proofs[uid], assemblies[uid]
        identity, foundation = proof["identity"], proof["foundation"]
        limit = FOUNDATION_LIMITS.get(uid, 0.001)
        assert digest(STAGE / model["asset"]) == model["sha256"] == source["candidate"]["entry"]["sha256"]
        assert proof["scriptedWorkComplete"] and identity["exactObjectAndCSUID"]
        assert identity["targetCoveredBySourceProjection"] >= 0.93
        assert foundation["completeTerrainTriangles"] == foundation["triangles"]
        assert foundation["fullyBuriedUpwardTriangles"] == 0
        assert foundation["fullyBuriedAreaFraction"] <= limit
        assert assembly["accepted"] and assembly["sourceSHA256"] == model["sha256"]
        assert model.get("suppressesBuildingUids", []) == assembly["suppressions"]
        model.update(
            priority="landmark",
            placementReviewed=True,
            sourceIdentityReviewed=True,
            identityReviewApproved=True,
            publicationApproved=True,
            proceduralWindows=False,
            placementReview=(
                "Exact unchanged government source matched by object ID and Building CSUID. Complete source-face "
                "terrain coverage, bounded below-grade foundation, assembly, mobile runtime and browser checks "
                "pass on the existing rendered terrain. No AI review, remodelling or geometry edit."
            ),
        )
        foundation_rows.append({
            "uid": uid,
            "accepted": True,
            "targetCoverage": identity["targetCoveredBySourceProjection"],
            "completeTerrainTriangles": foundation["completeTerrainTriangles"],
            "triangles": foundation["triangles"],
            "fullyBuriedUpwardTriangles": foundation["fullyBuriedUpwardTriangles"],
            "fullyBuriedAreaFraction": foundation["fullyBuriedAreaFraction"],
            "maximumBuriedAreaFraction": limit,
            "minimumGapM": foundation["minimumGapM"],
            "suppressions": assembly["suppressions"],
            "retainedForms": assembly["retainedForms"],
        })
    catalogue["models"] = [models[uid] for uid in UIDS]
    catalogue["loadingPolicy"] = "Published after deterministic identity, full-face existing-terrain, assembly, runtime and browser checks"
    save(STAGE / "catalogue.json", catalogue)

    selection = {
        **source_selection,
        "batch": BATCH,
        "manifestSHA256": digest(ROOT / "3d-viewer/city/data/manifest.json"),
        "rows": [source_rows[uid] for uid in UIDS],
        "aiCalls": 0,
    }
    save(DOC / "selection.json.gz", selection)
    save(DOC / "foundation-resolution.json", {
        "policy": (
            "Accept exact unchanged source on existing terrain when every source face has terrain coverage, no "
            "upward face is fully buried, total fully buried area is bounded, and source assembly is verified. "
            "Coarse bottom-sampler warnings are retained as diagnostics because below-grade foundation walls are valid."
        ),
        "rows": foundation_rows,
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    })
    save(DOC / "terrain-candidates.json", [])
    call([
        "node", str(HERE / "acceptance-metrics.mjs"), "--selection", relative(DOC / "selection.json.gz"),
        "--candidates", relative(STAGE), "--terrain-candidates", relative(DOC / "terrain-candidates.json"),
        "--out", relative(DOC / "metrics.json"),
    ])
    call([
        "node", str(HERE.parent / "building-batch/validate_candidates.mjs"),
        "--candidates", relative(STAGE),
        "--source-forms", relative(HERE / "local" / BATCH / "source-forms.json"),
        "--out", relative(DOC / "validation.json"),
    ], allowed=(0, 1))

    metrics = read(DOC / "metrics.json")
    validation = read(DOC / "validation.json")
    metric_rows = {row["uid"]: row for row in metrics["rows"]}
    validation_rows = {row["uid"]: row for row in validation["results"]}
    allowed_concerns = {"sampled-ground-gap-below-model-bottom", "sampled-terrain-above-model-bottom"}
    for uid in UIDS:
        metric, checked = metric_rows[uid], validation_rows[uid]
        assert metric["sourcePreserved"] and not metric["missingTerrain"]
        assert metric["budget"]["residentBytes"] <= metrics["profiles"]["mobile"]["residentBytes"]
        assert checked["outcome"] != "validation-exception", (uid, checked)
        assert set(checked.get("concerns", [])) <= allowed_concerns, (uid, checked)
    assert validation["loaderAccepted"] == validation["checksPassed"] == len(UIDS)
    assert validation["exceptions"] == 0

    destination = "city/data/official-models/" + BATCH + "/catalogue.json"
    plan = {
        "areas": [{"area": catalogue["area"], "catalogue": relative(STAGE / "catalogue.json"), "destination": destination}],
        "topLevelTerrainPatches": [],
    }
    save(STAGE / "plan.json", plan)
    save(STAGE / "browser-config.json", {
        "stage": relative(STAGE) + "/",
        "doc": relative(DOC) + "/",
        "catalogueURL": destination,
        "terrain": [],
        "fitBox": True,
        "browserUids": list(UIDS),
        "failureTestUids": list(UIDS),
    })
    call(["node", str(HERE / "resolution-browser.mjs"), "staged", relative(STAGE / "browser-config.json")])
    direct.browser_verified(DOC / "staged-browser.json", set(UIDS))

    for uid in UIDS:
        row = source_rows[uid]
        with connect() as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            native = connection.execute(
                "SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s",
                (row["native"]["cacheKey"],),
            ).fetchone()
        assert native and native[0] == row["native"]["resultSha"]

    decision = {
        "policy": "original-government-lantau-existing-terrain-full-face-v1",
        "uids": list(UIDS),
        "sourceSHA256s": {uid: models[uid]["sha256"] for uid in UIDS},
        "catalogueSHA256": digest(STAGE / "catalogue.json"),
        "planSHA256": digest(STAGE / "plan.json"),
        "foundationSHA256": digest(DOC / "foundation-resolution.json"),
        "metricsSHA256": digest(DOC / "metrics.json"),
        "validationSHA256": digest(DOC / "validation.json"),
        "stagedBrowserSHA256": digest(DOC / "staged-browser.json"),
        "aiCallsThisImport": 0,
        "geometryChanges": 0,
    }
    save(DOC / "decision.json", decision)

    pointer_path = ROOT / "docs/astra-city/model-integration-20260909/current-source-review.json"
    previous = read(pointer_path)
    inventory = read(ROOT / previous["inventory"])
    parts = {part["uid"]: part for part in inventory["parts"]}
    for uid in UIDS:
        model = models[uid]
        parts[uid] = {
            "uid": uid, "name": model.get("label"),
            "landmarkIds": parts.get(uid, {}).get("landmarkIds", []),
            "objectId": model["objectId"], "csuid": model["buildingCSUID"],
            "candidate": {"sha256": model["sha256"]},
            "sourceProgress": "prepared-for-review",
            "classification": "script-verified-original-government-lantau-landmark",
            "knownHold": False,
        }
    ordered = sorted(parts.values(), key=lambda row: row["uid"])
    snapshot = hashlib.sha256(jobs.encode([ordered, decision]).encode()).hexdigest()[:16]
    inventory_path = pointer_path.parent / f"source-review-inventory-{snapshot}.json"
    save(inventory_path, {
        **inventory, "snapshotId": snapshot, "derivedFrom": previous["snapshotId"], "parts": ordered,
        "qualification": (
            "Eleven unchanged Lantau government landmarks installed after deterministic identity, full-face "
            "existing-terrain, assembly, runtime and browser checks. No AI review or geometry edits."
        ),
    })
    ledger.seed(inventory_path, inherit=previous["snapshotId"])
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    effort = {
        "method": "scripted", "ai_model": None, "reasoning_effort": "not-applicable", "issue": "HKS-203",
        "run_id": snapshot, "output_ref": relative(DOC / "decision.json"),
    }
    observation = (
        "Exact unchanged government landmark source passed deterministic identity, complete source-face terrain, "
        "bounded foundation, assembly, mobile runtime and staged/live browser checks. Existing terrain remains "
        "unchanged. No AI review, remodelling, simplification or geometry edit."
    )
    ledger.record_many(
        snapshot, receipt,
        [(uid, "approved-for-integration", DOC / "decision.json", observation, commit) for uid in UIDS],
        effort=effort, request_id=BATCH + "-approved-" + snapshot,
    )

    publication = [
        sys.executable, str(HERE.parent / "model-integration-20260909/publish.py"),
        relative(STAGE / "plan.json"), "--receipt", str(receipt), "--phase", BATCH,
    ]
    call(publication)
    manifest = ROOT / "3d-viewer/city/data/manifest.json"
    before = manifest.read_bytes()
    (LOCAL / "manifest-before.json").write_bytes(before)
    call(publication + ["--apply"])
    try:
        call(["node", str(HERE / "resolution-browser.mjs"), "live", relative(STAGE / "browser-config.json")])
        direct.browser_verified(DOC / "live-browser.json", set(UIDS))
    except BaseException:
        manifest.write_bytes(before)
        shutil.rmtree(ROOT / "3d-viewer/city/data/official-models" / BATCH, ignore_errors=True)
        shutil.rmtree(ROOT / "docs/astra-city/model-integration-20260909" / BATCH, ignore_errors=True)
        raise

    acceptance = {
        **decision,
        "snapshot": snapshot,
        "liveBrowserSHA256": digest(DOC / "live-browser.json"),
        "manifestSHA256": digest(manifest),
        "installed": len(UIDS),
    }
    save(DOC / "installed-acceptance.json", acceptance)
    ledger.record_many(
        snapshot, receipt,
        [(uid, "installed-verified", DOC / "installed-acceptance.json", observation, commit) for uid in UIDS],
        effort=effort, request_id=BATCH + "-installed-" + snapshot,
    )
    assert read(pointer_path) == previous
    save(pointer_path, {
        **previous, "snapshotId": snapshot, "inventory": relative(inventory_path),
        "previousSnapshots": [*previous.get("previousSnapshots", []), previous["snapshotId"]],
    })
    call([sys.executable, str(HERE.parent / "building-progress/export.py"), "--refresh"])
    call(["node", str(ROOT / "3d-viewer/scripts/build_progress.mjs")])

    terminal = {
        "batch": BATCH,
        "modelsProcessed": len(UIDS),
        "newlyInstalled": len(UIDS),
        "humanCounts": {"installed": len(UIDS), "to-do": 0, "held-human": 0, "held-ai": 0, "held-unknown": 0, "in-process": 0},
        "foundationConcernCounts": dict(collections.Counter(
            concern for row in validation["results"] for concern in row.get("concerns", [])
        )),
        "installedUids": list(UIDS),
        "snapshotId": snapshot,
        "evidence": relative(DOC / "installed-acceptance.json"),
        "aiCalls": 0,
        "geometryChanges": 0,
    }
    job_id = jobs.enqueue(BATCH, "government-lantau-landmarks-terminal-v1", {"snapshot": snapshot, "manifestSHA256": acceptance["manifestSHA256"]})
    job = jobs.claim(BATCH, read(receipt)["owner"], ["government-lantau-landmarks-terminal-v1"], lease_seconds=600)
    assert job and job["id"] == job_id and jobs.finish(job, result=terminal)
    with connect() as connection:
        connection.execute("SET TRANSACTION READ ONLY")
        installed = connection.execute(
            "SELECT uid FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND review_state='installed-verified' AND uid=ANY(%s)",
            (snapshot, list(UIDS)),
        ).fetchall()
    assert {row[0] for row in installed} == set(UIDS)
    save(DOC / "summary.json", {**terminal, "jobId": job_id, "neonVerified": True, "progress": read(ROOT / "3d-viewer/city/data/building-progress.json")})
    print(json.dumps({"installed": len(UIDS), "snapshot": snapshot, "neonVerified": True, "aiCalls": 0}), flush=True)


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 else start()
