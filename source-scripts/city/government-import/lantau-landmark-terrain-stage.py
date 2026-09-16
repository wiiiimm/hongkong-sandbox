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
    return uid


def start(key):
    configure(key)
    original = stage.s.call

    def call(args):
        rewritten = list(args)
        if str(stage.__file__) in rewritten and rewritten[-1] == "owned":
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
