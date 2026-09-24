"""Stage unchanged Downtown 38 XL tower with its mapped solid podium."""

import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from run import ROOT, HERE, read, save, digest, reservations

spec = importlib.util.spec_from_file_location("xl_direct", HERE / "xl-remaining-direct.py")
direct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(direct)

BATCH = "government-xl-remaining-downtown-20260923"
BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "downtown"
LOCAL = HERE / "local" / BATCH
STAGE = HERE / "accepted" / BATCH
UIDS = ("landsd/260748:0",)
SUPPORT_UID = "landsd/267360:0"


def sha(path):
    return digest(Path(path).read_bytes())


def rel(path):
    return str(Path(path).relative_to(ROOT))


def call(args, allowed=(0,)):
    result = subprocess.run(args, cwd=ROOT)
    assert result.returncode in allowed, (args, result.returncode)


def start():
    claim = reservations.claim("codex-xl-remaining-supported-" + str(uuid.uuid4()),
                               ["building:" + uid for uid in (*UIDS, SUPPORT_UID)], batch=BATCH)
    assert claim["ok"], claim
    save(LOCAL / "reservation.json", json.loads(json.dumps(claim["reservation"], default=str)))
    call([sys.executable, str(HERE.parent / "shared-modelling/reservations.py"),
          "run", "--lease-file", str(LOCAL / "reservation.json"), "--",
          sys.executable, __file__, "owned"])


