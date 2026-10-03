"""Publish the exact V City/Century Gateway government assembly after deterministic acceptance."""
import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
spec = importlib.util.spec_from_file_location("second", Path(__file__).with_name("xl-second-pass.py"))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
ROOT, HERE = s.ROOT, s.HERE
read, save, h, rel = s.read, s.save, s.h, s.rel
CHECK = s.DOC / "third-pass/terrain-v-city"
DOC = s.DOC / "third-pass/terrain-v-city-install"
LOCAL = s.LOCAL / "third-pass-v-city-assembly"
INSTALL_LOCAL = s.LOCAL / "third-pass-v-city-assembly-install"
STAGE = HERE / "accepted/government-xl-v-city-assembly-20260914"
BATCH = "government-xl-v-city-assembly-20260914"
PRIMARY = "landsd/230643:0"
STATION = "landsd/243886:0"
REPRESENTATIVE = {PRIMARY, STATION, "landsd/248373:0", "landsd/308947:0"}

sys.path.insert(0, str(HERE.parent / "model-review-ledger"))
import ledger


def call(args):
    subprocess.run(args, cwd=ROOT, check=True)


def browser_verified(name):
    report = read(CHECK / name)
    assert report.get("passed") and not report["errors"]
    expected = {(uid, width, time) for uid in REPRESENTATIVE for width in (1280, 390) for time in ("15:00", "22:00")}
    actual = {(view["uid"], view["width"], view["time"]) for view in report["views"] if "time" in view}
    assert actual == expected
    assert {view["uid"] for view in report["views"] if view.get("fallbackRetained")} == {PRIMARY}
    assert report["aiCalls"] == 0 and not report["architectureReview"]
    for view in report["views"]:
        if "time" in view:
            assert view["active"] and view["visible"] and view["fullyFramed"]
            assert view["pick"] == view["uid"] and view["collision"] == view["uid"]
            assert not view["overflow"] and abs(view["ground"] - view["groundSampler"]) <= .004
    return report


def start():
    result = read(CHECK / "assembly-result.json")
    assert result["passed"] and result["models"] == 11 and result["aiCalls"] == result["modelGeometryChanges"] == 0
    resources = read(LOCAL / "reservation.json")["resources"]
    claim = s.reservations.claim("codex-xl-v-city-import-" + str(uuid.uuid4()), resources, batch=BATCH)
    assert claim["ok"], claim
    receipt = INSTALL_LOCAL / "reservation.json"
    save(receipt, json.loads(json.dumps(claim["reservation"], default=str)))
    call([sys.executable, str(HERE.parent / "shared-modelling/reservations.py"), "run", "--lease-file", str(receipt), "--", sys.executable, __file__, "owned"])


