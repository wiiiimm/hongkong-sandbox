"""Process all matched, uninstalled Pui O / Chi Ma Wan government forms; never AI."""
from __future__ import annotations

import argparse
import collections
import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BATCH = "government-pui-o-chi-ma-wan-362-20260916"
LOCAL = HERE / "local" / BATCH
DOC = ROOT / "docs/astra-city/government-import" / BATCH
INVENTORY = ROOT / "docs/astra-city/lantau-government-model-inventory-20260914/buildings.csv"

spec = importlib.util.spec_from_file_location("xl_pass", HERE / "xl-pass.py")
xl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xl)
xl.BATCH = BATCH
xl.LOCAL = LOCAL
xl.DOC = DOC


def target_uids():
    with INVENTORY.open() as stream:
        rows = list(csv.DictReader(stream))
    return tuple(row["uid"] for row in rows
                 if row["sectionId"] == "10.7"
                 and row["governmentAvailable"] == "True"
                 and row["actionableState"] == "enhancement-required")


UIDS = target_uids()
assert len(UIDS) == 362 and len(set(UIDS)) == len(UIDS)
xl.LIMIT = len(UIDS)


def current_sources(manifest):
    wanted = set(UIDS)
    result = {}
    for tile in manifest["tiles"]:
        path = ROOT / "3d-viewer" / tile["url"]
        raw = path.read_bytes()
        for building in json.loads(raw)["buildings"]:
            if building["uid"] in wanted:
                result[building["uid"]] = {
                    "building": building, "tile": tile["url"],
                    "tileSHA256": xl.digest(raw),
                }
    assert set(result) == wanted, sorted(wanted - set(result))
    return result


def installed_models(manifest):
    result = {}
    for url in manifest.get("officialModelCatalogues", []):
        for entry in xl.read(ROOT / "3d-viewer" / url)["models"]:
            result[entry["uid"]] = entry
    return result


