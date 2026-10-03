"""Finish the surface-clear portion of the held XL batch with deterministic checks only."""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DOC = ROOT / "docs/astra-city/government-import/government-xl-50-20260913/final-compute-pass/surface-clear"
LOCAL = HERE / "local/government-xl-held-surface-20260914"
STAGE = HERE / "accepted/government-xl-held-surface-20260914"
BATCH = "government-xl-held-surface-20260914"
SOURCE_DOC = ROOT / "docs/astra-city/government-import/government-xl-50-20260913/second-pass"
SOURCE_LOCAL = HERE / "local/government-xl-50-second-20260913"

UIDS = (
    "landsd/270867:0", "landsd/148321:0", "landsd/253890:0", "landsd/253891:0",
    "landsd/270427:0", "landsd/21915:0", "landsd/109530:0",
    "landsd/337014:0", "landsd/304700:0", "landsd/307295:0", "landsd/229481:0",
    "landsd/175935:0", "landsd/60113:0",
)

sys.path.insert(0, str(HERE.parent / "shared-modelling"))
import reservations  # noqa: E402


def read(path: Path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def save(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    temp.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == ".gz" else raw)
    temp.replace(path)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def call(args, allowed=(0,)) -> None:
    result = subprocess.run(args, cwd=ROOT)
    assert result.returncode in allowed, (args, result.returncode)


def current_installed_uids() -> set[str]:
    manifest = read(ROOT / "3d-viewer/city/data/manifest.json")
    result = set()
    for url in manifest["officialModelCatalogues"]:
        result.update(model["uid"] for model in read(ROOT / "3d-viewer" / url)["models"])
    return result


def build_evidence() -> tuple[list[dict], list[dict]]:
    runtime = {row["uid"]: row for row in read(SOURCE_DOC / "runtime-selection.json.gz")["rows"]}
    proofs = {row["uid"]: row for row in read(SOURCE_DOC / "final-script-pass/results.json.gz")["rows"]}
    installed = current_installed_uids()
    assert not (set(UIDS) & installed), "Surface-pass model was installed after selection"
    rows = []
    stage_rows = []
    for uid in UIDS:
        row = runtime[uid]
        proof = proofs[uid]
        identity = proof["identity"]
        foundation = proof["foundation"]
        runtime_proof = proof["runtime"]
        entry = dict(row["candidate"]["entry"])
        source_maximum = entry["worldBounds"][1][1]

        assert proof["scriptedWorkComplete"]
        assert identity["exactObjectAndCSUID"]
        assert identity["targetCoveredBySourceProjection"] >= 0.95
        assert runtime_proof["sourcePreserved"] and runtime_proof["mobileBudgetPassed"]
        assert foundation["completeTerrainTriangles"] == foundation["triangles"]
        assert foundation["fullyBuriedUpwardTriangles"] == 0
        assert foundation["fullyBuriedAreaFraction"] <= 0.001

        suppressions = []
        retained = []
        relationships = []
        for form in identity["intersectingForms"]:
            other_uid = form["uid"]
            if other_uid == uid:
                continue
            fully_covered_low_form = (
                form["fractionOfForm"] >= 0.95
                and form["top"] <= source_maximum + 1.0
                and form["base"] < source_maximum
            )
            action = "suppress-covered-low-form" if fully_covered_low_form else "retain-support-or-adjacent-form"
            (suppressions if fully_covered_low_form else retained).append(other_uid)
            relationships.append({
                "uid": other_uid,
                "action": action,
                "fractionOfForm": form["fractionOfForm"],
                "intersectionAreaM2": form["intersectionAreaM2"],
                "baseHeightHKPD": form["base"],
                "topHeightHKPD": form["top"],
                "sourceMaximumHeightHKPD": source_maximum,
                "sameParent": form["sameParent"],
                "sharedOsmReference": form["sharedOsmReference"],
            })

        suppressions = sorted(set(suppressions))
        retained = sorted(set(retained) - set(suppressions))
        entry.update(
            priority="landmark",
            placementReviewed=True,
            sourceIdentityReviewed=True,
            identityReviewApproved=True,
            publicationApproved=False,
            proceduralWindows=False,
            placementReview=(
                "Exact unchanged government source matched by object ID and Building CSUID. Full target "
                "coverage, complete terrain sampling, source integrity and mobile runtime budgets passed. "
                "Intersecting city forms were classified from exact projected coverage and vertical ranges; "
                "covered low forms are reversibly suppressed and taller support/adjacent forms remain visible. "
                "No AI review, remodelling, simplification or model geometry edit was used."
            ),
        )
        if suppressions:
            entry["suppressesBuildingUids"] = suppressions

        asset = STAGE / entry["asset"]
        asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(row["candidate"]["path"], asset)
        assert digest(asset) == entry["sha256"]
        form = dict(row["source"]["building"])
        form["tile"] = Path(row["source"]["tile"]).stem
        stage_rows.append({"entry": entry, "form": form, "source": row["source"], "runtime": row})
        rows.append({
            "uid": uid,
            "name": proof.get("name") or entry["label"],
            "sourceSHA256": entry["sha256"],
            "sourceSheet": proof["sourceSheet"],
            "triangles": entry["triangles"],
            "targetCoverage": identity["targetCoveredBySourceProjection"],
            "sourceExcessFraction": identity["sourceExcessFraction"],
            "sourceExcessMaximumDistanceM": identity["sourceExcessMaximumDistanceFromTargetM"],
            "fullyBuriedAreaFraction": foundation["fullyBuriedAreaFraction"],
            "fullyBuriedUpwardTriangles": foundation["fullyBuriedUpwardTriangles"],
            "suppressions": suppressions,
            "retainedForms": retained,
            "relationships": relationships,
            "aiCalls": 0,
            "modelGeometryChanges": 0,
        })
    return rows, stage_rows


def start() -> None:
    resources = ["building:" + uid for uid in UIDS]
    claim = reservations.claim("codex-xl-held-surface-" + str(uuid.uuid4()), resources, batch=BATCH)
    assert claim["ok"], claim
    save(LOCAL / "reservation.json", json.loads(json.dumps(claim["reservation"], default=str)))
    call([
        sys.executable, str(HERE.parent / "shared-modelling/reservations.py"), "run",
        "--lease-file", str(LOCAL / "reservation.json"), "--", sys.executable, __file__, "owned",
    ])


def owned() -> None:
    assert reservations.owns(read(LOCAL / "reservation.json"))
    evidence, stage_rows = build_evidence()
    template = read(HERE / "accepted/government-xxl-20260911/catalogue.json")
    template.update(
        area="XL held surface-clear government sources",
        loadingPolicy="Exact original sources accepted by deterministic identity, surface, assembly and runtime checks",
        counts={"packedModels": len(stage_rows)},
        models=[row["entry"] for row in stage_rows],
    )
    save(STAGE / "catalogue.json", template)
    save(STAGE / "catalogue-index.json", {"models": len(stage_rows), "catalogues": ["catalogue.json"]})
    save(STAGE / "source-forms.json", [row["form"] for row in stage_rows])
    save(LOCAL / "source-forms.json", {row["entry"]["uid"]: row["source"] for row in stage_rows})
    selection = read(SOURCE_DOC / "runtime-selection.json.gz")
    selection.update(
        batch=BATCH,
        manifestSHA256=digest(ROOT / "3d-viewer/city/data/manifest.json"),
        rows=[row["runtime"] for row in stage_rows],
        aiCalls=0,
    )
    save(DOC / "selection.json.gz", selection)
    save(DOC / "assembly-map.json", {
        "policy": (
            "For an exact object/CSUID source with at least 95% target coverage, suppress only another form "
            "whose footprint is at least 95% covered and whose recorded top does not extend more than one "
            "metre above the exact source. Retain taller towers, supports and partial boundary intersections."
        ),
        "rows": evidence,
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    })
    save(DOC / "terrain-candidates.json", [])
    call([
        "node", str(HERE / "acceptance-metrics.mjs"), "--selection", relative(DOC / "selection.json.gz"),
        "--candidates", relative(STAGE), "--terrain-candidates", relative(DOC / "terrain-candidates.json"),
        "--out", relative(DOC / "metrics.json"),
    ])
    call([
        "node", str(HERE.parent / "building-batch/validate_candidates.mjs"),
        "--candidates", relative(STAGE), "--source-forms", relative(LOCAL / "source-forms.json"),
        "--out", relative(DOC / "validation.json"),
    ], allowed=(0, 1))
    metrics = read(DOC / "metrics.json")
    validation = read(DOC / "validation.json")
    failures = []
    allowed_concerns = {"sampled-ground-gap-below-model-bottom", "sampled-terrain-above-model-bottom"}
    for metric in metrics["rows"]:
        if metric.get("error") or not metric.get("sourcePreserved") or metric.get("missingTerrain"):
            failures.append({"uid": metric["uid"], "reason": "source-integrity-or-terrain"})
        if metric.get("maxSamplerDelta", 0) > 0.004:
            failures.append({"uid": metric["uid"], "reason": "terrain-sampler-disagreement"})
        if any(metric["budget"][key] > metrics["profiles"]["mobile"][key] for key in ("triangles", "geometryBytes", "residentBytes")):
            failures.append({"uid": metric["uid"], "reason": "mobile-runtime-budget"})
    for result in validation["results"]:
        if result["outcome"] == "validation-exception":
            failures.append({"uid": result["uid"], "reason": "runtime-validation-exception"})
        for concern in result.get("concerns", []):
            if concern not in allowed_concerns:
                failures.append({"uid": result["uid"], "reason": concern})
    result = {
        "batch": BATCH,
        "policy": "original-government-xl-held-surface-compute-v1",
        "passed": not failures,
        "models": len(stage_rows),
        "failures": failures,
        "assemblyMapSHA256": digest(DOC / "assembly-map.json"),
        "metricsSHA256": digest(DOC / "metrics.json"),
        "validationSHA256": digest(DOC / "validation.json"),
        "aiCalls": 0,
        "modelGeometryChanges": 0,
        "publication": False,
    }
    save(DOC / "result.json", result)
    if result["passed"]:
        destination = "city/data/official-models/government-xl-held-surface-20260914/catalogue.json"
        save(STAGE / "plan.json", {"areas": [{
            "area": "XL held surface-clear government sources",
            "catalogue": relative(STAGE / "catalogue.json"),
            "destination": destination,
        }]})
        manifest = read(ROOT / "3d-viewer/city/data/manifest.json")
        live_detail = {model["uid"] for url in manifest["officialModelCatalogues"] for model in read(ROOT / "3d-viewer" / url)["models"]}
        retained = {row["uid"]: [uid for uid in row["retainedForms"] if uid not in live_detail] for row in evidence if any(uid not in live_detail for uid in row["retainedForms"])}
        save(STAGE / "browser-config.json", {
            "stage": relative(STAGE) + "/",
            "doc": relative(DOC) + "/",
            "catalogueURL": destination,
            "terrain": [],
            "fitBox": True,
            "fitBoxByModel": {"landsd/337014:0": False},
            "browserUids": list(UIDS),
            "failureTestUids": list(UIDS),
            "retainedBuildingUidsByModel": retained,
        })
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 and sys.argv[1] == "owned" else start()