def owned():
    receipt = INSTALL_LOCAL / "reservation.json"
    assert s.reservations.owns(read(receipt))
    catalogue = read(STAGE / "catalogue.json")
    ids = {model["uid"] for model in catalogue["models"]}
    assert len(ids) == len(catalogue["models"]) == 11 and {PRIMARY, STATION} <= ids
    assert all(h(STAGE / model["asset"]) == model["sha256"] for model in catalogue["models"])
    assert all(model["placementReviewed"] and model["sourceIdentityReviewed"] and model["identityReviewApproved"] for model in catalogue["models"])

    result = read(CHECK / "assembly-result.json")
    assert result["passed"] and result["models"] == 11 and not result["reasons"] and not result["blockedNeighbours"]
    assert result["policy"] == "original-government-v-city-assembly-v1"
    assert result["aiCalls"] == result["modelGeometryChanges"] == 0
    budget = read(CHECK / "assembly-budget.json")
    assert budget["measured"] == result["groupBudget"] and budget["measured"]["mobilePassed"]
    identity = read(CHECK / "assembly-identity.json")
    assert identity["primaryDetailedProof"]["passed"] and all(row["passed"] for row in identity["rows"])
    contact = read(CHECK / "native-support-contact.json")
    assert len(contact["rows"]) == 9 and all(row["rimSamples"] > 0 and row["minDistance"] <= .5 for row in contact["rows"])
    station = read(CHECK / "station-source-terrain.json")
    assert station["uid"] == STATION and station["passed"] and station["fullyBuriedTriangles"] == 0
    recovery = read(CHECK / "support-source-recovery.json")
    assert recovery["acquisition"]["expectedModels"] == 10 and len(recovery["models"]) == 10
    assert recovery["aiCalls"] == recovery["modelGeometryChanges"] == 0
    metrics = read(CHECK / "assembly-metrics.json")
    assert len(metrics["rows"]) == 11 and all(row["sourcePreserved"] and not row["missingTerrain"] for row in metrics["rows"])
    assert metrics["aiCalls"] == metrics["geometryChanges"] == 0
    validation = read(CHECK / "assembly-validation.json")
    assert validation["loaderAccepted"] == validation["checksPassed"] == 11 and validation["exceptions"] == 0
    neighbours = read(CHECK / "neighbour-checks.json")
    assert neighbours["aiCalls"] == 0 and not neighbours["patches"][0]["blockedBy"]
    browser_verified("staged-browser.json")

    evidence_paths = [
        CHECK / "assembly-result.json", CHECK / "assembly-budget.json", CHECK / "assembly-identity.json",
        CHECK / "assembly-metrics.json", CHECK / "assembly-validation.json", CHECK / "native-support-contact.json",
        CHECK / "station-source-terrain.json", CHECK / "support-source-recovery.json", CHECK / "neighbour-checks.json",
        CHECK / "staged-browser.json", HERE / "xl-stage-v-city-assembly.py", HERE / "xl-v-city-support.mjs",
        HERE / "xl-v-city-supports.py", HERE / "xl-v-city-import.py", HERE / "resolution-browser.mjs",
    ]
    evidence = {rel(path): h(path) for path in evidence_paths}
    inputs = {**metrics["inputHashes"], **neighbours["sourceInputHashes"]}
    for path, sha in inputs.items():
        assert h(ROOT / path) == sha, "Accepted source/terrain input changed: " + path
    decision = {
        "policy": result["policy"], "primaryUid": PRIMARY, "modelCount": 11,
        "sourceModels": [{"uid": model["uid"], "sha256": model["sha256"]} for model in catalogue["models"]],
        "catalogueSHA256": h(STAGE / "catalogue.json"), "planSHA256": h(STAGE / "plan.json"),
        "inputHashes": inputs, "evidenceHashes": evidence, "aiCalls": 0, "modelGeometryChanges": 0,
    }
    save(DOC / "decision.json", decision)

    pointer_path = ROOT / "docs/astra-city/model-integration-20260909/current-source-review.json"
    pointer = read(pointer_path)
    inventory = read(ROOT / pointer["inventory"])
    parts = {part["uid"]: part for part in inventory["parts"]}
    for model in catalogue["models"]:
        previous = parts.get(model["uid"], {})
        parts[model["uid"]] = {
            "uid": model["uid"], "name": model["label"], "landmarkIds": previous.get("landmarkIds", []),
            "objectId": model["objectId"], "csuid": model["buildingCSUID"],
            "candidate": {"sha256": model["sha256"]}, "sourceProgress": "prepared-for-review",
            "classification": "script-verified-original-government-v-city-assembly", "knownHold": False,
        }
    ordered = sorted(parts.values(), key=lambda row: row["uid"])
    snapshot = s.digest(s.jobs.encode([ordered, decision]).encode())[:16]
    inventory_path = pointer_path.parent / f"source-review-inventory-{snapshot}.json"
    save(inventory_path, {**inventory, "snapshotId": snapshot, "derivedFrom": pointer["snapshotId"], "parts": ordered})
    ledger.seed(inventory_path, inherit=pointer["snapshotId"])
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    effort = {"method": "scripted", "ai_model": None, "reasoning_effort": "not-applicable", "issue": "HKS-203", "run_id": snapshot, "output_ref": rel(DOC / "decision.json")}
    observation = "Exact unchanged government V City, Century Gateway and Tuen Mun Station source assembly passed identity, native support contact, same-sheet station foundation, neighbour, mobile budget, staged/live browser, picking, collision and fallback/retry checks. No AI modelling, review, simplification or model geometry edits."
    ledger.record_many(snapshot, receipt, [(uid, "approved-for-integration", DOC / "decision.json", observation, commit) for uid in sorted(ids)], effort=effort, request_id=BATCH + "-approved-" + snapshot)

    publish = [sys.executable, str(HERE.parent / "model-integration-20260909/publish.py"), rel(STAGE / "plan.json"), "--receipt", str(receipt), "--phase", BATCH]
    call(publish)
    manifest = ROOT / "3d-viewer/city/data/manifest.json"
    before = manifest.read_bytes()
    (INSTALL_LOCAL / "manifest-before.json").write_bytes(before)
    call(publish + ["--apply"])
    try:
        call(["node", str(HERE / "resolution-browser.mjs"), "live", rel(STAGE / "browser-config.json")])
        browser_verified("live-browser.json")
    except BaseException:
        manifest.write_bytes(before)
        shutil.rmtree(ROOT / "3d-viewer/city/data/official-models" / BATCH, ignore_errors=True)
        shutil.rmtree(ROOT / "docs/astra-city/model-integration-20260909" / BATCH, ignore_errors=True)
        raise

    acceptance = {**decision, "snapshot": snapshot, "liveBrowserSHA256": h(CHECK / "live-browser.json"), "manifestSHA256": h(manifest)}
    save(DOC / "installed-acceptance.json", acceptance)
    ledger.record_many(snapshot, receipt, [(uid, "installed-verified", DOC / "installed-acceptance.json", observation, commit) for uid in sorted(ids)], effort=effort, request_id=BATCH + "-installed-" + snapshot)
    assert read(pointer_path) == pointer
    save(pointer_path, {**pointer, "snapshotId": snapshot, "inventory": rel(inventory_path), "previousSnapshots": [*pointer.get("previousSnapshots", []), pointer["snapshotId"]]})
    call([sys.executable, str(HERE.parent / "building-progress/export.py"), "--refresh"])
    call(["node", str(ROOT / "3d-viewer/scripts/build_progress.mjs")])
    save(DOC / "summary.json", {"installedUids": sorted(ids), "primaryUid": PRIMARY, "supportingModels": 10, "snapshot": snapshot, "aiCalls": 0, "modelGeometryChanges": 0, "progress": read(ROOT / "3d-viewer/city/data/building-progress.json")})
    print(json.dumps({"installed": len(ids), "primary": PRIMARY, "snapshot": snapshot, "aiCalls": 0}), flush=True)


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 else start()
