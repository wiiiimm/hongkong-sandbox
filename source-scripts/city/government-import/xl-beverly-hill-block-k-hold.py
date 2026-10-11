"""Persist the exact-source Beverly Hill Block K compute hold in Neon."""

import json
import uuid

from run import ROOT, read, save, digest, jobs, reservations, connect, Jsonb, dict_row


DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/beverly-hill-block-k-terrain-diagnostic-20260927"
BATCH = "government-xl-beverly-hill-block-k-hold-20260927"
UID = "landsd/255543:0"


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def run():
    selection = read(DOC / "selection.json.gz")["rows"]
    assert [row["uid"] for row in selection] == [UID]
    acceptance = read(DOC / "acceptance.json")
    foundation = read(DOC / "foundation.json")["rows"][0]
    validation = read(DOC / "validation.json")["results"][0]
    neighbour = read(DOC / "neighbour-checks.json")
    native = read(DOC / "native-neighbour-checks.json")
    assert not acceptance["passed"] and foundation["strictFoundationAccepted"]
    assert validation["uid"] == foundation["uid"] == UID
    blocked = sorted({uid for patch in neighbour["patches"] for uid in patch["blockedBy"]} - {UID})
    failed_native = sorted(set(native["blocked"]) - set(native.get("resolved", [])))
    assert len(blocked) == 7 and len(failed_native) == 4
    low = validation["terrain"]["sourceYBounds"][0]
    ground = validation["terrain"]["maxGround"]
    gap = low - ground
    assert gap > 20
    inputs = [DOC / name for name in (
        "result.json", "selection.json.gz", "metrics.json", "validation.json",
        "foundation.json", "acceptance.json", "identity-resolution.json",
        "neighbour-checks.json", "native-neighbour-checks.json")]
    report = {
        "batch": BATCH, "stage": "compute-held-v1", "uid": UID,
        "sourceSHA256": selection[0]["candidate"]["entry"]["sha256"],
        "humanStatus": "held-unknown", "primaryHold": "terrain-contact",
        "detailedHold": "elevated-source-needs-support-and-neighbour-terrain-resolution",
        "strictFoundationAccepted": True,
        "minimumSourceBottomAboveMaximumTerrainM": gap,
        "runtimeConcerns": validation["concerns"],
        "blockedNeighbourUids": blocked,
        "failedInstalledNativeUids": failed_native,
        "nextWork": "Identify the exact government support or podium source; make a source-preserving support-aware terrain patch, then rerun identity, foundation, neighbour, runtime, staged-browser and live-browser checks.",
        "evidence": [ref(path) for path in inputs],
        "requiresAI": False, "requiresHuman": False, "aiCalls": 0,
        "modelGeometryChanges": 0, "publication": False,
    }
    path = DOC / "hold.json"
    save(path, report)
    claim = reservations.claim("codex-xl-block-k-hold-" + str(uuid.uuid4()),
                               ["building:" + UID], batch=BATCH)
    assert claim["ok"], claim
    receipt = claim["reservation"]
    try:
        job_id = jobs.enqueue(BATCH, report["stage"], {"evidence": ref(path), "aiCalls": 0})
        job = jobs.claim(BATCH, receipt["owner"], [report["stage"]], lease_seconds=1800)
        assert job and job["id"] == job_id
        recorded = {**report, "report": ref(path)}
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
        save(DOC / "hold-neon.json", {"jobId": job_id, "evidence": ref(path), "resultVerified": True})
        print(json.dumps({"jobId": job_id, "uid": UID, "status": "held-unknown", "aiCalls": 0}))
    finally:
        reservations.release(receipt)


if __name__ == "__main__":
    run()
