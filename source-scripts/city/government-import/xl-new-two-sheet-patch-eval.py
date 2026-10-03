"""Evaluate exact two-sheet terrain patches for three source-complete XL holds."""

import importlib.util
import json
import traceback

from run import ROOT, HERE, read, save, digest


spec = importlib.util.spec_from_file_location("xl_school_patch_template", HERE / "xl-diocesan-girls-school-terrain-diagnostic.py")
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
OUT = BASE / "new-two-sheet-patch-eval-20260927.json"
SITES = (
    ("landsd/91127:0", "cityplaza", "11-SE-7B", "11-SE-8A"),
    ("landsd/149020:0", "tin-shui-wai-station", "6-NW-8A", "6-NW-8C"),
    ("landsd/293822:0", "cainiao-smart-gateway", "9-SE-3C", "9-SE-2D"),
)


def run():
    survey = {row["uid"]: row for row in read(BASE / "cached-adjacent-sheet-survey-20260927.json")["rows"]}
    previous = {row["uid"]: row for row in read(OUT)["rows"]} if OUT.exists() else {}
    rows = []
    for uid, name, primary, adjacent in SITES:
        assert survey[uid]["routing"] == "cached-sheets-complete"
        assert survey[uid]["primarySheet"] == primary
        assert [row["sheet"] for row in survey[uid]["candidateSheets"]] == [adjacent]
        prior = previous.get(uid)
        if (prior and prior["state"] == "terrain-patch-validated-awaiting-model-and-neighbour-checks"
                and digest((ROOT / prior["patchPath"]).read_bytes()) == prior["patchSHA256"]):
            rows.append(prior)
            continue
        patch.UID = uid
        patch.SHEET = primary
        patch.TERRAIN_SHEETS = (primary, adjacent)
        patch.LOW_TERRAIN_POLICY = "omit-peripheral-below-clamp" if name == "cainiao-smart-gateway" else "reject"
        patch.DOC = BASE / f"{name}-terrain-diagnostic-20260927"
        patch.LOCAL = HERE / "local" / f"government-xl-{name}-terrain-20260927"
        try:
            patch.run()
            result = read(patch.DOC / "result.json")
            row = {"uid": uid, "state": result["state"], "terrainSheets": list(patch.TERRAIN_SHEETS),
                   "patchPath": result["patchPath"], "patchSHA256": result["patchSHA256"]}
        except Exception as error:
            row = {"uid": uid, "state": "script-held", "errorType": type(error).__name__,
                   "error": str(error)[:500], "traceback": traceback.format_exc(limit=3),
                   "terrainSheets": list(patch.TERRAIN_SHEETS)}
        rows.append(row)
        save(OUT, {"stage": "two-sheet-terrain-patch-evaluation-v1", "rows": rows,
                   "complete": len(rows) == len(SITES), "aiCalls": 0,
                   "modelGeometryChanges": 0, "publication": False})
        print(json.dumps({"uid": uid, "state": row["state"],
                          "error": row.get("error")}), flush=True)


if __name__ == "__main__":
    run()
