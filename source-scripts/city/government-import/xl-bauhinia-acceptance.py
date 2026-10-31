"""Run runtime, identity, and neighbour gates on the shared Bauhinia XL patch."""

import json
import shutil
import subprocess
from pathlib import Path

from shapely.geometry import Polygon, box

from run import ROOT, HERE, read, save, digest

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "bauhinia-terrain-diagnostic-20260924"
LOCAL = HERE / "local/government-xl-bauhinia-terrain-20260924"
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
    inputs = {row["uid"]: row for row in
              read(HERE / "local/government-xl-remaining-20260923/recovered/geometry-inputs.json")["rows"]}
    context = {row["uid"]: row for row in read(BASE / "context.json")["rows"]}
    assert len(uids) == 4 and all(uid in inputs and uid in context for uid in uids)
    rows, entries, forms = [], [], {}
    STAGE.mkdir(parents=True, exist_ok=True)
    for uid in uids:
        original = selection[uid]
        identity = context[uid]["identity"]
        assert identity["exactObjectAndCSUID"]
        assert identity["targetCoveredBySourceProjection"] >= .95
        assert identity["sourceExcessFraction"] <= .05
        assert identity["unrelatedIntersectingForms"] == 0
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
    template.update(area="Bauhinia Garden exact government sources",
                    models=entries, counts={"packedModels": len(entries)})
    save(STAGE / "catalogue.json", template)
    save(STAGE / "catalogue-index.json", {"models": len(entries), "catalogues": ["catalogue.json"]})
    save(STAGE / "source-forms.json", forms)
    manifest = ROOT / "3d-viewer/city/data/manifest.json"
    save(DOC / "selection.json.gz", {"batch": "government-xl-bauhinia-terrain-20260924",
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
    metrics = read(DOC / "metrics.json")
    validation = read(DOC / "validation.json")
    neighbour = read(DOC / "neighbour-checks.json")
    native_neighbour = read(DOC / "native-neighbour-checks.json")
    metric_by = {row["uid"]: row for row in metrics["rows"]}
    validation_by = {row["uid"]: row for row in validation["results"]}
    failures = []
    for uid in uids:
        metric = metric_by[uid]
        checked = validation_by[uid]
        if metric.get("error") or not metric.get("sourcePreserved") or metric.get("missingTerrain") or \
           metric.get("maxSamplerDelta", 1e9) > .004:
            failures.append({"uid": uid, "reason": "terrain-or-source-integrity"})
        if any(metric["budget"][key] > metrics["profiles"]["mobile"][key]
               for key in ("triangles", "geometryBytes", "residentBytes")):
            failures.append({"uid": uid, "reason": "mobile-runtime-budget"})
        if checked["outcome"] == "validation-exception" or checked.get("concerns"):
            failures.append({"uid": uid, "reason": "runtime-validation",
                             "concerns": checked.get("concerns", [])})
    blocked = sorted({uid for row in neighbour["patches"] for uid in row["blockedBy"]}
                     - set(native_neighbour.get("resolved", [])) - set(uids))
    if blocked:
        failures.append({"reason": "neighbour-terrain-regression", "uids": blocked})
    if native_neighbour.get("failed"):
        failures.append({"reason": "installed-native-neighbour-regression",
                         "uids": native_neighbour["failed"]})
    report = {"batch": "government-xl-bauhinia-terrain-20260924", "uids": uids,
              "patchSHA256": patch_row["sha256"], "neighbourForms": len(neighbours),
              "passed": not failures, "failures": failures, "aiCalls": 0,
              "modelGeometryChanges": 0, "publication": False}
    save(DOC / "acceptance.json", report)
    print(json.dumps({"passed": report["passed"], "failures": failures,
                      "neighbourForms": len(neighbours)}), flush=True)


if __name__ == "__main__":
    run()
