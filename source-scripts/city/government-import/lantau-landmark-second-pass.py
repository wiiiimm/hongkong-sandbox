"""Run exact-form and native source-terrain diagnostics for the Lantau landmark batch."""
import argparse
import importlib.util
import json
import subprocess
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BATCH = "government-lantau-landmarks-16-second-20260916"
BASE = ROOT / "docs/astra-city/government-import/government-lantau-landmarks-16-20260916"
DOC = BASE / "second-pass"
LOCAL = HERE / "local" / BATCH

spec = importlib.util.spec_from_file_location("xl_second", HERE / "xl-second-pass.py")
second = importlib.util.module_from_spec(spec)
spec.loader.exec_module(second)
second.BATCH = BATCH
second.BASE = BASE
second.DOC = DOC
second.LOCAL = LOCAL


def prepare():
    assert not (DOC / "selection.json.gz").exists(), "Frozen second pass exists; resume it explicitly"
    original = second.read(BASE / "selection.json.gz")
    first = second.read(BASE / "results.json.gz")
    held = {row["modelId"] for row in first["rows"] if row["humanStatus"] == "held-unknown"}
    rows = [row for row in original["rows"] if row["modelId"] in held]
    assert len(rows) == len(original["rows"]) == 16

    references = {row["modelId"][1:11] for row in rows}
    forms = []
    manifest = second.read(ROOT / "3d-viewer/city/data/manifest.json")
    for tile in manifest["tiles"]:
        path = ROOT / "3d-viewer" / tile["url"]
        raw = path.read_bytes()
        for building in json.loads(raw)["buildings"]:
            if (building.get("buildingCSUID") or "")[:10] in references:
                forms.append({"building": building, "tile": tile["url"], "tileSHA256": second.digest(raw)})
    for row in rows:
        row["diagnosticSourceCandidates"] = second.exact_forms(row["native"]["model"], forms)

    with second.connect() as connection:
        connection.execute("SET TRANSACTION READ ONLY")
        actual = dict(
            connection.execute(
                """
                SELECT r.cache_key,r.result_sha
                FROM astra_modelling.native_stage_results r
                JOIN astra_modelling.native_stage_members m USING(cache_key)
                WHERE m.run_id=%s AND r.cache_key=ANY(%s)
                """,
                (second.NATIVE_RUN, [row["native"]["cacheKey"] for row in rows]),
            )
        )
        metadata = dict(
            connection.execute(
                """
                SELECT DISTINCT ON(sheet) sheet,result-'models'
                FROM astra_modelling.city_source_directories
                WHERE sheet=ANY(%s)
                ORDER BY sheet,created_at DESC
                """,
                (sorted({row["native"]["sheet"] for row in rows}),),
            )
        )
    assert all(actual[row["native"]["cacheKey"]] == row["native"]["resultSha"] for row in rows)
    assert set(metadata) == {row["native"]["sheet"] for row in rows}

    frozen = {
        **original,
        "batch": BATCH,
        "rows": rows,
        "manifestSHA256": second.h(ROOT / "3d-viewer/city/data/manifest.json"),
        "previousResultSHA256": second.h(BASE / "results.json.gz"),
        "sourceCommit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "previousInstalled": 0,
        "aiCalls": 0,
    }
    second.save(DOC / "selection.json.gz", frozen)
    second.save(LOCAL / "source-directories.json", metadata)
    print(json.dumps({
        "selected": len(rows),
        "sheets": len(metadata),
        "exactFormCandidates": [
            {"uid": row["uid"], "modelId": row["modelId"], "count": len(row["diagnosticSourceCandidates"])}
            for row in rows
        ],
        "aiCalls": 0,
    }), flush=True)


def run():
    frozen = second.read(DOC / "selection.json.gz")
    resources = {"native-model:" + row["native"]["cacheKey"] + ":" + row["modelId"] for row in frozen["rows"]}
    resources |= {
        "building:" + source["building"]["uid"]
        for row in frozen["rows"]
        for source in row["diagnosticSourceCandidates"]
    }
    claim = second.reservations.claim(
        "codex-lantau-landmarks-second-" + str(uuid.uuid4()),
        sorted(resources),
        batch=BATCH,
    )
    assert claim["ok"], "Existing source owner; no takeover"
    second.save(LOCAL / "reservation.json", json.loads(json.dumps(claim["reservation"], default=str)))
    second.call([
        sys.executable,
        str(HERE.parent / "shared-modelling/reservations.py"),
        "run",
        "--lease-file",
        str(LOCAL / "reservation.json"),
        "--",
        sys.executable,
        __file__,
        "owned",
    ])


def complete_context():
    diagnostics = second.read(DOC / "diagnostics.json")
    assert diagnostics["complete"] and len(diagnostics["rows"]) == 16
    affected = [
        row["modelId"]
        for row in diagnostics["rows"]
        if "native-terrain-coverage" in row["native"].get("reasons", [])
    ]
    assert affected == [], "Adjacent terrain sheets must be acquired before classification"
    second.save(DOC / "adjacent-terrain-plan.json", {
        "selectionSHA256": second.h(DOC / "selection.json.gz"),
        "diagnosticsSHA256": second.h(DOC / "diagnostics.json"),
        "extraSheets": [],
        "affectedModels": [],
        "manifestSHA256": second.read(DOC / "selection.json.gz")["manifestSHA256"],
        "qualification": "All 16 models have complete terrain coverage from their seven pinned source sheets.",
        "aiCalls": 0,
    })
    second.save(DOC / "adjacent-terrain-results.json", {
        "rows": [],
        "complete": True,
        "sources": [],
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    })
    print(json.dumps({"complete": True, "modelsNeedingAdjacentSheets": 0, "aiCalls": 0}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "run", "owned", "complete-context"))
    phase = parser.parse_args().phase
    {"prepare": prepare, "run": run, "owned": second.owned, "complete-context": complete_context}[phase]()


if __name__ == "__main__":
    main()
