"""Recover exact government terrain members for XL terrain-contact holds.

This is an input-acquisition pass only. It does not alter model geometry,
approve terrain patches, or install models.
"""

import json
import sys
import uuid
import zipfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from run import ROOT, HERE, connect, digest, read, save, jobs, reservations, Jsonb, dict_row

sys.path.insert(0, str(HERE.parent / "enhancement-screening"))
from shape_prepare import canonical_bytes
sys.path.insert(0, str(HERE.parent / "citywide-source"))
from discover import scan
sys.path.insert(0, str(HERE.parent / "citywide-native"))
from download import acquire
from convert import _convert_one


BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
LOCAL = HERE / "local/government-xl-terrain-sources-20260924"
REPORT = BASE / "terrain-source-recovery-20260924.json"
NEON = BASE / "terrain-source-recovery-20260924-neon.json"


def member_identity(model):
    return sorted((part["name"], part["crc32"], part["decodedBytes"], part["compressedBytes"])
                  for part in model["members"])


def work(sheet, pinned, source_rows):
    folder = LOCAL / "sheets" / sheet
    uids = sorted(row["uid"] for row in source_rows)
    try:
        current, _ = scan({"SHEETNO": sheet, "Format_glTF": pinned["sourceURL"],
                           "REVISIONDATE": pinned["revision"]}, folder / "directory")
        revised = (current["etag"], current["directorySHA256"]) != (pinned["etag"], pinned["directorySHA256"])
        if revised:
            earlier = {model["modelId"]: model for model in pinned["models"]}
            latest = {model["modelId"]: model for model in current["models"]}
            if any(row["modelId"] not in earlier or row["modelId"] not in latest or
                   member_identity(earlier[row["modelId"]]) != member_identity(latest[row["modelId"]])
                   for row in source_rows):
                return {"sheet": sheet, "uids": uids, "state": "source-model-revision-changed",
                        "pinnedDirectorySHA256": pinned["directorySHA256"],
                        "currentDirectorySHA256": current["directorySHA256"]}
            current["models"] = [latest[row["modelId"]] for row in source_rows]
        else:
            current["models"] = []
        proof = acquire(current, folder / "directory/zip-directory.bin", folder / "original",
                        include_terrain=True)
        terrain = [entry for entry in proof["entries"] if entry["name"].startswith("TERRAIN")]
        if not any(entry["name"].endswith(".gltf") for entry in terrain):
            return {"sheet": sheet, "uids": uids, "state": "source-terrain-missing",
                    "directorySHA256": current["directorySHA256"]}
        with zipfile.ZipFile(folder / "original" / (sheet + ".zip")) as archive:
            if revised:
                packed = folder / "packed"
                packed.mkdir(exist_ok=True)
                for row in source_rows:
                    converted = _convert_one(archive, archive.getinfo(row["native"]["model"]["sourceEntry"]),
                                             folder / "decoded", packed, {}, {"modelId": row["modelId"]})
                    raw = canonical_bytes((packed / converted["asset"]["asset"]).read_bytes(),
                                          row["sourceSHA256"])
                    assert len(raw) == row["native"]["model"]["asset"]["bytes"]
            for entry in terrain:
                name = entry["name"]
                if not name.endswith((".gltf", ".bin")):
                    continue
                path = folder / "terrain" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(archive.read(name))
                assert digest(path.read_bytes()) == entry["sha256"]
        state = "revised-terrain-recovered-exact-model" if revised else "exact-terrain-recovered"
        save(folder / "recovery.json", {"source": {"directorySHA256": current["directorySHA256"]},
                                        "state": state, "archiveSHA256": proof["sha256"]})
        return {"sheet": sheet, "uids": uids, "state": state,
                "directorySHA256": current["directorySHA256"],
                "pinnedDirectorySHA256": pinned["directorySHA256"],
                "archiveSHA256": proof["sha256"], "terrainFiles": len(terrain),
                "terrainBytes": sum(entry["bytes"] for entry in terrain)}
    except Exception as error:
        return {"sheet": sheet, "uids": uids, "state": "source-recovery-error",
                "errorType": type(error).__name__}


