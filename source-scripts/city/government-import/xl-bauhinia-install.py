"""Install four unchanged Bauhinia Garden XL sources after all scripted gates."""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from run import ROOT, HERE, read, save, digest, reservations, jobs, connect

sys.path.insert(0, str(HERE.parent / "model-review-ledger"))
import ledger

spec = importlib.util.spec_from_file_location("direct_import_bauhinia", HERE / "integrate.py")
direct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(direct)

BATCH = "government-xl-bauhinia-20260924"
DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/bauhinia-terrain-diagnostic-20260924"
LOCAL = HERE / "local/government-xl-bauhinia-terrain-20260924"
STAGE = HERE / "accepted" / BATCH
CHROME = "/home/williamli/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell"


def sha(path):
    return digest(Path(path).read_bytes())


def rel(path):
    return str(Path(path).resolve().relative_to(ROOT))


def call(args):
    subprocess.run(args, cwd=ROOT, check=True, env={**os.environ, "CHROME_PATH": CHROME})


def start():
    uids = read(DOC / "acceptance.json")["uids"]
    claim = reservations.claim("codex-xl-bauhinia-install-" + str(uuid.uuid4()),
                               ["building:" + uid for uid in uids] + ["terrain-patch:" + uids[0]],
                               batch=BATCH)
    assert claim["ok"], claim
    receipt_path = LOCAL / "install-reservation.json"
    save(receipt_path, json.loads(json.dumps(claim["reservation"], default=str)))
    call([sys.executable, str(HERE.parent / "shared-modelling/reservations.py"),
          "run", "--lease-file", str(receipt_path), "--", sys.executable, __file__, "owned"])


