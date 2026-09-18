"""Persist the terminal human states for the bounded XL-50 government batch."""
from collections import Counter
import importlib.util
import json
import subprocess
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
spec = importlib.util.spec_from_file_location("second", Path(__file__).with_name("xl-second-pass.py"))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)

ROOT, HERE = s.ROOT, s.HERE
DOC = s.DOC / "final-script-pass"
LOCAL = s.LOCAL / "final-script-sync"
BATCH = "government-xl-50-final-script-pass-20260913"
STAGE = "deterministic-xl-terminal-routing-v1"
INSTALLED_UID = "landsd/229310:0"
read, save, h, rel = s.read, s.save, s.h, s.rel

sys.path.insert(0, str(HERE.parent / "model-review-ledger"))
import ledger


def terminal_reasons(row, diagnostic):
    reasons = list(row["reasons"])
    if row["publicationCandidate"]:
        for reason in diagnostic.get("previousReasons", []):
            if reason == "strict-identity-fit":
                reasons.append("strict-viewer-identity-policy-requires-component-resolution")
            elif reason == "existing-review-requires-resolution":
                reasons.append("existing-review-requires-resolution")
            else:
                reasons.append(reason)
        for reason in diagnostic["native"]["reasons"]:
            reasons.append(reason)
    return list(dict.fromkeys(reasons))


def next_step(reasons):
    identity = any("identity" in reason or "assembly" in reason or "existing-review" in reason for reason in reasons)
    terrain = any("terrain" in reason or "below-grade" in reason or "ground-contact" in reason for reason in reasons)
    if identity and terrain:
        return "Run the next local source-component and terrain/support pass, then repeat neighbour and browser gates."
    if identity:
        return "Run the next local source-component identity/suppression pass, then repeat neighbour and browser gates."
    if terrain:
        return "Build a bounded source-preserving terrain/support resolution, then repeat neighbour and browser gates."
    return "Extend the local deterministic pipeline for the recorded condition before publication."


