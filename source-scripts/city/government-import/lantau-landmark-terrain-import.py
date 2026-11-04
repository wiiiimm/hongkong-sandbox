"""Publish script-cleared Lantau landmarks with bounded native government terrain."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "docs/astra-city/government-import/government-lantau-landmarks-16-20260916/second-pass"
LOCAL_BASE = HERE / "local/government-lantau-landmarks-16-second-20260916"
SECOND_BATCH = "government-lantau-landmarks-16-second-20260916"
CONFIG = {
    "barion": {
        "uid": "landsd/176915:0",
        "batch": "government-lantau-barion-20260916",
        "policy": "original-government-lantau-landmark-native-terrain-v1",
        "classification": "script-verified-original-government-landmark-native-terrain",
        "review": (
            "Exact unchanged government source for The Barion matched by object ID and Building CSUID. "
            "Detailed projection, complete source-face foundation, bounded native terrain, neighbour, "
            "runtime and browser checks pass."
        ),
    },
}
CONFIG.update({
    "peaceful-mansion": {
        "uid": "landsd/108805:0",
        "batch": "government-lantau-peaceful-mansion-20260916",
        "policy": "original-government-lantau-landmark-neighbour-preserving-terrain-v1",
        "classification": "script-verified-original-government-landmark-neighbour-preserving-terrain",
        "priority": "landmark",
        "retainedBuildingUids": ["landsd/176915:0", "landsd/108741:0"],
        "review": (
            "Exact unchanged Peaceful Mansion government source matched by object ID and Building CSUID. "
            "The combined native terrain replacement retains The Barion and preserves the neighbouring Joyful "
            "Mansion footprint. Source, neighbour, runtime and browser checks pass."
        ),
    },
    "disney-east": {
        "uid": "landsd/108263:0",
        "batch": "government-lantau-disney-east-20260916",
        "policy": "original-government-lantau-landmark-native-terrain-v1",
        "classification": "script-verified-original-government-landmark-native-terrain",
        "priority": "landmark",
        "review": (
            "Exact unchanged Hong Kong Disneyland government source matched by object ID and Building CSUID. "
            "Detailed projection, complete source-face foundation, bounded native terrain, neighbour, "
            "runtime and browser checks pass."
        ),
    },
})

spec = importlib.util.spec_from_file_location("terrain_import", HERE / "xl-terrain-candidate-import.py")
publication = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publication)
publication.s.BASE = ROOT / "docs/astra-city/government-import/government-lantau-landmarks-16-20260916"
publication.s.DOC = BASE
publication.s.LOCAL = LOCAL_BASE
publication.s.BATCH = SECOND_BATCH
publication.CONFIG.update(CONFIG)


def prepare_catalogue(key):
    _, _, stage_local, _, _, _ = publication.paths(key)
    catalogue_path = stage_local / "candidates/catalogue.json"
    catalogue = publication.read(catalogue_path)
    assert [model["uid"] for model in catalogue["models"]] == [CONFIG[key]["uid"]]
    catalogue["models"][0]["proceduralWindows"] = False
    publication.save(catalogue_path, catalogue)


def configure_call(key):
    original = publication.call

    def call(args):
        rewritten = list(args)
        if str(publication.__file__) in rewritten and rewritten[-1] == "owned":
            index = rewritten.index(str(publication.__file__))
            rewritten[index:index + 1] = [__file__, key]
        return original(rewritten)

    publication.call = call


def start(key):
    prepare_catalogue(key)
    configure_call(key)
    publication.start(key)


def owned(key):
    prepare_catalogue(key)
    configure_call(key)
    publication.owned(key)


if __name__ == "__main__":
    key = sys.argv[1]
    assert key in CONFIG
    owned(key) if len(sys.argv) > 2 else start(key)
