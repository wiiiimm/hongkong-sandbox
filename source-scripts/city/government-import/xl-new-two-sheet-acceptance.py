"""Accept two unchanged XL sources only after exact staged browser verification."""

import importlib.util
import json
import shutil

from run import ROOT, HERE, read, save, digest


spec = importlib.util.spec_from_file_location("direct_new_two_sheet", HERE / "integrate.py")
direct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(direct)

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "new-two-sheet-browser-20260927"
STAGE = HERE / "accepted/government-xl-new-two-sheet-20260927"
SITES = (("landsd/91127:0", "cityplaza"),
         ("landsd/149020:0", "tin-shui-wai-station"))


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def run():
    stage = read(DOC / "stage.json")
    assert stage["uids"] == [uid for uid, _ in SITES]
    assert stage["catalogueSHA256"] == ref(STAGE / "catalogue.json")["sha256"]
    assert stage["planSHA256"] == ref(STAGE / "plan.json")["sha256"]
    catalogue = {row["uid"]: row for row in read(STAGE / "catalogue.json")["models"]}
    checks = {row["uid"]: row for row in read(BASE / "new-mask-checks-20260927.json")["rows"]}
    masks = {row["uid"]: row for row in read(BASE / "new-disjoint-neighbour-mask-eval-20260927.json")["rows"]}
    foundation = {row["uid"]: row for row in read(BASE / "new-masked-foundation-eval-20260927.json")["rows"]}
    browser = direct.browser_verified(DOC / "staged-browser.json", set(stage["uids"]))
    assert not browser["errors"]
    views = [view for view in browser["views"] if "time" in view]
    assert len(views) == 4 * len(SITES)
    for view in views:
        assert all(item["loaded"] and not item["hidden"] for item in view["retained"].values())
        assert abs(view["ground"] - view["groundSampler"]) <= .004
    models, evidence = [], {}
    for uid, name in SITES:
        check, mask, proof, model = checks[uid], masks[uid], foundation[uid], catalogue[uid]
        assert proof["strictFoundationAccepted"] and proof["foundation"]["fullyBuriedUpwardTriangles"] == 0
        assert proof["foundation"]["fullyBuriedAreaFraction"] == 0
        assert check["sourcePreserved"] and check["mobileBudgetPassed"]
        assert check["loaderAccepted"] == check["checksPassed"] == 1
        assert check["missingTerrainSamples"] == 0 and check["maxSamplerDeltaM"] <= .004
        assert not check["runtimeConcerns"] and not check["blockedNativeNeighbourUids"]
        assert not mask["remainingBlockedUids"]
        assert -.7 <= check["minimumLowRimGapM"] <= .1
        assert -.1 <= check["maximumLowRimGapM"] <= .1
        assert stage["sourceSHA256s"][uid] == proof["sourceSHA256"] == model["sha256"]
        assert digest((STAGE / model["asset"]).read_bytes()) == model["sha256"]
        assert stage["terrainSHA256s"][uid] == mask["candidatePatch"]["sha256"]
        assert uid in {view["uid"] for view in views}
        source_doc = BASE / f"{name}-terrain-diagnostic-20260927"
        source_local = HERE / "local/government-xl-new-disjoint-mask-eval-20260927" / name
        for label, path in (("identity", source_doc / "identity-resolution.json"),
                            ("metrics", source_local / "metrics.json"),
                            ("validation", source_local / "validation.json"),
                            ("neighbour", source_local / "neighbour-checks.json"),
                            ("nativeNeighbour", source_local / "native-neighbour-checks.json")):
            target = DOC / f"{name}-{label}.json"
            shutil.copyfile(path, target)
            evidence[f"{name}-{label}"] = ref(target)
        if name == "cityplaza":
            overlap = mask["sourceOverlapEvidence"]
            assert overlap and ref(ROOT / overlap["path"]) == overlap
            assert mask["numericalProjectedOverlapM2"] < mask["originalProjectedOverlapM2"]
            assert mask["parentSourceOverlapM2"] <= .25
            evidence[f"{name}-sourceOverlap"] = overlap
        models.append({"uid": uid, "name": name, "sourceSHA256": model["sha256"],
                       "terrainSHA256": mask["candidatePatch"]["sha256"],
                       "minimumLowRimGapM": check["minimumLowRimGapM"],
                       "maximumLowRimGapM": check["maximumLowRimGapM"],
                       "fullyBuriedUpwardTriangles": 0,
                       "blockedNeighbours": 0, "modelGeometryChanges": 0})
    evidence.update(stage=ref(DOC / "stage.json"), browser=ref(DOC / "staged-browser.json"),
                    foundation=ref(BASE / "new-masked-foundation-eval-20260927.json"),
                    masks=ref(BASE / "new-disjoint-neighbour-mask-eval-20260927.json"),
                    checks=ref(BASE / "new-mask-checks-20260927.json"),
                    sourceRecovery=ref(BASE / "adjacent-sheet-recovery-20260927.json"),
                    sourceCoverage=ref(BASE / "cached-adjacent-sheet-survey-20260927.json"))
    save(DOC / "acceptance.json", {"batch": stage["batch"], "uids": stage["uids"],
                                   "passed": True, "failures": [], "models": models,
                                   "evidence": evidence, "aiCalls": 0,
                                   "modelGeometryChanges": 0, "publication": False})
    print(json.dumps({"accepted": stage["uids"], "browserViews": len(views),
                      "aiCalls": 0}), flush=True)


if __name__ == "__main__":
    run()
