"""Run exact source, runtime, and neighbour gates on China Merchants Tower East."""

import importlib.util
import json
import sys

from run import ROOT, HERE, read, save

spec = importlib.util.spec_from_file_location("xl_china_checks", HERE / "xl-yoho-mall-ii-acceptance.py")
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)

DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/china-merchants-tower-east-terrain-diagnostic-20260927"
LOCAL = HERE / "local/government-xl-china-merchants-tower-east-terrain-20260927"


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
    result = {"uid": "landsd/264206:0", "sourcePreserved": metric["sourcePreserved"],
              "missingTerrainSamples": metric["missingTerrain"],
              "minLowGapM": metric["minLowGap"], "maxLowGapM": metric["maxLowGap"],
              "maxSamplerDeltaM": metric["maxSamplerDelta"],
              "runtimeConcerns": validation.get("concerns", []),
              "blockedNeighbourUids": sorted({uid for row in neighbour["patches"] for uid in row["blockedBy"]}),
              "blockedNativeNeighbourUids": sorted(set(native.get("blocked", [])) - set(native.get("resolved", []))),
              "aiCalls": 0, "modelGeometryChanges": 0, "publication": False}
    save(DOC / "checks.json", result)
    print(json.dumps(result), flush=True)
