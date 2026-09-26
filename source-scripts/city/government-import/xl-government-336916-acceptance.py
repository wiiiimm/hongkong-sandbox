"""Run runtime, identity, and neighbour gates on the government building landsd/336916:0 XL patch."""

import json
import shutil
import sys
import subprocess
from pathlib import Path

from shapely.geometry import Polygon, box

from run import ROOT, HERE, read, save, digest

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "government-336916-terrain-diagnostic-20260927"
LOCAL = HERE / "local/government-xl-government-336916-terrain-20260927"
STAGE = LOCAL / "candidates"


def sha(path):
    return digest(Path(path).read_bytes())


def rel(path):
    return str(Path(path).resolve().relative_to(ROOT))


def call(args, allowed=(0,)):
    outcome = subprocess.run(args, cwd=ROOT)
    assert outcome.returncode in allowed, (args, outcome.returncode)


def run():
    patch_result = read(DOC / "result.json")
    assert patch_result["state"] == "terrain-patch-validated-awaiting-model-and-neighbour-checks"
    patch_path = ROOT / patch_result["patchPath"]
    assert sha(patch_path) == patch_result["patchSHA256"]
    uids = patch_result["uids"]
    selection = {row["uid"]: row for row in read(BASE / "selection.json.gz")["rows"]}
    input_paths = [HERE / "local/government-xl-remaining-20260923/recovered/geometry-inputs.json",
                   HERE / "local/government-xl-remaining-held-20260923/recovered/geometry-inputs.json"]
    inputs = {row["uid"]: row for path in input_paths for row in read(path)["rows"]}
    context = {row["uid"]: row for path in (BASE / "context.json", BASE / "context-held.json")
               for row in read(path)["rows"]}
    assert len(uids) == 1 and all(uid in inputs and uid in context for uid in uids)
    rows, entries, forms, identity_resolutions = [], [], {}, []
    STAGE.mkdir(parents=True, exist_ok=True)
    for uid in uids:
        original = selection[uid]
        identity = context[uid]["identity"]
        assert identity["exactObjectAndCSUID"]
        assert identity["targetCoveredBySourceProjection"] >= .95
        assert identity["sourceExcessFraction"] <= .05
        unrelated_area = identity["sourceExcessCoveredByUnrelatedFormsM2"]
        bounded_edge_contact = (identity["unrelatedIntersectingForms"] <= 1
                                and unrelated_area <= 2.5
                                and unrelated_area / identity["sourceProjectionAreaM2"] <= .005
                                and identity["sourceExcessMaximumDistanceFromTargetM"] <= 1.2)
        assert identity["unrelatedIntersectingForms"] == 0
        identity_resolutions.append({"uid": uid, "exactObjectAndCSUID": True,
                                     "targetCoverage": identity["targetCoveredBySourceProjection"],
                                     "sourceExcessFraction": identity["sourceExcessFraction"],
                                     "unrelatedIntersectingForms": identity["unrelatedIntersectingForms"],
                                     "unrelatedAreaM2": unrelated_area,
                                     "boundedEdgeContact": bounded_edge_contact})
        candidate = inputs[uid]["candidate"]
        assert sha(candidate["path"]) == original["sourceSHA256"]
        entry = candidate["entry"]
        assert entry["uid"] == uid and entry["sha256"] == original["sourceSHA256"]
        target = STAGE / entry["asset"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(candidate["path"], target)
        assert sha(target) == original["sourceSHA256"]
        entries.append(entry)
        forms[uid] = original["source"]
        rows.append({"uid": uid, "source": original["source"],
                     "candidate": {"path": str(target), "entry": entry},
                     "native": original["native"]})
    template = read(HERE / "accepted/government-xxl-20260911/catalogue.json")
    template.update(area="government building landsd/336916:0 exact government sources",
                    models=entries, counts={"packedModels": len(entries)})
    save(STAGE / "catalogue.json", template)
    save(STAGE / "catalogue-index.json", {"models": len(entries), "catalogues": ["catalogue.json"]})
    save(STAGE / "source-forms.json", forms)
    save(DOC / "identity-resolution.json", {"rows": identity_resolutions,
                                             "policy": "Exact object/CSUID, at least 95% target coverage, at most 5% source excess, and no unrelated intersecting form.",
                                             "aiCalls": 0, "modelGeometryChanges": 0})
    manifest = ROOT / "3d-viewer/city/data/manifest.json"
    save(DOC / "selection.json.gz", {"batch": "government-xl-government-336916-terrain-20260927",
                                     "manifestSHA256": sha(manifest), "rows": rows, "aiCalls": 0})
    patch = read(patch_path)
    bounds = [patch["meta"]["georef"]["bE"] - 834500,
              816500 - patch["meta"]["georef"]["bN"],
              patch["meta"]["georef"]["bE"] - 834500 + (patch["w"] - 1) * patch["cell"],
              816500 - patch["meta"]["georef"]["bN"] + (patch["h"] - 1) * patch["cell"]]
    patch_row = {"path": rel(patch_path), "sha256": sha(patch_path), "uids": uids,
                 "bounds": bounds, "triangles": len(patch["nativeMesh"]["index"]) // 3}
    save(DOC / "terrain-candidates.json", [patch_row])
    region = box(*bounds)
    manifest_data = read(manifest)
    live = {model["uid"] for url in manifest_data["officialModelCatalogues"]
            for model in read(ROOT / "3d-viewer" / url)["models"]}
    neighbours, hashes = [], {}
    for tile in manifest_data["tiles"]:
        path = ROOT / "3d-viewer" / tile["url"]
        raw = path.read_bytes()
        touched = False
        for building in json.loads(raw)["buildings"]:
            if Polygon(building["rings"][0], building["rings"][1:]).intersects(region):
                neighbours.append({"building": building, "patchIndexes": [0],
                                   "existingNative": building["uid"] in live or bool(building.get("modelGeometry"))})
                touched = True
        if touched:
            hashes[rel(path)] = digest(raw)
    save(DOC / "neighbour-inputs.json.gz", {"rows": neighbours, "inputHashes": hashes,
                                             "candidateIds": uids, "patches": [patch_row]})
    call(["node", str(HERE / "acceptance-metrics.mjs"), "--selection", rel(DOC / "selection.json.gz"),
          "--candidates", rel(STAGE), "--terrain-candidates", rel(DOC / "terrain-candidates.json"),
          "--out", rel(DOC / "metrics.json")])
    call(["node", str(HERE.parent / "building-batch/validate_candidates.mjs"),
          "--candidates", rel(STAGE), "--source-forms", rel(STAGE / "source-forms.json"),
          "--terrain-candidates", rel(DOC / "terrain-candidates.json"),
          "--out", rel(DOC / "validation.json")], allowed=(0, 1))
    call(["node", str(HERE / "check-neighbours.mjs"), rel(DOC) + "/"])
    call(["node", str(HERE / "check-native-neighbours.mjs"), rel(DOC) + "/"])
    if len(sys.argv) > 1 and sys.argv[1] == "prepare":
        print(json.dumps({"prepared": len(uids), "neighbourForms": len(neighbours)}), flush=True)
        return
    metrics = read(DOC / "metrics.json")
    validation = read(DOC / "validation.json")
    neighbour = read(DOC / "neighbour-checks.json")
    native_neighbour = read(DOC / "native-neighbour-checks.json")
    foundation = {row["uid"]: row for row in read(DOC / "foundation.json")["rows"]}
    metric_by = {row["uid"]: row for row in metrics["rows"]}
    validation_by = {row["uid"]: row for row in validation["results"]}
    failures = []
    foundation_resolutions = []
    support_resolutions = []
    for uid in uids:
        metric = metric_by[uid]
        checked = validation_by[uid]
        proof = foundation[uid]["foundation"]
        strict = foundation[uid]["strictFoundationAccepted"]
        bounded = False
        foundation_resolutions.append({"uid": uid, "strict": strict, "boundedException": bounded,
                                       "accepted": strict or bounded,
                                       "originalSourceSHA256": foundation[uid]["sourceSHA256"],
                                       "fullyBuriedUpwardAreaM2": proof["fullyBuriedUpwardAreaM2"],
                                       "minimumGapM": proof["minimumGapM"]})
        if not (strict or bounded):
            failures.append({"uid": uid, "reason": "full-triangle-foundation-check"})
        if metric.get("error") or not metric.get("sourcePreserved") or metric.get("missingTerrain") or \
           metric.get("maxSamplerDelta", 1e9) > .004:
            failures.append({"uid": uid, "reason": "terrain-or-source-integrity"})
        if any(metric["budget"][key] > metrics["profiles"]["mobile"][key]
               for key in ("triangles", "geometryBytes", "residentBytes")):
            failures.append({"uid": uid, "reason": "mobile-runtime-budget"})
        concern = checked.get("concerns", [])
        support_resolutions.append({"uid": uid, "podiumUid": None,
                                    "accepted": False,
                                    "sourceBottomM": checked["terrain"]["sourceYBounds"][0],
                                    "terrainM": checked["terrain"]["minGround"],
                                    "podiumTopM": None})
        if checked["outcome"] == "validation-exception" or concern:
            failures.append({"uid": uid, "reason": "runtime-validation",
                             "concerns": concern})
    blocked = sorted({uid for row in neighbour["patches"] for uid in row["blockedBy"]}
                     - set(native_neighbour.get("resolved", [])) - set(uids))
    if blocked:
        failures.append({"reason": "neighbour-terrain-regression", "uids": blocked})
    failed_native = sorted(set(native_neighbour.get("blocked", []))
                           - set(native_neighbour.get("resolved", [])))
    if failed_native:
        failures.append({"reason": "installed-native-neighbour-regression",
                         "uids": failed_native})
    save(DOC / "foundation-resolution.json", {"rows": foundation_resolutions,
                                                "policy": "Original government source faces remain unchanged; the model requires strict full-triangle foundation acceptance.",
                                                "foundationSHA256": sha(DOC / "foundation.json"),
                                                "aiCalls": 0, "modelGeometryChanges": 0})
    save(DOC / "support-resolution.json", {"rows": support_resolutions,
                                            "policy": "The government building landsd/336916:0 form requires direct terrain contact; no podium exception is accepted.",
                                            "aiCalls": 0, "modelGeometryChanges": 0})
    report = {"batch": "government-xl-government-336916-terrain-20260927", "uids": uids,
              "patchSHA256": patch_row["sha256"], "neighbourForms": len(neighbours),
              "foundationResolutionSHA256": sha(DOC / "foundation-resolution.json"),
              "identityResolutionSHA256": sha(DOC / "identity-resolution.json"),
              "supportResolutionSHA256": sha(DOC / "support-resolution.json"),
              "passed": not failures, "failures": failures, "aiCalls": 0,
              "modelGeometryChanges": 0, "publication": False}
    save(DOC / "acceptance.json", report)
    print(json.dumps({"passed": report["passed"], "failures": failures,
                      "neighbourForms": len(neighbours)}), flush=True)


if __name__ == "__main__":
    run()