def start():
    source = read(DOC / "results.json.gz")
    uids = sorted(row["uid"] for row in source["rows"] if row["uid"] != INSTALLED_UID)
    claim = s.reservations.claim(
        "codex-xl-final-script-sync-" + str(uuid.uuid4()),
        ["building:" + uid for uid in uids],
        batch=BATCH,
    )
    assert claim["ok"]
    save(LOCAL / "reservation.json", json.loads(json.dumps(claim["reservation"], default=str)))
    s.call([
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
    source = read(DOC / "results.json.gz")
    diagnostics = {row["uid"]: row for row in read(s.DOC / "diagnostics.json")["rows"]}
    acceptance = s.DOC / "west9zone-install/installed-acceptance.json"
    assert acceptance.exists()
    rows = []
    for original in source["rows"]:
        row = {
            key: original[key]
            for key in (
                "modelId", "uid", "name", "sourceSHA256", "sourceSheet",
                "scriptedWorkComplete", "identityScriptAccepted",
                "foundationScriptAccepted", "requiresAI", "requiresUserDecision",
                "aiCalls", "modelGeometryChanges",
            )
        }
        if row["uid"] == INSTALLED_UID:
            row.update(
                humanStatus="installed",
                actionableState="installed-verified",
                needsMoreCompute=False,
                holdOwner=None,
                reasons=[],
                nextStep=None,
                installedEvidence={"path": rel(acceptance), "sha256": h(acceptance)},
            )
        else:
            reasons = terminal_reasons(original, diagnostics[row["uid"]])
            assert reasons
            row.update(
                humanStatus="held-unknown",
                actionableState="held-for-local-scripted-processing",
                needsMoreCompute=True,
                holdOwner="local-scripted-processing",
                reasons=reasons,
                nextStep=next_step(reasons),
            )
        rows.append(row)

    assert len(rows) == 50
    assert sum(row["humanStatus"] == "installed" for row in rows) == 1
    assert all(row["scriptedWorkComplete"] for row in rows)
    assert all(not row["requiresAI"] and not row["requiresUserDecision"] for row in rows)
    status_keys = ("installed", "to-do", "held-human", "held-ai", "held-unknown", "in-process")
    counts = {key: sum(row["humanStatus"] == key for row in rows) for key in status_keys}
    reason_counts = dict(Counter(reason for row in rows for reason in row["reasons"]))
    evidence = [
        HERE / "xl-pass.py",
        HERE / "xl-second-pass.py",
        HERE / "xl-complete-context.py",
        HERE / "xl-final-script-pass.py",
        HERE / "xl-stage-west9zone.py",
        HERE / "xl-west9zone-import.py",
        DOC / "results.json.gz",
        s.DOC / "diagnostics.json",
        s.DOC / "metrics.json",
        s.DOC / "west9zone-install/staged-browser.json",
        s.DOC / "west9zone-install/live-browser.json",
        acceptance,
    ]
    report = {
        "batch": BATCH,
        "stage": STAGE,
        "models": 50,
        "humanCounts": counts,
        "reasonCounts": reason_counts,
        "rows": rows,
        "evidenceHashes": {rel(path): h(path) for path in evidence},
        "aiCalls": 0,
        "modelGeometryChanges": 0,
        "publication": True,
        "qualification": (
            "All 50 XL government sources completed the configured local identifier, projection/assembly, "
            "foundation and runtime checks. WEST9ZONE additionally passed source support, neighbour, staged/live "
            "browser and installation gates. The other 49 are retained for later local scripted processing; none "
            "is waiting for AI modelling or a user decision."
        ),
    }
    payload = {
        "models": 50,
        "sourceEvidenceSHA256": h(DOC / "results.json.gz"),
        "installed": 1,
        "heldLocalProcessing": 49,
        "aiCalls": 0,
    }
    existing_path = DOC / "final-results.json.gz"
    existing = read(existing_path) if existing_path.exists() else None
    if existing and existing.get("batch") == BATCH and existing.get("jobId"):
        job_id = existing["jobId"]
        with s.connect() as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            stored = connection.execute(
                "SELECT result FROM astra_modelling.jobs WHERE id=%s AND status='complete'", (job_id,)
            ).fetchone()
        assert stored
        report = stored[0]
        sync = read(DOC / "neon-sync.json")
        pointer = read(ROOT / "docs/astra-city/model-integration-20260909/current-source-review.json")
        if sync.get("jobId") == job_id and pointer["snapshotId"] == sync.get("snapshot"):
            with s.connect() as connection:
                connection.execute("SET TRANSACTION READ ONLY")
                states = dict(connection.execute(
                    "SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)",
                    (sync["snapshot"], [row["uid"] for row in rows if row["humanStatus"] == "held-unknown"]),
                ))
            assert states == {
                row["uid"]: "held" for row in rows if row["humanStatus"] == "held-unknown"
            }
            assert counts["in-process"] == counts["held-ai"] == counts["held-human"] == 0
            print(json.dumps({
                "jobId": job_id,
                "snapshot": sync["snapshot"],
                "humanCounts": counts,
                "reasonCounts": reason_counts,
                "aiCalls": 0,
                "reused": True,
            }), flush=True)
            return
    else:
        job_id = s.jobs.enqueue(BATCH, STAGE, payload)
        job = s.jobs.claim(BATCH, read(receipt)["owner"], [STAGE], lease_seconds=600)
        assert job and job["id"] == job_id
        report["jobId"] = job_id
        save(existing_path, report)
        report["evidence"] = {"path": rel(existing_path), "sha256": h(existing_path)}
        assert s.jobs.finish(job, result=report)

    pointer_path = ROOT / "docs/astra-city/model-integration-20260909/current-source-review.json"
    pointer = read(pointer_path)
    previous_snapshot = pointer["snapshotId"]
    inventory = read(ROOT / pointer["inventory"])
    parts = {part["uid"]: part for part in inventory["parts"]}
    held = [row for row in rows if row["humanStatus"] == "held-unknown"]
    originals = {row["uid"]: row for row in source["rows"]}
    for row in held:
        target = originals[row["uid"]]["identity"]["target"]
        old = parts.get(row["uid"], {})
        parts[row["uid"]] = {
            "uid": row["uid"],
            "name": row["name"] or target.get("name"),
            "landmarkIds": old.get("landmarkIds", []),
            "objectId": target["objectId"],
            "csuid": target["buildingCSUID"],
            "candidate": {"sha256": row["sourceSHA256"]},
            "sourceProgress": "prepared-for-review",
            "classification": "scripted-xl-held-for-local-processing",
            "knownHold": True,
        }
    ordered = sorted(parts.values(), key=lambda item: item["uid"])
    snapshot = s.digest(s.jobs.encode([ordered, h(DOC / "results.json.gz")]).encode())[:16]
    inventory_path = pointer_path.parent / f"source-review-inventory-{snapshot}.json"
    save(inventory_path, {**inventory, "snapshotId": snapshot, "derivedFrom": previous_snapshot, "parts": ordered})
    ledger.seed(inventory_path, inherit=previous_snapshot)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    effort = {
        "method": "scripted",
        "ai_model": None,
        "reasoning_effort": "not-applicable",
        "issue": "HKS-203",
        "run_id": BATCH,
        "job_id": job_id,
        "output_ref": rel(existing_path),
    }
    entries = []
    for row in held:
        observation = (
            "Configured XL checks are complete; current fallback retained for local scripted processing. "
            + row["nextStep"]
            + " Reasons: "
            + ", ".join(row["reasons"])
        )
        entries.append((row["uid"], "held", existing_path, observation, commit))
    ledger.record_many(
        snapshot,
        receipt,
        entries,
        effort=effort,
        request_id=BATCH + "-" + job_id[:16],
    )
    assert read(pointer_path) == pointer
    save(pointer_path, {
        **pointer,
        "snapshotId": snapshot,
        "inventory": rel(inventory_path),
        "previousSnapshots": [*pointer.get("previousSnapshots", []), previous_snapshot],
    })
    with s.connect() as connection:
        connection.execute("SET TRANSACTION READ ONLY")
        stored = connection.execute(
            "SELECT result FROM astra_modelling.jobs WHERE id=%s AND status='complete'", (job_id,)
        ).fetchone()[0]
        states = dict(connection.execute(
            "SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)",
            (snapshot, [row["uid"] for row in held]),
        ))
    assert stored == report
    assert states == {row["uid"]: "held" for row in held}
    save(DOC / "neon-sync.json", {
        "jobId": job_id,
        "snapshot": snapshot,
        "rows": 50,
        "installed": 1,
        "heldLocalProcessing": 49,
        "inProcess": 0,
        "exactJobResultMatch": True,
        "heldReviewStatesMatch": True,
        "aiCalls": 0,
    })
    save(DOC / "final-summary.json", {key: value for key, value in report.items() if key != "rows"})
    print(json.dumps({
        "jobId": job_id,
        "snapshot": snapshot,
        "humanCounts": counts,
        "reasonCounts": reason_counts,
        "aiCalls": 0,
    }), flush=True)


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 else start()
