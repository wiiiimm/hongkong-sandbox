"""Accept Cainiao's unchanged support-first pair only after staged browser checks."""

import importlib.util
import json
import shutil

from run import ROOT, HERE, read, save, digest

spec = importlib.util.spec_from_file_location("direct_cainiao_pair", HERE / "integrate.py")
direct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(direct)

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "cainiao-pair-browser-20260927"
STAGE = HERE / "accepted/government-xl-cainiao-pair-20260927"
LOCAL = HERE / "local/government-xl-cainiao-pair-checks-20260927"
PODIUM = "landsd/327178:0"
TOWER = "landsd/293822:0"


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def run():
    stage = read(DOC / "stage.json")
    assert stage["uids"] == [PODIUM, TOWER]
    assert stage["catalogueSHA256"] == ref(STAGE / "catalogue.json")["sha256"]
    assert stage["planSHA256"] == ref(STAGE / "plan.json")["sha256"]
    catalogue = {row["uid"]: row for row in read(STAGE / "catalogue.json")["models"]}
    assert set(catalogue) == {PODIUM, TOWER}
    assert catalogue[TOWER]["supportDependencies"] == [{"uid": PODIUM, "state": "candidate",
        "csuid": catalogue[PODIUM]["buildingCSUID"], "sha256": catalogue[PODIUM]["sha256"]}]
    for uid in (PODIUM, TOWER):
        model = catalogue[uid]
        assert stage["sourceSHA256s"][uid] == ref(STAGE / model["asset"])["sha256"]
        assert model["sourceIdentityReviewed"] and model["identityReviewApproved"]
        assert model["placementReviewed"] and model["publicationApproved"]
    plan = read(STAGE / "plan.json")
    assert len(plan["topLevelTerrainPatches"]) == 1
    patch = plan["topLevelTerrainPatches"][0]
    assert stage["terrainSHA256"] == ref(ROOT / patch["source"])["sha256"]
    support = read(BASE / "cainiao-source-support-proof-20260927.json")
    assert support["passed"] and support["within05"] >= 100 and support["contactHullTargetCoverage"] >= .85
    foundation = {row["uid"]: row for row in read(BASE / "cainiao-pair-foundation-20260927.json")["rows"]}
    assert all(foundation[uid]["strictFoundationAccepted"] and foundation[uid]["foundation"]["fullyBuriedUpwardTriangles"] == 0
               for uid in (PODIUM, TOWER))
    metrics = read(LOCAL / "metrics.json")
    assert {row["uid"] for row in metrics["rows"]} == {PODIUM, TOWER}
    assert all(row["sourcePreserved"] and row["missingTerrain"] == 0 and row["maxSamplerDelta"] <= .004
               for row in metrics["rows"])
    validation = read(LOCAL / "validation.json")
    assert validation["loaderAccepted"] == validation["checksPassed"] == 2
    assert {row["uid"]: row["concerns"] for row in validation["results"]} == {
        PODIUM: [], TOWER: ["sampled-ground-gap-below-model-bottom"]}
    assert not read(LOCAL / "neighbour-checks.json")["patches"][0]["blockedBy"]
    assert not read(LOCAL / "native-neighbour-checks.json")["blocked"]
    browser = direct.browser_verified(DOC / "staged-browser.json", {PODIUM, TOWER})
    assert not browser["errors"]
    views = [view for view in browser["views"] if "time" in view]
    assert len(views) == 8 and {view["uid"] for view in views} == {PODIUM, TOWER}
    assert all(abs(view["ground"] - view["groundSampler"]) <= .004 for view in views)
    assert all(all(item["loaded"] and not item["hidden"] for item in view["retained"].values()) for view in views)
    evidence = {}
    for name in ("metrics", "validation", "neighbour-checks", "native-neighbour-checks"):
        target = DOC / (name + ".json")
        shutil.copyfile(LOCAL / (name + ".json"), target)
        evidence[name] = ref(target)
    for name, path in (("stage", DOC / "stage.json"), ("browser", DOC / "staged-browser.json"),
                       ("support", BASE / "cainiao-source-support-proof-20260927.json"),
                       ("foundation", BASE / "cainiao-pair-foundation-20260927.json"),
                       ("podiumSource", BASE / "cainiao-podium-source-recovery-20260927.json"),
                       ("towerSource", BASE / "cainiao-smart-gateway-terrain-diagnostic-20260927/identity-resolution.json"),
                       ("terrainMask", BASE / "cainiao-shared-mask-eval-20260927.json")):
        evidence[name] = ref(path)
    save(DOC / "acceptance.json", {"batch": stage["batch"], "uids": stage["uids"],
                                   "passed": True, "failures": [], "models": [
                                       {"uid": uid, "sourceSHA256": catalogue[uid]["sha256"],
                                        "terrainSHA256": patch["sha256"],
                                        "fullyBuriedUpwardTriangles": 0, "blockedNeighbours": 0}
                                       for uid in (PODIUM, TOWER)],
                                   "evidence": evidence, "aiCalls": 0,
                                   "modelGeometryChanges": 0, "publication": False})
    print(json.dumps({"accepted": stage["uids"], "browserViews": len(views),
                      "contactCoverage": support["contactHullTargetCoverage"], "aiCalls": 0}), flush=True)


if __name__ == "__main__":
    run()
