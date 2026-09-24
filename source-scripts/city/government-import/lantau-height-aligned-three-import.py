"""Publish five recovered Lantau government sources with guarded compute-only checks."""
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
SOURCE_BATCH = "government-lantau-final-14-20260921"
BATCH = "government-lantau-height-aligned-3-20260921"
SOURCE_DOC = ROOT / "docs/astra-city/government-import" / SOURCE_BATCH
DOC = ROOT / "docs/astra-city/government-import" / BATCH
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


def verify_browser(path, uids, config):
    report = read(path)
    assert report.get("passed") and report.get("errors") == []
    expected = {(uid, width, time) for uid in uids for width in (1280, 390) for time in ("15:00", "22:00")}
    actual = {(row["uid"], row["width"], row["time"]) for row in report["views"] if "time" in row}
    assert actual == expected
    assert {row["uid"] for row in report["views"] if row.get("fallbackRetained")} == uids
    tolerances = config.get("samplerToleranceByModel", {})
    missing_allowed = set(config.get("allowMissingRenderedGroundUids", []))
    for row in report["views"]:
        if "time" not in row:
            continue
        assert row["active"] and row["visible"]
        if config.get("fitBoxByModel", {}).get(row["uid"], config.get("fitBox", False)):
            assert row["fullyFramed"]
        assert row["pick"] == row["uid"] and row["collision"] == row["uid"]
        assert not row["overflow"]
        if row["ground"] is None:
            assert row["uid"] in missing_allowed
        else:
            assert abs(row["ground"] - row["groundSampler"]) <= tolerances.get(row["uid"], 0.004)
    return report


