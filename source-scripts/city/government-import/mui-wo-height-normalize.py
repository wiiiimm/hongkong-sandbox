"""Stage three exact Mui Wo sources using a bounded official-height placement correction.

The source GLB bytes, nodes, vertices, indices, materials and horizontal placement
remain unchanged. Each model receives one vertical translation equal to current
LandsD TopHeight minus the source mesh maximum HKPD elevation.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE_BATCH = "government-mui-wo-23-20260914"
BATCH = "government-mui-wo-height-correction-3-20260915"
SOURCE = ROOT / "docs/astra-city/government-import" / SOURCE_BATCH / "check-selection.json.gz"
SOURCE_PROOF = ROOT / "docs/astra-city/government-import/government-mui-wo-16-20260915/script-pass-results.json.gz"
LOCAL_SOURCE = HERE / "local" / SOURCE_BATCH
STAGE = HERE / "accepted" / BATCH
DOC = ROOT / "docs/astra-city/government-import" / BATCH
UIDS = {"landsd/172460:0", "landsd/201705:0", "landsd/208036:0"}


def read(path: Path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def save(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == ".gz" else raw)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def call(args, allowed=(0,)) -> None:
    result = subprocess.run(args, cwd=ROOT)
    assert result.returncode in allowed, (args, result.returncode)


def shifted_bounds(bounds, offset):
    return [[point[0], point[1] + offset, point[2]] for point in bounds]


def main() -> None:
    selected = read(SOURCE)
    rows = {row["uid"]: row for row in selected["rows"] if row["uid"] in UIDS}
    proof = {row["uid"]: row for row in read(SOURCE_PROOF)["rows"] if row["uid"] in UIDS}
    assert set(rows) == set(proof) == UIDS
    template = read(LOCAL_SOURCE / "recovered/catalogue.json")
    models, runtime_rows, forms, placement = [], [], [], []
    STAGE.mkdir(parents=True, exist_ok=True)
    for uid in sorted(UIDS):
        row = json.loads(json.dumps(rows[uid]))
        evidence = proof[uid]
        entry = dict(row["candidate"]["entry"])
        source_bounds = json.loads(json.dumps(entry["worldBounds"]))
        offset = entry["recordedTopHeight"] - source_bounds[1][1]
        assert 0 < abs(offset) <= 20
        bounds = shifted_bounds(source_bounds, offset)
        assert abs(bounds[1][1] - entry["recordedTopHeight"]) <= .002
        target = next(item for item in evidence["identity"]["intersectingForms"] if item["uid"] == uid)
        base_delta = bounds[0][1] - target["base"]
        assert abs(base_delta) <= 1.1
        entry.update(
            priority="detail",
            placementReviewed=True,
            sourceIdentityReviewed=True,
            identityReviewApproved=True,
            publicationApproved=False,
            proceduralWindows=False,
            sourceWorldBounds=source_bounds,
            worldBounds=bounds,
            verticalPlacementOffsetHKPD=offset,
            verticalPlacementBasis="current-recorded-top-height",
            placementReview=(
                "Exact government object ID, Building CSUID and horizontal footprint match. "
                f"The unchanged source asset receives one {offset:+.4f} m vertical translation so its highest source roof equals the current LandsD TopHeight {entry['recordedTopHeight']:.1f} m HKPD; "
                f"the shifted source bottom is {base_delta:+.4f} m from current LandsD BaseHeight. "
                "Source GLB bytes, nodes, vertices, indices, materials and XY placement are unchanged. Deterministic script only; no AI or remodelling."
            ),
        )
        source_asset = Path(row["candidate"]["path"])
        target_asset = STAGE / entry["asset"]
        target_asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_asset, target_asset)
        assert digest(target_asset) == entry["sha256"] and target_asset.stat().st_size == entry["bytes"]
        row["candidate"]["entry"] = entry
        row["candidate"]["path"] = str(target_asset)
        models.append(entry)
        runtime_rows.append(row)
        form = dict(row["source"]["building"])
        form["tile"] = Path(row["source"]["tile"]).stem
        forms.append(form)
        placement.append({
            "uid": uid,
            "modelId": entry["modelId"],
            "sourceSHA256": entry["sha256"],
            "sourceWorldBounds": source_bounds,
            "correctedWorldBounds": bounds,
            "verticalPlacementOffsetHKPD": offset,
            "verticalPlacementBasis": entry["verticalPlacementBasis"],
            "currentRecordedBaseHeight": entry["recordedBaseHeight"],
            "currentRecordedTopHeight": entry["recordedTopHeight"],
            "correctedBottomDeltaFromBaseM": base_delta,
            "sourceGeometryChanged": False,
            "horizontalPlacementChanged": False,
        })
    template.update(
        area="Mui Wo exact government sources with bounded current-height placement · September 2026",
        coordinatePolicy="Unchanged source GLB bytes/nodes/vertices/indices/materials and XY placement; one bounded vertical translation aligns source roof maximum to current LandsD TopHeight",
        loadingPolicy="Published only after deterministic identity, height-alignment, terrain, runtime and browser checks",
        counts={"packedModels": len(models)},
        models=models,
    )
    save(STAGE / "catalogue.json", template)
    save(STAGE / "catalogue-index.json", {"models": len(models), "catalogues": ["catalogue.json"]})
    save(STAGE / "source-forms.json", forms)
    selection = dict(selected)
    selection.update(batch=BATCH, rows=runtime_rows, manifestSHA256=digest(ROOT / "3d-viewer/city/data/manifest.json"), aiCalls=0)
    save(DOC / "selection.json.gz", selection)
    save(DOC / "terrain-candidates.json", [])
    save(DOC / "placement-proof.json", {
        "batch": BATCH,
        "models": len(placement),
        "policy": "bounded-current-landsd-height-alignment-v1",
        "rows": placement,
        "aiCalls": 0,
        "modelGeometryChanges": 0,
        "placementChanges": len(placement),
        "qualification": "Exact source identity and horizontal placement are retained. A deterministic vertical translation aligns the unchanged source roof maximum to current LandsD TopHeight, with corrected bottoms within 1.1 m of current LandsD BaseHeight.",
    })
    save(DOC / "source-forms.json", {row["uid"]: row["source"] for row in runtime_rows})
    call(["node", str(HERE / "acceptance-metrics.mjs"), "--selection", relative(DOC / "selection.json.gz"), "--candidates", relative(STAGE), "--terrain-candidates", relative(DOC / "terrain-candidates.json"), "--out", relative(DOC / "metrics.json")])
    call(["node", str(HERE.parent / "building-batch/validate_candidates.mjs"), "--candidates", relative(STAGE), "--source-forms", relative(DOC / "source-forms.json"), "--out", relative(DOC / "validation.json")], allowed=(0, 1))
    metrics, validation = read(DOC / "metrics.json"), read(DOC / "validation.json")
    assert not [row for row in metrics["rows"] if row.get("error") or not row.get("sourcePreserved")]
    assert validation["exceptions"] == 0 and validation["loaderAccepted"] == len(models)
    save(STAGE / "plan.json", {"areas": [{
        "area": template["area"],
        "catalogue": relative(STAGE / "catalogue.json"),
        "destination": f"city/data/official-models/{BATCH}/catalogue.json",
    }]})
    save(STAGE / "browser-config.json", {
        "stage": relative(STAGE) + "/",
        "doc": relative(DOC) + "/",
        "catalogueURL": f"city/data/official-models/{BATCH}/catalogue.json",
        "terrain": [],
        "fitBox": True,
        "browserUids": sorted(UIDS),
        "failureTestUids": [sorted(UIDS)[0]],
    })
    save(DOC / "result.json", {
        "batch": BATCH,
        "models": len(models),
        "runtimeAccepted": validation["loaderAccepted"],
        "validationExceptions": validation["exceptions"],
        "sourceAssetsPreserved": True,
        "modelGeometryChanges": 0,
        "placementChanges": len(models),
        "aiCalls": 0,
        "publication": False,
        "placementProofSHA256": digest(DOC / "placement-proof.json"),
        "metricsSHA256": digest(DOC / "metrics.json"),
        "validationSHA256": digest(DOC / "validation.json"),
    })
    print(json.dumps(read(DOC / "result.json"), indent=2))


if __name__ == "__main__":
    main()