def prepare():
    if LOCAL.exists():
        raise ValueError("Frozen batch exists; resume with recover or check")
    manifest_path = ROOT / "3d-viewer/city/data/manifest.json"
    manifest = xl.read(manifest_path)
    sources = current_sources(manifest)
    assert not (set(UIDS) & set(installed_models(manifest)))
    with xl.connect() as connection:
        connection.execute("SET TRANSACTION READ ONLY")
        inventory = connection.execute('''
            SELECT cache_key,model_id,viewer_uid,size_group,triangles
            FROM astra_modelling.native_model_sizes
            WHERE run_id=%s AND viewer_uid=ANY(%s)
            ORDER BY viewer_uid
        ''', (xl.NATIVE_RUN, list(UIDS))).fetchall()
        assert len(inventory) == len(UIDS) and {row[2] for row in inventory} == set(UIDS)
        keys = [row[0] for row in inventory]
        model_ids = [row[1] for row in inventory]
        native_rows = connection.execute('''
            SELECT r.cache_key,r.result_sha,i.sheet,x
            FROM astra_modelling.native_stage_results r
            JOIN astra_modelling.native_stage_inputs i USING(cache_key)
            CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') x
            WHERE r.cache_key=ANY(%s) AND x->>'modelId'=ANY(%s)
        ''', (keys, model_ids)).fetchall()
        reviews = dict(connection.execute('''
            SELECT DISTINCT ON(uid) uid,jsonb_build_object('state',review_state,'sha',source_sha256)
            FROM astra_modelling.model_reviews
            WHERE uid=ANY(%s)
            ORDER BY uid,updated_at DESC
        ''', (list(UIDS),)))
    native = {(key, model["modelId"]): {
        "cacheKey": key, "resultSha": result_sha, "sheet": sheet, "model": model,
    } for key, result_sha, sheet, model in native_rows}
    assert set(native) == {(row[0], row[1]) for row in inventory}
    rows = []
    for cache_key, model_id, uid, size_group, triangles in inventory:
        outcome = native[cache_key, model_id]
        model = outcome["model"]
        entry = model.get("candidate")
        building = sources[uid]["building"]
        assert model["state"] == "packed-needs-placement-review" and entry and entry["uid"] == uid
        assert entry["buildingCSUID"] == building.get("buildingCSUID")
        assert entry["objectId"] == building.get("objectId")
        assert entry["recordedBaseHeight"] == building.get("baseHeightHKPD")
        assert entry["recordedTopHeight"] == building.get("topHeightHKPD")
        concerns = []
        if entry["overlapOfSmallerFootprint"] < .98:
            concerns.append("strict-identity-overlap")
        if entry["footprintCentroidDistanceMetres"] > 1:
            concerns.append("strict-identity-centroid")
        previous = reviews.get(uid)
        if previous and previous["state"] in ("held", "source-unavailable", "identity-unresolved"):
            concerns.append("existing-review-requires-resolution")
        rows.append({
            "modelId": model_id, "uid": uid, "native": outcome, "source": sources[uid],
            "previousReview": previous, "installedProof": None, "humanStatus": "in-process",
            "reasons": [], "selectionConcerns": sorted(set(concerns)),
            "name": building.get("name"), "sourceSHA256": model["asset"]["sha256"],
            "triangles": triangles, "sizeGroup": size_group,
        })
    order = {uid: index for index, uid in enumerate(UIDS)}
    rows.sort(key=lambda row: order[row["uid"]])
    frozen = {
        "batch": BATCH, "nativeRun": xl.NATIVE_RUN, "rows": rows,
        "manifestSHA256": xl.h(manifest_path),
        "selectionPolicy": "All matched uninstalled forms in review section 10.7 Pui O and Chi Ma Wan",
        "sizeGroups": dict(collections.Counter(row["sizeGroup"] for row in rows)),
        "selectionLimit": len(UIDS),
        "sourceInventory": str(INVENTORY.relative_to(ROOT)),
        "sourceInventorySHA256": xl.h(INVENTORY),
        "sourceCommit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "aiCalls": 0,
    }
    xl.save(LOCAL / "selection.json.gz", frozen)
    xl.save(DOC / "selection.json.gz", frozen)
    xl.save(LOCAL / "recovery-inputs.json.gz", {
        "nativeRun": xl.NATIVE_RUN,
        "rows": list(UIDS),
        "sources": {row["uid"]: row["source"] for row in rows},
        "native": [row["native"] for row in rows],
    })
    (LOCAL / "recovered/assets").mkdir(parents=True, exist_ok=True)
    print(json.dumps({
        "scope": len(rows), "sizeGroups": frozen["sizeGroups"],
        "sourceSheets": dict(collections.Counter(row["native"]["sheet"] for row in rows)),
        "selectionConcerns": dict(collections.Counter(
            concern for row in rows for concern in row["selectionConcerns"])),
        "aiCalls": 0,
    }), flush=True)


def reserve_and_check():
    frozen = xl.read(LOCAL / "selection.json.gz")
    receipt = xl.reservations.claim(
        "codex-pui-o-chi-ma-wan-" + str(uuid.uuid4()),
        ["building:" + row["uid"] for row in frozen["rows"]], batch=BATCH, ttl=3600,
    )
    assert receipt["ok"], "Existing source owner; no takeover"
    xl.save(LOCAL / "reservation.json", json.loads(json.dumps(receipt["reservation"], default=str)))
    xl.command([
        sys.executable, str(HERE.parent / "shared-modelling/reservations.py"), "run",
        "--lease-file", str(LOCAL / "reservation.json"), "--",
        sys.executable, __file__, "check-owned",
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "recover", "check", "check-owned"))
    phase = parser.parse_args().phase
    {"prepare": prepare, "recover": xl.recover,
     "check": reserve_and_check, "check-owned": xl.check_owned}[phase]()


if __name__ == "__main__":
    main()
