"""Persist the two exact-TIN XL contact and neighbour holds in Neon."""

import json
import sys
import uuid

from run import ROOT, read, save, digest, connect, jobs, reservations, Jsonb, dict_row


BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
REPORT = BASE / "two-sheet-contact-holds-20260927.json"
RECEIPT = BASE / "two-sheet-contact-holds-20260927-neon.json"
BATCH = "government-xl-two-sheet-contact-holds-20260927"
MODELS = {
    "landsd/257352:0": ("diocesan-girls-school", ("11-NW-24B", "11-NW-24D")),
    "landsd/273672:0": ("yoho-mall-ii", ("6-NW-10C", "6-NW-10D")),
}


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def build():
    rows = []
    for uid, (name, sheets) in MODELS.items():
        folder = BASE / f"{name}-terrain-diagnostic-20260927"
        source = read(folder / "result.json")
        acceptance = read(folder / "acceptance.json")
        foundation = read(folder / "foundation.json")["rows"][0]
        metrics = read(folder / "metrics.json")["rows"][0]
        neighbour = read(folder / "neighbour-checks.json")
        validation = read(folder / "validation.json")["results"][0]
        assert source["uids"] == [uid] and tuple(source["terrainSheets"]) == sheets
        patch_path = ROOT / source["patchPath"]
        assert ref(patch_path)["sha256"] == source["patchSHA256"]
        patch = read(patch_path)
        fill_policy = patch["nativeMesh"]["source"]["parentHoleFill"]["policy"]
        assert "outside the protected source-model projection" in fill_policy or "No material parent hole" in fill_policy
        assert "sourceBoundaryToleranceFill" not in patch["nativeMesh"]["source"]
        assert not acceptance["passed"] and validation["uid"] == foundation["uid"] == uid
        blocked = sorted({building for patch in neighbour["patches"]
                          for building in patch["blockedBy"]} - {uid})
        assert blocked
        evidence = [ref(folder / file) for file in (
            "result.json", "selection.json.gz", "identity-resolution.json", "metrics.json",
            "validation.json", "foundation.json", "acceptance.json",
            "neighbour-checks.json", "native-neighbour-checks.json")]
        row = {"uid": uid, "sourceSheets": list(sheets),
               "sourceDirectorySHA256s": source["sourceDirectorySHA256s"],
               "humanStatus": "held-unknown", "primaryHold": "terrain-contact",
               "detailedHold": "two-sheet-source-complete-neighbour-contact-regression",
               "sourceTerrainGapM2": 0,
               "parentFillOutsideModelM2": source["parentHoleFill"]["missingAreaM2"],
               "strictFoundationAccepted": foundation["strictFoundationAccepted"],
               "fullyBuriedUpwardTriangles": foundation["foundation"]["fullyBuriedUpwardTriangles"],
               "fullyBuriedUpwardAreaM2": foundation["foundation"]["fullyBuriedUpwardAreaM2"],
               "minimumLowRimGapM": metrics["minLowGap"],
               "runtimeConcerns": validation["concerns"],
               "blockedNeighbourUids": blocked,
               "acceptanceFailures": acceptance["failures"],
               "nextWork": "Keep the exact government model and two-sheet TIN unchanged; design a source-preserving parent-terrain mask for blocked neighbouring forms, then rerun full foundation, neighbour, runtime and staged/live browser gates. Any buried upward source faces require separate bounded review.",
               "evidence": evidence, "requiresAI": False, "requiresHuman": False,
               "aiCalls": 0, "modelGeometryChanges": 0, "publication": False}
        rows.append(row)
    report = {"batch": BATCH, "stage": "compute-held-v1", "models": len(rows),
              "rows": rows, "aiCalls": 0, "modelGeometryChanges": 0, "publication": False}
    save(REPORT, report)
    print(json.dumps({"models": len(rows), "blockedNeighbours":
                      {row["uid"]: len(row["blockedNeighbourUids"]) for row in rows}}), flush=True)


def sync():
    report = read(REPORT)
    assert report["models"] == len(MODELS)
    claim = reservations.claim("codex-xl-two-sheet-holds-" + str(uuid.uuid4()),
                               ["building:" + uid for uid in MODELS], batch=BATCH)
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
        print(json.dumps({"jobId": job_id, "models": len(MODELS), "aiCalls": 0}), flush=True)
    finally:
        reservations.release(receipt)


if __name__ == "__main__":
    sync() if len(sys.argv) > 1 and sys.argv[1] == "sync" else build()
