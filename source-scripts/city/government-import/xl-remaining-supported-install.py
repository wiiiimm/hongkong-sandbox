"""Publish four supported XL towers after staged and live browser checks."""

import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from run import ROOT, HERE, read, save, digest, reservations, jobs, connect

sys.path.insert(0, str(HERE.parent / "model-review-ledger"))
import ledger

spec = importlib.util.spec_from_file_location("direct_import", HERE / "integrate.py")
direct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(direct)

BATCH = "government-xl-remaining-supported-20260923"
DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/supported"
LOCAL = HERE / "local" / BATCH
STAGE = HERE / "accepted" / BATCH
UIDS = {"landsd/255939:0", "landsd/256136:0", "landsd/255544:0", "landsd/256138:0"}
SUPPORT_UID = "landsd/233218:0"


def sha(path):
    return digest(Path(path).read_bytes())


def rel(path):
    return str(Path(path).relative_to(ROOT))


def call(args):
    subprocess.run(args, cwd=ROOT, check=True)


def start():
    claim = reservations.claim("codex-xl-remaining-install-" + str(uuid.uuid4()),
                               ["building:" + uid for uid in sorted(UIDS | {SUPPORT_UID})], batch=BATCH)
    assert claim["ok"], claim
    save(LOCAL / "install-reservation.json", json.loads(json.dumps(claim["reservation"], default=str)))
    call([sys.executable, str(HERE.parent / "shared-modelling/reservations.py"),
          "run", "--lease-file", str(LOCAL / "install-reservation.json"), "--",
          sys.executable, __file__, "owned"])


def owned():
    receipt_path = LOCAL / "install-reservation.json"
    assert reservations.owns(read(receipt_path))
    decision = read(DOC / "decision.json")
    assert set(decision["uids"]) == UIDS and decision["aiCalls"] == decision["geometryChanges"] == 0
    assert sha(DOC / "selection.json.gz") == decision["selectionSHA256"]
    assert sha(DOC.parent / "context.json") == decision["contextSHA256"]
    assert decision["supportUid"] == SUPPORT_UID
    assert sha(DOC.parent / "support-probe.json") == decision["supportProofSHA256"]
    for name in ("metrics", "validation"):
        assert sha(DOC / (name + ".json")) == decision[name + "SHA256"]
    for path, expected in decision["inputHashes"].items():
        assert sha(ROOT / path) == expected, path
    assert sha(STAGE / "catalogue.json") == decision["catalogueSHA256"]
    assert sha(STAGE / "plan.json") == decision["planSHA256"]
    catalogue = read(STAGE / "catalogue.json")
    assert {model["uid"] for model in catalogue["models"]} == UIDS
    assert all(sha(STAGE / model["asset"]) == model["sha256"] for model in catalogue["models"])
    direct.browser_verified(DOC / "staged-browser.json", UIDS)

    pointer_path = ROOT / "docs/astra-city/model-integration-20260909/current-source-review.json"
    pointer = read(pointer_path)
    inventory = read(ROOT / pointer["inventory"])
    parts = {part["uid"]: part for part in inventory["parts"]}
    for model in catalogue["models"]:
        previous = parts.get(model["uid"], {})
        parts[model["uid"]] = {
            "uid": model["uid"], "name": model["label"],
            "landmarkIds": previous.get("landmarkIds", []), "objectId": model["objectId"],
            "csuid": model["buildingCSUID"], "candidate": {"sha256": model["sha256"]},
            "sourceProgress": "prepared-for-review",
            "classification": "script-verified-original-government-xl-direct",
            "knownHold": False,
        }
    ordered = sorted(parts.values(), key=lambda item: item["uid"])
    snapshot = digest(jobs.encode([ordered, decision]).encode())[:16]
    inventory_path = pointer_path.parent / f"source-review-inventory-{snapshot}.json"
    save(inventory_path, {**inventory, "snapshotId": snapshot, "derivedFrom": pointer["snapshotId"],
                          "parts": ordered, "qualification": "Four unchanged government XL towers accepted with exact identity, retained solid podium support, runtime and staged browser checks. No geometry changes or per-model AI."})
    ledger.seed(inventory_path, inherit=pointer["snapshotId"])
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    effort = {"method": "scripted", "ai_model": None, "reasoning_effort": "not-applicable",
              "issue": "HKS-203", "run_id": snapshot, "output_ref": rel(DOC / "decision.json")}
    observation = ("Exact unchanged government XL tower. Object ID, Building CSUID, source hash, "
                   "projected identity and unique unchanged podium support passed scripted checks. "
                   "The podium remains visible. Mobile budget and staged/live desktop/mobile day/night, "
                   "picking, collision, fallback and retry checks passed. No AI model review or geometry edits.")
    ledger.record_many(snapshot, receipt_path,
                       [(uid, "approved-for-integration", DOC / "decision.json", observation, commit)
                        for uid in sorted(UIDS)], effort=effort,
                       request_id=BATCH + "-approved-" + snapshot)

    publication = [sys.executable, str(HERE.parent / "model-integration-20260909/publish.py"),
                   rel(STAGE / "plan.json"), "--receipt", str(receipt_path), "--phase", BATCH]
    call(publication)
    manifest = ROOT / "3d-viewer/city/data/manifest.json"
    before = manifest.read_bytes()
    (LOCAL / "manifest-before.json").write_bytes(before)
    call(publication + ["--apply"])
    try:
        call(["node", str(HERE / "resolution-browser.mjs"), "live", rel(STAGE / "browser-config.json")])
        direct.browser_verified(DOC / "live-browser.json", UIDS)
    except BaseException:
        manifest.write_bytes(before)
        shutil.rmtree(ROOT / "3d-viewer/city/data/official-models" / BATCH, ignore_errors=True)
        raise

    installed = {**decision, "snapshot": snapshot,
                 "liveBrowserSHA256": sha(DOC / "live-browser.json"),
                 "manifestSHA256": sha(manifest)}
    save(DOC / "installed-acceptance.json", installed)
    ledger.record_many(snapshot, receipt_path,
                       [(uid, "installed-verified", DOC / "installed-acceptance.json", observation, commit)
                        for uid in sorted(UIDS)], effort=effort,
                       request_id=BATCH + "-installed-" + snapshot)
    assert read(pointer_path) == pointer
    save(pointer_path, {**pointer, "snapshotId": snapshot, "inventory": rel(inventory_path),
                        "previousSnapshots": [*pointer.get("previousSnapshots", []), pointer["snapshotId"]]})
    call([sys.executable, str(HERE.parent / "building-progress/export.py"), "--refresh"])
    call(["node", str(ROOT / "3d-viewer/scripts/build_progress.mjs")])
    with connect() as connection:
        connection.execute("SET TRANSACTION READ ONLY")
        rows = connection.execute("SELECT uid,review_state,source_sha256 FROM astra_modelling.model_reviews "
                                  "WHERE snapshot_id=%s AND uid=ANY(%s)",
                                  (snapshot, sorted(UIDS))).fetchall()
    assert {uid for uid, state, _ in rows if state == "installed-verified"} == UIDS
    save(DOC / "summary.json", {"installedUids": sorted(UIDS), "snapshot": snapshot,
                                "aiCalls": 0, "geometryChanges": 0,
                                "progress": read(ROOT / "3d-viewer/city/data/building-progress.json")})
    print(json.dumps({"installed": sorted(UIDS), "snapshot": snapshot, "aiCalls": 0}), flush=True)


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 else start()
