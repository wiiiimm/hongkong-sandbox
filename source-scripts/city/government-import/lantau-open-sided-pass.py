"""Stage the unchanged Discovery Bay open-sided source after native collision repair."""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE_BATCH = "government-lantau-final-14-20260921"
BATCH = "government-lantau-open-sided-20260921"
DOC = ROOT / "docs/astra-city/government-import" / BATCH
STAGE = HERE / "accepted" / BATCH
LOCAL = HERE / "local" / BATCH
UIDS = ("landsd/288285:0",)

def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith(".gz") else raw)

def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(gzip.compress(raw, mtime=0) if str(path).endswith(".gz") else raw)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def rel(path):
    return str(Path(path).relative_to(ROOT))

def main():
    probe = {row["uid"]: row for row in read(ROOT / "docs/astra-city/government-import" / SOURCE_BATCH / "selection.json.gz")["rows"]}
    validation = {row["uid"]: row for row in read(ROOT / "docs/astra-city/government-import" / SOURCE_BATCH / "validation.json")["results"]}
    metrics = {row["uid"]: row for row in read(ROOT / "docs/astra-city/government-import" / SOURCE_BATCH / "metrics.json")["rows"]}
    exact = {}
    for path in sorted((ROOT / "docs/astra-city/government-import").glob("government-*/exact-pass-results.json.gz")):
        for row in read(path)["rows"]:
            if row["uid"] in UIDS:
                assert row["uid"] not in exact
                exact[row["uid"]] = (path, row)
    assert set(exact) == set(UIDS)
    proof, rows, models, forms = [], [], [], []
    for uid in UIDS:
        row = json.loads(json.dumps(probe[uid]))
        path, source = exact[uid]
        identity, foundation = source["identity"], source["foundation"]
        assert identity["exactObjectAndCSUID"]
        assert identity["officialOverlapOfSmallerFootprint"] >= 0.95
        assert identity["officialFootprintCentroidDistanceM"] <= 3.25
        assert identity["targetCoveredBySourceProjection"] >= 0.57
        assert identity["sourceProjectionInsideTarget"] >= 0.99
        assert foundation["completeTerrainTriangles"] == foundation["triangles"]
        assert foundation["fullyBuriedUpwardTriangles"] == 0
        assert foundation["minimumGapM"] >= -1
        assert foundation["maximumGapM"] >= 3
        assert not source["suppressesBuildingUids"]
        entry = row["candidate"]["entry"]
        entry.update(priority="detail", placementReviewed=True, sourceIdentityReviewed=True,
                     identityReviewApproved=True, publicationApproved=False,
                     proceduralWindows=False, retainsBasicForm=True,
                     placementReview=("Exact object and Building CSUID. Official canopy lies entirely within the target; "
                                      "no upward source faces are fully buried. Current runtime terrain, picking and "
                                      "native source-surface collision pass after fixing the open-sided collision volume. Retain the basic form for foundation support. Unchanged source mesh."))
        source_asset = Path(row["candidate"]["path"])
        target_asset = STAGE / entry["asset"]
        target_asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_asset, target_asset)
        assert sha(target_asset) == entry["sha256"]
        row["candidate"]["path"] = str(target_asset)
        rows.append(row)
        models.append(entry)
        form = dict(row["source"]["building"])
        form["tile"] = Path(row["source"]["tile"]).stem
        forms.append(form)
        proof.append({"uid": uid, "sourceEvidence": rel(path), "sourceSHA256": entry["sha256"],
                      "identity": identity, "foundation": foundation,
                      "probeValidation": validation[uid], "probeMetrics": metrics[uid]})
    template = read(ROOT / "3d-viewer/city/data/official-models/government-discovery-bay-compute-20260921/catalogue.json")
    template.update(area="Discovery Bay unchanged open-sided government source",
                    loadingPolicy="Exact source, visible roofs, retained basic foundation, CPU and browser checked",
                    counts={"packedModels": len(models)}, models=models)
    save(STAGE / "catalogue.json", template)
    save(STAGE / "catalogue-index.json", {"models": len(models), "catalogues": ["catalogue.json"]})
    save(STAGE / "source-forms.json", forms)
    save(LOCAL / "source-forms.json", {row["uid"]: row["source"] for row in rows})
    save(DOC / "assembly-proof.json", {"policy": "One original open-sided mesh with verified source identity, visible roof clearance, native source collision and retained basic support.", "rows": proof, "aiCalls": 0, "geometryChanges": 0})
    selection = {"batch": BATCH, "rows": rows,
                 "manifestSHA256": sha(ROOT / "3d-viewer/city/data/manifest.json"), "aiCalls": 0}
    save(DOC / "selection.json.gz", selection)
    save(DOC / "terrain-candidates.json", [])
    commands = [
        ["node", str(HERE / "acceptance-metrics.mjs"), "--selection", rel(DOC / "selection.json.gz"),
         "--candidates", rel(STAGE), "--terrain-candidates", rel(DOC / "terrain-candidates.json"),
         "--out", rel(DOC / "metrics.json")],
        ["node", str(HERE.parent / "building-batch/validate_candidates.mjs"), "--candidates", rel(STAGE),
         "--source-forms", rel(LOCAL / "source-forms.json"), "--out", rel(DOC / "validation.json")],
    ]
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)
    metrics2 = read(DOC / "metrics.json")
    validation2 = read(DOC / "validation.json")
    assert validation2["checksPassed"] == validation2["loaderAccepted"] == 1
    assert validation2["exceptions"] == 0
    assert len(metrics2["rows"]) == 1 and all(not row.get("error") and row["sourcePreserved"] and row["missingTerrain"] == 0 and row["maxSamplerDelta"] <= 0.004 for row in metrics2["rows"])
    destination = f"city/data/official-models/{BATCH}/catalogue.json"
    save(STAGE / "plan.json", {"areas": [{"area": template["area"], "catalogue": rel(STAGE / "catalogue.json"), "destination": destination}]})
    save(STAGE / "browser-config.json", {"stage": rel(STAGE) + "/", "doc": rel(DOC) + "/",
         "catalogueURL": destination, "terrain": [], "fitBox": True, "browserUids": list(UIDS),
         "failureTestUids": list(UIDS)})
    save(DOC / "result.json", {"batch": BATCH, "models": 1, "installedCandidates": list(UIDS),
         "held": [], "failures": [], "representativeUids": list(UIDS),
         "supportedSamplerUids": [], "missingRenderedGroundUids": [],
         "assemblyProofSHA256": sha(DOC / "assembly-proof.json"),
         "metricsSHA256": sha(DOC / "metrics.json"),
         "validationSHA256": sha(DOC / "validation.json"),
         "aiCalls": 0, "geometryChanges": 0, "modelGeometryChanges": 0, "publication": False})
    print(json.dumps({"candidates": 1, "checksPassed": 1, "aiCalls": 0, "geometryChanges": 0}))

if __name__ == "__main__":
    main()
