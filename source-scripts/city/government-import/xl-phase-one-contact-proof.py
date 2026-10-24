"""Prove Phase 1's visible base contacts terrain despite tiny buried source faces."""

import gzip
import json
from pathlib import Path

from shapely.geometry import MultiPoint, Polygon

from run import ROOT, HERE, read, save, digest

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
LOCAL = HERE / "local/government-xl-phase-one-terrain-20260927"
UID = "landsd/305672:0"


def run():
    path = LOCAL / "geometry-out.json.gz"
    geometry = json.loads(gzip.decompress(path.read_bytes()))["rows"][0]
    assert geometry["uid"] == UID
    source = read(LOCAL / "candidates/catalogue.json")["models"][0]
    assert geometry["sourceSHA256"] == source["sha256"]
    position, ground = geometry["position"], geometry["drawnGround"]
    assert len(position) == len(ground) * 3 and all(y is not None for y in ground)
    base = source["recordedBaseHeight"]
    values = [(position[3 * i], position[3 * i + 1], position[3 * i + 2], y)
              for i, y in enumerate(ground)]
    buried = [point for point in values if point[1] < point[3] - .25]
    contacts = [point for point in values if point[1] >= base - .2 and abs(point[1] - point[3]) <= .5]
    form = next(row for row in read(ROOT / "3d-viewer/city/data/tiles/0_-2.json")["buildings"] if row["uid"] == UID)
    target = Polygon(form["rings"][0], form["rings"][1:])
    hull = MultiPoint([(x, z) for x, _, z, _ in contacts]).convex_hull
    coverage = hull.intersection(target).area / target.area
    foundation = read(BASE / "phase-one-foundation-20260927.json")
    proof = foundation["foundation"]
    passed = (foundation["strictFoundationAccepted"] and proof["fullyBuriedUpwardTriangles"] == 0
              and proof["fullyBuriedAreaFraction"] <= .001 and len(buried) / len(values) < .01
              and len(contacts) >= 100 and coverage >= .8)
    result = {"uid": UID, "sourceSHA256": source["sha256"],
              "geometryInputSHA256": digest(path.read_bytes()),
              "sourceVertices": len(values), "buriedVertices": len(buried),
              "buriedVertexFraction": len(buried) / len(values),
              "minimumBuriedGapM": min(point[1] - point[3] for point in buried),
              "nearGroundContactVerticesAboveRecordedBase": len(contacts),
              "contactHullTargetCoverage": coverage,
              "fullyBuriedUpwardTriangles": proof["fullyBuriedUpwardTriangles"],
              "fullyBuriedAreaFraction": proof["fullyBuriedAreaFraction"],
              "passed": passed,
              "policy": "Original source stays unchanged. At most 0.1% of face area and 1% of vertices may be buried, no upward source face may be fully buried, and >=100 near-ground vertices above the recorded base must span >=80% of the target footprint.",
              "aiCalls": 0, "modelGeometryChanges": 0, "publication": False}
    save(BASE / "phase-one-contact-proof-20260927.json", result)
    assert passed, result
    print({"contactVertices": len(contacts), "coverage": coverage,
           "buriedVertices": len(buried), "buriedAreaFraction": proof["fullyBuriedAreaFraction"]}, flush=True)


if __name__ == "__main__":
    run()
