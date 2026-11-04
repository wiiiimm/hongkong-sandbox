"""Recover XL models from changed ZIPs only when model members are byte-identical."""

import json
import subprocess
import sys
import uuid
import zipfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from run import ROOT, HERE, read, save, digest, connect, reservations

sys.path.insert(0, str(HERE.parent / "enhancement-screening"))
import shape_prepare
sys.path.insert(0, str(HERE.parent / "citywide-native"))
from download import acquire
from convert import _convert_one

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
LOCAL = HERE / "local/government-xl-source-revision-20260924"
BATCH = "government-xl-source-revision-20260924"
FIRST = HERE / "local/government-xl-remaining-20260923/recovered"
HELD = HERE / "local/government-xl-remaining-held-20260923/recovered"


def sha(path):
    return digest(Path(path).read_bytes())


def member_identity(model):
    return sorted((part["name"], part["crc32"], part["decodedBytes"])
                  for part in model["members"])


def call(args):
    subprocess.run(args, cwd=ROOT, check=True)


def start():
    selection = {row["uid"]: row for row in read(BASE / "selection.json.gz")["rows"]}
    errors = {}
    for folder in (FIRST, HELD):
        errors.update(read(folder / "geometry-inputs.json")["errors"])
    uids = sorted(uid for uid, error in errors.items() if error == "ValueError: Source revision changed")
    assert len(uids) == 18
    claim = reservations.claim("codex-xl-source-revision-" + str(uuid.uuid4()),
                               ["building:" + uid for uid in uids], batch=BATCH)
    assert claim["ok"], claim
    save(LOCAL / "reservation.json", json.loads(json.dumps(claim["reservation"], default=str)))
    call([sys.executable, str(HERE.parent / "shared-modelling/reservations.py"),
          "run", "--lease-file", str(LOCAL / "reservation.json"), "--",
          sys.executable, __file__, "owned"])


def work(sheet, rows, current, prior):
    folder = LOCAL / "sheets" / sheet
    folder.mkdir(parents=True, exist_ok=True)
    old = {model["modelId"]: model for model in prior["models"]}
    new = {model["modelId"]: model for model in current["models"]}
    eligible = []
    outcomes = []
    for row in rows:
        uid, model_id = row["uid"], row["modelId"]
        earlier, latest = old.get(model_id), new.get(model_id)
        if not latest:
            outcomes.append({"uid": uid, "state": "source-model-missing-in-current-revision",
                             "sourceSheet": sheet, "sourceSHA256": row["sourceSHA256"]})
        elif not earlier or member_identity(earlier) != member_identity(latest):
            outcomes.append({"uid": uid, "state": "source-model-members-changed",
                             "sourceSheet": sheet, "sourceSHA256": row["sourceSHA256"]})
        else:
            eligible.append(row)
    if not eligible:
        return outcomes
    # The scanner's current directory and ETag are frozen in the local result.
    # acquire verifies that exact archive before the ZIP member is converted.
    directory_file = row["directoryFile"]
    acquired = acquire(current, directory_file, folder / "original")
    archive = folder / "original" / f"{sheet}.zip"
    assert archive.exists()
    (folder / "packed").mkdir(exist_ok=True)
    with zipfile.ZipFile(archive) as zipped:
        for row in eligible:
            uid = row["uid"]
            asset = LOCAL / "recovered/assets" / (row["sourceSHA256"] + ".glb.gz")
            asset.parent.mkdir(parents=True, exist_ok=True)
            try:
                entry = row["sourceEntry"]
                # CRC and decoded length from both directory snapshots are
                # checked again by ZipFile while extracting the model.
                converted = _convert_one(zipped, zipped.getinfo(entry),
                                         folder / "decoded", folder / "packed", {},
                                         {"modelId": row["modelId"]})
                packed = folder / "packed" / converted["asset"]["asset"]
                raw = shape_prepare.canonical_bytes(packed.read_bytes(), row["sourceSHA256"])
                assert len(raw) == row["sourceBytes"]
                asset.write_bytes(raw)
                outcomes.append({"uid": uid, "state": "exact-source-recovered",
                                 "sourceSheet": sheet, "sourceSHA256": row["sourceSHA256"],
                                 "priorDirectorySHA256": prior["directorySHA256"],
                                 "currentDirectorySHA256": current["directorySHA256"],
                                 "modelMemberCount": len(new[row["modelId"]]["members"]),
                                 "assetSHA256Verified": sha(asset) == row["sourceSHA256"],
                                 "archiveETagVerified": bool(acquired)})
            except Exception as error:
                outcomes.append({"uid": uid, "state": "exact-source-recovery-failed",
                                 "sourceSheet": sheet, "sourceSHA256": row["sourceSHA256"],
                                 "error": type(error).__name__ + ": " + str(error)[:120]})
    return outcomes


