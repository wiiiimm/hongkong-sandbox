"""Route remaining XL terrain holds by overlap with installed terrain patches."""

import importlib.util
import json
import sys
import uuid
from collections import Counter

from run import ROOT, HERE, read, save, digest, connect, jobs, reservations, Jsonb, dict_row

spec = importlib.util.spec_from_file_location("xl_second_overlap_triage", HERE / "xl-second-pass.py")
second = importlib.util.module_from_spec(spec)
spec.loader.exec_module(second)

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
REPORT = BASE / "terrain-overlap-triage-20260927.json"
RECEIPT = BASE / "terrain-overlap-triage-20260927-neon.json"
BATCH = "government-xl-terrain-overlap-triage-20260927"


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def build():
    reconciliation_path = BASE / "reconciliation.json.gz"
    selection_path = BASE / "selection.json.gz"
    manifest_path = ROOT / "3d-viewer/city/data/manifest.json"
    parent_path = ROOT / "3d-viewer/city/data/terrain.json"
    reconciliation = read(reconciliation_path)
    selection = {row["uid"]: row for row in read(selection_path)["rows"]}
    manifest = read(manifest_path)
    parent = read(parent_path)
    patches = [(entry["url"], read(ROOT / "3d-viewer" / entry["url"])["coarseCells"],
                ref(ROOT / "3d-viewer" / entry["url"]))
               for entry in manifest["terrainPatches"]]
    rows = []
    for item in reconciliation["rows"]:
        if item["primaryHold"] != "terrain-contact":
            continue
        uid = item["uid"]
        model = selection[uid]["native"]["model"]
        cells = second.resolution.rectangle_for(model["worldBounds"], parent)
        overlaps = [source for url, patch_cells, source in patches
                    if second.resolution.terrain.overlap(cells, patch_cells)]
        rows.append({"uid": uid, "name": item["name"], "sourceSheet": item["sourceSheet"],
                     "sourceSHA256": item["sourceSHA256"], "cells": cells,
                     "overlappingInstalledPatches": overlaps,
                     "triage": "replacement-patch-required" if overlaps else "standalone-patch-candidate",
                     "nextWork": ("Build a source-preserving replacement patch and revalidate every installed model it retains"
                                  if overlaps else "Build the original-source terrain patch and run identity, foundation, neighbour, runtime, and browser gates"),
                     "humanStatus": "held-unknown", "requiresAI": False, "requiresHuman": False,
                     "aiCalls": 0})
    rows.sort(key=lambda row: row["uid"])
    assert len(rows) == 68 and len({row["uid"] for row in rows}) == 68
    counts = dict(Counter(row["triage"] for row in rows))
    assert sum(counts.values()) == 68
    report = {"batch": BATCH, "stage": "coarse-terrain-overlap-triage-v1",
              "models": len(rows), "counts": counts, "rows": rows,
              "inputEvidence": [ref(path) for path in
                                (reconciliation_path, selection_path, manifest_path, parent_path)],
              "qualification": "Coarse-cell overlap is routing evidence only. A standalone patch candidate still requires all source, foundation, neighbour, runtime and browser gates. Existing XL human statuses do not change.",
              "aiCalls": 0, "modelGeometryChanges": 0, "publication": False}
    save(REPORT, report)
    print(json.dumps({"counts": counts, "report": str(REPORT.relative_to(ROOT))}), flush=True)
    return report


def sync():
    report = read(REPORT)
    assert report["models"] == 68
    claim = reservations.claim("codex-xl-terrain-overlap-" + str(uuid.uuid4()),
                               ["building:" + row["uid"] for row in report["rows"]], batch=BATCH)
    assert claim["ok"], claim
    receipt = claim["reservation"]
    try:
        job_id = jobs.enqueue(BATCH, report["stage"], {"evidence": ref(REPORT), "aiCalls": 0})
        job = jobs.claim(BATCH, receipt["owner"], [report["stage"]], lease_seconds=1800)
        assert job and job["id"] == job_id
        recorded = {**report, "evidence": ref(REPORT)}
        with connect() as connection:
            connection.row_factory = dict_row
            connection.execute("SELECT pg_advisory_xact_lock(%s)", (reservations.LOCK_ID,))
            assert reservations._current(connection, receipt)
            assert connection.execute(
                "UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() "
                "WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
                (Jsonb(recorded), job_id, job["owner"], job["token"])).rowcount == 1
        with connect() as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            assert connection.execute("SELECT result FROM astra_modelling.jobs WHERE id=%s",
                                      (job_id,)).fetchone()[0] == recorded
        save(RECEIPT, {"jobId": job_id, "evidence": ref(REPORT), "resultVerified": True})
        print(json.dumps({"jobId": job_id, "counts": report["counts"], "aiCalls": 0}), flush=True)
    finally:
        reservations.release(receipt)


if __name__ == "__main__":
    sync() if len(sys.argv) > 1 and sys.argv[1] == "sync" else build()
