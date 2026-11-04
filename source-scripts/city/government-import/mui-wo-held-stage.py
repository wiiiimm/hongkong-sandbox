"""Stage the 13 script-qualified Mui Wo sources for runtime checks; no AI."""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE_BATCH = "government-mui-wo-23-20260914"
BATCH = "government-mui-wo-held-13-20260915"
SOURCE = ROOT / "docs/astra-city/government-import" / SOURCE_BATCH / "check-selection.json.gz"
PROOF = ROOT / "docs/astra-city/government-import/government-mui-wo-16-20260915/script-pass-results.json.gz"
DOC = ROOT / "docs/astra-city/government-import/government-mui-wo-16-20260915/staging"
LOCAL = HERE / "local" / SOURCE_BATCH
STAGE = HERE / "accepted" / BATCH


def read(path):
    path = Path(path); raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def save(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == ".gz" else raw)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return str(Path(path).relative_to(ROOT))


def call(args, allowed=(0,)):
    result = subprocess.run(args, cwd=ROOT)
    assert result.returncode in allowed, (args, result.returncode)


def main():
    proof = read(PROOF)
    accepted = {row["uid"]: row for row in proof["rows"] if row["publicationCandidate"]}
    held = {row["uid"]: row for row in proof["rows"] if not row["publicationCandidate"]}
    assert len(accepted) == 13 and len(held) == 3 and proof["aiCalls"] == proof["modelGeometryChanges"] == 0
    selection = read(SOURCE)
    source_rows = {row["uid"]: row for row in selection["rows"]}
    template = read(LOCAL / "recovered/catalogue.json")
    models, runtime_rows, forms = [], [], []
    STAGE.mkdir(parents=True, exist_ok=True)
    for uid in sorted(accepted):
        proof_row = accepted[uid]; source_row = source_rows[uid]
        entry = dict(source_row["candidate"]["entry"])
        entry.update(
            priority="detail", placementReviewed=True, sourceIdentityReviewed=True,
            identityReviewApproved=True, publicationApproved=False, proceduralWindows=False,
            placementReview=(
                "Exact government object ID and Building CSUID with a unique viewer match. "
                "Full-face native terrain, projected fit and mobile source-budget checks are scripted. "
                + ("The mapped basic extrusion remains as the missing lower mass beneath this government upper shell. " if proof_row["retainsBasicForm"] else "")
                + "Original model geometry and placement are unchanged; no AI modelling or review."
            ),
        )
        if proof_row["retainsBasicForm"]:
            entry["retainsBasicForm"] = True
        if proof_row["suppressesBuildingUids"]:
            entry["suppressesBuildingUids"] = proof_row["suppressesBuildingUids"]
        source_asset = Path(source_row["candidate"]["path"])
        target_asset = STAGE / entry["asset"]
        target_asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_asset, target_asset)
        assert digest(target_asset) == entry["sha256"] and target_asset.stat().st_size == entry["bytes"]
        models.append(entry)
        runtime = json.loads(json.dumps(source_row))
        runtime["candidate"]["path"] = str(target_asset)
        runtime["candidate"]["entry"] = entry
        runtime_rows.append(runtime)
        form = dict(source_row["source"]["building"]); form["tile"] = Path(source_row["source"]["tile"]).stem
        forms.append(form)
    template.update(
        area="Mui Wo script-completed government sources · September 2026",
        loadingPolicy="Exact original sources accepted after deterministic identity, terrain, retained-support and runtime checks",
        counts={"packedModels": len(models)}, models=models,
    )
    save(STAGE / "catalogue.json", template)
    save(STAGE / "catalogue-index.json", {"models": len(models), "catalogues": ["catalogue.json"]})
    save(STAGE / "source-forms.json", forms)
    save(LOCAL / "held-13-source-forms.json", {row["uid"]: row["source"] for row in runtime_rows})
    runtime_selection = dict(selection)
    runtime_selection.update(batch=BATCH, rows=runtime_rows, manifestSHA256=digest(ROOT / "3d-viewer/city/data/manifest.json"), aiCalls=0)
    save(DOC / "selection.json.gz", runtime_selection)
    save(DOC / "terrain-candidates.json", [])
    call(["node", str(HERE / "acceptance-metrics.mjs"), "--selection", relative(DOC / "selection.json.gz"), "--candidates", relative(STAGE), "--terrain-candidates", relative(DOC / "terrain-candidates.json"), "--out", relative(DOC / "metrics.json")])
    call(["node", str(HERE.parent / "building-batch/validate_candidates.mjs"), "--candidates", relative(STAGE), "--source-forms", relative(LOCAL / "held-13-source-forms.json"), "--out", relative(DOC / "validation.json")], allowed=(0, 1))
    metrics = read(DOC / "metrics.json"); validation = read(DOC / "validation.json")
    failures = []
    mobile = metrics["profiles"]["mobile"]
    for row in metrics["rows"]:
        if row.get("error") or not row.get("sourcePreserved") or row.get("missingTerrain"):
            failures.append({"uid": row["uid"], "reason": "source-integrity-or-current-terrain"})
        if row.get("maxSamplerDelta", 0) > .004:
            failures.append({"uid": row["uid"], "reason": "terrain-sampler-disagreement"})
        if any(row["budget"][key] > mobile[key] for key in ("triangles", "geometryBytes", "residentBytes")):
            failures.append({"uid": row["uid"], "reason": "mobile-runtime-budget"})
    allowed = {"sampled-ground-gap-below-model-bottom", "sampled-terrain-above-model-bottom", "sampled-highest-roof-below-terrain"}
    for row in validation["results"]:
        if row["outcome"] == "validation-exception": failures.append({"uid": row["uid"], "reason": "runtime-validation-exception"})
        failures.extend({"uid": row["uid"], "reason": reason} for reason in row.get("concerns", []) if reason not in allowed)
    result = {
        "batch": BATCH, "models": len(models), "held": sorted(held), "failures": failures,
        "sourcePreserved": all(row.get("sourcePreserved") for row in metrics["rows"]),
        "validationExceptions": validation["exceptions"], "aiCalls": 0, "modelGeometryChanges": 0,
        "publication": False, "proofSHA256": digest(PROOF), "metricsSHA256": digest(DOC / "metrics.json"),
        "validationSHA256": digest(DOC / "validation.json"),
    }
    save(DOC / "result.json", result)
    destination = "city/data/official-models/government-mui-wo-held-13-20260915/catalogue.json"
    save(STAGE / "plan.json", {"areas": [{"area": template["area"], "catalogue": relative(STAGE / "catalogue.json"), "destination": destination}]})
    save(STAGE / "browser-config.json", {"stage": relative(STAGE) + "/", "doc": relative(DOC) + "/", "catalogueURL": destination, "terrain": [], "fitBox": True, "browserUids": sorted(accepted), "failureTestUids": [sorted(accepted)[0]]})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
