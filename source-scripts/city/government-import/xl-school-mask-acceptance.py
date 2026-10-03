"""Accept the unchanged school source against a bounded parent-terrain mask."""

import importlib.util
import json
import shutil

from run import ROOT, HERE, read, save, digest


spec = importlib.util.spec_from_file_location("direct_school_mask", HERE / "integrate.py")
direct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(direct)

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "diocesan-girls-school-mask-browser-20260927"
SOURCE = BASE / "shared-neighbour-mask-eval-20260927.json"
FOUNDATION = BASE / "masked-foundation-eval-20260927.json"
ORIGINAL = BASE / "diocesan-girls-school-terrain-diagnostic-20260927"
EVAL = HERE / "local/government-xl-shared-mask-eval-20260927/diocesan-girls-school"
UID = "landsd/257352:0"


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def run():
    masked = next(row for row in read(SOURCE)["rows"] if row["uid"] == UID)
    foundation = next(row for row in read(FOUNDATION)["rows"] if row["uid"] == UID)
    identity = read(ORIGINAL / "identity-resolution.json")["rows"][0]
    source = read(ORIGINAL / "result.json")
    assert source["terrainSheets"] == ["11-NW-24B", "11-NW-24D"]
    assert identity["uid"] == UID and identity["exactObjectAndCSUID"]
    assert identity["targetCoverage"] >= .95 and identity["sourceExcessFraction"] <= .05
    assert identity["unrelatedIntersectingForms"] == 0
    assert not masked["remainingBlockedUids"] and masked["sourcePreserved"]
    assert masked["missingTerrainSamples"] == 0
    assert foundation["strictFoundationAccepted"] and foundation["foundation"]["fullyBuriedTriangles"] == 0
    assert foundation["foundation"]["fullyBuriedUpwardTriangles"] == 0
    assert foundation["foundation"]["completeTerrainTriangles"] == foundation["foundation"]["triangles"]
    assert -.7 <= masked["minLowRimGapM"] < 0
    assert -.1 <= masked["maxLowRimGapM"] <= .1
    assert masked["numericalProjectedOverlapM2"] <= .25
    assert masked["numericalCoverageGapM2"] <= 78.4
    for file in ("metrics.json", "neighbour-checks.json", "native-neighbour-checks.json"):
        shutil.copyfile(EVAL / file, DOC / ("final-" + file))
    metrics = read(DOC / "final-metrics.json")
    metric = metrics["rows"][0]
    assert metric["uid"] == UID and metric["sourcePreserved"]
    assert metric["maxSamplerDelta"] <= .004 and metric["missingTerrain"] == 0
    assert not metric.get("error") and not metric.get("missingDrawnTerrain", {}).get("count")
    assert all(metric["budget"][key] <= metrics["profiles"]["mobile"][key]
               for key in ("triangles", "geometryBytes", "residentBytes"))
    neighbour = read(DOC / "final-neighbour-checks.json")
    native = read(DOC / "final-native-neighbour-checks.json")
    assert not {item for patch in neighbour["patches"] for item in patch["blockedBy"]}
    assert not set(native["blocked"]) - set(native.get("resolved", []))
    validation = read(DOC / "masked-validation.json")
    assert validation["loaderAccepted"] == validation["checksPassed"] == 1
    assert validation["exceptions"] == 0
    assert validation["results"][0]["concerns"] == ["sampled-terrain-above-model-bottom"]
    browser = direct.browser_verified(DOC / "staged-browser.json", {UID})
    views = [view for view in browser["views"] if "time" in view]
    retained = {"landsd/235733:0", "landsd/321006:0"}
    assert all(set(view["retained"]) == retained and
               all(item["loaded"] and not item["hidden"] for item in view["retained"].values()) and
               abs(view["ground"] - view["groundSampler"]) <= .004
               for view in views)
    contact = {
        "uid": UID, "accepted": True,
        "coarseConcern": "sampled-terrain-above-model-bottom",
        "policy": "This source's coarse bounds warning is resolved only for this model: every original face has terrain coverage, no source triangle is fully buried, the low rim is between -0.7 and +0.1 m of terrain, the terrain sampler agrees within 4 mm, all neighbours remain valid, and staged desktop/mobile browser checks pass.",
        "minimumLowRimGapM": metric["minLowGap"], "maximumLowRimGapM": metric["maxLowGap"],
        "fullyBuriedTriangles": 0, "fullyBuriedUpwardTriangles": 0,
        "foundationEvidence": ref(FOUNDATION), "metricEvidence": ref(DOC / "final-metrics.json"),
        "validationEvidence": ref(DOC / "masked-validation.json"),
        "browserEvidence": ref(DOC / "staged-browser.json"),
        "aiCalls": 0, "modelGeometryChanges": 0,
    }
    save(DOC / "contact-resolution.json", contact)
    report = {"batch": "government-xl-diocesan-girls-school-mask-20260927",
              "uids": [UID], "passed": True, "failures": [],
              "sourceSHA256": metric["sourceSHA256"],
              "candidatePatch": masked["candidatePatch"],
              "sourceTerrainSheets": source["terrainSheets"],
              "disjointMaskEvidence": ref(BASE / "disjoint-neighbour-mask-eval-20260927.json"),
              "sharedMaskEvidence": ref(SOURCE),
              "foundationEvidence": ref(FOUNDATION),
              "identityEvidence": ref(ORIGINAL / "identity-resolution.json"),
              "contactResolutionEvidence": ref(DOC / "contact-resolution.json"),
              "metricsEvidence": ref(DOC / "final-metrics.json"),
              "neighbourEvidence": ref(DOC / "final-neighbour-checks.json"),
              "nativeNeighbourEvidence": ref(DOC / "final-native-neighbour-checks.json"),
              "validationEvidence": ref(DOC / "masked-validation.json"),
              "stagedBrowserEvidence": ref(DOC / "staged-browser.json"),
              "aiCalls": 0, "modelGeometryChanges": 0, "publication": False}
    save(DOC / "acceptance.json", report)
    print(json.dumps({"uid": UID, "passed": True, "geometryChanges": 0,
                      "lowRimM": [metric["minLowGap"], metric["maxLowGap"]]}), flush=True)


if __name__ == "__main__":
    run()
