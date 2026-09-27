"""Recover Cainiao's original podium from the pinned 9-SE-3C archive."""

import json
import sys
import zipfile
from pathlib import Path

from shapely.geometry import MultiPoint, Polygon

from run import ROOT, HERE, read, save, digest

sys.path.insert(0, str(HERE.parent / "citywide-native"))
from download import acquire
from convert import _convert_one

SHEET = "9-SE-3C"
UID = "landsd/327178:0"
MODEL = "B106321714602063C0"
SOURCE = HERE / "local/government-xl-remaining-held-20260923/recovered/sheets" / SHEET
LOCAL = HERE / "local/government-xl-cainiao-podium-20260927"
DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"


def run():
    directory = read(SOURCE / "directory/result.json")
    assert directory["directorySHA256"] == "f4f83580314b2999cd30237f7634dfa229cf91297271822c0cbdf8abfb2c74dd"
    models = {row["modelId"]: row for row in directory["models"]}
    directory["models"] = [models[MODEL]]
    out = LOCAL / "source"
    acquired = acquire(directory, SOURCE / "directory/zip-directory.bin", out / "original")
    (out / "packed").mkdir(parents=True, exist_ok=True)
    tile = ROOT / "3d-viewer/city/data/tiles/-12_-1.json"
    raw = tile.read_bytes()
    building = next(row for row in json.loads(raw)["buildings"] if row["uid"] == UID)
    assert building["buildingCSUID"] == "1063217146P20231102"
    with zipfile.ZipFile(out / "original" / (SHEET + ".zip")) as archive:
        name = "BUILDING/" + MODEL + "/" + MODEL + ".gltf"
        converted = _convert_one(archive, archive.getinfo(name), out / "decoded", out / "packed", {}, {"modelId": MODEL})
    footprint = Polygon(building["rings"][0], building["rings"][1:])
    hull = MultiPoint([(x, z) for x, _, z in converted["terrainSamples"]["position"]]).convex_hull
    overlap = hull.intersection(footprint).area / min(hull.area, footprint.area)
    entry = {**converted["asset"], "uid": UID, "modelId": MODEL,
             "objectId": building["objectId"], "buildingCSUID": building["buildingCSUID"],
             "label": "Cainiao Smart Gateway podium", "recordedBaseHeight": building["baseHeightHKPD"],
             "recordedTopHeight": building["topHeightHKPD"], "worldBounds": converted["worldBounds"],
             "triangles": converted["triangles"], "footprintCentroidDistanceMetres": hull.centroid.distance(footprint.centroid),
             "overlapOfSmallerFootprint": overlap, "placementReviewed": False, "priority": "unreviewed",
             "publicationApproved": False, "rootTranslation": [-834500, 0, 816500], "sourceTile": SHEET}
    asset = out / "packed" / entry["asset"]
    assert digest(asset.read_bytes()) == entry["sha256"]
    row = {"uid": UID, "source": {"building": building, "tile": "city/data/tiles/-12_-1.json",
                                     "tileSHA256": digest(raw)},
           "candidate": {"path": str(asset), "entry": entry},
           "native": {"sheet": SHEET, "model": converted, "directPinnedRecovery": True}}
    save(LOCAL / "support-runtime.json.gz", {"rows": [row], "aiCalls": 0, "modelGeometryChanges": 0})
    save(DOC / "cainiao-podium-source-recovery-20260927.json",
         {"sheet": SHEET, "directorySHA256": directory["directorySHA256"], "sourceETag": directory["etag"],
          "uid": UID, "modelId": MODEL, "sourceSHA256": entry["sha256"],
          "triangles": entry["triangles"], "overlapOfSmallerFootprint": overlap,
          "worldBounds": entry["worldBounds"], "acquisition": {k: v for k, v in acquired.items() if k != "source"},
          "aiCalls": 0, "modelGeometryChanges": 0, "publication": False})
    print(json.dumps({"uid": UID, "triangles": entry["triangles"], "bounds": entry["worldBounds"],
                      "overlap": overlap, "aiCalls": 0}), flush=True)


if __name__ == "__main__":
    run()
