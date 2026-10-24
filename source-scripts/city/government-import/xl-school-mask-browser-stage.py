"""Stage an unpublished Diocesan Girls' School mask for browser verification."""

import json
import shutil
from pathlib import Path

from run import ROOT, HERE, read, save, digest


BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "diocesan-girls-school-mask-browser-20260927"
SOURCE = BASE / "shared-neighbour-mask-eval-20260927.json"
FOUNDATION = BASE / "masked-foundation-eval-20260927.json"
LOCAL = HERE / "local/government-xl-diocesan-girls-school-terrain-20260927/candidates"
STAGE = HERE / "local/government-xl-diocesan-girls-school-browser-stage-20260927"
UID = "landsd/257352:0"


def sha(path):
    return digest(Path(path).read_bytes())


def rel(path):
    return str(Path(path).relative_to(ROOT))


def run():
    candidate = next(row for row in read(SOURCE)["rows"] if row["uid"] == UID)
    foundation = next(row for row in read(FOUNDATION)["rows"] if row["uid"] == UID)
    assert not candidate["remainingBlockedUids"] and foundation["strictFoundationAccepted"]
    original = read(LOCAL / "catalogue.json")
    assert len(original["models"]) == 1 and original["models"][0]["uid"] == UID
    STAGE.mkdir(parents=True, exist_ok=True)
    entry = dict(original["models"][0])
    asset = STAGE / entry["asset"]
    asset.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(LOCAL / entry["asset"], asset)
    assert sha(asset) == entry["sha256"]
    entry.update(priority="detail", proceduralWindows=False, sourceIdentityReviewed=True,
                 identityReviewApproved=True, placementReviewed=True, publicationApproved=True,
                 suppressesBuildingUids=[],
                 placementReview="Staged compute-only school terrain-mask evaluation; no viewer publication.")
    original.update(area="Diocesan Girls' School unpublished mask evaluation",
                    loadingPolicy="Browser evaluation only", models=[entry],
                    counts={"packedModels": 1})
    save(STAGE / "catalogue.json", original)
    save(STAGE / "catalogue-index.json", {"models": 1, "catalogues": ["catalogue.json"]})
    forms = read(LOCAL / "source-forms.json")
    save(STAGE / "source-forms.json", [forms[UID]["building"]])
    source_patch = ROOT / candidate["candidatePatch"]["path"]
    assert sha(source_patch) == candidate["candidatePatch"]["sha256"]
    patch = read(source_patch)
    staged_patch = STAGE / source_patch.name
    shutil.copyfile(source_patch, staged_patch)
    destination = "city/data/official-models/government-xl-school-mask-browser-20260927/catalogue.json"
    terrain = {"source": rel(staged_patch), "sha256": sha(staged_patch),
               "destination": "city/data/" + staged_patch.name,
               "resolution": patch["cell"],
               "area": "Diocesan Girls' School unpublished exact-source terrain mask"}
    save(STAGE / "browser-config.json", {"stage": rel(STAGE) + "/", "doc": rel(DOC) + "/",
                                         "catalogueURL": destination, "terrain": [terrain],
                                         "fitBox": False, "browserUids": [UID],
                                         "failureTestUids": [UID],
                                         "retainedBuildingUidsByModel": {
                                             UID: ["landsd/235733:0", "landsd/321006:0"]},
                                         "samplerToleranceByModel": {}})
    save(DOC / "stage.json", {"uid": UID, "candidatePatch": candidate["candidatePatch"],
                              "catalogueSHA256": sha(STAGE / "catalogue.json"),
                              "stagedPatchSHA256": sha(staged_patch),
                              "aiCalls": 0, "modelGeometryChanges": 0, "publication": False})
    print(json.dumps({"staged": UID, "catalogue": destination, "publication": False}), flush=True)


if __name__ == "__main__":
    run()
