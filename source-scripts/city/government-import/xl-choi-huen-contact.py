"""Prove contact inside the unchanged Choi Huen government assembly; never AI."""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("second", HERE / "xl-second-pass.py")
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
spec = importlib.util.spec_from_file_location("support", HERE / "xxl-support-context.py")
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)

PRIMARY = "landsd/50009:0"
DOC = s.DOC / "third-pass/terrain-choi-huen"
RECOVERY = s.LOCAL / "third-pass-terrain-choi-huen-supports/runtime.json.gz"


def flattened(row):
    entry = row["candidate"]["entry"]
    return {
        **row,
        "sourceSHA256": entry["sha256"],
        "modelId": entry["modelId"],
        "triangles": entry["triangles"],
    }


def main():
    primary = next(
        row for row in s.read(s.DOC / "runtime-selection.json.gz")["rows"]
        if row["uid"] == PRIMARY
    )
    recovered = s.read(RECOVERY)
    assert recovered["aiCalls"] == 0 and not recovered["publication"]
    rows = [primary, *recovered["rows"]]
    assert len(rows) == len({row["uid"] for row in rows}) == 5
    assert {row["candidate"]["entry"]["sourceTile"] for row in rows} == {"11-NE-12B"}

    triangles = {row["uid"]: s.glb_triangles(flattened(row)) for row in rows}
    proofs = []
    for row in rows[1:]:
        uid = row["uid"]
        geometry = triangles[uid]
        points, bottom = s.resolution.sample_points({
            "position": geometry.reshape(-1).tolist(),
            "index": list(range(len(geometry) * 3)),
        })
        low = points[points[:, 1] <= bottom + .35]
        other = np.concatenate([value for key, value in triangles.items() if key != uid])
        surface_triangles, tree = support.surface(other)
        heights = support.samples_below(low[:, [0, 2]], surface_triangles, tree, bottom + .5)
        covered = np.isfinite(heights)
        gaps = low[:, 1] - heights
        contacts = covered & (np.abs(gaps) <= .5)
        outliers = [
            {"point": point.tolist(), "supportHeight": float(height), "gapM": float(gap)}
            for point, height, gap, contact in zip(low, heights, gaps, contacts)
            if not contact
        ]
        entry = row["candidate"]["entry"]
        building = row["source"]["building"]
        contact_fraction = float(contacts.sum() / len(low))
        exact_identity = (
            entry["objectId"] == building["objectId"]
            and entry["buildingCSUID"] == building["buildingCSUID"]
            and entry["modelId"][1:11] == entry["buildingCSUID"][:10]
        )
        passed = bool(
            exact_identity
            and len(low) > 0
            and covered.all()
            and contact_fraction >= .99
            and entry["overlapOfSmallerFootprint"] >= .995
            and entry["footprintCentroidDistanceMetres"] <= 2.25
        )
        proofs.append({
            "uid": uid,
            "sourceSHA256": entry["sha256"],
            "supportUids": sorted(set(triangles) - {uid}),
            "bottomM": float(bottom),
            "rimSamples": len(low),
            "covered": int(covered.sum()),
            "contactsWithinHalfMetre": int(contacts.sum()),
            "contactFraction": contact_fraction,
            "gapRangeM": [float(gaps[covered].min()), float(gaps[covered].max())],
            "outliers": outliers,
            "exactIdentity": exact_identity,
            "overlapOfSmallerFootprint": entry["overlapOfSmallerFootprint"],
            "footprintCentroidDistanceMetres": entry["footprintCentroidDistanceMetres"],
            "passed": passed,
        })

    result = {
        "primaryUid": PRIMARY,
        "primarySHA256": primary["candidate"]["entry"]["sha256"],
        "sourceSheet": "11-NE-12B",
        "rows": proofs,
        "passed": all(row["passed"] for row in proofs),
        "policy": "Every unchanged support component must have exact source identity, >=99.5% footprint overlap, <=2.25m centroid offset, complete vertical source coverage and >=99% of low-rim samples within 0.5m of another component from the same pinned source sheet. Isolated cantilever rim vertices may remain unsupported by the podium surface.",
        "aiCalls": 0,
        "modelGeometryChanges": 0,
        "publication": False,
    }
    s.save(DOC / "assembly-support.json", result)
    assert result["passed"], result
    print(json.dumps({"components": len(proofs), "passed": result["passed"], "aiCalls": 0}))


if __name__ == "__main__":
    main()
