"""Persist Yoho Mall II's remaining source/terrain contact hold after neighbour masking."""

import json
import uuid

from run import ROOT, read, save, digest, jobs, reservations, connect, Jsonb, dict_row


BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
SHARED = BASE / "shared-neighbour-mask-eval-20260927.json"
FOUNDATION = BASE / "masked-foundation-eval-20260927.json"
OUTPUT = BASE / "yoho-mall-ii-masked-hold-20260927.json"
RECEIPT = BASE / "yoho-mall-ii-masked-hold-20260927-neon.json"
BATCH = "government-xl-yoho-masked-hold-20260927"
UID = "landsd/273672:0"


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def run():
    candidate = next(row for row in read(SHARED)["rows"] if row["uid"] == UID)
    foundation = next(row for row in read(FOUNDATION)["rows"] if row["uid"] == UID)
    identity_path = BASE / "yoho-mall-ii-terrain-diagnostic-20260927/identity-resolution.json"
    identity = read(identity_path)["rows"][0]
    assert identity["uid"] == UID and identity["exactObjectAndCSUID"]
    assert candidate["sourcePreserved"] and not candidate["remainingBlockedUids"]
    assert candidate["missingTerrainSamples"] == 0
    assert not foundation["strictFoundationAccepted"]
    assert foundation["foundation"]["fullyBuriedUpwardTriangles"] == 2
    assert candidate["minLowRimGapM"] < -9
    report = {
        "batch": BATCH, "stage": "compute-held-v2", "uid": UID,
        "sourceSHA256": foundation["sourceSHA256"],
        "humanStatus": "held-unknown", "primaryHold": "terrain-contact",
        "detailedHold": "deep-source-burial-after-neighbour-preservation",
        "sourceTerrainGapSamples": candidate["missingTerrainSamples"],
        "blockedNeighbourUids": candidate["remainingBlockedUids"],
        "minimumLowRimGapM": candidate["minLowRimGapM"],
        "maximumLowRimGapM": candidate["maxLowRimGapM"],
        "fullyBuriedUpwardTriangles": foundation["foundation"]["fullyBuriedUpwardTriangles"],
        "fullyBuriedUpwardAreaM2": foundation["foundation"]["fullyBuriedUpwardAreaM2"],
        "fullyBuriedAreaFraction": foundation["foundation"]["fullyBuriedAreaFraction"],
        "nextWork": "Use scripts to inspect the two buried upward source faces and their source components against the government ground and the current footprint. Keep original geometry unchanged; only install after a bounded contact explanation or source-preserving terrain solution passes full acceptance and browser checks.",
        "evidence": [ref(SHARED), ref(FOUNDATION), ref(identity_path)],
        "requiresAI": False, "requiresHuman": False,
        "aiCalls": 0, "modelGeometryChanges": 0, "publication": False,
    }
    save(OUTPUT, report)
    claim = reservations.claim("codex-xl-yoho-masked-hold-" + str(uuid.uuid4()),
                               ["building:" + UID], batch=BATCH)
    assert claim["ok"], claim
    receipt = claim["reservation"]
    try:
        job_id = jobs.enqueue(BATCH, report["stage"], {"evidence": ref(OUTPUT), "aiCalls": 0})
        job = jobs.claim(BATCH, receipt["owner"], [report["stage"]], lease_seconds=1800)
        assert job and job["id"] == job_id
        recorded = {**report, "report": ref(OUTPUT)}
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
        save(RECEIPT, {"jobId": job_id, "evidence": ref(OUTPUT), "resultVerified": True})
        print(json.dumps({"jobId": job_id, "uid": UID, "status": "held-unknown", "aiCalls": 0}))
    finally:
        reservations.release(receipt)


if __name__ == "__main__":
    run()
