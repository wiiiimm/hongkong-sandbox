"""Run exact geometry, identity, terrain and runtime checks on recovered XL retries."""

import importlib.util
import json
import subprocess
import sys
import uuid
from collections import Counter
from pathlib import Path

from run import ROOT, HERE, read, save, digest, reservations, connect, jobs, Jsonb, dict_row

spec = importlib.util.spec_from_file_location("xl_context", HERE / "xl-final-script-pass.py")
context = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context)

BATCH = "government-xl-source-http-retry-check-20260924"
BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "http-retry-check-20260924"
LOCAL = HERE / "local/government-xl-source-http-retry-20260924"
RECOVERED = LOCAL / "recovered"


def sha(path):
    return digest(Path(path).read_bytes())


def rel(path):
    return str(Path(path).relative_to(ROOT))


def call(args, allowed=(0,)):
    result = subprocess.run(args, cwd=ROOT)
    assert result.returncode in allowed, (args, result.returncode)


def start():
    recovered = read(RECOVERED / "geometry-inputs.json")
    uids = [row["uid"] for row in recovered["rows"]]
    assert len(uids) == 10 and not recovered["errors"]
    claim = reservations.claim("codex-xl-http-check-" + str(uuid.uuid4()),
                               ["building:" + uid for uid in uids], batch=BATCH)
    assert claim["ok"], claim
    save(LOCAL / "check-reservation.json", json.loads(json.dumps(claim["reservation"], default=str)))
    call([sys.executable, str(HERE.parent / "shared-modelling/reservations.py"),
          "run", "--lease-file", str(LOCAL / "check-reservation.json"), "--",
          sys.executable, __file__, "owned"])


