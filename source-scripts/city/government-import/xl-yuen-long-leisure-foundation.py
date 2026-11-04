"""Audit every unchanged Yuen Long Leisure source triangle against its original government TIN."""

import importlib.util
import json
from pathlib import Path

import numpy as np
from shapely.geometry import Polygon

from run import ROOT, HERE, read, save

spec = importlib.util.spec_from_file_location("xl_final_ching", HERE / "xl-final-script-pass.py")
final = importlib.util.module_from_spec(spec)
spec.loader.exec_module(final)

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "yuen-long-leisure-terrain-diagnostic-20260925"
SOURCE = HERE / "local/government-xl-terrain-sources-20260924/sheets/6-NW-14B/terrain"


def run():
    selection = read(DOC / "selection.json.gz")["rows"]
    assert len(selection) == 1
    terrain = np.concatenate([final.s.terrain_triangles(path) for path in SOURCE.rglob("*.gltf")])
    metrics = {row["uid"]: row for row in read(DOC / "metrics.json")["rows"]}
    rows = []
    for row in selection:
        uid = row["uid"]
        triangles = final.s.glb_triangles({**row["native"]["model"],
                                           "sourceSHA256": row["candidate"]["entry"]["sha256"],
                                           "modelId": row["candidate"]["entry"]["modelId"],
                                           "triangles": row["candidate"]["entry"]["triangles"],
                                           "native": row["native"]})
        building = row["source"]["building"]
        polygon = Polygon(building["rings"][0], building["rings"][1:])
        proof = final.foundation_context(triangles, terrain, polygon)
        strict = (proof["completeTerrainTriangles"] == proof["triangles"]
                  and proof["fullyBuriedUpwardTriangles"] == 0
                  and proof["fullyBuriedAreaFraction"] <= .001)
        rows.append({"uid": uid, "sourceSHA256": row["candidate"]["entry"]["sha256"],
                     "minimumRenderedGapM": metrics[uid]["minSurfaceGap"],
                     "strictFoundationAccepted": strict, "foundation": proof})
        print(json.dumps({"uid": uid, "strict": strict,
                          "buriedFraction": proof["fullyBuriedAreaFraction"],
                          "buriedUpward": proof["fullyBuriedUpwardTriangles"]}), flush=True)
    save(DOC / "foundation.json", {"rows": rows, "aiCalls": 0, "modelGeometryChanges": 0,
                                    "qualification": "Complete native triangle sampling uses original model and terrain; deeper contact requires a separately justified bounded foundation exception."})


if __name__ == "__main__":
    run()
