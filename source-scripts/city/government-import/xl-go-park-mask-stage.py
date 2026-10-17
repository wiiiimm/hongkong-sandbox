"""Stage unchanged GO PARK source with its original terrain."""

import json
import shutil

from run import ROOT, HERE, read, save, digest

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "go-park-mask-browser-20260929"
SOURCE = BASE / "go-park-mask-final-20260929"
LOCAL = HERE / "local/government-xl-go-park-terrain-20260929"
BATCH = "government-xl-go-park-mask-20260929"
STAGE = HERE / "accepted" / BATCH
UID = "landsd/318499:0"


def sha(path):
    return digest(path.read_bytes())


def rel(path):
    return str(path.relative_to(ROOT))


def run():
    foundation = read(SOURCE / "foundation.json")
    assert foundation["strictFoundationAccepted"] and foundation["foundation"]["fullyBuriedUpwardTriangles"] == 0
    checks = read(SOURCE / "checks.json")
    assert checks["uid"] == UID and checks["sourcePreserved"] and checks["missingTerrainSamples"] == 0
    assert checks["maxSamplerDeltaM"] <= .004 and not checks["blockedNeighbourUids"]
    assert not checks["blockedNativeNeighbourUids"]
    assert checks["runtimeConcerns"] == []
    metrics = read(SOURCE / "metrics.json")
    row = metrics["rows"][0]
    assert all(row["budget"][key] <= metrics["profiles"]["mobile"][key]
               for key in ("triangles", "geometryBytes", "residentBytes"))
    catalogue = read(LOCAL / "candidates/catalogue.json")
    assert len(catalogue["models"]) == 1 and catalogue["models"][0]["uid"] == UID
    entry = dict(catalogue["models"][0])
    assert entry["sha256"] == foundation["sourceSHA256"]
    entry.update(priority="landmark", proceduralWindows=False, sourceIdentityReviewed=True,
                 identityReviewApproved=True, placementReviewed=True, publicationApproved=True,
                 suppressesBuildingUids=[],
                 placementReview="Exact original government source and footprint, complete source foundation, terrain contact, neighbour and runtime checks; no geometry edits or AI modelling.")
    STAGE.mkdir(parents=True, exist_ok=True)
    target = STAGE / entry["asset"]
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(LOCAL / "candidates" / entry["asset"], target)
    assert sha(target) == entry["sha256"]
    staged = read(HERE / "accepted/government-xxl-20260911/catalogue.json")
    staged.update(area="GO PARK original government source",
                  loadingPolicy="Exact original source with government TIN with parent-ground masks and full foundation proof",
                  models=[entry], counts={"packedModels": 1})
    save(STAGE / "catalogue.json", staged)
    save(STAGE / "catalogue-index.json", {"models": 1, "catalogues": ["catalogue.json"]})
    source_form = read(LOCAL / "candidates/source-forms.json")[UID]["building"]
    save(STAGE / "source-forms.json", [source_form])
    result = read(SOURCE / "result.json")
    source_patch = ROOT / result["patchPath"]
    assert sha(source_patch) == result["patchSHA256"]
    patch = STAGE / source_patch.name
    shutil.copyfile(source_patch, patch)
    assert sha(patch) == result["patchSHA256"]
    terrain = {"source": rel(patch), "sha256": sha(patch),
               "destination": "city/data/" + patch.name,
               "resolution": read(patch)["cell"],
               "area": "GO PARK government terrain with retained neighbor ground"}
    destination = "city/data/official-models/" + BATCH + "/catalogue.json"
    save(STAGE / "plan.json", {"areas": [{"area": staged["area"],
                                           "catalogue": rel(STAGE / "catalogue.json"),
                                           "destination": destination}],
                               "topLevelTerrainPatches": [terrain]})
    save(STAGE / "browser-config.json", {"stage": rel(STAGE) + "/", "doc": rel(DOC) + "/",
                                          "catalogueURL": destination, "terrain": [terrain],
                                          "retainedBuildingUids": ["landsd/323150:0", "landsd/325612:0", "landsd/325613:0"], "fitBox": True, "browserUids": [UID], "failureTestUids": [UID]})
    save(DOC / "stage.json", {"batch": BATCH, "uids": [UID],
                              "catalogueSHA256": sha(STAGE / "catalogue.json"),
                              "planSHA256": sha(STAGE / "plan.json"),
                              "terrainSHA256": sha(patch), "sourceSHA256": entry["sha256"],
                              "aiCalls": 0, "modelGeometryChanges": 0, "publication": False})
    print(json.dumps({"staged": UID, "terrainSHA256": sha(patch), "aiCalls": 0}), flush=True)


if __name__ == "__main__":
    run()