def owned():
    assert reservations.owns(read(LOCAL / "reservation.json"))
    manifest = ROOT / "3d-viewer/city/data/manifest.json"
    selection = read(BASE / "selection.json.gz")
    results = {row["uid"]: row for row in read(BASE / "results.json.gz")["rows"]}
    source = {row["uid"]: row for row in selection["rows"]}
    context = read(BASE / "context.json")
    identity = {row["uid"]: row["identity"] for row in context["rows"]}
    support_report = read(BASE / "support-probe.json")
    supports = {row["uid"]: row for row in support_report["rows"]}
    assert support_report["sourceSHA256"] == sha(BASE / "selection.json.gz")
    assert support_report["resultsSHA256"] == sha(BASE / "results.json.gz")
    recovered = {row["uid"]: row for row in read(HERE / "local/government-xl-remaining-20260923/recovered/geometry-inputs.json")["rows"]}
    manifest_data = read(manifest)
    installed = {model["uid"] for url in manifest_data["officialModelCatalogues"]
                 for model in read(ROOT / "3d-viewer" / url)["models"]}
    assert not (set(UIDS) & installed) and SUPPORT_UID not in installed
    template = read(HERE / "accepted/government-xxl-20260911/catalogue.json")
    models, forms, chosen, decisions = [], [], [], []
    for uid in UIDS:
        original, result, proof = source[uid], results[uid], identity[uid]
        support = supports[uid]
        other = [form for form in proof["intersectingForms"] if form["uid"] != uid]
        assert proof["exactObjectAndCSUID"]
        assert proof["targetCoveredBySourceProjection"] >= .995
        assert proof["sourceExcessFraction"] <= .12
        assert proof["sourceExcessMaximumDistanceFromTargetM"] <= 1.5
        assert proof["sourceExcessCoveredByUnrelatedFormsM2"] <= 1e-6
        assert proof["sourceExcessAreaM2"] - proof["sourceExcessCoveredByAnyOtherFormM2"] <= 1
        assert len(other) == 1 and other[0]["uid"] == SUPPORT_UID and other[0]["sameParent"]
        assert support["passed"] and len(support["candidates"]) == 1
        assert support["candidates"][0]["uid"] == SUPPORT_UID
        assert support["candidates"][0]["lowRimHullCoverage"] >= .97
        assert support["candidates"][0]["targetFootprintCoverage"] >= .8
        assert -.1 <= support["candidates"][0]["verticalMarginM"] <= 1
        assert set(result["reasons"]) - {"ground-contact-unresolved",
                                         "sampled-ground-gap-below-model-bottom",
                                         "sampled-terrain-above-model-bottom"} == set()
        metric = result["metrics"]
        assert metric["sourcePreserved"] and not metric["missingTerrain"]
        assert metric["minSurfaceGap"] >= -.5 and metric["maxSamplerDelta"] <= .004
        assert sha(ROOT / "3d-viewer" / original["source"]["tile"]) == original["source"]["tileSHA256"]
        entry = dict(recovered[uid]["candidate"]["entry"])
        assert entry["sha256"] == original["sourceSHA256"]
        entry.update(priority="landmark", placementReviewed=True, sourceIdentityReviewed=True,
                     identityReviewApproved=True, publicationApproved=False, proceduralWindows=False,
                     placementReview=f"Exact unchanged government tower supported by unchanged same-parent solid podium {SUPPORT_UID}. Source excess is bounded and covered by that podium. Low-rim hull, source hash, identifiers, terrain surface and mobile runtime passed. No AI or geometry edits.")
        asset = STAGE / entry["asset"]
        asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(recovered[uid]["candidate"]["path"], asset)
        assert sha(asset) == entry["sha256"]
        models.append(entry)
        building = dict(original["source"]["building"])
        building["tile"] = Path(original["source"]["tile"]).stem
        forms.append(building)
        chosen.append({"uid": uid, "source": original["source"],
                       "candidate": {"entry": entry, "path": str(asset)}, "native": original["native"]})
        decisions.append({"uid": uid, "name": original.get("name"), "sourceSHA256": entry["sha256"],
                          "supportUid": SUPPORT_UID, "support": support["candidates"][0],
                          "sourceExcessAreaM2": proof["sourceExcessAreaM2"],
                          "sourceExcessCoveredByOtherFormM2": proof["sourceExcessCoveredByAnyOtherFormM2"],
                          "sourceGeometryChanges": 0, "aiCalls": 0})
    template.update(area="Downtown 38 unchanged government XL tower with retained podium",
                    models=models, counts={"packedModels": len(models)},
                    loadingPolicy="Exact source and unchanged basic podium support")
    save(STAGE / "catalogue.json", template)
    save(STAGE / "catalogue-index.json", {"models": len(models), "catalogues": ["catalogue.json"]})
    save(STAGE / "source-forms.json", forms)
    save(LOCAL / "source-forms.json", {uid: source[uid]["source"] for uid in UIDS})
    destination = "city/data/official-models/" + BATCH + "/catalogue.json"
    save(STAGE / "plan.json", {"areas": [{"area": template["area"],
                                           "catalogue": rel(STAGE / "catalogue.json"),
                                           "destination": destination}]})
    save(STAGE / "browser-config.json", {"stage": rel(STAGE) + "/", "doc": rel(DOC) + "/",
                                         "catalogueURL": destination, "terrain": [], "fitBox": True,
                                         "browserUids": list(UIDS), "failureTestUids": list(UIDS),
                                         "retainedBuildingUidsByModel": {uid: [SUPPORT_UID] for uid in UIDS}})
    save(DOC / "selection.json.gz", {"batch": BATCH, "nativeRun": selection["nativeRun"],
                                     "manifestSHA256": sha(manifest), "rows": chosen, "aiCalls": 0})
    call(["node", str(HERE / "acceptance-metrics.mjs"), "--selection", rel(DOC / "selection.json.gz"),
          "--candidates", rel(STAGE), "--out", rel(DOC / "metrics.json")])
    call(["node", str(HERE.parent / "building-batch/validate_candidates.mjs"),
          "--candidates", rel(STAGE), "--source-forms", rel(LOCAL / "source-forms.json"),
          "--out", rel(DOC / "validation.json")], allowed=(0, 1))
    metrics, validation = read(DOC / "metrics.json"), read(DOC / "validation.json")
    assert validation["loaderAccepted"] == validation["checksPassed"] == len(UIDS)
    assert validation["exceptions"] == 0
    assert {row["uid"] for row in metrics["rows"]} == set(UIDS)
    for metric in metrics["rows"]:
        assert metric["sourcePreserved"] and not metric["missingTerrain"]
        assert metric["minSurfaceGap"] >= -.5 and metric["maxSamplerDelta"] <= .004
        assert all(metric["budget"][key] <= metrics["profiles"]["mobile"][key]
                   for key in ("triangles", "geometryBytes", "residentBytes"))
    assert all(not (set(row.get("concerns", [])) - {
        "sampled-ground-gap-below-model-bottom", "sampled-terrain-above-model-bottom"})
               for row in validation["results"])
    decision = {"batch": BATCH, "policy": "original-government-xl-same-parent-podium-v1",
                "uids": list(UIDS), "rows": decisions, "supportUid": SUPPORT_UID,
                "supportProofSHA256": sha(BASE / "support-probe.json"),
                "selectionSHA256": sha(DOC / "selection.json.gz"),
                "contextSHA256": sha(BASE / "context.json"),
                "metricsSHA256": sha(DOC / "metrics.json"),
                "validationSHA256": sha(DOC / "validation.json"),
                "catalogueSHA256": sha(STAGE / "catalogue.json"),
                "planSHA256": sha(STAGE / "plan.json"),
                "inputHashes": metrics["inputHashes"],
                "aiCalls": 0, "geometryChanges": 0, "publication": False}
    save(DOC / "decision.json", decision)
    print(json.dumps({"staged": list(UIDS), "supportUid": SUPPORT_UID, "aiCalls": 0}), flush=True)


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 else start()
