"""Publish the script-completed Mui Wo sources and record terminal states in Neon."""
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
BATCH = "government-mui-wo-held-13-20260915"
DOC = ROOT / "docs/astra-city/government-import/government-mui-wo-16-20260915"
STAGING = DOC / "staging"
STAGE = HERE / "accepted" / BATCH
LOCAL = HERE / "local" / BATCH
ALL_UIDS = {
    "landsd/121912:0", "landsd/172460:0", "landsd/179822:0", "landsd/201705:0",
    "landsd/206975:0", "landsd/207849:0", "landsd/207855:0", "landsd/207859:0",
    "landsd/207860:0", "landsd/208036:0", "landsd/208958:0", "landsd/254783:0",
    "landsd/262466:0", "landsd/299366:0", "landsd/299369:0", "landsd/299383:0",
}

sys.path.insert(0, str(HERE.parent / "shared-modelling"))
from db import connect
import jobs
import reservations
from psycopg.rows import dict_row

sys.path.insert(0, str(HERE.parent / "model-review-ledger"))
import ledger

spec = importlib.util.spec_from_file_location("direct", HERE / "integrate.py")
direct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(direct)


def read(path):
    path = Path(path); raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def save(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temp.replace(path)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return str(Path(path).relative_to(ROOT))


def call(args):
    subprocess.run(args, cwd=ROOT, check=True)


def verify_browser(path, installed):
    report = read(path)
    assert report.get("passed") and report["errors"] == []
    expected = {(uid, width, time) for uid in installed for width in (1280, 390) for time in ("15:00", "22:00")}
    actual = {(row["uid"], row["width"], row["time"]) for row in report["views"] if "time" in row}
    assert actual == expected
    assert {row["uid"] for row in report["views"] if row.get("fallbackRetained")} == {sorted(installed)[0]}
    for row in report["views"]:
        if "time" in row:
            assert row["active"] and row["visible"] and row["pick"] == row["uid"] and row["collision"] == row["uid"] and not row["overflow"]
    return report


def start():
    claim = reservations.claim("codex-mui-wo-held-" + str(uuid.uuid4()), ["building:" + uid for uid in sorted(ALL_UIDS)], batch=BATCH)
    assert claim["ok"], claim
    save(LOCAL / "reservation.json", json.loads(json.dumps(claim["reservation"], default=str)))
    call([sys.executable, str(HERE.parent / "shared-modelling/reservations.py"), "run", "--lease-file", str(LOCAL / "reservation.json"), "--", sys.executable, __file__, "owned"])


def owned():
    receipt = LOCAL / "reservation.json"
    assert reservations.owns(read(receipt))
    proof = read(DOC / "script-pass-results.json.gz")
    result = read(STAGING / "result.json")
    catalogue = read(STAGE / "catalogue.json")
    installed = {model["uid"] for model in catalogue["models"]}
    held = ALL_UIDS - installed
    assert len(installed) == 13 and held == set(result["held"])
    assert proof["aiCalls"] == proof["modelGeometryChanges"] == result["aiCalls"] == result["modelGeometryChanges"] == 0
    assert result["sourcePreserved"] and result["validationExceptions"] == 0
    for model in catalogue["models"]:
        assert digest(STAGE / model["asset"]) == model["sha256"]
    verify_browser(STAGING / "staged-browser.json", installed)

    pointer_path = ROOT / "docs/astra-city/model-integration-20260909/current-source-review.json"
    previous = read(pointer_path); inventory = read(ROOT / previous["inventory"])
    parts = {part["uid"]: part for part in inventory["parts"]}
    models = {model["uid"]: model for model in catalogue["models"]}
    source_rows = {row["uid"]: row for row in read(ROOT / "docs/astra-city/government-import/government-mui-wo-23-20260914/check-selection.json.gz")["rows"]}
    for uid in sorted(ALL_UIDS):
        source = source_rows[uid]["candidate"]["entry"]
        model = models.get(uid, source)
        parts[uid] = {
            "uid": uid, "name": model.get("label"), "landmarkIds": parts.get(uid, {}).get("landmarkIds", []),
            "objectId": model["objectId"], "csuid": model["buildingCSUID"], "candidate": {"sha256": model["sha256"]},
            "sourceProgress": "prepared-for-review",
            "classification": "script-verified-original-government-import" if uid in installed else "script-blocked-original-government-import",
            "knownHold": uid in held,
        }
    ordered = sorted(parts.values(), key=lambda row: row["uid"])
    snapshot = hashlib.sha256(jobs.encode([ordered, digest(DOC / "script-pass-results.json.gz"), digest(STAGE / "catalogue.json")]).encode()).hexdigest()[:16]
    inventory_path = pointer_path.parent / f"source-review-inventory-{snapshot}.json"
    save(inventory_path, {
        **inventory, "snapshotId": snapshot, "derivedFrom": previous["snapshotId"], "parts": ordered,
        "qualification": "Thirteen unchanged Mui Wo government sources installed after deterministic identity, full-face native terrain, retained-basic-support, runtime and browser checks. Three terminal local-compute holds remain. No AI review or geometry edits.",
    })
    ledger.seed(inventory_path, inherit=previous["snapshotId"])
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    effort = {"method": "scripted", "ai_model": None, "reasoning_effort": "not-applicable", "issue": "HKS-203", "run_id": snapshot, "output_ref": relative(DOC / "script-pass-results.json.gz")}
    installed_observation = "Exact unchanged government source passed scripted identity, full-face native terrain, runtime and staged browser checks. Any upper-shell source retains its existing mapped lower mass explicitly. No AI review, remodelling, simplification or model geometry edit."
    held_by_uid = {row["uid"]: row for row in proof["rows"] if row["uid"] in held}
    held_observation = {uid: "All local scripted checks completed; current basic form retained. Hold reasons: " + ", ".join(held_by_uid[uid]["reasons"]) + ". No AI review requested." for uid in held}
    ledger.record_many(snapshot, receipt, [(uid, "approved-for-integration", STAGING / "result.json", installed_observation, commit) for uid in sorted(installed)], effort=effort, request_id=BATCH + "-approved-" + snapshot)
    ledger.record_many(snapshot, receipt, [(uid, "held", DOC / "script-pass-results.json.gz", held_observation[uid], commit) for uid in sorted(held)], effort=effort, request_id=BATCH + "-held-" + snapshot)

    publication = [sys.executable, str(HERE.parent / "model-integration-20260909/publish.py"), relative(STAGE / "plan.json"), "--receipt", str(receipt), "--phase", BATCH]
    call(publication)
    manifest = ROOT / "3d-viewer/city/data/manifest.json"; before = manifest.read_bytes(); (LOCAL / "manifest-before.json").write_bytes(before)
    call(publication + ["--apply"])
    try:
        call(["node", str(HERE / "resolution-browser.mjs"), "live", relative(STAGE / "browser-config.json")])
        verify_browser(STAGING / "live-browser.json", installed)
    except BaseException:
        manifest.write_bytes(before)
        shutil.rmtree(ROOT / "3d-viewer/city/data/official-models" / BATCH, ignore_errors=True)
        shutil.rmtree(ROOT / "docs/astra-city/model-integration-20260909" / BATCH, ignore_errors=True)
        raise
    acceptance = {
        "policy": "original-government-mui-wo-complete-script-pass-v1", "snapshot": snapshot,
        "installedUids": sorted(installed), "heldUids": sorted(held),
        "sourceProofSHA256": digest(DOC / "script-pass-results.json.gz"), "catalogueSHA256": digest(STAGE / "catalogue.json"),
        "stagedBrowserSHA256": digest(STAGING / "staged-browser.json"), "liveBrowserSHA256": digest(STAGING / "live-browser.json"),
        "manifestSHA256": digest(manifest), "aiCalls": 0, "geometryChanges": 0,
    }
    save(DOC / "installed-acceptance.json", acceptance)
    ledger.record_many(snapshot, receipt, [(uid, "installed-verified", DOC / "installed-acceptance.json", installed_observation, commit) for uid in sorted(installed)], effort=effort, request_id=BATCH + "-installed-" + snapshot)
    assert read(pointer_path) == previous
    save(pointer_path, {**previous, "snapshotId": snapshot, "inventory": relative(inventory_path), "previousSnapshots": [*previous.get("previousSnapshots", []), previous["snapshotId"]]})
    call([sys.executable, str(HERE.parent / "building-progress/export.py"), "--refresh"])
    call(["node", str(ROOT / "3d-viewer/scripts/build_progress.mjs")])

    terminal = {
        "batch": BATCH, "modelsProcessed": 16, "newlyInstalled": 13,
        "humanCounts": {"installed": 13, "to-do": 0, "held-human": 0, "held-ai": 0, "held-unknown": 3, "in-process": 0},
        "heldReasonCounts": dict(collections.Counter(reason for uid in held for reason in held_by_uid[uid]["reasons"])),
        "installedUids": sorted(installed), "heldRows": [{"uid": uid, "reasons": held_by_uid[uid]["reasons"], "requiresAI": False, "nextDependency": "local-compute/source-placement-or-terrain"} for uid in sorted(held)],
        "snapshotId": snapshot, "evidence": relative(DOC / "installed-acceptance.json"), "aiCalls": 0, "geometryChanges": 0,
    }
    job_id = jobs.enqueue(BATCH, "government-mui-wo-terminal-v2", {"snapshot": snapshot, "manifestSHA256": acceptance["manifestSHA256"]})
    job = jobs.claim(BATCH, read(receipt)["owner"], ["government-mui-wo-terminal-v2"], lease_seconds=600)
    assert job and job["id"] == job_id and jobs.finish(job, result=terminal)
    with connect() as connection:
        connection.row_factory = dict_row
        stored = connection.execute("SELECT result FROM astra_modelling.jobs WHERE id=%s", (job_id,)).fetchone()["result"]
        states = {row["uid"]: row["review_state"] for row in connection.execute("SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)", (snapshot, sorted(ALL_UIDS))).fetchall()}
    assert stored == terminal and all(states[uid] == ("installed-verified" if uid in installed else "held") for uid in ALL_UIDS)
    save(DOC / "terminal-summary.json", {**terminal, "jobId": job_id, "neonVerified": True, "progress": read(ROOT / "3d-viewer/city/data/building-progress.json")})
    released = reservations.release(read(receipt)); assert released["ok"]
    print(json.dumps({"installed": 13, "held": 3, "inProcess": 0, "snapshot": snapshot, "neonVerified": True, "aiCalls": 0}))


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 else start()
