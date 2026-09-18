"""Publish the compute-only Ngong Ping / Lantau peaks batch and persist terminal states."""
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
SOURCE_BATCH = "government-ngong-ping-peaks-473-20260918"
BATCH = "government-ngong-ping-peaks-compute-20260918"
DOC = ROOT / "docs/astra-city/government-import" / SOURCE_BATCH
STAGE = HERE / "accepted" / BATCH
LOCAL = HERE / "local" / BATCH

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


def verify_browser(path, browser_uids, failure_uids):
    report = read(path)
    assert report.get("passed") and report.get("errors") == []
    expected = {
        (uid, width, time)
        for uid in browser_uids
        for width in (1280, 390)
        for time in ("15:00", "22:00")
    }
    actual = {
        (row["uid"], row["width"], row["time"])
        for row in report["views"]
        if "time" in row
    }
    assert actual == expected
    fallback = {
        row["uid"] for row in report["views"] if row.get("fallbackRetained")
    }
    assert fallback == failure_uids
    for row in report["views"]:
        if "time" not in row:
            continue
        assert row["active"] and row["visible"] and row["fullyFramed"]
        assert row["pick"] == row["uid"] and row["collision"] == row["uid"]
        assert not row["overflow"]
        assert abs(row["ground"] - row["groundSampler"]) < 0.01
    return report


