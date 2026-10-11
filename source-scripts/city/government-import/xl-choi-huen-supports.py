"""Recover exact Choi Huen assembly components from the pinned government run; never AI."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run import ROOT, HERE, NATIVE_RUN, connect, digest, read, save

sys.path.insert(0, str(HERE.parent / "enhancement-screening"))
import shape_prepare

UIDS = {
    "landsd/116574:0",
    "landsd/145664:0",
    "landsd/329933:0",
    "landsd/330096:0",
}
DOC = ROOT / "docs/astra-city/government-import/government-xl-50-20260913/second-pass/third-pass/terrain-choi-huen"
LOCAL = HERE / "local/government-xl-50-second-20260913/third-pass-terrain-choi-huen-supports"


def main():
    manifest = read(ROOT / "3d-viewer/city/data/manifest.json")
    sources = {}
    for tile in manifest["tiles"]:
        path = ROOT / "3d-viewer" / tile["url"]
        raw = path.read_bytes()
        for building in json.loads(raw)["buildings"]:
            if building["uid"] in UIDS:
                sources[building["uid"]] = {
                    "building": building,
                    "tile": tile["url"],
                    "tileSHA256": digest(raw),
                }
    assert set(sources) == UIDS

    with connect() as connection:
        connection.execute("SET TRANSACTION READ ONLY")
        rows = connection.execute(
            """SELECT i.sheet,r.cache_key,r.result_sha,x
            FROM astra_modelling.native_stage_members m
            JOIN astra_modelling.native_stage_results r USING(cache_key)
            JOIN astra_modelling.native_stage_inputs i USING(cache_key)
            CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') x
            WHERE m.run_id=%s
              AND EXISTS(
                SELECT 1
                FROM jsonb_array_elements(x->'matching'->'viewerMatches') v
                WHERE v->>'uid'=ANY(%s)
              )
            ORDER BY i.sheet,x->>'modelId'""",
            (NATIVE_RUN, sorted(UIDS)),
        ).fetchall()

    native = [
        {"sheet": sheet, "cacheKey": key, "resultSha": sha, "model": model}
        for sheet, key, sha, model in rows
    ]
    matches = [
        match["uid"]
        for item in native
        for match in item["model"].get("matching", {}).get("viewerMatches", [])
        if match["uid"] in UIDS
    ]
    assert len(native) == len(UIDS) and sorted(matches) == sorted(UIDS)
    assert len({item["cacheKey"] for item in native}) == 1
    assert len({item["resultSha"] for item in native}) == 1

    inputs = {
        "nativeRun": NATIVE_RUN,
        "rows": sorted(UIDS),
        "requestedUids": sorted(UIDS),
        "sources": sources,
        "native": native,
    }
    save(LOCAL / "inputs.json.gz", inputs)
    result = shape_prepare.prepare(
        LOCAL / "inputs.json.gz",
        LOCAL,
        allow_source=True,
        workers=1,
        env_file=ROOT / ".env.modelling",
    )
    assert len(result["rows"]) == len(UIDS) and not result["errors"]

    by_uid = {
        match["uid"]: item
        for item in native
        for match in item["model"].get("matching", {}).get("viewerMatches", [])
        if match["uid"] in UIDS
    }
    runtime_rows = []
    for row in result["rows"]:
        entry = row["candidate"]["entry"]
        entry.update(placementReviewed=False, publicationApproved=False)
        runtime_rows.append({
            **row,
            "source": sources[row["uid"]],
            "native": by_uid[row["uid"]],
        })
    save(LOCAL / "runtime.json.gz", {"rows": runtime_rows, "aiCalls": 0, "publication": False})

    evidence = {
        "uids": sorted(UIDS),
        "sheet": next(iter({item["sheet"] for item in native})),
        "cacheKey": native[0]["cacheKey"],
        "resultSha": native[0]["resultSha"],
        "models": [
            {
                "uid": row["uid"],
                "modelId": row["candidate"]["entry"]["modelId"],
                "sourceSHA256": row["candidate"]["entry"]["sha256"],
                "triangles": row["candidate"]["entry"]["triangles"],
            }
            for row in runtime_rows
        ],
        "methods": result["methods"],
        "sourceFallbackEnabled": result["sourceFallbackEnabled"],
        "aiCalls": 0,
        "modelGeometryChanges": 0,
        "publication": False,
    }
    save(DOC / "support-source-recovery.json", evidence)
    print(json.dumps(evidence), flush=True)


if __name__ == "__main__":
    main()
