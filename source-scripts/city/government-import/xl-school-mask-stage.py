"""Stage the accepted unchanged school source and source-preserving terrain mask."""

import json
import shutil
from pathlib import Path

from run import ROOT, HERE, read, save, digest


BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "diocesan-girls-school-mask-browser-20260927"
BATCH = "government-xl-diocesan-girls-school-mask-20260927"
PREVIEW = HERE / "local/government-xl-diocesan-girls-school-browser-stage-20260927"
STAGE = HERE / "accepted" / BATCH
UID = "landsd/257352:0"


def sha(path):
    return digest(Path(path).read_bytes())


def rel(path):
    return str(Path(path).relative_to(ROOT))


def run():
    accepted = read(DOC / "acceptance.json")
    assert accepted["passed"] and accepted["uids"] == [UID]
    assert accepted["aiCalls"] == accepted["modelGeometryChanges"] == 0
    source_patch = ROOT / accepted["candidatePatch"]["path"]
    assert sha(source_patch) == accepted["candidatePatch"]["sha256"]
    preview = read(PREVIEW / "catalogue.json")
    assert [entry["uid"] for entry in preview["models"]] == [UID]
    STAGE.mkdir(parents=True, exist_ok=True)
    for item in ("catalogue-index.json", "source-forms.json"):
        shutil.copyfile(PREVIEW / item, STAGE / item)
    catalogue = {**preview,
                 "area": "Diocesan Girls' School original government source",
                 "loadingPolicy": "Exact unchanged source with validated two-sheet government terrain and parent masks under retained neighbours"}
    catalogue["models"] = [{**entry,
                            "placementReview": "Exact original government source identity, placement, masked terrain contact, neighbour and browser checks passed; no geometry edits."}
                           for entry in preview["models"]]
    save(STAGE / "catalogue.json", catalogue)
    for entry in preview["models"]:
        source = PREVIEW / entry["asset"]
        target = STAGE / entry["asset"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        assert sha(target) == entry["sha256"]
    patch = read(source_patch)
    staged_patch = STAGE / source_patch.name
    shutil.copyfile(source_patch, staged_patch)
    assert sha(staged_patch) == accepted["candidatePatch"]["sha256"]
    destination = "city/data/official-models/" + BATCH + "/catalogue.json"
    terrain = {"source": rel(staged_patch), "sha256": sha(staged_patch),
               "destination": "city/data/" + staged_patch.name,
               "resolution": patch["cell"],
               "area": "Diocesan Girls' School exact two-sheet source terrain with parent masks under retained neighbours"}
    save(STAGE / "plan.json", {"areas": [{"area": catalogue["area"],
                                           "catalogue": rel(STAGE / "catalogue.json"),
                                           "destination": destination}],
                               "topLevelTerrainPatches": [terrain]})
    config = read(PREVIEW / "browser-config.json")
    config.update(stage=rel(STAGE) + "/", catalogueURL=destination, terrain=[terrain])
    save(STAGE / "browser-config.json", config)
    save(DOC / "stage.json", {"batch": BATCH, "uids": [UID],
                              "catalogueSHA256": sha(STAGE / "catalogue.json"),
                              "planSHA256": sha(STAGE / "plan.json"),
                              "terrainSHA256": sha(staged_patch),
                              "previewCatalogueSHA256": sha(PREVIEW / "catalogue.json"),
                              "previewTerrainSHA256": sha(PREVIEW / source_patch.name),
                              "aiCalls": 0, "modelGeometryChanges": 0, "publication": False})
    assert sha(STAGE / preview["models"][0]["asset"]) == accepted["sourceSHA256"]
    assert sha(staged_patch) == sha(PREVIEW / source_patch.name)
    print(json.dumps({"staged": UID, "batch": BATCH,
                      "patchSHA256": sha(staged_patch)}), flush=True)


if __name__ == "__main__":
    run()
