"""Fetch only exact indexed adjacent government terrain sheets for four XL holds."""

import importlib.util
import json

from shapely.geometry import Polygon, box

from run import ROOT, HERE, read, save, digest, connect


spec = importlib.util.spec_from_file_location("xl_terrain_source_recover", HERE / "xl-terrain-source-recover.py")
recover = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recover)

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
INDEX = ROOT / "source-scripts/city/landmark-acquisition/index.json"
OUT = BASE / "adjacent-sheet-recovery-20260927.json"
EXPECTED = {
    "landsd/91127:0": ("11-SE-7B", "11-SE-8A"),
    "landsd/149020:0": ("6-NW-8A", "6-NW-8C"),
    "landsd/264206:0": ("11-SW-8A", "11-SW-8B"),
    "landsd/293822:0": ("9-SE-3C", "9-SE-2D"),
}


def run():
    selection = {row["uid"]: row for row in read(BASE / "selection.json.gz")["rows"]}
    features = read(INDEX)["features"]
    indexed = {row["attributes"]["SHEETNO"]: row for row in features}
    assert read(INDEX)["completePagination"]
    by_sheet = {}
    for uid, (primary, adjacent) in EXPECTED.items():
        bounds = selection[uid]["native"]["model"]["worldBounds"]
        area = box(834500 + bounds[0][0], 816500 - bounds[1][2],
                   834500 + bounds[1][0], 816500 - bounds[0][2])
        hits = {row["attributes"]["SHEETNO"] for row in features
                if area.intersection(Polygon(row["geometry"]["rings"][0])).area > 1}
        assert hits == {primary, adjacent}, (uid, hits)
        assert selection[uid]["native"]["sheet"] == primary
        by_sheet[adjacent] = uid
    with connect() as connection:
        connection.execute("SET TRANSACTION READ ONLY")
        pinned = dict(connection.execute(
            "SELECT DISTINCT ON(sheet) sheet,result FROM astra_modelling.city_source_directories "
            "WHERE sheet=ANY(%s) ORDER BY sheet,created_at DESC", (list(by_sheet),)).fetchall())
    assert set(pinned) == set(by_sheet)
    rows = []
    for sheet, uid in sorted(by_sheet.items()):
        assert pinned[sheet]["sourceURL"] == indexed[sheet]["attributes"]["Format_glTF"]
        result = recover.work(sheet, pinned[sheet], [])
        assert result["state"] in {"exact-terrain-recovered", "revised-terrain-recovered-exact-model"}, result
        rows.append({**result, "uid": uid, "indexedIntersection": True,
                     "directorySourceSHA256": pinned[sheet]["directorySHA256"]})
        save(OUT, {"stage": "exact-indexed-adjacent-terrain-acquisition-v1",
                   "rows": rows, "complete": len(rows) == len(by_sheet),
                   "sourceIndexSHA256": digest(INDEX.read_bytes()),
                   "aiCalls": 0, "modelGeometryChanges": 0, "publication": False})
        print(json.dumps({"sheet": sheet, "uid": uid, "state": result["state"],
                          "terrainBytes": result["terrainBytes"]}), flush=True)


if __name__ == "__main__":
    run()
