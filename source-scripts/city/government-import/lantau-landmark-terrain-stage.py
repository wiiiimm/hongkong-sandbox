"""Stage native government terrain for script-cleared Lantau landmarks."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "docs/astra-city/government-import/government-lantau-landmarks-16-20260916/second-pass"
LOCAL_BASE = HERE / "local/government-lantau-landmarks-16-second-20260916"
BATCH = "government-lantau-landmarks-16-second-20260916"
MODELS = {
    "disney-east": "landsd/108263:0",
    "peaceful-mansion": "landsd/108805:0",
    "barion": "landsd/176915:0",
    "disney-hotel-west": "landsd/72608:0",
    "disney-hotel-east": "landsd/76821:0",
}

spec = importlib.util.spec_from_file_location("terrain_stage", HERE / "xl-stage-west9zone.py")
stage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage)


def configure(key):
    uid = MODELS[key]
    stage.s.BASE = ROOT / "docs/astra-city/government-import/government-lantau-landmarks-16-20260916"
    stage.s.DOC = BASE
    stage.s.LOCAL = LOCAL_BASE
    stage.s.BATCH = BATCH
    stage.DOC = BASE / "third-pass" / ("terrain-" + key)
    stage.LOCAL = LOCAL_BASE / ("third-pass-terrain-" + key)
    stage.UID = uid
    stage.IDENTITY_FINAL_SCRIPT_EXCEPTIONS.add(uid)
    stage.NATIVE_COMPLETE_FACE_EXCEPTIONS.add(uid)
    if key == "disney-hotel-west":
        original_rectangle = stage.s.resolution.rectangle_for
        def hotel_pair_rectangle(bounds, parent):
            cells = original_rectangle(bounds, parent)
            selected = stage.read(BASE / "runtime-selection.json.gz")["rows"]
            other = next(row for row in selected if row["uid"] == "landsd/76821:0")
            other_cells = original_rectangle(other["candidate"]["entry"]["worldBounds"], parent)
            return [min(cells[0], other_cells[0]), min(cells[1], other_cells[1]), max(cells[2], other_cells[2]), max(cells[3], other_cells[3])]
        stage.s.resolution.rectangle_for = hotel_pair_rectangle
    if key == "peaceful-mansion":
        original_rectangle = stage.s.resolution.rectangle_for
        def combined_rectangle(bounds, parent):
            cells = original_rectangle(bounds, parent)
            manifest = stage.read(ROOT / "3d-viewer/city/data/manifest.json")
            entry = next(item for item in manifest["terrainPatches"] if item["url"] == "city/data/government-native-176915-0.json")
            other = stage.read(ROOT / "3d-viewer" / entry["url"])["coarseCells"]
            return [min(cells[0], other[0]), min(cells[1], other[1]), max(cells[2], other[2]), max(cells[3], other[3])]
        stage.s.resolution.rectangle_for = combined_rectangle
    return uid


def start(key):
    configure(key)
    original = stage.s.call

    def call(args):
        rewritten = list(args)
        if str(stage.__file__) in rewritten and rewritten[-1] == "owned":
            plan_path = stage.DOC / "patch-plan.json"
            plan = stage.read(plan_path)
            if key == "peaceful-mansion":
                manifest = stage.read(ROOT / "3d-viewer/city/data/manifest.json")
                url = "city/data/government-native-176915-0.json"
                entry = next(item for item in manifest["terrainPatches"] if item["url"] == url)
                plan["replaces"] = {"url": url, "sha256": stage.h(ROOT / "3d-viewer" / url), "retainedUids": ["landsd/176915:0"]}
                plan["uids"] = [MODELS[key]]
            if key == "disney-hotel-east":
                row = stage.read(stage.DOC / "selection.json.gz")["rows"][0]
                lo, hi = row["candidate"]["entry"]["worldBounds"]
                plan["coreBounds"] = [[lo[0] - 5, lo[1], lo[2] - 5], [hi[0] + 5, hi[1], hi[2] + 5]]
            if key == "disney-hotel-west":
                selected = stage.read(BASE / "runtime-selection.json.gz")["rows"]
                pair = [next(row for row in selected if row["uid"] == pair_uid) for pair_uid in ("landsd/72608:0", "landsd/76821:0")]
                lows = [row["candidate"]["entry"]["worldBounds"][0] for row in pair]
                highs = [row["candidate"]["entry"]["worldBounds"][1] for row in pair]
                plan["uids"] = [row["uid"] for row in pair]
                plan["coreBounds"] = [[min(lo[0] for lo in lows) - 5, min(lo[1] for lo in lows), min(lo[2] for lo in lows) - 5], [max(hi[0] for hi in highs) + 5, max(hi[1] for hi in highs), max(hi[2] for hi in highs) + 5]]
                neighbour_path = stage.DOC / "neighbour-inputs.json.gz"
                neighbours = stage.read(neighbour_path)
                neighbours["candidateIds"] = plan["uids"]
                stage.save(neighbour_path, neighbours)
            stage.save(plan_path, plan)
            index = rewritten.index(str(stage.__file__))
            rewritten[index:index + 1] = [__file__, key]
        return original(rewritten)

    stage.s.call = call
    stage.start()


def owned(key):
    configure(key)
    stage.owned()


if __name__ == "__main__":
    key = sys.argv[1]
    assert key in MODELS
    owned(key) if len(sys.argv) > 2 else start(key)