def owned():
    assert reservations.owns(read(LOCAL / "check-reservation.json"))
    original = {row["uid"]: row for row in read(BASE / "selection.json.gz")["rows"]}
    recovered = read(RECOVERED / "geometry-inputs.json")
    rows = recovered["rows"]
    assert len(rows) == 10 and not recovered["errors"]
    context.s.LOCAL = RECOVERED
    identity = {}
    chosen = []
    for row in rows:
        uid = row["uid"]
        source = original[uid]
        assert sha(row["candidate"]["path"]) == source["sourceSHA256"]
        assert sha(ROOT / "3d-viewer" / source["source"]["tile"]) == source["source"]["tileSHA256"]
        triangles = context.s.glb_triangles(source)
        lo, hi = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
        forms = context.load_forms([lo[0] - 2, lo[2] - 2, hi[0] + 2, hi[2] + 2])
        identity[uid] = context.identity_context(source, triangles, forms)
        chosen.append({"uid": uid, "source": source["source"],
                       "candidate": row["candidate"], "native": source["native"]})
    save(DOC / "identity.json", {"rows": [{"uid": uid, "identity": item} for uid, item in identity.items()],
                                  "selectionSHA256": sha(BASE / "selection.json.gz"),
                                  "retrySHA256": sha(BASE / "http-retry-20260924.json"), "aiCalls": 0})
    save(DOC / "selection.json.gz", {"batch": BATCH, "nativeRun": read(BASE / "selection.json.gz")["nativeRun"],
                                      "manifestSHA256": sha(ROOT / "3d-viewer/city/data/manifest.json"),
                                      "rows": chosen, "aiCalls": 0})
    template = read(HERE.parent / "kai-tak-port/staged/catalogue.json")
    template.update(area="Recovered XL source runtime checks", models=[row["candidate"]["entry"] for row in chosen],
                    counts={"packedModels": len(chosen)})
    save(RECOVERED / "catalogue.json", template)
    save(RECOVERED / "catalogue-index.json", {"models": len(chosen), "catalogues": ["catalogue.json"]})
    save(LOCAL / "source-forms.json", {row["uid"]: row["source"] for row in chosen})
    call(["node", str(HERE.parent / "building-batch/validate_candidates.mjs"),
          "--candidates", rel(RECOVERED), "--source-forms", rel(LOCAL / "source-forms.json"),
          "--out", rel(DOC / "validation.json")], allowed=(0, 1))
    call(["node", str(HERE / "acceptance-metrics.mjs"), "--selection", rel(DOC / "selection.json.gz"),
          "--candidates", rel(RECOVERED), "--out", rel(DOC / "metrics.json")])
    validation = read(DOC / "validation.json")
    metrics = read(DOC / "metrics.json")
    by_v = {row["uid"]: row for row in validation["results"]}
    by_m = {row["uid"]: row for row in metrics["rows"]}
    assert set(by_v) == set(by_m) == set(identity)
    outcomes = []
    for uid in sorted(identity):
        proof, metric, checked = identity[uid], by_m[uid], by_v[uid]
        source = original[uid]
        clear = (proof["exactObjectAndCSUID"] and proof["targetCoveredBySourceProjection"] >= .95
                 and proof["sourceExcessFraction"] <= .05)
        reasons = []
        if not clear:
            reasons.append("projected-source-identity-or-assembly")
        if (metric.get("error") or not metric.get("sourcePreserved")
                or metric.get("sourceSHA256") != source["sourceSHA256"]):
            reasons.append("runtime-or-source-integrity")
        elif (metric.get("missingTerrain") or metric.get("minSurfaceGap", -1e9) < -.5
              or metric.get("maxLowGap", 1e9) > 1 or metric.get("minLowGap", 1e9) > .1
              or metric.get("maxSamplerDelta", 1e9) > .004):
            reasons.append("current-terrain-contact")
        if checked["outcome"] == "validation-exception":
            reasons.append("runtime-validation-exception")
        reasons.extend(set(checked.get("concerns", [])) - {
            "sampled-ground-gap-below-model-bottom", "sampled-terrain-above-model-bottom"})
        if any(metric["budget"][key] > metrics["profiles"]["mobile"][key]
               for key in ("triangles", "geometryBytes", "residentBytes")):
            reasons.append("mobile-runtime-budget")
        outcomes.append({"uid": uid, "name": source["name"], "sourceSHA256": source["sourceSHA256"],
                         "sourceSheet": source["native"]["sheet"], "humanStatus": "held-unknown" if reasons else "in-process",
                         "reasons": sorted(set(reasons)), "identity": proof, "metric": metric,
                         "validation": checked, "aiCalls": 0, "geometryChanges": 0})
    report = {"batch": BATCH, "stage": "recovered-source-checks-v1", "models": len(outcomes),
              "humanCounts": dict(Counter(row["humanStatus"] for row in outcomes)),
              "reasons": dict(Counter(reason for row in outcomes for reason in row["reasons"])),
              "rows": outcomes, "inputHashes": metrics["inputHashes"],
              "aiCalls": 0, "geometryChanges": 0, "publication": False}
    save(DOC / "results.json.gz", report)
    save(DOC / "summary.json", {key: value for key, value in report.items() if key not in ("rows", "inputHashes")})
    receipt = read(LOCAL / "check-reservation.json")
    job_id = jobs.enqueue(BATCH, report["stage"], {"evidence": rel(DOC / "results.json.gz"),
                                                      "sha256": sha(DOC / "results.json.gz")})
    job = jobs.claim(BATCH, receipt["owner"], [report["stage"]], lease_seconds=1800)
    assert job and job["id"] == job_id
    result = {**report, "evidence": {"path": rel(DOC / "results.json.gz"),
                                      "sha256": sha(DOC / "results.json.gz")}}
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
        assert connection.execute("SELECT result FROM astra_modelling.jobs WHERE id=%s", (job_id,)).fetchone()[0] == result
    save(DOC / "neon-sync.json", {"jobId": job_id, "resultVerified": True, "evidenceSHA256": sha(DOC / "results.json.gz")})
    print(json.dumps({"humanCounts": report["humanCounts"], "reasons": report["reasons"],
                      "jobId": job_id}), flush=True)


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 else start()
