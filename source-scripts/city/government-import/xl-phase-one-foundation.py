"""Audit every original Phase 1 source face against its complete terrain patch."""

import importlib.util
import shutil

import numpy as np
from shapely.geometry import Polygon

from run import ROOT, HERE, read, save, digest

spec = importlib.util.spec_from_file_location("xl_phase_one_foundation", HERE / "xl-final-script-pass.py")
final = importlib.util.module_from_spec(spec)
spec.loader.exec_module(final)

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DOC = BASE / "phase-one-terrain-diagnostic-20260927"
LOCAL = HERE / "local/government-xl-phase-one-terrain-20260927"
UID = "landsd/305672:0"
OUTPUT = BASE / "phase-one-foundation-20260927.json"
SELECTION = DOC / "selection.json.gz"


def run():
    row = read(SELECTION)["rows"][0]
    assert row["uid"] == UID
    entry = row["candidate"]["entry"]
    final.s.LOCAL = LOCAL
    asset = LOCAL / "assets" / (entry["sha256"] + ".glb.gz")
    asset.parent.mkdir(parents=True, exist_ok=True)
    if not asset.exists():
        shutil.copyfile(row["candidate"]["path"], asset)
    assert digest(asset.read_bytes()) == entry["sha256"]
    triangles = final.s.glb_triangles({**row["native"]["model"], "sourceSHA256": entry["sha256"],
                                       "modelId": entry["modelId"], "triangles": entry["triangles"],
                                       "native": row["native"]})
    result = read(DOC / "result.json")
    patch_path = ROOT / result["patchPath"]
    assert digest(patch_path.read_bytes()) == result["patchSHA256"]
    patch = read(patch_path)
    position = np.asarray(patch["nativeMesh"]["position"], dtype=np.float32).reshape(-1, 3)
    terrain = position[np.asarray(patch["nativeMesh"]["index"]).reshape(-1, 3)]
    building = row["source"]["building"]
    footprint = Polygon(building["rings"][0], building["rings"][1:])
    foundation = final.foundation_context(triangles, terrain, footprint)
    strict = (foundation["completeTerrainTriangles"] == foundation["triangles"]
              and foundation["fullyBuriedUpwardTriangles"] == 0
              and foundation["fullyBuriedAreaFraction"] <= .001)
    save(OUTPUT,
         {"uid": row["uid"], "sourceSHA256": entry["sha256"],
          "terrainSHA256": result["patchSHA256"], "strictFoundationAccepted": strict,
          "foundation": foundation, "aiCalls": 0, "modelGeometryChanges": 0, "publication": False})
    print({"uid": row["uid"], "strict": strict,
           "buriedUpward": foundation["fullyBuriedUpwardTriangles"],
           "buriedFraction": foundation["fullyBuriedAreaFraction"]}, flush=True)


if __name__ == "__main__":
    run()
