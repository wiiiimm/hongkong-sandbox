"""Prove Harbourview Horizon's visible base contacts terrain despite tiny buried source faces."""

import gzip
import json
from pathlib import Path

from shapely.geometry import MultiPoint, Polygon

from run import ROOT, HERE, read, save, digest

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
LOCAL = HERE / "local/government-xl-harbourview-horizon-mask-20260929/harbourview-horizon"
UID = "landsd/237402:0"


def run():
    path = LOCAL / "geometry-out.json.gz"
    geometry = json.loads(gzip.decompress(path.read_bytes()))["rows"][0]
    assert geometry["uid"] == UID
    source = read(HERE / "local/government-xl-harbourview-horizon-terrain-20260929/candidates/catalogue.json")["models"][0]
    assert geometry["sourceSHA256"] == source["sha256"]
    position, ground = geometry["position"], geometry["drawnGround"]
    assert len(position) == len(ground) * 3 and all(y is not None for y in ground)
    base = source["recordedBaseHeight"]
    values = [(position[3 * i], position[3 * i + 1], position[3 * i + 2], y)
              for i, y in enumerate(ground)]
    buried = [point for point in values if point[1] < point[3] - .25]
    contacts = [point for point in values if point[1] >= base - .2 and abs(point[1] - point[3]) <= .5]
    form = read(BASE / "harbourview-horizon-terrain-diagnostic-20260929/selection.json.gz")["rows"][0]["source"]["building"]
    target = Polygon(form["rings"][0], form["rings"][1:])
    hull = MultiPoint([(x, z) for x, _, z, _ in contacts]).convex_hull
    coverage = hull.intersection(target).area / target.area
    foundation = read(BASE / "harbourview-horizon-mask-foundation-20260929.json")["rows"][0]
    proof = foundation["foundation"]
    passed = (foundation["strictFoundationAccepted"] and proof["fullyBuriedUpwardTriangles"] == 0
              and proof["fullyBuriedAreaFraction"] <= .001 and len(buried) / len(values) < .01
              and len(contacts) >= 100 and coverage >= .8)
    result = {"uid": UID, "sourceSHA256": source["sha256"],
              "terrainSHA256": foundation["candidatePatch"]["sha256"],
              "geometryInputSHA256": digest(path.read_bytes()),
              "sourceVertices": len(values), "buriedVertices": len(buried),
              "buriedVertexFraction": len(buried) / len(values),
              "minimumBuriedGapM": min((point[1] - point[3] for point in buried), default=0),
              "nearGroundContactVerticesAboveRecordedBase": len(contacts),
              "contactHullTargetCoverage": coverage,
              "fullyBuriedUpwardTriangles": proof["fullyBuriedUpwardTriangles"],
              "fullyBuriedAreaFraction": proof["fullyBuriedAreaFraction"],
              "passed": passed,
              "policy": "Original source stays unchanged. At most 0.1% of face area and 1% of vertices may be buried, no upward source face may be fully buried, and >=100 near-ground vertices above the recorded base must span >=80% of the target footprint.",
              "aiCalls": 0, "modelGeometryChanges": 0, "publication": False}
    save(BASE / "harbourview-horizon-contact-proof-20260929.json", result)
    assert passed, result
    print({"contactVertices": len(contacts), "coverage": coverage,
           "buriedVertices": len(buried), "buriedAreaFraction": proof["fullyBuriedAreaFraction"]}, flush=True)


if __name__ == "__main__":
    run()