def owned():
    assert reservations.owns(read(LOCAL / "reservation.json"))
    selection = {row["uid"]: row for row in read(BASE / "selection.json.gz")["rows"]}
    errors = {}
    folders = {}
    for folder in (FIRST, HELD):
        for uid, error in read(folder / "geometry-inputs.json")["errors"].items():
            errors[uid] = error
            folders[uid] = folder
    uids = sorted(uid for uid, error in errors.items() if error == "ValueError: Source revision changed")
    assert len(uids) == 18
    sheets = sorted({selection[uid]["native"]["sheet"] for uid in uids})
    assert len(sheets) == 8
    with connect() as connection:
        connection.execute("SET TRANSACTION READ ONLY")
        prior = dict(connection.execute(
            "SELECT DISTINCT ON(sheet) sheet,result FROM astra_modelling.city_source_directories "
            "WHERE sheet=ANY(%s) ORDER BY sheet,created_at DESC", (sheets,)).fetchall())
    grouped = defaultdict(list)
    current = {}
    for uid in uids:
        source = selection[uid]
        sheet = source["native"]["sheet"]
        directory = folders[uid] / "sheets" / sheet / "directory"
        if sheet not in current:
            current[sheet] = read(directory / "result.json")
        assert current[sheet]["directorySHA256"] != prior[sheet]["directorySHA256"]
        grouped[sheet].append({"uid": uid, "modelId": source["modelId"],
                               "sourceSHA256": source["sourceSHA256"],
                               "sourceEntry": source["native"]["model"]["sourceEntry"],
                               "sourceBytes": source["native"]["model"]["asset"]["bytes"],
                               "directoryFile": directory / "zip-directory.bin"})
    outcomes = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(work, sheet, rows, current[sheet], prior[sheet]): sheet
                   for sheet, rows in grouped.items()}
        for future in as_completed(futures):
            sheet = futures[future]
            try:
                group = future.result()
            except Exception as error:
                group = [{"uid": row["uid"], "state": "archive-recovery-failed",
                          "sourceSheet": sheet, "sourceSHA256": row["sourceSHA256"],
                          "error": type(error).__name__ + ": " + str(error)[:120]}
                         for row in grouped[sheet]]
            outcomes.extend(group)
            print(json.dumps({"sheet": sheet, "done": len(outcomes),
                              "exact": sum(row["state"] == "exact-source-recovered" for row in outcomes)}), flush=True)
    outcomes.sort(key=lambda row: row["uid"])
    assert len(outcomes) == 18
    report = {"batch": BATCH, "stage": "model-member-revision-proof-v1", "models": len(outcomes),
              "sourceRun": read(BASE / "selection.json.gz")["nativeRun"],
              "selectionSHA256": sha(BASE / "selection.json.gz"),
              "rows": outcomes, "aiCalls": 0, "geometryChanges": 0,
              "publication": False,
              "qualification": "A changed sheet revision alone does not clear a hold. Exact model members and the final canonical asset SHA must both match the pinned source. Missing or changed models remain held."}
    recovered_rows = []
    errors = {}
    for item in outcomes:
        uid = item["uid"]
        source = selection[uid]
        if item["state"] == "exact-source-recovered":
            asset = LOCAL / "recovered/assets" / (source["sourceSHA256"] + ".glb.gz")
            assert sha(asset) == source["sourceSHA256"]
            building = source["source"]["building"]
            recovered_rows.append({"uid": uid, "building": building,
                                   "candidate": {"path": str(asset.resolve()),
                                                 "entry": shape_prepare.entry(source["native"], building)},
                                   "currentNative": None})
        else:
            errors[uid] = item["state"]
    save(LOCAL / "recovered/geometry-inputs.json",
         {"rows": recovered_rows, "errors": errors,
          "methods": {"verified-same-member-revision": len(recovered_rows)},
          "aiCalls": 0, "publication": False})
    save(BASE / "revision-recovery-20260924.json", report)
    print(json.dumps({"models": len(outcomes), "states":
                      {state: sum(row["state"] == state for row in outcomes)
                       for state in sorted({row["state"] for row in outcomes})}}), flush=True)


if __name__ == "__main__":
    owned() if len(sys.argv) > 1 else start()
