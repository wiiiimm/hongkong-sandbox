"""Drop a Tai O terrain patch that crosses an installed Ngong Ping patch."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = "government-tai-o-northwest-600-20260921"
BATCH = "government-tai-o-northwest-compute-20260921"
DOC = ROOT / "docs/astra-city/government-import" / SOURCE
STAGE = HERE / "accepted" / BATCH
DROP_DESTINATION = "city/data/government-tai-o-northwest-016.json"


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    plan = read(STAGE / "plan.json")
    matches = [row for row in plan["topLevelTerrainPatches"] if row["destination"] == DROP_DESTINATION]
    assert len(matches) == 1
    dropped = matches[0]
    patch = read(ROOT / dropped["source"])
    uids = sorted(patch["meta"]["targetUids"])
    assert len(uids) == 20
    plan["topLevelTerrainPatches"] = [
        row for row in plan["topLevelTerrainPatches"] if row["destination"] != DROP_DESTINATION
    ]
    save(STAGE / "plan.json", plan)

    terrain = read(DOC / "terrain-pass.json")
    terrain["topLevelTerrainPatches"] = plan["topLevelTerrainPatches"]
    current_metric = read(DOC / "terrain-candidates.json")
    terrain["metricTerrainCandidates"] = [
        row for row in current_metric if row["path"] != dropped["source"]
    ]
    terrain["overlapTerrainRetained"] = [{
        "uids": uids,
        "droppedCandidate": dropped["source"],
        "installedConflict": "city/data/government-ngong-ping-009.json",
        "reason": "Merged top-level patch crossed an installed patch; existing verified terrain retained and runtime contact rechecked.",
    }]
    save(DOC / "terrain-pass.json", terrain)
    save(DOC / "terrain-candidates.json", terrain["metricTerrainCandidates"])

    browser = read(STAGE / "browser-config.json")
    browser["terrain"] = [
        row for row in browser["terrain"] if row["destination"] != DROP_DESTINATION
    ]
    save(STAGE / "browser-config.json", browser)
    print(json.dumps({
        "droppedTerrainPatches": 1,
        "existingTerrainCandidates": len(uids),
        "remainingTopLevelPatches": len(plan["topLevelTerrainPatches"]),
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    }))


if __name__ == "__main__":
    main()
