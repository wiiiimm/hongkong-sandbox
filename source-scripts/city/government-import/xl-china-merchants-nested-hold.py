"""Preserve the exact compute-only blocker for China Merchants Tower East."""

from run import ROOT, HERE, read, save, digest

DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/china-merchants-tower-east-terrain-diagnostic-20260927"


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def run():
    uid = "landsd/264206:0"
    identity = read(DOC / "identity-resolution.json")["rows"][0]
    checks = read(DOC / "checks.json")
    foundation = read(DOC / "foundation.json")
    source = foundation["foundation"]
    assert identity["exactObjectAndCSUID"]
    assert checks["sourcePreserved"] and checks["missingTerrainSamples"] == 0
    assert not checks["blockedNeighbourUids"] and not checks["blockedNativeNeighbourUids"]
    assert not foundation["strictFoundationAccepted"]
    assert source["fullyBuriedUpwardTriangles"] > 0
    result = {"uid": uid, "humanStatus": "held-unknown", "primaryHold": "terrain-contact",
              "detailedHold": "original-source-base-buried-in-nested-terrain",
              "fullyBuriedUpwardTriangles": source["fullyBuriedUpwardTriangles"],
              "fullyBuriedUpwardAreaM2": source["fullyBuriedUpwardAreaM2"],
              "fullyBuriedAreaFraction": source["fullyBuriedAreaFraction"],
              "minimumSourceGroundGapM": source["minimumGapM"],
              "maxSamplerDeltaM": checks["maxSamplerDeltaM"],
              "nextWork": "Use scripts to examine original government source components and nested parent terrain at the 102 buried upward faces. Resolve terrain contact without geometry edits; then rerun foundation, installed-neighbour, runtime and browser checks.",
              "requiresAI": False, "requiresHuman": False, "aiCalls": 0,
              "modelGeometryChanges": 0, "publication": False,
              "evidence": [ref(DOC / name) for name in
                           ("identity-resolution.json", "result.json", "checks.json", "foundation.json")]}
    save(DOC / "held.json", result)
    return result


if __name__ == "__main__":
    result = run()
    print({"uid": result["uid"], "held": result["detailedHold"],
           "buriedUpwardTriangles": result["fullyBuriedUpwardTriangles"]}, flush=True)
