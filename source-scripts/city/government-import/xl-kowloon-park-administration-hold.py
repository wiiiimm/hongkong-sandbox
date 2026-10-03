"""Preserve exact Kowloon Park identity, neighbour and contact blockers."""

from run import ROOT, read, save, digest

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "kowloon-park-administration-terrain-diagnostic-20260927"
UID = "landsd/336430:0"


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def run():
    identity = read(DOC / "identity-resolution.json")["rows"][0]
    checks = read(DOC / "checks.json")
    foundation = read(DOC / "foundation.json")
    source = foundation["foundation"]
    assert identity["uid"] == UID and not identity["identityAccepted"]
    assert identity["unrelatedIntersectingForms"] == 4
    assert checks["sourcePreserved"] and checks["missingTerrainSamples"] == 0
    assert checks["blockedNeighbourUids"] == ["way/725945983:0"]
    assert not foundation["strictFoundationAccepted"] and source["fullyBuriedUpwardTriangles"] > 0
    result = {"uid": UID, "humanStatus": "held-unknown", "primaryHold": "terrain-contact",
              "detailedHold": "source-overlaps-neighbours-and-buried-original-base",
              "unrelatedIntersectingForms": identity["unrelatedIntersectingForms"],
              "unrelatedOverlapAreaM2": identity["unrelatedAreaM2"],
              "blockedNeighbourUids": checks["blockedNeighbourUids"],
              "fullyBuriedUpwardTriangles": source["fullyBuriedUpwardTriangles"],
              "fullyBuriedUpwardAreaM2": source["fullyBuriedUpwardAreaM2"],
              "fullyBuriedAreaFraction": source["fullyBuriedAreaFraction"],
              "minimumSourceGroundGapM": source["minimumGapM"],
              "nextWork": "Compute exact source-component boundaries for the four intersecting forms and preserve the blocked neighbour. Resolve the original base against government terrain, then rerun identity, foundation, neighbour, runtime and browser checks without editing geometry.",
              "requiresAI": False, "requiresHuman": False, "aiCalls": 0,
              "modelGeometryChanges": 0, "publication": False,
              "evidence": [ref(DOC / name) for name in
                           ("identity-resolution.json", "result.json", "checks.json", "foundation.json")]}
    save(DOC / "held.json", result)
    return result


if __name__ == "__main__":
    result = run()
    print({"uid": UID, "held": result["detailedHold"],
           "buriedUpwardTriangles": result["fullyBuriedUpwardTriangles"]}, flush=True)
