"""Gate the exact Cainiao tower/podium pair against the masked terrain."""

import importlib.util
import json
import shutil
import subprocess

import numpy as np
from shapely.geometry import MultiPoint, Polygon

from run import ROOT, HERE, read, save, digest

spec = importlib.util.spec_from_file_location("xl_final_script_pass", HERE / "xl-final-script-pass.py")
final = importlib.util.module_from_spec(spec)
spec.loader.exec_module(final)

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
LOCAL = HERE / "local/government-xl-cainiao-pair-checks-20260927"
TOWER = "landsd/293822:0"
PODIUM = "landsd/327178:0"


def rel(path):
    return str(path.relative_to(ROOT))


def call(args, allowed=(0,)):
    result = subprocess.run(args, cwd=ROOT)
    assert result.returncode in allowed, (args, result.returncode)


def run():
    tower = read(BASE / "cainiao-smart-gateway-terrain-diagnostic-20260927/selection.json.gz")["rows"][0]
    podium = read(HERE / "local/government-xl-cainiao-podium-20260927/support-runtime.json.gz")["rows"][0]
    assert tower["uid"] == TOWER and podium["uid"] == PODIUM
    proof = read(BASE / "cainiao-source-support-probe-20260927.json")
    target = Polygon(tower["source"]["building"]["rings"][0], tower["source"]["building"]["rings"][1:])
    contact = MultiPoint([(x, z) for x, _, z in proof["contactPositions"]]).convex_hull
    coverage = contact.intersection(target).area / target.area
    support_ok = (proof["uid"] == TOWER and proof["supportUid"] == PODIUM
                  and proof["sourceSHA256"] == tower["candidate"]["entry"]["sha256"]
                  and proof["supportSHA256"] == podium["candidate"]["entry"]["sha256"]
                  and proof["within05"] >= 100 and coverage >= .85)
    assert support_ok
    save(BASE / "cainiao-source-support-proof-20260927.json",
         {"uid": TOWER, "supportUid": PODIUM, "sourceSHA256": proof["sourceSHA256"],
          "supportSHA256": proof["supportSHA256"], "within05": proof["within05"],
          "interfaceSamples": proof["interfaceSamples"], "contactHullTargetCoverage": coverage,
          "passed": True, "probeSHA256": digest((BASE / "cainiao-source-support-probe-20260927.json").read_bytes()),
          "policy": "At least 100 original lower vertices within 0.5 m of exact podium triangles; contact hull covers at least 85% of tower footprint.",
          "aiCalls": 0, "modelGeometryChanges": 0})
    mask = read(BASE / "cainiao-shared-mask-eval-20260927.json")["rows"][0]
    assert mask["uid"] == TOWER and not mask["remainingBlockedUids"]
    patch_path = ROOT / mask["candidatePatch"]["path"]
    assert digest(patch_path.read_bytes()) == mask["candidatePatch"]["sha256"]
    patch = read(patch_path)
    positions = np.asarray(patch["nativeMesh"]["position"], dtype=np.float32).reshape(-1, 3)
    terrain = positions[np.asarray(patch["nativeMesh"]["index"]).reshape(-1, 3)]
    (LOCAL / "assets").mkdir(parents=True, exist_ok=True)
    final.s.LOCAL = LOCAL
    for row in (podium, tower):
        source = row["candidate"]["path"]
        target = LOCAL / "assets" / (row["candidate"]["entry"]["sha256"] + ".glb.gz")
        shutil.copyfile(source, target)
    rows = []
    for row in (podium, tower):
        entry = row["candidate"]["entry"]
        triangles = final.s.glb_triangles({**row["native"]["model"], "sourceSHA256": entry["sha256"],
                                           "modelId": entry["modelId"], "triangles": entry["triangles"],
                                           "native": row["native"]})
        form = row["source"]["building"]
        footprint = Polygon(form["rings"][0], form["rings"][1:])
        foundation = final.foundation_context(triangles, terrain, footprint)
        strict = (foundation["completeTerrainTriangles"] == foundation["triangles"]
                  and foundation["fullyBuriedUpwardTriangles"] == 0
                  and foundation["fullyBuriedAreaFraction"] <= .001)
        rows.append({"uid": row["uid"], "strictFoundationAccepted": strict,
                     "foundation": foundation, "sourceSHA256": entry["sha256"]})
    save(BASE / "cainiao-pair-foundation-20260927.json",
         {"rows": rows, "terrainSHA256": mask["candidatePatch"]["sha256"],
          "aiCalls": 0, "modelGeometryChanges": 0, "publication": False})
    LOCAL.mkdir(parents=True, exist_ok=True)
    assets = LOCAL / "candidates/assets"
    assets.mkdir(parents=True, exist_ok=True)
    entries = []
    for row in (podium, tower):
        entry = row["candidate"]["entry"]
        source = row["candidate"]["path"]
        target = LOCAL / "candidates" / entry["asset"]
        shutil.copyfile(source, target)
        assert digest(target.read_bytes()) == entry["sha256"]
        entries.append(entry)
    catalogue = read(HERE / "accepted/government-xxl-20260911/catalogue.json")
    catalogue.update(models=entries, counts={"packedModels": 2})
    save(LOCAL / "candidates/catalogue.json", catalogue)
    save(LOCAL / "candidates/catalogue-index.json", {"models": 2, "catalogues": ["catalogue.json"]})
    save(LOCAL / "candidates/source-forms.json", {row["uid"]: row["source"] for row in (podium, tower)})
    save(LOCAL / "selection.json.gz", {"manifestSHA256": digest((ROOT / "3d-viewer/city/data/manifest.json").read_bytes()),
                                       "rows": [podium, tower]})
    neighbour = read(HERE / "local/government-xl-cainiao-shared-mask-20260927/cainiao-smart-gateway/neighbour-inputs.json.gz")
    save(LOCAL / "terrain-candidates.json", [{**neighbour["patches"][0], **mask["candidatePatch"]}])
    neighbour["candidateIds"] = [PODIUM, TOWER]
    neighbour["patches"] = read(LOCAL / "terrain-candidates.json")
    save(LOCAL / "neighbour-inputs.json.gz", neighbour)
    call(["node", str(HERE / "acceptance-metrics.mjs"), "--selection", rel(LOCAL / "selection.json.gz"),
          "--candidates", rel(LOCAL / "candidates"), "--terrain-candidates", rel(LOCAL / "terrain-candidates.json"),
          "--out", rel(LOCAL / "metrics.json")])
    call(["node", str(HERE.parent / "building-batch/validate_candidates.mjs"),
          "--candidates", rel(LOCAL / "candidates"), "--source-forms", rel(LOCAL / "candidates/source-forms.json"),
          "--terrain-candidates", rel(LOCAL / "terrain-candidates.json"),
          "--out", rel(LOCAL / "validation.json")], allowed=(0, 1))
    call(["node", str(HERE / "check-neighbours.mjs"), rel(LOCAL) + "/"])
    call(["node", str(HERE / "check-native-neighbours.mjs"), rel(LOCAL) + "/"])
    metric = {row["uid"]: row for row in read(LOCAL / "metrics.json")["rows"]}
    validation = {row["uid"]: row for row in read(LOCAL / "validation.json")["results"]}
    neighbors = read(LOCAL / "neighbour-checks.json")
    native = read(LOCAL / "native-neighbour-checks.json")
    print(json.dumps({"supportCoverage": coverage,
                      "foundation": {row["uid"]: {"strict": row["strictFoundationAccepted"],
                                                    "buriedUpward": row["foundation"]["fullyBuriedUpwardTriangles"]} for row in rows},
                      "metrics": {uid: {"missingTerrain": value.get("missingTerrain"),
                                         "minLowGap": value.get("minLowGap"), "maxLowGap": value.get("maxLowGap")}
                                  for uid, value in metric.items()},
                      "validation": {uid: value.get("concerns", []) for uid, value in validation.items()},
                      "blockedNeighbors": [uid for p in neighbors["patches"] for uid in p["blockedBy"]],
                      "blockedNative": native["blocked"], "resolvedNative": native["resolved"]}), flush=True)


if __name__ == "__main__":
    run()
