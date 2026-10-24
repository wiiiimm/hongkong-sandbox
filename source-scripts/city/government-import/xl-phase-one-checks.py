"""Run original-source runtime and neighbour gates for the Phase 1 XL patch."""

import importlib.util
import sys

from run import ROOT, HERE, read, save

spec = importlib.util.spec_from_file_location("xl_phase_one_checks", HERE / "xl-yoho-mall-ii-acceptance.py")
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "phase-one-terrain-diagnostic-20260927"
LOCAL = HERE / "local/government-xl-phase-one-terrain-20260927"


if __name__ == "__main__":
    checks.DOC = DOC
    checks.LOCAL = LOCAL
    checks.STAGE = LOCAL / "candidates"
    sys.argv = [__file__, "prepare"]
    checks.run()
    metric = read(DOC / "metrics.json")["rows"][0]
    validation = read(DOC / "validation.json")["results"][0]
    neighbour = read(DOC / "neighbour-checks.json")
    native = read(DOC / "native-neighbour-checks.json")
    save(BASE / "phase-one-checks-20260927.json",
         {"uid": "landsd/305672:0", "sourcePreserved": metric["sourcePreserved"],
          "missingTerrainSamples": metric["missingTerrain"],
          "minLowGapM": metric["minLowGap"], "maxLowGapM": metric["maxLowGap"],
          "maxSamplerDeltaM": metric["maxSamplerDelta"],
          "runtimeConcerns": validation.get("concerns", []),
          "blockedNeighbourUids": sorted({uid for row in neighbour["patches"] for uid in row["blockedBy"]}),
          "blockedNativeNeighbourUids": sorted(set(native.get("blocked", [])) - set(native.get("resolved", []))),
          "aiCalls": 0, "modelGeometryChanges": 0, "publication": False})
