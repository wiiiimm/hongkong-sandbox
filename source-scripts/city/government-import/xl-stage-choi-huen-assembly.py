"""Stage five unchanged Choi Huen government models with bounded native terrain; never AI."""
import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import Polygon

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("second", HERE / "xl-second-pass.py")
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
import native_patch_resolution as patch_resolution

ROOT = s.ROOT
read, save, h, rel = s.read, s.save, s.h, s.rel
DOC = s.DOC / "third-pass/terrain-choi-huen"
LOCAL = s.LOCAL / "third-pass-terrain-choi-huen-assembly"
RECOVERY = s.LOCAL / "third-pass-terrain-choi-huen-supports/runtime.json.gz"
STAGE = HERE / "accepted/government-xl-choi-huen-assembly-20260914"
BATCH = "government-xl-choi-huen-assembly-20260914"
PRIMARY = "landsd/50009:0"
RETAINED = "landsd/266748:0"
IDS = {PRIMARY, "landsd/116574:0", "landsd/145664:0", "landsd/329933:0", "landsd/330096:0"}
REPRESENTATIVE = [PRIMARY, "landsd/329933:0", "landsd/330096:0"]
MOBILE = {"count": 24, "geometryBytes": 48 * 1024 * 1024, "residentBytes": 128 * 1024 * 1024, "triangles": 450000}


def call(args, allowed=(0,)):
    result = subprocess.run(args, cwd=ROOT)
    assert result.returncode in allowed, (args, result.returncode)


def flattened(row):
    entry = row["candidate"]["entry"]
    return {**row, "sourceSHA256": entry["sha256"], "modelId": entry["modelId"], "triangles": entry["triangles"]}


def rows():
    frozen = read(s.DOC / "runtime-selection.json.gz")
    primary = next(row for row in frozen["rows"] if row["uid"] == PRIMARY)
    recovered = read(RECOVERY)
    assert recovered["aiCalls"] == 0 and not recovered["publication"]
    selected = [primary, *recovered["rows"]]
    assert {row["uid"] for row in selected} == IDS and len(selected) == 5
    return frozen, selected


def budget(entries):
    result = {"count": len(entries), "geometryBytes": 0, "residentBytes": 0, "triangles": 0}
    for entry in entries:
        collision = entry["indexedVertices"] * 24 + entry["triangles"] * (12 + 48 + 64)
        result["geometryBytes"] += entry["decodedGeometryBytes"]
        result["residentBytes"] += entry["decodedGeometryBytes"] * 2 + collision + 65536
        result["triangles"] += entry["triangles"]
    result["mobilePassed"] = all(result[key] <= MOBILE[key] for key in MOBILE)
    return result


def start():
    frozen, selected = rows()
    original_inputs = read(DOC / "neighbour-inputs.json.gz")
    original_inputs["candidateIds"] = sorted(IDS)
    original_inputs["manifestSHA256"] = h(ROOT / "3d-viewer/city/data/manifest.json")
    save(DOC / "assembly-selection.json.gz", {**frozen, "manifestSHA256": original_inputs["manifestSHA256"], "rows": selected})
    save(DOC / "assembly-neighbour-inputs.json.gz", original_inputs)
    resources = {"building:" + uid for uid in IDS}
    resources |= {("building:" if row["building"]["uid"].startswith("landsd/") else "source-form:") + row["building"]["uid"] for row in original_inputs["rows"]}
    claim = s.reservations.claim("codex-xl-choi-huen-" + str(uuid.uuid4()), sorted(resources), batch=BATCH)
    assert claim["ok"], claim
    save(LOCAL / "reservation.json", json.loads(json.dumps(claim["reservation"], default=str)))
    s.call([sys.executable, str(HERE.parent / "shared-modelling/reservations.py"), "run", "--lease-file", str(LOCAL / "reservation.json"), "--", sys.executable, __file__, "owned"])


