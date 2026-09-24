"""Stage the 14 remaining Lantau government sources for read-only runtime diagnosis."""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BATCH = "government-lantau-final-14-20260921"
DOC = ROOT / "docs/astra-city/government-import" / BATCH
STAGE = HERE / "local" / BATCH / "candidates"
SOURCE_FORMS = HERE / "local" / BATCH / "source-forms.json"
INVENTORY = ROOT / "docs/astra-city/lantau-government-model-inventory-20260921/review-states.json"

def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith(".gz") else raw)

def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(gzip.compress(raw, mtime=0) if str(path).endswith(".gz") else raw)

def relative(path):
    return str(Path(path).relative_to(ROOT))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    wanted = {row["uid"] for row in read(INVENTORY)["rows"]}
    assert len(wanted) == 14
    selections = {}
    for path in sorted((ROOT / "docs/astra-city/government-import").glob("government-*/check-selection.json.gz")):
        for row in read(path)["rows"]:
            if row["uid"] in wanted:
                assert row["uid"] not in selections
                selections[row["uid"]] = (path, row)
    assert set(selections) == wanted
    template = read(ROOT / "3d-viewer/city/data/official-models/government-discovery-bay-compute-20260921/catalogue.json")
    rows, models, forms = [], [], {}
    for uid in sorted(wanted):
        path, original = selections[uid]
        row = json.loads(json.dumps(original))
        entry = row["candidate"]["entry"]
        entry.update(priority="detail", placementReviewed=True, sourceIdentityReviewed=True,
                     identityReviewApproved=True, publicationApproved=False,
                     proceduralWindows=False, retainsBasicForm=True,
                     placementReview="Exact unchanged government source staged for deterministic validation only.")
        source = Path(row["candidate"]["path"])
        target = STAGE / entry["asset"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        assert sha(target) == entry["sha256"]
        row["candidate"]["path"] = str(target)
        rows.append(row)
        models.append(entry)
        forms[uid] = row["source"]
    template.update(area="Lantau final 14 diagnostic", loadingPolicy="Read-only exact-source probe",
                    counts={"packedModels": len(models)}, models=models)
    save(STAGE / "catalogue.json", template)
    save(STAGE / "catalogue-index.json", {"models": len(models), "catalogues": ["catalogue.json"]})
    save(SOURCE_FORMS, forms)
    save(DOC / "selection.json.gz", {"batch": BATCH, "rows": rows,
                                    "manifestSHA256": sha(ROOT / "3d-viewer/city/data/manifest.json"), "aiCalls": 0})
    save(DOC / "terrain-candidates.json", [])
    commands = [
        ["node", str(HERE / "acceptance-metrics.mjs"), "--selection", relative(DOC / "selection.json.gz"),
         "--candidates", relative(STAGE), "--terrain-candidates", relative(DOC / "terrain-candidates.json"),
         "--out", relative(DOC / "metrics.json")],
        ["node", str(HERE.parent / "building-batch/validate_candidates.mjs"), "--candidates", relative(STAGE),
         "--source-forms", relative(SOURCE_FORMS), "--out", relative(DOC / "validation.json")],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=ROOT)
        assert result.returncode in (0, 1), (command, result.returncode)
    metrics = read(DOC / "metrics.json")
    validation = read(DOC / "validation.json")
    report = {"batch": BATCH, "metrics": len(metrics["rows"]), "validation": validation["models"],
              "checksPassed": validation["checksPassed"], "exceptions": validation["exceptions"],
              "errors": [{"uid": row["uid"], "error": row.get("error")} for row in validation["results"]
                         if row["outcome"] == "validation-exception"],
              "sourceGeometryChanges": 0, "aiCalls": 0, "publication": False}
    save(DOC / "probe-summary.json", report)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
