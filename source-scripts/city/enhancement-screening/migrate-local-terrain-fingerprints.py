"""Migrate verified good-to-go rows from global to local terrain fingerprints."""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROOF = ROOT / "3d-viewer/scripts/building-progress/screening-proof.json"
UIDS = {"landsd/195308:0", "landsd/196549:0"}
REQUEST_ID = "good-to-go-local-terrain-fingerprint-v1-20260917"

sys.path.insert(0, str(HERE.parent / "shared-modelling"))
import reservations  # noqa: E402


def save(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    proof = json.loads(PROOF.read_text())
    rows = {row["uid"]: row for row in proof["rows"] if row["uid"] in UIDS}
    assert set(rows) == UIDS
    for row in rows.values():
        evidence = ROOT / row["evidence"]
        assert evidence.is_file()
        assert hashlib.sha256(evidence.read_bytes()).hexdigest() == row["evidenceHash"]

    work = HERE / "local-terrain-fingerprint-migration"
    plan_path = work / "inputs.json.gz"
    work.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "node", str(ROOT / "3d-viewer/scripts/building-progress/generate.mjs"),
        "--plan", str(plan_path),
    ], cwd=ROOT, check=True)
    with gzip.open(plan_path, "rt") as stream:
        plan = json.load(stream)
    hashes = {row["uid"]: row["inputHash"] for row in plan["rows"] if row["uid"] in UIDS}
    assert set(hashes) == UIDS

    entries = [{
        "uid": uid,
        "inputHash": hashes[uid],
        "decision": rows[uid]["decision"],
        "reason": rows[uid]["reason"],
        "evidence": rows[uid]["evidence"],
        "evidenceHash": rows[uid]["evidenceHash"],
    } for uid in sorted(UIDS)]
    entries_path = work / "entries.json"
    save(entries_path, entries)

    claim = reservations.claim(
        "codex-local-terrain-fingerprint-" + str(uuid.uuid4()),
        ["building:" + uid for uid in sorted(UIDS)],
        batch=REQUEST_ID,
        ttl=900,
    )
    assert claim["ok"], claim
    receipt_path = work / "reservation.json"
    save(receipt_path, json.loads(json.dumps(claim["reservation"], default=str)))
    try:
        subprocess.run([
            sys.executable, str(HERE / "screen.py"), "record",
            "--out", str(work),
            "--entries", str(entries_path),
            "--receipt", str(receipt_path),
            "--request-id", REQUEST_ID,
        ], cwd=ROOT, check=True)
    finally:
        reservations.release(json.loads(receipt_path.read_text()))
    exported = json.loads(PROOF.read_text())
    current = {row["uid"]: row["inputHash"] for row in exported["rows"] if row["uid"] in UIDS}
    assert current == hashes
    print(json.dumps({"migrated": len(UIDS), "aiCalls": 0, "requestId": REQUEST_ID}))


if __name__ == "__main__":
    main()
