"""Keep unresolved XL terrain-patch investigations resumable in Neon."""

import json
import uuid
from pathlib import Path

from run import ROOT, HERE, read, save, digest, jobs, reservations, connect, Jsonb, dict_row

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
OUTPUT = BASE / "terrain-exceptions-20260925.json"
BATCH = "government-xl-terrain-exceptions-20260925"


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def run():
    rows = []
    for slug in ("citywalk", "parkview", "go-park"):
        doc = BASE / f"{slug}-terrain-diagnostic-20260925"
        selection = read(doc / "selection.json.gz")
        foundation = {r["uid"]: r for r in read(doc / "foundation.json")["rows"]}
        validation = {r["uid"]: r for r in read(doc / "validation.json")["results"]}
        neighbour = read(doc / "neighbour-checks.json")
        native_neighbour = read(doc / "native-neighbour-checks.json")
        blocked = sorted({uid for patch in neighbour["patches"] for uid in patch["blockedBy"]}
                         - set(native_neighbour.get("resolved", []))
                         - {r["uid"] for r in selection["rows"]})
        native_failed = sorted(native_neighbour.get("failed", []))
        sources = [ref(doc / name) for name in ("result.json", "selection.json.gz", "metrics.json",
                                                "validation.json", "foundation.json", "neighbour-checks.json",
                                                "native-neighbour-checks.json")]
        if slug == "parkview":
            sources.append(ref(doc / "support-proof.json"))
        for row in selection["rows"]:
            uid = row["uid"]
            reason = ("installed-native-neighbour-regression" if native_failed else
                      "related-source-components-terrain-gap" if slug == "go-park" else
                      "adjacent-basic-form-terrain-gap")
            rows.append({"uid": uid, "sourceSHA256": row["candidate"]["entry"]["sha256"],
                         "humanStatus": "held-unknown", "primaryHold": "terrain-contact",
                         "detailedHold": reason,
                         "strictFoundationAccepted": foundation[uid]["strictFoundationAccepted"],
                         "runtimeConcerns": validation[uid].get("concerns", []),
                         "blockedNeighbourUids": blocked,
                         "failedInstalledNativeUids": native_failed,
                         "installedSupportProofPassed": slug == "parkview",
                         "nextWork": ("Identify and port three neighbouring original GO PARK components with shared terrain, or compute a smaller patch; rerun all gates"
                                      if slug == "go-park" else
                                      "Compute a smaller or support-aware exact-source patch and rerun all neighbour/browser gates"),
                         "evidence": sources, "requiresAI": False, "requiresHuman": False, "aiCalls": 0})
    selection = {row["uid"]: row for row in read(BASE / "selection.json.gz")["rows"]}
    west = [row for row in read(BASE / "reconciliation.json.gz")["rows"]
            if row["sourceSheet"] == "11-NW-19A" and row["primaryHold"] == "terrain-contact"
            and row["uid"] != "landsd/84014:0"]
    assert len(west) == 4
    parent = read(ROOT / "3d-viewer/city/data/terrain.json")
    manifest = read(ROOT / "3d-viewer/city/data/manifest.json")
    import importlib.util
    spec = importlib.util.spec_from_file_location("xl_second_exceptions", HERE / "xl-second-pass.py")
    second = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(second)
    cells = [second.resolution.rectangle_for(selection[row["uid"]]["native"]["model"]["worldBounds"], parent)
             for row in west]
    union = [min(c[0] for c in cells), min(c[1] for c in cells), max(c[2] for c in cells), max(c[3] for c in cells)]
    overlaps = [item["url"] for item in manifest["terrainPatches"]
                if second.resolution.terrain.overlap(union, read(ROOT / "3d-viewer" / item["url"])["coarseCells"])]
    assert overlaps == ["city/data/government-native-229310-0.json",
                        "city/data/government-native-233970-0.json"], overlaps
    for row in west:
        rows.append({"uid": row["uid"], "sourceSHA256": row["sourceSHA256"],
                     "humanStatus": "held-unknown", "primaryHold": "terrain-contact",
                     "detailedHold": "overlapping-installed-terrain-patches",
                     "overlappingPatchURLs": overlaps,
                     "nextWork": "Build a source-preserving replacement covering existing patches and verify their installed models",
                     "evidence": [ref(BASE / "selection.json.gz"), ref(BASE / "reconciliation.json.gz")],
                     "requiresAI": False, "requiresHuman": False, "aiCalls": 0})
    assert len(rows) == 10 and len({r["uid"] for r in rows}) == 10
    report = {"batch": BATCH, "stage": "compute-held-v2", "rows": rows,
              "humanCounts": {"held-unknown": 10, "held-ai": 0, "held-human": 0, "in-process": 0},
              "qualification": "These ten remain held for explicit terrain/assembly compute work; no model geometry was modified or installed. The other XL states remain in the territory reconciliation.",
              "aiCalls": 0, "modelGeometryChanges": 0}
    save(OUTPUT, report)
    claim = reservations.claim("codex-xl-terrain-exceptions-" + str(uuid.uuid4()),
                               ["building:" + row["uid"] for row in rows], batch=BATCH)
    assert claim["ok"], claim
    receipt = claim["reservation"]
    try:
        payload = {"evidence": ref(OUTPUT), "uids": [r["uid"] for r in rows], "aiCalls": 0}
        job_id = jobs.enqueue(BATCH, report["stage"], payload)
        job = jobs.claim(BATCH, receipt["owner"], [report["stage"]], lease_seconds=1800)
        assert job and job["id"] == job_id
        recorded = {**report, "evidence": ref(OUTPUT)}
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
        save(BASE / "terrain-exceptions-20260925-neon.json", {"jobId": job_id,
                                                               "evidence": ref(OUTPUT), "resultVerified": True})
        print(json.dumps({"jobId": job_id, "held": len(rows), "aiCalls": 0}), flush=True)
    finally:
        reservations.release(receipt)


if __name__ == "__main__":
    run()
