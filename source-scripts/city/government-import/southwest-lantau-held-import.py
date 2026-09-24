"""Publish the resolved Shek Pik / Fan Lau / southwest Lantau holds and persist terminal states."""
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
SOURCE_BATCH = "government-shek-pik-fan-lau-304-20260917"
BATCH = "government-shek-pik-fan-lau-held-39-20260917"
DOC = ROOT / "docs/astra-city/government-import" / SOURCE_BATCH / "held-39"
STAGE = HERE / "accepted" / BATCH
LOCAL = HERE / "local" / BATCH
GOOD_TO_GO = {"landsd/182471:0"}
SAMPLER_SUPPORT_UID = "landsd/206765:0"

sys.path.insert(0, str(HERE.parent / "shared-modelling"))
from db import connect  # noqa: E402
import jobs  # noqa: E402
import reservations  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402

sys.path.insert(0, str(HERE.parent / "model-review-ledger"))
import ledger  # noqa: E402

spec = importlib.util.spec_from_file_location("direct", HERE / "integrate.py")
direct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(direct)


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


def call(args):
    subprocess.run(args, cwd=ROOT, check=True)


def verify_browser(path, uids):
    report = read(path)
    assert report.get("passed") and report.get("errors") == []
    expected = {(uid, width, time) for uid in uids for width in (1280, 390) for time in ("15:00", "22:00")}
    actual = {(row["uid"], row["width"], row["time"]) for row in report["views"] if "time" in row}
    assert actual == expected
    assert {row["uid"] for row in report["views"] if row.get("fallbackRetained")} == uids
    for row in report["views"]:
        if "time" not in row:
            continue
        assert row["active"] and row["visible"] and row["fullyFramed"]
        assert row["pick"] == row["uid"] and row["collision"] == row["uid"]
        assert not row["overflow"]
        tolerance = 1.8 if row["uid"] == SAMPLER_SUPPORT_UID else 0.004
        assert abs(row["ground"] - row["groundSampler"]) <= tolerance
    return report


def start():
    terminal = read(ROOT / "docs/astra-city/government-import" / SOURCE_BATCH / "terminal-states.json")
    all_uids = sorted(row["uid"] for row in terminal["heldRows"])
    assert len(all_uids) == 39 and set(all_uids) >= GOOD_TO_GO
    claim = reservations.claim(
        "codex-southwest-lantau-held-" + str(uuid.uuid4()),
        ["building:" + uid for uid in all_uids],
        batch=BATCH,
        ttl=3600,
    )
    assert claim["ok"], claim
    save(LOCAL / "reservation.json", json.loads(json.dumps(claim["reservation"], default=str)))
    call([
        sys.executable,
        str(HERE.parent / "shared-modelling/reservations.py"),
        "run",
        "--lease-file",
        str(LOCAL / "reservation.json"),
        "--",
        sys.executable,
        __file__,
        "owned",
    ])


