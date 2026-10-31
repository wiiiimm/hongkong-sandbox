"""Publish the three bounded-height Mui Wo models and persist terminal state."""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BATCH = "government-mui-wo-height-correction-3-20260915"
DOC = ROOT / "docs/astra-city/government-import" / BATCH
STAGE = HERE / "accepted" / BATCH
LOCAL = HERE / "local" / BATCH
UIDS = {"landsd/172460:0", "landsd/201705:0", "landsd/208036:0"}

sys.path.insert(0, str(HERE.parent / "shared-modelling"))
from db import connect
import jobs
import reservations
from psycopg.rows import dict_row

sys.path.insert(0, str(HERE.parent / "model-review-ledger"))
import ledger


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temp.replace(path)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return str(Path(path).relative_to(ROOT))


def call(args):
    subprocess.run(args, cwd=ROOT, check=True)


def verify_browser(path):
    report = read(path)
    assert report.get("passed") and report["errors"] == []
    expected = {(uid, width, time) for uid in UIDS for width in (1280, 390) for time in ("15:00", "22:00")}
    actual = {(row["uid"], row["width"], row["time"]) for row in report["views"] if "time" in row}
    assert actual == expected
    assert {row["uid"] for row in report["views"] if row.get("fallbackRetained")} == {sorted(UIDS)[0]}
    for row in report["views"]:
        if "time" in row:
            assert row["active"] and row["visible"] and row["pick"] == row["uid"] and row["collision"] == row["uid"] and not row["overflow"]
    return report


def start():
    claim = reservations.claim("codex-mui-wo-height-" + str(uuid.uuid4()), ["building:" + uid for uid in sorted(UIDS)], batch=BATCH)
    assert claim["ok"], claim
    save(LOCAL / "reservation.json", json.loads(json.dumps(claim["reservation"], default=str)))
    call([sys.executable, str(HERE.parent / "shared-modelling/reservations.py"), "run", "--lease-file", str(LOCAL / "reservation.json"), "--", sys.executable, __file__, "owned"])


