"""Remove unsupported child bundles from native terrain parents before Ngong Ping runtime checks."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = "government-ngong-ping-peaks-473-20260918"
BATCH = "government-ngong-ping-peaks-compute-20260918"
DOC = ROOT / "docs/astra-city/government-import" / SOURCE
STAGE = HERE / "accepted" / BATCH


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    terrain = read(DOC / "terrain-pass.json")
    retained = []
    removed = []
    uids = []
    for relative in terrain["nestedTerrainBundles"]:
        bundle = read(ROOT / relative)
        parent = read(ROOT / "3d-viewer" / bundle["parentTerrainURL"])
        if parent.get("nativeMesh"):
            removed.append(relative)
            uids.extend(uid for patch in bundle["patches"] for uid in patch["meta"]["targetUids"])
        else:
            retained.append(relative)
    assert removed and set(uids) == {"landsd/62290:0"}
    terrain["nestedTerrainBundles"] = retained
    terrain["metricTerrainCandidates"] = [
        row for row in terrain["metricTerrainCandidates"]
        if row.get("replaces", {}).get("url") != "city/data/government-southwest-lantau-017.json"
    ]
    terrain["nativeParentTerrainRetained"] = [{
        "uid": uid,
        "parentURL": "city/data/government-southwest-lantau-017.json",
        "reason": "Runtime does not allow nested children on a native terrain parent; existing verified parent retained.",
    } for uid in sorted(uids)]
    save(DOC / "terrain-pass.json", terrain)
    save(DOC / "terrain-candidates.json", terrain["metricTerrainCandidates"])
    plan = read(STAGE / "plan.json")
    plan["areas"][0]["terrain"] = retained
    save(STAGE / "plan.json", plan)
    print(json.dumps({
        "retainedBundles": len(retained),
        "removedNativeParentBundles": len(removed),
        "existingTerrainUids": sorted(uids),
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    }))


if __name__ == "__main__":
    main()
