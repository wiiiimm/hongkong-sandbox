"""Account for the final three published Lantau government forms in Neon.

The viewer assets and browser acceptance must already have been committed. This
script changes only the source-review snapshot, review states, and progress data.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "source-scripts/city/model-review-ledger"))
sys.path.insert(0, str(ROOT / "source-scripts/city/shared-modelling"))

import ledger
import reservations


POINTER = ROOT / "docs/astra-city/model-integration-20260909/current-source-review.json"
MANIFEST = ROOT / "3d-viewer/city/data/manifest.json"
PROOF = ROOT / "docs/astra-city/government-import/government-lantau-final-install-20260921/terminal-summary.json"
PUBLICATIONS = (
    (
        "government-lantau-ngong-component-20260921",
        "source-scripts/city/government-import/local/government-lantau-ngong-component-20260921/reservation.json",
    ),
    (
        "government-lantau-visible-placement-20260921",
        "source-scripts/city/government-import/local/government-lantau-visible-placement-20260921/reservation.json",
    ),
)


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    previous = read(POINTER)
    inventory = read(ROOT / previous["inventory"])
    assert previous["snapshotId"] == inventory["snapshotId"]
    manifest_sha = digest(MANIFEST)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    sources = {}
    receipts = []
    for batch, receipt_name in PUBLICATIONS:
        catalogue_path = ROOT / "3d-viewer/city/data/official-models" / batch / "catalogue.json"
        acceptance_path = ROOT / "docs/astra-city/government-import" / batch / "installed-acceptance.json"
        catalogue = read(catalogue_path)
        acceptance = read(acceptance_path)
        assert acceptance["manifestSHA256"] == manifest_sha
        assert acceptance["aiModellingCalls"] == 0
        assert sorted(acceptance["installedUids"]) == sorted(model["uid"] for model in catalogue["models"])
        for model in catalogue["models"]:
            uid = model["uid"]
            assert model["sha256"] == acceptance["sourceAssets"][uid]
            assert digest(catalogue_path.parent / model["asset"]) == model["sha256"]
            assert uid not in sources
            sources[uid] = (model["sha256"], acceptance_path, batch)
        receipt_path = ROOT / receipt_name
        receipt = read(receipt_path)
        assert set(receipt["resources"]) == {"building:" + uid for uid in acceptance["installedUids"]}
        assert reservations.heartbeat(receipt, ttl=3600)["ok"], "Source reservation expired"
        receipts.append((batch, receipt_path, receipt))

    assert set(sources) == {"landsd/112959:0", "landsd/168823:0", "landsd/182471:0"}
    parts = {part["uid"]: part for part in inventory["parts"]}
    for uid, (asset_sha, _, _) in sources.items():
        part = parts[uid]
        part["candidate"] = {"sha256": asset_sha}
        part["sourceProgress"] = "prepared-for-review"
        part["classification"] = "script-verified-government-source-install"
        part["knownHold"] = False
    snapshot = hashlib.sha256(json.dumps(
        [previous["snapshotId"], manifest_sha, sorted((uid, source[0]) for uid, source in sources.items())],
        sort_keys=True,
    ).encode()).hexdigest()[:16]
    inventory_path = POINTER.parent / f"source-review-inventory-{snapshot}.json"
    save(inventory_path, {
        **inventory,
        "snapshotId": snapshot,
        "derivedFrom": previous["snapshotId"],
        "parts": sorted(parts.values(), key=lambda part: part["uid"]),
        "qualification": "Three previously held or good-to-go Lantau source forms are installed in the feature-branch viewer after scripted source isolation or visible placement and live browser checks. No AI modelling.",
    })
    ledger.seed(inventory_path, inherit=previous["snapshotId"])
    effort = {
        "method": "scripted",
        "ai_model": None,
        "reasoning_effort": "not-applicable",
        "issue": "HKS-203",
        "run_id": snapshot,
        "output_ref": str(PROOF.relative_to(ROOT)),
    }
    for batch, receipt_path, _ in receipts:
        entries = []
        for uid, (_, acceptance_path, source_batch) in sorted(sources.items()):
            if source_batch == batch:
                entries.append((
                    uid,
                    "installed-verified",
                    acceptance_path,
                    "Published source asset passed identity, placement, terrain, runtime, and live desktop/mobile browser checks. Scripted source processing; no AI modelling.",
                    commit,
                ))
        ledger.record_many(
            snapshot, receipt_path, entries, effort=effort,
            request_id=f"{batch}-installed-{snapshot}",
        )
    with ledger.connect() as connection:
        states = dict(connection.execute(
            "SELECT uid, review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)",
            (snapshot, sorted(sources)),
        ).fetchall())
    assert states == {uid: "installed-verified" for uid in sources}
    assert read(POINTER) == previous
    save(POINTER, {
        **previous,
        "snapshotId": snapshot,
        "inventory": str(inventory_path.relative_to(ROOT)),
        "previousSnapshots": [*previous.get("previousSnapshots", []), previous["snapshotId"]],
    })
    subprocess.run([sys.executable, str(ROOT / "source-scripts/city/building-progress/export.py"), "--refresh"], cwd=ROOT, check=True)
    subprocess.run(["node", str(ROOT / "3d-viewer/scripts/build_progress.mjs")], cwd=ROOT, check=True)
    save(PROOF, {
        "snapshotId": snapshot,
        "installedUids": sorted(sources),
        "reviewStates": states,
        "manifestSHA256": manifest_sha,
        "installationCommit": commit,
        "neonVerified": True,
        "aiModellingCalls": 0,
        "progress": read(ROOT / "3d-viewer/city/data/building-progress.json"),
    })
    for _, _, receipt in receipts:
        assert reservations.release(receipt)["ok"]
    print(json.dumps({"snapshot": snapshot, "installed": len(sources), "neonVerified": True, "aiModellingCalls": 0}))


if __name__ == "__main__":
    main()
