"""Prove unchanged Parkview XL towers touch their installed government podium."""

from shapely.geometry import MultiPoint, Polygon

from run import ROOT, HERE, read, save, digest

DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/parkview-terrain-diagnostic-20260925"
SUPPORT_UID = "landsd/254491:0"


def sha(path):
    return digest(path.read_bytes())


def run():
    probe = read(DOC / "support-probe-refined.json")
    selection = {row["uid"]: row for row in read(DOC / "selection.json.gz")["rows"]}
    installed = {}
    for url in read(ROOT / "3d-viewer/city/data/manifest.json")["officialModelCatalogues"]:
        for model in read(ROOT / "3d-viewer" / url)["models"]:
            installed[model["uid"]] = {"sha256": model["sha256"], "catalogue": url}
    assert SUPPORT_UID in installed
    result = []
    for source in probe["rows"]:
        row = dict(source)
        points = row.pop("contactPositions")
        target = selection[row["uid"]]["source"]["building"]
        polygon = Polygon(target["rings"][0], target["rings"][1:])
        contact = MultiPoint([(p[0], p[2]) for p in points]).convex_hull
        coverage = contact.intersection(polygon).area / polygon.area
        passed = (row["supportUid"] == SUPPORT_UID
                  and row["sourceSHA256"] == selection[row["uid"]]["candidate"]["entry"]["sha256"]
                  and row["supportSHA256"] == installed[SUPPORT_UID]["sha256"]
                  and row["within05"] >= 100 and coverage >= .85
                  and row["minimumDistance"] <= .5)
        result.append({**row, "contactHullTargetCoverage": coverage,
                       "contactHullAreaM2": contact.area,
                       "supportCatalogue": installed[SUPPORT_UID]["catalogue"],
                       "passed": passed})
    assert len(result) == 2 and all(row["passed"] for row in result), result
    save(DOC / "support-proof.json", {"rows": result, "probeSHA256": sha(DOC / "support-probe-refined.json"),
                                       "policy": "At least 100 original-vertex or adjacent original-face samples within 0.5 m of the installed exact government podium, with contact hull covering at least 85% of the tower footprint.",
                                       "aiCalls": 0, "modelGeometryChanges": 0})
    print({"passed": len(result), "coverage": [round(row["contactHullTargetCoverage"], 3) for row in result]})


if __name__ == "__main__":
    run()