def owned():
    receipt_path = LOCAL / "install-reservation.json"
    assert reservations.owns(read(receipt_path))
    acceptance = read(DOC / "acceptance.json")
    assert acceptance["passed"] and acceptance["failures"] == []
    assert acceptance["aiCalls"] == acceptance["modelGeometryChanges"] == 0
    stage = read(DOC / "stage.json")
    uids = acceptance["uids"]
    assert len(uids) == 4 and stage["uids"] == uids
    assert sha(STAGE / "catalogue.json") == stage["catalogueSHA256"]
    assert sha(STAGE / "plan.json") == stage["planSHA256"]
    catalogue = read(STAGE / "catalogue.json")
    assert {model["uid"] for model in catalogue["models"]} == set(uids)
    assert all(sha(STAGE / model["asset"]) == model["sha256"] and
               model["publicationApproved"] and model["placementReviewed"] and
               model["identityReviewApproved"] for model in catalogue["models"])
    patch_plan = read(STAGE / "plan.json")["topLevelTerrainPatches"]
    assert len(patch_plan) == 1 and sha(ROOT / patch_plan[0]["source"]) == patch_plan[0]["sha256"]
    direct.browser_verified(DOC / "staged-browser.json", set(uids))
    decision = {"policy": "Install unchanged government towers only after exact-source terrain, identity, runtime, neighbour and staged browser checks.",
                "uids": uids, "sourceSHA256s": {model["uid"]: model["sha256"] for model in catalogue["models"]},
                "catalogueSHA256": stage["catalogueSHA256"], "planSHA256": stage["planSHA256"],
                "patchSHA256": patch_plan[0]["sha256"],
                "acceptanceSHA256": sha(DOC / "acceptance.json"),
                "metricsSHA256": sha(DOC / "metrics.json"),
                "validationSHA256": sha(DOC / "validation.json"),
                "neighbourSHA256": sha(DOC / "neighbour-checks.json"),
                "nativeNeighbourSHA256": sha(DOC / "native-neighbour-checks.json"),
                "stagedBrowserSHA256": sha(DOC / "staged-browser.json"),
                "aiCalls": 0, "geometryChanges": 0}
    save(DOC / "decision.json", decision)

    pointer_path = ROOT / "docs/astra-city/model-integration-20260909/current-source-review.json"
    pointer = read(pointer_path)
    inventory = read(ROOT / pointer["inventory"])
    parts = {part["uid"]: part for part in inventory["parts"]}
    for model in catalogue["models"]:
        previous = parts.get(model["uid"], {})
        parts[model["uid"]] = {"uid": model["uid"], "name": model["label"],
                               "landmarkIds": previous.get("landmarkIds", []),
                               "objectId": model["objectId"], "csuid": model["buildingCSUID"],
                               "candidate": {"sha256": model["sha256"]},
                               "sourceProgress": "prepared-for-review",
                               "classification": "script-verified-original-government-xl-native-terrain",
                               "knownHold": False}
    ordered = sorted(parts.values(), key=lambda part: part["uid"])
    snapshot = digest(jobs.encode([ordered, decision]).encode())[:16]
    inventory_path = pointer_path.parent / f"source-review-inventory-{snapshot}.json"
    save(inventory_path, {**inventory, "snapshotId": snapshot,
                          "derivedFrom": pointer["snapshotId"], "parts": ordered,
                          "qualification": "Four unchanged Bauhinia Garden XL towers accepted by exact government source terrain, identity, runtime, neighbour and browser checks; no AI review or geometry edits."})
    ledger.seed(inventory_path, inherit=pointer["snapshotId"])
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    effort = {"method": "scripted", "ai_model": None, "reasoning_effort": "not-applicable",
              "issue": "HKS-203", "run_id": snapshot, "output_ref": rel(DOC / "decision.json")}
    observation = ("Four unchanged original Bauhinia Garden sources installed with one shared government terrain patch. "
                   "Exact identity, terrain, source hashes, runtime, all 24 neighbouring forms and staged/live "
                   "browser checks pass. No AI model review or geometry edit.")
    ledger.record_many(snapshot, receipt_path,
                       [(uid, "approved-for-integration", DOC / "decision.json", observation, commit)
                        for uid in uids], effort=effort, request_id=BATCH + "-approved-" + snapshot)
    publication = [sys.executable, str(HERE.parent / "model-integration-20260909/publish.py"),
                   rel(STAGE / "plan.json"), "--receipt", str(receipt_path), "--phase", BATCH]
    call(publication)
    manifest = ROOT / "3d-viewer/city/data/manifest.json"
    before = manifest.read_bytes()
    (LOCAL / "manifest-before.json").write_bytes(before)
    call(publication + ["--apply"])
    try:
        call(["node", str(HERE / "resolution-browser.mjs"), "live", rel(STAGE / "browser-config.json")])
        direct.browser_verified(DOC / "live-browser.json", set(uids))
    except BaseException:
        manifest.write_bytes(before)
        shutil.rmtree(ROOT / "3d-viewer/city/data/official-models" / BATCH, ignore_errors=True)
        (ROOT / "3d-viewer" / patch_plan[0]["destination"]).unlink(missing_ok=True)
        raise
    installed = {**decision, "snapshot": snapshot,
                 "liveBrowserSHA256": sha(DOC / "live-browser.json"),
                 "manifestSHA256": sha(manifest)}
    save(DOC / "installed-acceptance.json", installed)
    ledger.record_many(snapshot, receipt_path,
                       [(uid, "installed-verified", DOC / "installed-acceptance.json", observation, commit)
                        for uid in uids], effort=effort, request_id=BATCH + "-installed-" + snapshot)
    assert read(pointer_path) == pointer
    save(pointer_path, {**pointer, "snapshotId": snapshot, "inventory": rel(inventory_path),
                        "previousSnapshots": [*pointer.get("previousSnapshots", []), pointer["snapshotId"]]})
    call([sys.executable, str(HERE.parent / "building-progress/export.py"), "--refresh"])
    call(["node", str(ROOT / "3d-viewer/scripts/build_progress.mjs")])
    with connect() as connection:
        connection.execute("SET TRANSACTION READ ONLY")
        rows = connection.execute("SELECT uid,review_state FROM astra_modelling.model_reviews "
                                  "WHERE snapshot_id=%s AND uid=ANY(%s)", (snapshot, uids)).fetchall()
    assert {uid for uid, state in rows if state == "installed-verified"} == set(uids)
    save(DOC / "summary.json", {"installedUids": uids, "snapshot": snapshot,
                                "aiCalls": 0, "geometryChanges": 0,
                                "progress": read(ROOT / "3d-viewer/city/data/building-progress.json")})
    print(json.dumps({"installed": uids, "snapshot": snapshot, "aiCalls": 0}), flush=True)


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 else start()
