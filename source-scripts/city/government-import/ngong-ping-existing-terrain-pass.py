"""Stage Ngong Ping sources against already installed government terrain; no geometry edits or AI."""
from __future__ import annotations

from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = "government-ngong-ping-peaks-473-20260918"
BATCH = "government-ngong-ping-peaks-compute-20260918"
DOC = ROOT / "docs/astra-city/government-import" / SOURCE
STAGE = HERE / "accepted" / BATCH


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == ".gz" else raw)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    exact = {row["uid"]: row for row in read(DOC / "exact-pass-results.json.gz")["rows"]}
    selection = {row["uid"]: row for row in read(DOC / "check-selection.json.gz")["rows"]}
    terrain = read(DOC / "terrain-pass.json")
    existing = set(terrain["held"])
    assert len(existing) == 191
    assert all(exact[uid]["publicationCandidate"] for uid in existing)

    catalogue = read(STAGE / "catalogue.json")
    models = {row["uid"]: row for row in catalogue["models"]}
    forms = {row["uid"]: row for row in read(STAGE / "source-forms.json")}
    assert len(models) == 219 and not (set(models) & existing)

    grouped = defaultdict(list)
    for uid in sorted(existing):
        row = selection[uid]
        proof = exact[uid]
        entry = dict(row["candidate"]["entry"])
        entry.update(
            priority="detail",
            placementReviewed=True,
            sourceIdentityReviewed=True,
            identityReviewApproved=True,
            publicationApproved=False,
            proceduralWindows=False,
            placementReview=(
                "Exact unchanged Lands Department source matched by object ID and Building CSUID. "
                "Full-face same-revision source terrain passed; installed 5 m government terrain retained "
                "and runtime/browser contact remains mandatory. No AI review, remodelling, simplification "
                "or geometry edit."
            ),
        )
        if proof["suppressesBuildingUids"]:
            entry["suppressesBuildingUids"] = proof["suppressesBuildingUids"]
        asset = STAGE / entry["asset"]
        asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(row["candidate"]["path"], asset)
        assert sha(asset) == entry["sha256"]
        models[uid] = entry
        form = dict(row["source"]["building"])
        form["tile"] = Path(row["source"]["tile"]).stem
        forms[uid] = form
        grouped[(terrain["held"][uid], row["native"]["sheet"])].append(uid)

    catalogue["models"] = [models[uid] for uid in sorted(models)]
    catalogue["counts"] = {"packedModels": len(models)}
    save(STAGE / "catalogue.json", catalogue)
    save(STAGE / "catalogue-index.json", {"models": len(models), "catalogues": ["catalogue.json"]})
    save(STAGE / "source-forms.json", [forms[uid] for uid in sorted(forms)])

    groups = list(terrain["groups"])
    for number, ((reason, sheet), uids) in enumerate(sorted(grouped.items()), 1):
        groups.append({
            "id": f"existing-government-terrain-{number:03d}",
            "parentURL": "installed-government-terrain",
            "uids": uids,
            "sourceSheets": [sheet],
            "existingTerrainRuntimeCandidate": True,
            "reason": reason,
        })
    terrain.update(
        terrainAccepted=len(models),
        terrainHeld=0,
        held={},
        reasonCounts={},
        groups=groups,
        existingTerrainAccepted=len(existing),
        existingTerrainPolicy=(
            "Full-face same-revision source terrain passed. Existing installed government terrain is "
            "retained when an equal-resolution child would not refine its parent; runtime and browser "
            "ground-contact checks remain mandatory."
        ),
        aiCalls=0,
        modelGeometryChanges=0,
        publication=False,
    )
    save(DOC / "terrain-pass.json", terrain)
    print(json.dumps({
        "refinedTerrain": 219,
        "existingTerrainCandidates": len(existing),
        "runtimeCandidates": len(models),
        "representativeGroups": len(groups),
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    }))


if __name__ == "__main__":
    main()
