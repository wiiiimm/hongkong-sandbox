"""Install unchanged Phase One XL source after bounded contact and browser gates."""

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

spec = importlib.util.spec_from_file_location("direct_import_school_mask", HERE / "integrate.py")
direct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(direct)

BATCH = "government-xl-phase-one-20260927"
DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/phase-one-browser-20260927"
LOCAL = HERE / "local/government-xl-phase-one-install-20260927"
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
    claim = reservations.claim("codex-xl-phase-one-install-" + str(uuid.uuid4()),
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
    for key, evidence in acceptance["evidence"].items():
        assert sha(ROOT / evidence["path"]) == evidence["sha256"], key
    contact = acceptance["contactResolution"]
    assert contact["buriedVertexFraction"] <= .01
    assert contact["buriedAreaFraction"] <= .001
    assert contact["fullyBuriedUpwardTriangles"] == 0
    assert contact["visibleContactHullCoverage"] >= .8
    stage = read(DOC / "stage.json")
    uids = acceptance["uids"]
    assert len(uids) == 1 and stage["uids"] == uids
    assert sha(STAGE / "catalogue.json") == stage["catalogueSHA256"]
    assert sha(STAGE / "plan.json") == stage["planSHA256"]
    catalogue = read(STAGE / "catalogue.json")
    assert {model["uid"] for model in catalogue["models"]} == set(uids)
    assert catalogue["models"][0]["sha256"] == acceptance["sourceSHA256"]
    assert all(sha(STAGE / model["asset"]) == model["sha256"] and
               model["publicationApproved"] and model["placementReviewed"] and
               model["identityReviewApproved"] for model in catalogue["models"])
    patch_plan = read(STAGE / "plan.json")["topLevelTerrainPatches"]
    assert len(patch_plan) == 1 and sha(ROOT / patch_plan[0]["source"]) == patch_plan[0]["sha256"]
    assert patch_plan[0]["sha256"] == acceptance["candidatePatch"]["sha256"] == stage["terrainSHA256"]
    direct.browser_verified(DOC / "staged-browser.json", set(uids))
    decision = {"policy": "Install unchanged Phase One source after exact identity, measured bounded buried-base contact, source preservation, runtime, neighbour and staged browser checks.",
                "uids": uids, "sourceSHA256s": {model["uid"]: model["sha256"] for model in catalogue["models"]},
                "catalogueSHA256": stage["catalogueSHA256"], "planSHA256": stage["planSHA256"],
                "patchSHA256": patch_plan[0]["sha256"],
                "acceptanceSHA256": sha(DOC / "acceptance.json"),
                "evidenceSHA256s": {key: value["sha256"] for key, value in acceptance["evidence"].items()},
                "contactResolution": contact,
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
                               "classification": "script-verified-original-government-xl-bounded-terrain-contact",
                               "knownHold": False}
    ordered = sorted(parts.values(), key=lambda part: part["uid"])
    snapshot = digest(jobs.encode([ordered, decision]).encode())[:16]
    inventory_path = pointer_path.parent / f"source-review-inventory-{snapshot}.json"
    save(inventory_path, {**inventory, "snapshotId": snapshot,
                          "derivedFrom": pointer["snapshotId"], "parts": ordered,
                          "qualification": "One unchanged government Phase One XL source accepted by exact source identity, measured buried-base contact, runtime, neighbour and browser checks; no AI review or geometry edits."})
    ledger.seed(inventory_path, inherit=pointer["snapshotId"])
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    effort = {"method": "scripted", "ai_model": None, "reasoning_effort": "not-applicable",
              "issue": "HKS-203", "run_id": snapshot, "output_ref": rel(DOC / "decision.json")}
    observation = ("One unchanged original government Phase One source installed with a complete source terrain patch. "
                   "Exact identity, measured bounded buried-base contact, source hashes, "
                   "runtime, neighbouring forms and staged/live browser checks pass. No AI modelling or geometry edit.")
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
