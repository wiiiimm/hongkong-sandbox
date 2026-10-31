"""Find unchanged solid podiums under ground-gap-only XL source models."""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from shapely.geometry import MultiPoint

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run import ROOT, HERE, read, save, digest

spec = importlib.util.spec_from_file_location("xl_context", HERE / "xl-final-script-pass.py")
context = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context)
context.s.LOCAL = HERE / "local/government-xl-remaining-20260923/recovered"

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"


def run():
    source = {row["uid"]: row for row in read(BASE / "selection.json.gz")["rows"]}
    results = {row["uid"]: row for row in read(BASE / "results.json.gz")["rows"]}
    identity = {row["uid"]: row["identity"] for row in read(BASE / "context.json")["rows"]}
    manifest = read(ROOT / "3d-viewer/city/data/manifest.json")
    installed = {model["uid"] for url in manifest["officialModelCatalogues"]
                 for model in read(ROOT / "3d-viewer" / url)["models"]}
    rows = []
    for uid, result in results.items():
        if uid not in identity or set(result["reasons"]) - {
                "ground-contact-unresolved", "sampled-ground-gap-below-model-bottom",
                "sampled-terrain-above-model-bottom"}:
            continue
        if "ground-contact-unresolved" not in result["reasons"]:
            continue
        proof = identity[uid]
        if not proof["exactObjectAndCSUID"] or proof["targetCoveredBySourceProjection"] < .95:
            continue
        triangles = context.s.glb_triangles(source[uid])
        minimum = float(triangles[:, :, 1].min())
        low = triangles[np.any(triangles[:, :, 1] <= minimum + .35, axis=1)]
        hull = MultiPoint(low[:, :, [0, 2]].reshape(-1, 2)).convex_hull
        lo, hi = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
        forms = context.load_forms([lo[0] - 2, lo[2] - 2, hi[0] + 2, hi[2] + 2])
        target = next(polygon for building, polygon, _ in forms if building["uid"] == uid)
        candidates = []
        for building, polygon, _ in forms:
            support_uid = building["uid"]
            if support_uid == uid or support_uid in installed or building.get("modelGeometry"):
                continue
            if building.get("structureType") == "Open-sided Structure":
                continue
            top = building["base"] + building["height"]
            margin = top - minimum
            if not -.1 <= margin <= 5:
                continue
            low_coverage = polygon.intersection(hull).area / hull.area if hull.area else 0
            target_coverage = polygon.intersection(target).area / target.area
            if low_coverage >= .97 and target_coverage >= .8:
                candidates.append({"uid": support_uid, "name": building.get("name"),
                                   "sourceMinimumY": minimum, "supportTopY": top,
                                   "verticalMarginM": margin, "lowRimHullCoverage": low_coverage,
                                   "targetFootprintCoverage": target_coverage})
        rows.append({"uid": uid, "name": result.get("name"), "sourceSHA256": source[uid]["sourceSHA256"],
                     "lowRimTriangles": len(low), "candidates": candidates,
                     "passed": len(candidates) == 1,
                     "reason": "unique-unchanged-solid-support" if len(candidates) == 1 else
                               "no-unique-supported-podium"})
        print(json.dumps({"uid": uid, "candidates": len(candidates)}), flush=True)
    report = {"policy": "same unchanged-podium low-rim and target-coverage gates as prior XL supported towers",
              "sourceSHA256": digest((BASE / "selection.json.gz").read_bytes()),
              "resultsSHA256": digest((BASE / "results.json.gz").read_bytes()),
              "rows": rows, "passed": sum(row["passed"] for row in rows),
              "aiCalls": 0, "geometryChanges": 0, "publication": False}
    save(BASE / "support-probe.json", report)
    print(json.dumps({"tested": len(rows), "passed": report["passed"]}), flush=True)


if __name__ == "__main__":
    run()
