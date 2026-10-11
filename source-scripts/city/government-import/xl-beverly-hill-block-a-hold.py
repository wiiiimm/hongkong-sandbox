"""Preserve recovered support and remaining deterministic Block A blockers."""

from shapely.geometry import MultiPoint, Polygon

from run import ROOT, read, save, digest

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "beverly-hill-block-a-terrain-diagnostic-20260927"
UID = "landsd/255539:0"
SUPPORT = "landsd/233218:0"


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def run():
    checks = read(DOC / "checks.json")
    foundation = read(DOC / "foundation.json")
    support = read(DOC / "support-foundation.json")
    probe = read(BASE / "beverly-hill-source-support-probe-20260927.json")
    row = read(DOC / "selection.json.gz")["rows"][0]
    footprint = Polygon(row["source"]["building"]["rings"][0], row["source"]["building"]["rings"][1:])
    contact = MultiPoint([(x, z) for x, _, z in probe["contactPositions"]]).convex_hull
    coverage = contact.intersection(footprint).area / footprint.area
    assert probe["uid"] == UID and probe["supportUid"] == SUPPORT
    assert probe["within05"] == probe["interfaceSamples"] == 50 and coverage >= .99
    assert foundation["strictFoundationAccepted"] and not support["strictFoundationAccepted"]
    assert checks["blockedNeighbourUids"] and checks["blockedNativeNeighbourUids"]
    result = {"uid": UID, "supportUid": SUPPORT, "humanStatus": "held-unknown",
              "primaryHold": "terrain-contact",
              "detailedHold": "exact-government-support-found-but-podium-terrain-and-neighbours-unresolved",
              "supportSHA256": probe["supportSHA256"],
              "sourceInterfaceVertices": probe["interfaceSamples"],
              "sourceVerticesWithinHalfMetreOfSupport": probe["within05"],
              "maximumSourceSupportDistanceM": probe["maximumDistance"],
              "contactHullTargetCoverage": coverage,
              "podiumBuriedUpwardTriangles": support["foundation"]["fullyBuriedUpwardTriangles"],
              "podiumBuriedAreaFraction": support["foundation"]["fullyBuriedAreaFraction"],
              "blockedNeighbourUids": checks["blockedNeighbourUids"],
              "blockedNativeNeighbourUids": checks["blockedNativeNeighbourUids"],
              "nextWork": "Use source-preserving terrain masking to expose the recovered original Beverly Hill podium without burying upward faces or disrupting Block K and the native neighbour. Then validate the podium and Block A together through identity, foundation, runtime, neighbour and browser gates.",
              "requiresAI": False, "requiresHuman": False, "aiCalls": 0,
              "modelGeometryChanges": 0, "publication": False,
              "evidence": [ref(path) for path in
                           (BASE / "beverly-hill-podium-source-recovery-20260927.json",
                            BASE / "beverly-hill-source-support-probe-20260927.json",
                            DOC / "result.json", DOC / "identity-resolution.json",
                            DOC / "checks.json", DOC / "foundation.json",
                            DOC / "support-foundation.json") ]}
    save(DOC / "held.json", result)
    return result


if __name__ == "__main__":
    result = run()
    print({"uid": UID, "supportUid": SUPPORT,
           "contactHullTargetCoverage": result["contactHullTargetCoverage"],
           "podiumBuriedUpwardTriangles": result["podiumBuriedUpwardTriangles"]}, flush=True)
