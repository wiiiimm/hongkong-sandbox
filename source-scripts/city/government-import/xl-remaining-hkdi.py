"""Stage unchanged HKDI XL wings whose source excess belongs to the same parent."""

import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from run import ROOT, HERE, read, save, digest, reservations

BATCH = "government-xl-remaining-hkdi-20260923"
BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "hkdi"
LOCAL = HERE / "local" / BATCH
STAGE = HERE / "accepted" / BATCH
UIDS = ("landsd/88345:0", "landsd/89615:0")


def sha(path):
    return digest(Path(path).read_bytes())


def rel(path):
    return str(Path(path).relative_to(ROOT))


def call(args):
    subprocess.run(args, cwd=ROOT, check=True)


def start():
    claim = reservations.claim("codex-xl-remaining-direct-" + str(uuid.uuid4()),
                               ["building:" + uid for uid in UIDS], batch=BATCH)
    assert claim["ok"], claim
    save(LOCAL / "reservation.json", json.loads(json.dumps(claim["reservation"], default=str)))
    call([sys.executable, str(HERE.parent / "shared-modelling/reservations.py"),
          "run", "--lease-file", str(LOCAL / "reservation.json"), "--",
          sys.executable, __file__, "owned"])


def identity_clear(proof):
    parent = proof["target"]["parent"]
    same_parent_forms = [form for form in proof["intersectingForms"]
                         if form["uid"] != proof["target"]["uid"] and form["parent"] == parent]
    return (proof["exactObjectAndCSUID"]
            and proof["targetCoveredBySourceProjection"] >= .999
            and proof["sourceExcessCoveredByUnrelatedFormsM2"] <= 1e-6
            and proof["sourceExcessAreaM2"] - proof["sourceExcessCoveredByAnyOtherFormM2"] <= .1
            and proof["sourceExcessMaximumDistanceFromTargetM"] <= 3
            and len(same_parent_forms) == 1
            and same_parent_forms[0]["fractionOfForm"] <= .02)


