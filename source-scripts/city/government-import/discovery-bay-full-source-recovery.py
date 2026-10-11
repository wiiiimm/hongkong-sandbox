"""Recover persistent Discovery Bay source-range failures from verified full sheets; no AI."""
from __future__ import annotations

import collections
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import time
import urllib.error
import urllib.request
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BATCH = "government-discovery-bay-1103-20260921"
LOCAL = HERE / "local" / BATCH
RECOVERED = LOCAL / "recovered"


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temp.replace(path)


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def download(row, destination, attempts=20):
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_suffix(".zip.part")
    for attempt in range(1, attempts + 1):
        temp.unlink(missing_ok=True)
        request = urllib.request.Request(row["sourceURL"], headers={"User-Agent": "HKS-203-government-source-recovery/1"})
        try:
            with urllib.request.urlopen(request, timeout=120) as response, temp.open("wb") as output:
                etag = response.headers.get("ETag")
                if etag != row["etag"]:
                    raise ValueError(f"ETag changed: {etag!r}")
                shutil.copyfileobj(response, output, length=1024 * 1024)
            if temp.stat().st_size != row["archiveBytes"]:
                raise ValueError(f"byte count {temp.stat().st_size} != {row['archiveBytes']}")
            temp.replace(destination)
            return attempt
        except (OSError, ValueError, urllib.error.HTTPError) as error:
            temp.unlink(missing_ok=True)
            if attempt == attempts:
                raise
            print(json.dumps({"sheet": row["sheet"], "attempt": attempt, "retry": type(error).__name__}), flush=True)
            time.sleep(min(3, attempt))
    raise AssertionError("unreachable")


def main():
    selection = read(LOCAL / "selection.json.gz")
    recovery = read(RECOVERED / "geometry-inputs.json")
    metadata = read(RECOVERED / "source-metadata.json")
    by_uid = {row["uid"]: row for row in selection["rows"]}
    failed_sheets = sorted({by_uid[uid]["native"]["sheet"] for uid in recovery["errors"]})
    models = collections.defaultdict(list)
    for uid in recovery["errors"]:
        row = by_uid[uid]
        models[row["native"]["sheet"]].append(row["native"]["model"])
    results = []
    for sheet in failed_sheets:
        row = metadata["directories"][sheet]
        assert row["sheet"] == sheet and row["sourceURL"].startswith("https://download.map.gov.hk/")
        full = RECOVERED / "sheets" / sheet / "full-source" / f"{sheet}.zip"
        attempts = 0
        if not full.exists() or full.stat().st_size != row["archiveBytes"]:
            attempts = download(row, full)
        with zipfile.ZipFile(full) as archive:
            bad = archive.testzip()
            assert bad is None, bad
        original = RECOVERED / "sheets" / sheet / "original"
        original.mkdir(parents=True, exist_ok=True)
        archive_path = original / f"{sheet}.zip"
        record_path = original / "download.json"
        if archive_path.exists() and not archive_path.samefile(full):
            backup = original / f"{sheet}.range-cache.zip"
            if not backup.exists():
                archive_path.replace(backup)
            else:
                archive_path.unlink()
        if record_path.exists():
            backup = original / "download.range-cache.json"
            if not backup.exists():
                record_path.replace(backup)
            else:
                record_path.unlink()
        try:
            os.link(full, archive_path)
        except OSError:
            shutil.copyfile(full, archive_path)
        sha = digest(full)
        record = {
            "sheet": sheet,
            "source": row["sourceURL"],
            "sourceETag": row["etag"],
            "directorySHA256": row["directorySHA256"],
            "sha256": sha,
            "bytes": full.stat().st_size,
            "cacheKind": "Verified complete government source ZIP fallback after persistent range proxy failures",
            "dependencyScanVersion": 1,
            "terrainGeometryIncluded": False,
            "expectedModels": len(models[sheet]),
            "aiCalls": 0,
        }
        save(record_path, record)
        results.append({
            "sheet": sheet, "bytes": full.stat().st_size, "sha256": sha,
            "models": len(models[sheet]), "downloadAttempts": attempts,
        })
        print(json.dumps(results[-1]), flush=True)
    report = {
        "batch": BATCH, "failedSheetsRecovered": len(results),
        "modelsCovered": sum(row["models"] for row in results),
        "bytes": sum(row["bytes"] for row in results),
        "rows": results, "aiCalls": 0, "geometryChanges": 0,
    }
    save(ROOT / "docs/astra-city/government-import" / BATCH / "full-source-recovery.json", report)
    print(json.dumps({key: value for key, value in report.items() if key != "rows"}), flush=True)


if __name__ == "__main__":
    main()