def owned():
    receipt = LOCAL / "reservation.json"
    assert reservations.owns(read(receipt))
    result = read(DOC / "result.json")
    proof = read(DOC / "placement-proof.json")
    catalogue = read(STAGE / "catalogue.json")
    assert {model["uid"] for model in catalogue["models"]} == UIDS
    assert result["runtimeAccepted"] == len(UIDS) and result["validationExceptions"] == 0
    assert result["aiCalls"] == result["modelGeometryChanges"] == proof["aiCalls"] == proof["modelGeometryChanges"] == 0
    assert result["placementChanges"] == proof["placementChanges"] == len(UIDS)
    for model in catalogue["models"]:
        assert digest(STAGE / model["asset"]) == model["sha256"]
    verify_browser(DOC / "staged-browser.json")

    pointer_path = ROOT / "docs/astra-city/model-integration-20260909/current-source-review.json"
    previous = read(pointer_path)
    inventory = read(ROOT / previous["inventory"])
    parts = {part["uid"]: part for part in inventory["parts"]}
    models = {model["uid"]: model for model in catalogue["models"]}
    for uid in sorted(UIDS):
        model = models[uid]
        parts[uid] = {
            "uid": uid,
            "name": model.get("label"),
            "landmarkIds": parts.get(uid, {}).get("landmarkIds", []),
            "objectId": model["objectId"],
            "csuid": model["buildingCSUID"],
            "candidate": {"sha256": model["sha256"]},
            "sourceProgress": "prepared-for-review",
            "classification": "script-verified-height-aligned-government-import",
            "knownHold": False,
        }
    ordered = sorted(parts.values(), key=lambda row: row["uid"])
    snapshot = hashlib.sha256(jobs.encode([ordered, digest(DOC / "placement-proof.json"), digest(STAGE / "catalogue.json")]).encode()).hexdigest()[:16]
    inventory_path = pointer_path.parent / f"source-review-inventory-{snapshot}.json"
    save(inventory_path, {
        **inventory,
        "snapshotId": snapshot,
        "derivedFrom": previous["snapshotId"],
        "parts": ordered,
        "qualification": "Three exact Mui Wo sources installed with unchanged asset geometry and XY placement. One bounded deterministic vertical translation per source aligns its roof maximum to current LandsD TopHeight; runtime and browser checks passed. No AI or remodelling.",
    })
    ledger.seed(inventory_path, inherit=previous["snapshotId"])

    publication = [sys.executable, str(HERE.parent / "model-integration-20260909/publish.py"), relative(STAGE / "plan.json"), "--receipt", str(receipt), "--phase", BATCH]
    call(publication)
    manifest = ROOT / "3d-viewer/city/data/manifest.json"
    before = manifest.read_bytes()
    (LOCAL / "manifest-before.json").write_bytes(before)
    call(publication + ["--apply"])
    try:
        call(["node", str(HERE / "resolution-browser.mjs"), "live", relative(STAGE / "browser-config.json")])
        verify_browser(DOC / "live-browser.json")
    except BaseException:
        manifest.write_bytes(before)
        shutil.rmtree(ROOT / "3d-viewer/city/data/official-models" / BATCH, ignore_errors=True)
        shutil.rmtree(ROOT / "docs/astra-city/model-integration-20260909" / BATCH, ignore_errors=True)
        raise

    acceptance = {
        "policy": "bounded-current-landsd-height-alignment-v1",
        "snapshot": snapshot,
        "installedUids": sorted(UIDS),
        "placementProofSHA256": digest(DOC / "placement-proof.json"),
        "catalogueSHA256": digest(STAGE / "catalogue.json"),
        "stagedBrowserSHA256": digest(DOC / "staged-browser.json"),
        "liveBrowserSHA256": digest(DOC / "live-browser.json"),
        "manifestSHA256": digest(manifest),
        "aiCalls": 0,
        "geometryChanges": 0,
        "placementChanges": len(UIDS),
    }
    save(DOC / "installed-acceptance.json", acceptance)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    effort = {"method": "scripted", "ai_model": None, "reasoning_effort": "not-applicable", "issue": "HKS-203", "run_id": snapshot, "output_ref": relative(DOC / "placement-proof.json")}
    observation = "Exact source identity and asset hash preserved. A bounded deterministic vertical translation aligns the source roof maximum to current LandsD TopHeight; terrain, runtime, staged browser and live browser checks passed. No AI, remodelling, simplification or source geometry edit."
    ledger.record_many(snapshot, receipt, [(uid, "approved-for-integration", DOC / "result.json", observation, commit) for uid in sorted(UIDS)], effort=effort, request_id=BATCH + "-approved-" + snapshot)
    ledger.record_many(snapshot, receipt, [(uid, "installed-verified", DOC / "installed-acceptance.json", observation, commit) for uid in sorted(UIDS)], effort=effort, request_id=BATCH + "-installed-" + snapshot)
    assert read(pointer_path) == previous
    save(pointer_path, {**previous, "snapshotId": snapshot, "inventory": relative(inventory_path), "previousSnapshots": [*previous.get("previousSnapshots", []), previous["snapshotId"]]})
    call([sys.executable, str(HERE.parent / "building-progress/export.py"), "--refresh"])
    call(["node", str(ROOT / "3d-viewer/scripts/build_progress.mjs")])

    terminal = {
        "batch": BATCH,
        "modelsProcessed": len(UIDS),
        "newlyInstalled": len(UIDS),
        "humanCounts": {"installed": len(UIDS), "to-do": 0, "held-human": 0, "held-ai": 0, "held-unknown": 0, "in-process": 0},
        "installedUids": sorted(UIDS),
        "snapshotId": snapshot,
        "evidence": relative(DOC / "installed-acceptance.json"),
        "aiCalls": 0,
        "geometryChanges": 0,
        "placementChanges": len(UIDS),
    }
    job_id = jobs.enqueue(BATCH, "government-mui-wo-height-terminal-v1", {"snapshot": snapshot, "manifestSHA256": acceptance["manifestSHA256"]})
    job = jobs.claim(BATCH, read(receipt)["owner"], ["government-mui-wo-height-terminal-v1"], lease_seconds=600)
    assert job and job["id"] == job_id and jobs.finish(job, result=terminal)
    with connect() as connection:
        connection.row_factory = dict_row
        stored = connection.execute("SELECT result FROM astra_modelling.jobs WHERE id=%s", (job_id,)).fetchone()["result"]
        states = {row["uid"]: row["review_state"] for row in connection.execute("SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)", (snapshot, sorted(UIDS))).fetchall()}
    assert stored == terminal and all(states[uid] == "installed-verified" for uid in UIDS)
    save(DOC / "terminal-summary.json", {**terminal, "jobId": job_id, "neonVerified": True, "progress": read(ROOT / "3d-viewer/city/data/building-progress.json")})
    released = reservations.release(read(receipt))
    assert released["ok"]
    print(json.dumps({"installed": len(UIDS), "held": 0, "inProcess": 0, "snapshot": snapshot, "neonVerified": True, "aiCalls": 0}, indent=2))


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 else start()