def start():
    selection = read(DOC / "check-selection.json.gz")
    all_uids = sorted(row["uid"] for row in selection["rows"])
    assert len(all_uids) == 473 and len(set(all_uids)) == 473
    claim = reservations.claim(
        "codex-ngong-ping-peaks-" + str(uuid.uuid4()),
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
    receipt = LOCAL / "reservation.json"
    assert reservations.owns(read(receipt))

    selection = read(DOC / "check-selection.json.gz")
    source_rows = {row["uid"]: row for row in selection["rows"]}
    all_uids = set(source_rows)
    terminal = read(DOC / "terminal-states.json")
    held_rows = {row["uid"]: row for row in terminal["heldRows"]}
    catalogue = read(STAGE / "catalogue.json")
    models = {model["uid"]: model for model in catalogue["models"]}
    installed = set(models)
    held = set(held_rows)
    installed_count = terminal["installable"]
    held_count = terminal["held"]

    assert len(all_uids) == 473 and len(installed) == installed_count and len(held) == held_count
    assert installed | held == all_uids and not (installed & held)
    assert terminal["modelsProcessed"] == 473
    assert installed_count + held_count == 473
    assert terminal["aiCalls"] == terminal["modelGeometryChanges"] == 0
    assert terminal["humanCounts"] == {
        "installed": 0,
        "to-do": installed_count,
        "held-human": 0,
        "held-ai": 0,
        "held-unknown": held_count,
        "in-process": 0,
    }
    for row in held_rows.values():
        assert row["scriptedWorkComplete"] and not row["needsMoreCompute"]
        assert not row["requiresAI"] and not row["requiresUserDecision"]
        assert row["reasons"]

    exact = read(DOC / "exact-pass-results.json.gz")
    exact_rows = {row["uid"]: row for row in exact["rows"]}
    assert set(exact_rows) == all_uids
    assert exact["aiCalls"] == exact["modelGeometryChanges"] == 0
    runtime = read(DOC / "runtime-validation-final.json")
    assert runtime["models"] == runtime["loaderAccepted"] == runtime["checksPassed"] == installed_count
    assert runtime["exceptions"] == 0
    assert not runtime["published"]
    metrics = read(DOC / "runtime-metrics.json")
    assert len(metrics["rows"]) == installed_count
    assert metrics["aiCalls"] == metrics["geometryChanges"] == 0
    assert all(row["sourcePreserved"] and not row["missingTerrain"] for row in metrics["rows"])

    for uid, model in models.items():
        source = source_rows[uid]["candidate"]["entry"]
        proof = exact_rows[uid]
        assert proof["scriptedWorkComplete"] and proof["publicationCandidate"]
        assert proof["sourceSHA256"] == model["sha256"] == source["sha256"]
        assert model["objectId"] == source["objectId"]
        assert model["buildingCSUID"] == source["buildingCSUID"]
        assert model["sourceIdentityReviewed"] and model["placementReviewed"]
        assert model["identityReviewApproved"] and model["publicationApproved"]
        assert model["proceduralWindows"] is False
        assert digest(STAGE / model["asset"]) == model["sha256"]

    browser_config = read(STAGE / "browser-config.json")
    browser_uids = set(browser_config["browserUids"])
    failure_uids = set(browser_config["failureTestUids"])
    assert browser_uids and browser_uids <= installed
    assert failure_uids == browser_uids
    verify_browser(DOC / "staged-browser.json", browser_uids, failure_uids)

    evidence_paths = {
        "selectionSHA256": DOC / "check-selection.json.gz",
        "exactPassSHA256": DOC / "exact-pass-results.json.gz",
        "sourceTerrainSHA256": DOC / "source-terrain.json",
        "terrainPassSHA256": DOC / "terrain-pass.json",
        "terminalStatesSHA256": DOC / "terminal-states.json",
        "catalogueSHA256": STAGE / "catalogue.json",
        "planSHA256": STAGE / "plan.json",
        "runtimeMetricsSHA256": DOC / "runtime-metrics.json",
        "runtimeValidationSHA256": DOC / "runtime-validation-final.json",
        "stagedBrowserSHA256": DOC / "staged-browser.json",
    }
    decision = {
        "policy": "original-government-ngong-ping-compute-only-v1",
        "sourceBatch": SOURCE_BATCH,
        "publicationBatch": BATCH,
        "modelsProcessed": 473,
        "installedUids": sorted(installed),
        "heldRows": [held_rows[uid] for uid in sorted(held)],
        "browserRepresentativeUids": sorted(browser_uids),
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
                else "script-blocked-original-government-import"
            ),
            "knownHold": uid in held,
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
            f"{installed_count} unchanged Ngong Ping / Lantau peaks government sources installed after deterministic identity, "
            f"full-face terrain, runtime and representative desktop/mobile browser checks. {held_count} terminal "
            "compute/source-policy holds retain their basic forms. No AI review or geometry edits."
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
        "Exact unchanged government source passed scripted identity, complete source-face terrain, runtime and "
        "representative desktop/mobile browser checks. No AI review, remodelling, simplification or geometry edit."
    )
    held_observations = {
        uid: (
            "All local scripted checks completed; current basic form retained. Hold reasons: "
            + ", ".join(held_rows[uid]["reasons"])
            + ". No AI or user decision required."
        )
        for uid in held
    }
    ledger.record_many(
        snapshot,
        receipt,
        [(uid, "approved-for-integration", DOC / "decision.json", installed_observation, commit) for uid in sorted(installed)],
        effort=effort,
        request_id=BATCH + "-approved-" + snapshot,
    )
    ledger.record_many(
        snapshot,
        receipt,
        [(uid, "held", DOC / "terminal-states.json", held_observations[uid], commit) for uid in sorted(held)],
        effort=effort,
        request_id=BATCH + "-held-" + snapshot,
    )

    publication = [
        sys.executable,
        str(HERE.parent / "model-integration-20260909/publish.py"),
        relative(STAGE / "plan.json"),
        "--receipt",
        str(receipt),
        "--phase",
        BATCH,
    ]
    call(publication)
    manifest = ROOT / "3d-viewer/city/data/manifest.json"
    before = {manifest: manifest.read_bytes()}
    for path, data in before.items():
        (LOCAL / (path.name + ".before")).write_bytes(data)
    call(publication + ["--apply"])
    try:
        call(["node", str(HERE / "resolution-browser.mjs"), "live", relative(STAGE / "browser-config.json")])
        verify_browser(DOC / "live-browser.json", browser_uids, failure_uids)
    except BaseException:
        for path, data in before.items():
            path.write_bytes(data)
        shutil.rmtree(ROOT / "3d-viewer/city/data/official-models" / BATCH, ignore_errors=True)
        for entry in read(STAGE / "plan.json").get("topLevelTerrainPatches", []):
            (ROOT / "3d-viewer" / entry["destination"]).unlink(missing_ok=True)
        shutil.rmtree(ROOT / "docs/astra-city/model-integration-20260909" / BATCH, ignore_errors=True)
        raise

    acceptance = {
        **decision,
        "snapshot": snapshot,
        "liveBrowserSHA256": digest(DOC / "live-browser.json"),
        "manifestSHA256": digest(manifest),
        "installed": installed_count,
        "held": held_count,
    }
    save(DOC / "installed-acceptance.json", acceptance)
    ledger.record_many(
        snapshot,
        receipt,
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
    call([sys.executable, str(HERE.parent / "building-progress/export.py"), "--refresh"])
    call(["node", str(ROOT / "3d-viewer/scripts/build_progress.mjs")])

    reason_counts = dict(collections.Counter(
        reason for row in held_rows.values() for reason in row["reasons"]
    ))
    terminal_result = {
        "batch": BATCH,
        "modelsProcessed": 473,
        "newlyInstalled": installed_count,
        "humanCounts": {
            "installed": installed_count,
            "to-do": 0,
            "held-human": 0,
            "held-ai": 0,
            "held-unknown": held_count,
            "in-process": 0,
        },
        "heldReasonCounts": reason_counts,
        "installedUids": sorted(installed),
        "heldRows": [
            {
                "uid": uid,
                "reasons": held_rows[uid]["reasons"],
                "requiresAI": False,
                "requiresUserDecision": False,
                "needsMoreCompute": False,
                "scriptedWorkComplete": True,
                "nextDependency": "future-source-or-renderer-policy-change",
            }
            for uid in sorted(held)
        ],
        "snapshotId": snapshot,
        "evidence": relative(DOC / "installed-acceptance.json"),
        "aiCalls": 0,
        "geometryChanges": 0,
    }
    stage_name = "government-ngong-ping-terminal-v1"
    job_id = jobs.enqueue(BATCH, stage_name, {
        "snapshot": snapshot,
        "manifestSHA256": acceptance["manifestSHA256"],
    })
    job = jobs.claim(BATCH, read(receipt)["owner"], [stage_name], lease_seconds=900)
    assert job and job["id"] == job_id and jobs.finish(job, result=terminal_result)
    with connect() as connection:
        connection.row_factory = dict_row
        stored = connection.execute(
            "SELECT result FROM astra_modelling.jobs WHERE id=%s", (job_id,)
        ).fetchone()["result"]
        states = {
            row["uid"]: row["review_state"]
            for row in connection.execute(
                "SELECT uid,review_state FROM astra_modelling.model_reviews "
                "WHERE snapshot_id=%s AND uid=ANY(%s)",
                (snapshot, sorted(all_uids)),
            ).fetchall()
        }
    assert stored == terminal_result
    assert set(states) == all_uids
    assert all(
        states[uid] == ("installed-verified" if uid in installed else "held")
        for uid in all_uids
    )
    save(DOC / "terminal-summary.json", {
        **terminal_result,
        "jobId": job_id,
        "neonVerified": True,
        "progress": read(ROOT / "3d-viewer/city/data/building-progress.json"),
    })
    released = reservations.release(read(receipt))
    assert released["ok"]
    print(json.dumps({
        "installed": installed_count,
        "held": held_count,
        "inProcess": 0,
        "snapshot": snapshot,
        "neonVerified": True,
        "aiCalls": 0,
    }), flush=True)


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 else start()
