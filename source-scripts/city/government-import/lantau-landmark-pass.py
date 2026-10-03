"""Process 16 named high-complexity Lantau landmarks; exact government sources, no AI."""
import argparse
import collections
import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BATCH = "government-lantau-landmarks-16-20260916"
UIDS = tuple(
    "landsd/" + value + ":0"
    for value in (
        "107386 108263 108265 108736 108741 108805 176915 178555 "
        "187251 246229 246471 271137 296766 337237 72608 76821"
    ).split()
)

spec = importlib.util.spec_from_file_location("xl_pass", HERE / "xl-pass.py")
xl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xl)
xl.BATCH = BATCH
xl.LIMIT = len(UIDS)
xl.LOCAL = HERE / "local" / BATCH
xl.DOC = ROOT / "docs/astra-city/government-import" / BATCH


def current_sources(manifest):
    sources = {}
    for tile in manifest["tiles"]:
        path = ROOT / "3d-viewer" / tile["url"]
        raw = path.read_bytes()
        for building in json.loads(raw)["buildings"]:
            if building["uid"] in UIDS:
                sources[building["uid"]] = {
                    "building": building,
                    "tile": tile["url"],
                    "tileSHA256": xl.digest(raw),
                }
    assert set(sources) == set(UIDS), sorted(set(UIDS) - set(sources))
    return sources


def installed_models(manifest):
    installed = {}
    for url in manifest.get("officialModelCatalogues", []):
        for entry in xl.read(ROOT / "3d-viewer" / url)["models"]:
            installed[entry["uid"]] = entry
    return installed


def prepare():
    if xl.LOCAL.exists():
        raise ValueError("Frozen landmark batch exists; resume with recover or check")
    manifest_path = ROOT / "3d-viewer/city/data/manifest.json"
    manifest = xl.read(manifest_path)
    sources = current_sources(manifest)
    assert not set(UIDS) & set(installed_models(manifest)), "Landmark model is already installed"

    with xl.connect() as connection:
        connection.execute("SET TRANSACTION READ ONLY")
        inventory = connection.execute(
            """
            SELECT cache_key,model_id,viewer_uid,size_group,triangles
            FROM astra_modelling.native_model_sizes
            WHERE run_id=%s AND viewer_uid=ANY(%s)
            ORDER BY viewer_uid
            """,
            (xl.NATIVE_RUN, list(UIDS)),
        ).fetchall()
        assert len(inventory) == len(UIDS) and {row[2] for row in inventory} == set(UIDS)
        native_rows = connection.execute(
            """
            SELECT r.cache_key,r.result_sha,i.sheet,x
            FROM astra_modelling.native_stage_results r
            JOIN astra_modelling.native_stage_inputs i USING(cache_key)
            CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') x
            WHERE r.cache_key=ANY(%s) AND x->>'modelId'=ANY(%s)
            """,
            ([row[0] for row in inventory], [row[1] for row in inventory]),
        ).fetchall()
        reviews = dict(
            connection.execute(
                """
                SELECT DISTINCT ON(uid) uid,
                       jsonb_build_object('state',review_state,'sha',source_sha256)
                FROM astra_modelling.model_reviews
                WHERE uid=ANY(%s)
                ORDER BY uid,updated_at DESC
                """,
                (list(UIDS),),
            )
        )

    native = {
        (cache_key, model["modelId"]): {
            "cacheKey": cache_key,
            "resultSha": result_sha,
            "sheet": sheet,
            "model": model,
        }
        for cache_key, result_sha, sheet, model in native_rows
    }
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
        if previous and previous["state"] in ("source-unavailable", "identity-unresolved"):
            concerns.append("existing-source-or-identity-hold")
        rows.append({
            "modelId": model_id,
            "uid": uid,
            "native": outcome,
            "source": sources[uid],
            "previousReview": previous,
            "installedProof": None,
            "humanStatus": "in-process",
            "reasons": [],
            "selectionConcerns": sorted(set(concerns)),
            "name": building.get("name"),
            "nameZh": building.get("zh"),
            "sourceSHA256": model["asset"]["sha256"],
            "triangles": triangles,
            "sizeGroup": size_group,
        })
    order = {uid: index for index, uid in enumerate(UIDS)}
    rows.sort(key=lambda row: order[row["uid"]])
    frozen = {
        "batch": BATCH,
        "nativeRun": xl.NATIVE_RUN,
        "rows": rows,
        "manifestSHA256": xl.h(manifest_path),
        "selectionPolicy": "Named uninstalled Lantau XL/L landmarks from the refreshed 2026-09-16 inventory",
        "sizeGroups": dict(collections.Counter(row["sizeGroup"] for row in rows)),
        "selectionLimit": len(UIDS),
        "sourceCommit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "aiCalls": 0,
    }
    xl.save(xl.LOCAL / "selection.json.gz", frozen)
    xl.save(xl.DOC / "selection.json.gz", frozen)
    xl.save(
        xl.LOCAL / "recovery-inputs.json.gz",
        {
            "nativeRun": xl.NATIVE_RUN,
            "rows": list(UIDS),
            "sources": {row["uid"]: row["source"] for row in rows},
            "native": [row["native"] for row in rows],
        },
    )
    cache = xl.LOCAL / "recovered/assets"
    cache.mkdir(parents=True, exist_ok=True)
    reused = 0
    search_roots = (
        HERE.parent / "enhancement-screening/local/shapes/assets",
        HERE.parent / "enhancement-screening/local/shape-5000/assets",
        HERE / "local/government-xl-50-20260913/recovered/assets",
    )
    for row in rows:
        destination = cache / (row["sourceSHA256"] + ".glb.gz")
        for root in search_roots:
            source = root / destination.name
            if source.exists() and xl.h(source) == row["sourceSHA256"]:
                shutil.copyfile(source, destination)
                reused += 1
                break
    print(json.dumps({
        "scope": len(rows),
        "sizeGroups": frozen["sizeGroups"],
        "sheets": len({row["native"]["sheet"] for row in rows}),
        "preseededExactAssets": reused,
        "selectionConcerns": dict(collections.Counter(reason for row in rows for reason in row["selectionConcerns"])),
        "aiCalls": 0,
    }), flush=True)


def check():
    frozen = xl.read(xl.LOCAL / "selection.json.gz")
    receipt = xl.reservations.claim(
        "codex-lantau-landmarks-" + str(uuid.uuid4()),
        ["building:" + row["uid"] for row in frozen["rows"]],
        batch=BATCH,
    )
    assert receipt["ok"], "Existing source owner; no takeover"
    xl.save(xl.LOCAL / "reservation.json", json.loads(json.dumps(receipt["reservation"], default=str)))
    xl.command([
        sys.executable,
        str(HERE.parent / "shared-modelling/reservations.py"),
        "run",
        "--lease-file",
        str(xl.LOCAL / "reservation.json"),
        "--",
        sys.executable,
        __file__,
        "check-owned",
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "recover", "check", "check-owned"))
    phase = parser.parse_args().phase
    {"prepare": prepare, "recover": xl.recover, "check": check, "check-owned": xl.check_owned}[phase]()


if __name__ == "__main__":
    main()