def owned():
    assert reservations.owns(read(LOCAL / "reservation.json"))
    manifest = ROOT / "3d-viewer/city/data/manifest.json"
    selection = read(BASE / "selection.json.gz")
    # Earlier XL installations changed only the catalogue list. Source tile
    # hashes are checked for each selected wing below.
    assert read(manifest)["tiles"]
    results = read(BASE / "results.json.gz")
    assert results["jobId"] == "fe103e108561a902feb58a70aecc894844d48a3ab78f5dab20aff19ce93ba541"
    context = read(BASE / "context.json")
    assert context["inputSHA256"]["selection"] == sha(BASE / "selection.json.gz")
    assert context["inputSHA256"]["results"] == sha(BASE / "results.json.gz")
    by_source = {row["uid"]: row for row in selection["rows"]}
    by_result = {row["uid"]: row for row in results["rows"]}
    by_context = {row["uid"]: row for row in context["rows"]}
    recovered = {row["uid"]: row for row in read(HERE / "local/government-xl-remaining-20260923/recovered/geometry-inputs.json")["rows"]}
    assert set(UIDS) <= by_source.keys() & by_result.keys() & by_context.keys() & recovered.keys()
    manifest_data = read(manifest)
    installed = {model["uid"] for url in manifest_data["officialModelCatalogues"]
                 for model in read(ROOT / "3d-viewer" / url)["models"]}
    template = read(HERE / "accepted/government-xxl-20260911/catalogue.json")
    models, forms, chosen, decisions, retained = [], [], [], [], {}
    for uid in UIDS:
        source = by_source[uid]
        outcome = by_result[uid]
        evidence = by_context[uid]
        identity = evidence["identity"]
        assert uid not in installed and not source["reasons"]
        assert outcome["humanStatus"] == "in-process" and not outcome["reasons"]
        assert identity_clear(identity) and evidence["sourceSHA256"] == source["sourceSHA256"]
        assert sha(ROOT / "3d-viewer" / source["source"]["tile"]) == source["source"]["tileSHA256"]
        assert outcome["metrics"]["sourcePreserved"] and not outcome["metrics"]["missingTerrain"]
        assert outcome["metrics"]["minSurfaceGap"] >= -.5
        assert outcome["metrics"]["maxLowGap"] <= 1 and outcome["metrics"]["minLowGap"] <= .1
        assert outcome["metrics"]["maxSamplerDelta"] <= .004

        entry = dict(recovered[uid]["candidate"]["entry"])
        assert entry["sha256"] == source["sourceSHA256"]
        entry.update(priority="landmark", placementReviewed=True, sourceIdentityReviewed=True,
                     identityReviewApproved=True, publicationApproved=False, proceduralWindows=False,
                     placementReview="Exact unchanged government XL wing: original identifiers and SHA, complete target projection, source excess inside the same-parent HKDI form, sampled terrain contact and mobile runtime checks. No AI or source geometry edits.")
        asset = STAGE / entry["asset"]
        asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(recovered[uid]["candidate"]["path"], asset)
        assert sha(asset) == entry["sha256"]
        models.append(entry)
        building = dict(source["source"]["building"])
        building["tile"] = Path(source["source"]["tile"]).stem
        forms.append(building)
        chosen.append({"uid": uid, "source": source["source"],
                       "candidate": {"entry": entry, "path": str(asset)}, "native": source["native"]})
        other = sorted({form["uid"] for form in identity["intersectingForms"]
                        if form["uid"] != uid and form["uid"] not in installed})
        if other:
            retained[uid] = other
        decisions.append({"uid": uid, "name": source.get("name"), "sourceSHA256": entry["sha256"],
                          "targetCoverage": identity["targetCoveredBySourceProjection"],
                          "sourceInsideTarget": identity["sourceProjectionInsideTarget"],
                          "sourceExcessFraction": identity["sourceExcessFraction"],
                          "retainedForms": other, "sourceGeometryChanges": 0, "aiCalls": 0})
    template.update(area="HKDI XL same-parent original government imports", models=models,
                    counts={"packedModels": len(models)},
                    loadingPolicy="Exact unchanged source; scripted same-parent identity, terrain and runtime checks")
    save(STAGE / "catalogue.json", template)
    save(STAGE / "catalogue-index.json", {"models": len(models), "catalogues": ["catalogue.json"]})
    save(STAGE / "source-forms.json", forms)
    save(LOCAL / "source-forms.json", {uid: by_source[uid]["source"] for uid in UIDS})
    destination = "city/data/official-models/" + BATCH + "/catalogue.json"
    save(STAGE / "plan.json", {"areas": [{"area": template["area"],
                                           "catalogue": rel(STAGE / "catalogue.json"),
                                           "destination": destination}]})
    save(STAGE / "browser-config.json", {"stage": rel(STAGE) + "/", "doc": rel(DOC) + "/",
                                         "catalogueURL": destination, "terrain": [], "fitBox": True,
                                         "browserUids": list(UIDS), "failureTestUids": list(UIDS),
                                         "retainedBuildingUidsByModel": retained})
    save(DOC / "selection.json.gz", {"batch": BATCH, "nativeRun": selection["nativeRun"],
                                     "manifestSHA256": sha(manifest), "rows": chosen,
                                     "aiCalls": 0})
    call(["node", str(HERE / "acceptance-metrics.mjs"), "--selection", rel(DOC / "selection.json.gz"),
          "--candidates", rel(STAGE), "--out", rel(DOC / "metrics.json")])
    call(["node", str(HERE.parent / "building-batch/validate_candidates.mjs"),
          "--candidates", rel(STAGE), "--source-forms", rel(LOCAL / "source-forms.json"),
          "--out", rel(DOC / "validation.json")])
    metrics, validation = read(DOC / "metrics.json"), read(DOC / "validation.json")
    assert validation["loaderAccepted"] == validation["checksPassed"] == len(UIDS)
    assert validation["exceptions"] == 0
    assert {row["uid"] for row in metrics["rows"]} == set(UIDS)
    for metric in metrics["rows"]:
        previous = by_result[metric["uid"]]["metrics"]
        assert metric["sourceSHA256"] == previous["sourceSHA256"]
        assert metric["sourcePreserved"] and not metric["missingTerrain"]
        assert metric["minSurfaceGap"] >= -.5 and metric["minLowGap"] <= .1
        assert metric["maxLowGap"] <= 1 and metric["maxSamplerDelta"] <= .004
        assert all(metric["budget"][key] <= metrics["profiles"]["mobile"][key]
                   for key in ("triangles", "geometryBytes", "residentBytes"))
    decision = {"batch": BATCH, "policy": "original-government-xl-same-parent-v1",
                "sourceJobId": results["jobId"], "uids": list(UIDS), "rows": decisions,
                "inputHashes": metrics["inputHashes"],
                "selectionSHA256": sha(DOC / "selection.json.gz"),
                "contextSHA256": sha(BASE / "context.json"),
                "metricsSHA256": sha(DOC / "metrics.json"),
                "validationSHA256": sha(DOC / "validation.json"),
                "catalogueSHA256": sha(STAGE / "catalogue.json"),
                "planSHA256": sha(STAGE / "plan.json"),
                "aiCalls": 0, "geometryChanges": 0, "publication": False}
    save(DOC / "decision.json", decision)
    print(json.dumps({"staged": list(UIDS), "retained": retained, "aiCalls": 0}), flush=True)


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 else start()
