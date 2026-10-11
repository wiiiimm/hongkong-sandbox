"""Classify covered and retained viewer forms for the remaining Lantau landmarks."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DOC = ROOT / "docs/astra-city/government-import/government-lantau-landmarks-16-20260916/second-pass"
FINAL = DOC / "final-script-pass/results.json.gz"
SELECTION = DOC / "runtime-selection.json.gz"
OUT = DOC / "assembly-map.json"
UIDS = {
    "landsd/107386:0", "landsd/108265:0", "landsd/108736:0",
    "landsd/108741:0", "landsd/178555:0", "landsd/187251:0",
    "landsd/246229:0", "landsd/246471:0", "landsd/271137:0",
    "landsd/296766:0", "landsd/337237:0",
}
POLICY = (
    "For exact unchanged government sources covering at least 93% of their target, "
    "suppress only LandsD forms whose footprint is at least 95% covered and whose top "
    "is vertically contained by the source within 0.25m. Retain partial, taller, OSM, "
    "support and adjacent forms."
)


def read(path):
    import gzip
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    final = {row["uid"]: row for row in read(FINAL)["rows"] if row["uid"] in UIDS}
    selected = {row["uid"]: row for row in read(SELECTION)["rows"] if row["uid"] in UIDS}
    assert set(final) == UIDS == set(selected)
    rows = []
    for uid in sorted(UIDS):
        frozen = final[uid]
        runtime = selected[uid]
        identity = frozen["identity"]
        entry = runtime["candidate"]["entry"]
        building = runtime["source"]["building"]
        matches = runtime["native"]["model"]["matching"]["viewerMatches"]
        assert identity["exactObjectAndCSUID"]
        assert identity["targetCoveredBySourceProjection"] >= 0.93
        assert entry["objectId"] == building["objectId"]
        assert entry["buildingCSUID"] == building["buildingCSUID"]
        assert len(matches) == 1 and matches[0]["uid"] == uid
        suppressions, retained, relationships = [], [], []
        for form in identity["intersectingForms"]:
            other_uid = form["uid"]
            if other_uid == uid:
                continue
            vertically_contained = form["sourceYRange"][1] >= form["top"] - 0.25
            suppress = (
                other_uid.startswith("landsd/")
                and form["fractionOfForm"] >= 0.95
                and vertically_contained
            )
            (suppressions if suppress else retained).append(other_uid)
            relationships.append({
                "uid": other_uid,
                "action": "suppress-covered-low-form" if suppress else "retain-support-or-adjacent-form",
                "fractionOfForm": form["fractionOfForm"],
                "intersectionAreaM2": form["intersectionAreaM2"],
                "sourceIntersectionHeightRangeHKPD": form["sourceYRange"],
                "baseHeightHKPD": form["base"],
                "topHeightHKPD": form["top"],
                "verticallyContained": vertically_contained,
                "sameParent": form["sameParent"],
                "sharedOsmReference": form["sharedOsmReference"],
            })
        suppressions = sorted(set(suppressions))
        retained = sorted(set(retained) - set(suppressions))
        adjacent = {form["uid"] for form in identity["intersectingForms"] if form["uid"] != uid}
        accepted = adjacent == set(suppressions) | set(retained) and not (set(suppressions) & set(retained))
        rows.append({
            "uid": uid,
            "name": entry["label"],
            "sourceSHA256": entry["sha256"],
            "targetCoverage": identity["targetCoveredBySourceProjection"],
            "accepted": accepted,
            "policy": POLICY,
            "suppressions": suppressions,
            "retainedForms": retained,
            "relationships": relationships,
            "aiCalls": 0,
            "modelGeometryChanges": 0,
        })
    document = {
        "batch": "government-lantau-landmarks-remaining-11-20260916",
        "policy": POLICY,
        "finalScriptPassSHA256": digest(FINAL),
        "runtimeSelectionSHA256": digest(SELECTION),
        "models": len(rows),
        "accepted": sum(row["accepted"] for row in rows),
        "aiCalls": 0,
        "modelGeometryChanges": 0,
        "rows": rows,
    }
    OUT.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(OUT.relative_to(ROOT)), "models": len(rows), "accepted": document["accepted"], "suppressions": {row["uid"]: row["suppressions"] for row in rows if row["suppressions"]}}, indent=2))


if __name__ == "__main__":
    main()
