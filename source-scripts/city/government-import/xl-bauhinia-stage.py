"""Stage four verified original Bauhinia Garden XL models for browser checks."""

import json
import shutil
from pathlib import Path

from run import ROOT, HERE, read, save, digest

BATCH = "government-xl-bauhinia-20260924"
DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/bauhinia-terrain-diagnostic-20260924"
LOCAL = HERE / "local/government-xl-bauhinia-terrain-20260924"
STAGE = HERE / "accepted" / BATCH


def sha(path):
    return digest(Path(path).read_bytes())


def rel(path):
    return str(Path(path).resolve().relative_to(ROOT))


def run():
    accepted = read(DOC / "acceptance.json")
    assert accepted["passed"] and not accepted["failures"] and accepted["aiCalls"] == 0
    uids = accepted["uids"]
    original = read(LOCAL / "candidates/catalogue.json")
    assert {row["uid"] for row in original["models"]} == set(uids)
    STAGE.mkdir(parents=True, exist_ok=True)
    entries = []
    for source in original["models"]:
        entry = dict(source)
        asset = STAGE / entry["asset"]
        asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(LOCAL / "candidates" / entry["asset"], asset)
        assert sha(asset) == entry["sha256"]
        entry.update(priority="detail", proceduralWindows=False, sourceIdentityReviewed=True,
                     identityReviewApproved=True, placementReviewed=True, publicationApproved=True,
                     suppressesBuildingUids=[],
                     placementReview=("Exact government source object ID and Building CSUID, unique viewer match, "
                                      "at least 95% target coverage and at most 5% source excess. Four original "
                                      "tower assets and one exact-source terrain patch pass loader, foundation, "
                                      "runtime and neighbour checks without geometry edits or AI modelling."))
        entries.append(entry)
    original.update(area="Bauhinia Garden original government towers",
                    loadingPolicy="Exact unchanged source and government terrain accepted by scripted identity, runtime and neighbour checks",
                    models=entries, counts={"packedModels": len(entries)})
    save(STAGE / "catalogue.json", original)
    save(STAGE / "catalogue-index.json", {"models": len(entries), "catalogues": ["catalogue.json"]})
    source_forms = read(LOCAL / "candidates/source-forms.json")
    save(STAGE / "source-forms.json", [source_forms[uid]["building"] for uid in uids])
    patch_row = read(DOC / "terrain-candidates.json")[0]
    patch_source = ROOT / patch_row["path"]
    assert sha(patch_source) == patch_row["sha256"]
    patch = read(patch_source)
    patch_target = STAGE / patch_source.name
    shutil.copyfile(patch_source, patch_target)
    assert sha(patch_target) == patch_row["sha256"]
    destination = "city/data/official-models/" + BATCH + "/catalogue.json"
    terrain = {"source": rel(patch_target), "sha256": sha(patch_target),
               "destination": "city/data/" + patch_target.name,
               "resolution": patch["cell"], "area": "Bauhinia Garden exact government terrain"}
    save(STAGE / "plan.json", {"areas": [{"area": original["area"],
                                           "catalogue": rel(STAGE / "catalogue.json"),
                                           "destination": destination}],
                               "topLevelTerrainPatches": [terrain]})
    save(STAGE / "browser-config.json", {"stage": rel(STAGE) + "/", "doc": rel(DOC) + "/",
                                         "catalogueURL": destination, "terrain": [terrain],
                                         "fitBox": True, "browserUids": uids, "failureTestUids": uids,
                                         "retainedBuildingUidsByModel": {uid: [] for uid in uids},
                                         "samplerToleranceByModel": {}})
    save(DOC / "stage.json", {"batch": BATCH, "uids": uids,
                              "catalogueSHA256": sha(STAGE / "catalogue.json"),
                              "planSHA256": sha(STAGE / "plan.json"),
                              "terrainSHA256": sha(patch_target), "aiCalls": 0,
                              "modelGeometryChanges": 0, "publication": False})
    print(json.dumps({"staged": len(uids), "batch": BATCH}), flush=True)


if __name__ == "__main__":
    run()