def start():
    all_uids = sorted(read(DOC / "result.json")["installedCandidates"])
    assert len(all_uids) == 3 and len(set(all_uids)) == 3
    claim = reservations.claim(
        "codex-discovery-bay-held-" + str(uuid.uuid4()),
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
    source_selection = read(DOC / "selection.json.gz")
    source_rows = {row["uid"]: row for row in source_selection["rows"]}
    assert source_selection["manifestSHA256"] == digest(ROOT / "3d-viewer/city/data/manifest.json")
    assert result["assemblyProofSHA256"] == digest(DOC / "assembly-proof.json")
    assert result["metricsSHA256"] == digest(DOC / "metrics.json")
    assert result["validationSHA256"] == digest(DOC / "validation.json")
    assert len(source_rows) == result["models"] == 3
    held = set()
    assert result["held"] == [] and set(result["installedCandidates"]) == set(source_rows)
    assert result["failures"] == [] and result["aiCalls"] == result["modelGeometryChanges"] == 0
    assert not result["publication"]
    catalogue = read(STAGE / "catalogue.json")
    models = {model["uid"]: model for model in catalogue["models"]}
    installed = set(models)
    all_uids = installed | held
    assert all_uids == set(source_rows) and not (installed & held)
    assert all(digest(STAGE / model["asset"]) == model["sha256"] for model in models.values())
    assert all(model["placementReviewed"] and model["sourceIdentityReviewed"] and model["identityReviewApproved"] for model in models.values())
    assert all(model["retainsBasicForm"] and model["proceduralWindows"] is False for model in models.values())

    metrics = read(DOC / "metrics.json")
    assert len(metrics["rows"]) == len(installed) and metrics["aiCalls"] == metrics["geometryChanges"] == 0
    metric_by_uid = {row["uid"]: row for row in metrics["rows"]}
    assert set(metric_by_uid) == installed
    supported_sampler = set(result["supportedSamplerUids"])
    missing_ground = set(result["missingRenderedGroundUids"])
    for uid, metric in metric_by_uid.items():
        assert metric["sourcePreserved"] and not metric.get("error")
        assert metric["budget"]["residentBytes"] <= metrics["profiles"]["mobile"]["residentBytes"]
        if uid not in missing_ground:
            assert metric["missingTerrain"] == 0
        if uid not in supported_sampler:
            assert metric["maxSamplerDelta"] <= 0.004

    validation = read(DOC / "validation.json")
    assert validation["models"] == validation["loaderAccepted"] == validation["checksPassed"] == len(installed)
    assert validation["exceptions"] == 0
    browser_config = read(STAGE / "browser-config.json")
    browser_uids = set(browser_config["browserUids"])
    assert browser_uids == set(result["representativeUids"]) and browser_uids <= installed
    assert set(browser_config["failureTestUids"]) == browser_uids
    verify_browser(DOC / "staged-browser.json", browser_uids, browser_config)

    for model in catalogue["models"]:
        model["publicationApproved"] = True
    save(STAGE / "catalogue.json", catalogue)
    save(STAGE / "catalogue-index.json", {"models": len(installed), "catalogues": ["catalogue.json"]})

    assert all_uids == set(source_rows)
    evidence_paths = {
        "resultSHA256": DOC / "result.json",
        "assemblyProofSHA256": DOC / "assembly-proof.json",
        "metricsSHA256": DOC / "metrics.json",
        "validationSHA256": DOC / "validation.json",
        "stagedBrowserSHA256": DOC / "staged-browser.json",
        "catalogueSHA256": STAGE / "catalogue.json",
        "planSHA256": STAGE / "plan.json",
    }
    decision = {
        "policy": "original-government-lantau-height-aligned-compute-only-v1",
        "sourceBatch": SOURCE_BATCH,
        "publicationBatch": BATCH,
        "modelsProcessed": len(all_uids),
        "installedUids": sorted(installed),
        "heldRows": [],
        "browserRepresentativeUids": sorted(browser_uids),
        "evidenceHashes": {key: digest(path) for key, path in evidence_paths.items()},
        "sourceGeometryPreserved": True,
        "aiCalls": 0,
        "modelGeometryChanges": 0,
        "placementChanges": len(installed),
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
            "classification": "script-verified-original-government-import",
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
            f"The recorded-height placement pass installed {len(installed)} unchanged government sources after "
            "exact identity, visible-roof, retained-basic-support, runtime and browser checks. "
            "No AI review or geometry edits."
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
        "Exact original government source with bounded recorded-height placement passed deterministic identity, visible-roof, retained-basic-support, "
        "runtime and desktop/mobile browser checks. No AI review, remodelling, simplification or source geometry edit."
    )
    ledger.record_many(
        snapshot,
        receipt_path,
        [(uid, "approved-for-integration", DOC / "decision.json", installed_observation, commit) for uid in sorted(installed)],
        effort=effort,
        request_id=BATCH + "-approved-" + snapshot,
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
        verify_browser(DOC / "live-browser.json", browser_uids, browser_config)
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
        "held": len(held),
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
    call([sys.executable, str(HERE.parent / "building-progress/export.py"), "--refresh"])
    call(["node", str(ROOT / "3d-viewer/scripts/build_progress.mjs")])

    terminal_result = {
        "batch": BATCH,
        "modelsProcessed": len(all_uids),
        "newlyInstalled": len(installed),
        "humanCounts": {
            "installed": len(installed),
            "to-do": 0,
            "held-human": 0,
            "held-ai": 0,
            "held-unknown": len(held),
            "in-process": 0,
        },
        "heldReasonCounts": dict(collections.Counter(reason for row in decision["heldRows"] for reason in row["reasons"])),
        "installedUids": sorted(installed),
        "heldRows": decision["heldRows"],
        "snapshotId": snapshot,
        "evidence": relative(DOC / "installed-acceptance.json"),
        "aiCalls": 0,
        "geometryChanges": 0,
    }
    stage_name = "government-lantau-height-aligned-three-terminal-v1"
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
    assert all(states[uid] == ("installed-verified" if uid in installed else "held") for uid in all_uids)
    save(DOC / "terminal-summary.json", {
        **terminal_result,
        "jobId": job_id,
        "neonVerified": True,
        "reviewStates": dict(collections.Counter(states.values())),
        "progress": read(ROOT / "3d-viewer/city/data/building-progress.json"),
    })
    released = reservations.release(receipt)
    assert released["ok"]
    print(json.dumps({
        "installed": len(installed),
        "held": len(held),
        "inProcess": 0,
        "snapshot": snapshot,
        "neonVerified": True,
        "aiCalls": 0,
    }), flush=True)


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 else start()
