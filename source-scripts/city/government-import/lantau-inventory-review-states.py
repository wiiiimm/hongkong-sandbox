"""Reconcile matched but uninstalled Lantau forms with the current Neon review snapshot."""
import csv
import json
from collections import Counter
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "source-scripts/city/shared-modelling"))
from db import connect
from psycopg.rows import dict_row

def main():
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs/astra-city/lantau-government-model-inventory-20260921"
    summary = json.loads((output / "summary.json").read_text())
    rows = [row for row in csv.DictReader((output / "buildings.csv").open())
            if row["actionableState"] == "enhancement-required"]
    assert len(rows) == summary["enhancementRequired"]
    pointer = json.loads((ROOT / "docs/astra-city/model-integration-20260909/current-source-review.json").read_text())
    snapshot = pointer["snapshotId"]
    with connect() as connection:
        connection.row_factory = dict_row
        states = connection.execute(
            "SELECT uid, review_state FROM astra_modelling.model_reviews "
            "WHERE snapshot_id=%s AND uid=ANY(%s)",
            (snapshot, [row["uid"] for row in rows]),
        ).fetchall()
    by_uid = {row["uid"]: row["review_state"] for row in states}
    assert len(by_uid) == len(rows)
    dispositions = [
        {"uid": row["uid"], "sectionId": row["sectionId"],
         "sizeGroup": row["sizeGroup"], "reviewState": by_uid[row["uid"]]}
        for row in rows
    ]
    counts = Counter(row["reviewState"] for row in dispositions)
    assert set(counts) <= {"held", "good-to-go", "approved-for-integration"}
    result = {
        "snapshotId": snapshot,
        "manifestSHA256": summary["inputs"]["3d-viewer/city/data/manifest.json"],
        "uninstalledMatchedForms": len(rows),
        "reviewStates": dict(counts),
        "rows": dispositions,
        "databaseWrites": 0,
        "aiCalls": 0,
    }
    (output / "review-states.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"uninstalled": len(rows), "states": dict(counts), "snapshot": snapshot}))

if __name__ == "__main__":
    main()
