"""Stage the unchanged Cainiao government podium and tower as a support-first pair."""

import json
import shutil

from run import ROOT, HERE, read, save, digest

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "cainiao-pair-browser-20260927"
BATCH = "government-xl-cainiao-pair-20260927"
STAGE = HERE / "accepted" / BATCH
LOCAL = HERE / "local/government-xl-cainiao-pair-checks-20260927"
PODIUM = "landsd/327178:0"
TOWER = "landsd/293822:0"


def sha(path):
    return digest(path.read_bytes())


def rel(path):
    return str(path.relative_to(ROOT))


def run():
    source = read(LOCAL / "candidates/catalogue.json")
    assert [row["uid"] for row in source["models"]] == [PODIUM, TOWER]
    proof = read(BASE / "cainiao-source-support-proof-20260927.json")
    assert proof["passed"] and proof["contactHullTargetCoverage"] >= .85 and proof["within05"] >= 100
    foundation = {row["uid"]: row for row in read(BASE / "cainiao-pair-foundation-20260927.json")["rows"]}
    assert set(foundation) == {PODIUM, TOWER}
    assert all(row["strictFoundationAccepted"] and row["foundation"]["fullyBuriedUpwardTriangles"] == 0 for row in foundation.values())
    metrics = read(LOCAL / "metrics.json")
    assert all(not row.get("error") and row["sourcePreserved"] and row["missingTerrain"] == 0
               and row["maxSamplerDelta"] <= .004 and
               all(row["budget"][key] <= metrics["profiles"]["mobile"][key]
                   for key in ("triangles", "geometryBytes", "residentBytes")) for row in metrics["rows"])
    validation = read(LOCAL / "validation.json")
    assert validation["loaderAccepted"] == validation["checksPassed"] == 2
    assert {row["uid"]: row["concerns"] for row in validation["results"]} == {
        PODIUM: [], TOWER: ["sampled-ground-gap-below-model-bottom"]}
    assert not read(LOCAL / "neighbour-checks.json")["patches"][0]["blockedBy"]
    assert not read(LOCAL / "native-neighbour-checks.json")["blocked"]
    patch_row = read(LOCAL / "terrain-candidates.json")[0]
    patch_source = ROOT / patch_row["path"]
    assert sha(patch_source) == patch_row["sha256"]
    STAGE.mkdir(parents=True, exist_ok=True)
    entries = []
    for row in source["models"]:
        entry = dict(row)
        src = LOCAL / "candidates" / entry["asset"]
        target = STAGE / entry["asset"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
        assert sha(target) == entry["sha256"]
        entry.update(priority="landmark", proceduralWindows=False, sourceIdentityReviewed=True,
                     identityReviewApproved=True, placementReviewed=True, publicationApproved=True,
                     suppressesBuildingUids=[],
                     placementReview="Exact original government source, pinned source identity, full-triangle terrain, contact, neighbour and runtime checks. No model geometry edits or AI modelling.")
        if entry["uid"] == TOWER:
            entry["supportDependencies"] = [{"uid": PODIUM, "state": "candidate",
                                              "csuid": source["models"][0]["buildingCSUID"],
                                              "sha256": source["models"][0]["sha256"]}]
        entries.append(entry)
    patch = STAGE / patch_source.name
    shutil.copyfile(patch_source, patch)
    assert sha(patch) == patch_row["sha256"]
    catalogue = read(HERE / "accepted/government-xxl-20260911/catalogue.json")
    catalogue.update(area="Cainiao Smart Gateway original government podium and tower",
                     loadingPolicy="Exact original pair; source podium loads before and remains with tower",
                     models=entries, counts={"packedModels": 2})
    save(STAGE / "catalogue.json", catalogue)
    save(STAGE / "catalogue-index.json", {"models": 2, "catalogues": ["catalogue.json"]})
    save(STAGE / "source-forms.json", [read(LOCAL / "candidates/source-forms.json")[uid]["building"]
                                        for uid in (PODIUM, TOWER)])
    terrain = {"source": rel(patch), "sha256": sha(patch),
               "destination": "city/data/" + patch.name,
               "resolution": read(patch)["cell"],
               "area": "Cainiao Smart Gateway two-sheet original government terrain with retained parent under disjoint forms"}
    destination = "city/data/official-models/" + BATCH + "/catalogue.json"
    save(STAGE / "plan.json", {"areas": [{"area": catalogue["area"],
                                           "catalogue": rel(STAGE / "catalogue.json"),
                                           "destination": destination}],
                               "topLevelTerrainPatches": [terrain]})
    save(STAGE / "browser-config.json", {"stage": rel(STAGE) + "/", "doc": rel(DOC) + "/",
                                          "catalogueURL": destination, "terrain": [terrain],
                                          "fitBox": True, "browserUids": [PODIUM, TOWER],
                                          "failureTestUids": [PODIUM, TOWER],
                                          "retainedBuildingUidsByModel": {
                                              PODIUM: ["way/102137667:0"],
                                              TOWER: ["way/102137667:0"]}})
    save(DOC / "stage.json", {"batch": BATCH, "uids": [PODIUM, TOWER],
                              "catalogueSHA256": sha(STAGE / "catalogue.json"),
                              "planSHA256": sha(STAGE / "plan.json"),
                              "terrainSHA256": terrain["sha256"],
                              "sourceSHA256s": {row["uid"]: row["sha256"] for row in entries},
                              "aiCalls": 0, "modelGeometryChanges": 0, "publication": False})
    print(json.dumps({"staged": [PODIUM, TOWER], "batch": BATCH, "supportCoverage": proof["contactHullTargetCoverage"]}), flush=True)


if __name__ == "__main__":
    run()
