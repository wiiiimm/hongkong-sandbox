"""Complete the two Lantau XL holds and summarize territory-wide XL work."""

import json
import uuid
from pathlib import Path

from run import ROOT, read, save, digest, connect, jobs, reservations, Jsonb, dict_row

BATCH = "government-xl-territory-reconciled-20260923"
BASE = ROOT / "docs/astra-city/government-import"
LANTAU = BASE / "government-xl-lantau-exceptions-20260923"
OUTSIDE = BASE / "government-xl-remaining-20260923"
OUTPUT = BASE / "government-xl-territory-20260923.json"


def sha(path):
    return digest(Path(path).read_bytes())


def rel(path):
    return str(Path(path).relative_to(ROOT))


def run():
    selection = read(LANTAU / "selection.json.gz")
    first = read(LANTAU / "results.json.gz")
    context = read(LANTAU / "context.json")
    outside = read(OUTSIDE / "reconciliation-summary.json")
    assert len(selection["rows"]) == len(first["rows"]) == len(context["rows"]) == 2
    assert outside["models"] == 352 and outside["installedThisPass"] == 10
    source = {row["uid"]: row for row in selection["rows"]}
    result = {row["uid"]: row for row in first["rows"]}
    rows = []
    for item in context["rows"]:
        uid = item["uid"]
        assert source[uid]["sourceSHA256"] == item["sourceSHA256"]
        assert result[uid]["humanStatus"] == "held-unknown"
        assert "terrain-intersects-source-over-0.5m" in result[uid]["reasons"]
        identity = item["identity"]
        assert identity["exactObjectAndCSUID"]
        assert identity["sourceExcessFraction"] > .05
        rows.append({
            "uid": uid, "name": item["name"], "sourceSHA256": item["sourceSHA256"],
            "humanStatus": "held-unknown", "primaryHold": "source-identity-or-assembly",
            "reasons": sorted(set(result[uid]["reasons"] + ["projected-source-identity-or-assembly"])),
            "sourceExcessFraction": identity["sourceExcessFraction"],
            "otherIntersectingForms": len(identity["intersectingForms"]) - 1,
            "terrainMinimumSurfaceGapM": result[uid]["metrics"]["minSurfaceGap"],
            "evidence": [rel(LANTAU / "selection.json.gz"), rel(LANTAU / "results.json.gz"),
                         rel(LANTAU / "context.json")], "aiCalls": 0,
        })
    assert {row["uid"] for row in rows} == {"landsd/290981:0", "landsd/183776:0"}
    summary = {
        "batch": BATCH, "stage": "territory-xl-reconciliation-v1",
        "initiallyUninstalled": 354, "installedThisPass": 10,
        "humanCounts": {"installed": 10, "held-unknown": 344, "in-process": 0,
                        "held-ai": 0, "held-human": 0, "to-do": 0},
        "primaryHoldCounts": {"source-identity-or-assembly": 241,
                              "terrain-contact": 75, "source-recovery": 28},
        "outsideJobId": outside["jobId"], "lantauFirstJobId": first["jobId"],
        "lantauRows": rows,
        "inputSHA256": {rel(path): sha(path) for path in
                        (LANTAU / "selection.json.gz", LANTAU / "results.json.gz",
                         LANTAU / "context.json", OUTSIDE / "reconciliation.json.gz")},
        "aiCalls": 0, "geometryChanges": 0,
        "qualification": "All 354 exact-matched XL source forms initially uninstalled at this pass are accounted for. Held is a compute/source evidence disposition, not a request for a human or AI modelling decision.",
    }
    save(OUTPUT, summary)
    claim = reservations.claim("codex-xl-territory-" + str(uuid.uuid4()),
                               ["building:" + row["uid"] for row in rows], batch=BATCH)
    assert claim["ok"], claim
    receipt = claim["reservation"]
    try:
        payload = {"evidence": rel(OUTPUT), "sha256": sha(OUTPUT), "outsideJobId": outside["jobId"]}
        job_id = jobs.enqueue(BATCH, summary["stage"], payload)
        job = jobs.claim(BATCH, receipt["owner"], [summary["stage"]], lease_seconds=1800)
        assert job and job["id"] == job_id
        recorded = {**summary, "evidence": {"path": rel(OUTPUT), "sha256": sha(OUTPUT)}}
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
        save(BASE / "government-xl-territory-20260923-neon.json",
             {"jobId": job_id, "evidenceSHA256": sha(OUTPUT), "resultVerified": True})
        print(json.dumps({"jobId": job_id, "counts": summary["humanCounts"],
                          "primaryHolds": summary["primaryHoldCounts"], "aiCalls": 0}), flush=True)
    finally:
        reservations.release(receipt)


if __name__ == "__main__":
    run()