def run():
    reconciled = read(BASE / "reconciliation.json.gz")
    selection = {row["uid"]: row for row in read(BASE / "selection.json.gz")["rows"]}
    by_sheet = defaultdict(list)
    for row in reconciled["rows"]:
        if row["primaryHold"] == "terrain-contact":
            by_sheet[row["sourceSheet"]].append(row["uid"])
    assert sum(map(len, by_sheet.values())) == 83 and len(by_sheet) == 59
    with connect() as connection:
        connection.execute("SET TRANSACTION READ ONLY")
        pinned = dict(connection.execute(
            "SELECT DISTINCT ON(sheet) sheet,result FROM astra_modelling.city_source_directories "
            "WHERE sheet=ANY(%s) ORDER BY sheet,created_at DESC", (list(by_sheet),)).fetchall())
    assert set(pinned) == set(by_sheet)
    uncached = {}
    for sheet, uids in by_sheet.items():
        candidates = [path for path in (HERE / "local").glob(f"*/sheets/{sheet}/terrain/**/*.gltf")
                      if LOCAL not in path.parents]
        matched = False
        for path in candidates:
            proof_path = next((parent / "recovery.json" for parent in path.parents
                               if parent.name == sheet and (parent / "recovery.json").exists()), None)
            if proof_path:
                proof = read(proof_path)
                source = proof.get("source") or proof.get("download") or {}
                matched |= source.get("directorySHA256") == pinned[sheet]["directorySHA256"]
        if not matched:
            uncached[sheet] = uids
    rows = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(work, sheet, pinned[sheet], [selection[uid] for uid in uids]): sheet
                   for sheet, uids in sorted(uncached.items())}
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            print(json.dumps({"sheet": row["sheet"], "state": row["state"],
                              "completed": len(rows), "total": len(uncached)}), flush=True)
    rows.sort(key=lambda row: row["sheet"])
    report = {"batch": "government-xl-terrain-sources-20260924", "stage": "source-terrain-acquisition-v1",
              "terrainContactModels": 83, "sheets": 59, "alreadyCachedPinnedSheets": 59 - len(uncached),
              "attemptedSheets": len(uncached), "counts": dict(Counter(row["state"] for row in rows)),
              "rows": rows, "aiCalls": 0, "geometryChanges": 0, "publication": False,
              "qualification": "Terrain acquisition does not clear model contact or neighbour checks. Changed revisions remain held until exact source identity is established."}
    save(REPORT, report)
    print(json.dumps({"counts": report["counts"], "report": str(REPORT.relative_to(ROOT))}), flush=True)


def sync():
    report = read(REPORT)
    assert report["counts"] == {"exact-terrain-recovered": 32,
                                 "revised-terrain-recovered-exact-model": 5}
    claim = reservations.claim("codex-xl-terrain-source-" + str(uuid.uuid4()),
                               ["building:" + uid for row in report["rows"] for uid in row["uids"]],
                               batch=report["batch"])
    assert claim["ok"], claim
    receipt = claim["reservation"]
    try:
        evidence = {"path": str(REPORT.relative_to(ROOT)), "sha256": digest(REPORT.read_bytes())}
        job_id = jobs.enqueue(report["batch"], report["stage"], evidence)
        job = jobs.claim(report["batch"], receipt["owner"], [report["stage"]], lease_seconds=1800)
        assert job and job["id"] == job_id
        result = {**report, "evidence": evidence}
        with connect() as connection:
            connection.row_factory = dict_row
            connection.execute("SELECT pg_advisory_xact_lock(%s)", (reservations.LOCK_ID,))
            assert reservations._current(connection, receipt)
            assert connection.execute(
                "UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,"
                "lease_until=NULL,updated_at=clock_timestamp() "
                "WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
                (Jsonb(result), job_id, job["owner"], job["token"])).rowcount == 1
        with connect() as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            assert connection.execute("SELECT result FROM astra_modelling.jobs WHERE id=%s",
                                      (job_id,)).fetchone()[0] == result
        save(NEON, {"jobId": job_id, "evidenceSHA256": evidence["sha256"], "resultVerified": True})
        print(json.dumps({"jobId": job_id, "verified": True}), flush=True)
    finally:
        reservations.release(receipt)


if __name__ == "__main__":
    sync() if len(sys.argv) > 1 and sys.argv[1] == "sync" else run()
