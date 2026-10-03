"""Run current-terrain and runtime checks on recovered XL identity holds."""

import json
import subprocess
import sys
import uuid
from collections import Counter
from pathlib import Path

from run import ROOT, HERE, read, save, digest, reservations

BATCH = "government-xl-remaining-held-20260923"
BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "held-second-pass"
LOCAL = HERE / "local" / BATCH
RECOVERED = LOCAL / "recovered"


def rel(path):
    return str(Path(path).relative_to(ROOT))


def call(args, allowed=(0,)):
    result = subprocess.run(args, cwd=ROOT)
    assert result.returncode in allowed, (args, result.returncode)


def start():
    frozen = read(BASE / "selection.json.gz")
    uids = [row["uid"] for row in frozen["rows"] if row["humanStatus"] == "held-unknown"]
    assert len(uids) == 199
    claim = reservations.claim("codex-xl-remaining-held-" + str(uuid.uuid4()),
                               ["building:" + uid for uid in uids], batch=BATCH)
    assert claim["ok"], claim
    save(LOCAL / "check-reservation.json", json.loads(json.dumps(claim["reservation"], default=str)))
    call([sys.executable, str(HERE.parent / "shared-modelling/reservations.py"),
          "run", "--lease-file", str(LOCAL / "check-reservation.json"), "--",
          sys.executable, __file__, "owned"])


def identity_clear(proof):
    return proof["exactObjectAndCSUID"] and proof["targetCoveredBySourceProjection"] >= .95 and (
        proof["sourceProjectionInsideTarget"] >= .98 or (
            proof["sourceExcessFraction"] <= .10
            and proof["sourceExcessCoveredByUnrelatedFormsM2"] <= 1
            and proof["sourceExcessMaximumDistanceFromTargetM"] <= 10
        )
    )


def owned():
    assert reservations.owns(read(LOCAL / "check-reservation.json"))
    frozen = read(BASE / "selection.json.gz")
    manifest = ROOT / "3d-viewer/city/data/manifest.json"
    recovered = read(RECOVERED / "geometry-inputs.json")
    assert len(recovered["rows"]) == 182 and len(recovered["errors"]) == 17
    source = {row["uid"]: row for row in frozen["rows"] if row["humanStatus"] == "held-unknown"}
    context = read(BASE / "context-held.json")
    assert context["inputSHA256"]["selection"] == digest((BASE / "selection.json.gz").read_bytes())
    assert context["inputSHA256"]["results"] == digest((BASE / "results.json.gz").read_bytes())
    by_context = {row["uid"]: row for row in context["rows"]}
    assert len(by_context) == 182 and not context["errors"]
    chosen = []
    for row in recovered["rows"]:
        uid = row["uid"]
        original = source[uid]
        assert digest((ROOT / "3d-viewer" / original["source"]["tile"]).read_bytes()) == original["source"]["tileSHA256"]
        assert digest(Path(row["candidate"]["path"]).read_bytes()) == original["sourceSHA256"]
        chosen.append({"uid": uid, "source": original["source"], "candidate": row["candidate"],
                       "native": original["native"]})
    save(DOC / "selection.json.gz", {"batch": BATCH, "nativeRun": frozen["nativeRun"],
                                     "manifestSHA256": digest(manifest.read_bytes()),
                                     "rows": chosen, "aiCalls": 0})
    template = read(HERE.parent / "kai-tak-port/staged/catalogue.json")
    template.update(area="Remaining XL held source validation", models=[row["candidate"]["entry"] for row in chosen],
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
    by_validation = {row["uid"]: row for row in validation["results"]}
    by_metric = {row["uid"]: row for row in metrics["rows"]}
    assert set(by_validation) == set(by_metric) == set(by_context) == {row["uid"] for row in chosen}
    rows = []
    for uid, original in source.items():
        row = {"uid": uid, "name": original.get("name"), "sourceSHA256": original["sourceSHA256"],
               "sourceSheet": original["native"]["sheet"], "previousReasons": original["reasons"],
               "aiCalls": 0, "modelGeometryChanges": 0}
        if uid in recovered["errors"]:
            row.update(state="held-source-recovery", reasons=["source-recovery-failed"],
                       recoveryError=recovered["errors"][uid])
        else:
            metric = by_metric[uid]
            identity = by_context[uid]["identity"]
            validation_row = by_validation[uid]
            reasons = []
            if not identity_clear(identity):
                reasons.append("projected-source-identity-or-assembly")
            if original["previousReview"] and original["previousReview"]["state"] in (
                    "held", "source-unavailable", "identity-unresolved", "installed-verified"):
                reasons.append("existing-review-requires-resolution")
            if original["native"]["model"]["state"] != "packed-needs-placement-review":
                reasons.append("native-preparation-held")
            if metric.get("error") or not metric.get("sourcePreserved") or metric.get("sourceSHA256") != original["sourceSHA256"]:
                reasons.append("runtime-or-source-integrity")
            elif metric.get("missingTerrain") or metric.get("minSurfaceGap", -1e9) < -.5 or metric.get("maxLowGap", 1e9) > 1 or metric.get("minLowGap", 1e9) > .1 or metric.get("maxSamplerDelta", 1e9) > .004:
                reasons.append("current-terrain-contact")
            if any(metric["budget"][key] > metrics["profiles"]["mobile"][key]
                   for key in ("triangles", "geometryBytes", "residentBytes")):
                reasons.append("mobile-runtime-budget")
            if validation_row["outcome"] == "validation-exception":
                reasons.append("runtime-validation-exception")
            reasons.extend(set(validation_row.get("concerns", [])) - {
                "sampled-ground-gap-below-model-bottom", "sampled-terrain-above-model-bottom"})
            row.update(state="ready-for-publication-gates" if not reasons else "held-after-second-script-pass",
                       reasons=sorted(set(reasons)), identityClear=identity_clear(identity),
                       currentTerrainContact=not any(item in reasons for item in ("current-terrain-contact", "runtime-or-source-integrity")),
                       identity=identity, metric=metric, validation=validation_row)
        rows.append(row)
    rows.sort(key=lambda item: item["uid"])
    report = {"batch": BATCH, "stage": "exact-projection-current-terrain-v1", "models": len(rows),
              "counts": dict(Counter(row["state"] for row in rows)),
              "reasons": dict(Counter(reason for row in rows for reason in row["reasons"])),
              "rows": rows, "inputHashes": metrics["inputHashes"],
              "selectionSHA256": digest((DOC / "selection.json.gz").read_bytes()),
              "contextSHA256": digest((BASE / "context-held.json").read_bytes()),
              "aiCalls": 0, "geometryChanges": 0, "publication": False}
    save(DOC / "results.json.gz", report)
    save(DOC / "summary.json", {key: value for key, value in report.items() if key not in ("rows", "inputHashes")})
    print(json.dumps({"models": len(rows), "counts": report["counts"], "reasons": report["reasons"]}), flush=True)


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 else start()
