"""Exhaustively audit unchanged XL source faces against shared-mask candidates."""

import importlib.util
import json

import numpy as np
from shapely.geometry import Polygon

from run import ROOT, HERE, read, save, digest


spec = importlib.util.spec_from_file_location("xl_final_mask_eval", HERE / "xl-final-script-pass.py")
final = importlib.util.module_from_spec(spec)
spec.loader.exec_module(final)

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DIAGNOSTIC_DIRS = {}
SOURCE = BASE / "shared-neighbour-mask-eval-20260927.json"
OUT = BASE / "masked-foundation-eval-20260927.json"


def run():
    results = []
    for candidate in read(SOURCE)["rows"]:
        uid, name = candidate["uid"], candidate["site"]
        doc = DIAGNOSTIC_DIRS.get(name, BASE / f"{name}-terrain-diagnostic-20260927")
        selection = read(doc / "selection.json.gz")["rows"]
        assert len(selection) == 1 and selection[0]["uid"] == uid
        row = selection[0]
        triangles = final.s.glb_triangles({**row["native"]["model"],
                                           "sourceSHA256": row["candidate"]["entry"]["sha256"],
                                           "modelId": row["candidate"]["entry"]["modelId"],
                                           "triangles": row["candidate"]["entry"]["triangles"],
                                           "native": row["native"]})
        path = ROOT / candidate["candidatePatch"]["path"]
        assert digest(path.read_bytes()) == candidate["candidatePatch"]["sha256"]
        patch = read(path)
        position = np.asarray(patch["nativeMesh"]["position"], dtype=np.float32).reshape(-1, 3)
        terrain = position[np.asarray(patch["nativeMesh"]["index"]).reshape(-1, 3)]
        building = row["source"]["building"]
        footprint = Polygon(building["rings"][0], building["rings"][1:])
        proof = final.foundation_context(triangles, terrain, footprint)
        strict = (proof["completeTerrainTriangles"] == proof["triangles"]
                  and proof["fullyBuriedUpwardTriangles"] == 0
                  and proof["fullyBuriedAreaFraction"] <= .001)
        result = {"uid": uid, "candidatePatch": candidate["candidatePatch"],
                  "sourceSHA256": row["candidate"]["entry"]["sha256"],
                  "strictFoundationAccepted": strict, "foundation": proof,
                  "aiCalls": 0, "modelGeometryChanges": 0, "publication": False}
        results.append(result)
        print(json.dumps({"uid": uid, "strict": strict,
                          "buriedFraction": proof["fullyBuriedAreaFraction"],
                          "buriedUpwardTriangles": proof["fullyBuriedUpwardTriangles"]}), flush=True)
        save(OUT, {"stage": "shared-mask-full-triangle-audit-v1", "rows": results,
                   "aiCalls": 0, "modelGeometryChanges": 0, "publication": False})


if __name__ == "__main__":
    run()