def owned():
    receipt_path = LOCAL / "reservation.json"
    receipt = read(receipt_path)
    assert reservations.owns(receipt)

    result = read(DOC / "result.json")
    assert result["models"] == 38 and set(result["goodToGo"]) == GOOD_TO_GO
    assert result["failures"] == [] and result["aiCalls"] == result["modelGeometryChanges"] == 0
    assert not result["publication"]
    proof = read(DOC / "good-to-go-proof.json")
    assert {row["uid"] for row in proof["rows"]} == GOOD_TO_GO
    assert proof["aiCalls"] == proof["modelGeometryChanges"] == 0
    support = read(DOC / "sampler-support-proof.json")
    assert support["accepted"] and support["uid"] == SAMPLER_SUPPORT_UID
    assert support["retainsBasicForm"] and support["aiCalls"] == support["modelGeometryChanges"] == 0

    catalogue = read(STAGE / "catalogue.json")
    models = {model["uid"]: model for model in catalogue["models"]}
    installed = set(models)
    all_uids = installed | GOOD_TO_GO
    assert len(installed) == 38 and len(all_uids) == 39 and not (installed & GOOD_TO_GO)
    assert all(digest(STAGE / model["asset"]) == model["sha256"] for model in models.values())
    assert all(model["placementReviewed"] and model["sourceIdentityReviewed"] and model["identityReviewApproved"] for model in models.values())
    assert all(model["proceduralWindows"] is False for model in models.values())

    metrics = read(DOC / "metrics.json")
    assert len(metrics["rows"]) == 38 and metrics["aiCalls"] == metrics["geometryChanges"] == 0
    metric_by_uid = {row["uid"]: row for row in metrics["rows"]}
    assert set(metric_by_uid) == installed
    for uid, metric in metric_by_uid.items():
        assert metric["sourcePreserved"] and not metric.get("error")
        assert metric["budget"]["residentBytes"] <= metrics["profiles"]["mobile"]["residentBytes"]
        assert metric["missingTerrain"] == 0
        assert metric["maxSamplerDelta"] <= (1.8 if uid == SAMPLER_SUPPORT_UID else 0.004)

    validation = read(DOC / "validation.json")
    exceptions = [row for row in validation["results"] if row["outcome"] == "validation-exception"]
    assert validation["models"] == validation["loaderAccepted"] == 38
    assert exceptions == [{
        "uid": SAMPLER_SUPPORT_UID,
        "outcome": "validation-exception",
        "loaderAccepted": True,
        "error": "Sampler differs from rendered terrain or overlapping surfaces disagree",
    }]
    browser_config = read(STAGE / "browser-config.json")
    assert set(browser_config["browserUids"]) == installed
    assert set(browser_config["failureTestUids"]) == installed
    assert browser_config["allowMissingRenderedGroundUids"] == []
    assert browser_config["samplerToleranceByModel"] == {SAMPLER_SUPPORT_UID: 1.8}
    verify_browser(DOC / "staged-browser.json", installed)

    # Approval is frozen only after every staged compute and browser gate passed.
    for model in catalogue["models"]:
        model["publicationApproved"] = True
    save(STAGE / "catalogue.json", catalogue)
    save(STAGE / "catalogue-index.json", {"models": len(installed), "catalogues": ["catalogue.json"]})

    source_selection = read(ROOT / "docs/astra-city/government-import" / SOURCE_BATCH / "check-selection.json.gz")
    source_rows = {row["uid"]: row for row in source_selection["rows"]}
    assert all_uids <= set(source_rows)
    evidence_paths = {
        "resultSHA256": DOC / "result.json",
        "assemblyProofSHA256": DOC / "assembly-proof.json",
        "stitchedTerrainProofSHA256": DOC / "stitched-terrain-proof.json",
        "goodToGoProofSHA256": DOC / "good-to-go-proof.json",
        "samplerSupportProofSHA256": DOC / "sampler-support-proof.json",
        "metricsSHA256": DOC / "metrics.json",
        "validationSHA256": DOC / "validation.json",
        "stagedBrowserSHA256": DOC / "staged-browser.json",
        "catalogueSHA256": STAGE / "catalogue.json",
        "planSHA256": STAGE / "plan.json",
    }
    decision = {
        "policy": "original-government-southwest-lantau-held-compute-only-v1",
        "sourceBatch": SOURCE_BATCH,
        "publicationBatch": BATCH,
        "modelsProcessed": 39,
        "installedUids": sorted(installed),
        "goodToGoUids": sorted(GOOD_TO_GO),
        "evidenceHashes": {key: digest(path) for key, path in evidence_paths.items()},
        "sourceGeometryPreserved": True,
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    }
    save(DOC / "decision.json", decision)

    pointer_path = ROOT / "docs/astra-city/model-integration-20260909/current-source-review.json"
    previous = read(pointer_path)
    inventory = read(ROOT / previous["inventory"])
    parts = {part["uid"]: part for part in inventory["parts"]}
    for uid in sorted(all_uids):
        source = source_rows[uid]["candidate"]["entry"]
        model = models.get(uid, source)
        parts[uid] = {
            "uid": uid,
            "name": model.get("label"),
            "landmarkIds": parts.get(uid, {}).get("landmarkIds", []),
            "objectId": model["objectId"],
            "csuid": model["buildingCSUID"],
            "candidate": {"sha256": model["sha256"]},
            "sourceProgress": "prepared-for-review",
            "classification": (
                "script-verified-original-government-import"
                if uid in installed
                else "script-verified-current-form-good-to-go"
            ),
            "knownHold": False,
        }
    ordered = sorted(parts.values(), key=lambda row: row["uid"])
    snapshot = hashlib.sha256(jobs.encode([ordered, decision]).encode()).hexdigest()[:16]
    inventory_path = pointer_path.parent / f"source-review-inventory-{snapshot}.json"
    save(inventory_path, {
        **inventory,
        "snapshotId": snapshot,
        "derivedFrom": previous["snapshotId"],
        "parts": ordered,
        "qualification": (
            "The final 39 Shek Pik / Fan Lau / southwest Lantau source forms reached terminal compute-only "
            "states: 38 unchanged government sources installed and 1 current form accepted as good to go because its government "
            "source adds no visible detail. No AI review or geometry edits."
        ),
    })
    ledger.seed(inventory_path, inherit=previous["snapshotId"])

    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    effort = {
        "method": "scripted",
        "ai_model": None,
        "reasoning_effort": "not-applicable",
        "issue": "HKS-203",
        "run_id": snapshot,
        "output_ref": relative(DOC / "decision.json"),
    }
    installed_observation = (
        "Exact unchanged government source passed deterministic identity, assembly, terrain, mobile runtime and "
        "complete desktop/mobile day/night browser checks with fallback/retry. No AI review or geometry edit."
    )
    good_observations = {
        row["uid"]: row["reason"] + " No AI review or geometry edit."
        for row in proof["rows"]
    }
    ledger.record_many(
        snapshot,
        receipt_path,
        [(uid, "approved-for-integration", DOC / "decision.json", installed_observation, commit) for uid in sorted(installed)],
        effort=effort,
        request_id=BATCH + "-approved-" + snapshot,
    )
    ledger.record_many(
        snapshot,
        receipt_path,
        [(uid, "good-to-go", DOC / "good-to-go-proof.json", good_observations[uid], commit) for uid in sorted(GOOD_TO_GO)],
        effort=effort,
        request_id=BATCH + "-good-to-go-" + snapshot,
    )

    publication = [
        sys.executable,
        str(HERE.parent / "model-integration-20260909/publish.py"),
        relative(STAGE / "plan.json"),
        "--receipt",
        str(receipt_path),
        "--phase",
        BATCH,
    ]
    call(publication)
    manifest = ROOT / "3d-viewer/city/data/manifest.json"
    before_manifest = manifest.read_bytes()
    (LOCAL / "manifest-before.json").write_bytes(before_manifest)
    call(publication + ["--apply"])
    destination = ROOT / "3d-viewer/city/data/official-models" / BATCH
    try:
        call(["node", str(HERE / "resolution-browser.mjs"), "live", relative(STAGE / "browser-config.json")])
        verify_browser(DOC / "live-browser.json", installed)
    except BaseException:
        manifest.write_bytes(before_manifest)
        shutil.rmtree(destination, ignore_errors=True)
        shutil.rmtree(ROOT / "docs/astra-city/model-integration-20260909" / BATCH, ignore_errors=True)
        raise

    acceptance = {
        **decision,
        "snapshot": snapshot,
        "liveBrowserSHA256": digest(DOC / "live-browser.json"),
        "manifestSHA256": digest(manifest),
        "installed": len(installed),
        "goodToGo": len(GOOD_TO_GO),
        "held": 0,
    }
    save(DOC / "installed-acceptance.json", acceptance)
    ledger.record_many(
        snapshot,
        receipt_path,
        [(uid, "installed-verified", DOC / "installed-acceptance.json", installed_observation, commit) for uid in sorted(installed)],
        effort=effort,
        request_id=BATCH + "-installed-" + snapshot,
    )

    assert read(pointer_path) == previous
    save(pointer_path, {
        **previous,
        "snapshotId": snapshot,
        "inventory": relative(inventory_path),
        "previousSnapshots": [*previous.get("previousSnapshots", []), previous["snapshotId"]],
    })

    # Record the current-form acceptance after publication so their input hashes include the final manifest.
    screening_dir = LOCAL / "screening"
    call([sys.executable, str(HERE.parent / "enhancement-screening/screen.py"), "plan", "--out", str(screening_dir)])
    screening_plan = read(screening_dir / "inputs.json.gz")
    plan_by_uid = {row["uid"]: row for row in screening_plan["rows"]}
    proof_path = DOC / "good-to-go-proof.json"
    entries = [{
        "uid": uid,
        "inputHash": plan_by_uid[uid]["inputHash"],
        "decision": "good-to-go",
        "reason": good_observations[uid],
        "evidence": relative(proof_path),
        "evidenceHash": digest(proof_path),
    } for uid in sorted(GOOD_TO_GO)]
    entries_path = LOCAL / "good-to-go-entries.json"
    save(entries_path, entries)
    call([
        sys.executable,
        str(HERE.parent / "enhancement-screening/screen.py"),
        "record",
        "--out", str(screening_dir),
        "--entries", str(entries_path),
        "--receipt", str(receipt_path),
        "--request-id", BATCH + "-screening-" + snapshot,
    ])

    call([sys.executable, str(HERE.parent / "building-progress/export.py"), "--refresh"])
    call(["node", str(ROOT / "3d-viewer/scripts/build_progress.mjs")])
    progress = read(ROOT / "3d-viewer/city/data/building-progress.json")
    assert progress["breakdown"]["goodToGo"] >= 3
    assert progress["government"]["goodToGo"] >= 3

    terminal_result = {
        "batch": BATCH,
        "modelsProcessed": 39,
        "newlyInstalled": 38,
        "goodToGo": 1,
        "humanCounts": {
            "installed": 38,
            "good-to-go": 1,
            "to-do": 0,
            "held-human": 0,
            "held-ai": 0,
            "held-unknown": 0,
            "in-process": 0,
        },
        "installedUids": sorted(installed),
        "goodToGoUids": sorted(GOOD_TO_GO),
        "snapshotId": snapshot,
        "evidence": relative(DOC / "installed-acceptance.json"),
        "aiCalls": 0,
        "geometryChanges": 0,
    }
    stage_name = "government-southwest-lantau-held-terminal-v1"
    job_id = jobs.enqueue(BATCH, stage_name, {
        "snapshot": snapshot,
        "manifestSHA256": acceptance["manifestSHA256"],
    })
    job = jobs.claim(BATCH, receipt["owner"], [stage_name], lease_seconds=900)
    assert job and job["id"] == job_id and jobs.finish(job, result=terminal_result)
    with connect() as connection:
        connection.row_factory = dict_row
        stored = connection.execute("SELECT result FROM astra_modelling.jobs WHERE id=%s", (job_id,)).fetchone()["result"]
        states = {
            row["uid"]: row["review_state"]
            for row in connection.execute(
                "SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)",
                (snapshot, sorted(all_uids)),
            ).fetchall()
        }
    assert stored == terminal_result and set(states) == all_uids
    assert all(states[uid] == ("installed-verified" if uid in installed else "good-to-go") for uid in all_uids)
    save(DOC / "terminal-summary.json", {
        **terminal_result,
        "jobId": job_id,
        "neonVerified": True,
        "reviewStates": dict(collections.Counter(states.values())),
        "progress": progress,
    })
    released = reservations.release(receipt)
    assert released["ok"]
    print(json.dumps({
        "installed": 38,
        "goodToGo": 1,
        "held": 0,
        "inProcess": 0,
        "snapshot": snapshot,
        "neonVerified": True,
        "aiCalls": 0,
    }), flush=True)


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 else start()
