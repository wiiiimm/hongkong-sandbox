"""Stage two unchanged XL sources with their neighbour-safe government terrain."""

import json
import shutil

from run import ROOT, HERE, read, save, digest


BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "new-two-sheet-browser-20260927"
BATCH = "government-xl-new-two-sheet-20260927"
STAGE = HERE / "accepted" / BATCH
SITES = (("landsd/91127:0", "cityplaza", "Cityplaza"),
         ("landsd/149020:0", "tin-shui-wai-station", "Tin Shui Wai Station"))


def sha(path):
    return digest(path.read_bytes())


def rel(path):
    return str(path.relative_to(ROOT))


def run():
    checks = {row["uid"]: row for row in read(BASE / "new-mask-checks-20260927.json")["rows"]}
    masks = {row["uid"]: row for row in read(BASE / "new-disjoint-neighbour-mask-eval-20260927.json")["rows"]}
    foundation = {row["uid"]: row for row in read(BASE / "new-masked-foundation-eval-20260927.json")["rows"]}
    assert set(checks) == set(masks) == set(foundation) == {uid for uid, _, _ in SITES}
    STAGE.mkdir(parents=True, exist_ok=True)
    entries, forms, terrains = [], [], []
    for uid, name, label in SITES:
        check, mask, proof = checks[uid], masks[uid], foundation[uid]
        assert (check["foundationAccepted"] and check["fullyBuriedUpwardTriangles"] == 0
                and check["fullyBuriedAreaFraction"] == 0 and check["sourcePreserved"]
                and check["mobileBudgetPassed"] and check["loaderAccepted"] == check["checksPassed"] == 1)
        assert (check["missingTerrainSamples"] == 0 and check["maxSamplerDeltaM"] <= .004
                and not check["runtimeConcerns"] and not check["blockedNativeNeighbourUids"]
                and not mask["remainingBlockedUids"])
        assert -.7 <= check["minimumLowRimGapM"] <= .1
        assert -.1 <= check["maximumLowRimGapM"] <= .1
        assert proof["strictFoundationAccepted"] and proof["sourceSHA256"]
        source = HERE / "local" / f"government-xl-{name}-terrain-20260927/candidates"
        catalogue = read(source / "catalogue.json")
        assert len(catalogue["models"]) == 1 and catalogue["models"][0]["uid"] == uid
        entry = dict(catalogue["models"][0])
        asset = STAGE / entry["asset"]
        asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / entry["asset"], asset)
        assert sha(asset) == entry["sha256"] == proof["sourceSHA256"]
        entry.update(priority="detail", proceduralWindows=False, sourceIdentityReviewed=True,
                     identityReviewApproved=True, placementReviewed=True, publicationApproved=True,
                     suppressesBuildingUids=[],
                     placementReview="Exact source identity, two-sheet terrain, full-triangle contact, neighbour and runtime checks passed; no geometry edits.")
        entries.append(entry)
        form = read(source / "source-forms.json")[uid]["building"]
        forms.append(form)
        source_patch = ROOT / mask["candidatePatch"]["path"]
        assert sha(source_patch) == mask["candidatePatch"]["sha256"]
        patch = STAGE / source_patch.name
        shutil.copyfile(source_patch, patch)
        assert sha(patch) == sha(source_patch)
        terrains.append({"source": rel(patch), "sha256": sha(patch),
                         "destination": "city/data/" + patch.name,
                         "resolution": read(patch)["cell"],
                         "area": label + " exact two-sheet government terrain with current parent under disjoint neighbours"})
    template = read(HERE / "accepted/government-xxl-20260911/catalogue.json")
    template.update(area="Cityplaza and Tin Shui Wai Station original government sources",
                    loadingPolicy="Exact original source with verified two-sheet terrain and neighbour-safe parent masks",
                    models=entries, counts={"packedModels": len(entries)})
    save(STAGE / "catalogue.json", template)
    save(STAGE / "catalogue-index.json", {"models": len(entries), "catalogues": ["catalogue.json"]})
    save(STAGE / "source-forms.json", forms)
    destination = "city/data/official-models/" + BATCH + "/catalogue.json"
    save(STAGE / "plan.json", {"areas": [{"area": template["area"],
                                           "catalogue": rel(STAGE / "catalogue.json"),
                                           "destination": destination}],
                               "topLevelTerrainPatches": terrains})
    config = {"stage": rel(STAGE) + "/", "doc": rel(DOC) + "/",
              "catalogueURL": destination, "terrain": terrains,
              "fitBox": False, "browserUids": [uid for uid, _, _ in SITES],
              "failureTestUids": [uid for uid, _, _ in SITES],
              "retainedBuildingUidsByModel": {
                  "landsd/91127:0": ["way/667262850:0", "way/667262851:0", "way/667262944:0"],
                  "landsd/149020:0": ["landsd/183109:0", "landsd/269568:0", "landsd/305543:0"]}}
    save(STAGE / "browser-config.json", config)
    save(DOC / "stage.json", {"batch": BATCH, "uids": [uid for uid, _, _ in SITES],
                              "catalogueSHA256": sha(STAGE / "catalogue.json"),
                              "planSHA256": sha(STAGE / "plan.json"),
                              "terrainSHA256s": {uid: terrain["sha256"] for (uid, _, _), terrain in zip(SITES, terrains)},
                              "sourceSHA256s": {entry["uid"]: entry["sha256"] for entry in entries},
                              "aiCalls": 0, "modelGeometryChanges": 0, "publication": False})
    print(json.dumps({"staged": [uid for uid, _, _ in SITES], "batch": BATCH}), flush=True)


if __name__ == "__main__":
    run()
