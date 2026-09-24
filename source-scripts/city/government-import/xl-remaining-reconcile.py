"""Freeze final XL pass states and sync resumable per-form evidence to Neon."""

import json
import uuid
from collections import Counter
from pathlib import Path

from run import ROOT, HERE, read, save, digest, connect, jobs, reservations, Jsonb, dict_row

BATCH = "government-xl-remaining-reconciled-20260923"
DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
INITIAL = DOC / "results.json.gz"
HELD = DOC / "held-second-pass/results.json.gz"
CONTEXT = DOC / "context.json"
HELD_CONTEXT = DOC / "context-held.json"
HTTP_RETRY = DOC / "http-retry-check-20260924/results.json.gz"
REVISION_CHECK = DOC / "revision-check-20260924/results.json.gz"
PROOF = DOC / "reconciliation.json.gz"


def sha(path):
    return digest(Path(path).read_bytes())


def rel(path):
    return str(Path(path).relative_to(ROOT))


def installed_entries():
    found = {}
    manifest = read(ROOT / "3d-viewer/city/data/manifest.json")
    for url in manifest["officialModelCatalogues"]:
        catalogue = read(ROOT / "3d-viewer" / url)
        for model in catalogue["models"]:
            if model["uid"] in found:
                raise ValueError("Duplicate installed model: " + model["uid"])
            found[model["uid"]] = {"sha256": model["sha256"], "catalogue": url}
    return found


def build():
    selection = read(DOC / "selection.json.gz")
    first = read(INITIAL)
    held = read(HELD)
    by_first = {row["uid"]: row for row in first["rows"]}
    by_held = {row["uid"]: row for row in held["rows"]}
    contexts = {row["uid"]: row for path in (CONTEXT, HELD_CONTEXT)
                for row in read(path)["rows"]}
    retry_sources = (HTTP_RETRY, REVISION_CHECK)
    retried = {row["uid"]: (row, path) for path in retry_sources
               for row in read(path)["rows"]}
    installed = installed_entries()
    assert len(selection["rows"]) == len(by_first) == 352
    assert len(by_held) == 199 and len(contexts) == 324 and len(retried) == 26
    rows = []
    for original in selection["rows"]:
        uid = original["uid"]
        if original["source"]:
            assert sha(ROOT / "3d-viewer" / original["source"]["tile"]) == original["source"]["tileSHA256"]
        current = installed.get(uid)
        context = contexts.get(uid) or (retried[uid][0] if uid in retried else None)
        second = by_held.get(uid)
        reasons = set(by_first[uid]["reasons"])
        if second:
            reasons.update(second["reasons"])
        if uid in retried:
            reasons.discard("source-recovery-failed")
            reasons.update(retried[uid][0]["reasons"])
        if current:
            assert current["sha256"] == original["sourceSHA256"]
            status, primary = "installed", None
            reasons.clear()
        elif not context:
            assert "source-recovery-failed" in reasons
            status, primary = "held-unknown", "source-recovery"
        else:
            identity = context["identity"]
            strict = (identity["exactObjectAndCSUID"]
                      and identity["targetCoveredBySourceProjection"] >= .95
                      and identity["sourceExcessFraction"] <= .05)
            status = "held-unknown"
            primary = "terrain-contact" if strict else "source-identity-or-assembly"
            if strict:
                reasons.add("current-terrain-contact")
            else:
                reasons.add("projected-source-identity-or-assembly")
        rows.append({
            "uid": uid, "modelId": original["modelId"], "name": original["name"],
            "sectionId": original["sectionId"], "sourceSHA256": original["sourceSHA256"],
            "sourceSheet": original["native"]["sheet"],
            "nativeCacheKey": original["native"]["cacheKey"],
            "humanStatus": status, "primaryHold": primary,
            "reasons": sorted(reasons), "installedProof": current,
            "exactSourceRecovered": context is not None,
            "evidence": [rel(INITIAL), rel(HELD) if second else None,
                         rel(retried[uid][1]) if uid in retried else
                         rel(HELD_CONTEXT if second else CONTEXT) if context else None],
            "aiCalls": 0,
        })
    counts = dict(Counter(row["humanStatus"] for row in rows))
    holds = dict(Counter(row["primaryHold"] for row in rows if row["primaryHold"]))
    assert counts == {"installed": 10, "held-unknown": 342}, counts
    assert holds == {"source-identity-or-assembly": 257,
                     "terrain-contact": 83, "source-recovery": 2}, holds
    report = {
        "batch": BATCH, "stage": "installed-and-held-reconciliation-v4",
        "models": 352, "outsideLantau": True, "installedThisPass": 10,
        "humanCounts": {key: counts.get(key, 0) for key in
                        ("installed", "to-do", "held-human", "held-ai", "held-unknown", "in-process")},
        "primaryHoldCounts": holds, "sourceRun": selection["nativeRun"],
        "excludedLantauUids": selection["excludedLantauUids"],
        "inputSHA256": {rel(path): sha(path) for path in
                        (DOC / "selection.json.gz", INITIAL, HELD, CONTEXT, HELD_CONTEXT,
                         HTTP_RETRY, REVISION_CHECK)},
        "rows": rows, "aiCalls": 0, "geometryChanges": 0,
        "qualification": "Exclusive primary holds are routing labels, not assertions that all other checks passed. Exact source assets and original reasons are retained for each form. No human or AI modelling decision is currently requested.",
    }
    save(PROOF, report)
    return report


def sync():
    report = build()
    claim = reservations.claim("codex-xl-remaining-reconcile-" + str(uuid.uuid4()),
                               ["building:" + row["uid"] for row in report["rows"]], batch=BATCH)
    assert claim["ok"], claim
    receipt = claim["reservation"]
    try:
        payload = {"evidence": rel(PROOF), "sha256": sha(PROOF),
                   "models": 352, "installed": 10, "aiCalls": 0}
        job_id = jobs.enqueue(BATCH, report["stage"], payload)
        job = jobs.claim(BATCH, receipt["owner"], [report["stage"]], lease_seconds=1800)
        assert job and job["id"] == job_id
        result = {**report, "evidence": {"path": rel(PROOF), "sha256": sha(PROOF)}}
        with connect() as connection:
            connection.row_factory = dict_row
            connection.execute("SELECT pg_advisory_xact_lock(%s)", (reservations.LOCK_ID,))
            assert reservations._current(connection, receipt)
            assert connection.execute(
                "UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() "
                "WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
                (Jsonb(result), job_id, job["owner"], job["token"])).rowcount == 1
        with connect() as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            assert connection.execute("SELECT result FROM astra_modelling.jobs WHERE id=%s",
                                      (job_id,)).fetchone()[0] == result
        save(DOC / "reconciliation-summary.json", {key: value for key, value in report.items() if key != "rows"}
             | {"jobId": job_id, "resultVerified": True, "proofSHA256": sha(PROOF)})
        print(json.dumps({"jobId": job_id, "humanCounts": report["humanCounts"],
                          "primaryHoldCounts": report["primaryHoldCounts"], "aiCalls": 0}), flush=True)
    finally:
        reservations.release(receipt)


if __name__ == "__main__":
    sync()
