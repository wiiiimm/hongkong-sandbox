"""Install two script-cleared Disneyland models with one neighbour-preserving terrain patch."""
import collections
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

BATCH = "government-lantau-disney-hotel-pair-20260916"
UIDS = ["landsd/72608:0", "landsd/76821:0"]
BASE = ROOT / "docs/astra-city/government-import/government-lantau-landmarks-16-20260916/second-pass"
CHECK = BASE / "third-pass/terrain-disney-hotel-west"
SOURCE_LOCAL = HERE / "local/government-lantau-landmarks-16-second-20260916/third-pass-terrain-disney-hotel-west"
LOCAL = HERE / "local/government-lantau-landmarks-16-second-20260916/third-pass-terrain-disney-hotel-west-install"
STAGE = HERE / "accepted" / BATCH
DOC = CHECK / "installation"

sys.path.insert(0, str(HERE.parent / "model-review-ledger"))
import ledger

direct_spec = importlib.util.spec_from_file_location("direct", HERE / "integrate.py")
direct = importlib.util.module_from_spec(direct_spec)
direct_spec.loader.exec_module(direct)


def call(args):
    subprocess.run(args, cwd=ROOT, check=True)


def start():
    result = read(CHECK / "preservation-result.json")
    assert result["passed"] and result["models"] == len(UIDS)
    assert result["aiCalls"] == result["modelGeometryChanges"] == 0
    resources = ["building:" + uid for uid in UIDS]
    claim = s.reservations.claim(
        "codex-lantau-disney-pair-import-" + str(uuid.uuid4()),
        resources,
        ttl=1800,
        batch=BATCH,
    )
    assert claim["ok"]
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
    assert s.reservations.owns(read(receipt))
    result = read(CHECK / "preservation-result.json")
    assert result["passed"] and result["models"] == 2 and not result["failures"]
    assert result["preservedOrdinaryForms"] == 8
    assert result["aiCalls"] == result["modelGeometryChanges"] == 0

    selection = read(CHECK / "selection.json.gz")
    rows = {row["uid"]: row for row in selection["rows"]}
    assert set(rows) == set(UIDS)
    metrics = read(CHECK / "metrics.json")
    assert {row["uid"] for row in metrics["rows"]} == set(UIDS)
    assert metrics["aiCalls"] == metrics["geometryChanges"] == 0
    assert all(row["sourcePreserved"] and not row["missingTerrain"] for row in metrics["rows"])
    assert all(row["budget"]["residentBytes"] <= metrics["profiles"]["mobile"]["residentBytes"] for row in metrics["rows"])
    validation = read(CHECK / "validation.json")
    assert validation["models"] == validation["loaderAccepted"] == validation["checksPassed"] == 2
    assert validation["exceptions"] == 0
    allowed = {"sampled-ground-gap-below-model-bottom", "sampled-terrain-above-model-bottom"}
    assert all(set(row.get("concerns", [])) <= allowed for row in validation["results"])
    neighbours = read(CHECK / "neighbour-checks.json")
    assert neighbours["aiCalls"] == 0 and neighbours["patches"][0]["blockedBy"] == []
    native = read(CHECK / "native-neighbour-checks.json")
    assert native["aiCalls"] == native["modelGeometryChanges"] == 0 and not native.get("failed", []) and all(row.get("passed") for row in native.get("rows", []))
    preservation = read(CHECK / "parent-preservation.json")
    protected = sorted({uid for patch in preservation["patches"] for uid in patch["uids"]})
    assert len(protected) == 8

    source_catalogue = read(SOURCE_LOCAL / "candidates/catalogue.json")
    models = {model["uid"]: model for model in source_catalogue["models"]}
    assert set(models) == set(UIDS)
    STAGE.mkdir(parents=True, exist_ok=True)
    for uid in UIDS:
        entry = models[uid]
        entry.update(
            priority="landmark",
            placementReviewed=True,
            sourceIdentityReviewed=True,
            identityReviewApproved=True,
            publicationApproved=True,
            proceduralWindows=False,
            placementReview=(
                "Exact unchanged Hong Kong Disneyland government source matched by object ID and Building CSUID. "
                "The paired native terrain retains current terrain under eight ordinary neighbouring footprints; "
                "source, neighbour, mobile runtime and browser checks pass."
            ),
        )
        asset = STAGE / entry["asset"]
        asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE_LOCAL / "candidates" / entry["asset"], asset)
        assert h(asset) == entry["sha256"]
    catalogue = {
        **source_catalogue,
        "area": "Hong Kong Disneyland paired original government models",
        "loadingPolicy": "Published after deterministic source, terrain, neighbour, runtime and browser checks",
        "models": [models[uid] for uid in UIDS],
    }
    save(STAGE / "catalogue.json", catalogue)
    save(STAGE / "catalogue-index.json", {"models": 2, "catalogues": ["catalogue.json"]})

    source_forms = read(SOURCE_LOCAL / "source-forms.json")
    forms = []
    for uid in UIDS:
        form = dict(source_forms[uid]["building"])
        form["tile"] = Path(source_forms[uid]["tile"]).stem
        forms.append(form)
    save(STAGE / "source-forms.json", forms)

    candidates = read(CHECK / "terrain-candidates.json")
    assert len(candidates) == 1 and set(candidates[0]["uids"]) == set(UIDS)
    patch = candidates[0]
    patch_source = ROOT / patch["path"]
    assert h(patch_source) == patch["sha256"]
    patch_destination = STAGE / patch_source.name
    shutil.copyfile(patch_source, patch_destination)
    terrain = {
        "source": rel(patch_destination),
        "sha256": h(patch_destination),
        "destination": "city/data/" + patch_destination.name,
        "resolution": read(patch_destination)["cell"],
        "area": "Hong Kong Disneyland paired bounded original government terrain",
    }
    catalogue_url = "city/data/official-models/" + BATCH + "/catalogue.json"
    plan = {
        "areas": [{"area": catalogue["area"], "catalogue": rel(STAGE / "catalogue.json"), "destination": catalogue_url}],
        "topLevelTerrainPatches": [terrain],
    }
    save(STAGE / "plan.json", plan)
    save(STAGE / "browser-config.json", {
        "stage": rel(STAGE) + "/",
        "doc": rel(CHECK) + "/",
        "catalogueURL": catalogue_url,
        "terrain": [terrain],
        "fitBox": True,
        "browserUids": UIDS,
        "failureTestUids": UIDS,
        "retainedBuildingUids": protected,
    })

    call(["node", str(HERE / "resolution-browser.mjs"), "staged", rel(STAGE / "browser-config.json")])
    direct.browser_verified(CHECK / "staged-browser.json", set(UIDS))

    for row in selection["rows"]:
        with s.connect() as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            native_rows = dict(connection.execute(
                "SELECT cache_key,result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s",
                (row["native"]["cacheKey"],),
            ))
        assert native_rows[row["native"]["cacheKey"]] == row["native"]["resultSha"]

    decision = {
        "policy": "Install two unchanged paired Disneyland government models after deterministic identity, source-terrain, neighbour-preservation, runtime and browser acceptance.",
        "uids": UIDS,
        "sourceSHA256s": {uid: models[uid]["sha256"] for uid in UIDS},
        "catalogueSHA256": h(STAGE / "catalogue.json"),
        "planSHA256": h(STAGE / "plan.json"),
        "metricsSHA256": h(CHECK / "metrics.json"),
        "validationSHA256": h(CHECK / "validation.json"),
        "neighbourChecksSHA256": h(CHECK / "neighbour-checks.json"),
        "parentPreservationSHA256": h(CHECK / "parent-preservation.json"),
        "stagedBrowserSHA256": h(CHECK / "staged-browser.json"),
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    }
    save(DOC / "decision.json", decision)

    pointer_path = ROOT / "docs/astra-city/model-integration-20260909/current-source-review.json"
    pointer = read(pointer_path)
    inventory = read(ROOT / pointer["inventory"])
    parts = {part["uid"]: part for part in inventory["parts"]}
    for uid in UIDS:
        model = models[uid]
        previous = parts.get(uid, {})
        parts[uid] = {
            "uid": uid,
            "name": model["label"],
            "landmarkIds": previous.get("landmarkIds", []),
            "objectId": model["objectId"],
            "csuid": model["buildingCSUID"],
            "candidate": {"sha256": model["sha256"]},
            "sourceProgress": "prepared-for-review",
            "classification": "script-verified-original-government-landmark-neighbour-preserving-terrain",
            "knownHold": False,
        }
    ordered = sorted(parts.values(), key=lambda row: row["uid"])
    snapshot = s.digest(s.jobs.encode([ordered, decision]).encode())[:16]
    inventory_path = pointer_path.parent / ("source-review-inventory-" + snapshot + ".json")
    save(inventory_path, {**inventory, "snapshotId": snapshot, "derivedFrom": pointer["snapshotId"], "parts": ordered})
    ledger.seed(inventory_path, inherit=pointer["snapshotId"])

    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    effort = {"method": "scripted", "ai_model": None, "reasoning_effort": "not-applicable", "issue": "HKS-203", "run_id": snapshot, "output_ref": rel(DOC / "decision.json")}
    observation = "Exact unchanged paired Disneyland government source installed after deterministic identity, neighbour-preserving terrain, mobile runtime and browser checks. No AI modelling or model geometry edits."
    ledger.record_many(snapshot, receipt, [(uid, "approved-for-integration", DOC / "decision.json", observation, commit) for uid in UIDS], effort=effort, request_id=BATCH + "-approved-" + snapshot)

    publish = [sys.executable, str(HERE.parent / "model-integration-20260909/publish.py"), rel(STAGE / "plan.json"), "--receipt", str(receipt), "--phase", BATCH]
    call(publish)
    manifest = ROOT / "3d-viewer/city/data/manifest.json"
    before = manifest.read_bytes()
    (LOCAL / "manifest-before.json").write_bytes(before)
    call(publish + ["--apply"])
    try:
        call(["node", str(HERE / "resolution-browser.mjs"), "live", rel(STAGE / "browser-config.json")])
        direct.browser_verified(CHECK / "live-browser.json", set(UIDS))
    except BaseException:
        manifest.write_bytes(before)
        shutil.rmtree(ROOT / "3d-viewer/city/data/official-models" / BATCH, ignore_errors=True)
        shutil.rmtree(ROOT / "docs/astra-city/model-integration-20260909" / BATCH, ignore_errors=True)
        (ROOT / "3d-viewer" / terrain["destination"]).unlink(missing_ok=True)
        raise

    acceptance = {**decision, "snapshot": snapshot, "liveBrowserSHA256": h(CHECK / "live-browser.json"), "manifestSHA256": h(manifest)}
    save(DOC / "installed-acceptance.json", acceptance)
    ledger.record_many(snapshot, receipt, [(uid, "installed-verified", DOC / "installed-acceptance.json", observation, commit) for uid in UIDS], effort=effort, request_id=BATCH + "-installed-" + snapshot)
    assert read(pointer_path) == pointer
    save(pointer_path, {**pointer, "snapshotId": snapshot, "inventory": rel(inventory_path), "previousSnapshots": [*pointer.get("previousSnapshots", []), pointer["snapshotId"]]})
    call([sys.executable, str(HERE.parent / "building-progress/export.py"), "--refresh"])
    call(["node", str(ROOT / "3d-viewer/scripts/build_progress.mjs")])

    with direct.connect() as connection:
        connection.execute("SET TRANSACTION READ ONLY")
        states = dict(connection.execute("SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)", (snapshot, UIDS)).fetchall())
    assert set(states) == set(UIDS) and set(states.values()) == {"installed-verified"}
    summary = {
        "installedUids": UIDS,
        "installed": 2,
        "snapshot": snapshot,
        "states": dict(collections.Counter(states.values())),
        "inProcess": 0,
        "aiCalls": 0,
        "modelGeometryChanges": 0,
        "progress": read(ROOT / "3d-viewer/city/data/building-progress.json"),
    }
    save(DOC / "summary.json", summary)
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 else start()