def owned():
    assert s.reservations.owns(read(LOCAL / "reservation.json"))
    selection = read(DOC / "assembly-selection.json.gz")
    neighbour_inputs = read(DOC / "assembly-neighbour-inputs.json.gz")
    assert h(ROOT / "3d-viewer/city/data/manifest.json") == selection["manifestSHA256"] == neighbour_inputs["manifestSHA256"]
    selected = selection["rows"]

    support = read(DOC / "assembly-support.json")
    assert support["passed"] and support["aiCalls"] == support["modelGeometryChanges"] == 0
    assert {row["uid"] for row in support["rows"]} == IDS - {PRIMARY}

    old_entry = read(DOC / "terrain-candidates.json")[0]
    old_path = ROOT / old_entry["path"]
    assert h(old_path) == old_entry["sha256"]
    patch = read(old_path)
    patch["id"] = "government-native-choi-huen-assembly"
    patch["meta"]["targetUids"] = sorted(IDS)

    triangles = {row["uid"]: s.glb_triangles(flattened(row)) for row in selected}
    source_projection = shapely.union_all([
        shapely.union_all(shapely.polygons(value[:, :, [0, 2]]))
        for value in triangles.values()
    ])
    retained = next(row["building"] for row in neighbour_inputs["rows"] if row["building"]["uid"] == RETAINED)
    retained_polygon = Polygon(retained["rings"][0], retained["rings"][1:])
    protected = retained_polygon.buffer(.01, join_style="mitre")
    parent = read(ROOT / "3d-viewer/city/data/terrain.json")
    sampler = s.resolution.terrain.fine.DemSampler(parent, rendered=True)
    clearance_rows = []
    for uid, value in triangles.items():
        projections = shapely.polygons(value[:, :, [0, 2]])
        indexes = np.flatnonzero(shapely.intersects(projections, protected) & (shapely.area(projections) > 1e-10))
        for index in indexes:
            overlap = projections[index].intersection(protected)
            if overlap.area <= 1e-12:
                continue
            point = overlap.representative_point()
            a, b, c = value[index]
            normal = np.cross(b - a, c - a)
            if abs(normal[1]) <= 1e-10:
                continue
            source_y = a[1] - (normal[0] * (point.x - a[0]) + normal[2] * (point.y - a[2])) / normal[1]
            parent_y = sampler.ground(point.x, point.y)
            clearance_rows.append({
                "uid": uid, "overlapAreaM2": float(overlap.area), "x": point.x, "z": point.y,
                "sourceY": float(source_y), "parentY": parent_y, "clearanceM": float(source_y - parent_y),
            })
    assert clearance_rows and min(row["clearanceM"] for row in clearance_rows) > 8.5
    proof = patch_resolution.preserve_parent_under_projection(patch, old_entry["bounds"], protected, sampler)
    proof.update({
        "retainedUid": RETAINED,
        "retainedFootprintAreaM2": retained_polygon.area,
        "boundaryBufferM": .01,
        "sourceIntersectionAreaM2": float(protected.intersection(source_projection).area),
        "sourceIntersectionFacetChecks": len(clearance_rows),
        "minimumSourceClearanceAboveParentM": min(row["clearanceM"] for row in clearance_rows),
        "clearanceRows": clearance_rows,
        "clearancePolicy": "The complete current parent surface is retained under the unrelated neighbour. At every source facet that projects into this tiny boundary overlap, the unchanged government surface is at least 8.5m above that parent terrain.",
    })
    patch["nativeMesh"]["source"]["protectedParentProjection"] = proof
    patch_resolution.fill_parent_only_holes(patch, parent, old_entry["bounds"], source_projection, sampler)
    s.resolution.validate_patch(patch, parent)
    patch_path = LOCAL / (patch["id"] + ".json")
    save(patch_path, patch)
    patch_entry = {
        "path": rel(patch_path), "sha256": h(patch_path), "uids": sorted(IDS),
        "bounds": old_entry["bounds"], "triangles": len(patch["nativeMesh"]["index"]) // 3,
    }
    save(DOC / "assembly-terrain-candidates.json", [patch_entry])
    neighbour_inputs["patches"] = [patch_entry]
    save(DOC / "neighbour-inputs.json.gz", neighbour_inputs)
    save(DOC / "assembly-terrain-resolution.json", {
        "patch": patch_entry,
        "retainedNeighbour": proof,
        "sourceProjectionAreaM2": float(source_projection.area),
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    })

    template = read(HERE / "accepted/government-xxl-20260911/catalogue.json")
    entries, source_forms, browser_forms, identity_rows = [], {}, [] , []
    for row in selected:
        entry = dict(row["candidate"]["entry"])
        building = row["source"]["building"]
        exact = entry["objectId"] == building["objectId"] and entry["buildingCSUID"] == building["buildingCSUID"]
        embedded = entry["modelId"][1:11] == entry["buildingCSUID"][:10]
        coarse = entry["overlapOfSmallerFootprint"] >= .995 and entry["footprintCentroidDistanceMetres"] <= 2.25
        identity_rows.append({
            "uid": row["uid"], "exactObjectAndCSUID": exact, "modelIdEmbedsCSUID": embedded,
            "overlapOfSmallerFootprint": entry["overlapOfSmallerFootprint"],
            "footprintCentroidDistanceMetres": entry["footprintCentroidDistanceMetres"],
            "passed": bool(exact and embedded and (coarse or row["uid"] == PRIMARY)),
        })
        entry.update(
            label=building.get("name") or entry["modelId"], priority="landmark",
            placementReviewed=True, sourceIdentityReviewed=True, identityReviewApproved=True,
            placementReview="Exact UID/CSUID-matched unchanged government source in the Choi Huen House assembly. Native terrain, component support and neighbour preservation are validated as one atomic source-sheet group; no AI modelling, review, simplification or model geometry edits.",
        )
        if row["uid"] != PRIMARY:
            entry["supportDependencies"] = [{"uid": PRIMARY, "state": "candidate", "csuid": next(item["candidate"]["entry"]["buildingCSUID"] for item in selected if item["uid"] == PRIMARY)}]
        source_asset = Path(row["candidate"]["path"])
        assert h(source_asset) == entry["sha256"]
        target = STAGE / entry["asset"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_asset, target)
        entries.append(entry)
        source_forms[row["uid"]] = row["source"]
        form = dict(building)
        form["tile"] = Path(row["source"]["tile"]).stem
        browser_forms.append(form)
    assert all(row["passed"] for row in identity_rows)
    primary_final = next(row for row in read(s.DOC / "final-script-pass/results.json.gz")["rows"] if row["uid"] == PRIMARY)
    foundation = primary_final["foundation"]
    primary_passed = (
        primary_final["identityScriptAccepted"] and primary_final["foundationScriptAccepted"]
        and foundation["completeTerrainTriangles"] == foundation["triangles"]
        and foundation["fullyBuriedTriangles"] == foundation["fullyBuriedUpwardTriangles"] == 0
    )
    assert primary_passed
    save(DOC / "assembly-identity.json", {
        "rows": identity_rows,
        "primaryDetailedProof": {"passed": primary_passed, "identity": primary_final["identity"], "foundation": foundation},
        "sourceSheet": "11-NE-12B", "samePinnedDirectory": True, "aiCalls": 0, "modelGeometryChanges": 0,
    })

    group_budget = budget(entries)
    assert group_budget["mobilePassed"], group_budget
    save(DOC / "assembly-budget.json", {"measured": group_budget, "mobileLimits": MOBILE, "aiCalls": 0})
    template.update(area="Choi Huen House original government source assembly", counts={"packedModels": len(entries)}, models=entries)
    save(STAGE / "catalogue.json", template)
    save(STAGE / "catalogue-index.json", {"models": len(entries), "catalogues": ["catalogue.json"]})
    save(STAGE / "source-forms.json", browser_forms)
    save(LOCAL / "source-forms.json", source_forms)

    save(DOC / "terrain-candidates.json", [patch_entry])
    call(["node", str(HERE / "acceptance-metrics.mjs"), "--selection", rel(DOC / "assembly-selection.json.gz"), "--candidates", rel(STAGE), "--terrain-candidates", rel(DOC / "terrain-candidates.json"), "--out", rel(DOC / "assembly-metrics.json")])
    call(["node", str(HERE.parent / "building-batch/validate_candidates.mjs"), "--candidates", rel(STAGE), "--source-forms", rel(LOCAL / "source-forms.json"), "--terrain-candidates", rel(DOC / "terrain-candidates.json"), "--out", rel(DOC / "assembly-validation.json")], allowed=(0, 1))
    call(["node", str(HERE / "check-neighbours.mjs"), rel(DOC) + "/"])

    metrics = read(DOC / "assembly-metrics.json")
    reasons = []
    for metric in metrics["rows"]:
        if metric.get("error") or not metric.get("sourcePreserved") or metric.get("missingTerrain"):
            reasons.append(metric["uid"] + ":source-integrity-or-terrain-coverage")
        if metric.get("maxSamplerDelta", 0) > .004:
            reasons.append(metric["uid"] + ":rendered-terrain-disagreement")
        if metric.get("budget") and any(metric["budget"][key] > metrics["profiles"]["mobile"][key] for key in ("triangles", "geometryBytes", "residentBytes")):
            reasons.append(metric["uid"] + ":mobile-runtime-budget")
    allowed_contact = {"sampled-ground-gap-below-model-bottom", "sampled-terrain-above-model-bottom"}
    for result in read(DOC / "assembly-validation.json")["results"]:
        if result["outcome"] == "validation-exception":
            reasons.append(result["uid"] + ":runtime-validation-exception")
        allowed = allowed_contact if result["uid"] != PRIMARY else {"sampled-terrain-above-model-bottom"}
        reasons.extend(result["uid"] + ":" + concern for concern in result.get("concerns", []) if concern not in allowed)
    blocked = read(DOC / "neighbour-checks.json")["patches"][0]["blockedBy"]
    if blocked:
        reasons.append("terrain-correction-regresses-unrelated-neighbours")
    result = {
        "uid": PRIMARY, "models": len(entries), "policy": "original-government-choi-huen-assembly-v1",
        "passed": not reasons, "reasons": sorted(set(reasons)), "blockedNeighbours": blocked,
        "patch": patch_entry, "groupBudget": group_budget,
        "identitySHA256": h(DOC / "assembly-identity.json"), "supportContactSHA256": h(DOC / "assembly-support.json"),
        "sourceRecoverySHA256": h(DOC / "support-source-recovery.json"),
        "terrainResolutionSHA256": h(DOC / "assembly-terrain-resolution.json"),
        "aiCalls": 0, "modelGeometryChanges": 0, "publication": False,
    }
    save(DOC / "assembly-result.json", result)
    if result["passed"]:
        staged_patch = STAGE / patch_path.name
        shutil.copyfile(patch_path, staged_patch)
        terrain = {"source": rel(staged_patch), "sha256": h(staged_patch), "destination": "city/data/" + staged_patch.name, "resolution": patch["cell"], "area": "Choi Huen original native terrain"}
        destination = "city/data/official-models/" + BATCH + "/catalogue.json"
        save(STAGE / "plan.json", {"areas": [{"area": template["area"], "catalogue": rel(STAGE / "catalogue.json"), "destination": destination}], "topLevelTerrainPatches": [terrain]})
        save(STAGE / "browser-config.json", {"stage": rel(STAGE) + "/", "doc": rel(DOC) + "/", "catalogueURL": destination, "terrain": [terrain], "fitBox": True, "browserUids": REPRESENTATIVE, "failureTestUids": [PRIMARY]})
    print(json.dumps(result))


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 else start()
