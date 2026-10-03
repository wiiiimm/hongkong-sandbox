"""Correct copied bundle labels after the verified 336916 installation."""

from run import ROOT, read, save, digest


BATCH = "government-xl-government-336916-20260927"
DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/government-336916-terrain-diagnostic-20260927"
STAGED = ROOT / "source-scripts/city/government-import/accepted" / BATCH / "catalogue.json"
LIVE = ROOT / "3d-viewer/city/data/official-models" / BATCH / "catalogue.json"
MANIFEST = ROOT / "3d-viewer/city/data/manifest.json"
PATCH_URL = "city/data/government-native-336916-0.json"
OLD_MODEL = "government building landsd/336916:0 Youth Hostel original government model"
NEW_MODEL = "Government building 336916 original source model"
OLD_TERRAIN = "government building landsd/336916:0 Youth Hostel exact government terrain"
NEW_TERRAIN = "Government building 336916 exact source terrain"


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def run():
    installed = read(DOC / "installed-acceptance.json")
    assert installed["snapshot"] and installed["aiCalls"] == 0
    assert read(DOC / "live-browser.json")["passed"]
    staged = read(STAGED)
    live = read(LIVE)
    manifest = read(MANIFEST)
    assert staged == live and staged["area"] == OLD_MODEL
    assert len(live["models"]) == 1 and live["models"][0]["uid"] == "landsd/336916:0"
    patch = [row for row in manifest["terrainPatches"] if row["url"] == PATCH_URL]
    assert len(patch) == 1 and patch[0]["area"] == OLD_TERRAIN
    before = {"catalogue": ref(LIVE), "manifest": ref(MANIFEST)}
    live["area"] = NEW_MODEL
    patch[0]["area"] = NEW_TERRAIN
    save(LIVE, live)
    save(MANIFEST, manifest)
    assert read(LIVE) == {**staged, "area": NEW_MODEL}
    assert next(row for row in read(MANIFEST)["terrainPatches"]
                if row["url"] == PATCH_URL)["area"] == NEW_TERRAIN
    assert read(STAGED) == staged
    save(DOC / "metadata-correction.json", {
        "uid": "landsd/336916:0", "reason": "Remove a copied Youth Hostel label from live bundle metadata",
        "modelArea": {"before": OLD_MODEL, "after": NEW_MODEL},
        "terrainArea": {"before": OLD_TERRAIN, "after": NEW_TERRAIN},
        "before": before, "after": {"catalogue": ref(LIVE), "manifest": ref(MANIFEST)},
        "stagedAcceptancePreserved": ref(STAGED),
        "modelGeometryChanges": 0, "terrainGeometryChanges": 0, "aiCalls": 0,
    })
    print("Corrected live bundle labels; staged acceptance and model assets unchanged")


if __name__ == "__main__":
    run()
