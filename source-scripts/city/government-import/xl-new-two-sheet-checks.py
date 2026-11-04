"""Run identity, runtime, and neighbour checks on three exact two-sheet XL patches."""

import importlib.util
import json
import sys
import traceback

from run import ROOT, HERE, read, save


spec = importlib.util.spec_from_file_location("xl_two_sheet_checks", HERE / "xl-yoho-mall-ii-acceptance.py")
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
OUT = BASE / "new-two-sheet-checks-20260927.json"
SITES = (("landsd/91127:0", "cityplaza"),
         ("landsd/149020:0", "tin-shui-wai-station"),
         ("landsd/293822:0", "cainiao-smart-gateway"))


def run():
    candidates = {row["uid"]: row for row in read(BASE / "new-two-sheet-patch-eval-20260927.json")["rows"]}
    rows = []
    original_args = sys.argv
    try:
        sys.argv = [__file__, "prepare"]
        for uid, name in SITES:
            if candidates[uid]["state"] != "terrain-patch-validated-awaiting-model-and-neighbour-checks":
                rows.append({"uid": uid, "state": "patch-held"})
                continue
            checks.DOC = BASE / f"{name}-terrain-diagnostic-20260927"
            checks.LOCAL = HERE / "local" / f"government-xl-{name}-terrain-20260927"
            checks.STAGE = checks.LOCAL / "candidates"
            try:
                checks.run()
                metric = read(checks.DOC / "metrics.json")["rows"][0]
                validation = read(checks.DOC / "validation.json")["results"][0]
                neighbour = read(checks.DOC / "neighbour-checks.json")
                native = read(checks.DOC / "native-neighbour-checks.json")
                row = {"uid": uid, "state": "checks-complete",
                       "identityExact": read(checks.DOC / "identity-resolution.json")["rows"][0]["exactObjectAndCSUID"],
                       "sourcePreserved": metric["sourcePreserved"],
                       "minimumLowRimGapM": metric.get("minLowGap"),
                       "maximumSamplerDeltaM": metric.get("maxSamplerDelta"),
                       "missingTerrainSamples": metric.get("missingTerrain"),
                       "runtimeConcerns": validation.get("concerns", []),
                       "blockedNeighbourUids": sorted({blocked for patch in neighbour["patches"]
                                                        for blocked in patch["blockedBy"]}),
                       "blockedNativeNeighbourUids": sorted(set(native.get("blocked", [])) -
                                                            set(native.get("resolved", []))),
                       "aiCalls": 0, "modelGeometryChanges": 0, "publication": False}
            except Exception as error:
                row = {"uid": uid, "state": "script-held", "errorType": type(error).__name__,
                       "error": str(error)[:500], "traceback": traceback.format_exc(limit=3),
                       "aiCalls": 0, "modelGeometryChanges": 0, "publication": False}
            rows.append(row)
            save(OUT, {"stage": "two-sheet-identity-runtime-neighbour-checks-v1",
                       "rows": rows, "complete": len(rows) == len(SITES),
                       "aiCalls": 0, "modelGeometryChanges": 0, "publication": False})
            print(json.dumps({"uid": uid, "state": row["state"],
                              "blocked": len(row.get("blockedNeighbourUids", [])),
                              "error": row.get("error")}), flush=True)
    finally:
        sys.argv = original_args


if __name__ == "__main__":
    run()
