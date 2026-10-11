"""Recover exact source bytes for held XL forms without changing their review state."""

import json
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

from run import ROOT, HERE, read, save, digest

sys.path.insert(0, str(HERE.parent / "enhancement-screening"))
import shape_prepare

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
LOCAL = HERE / "local/government-xl-remaining-held-20260923"
OUT = LOCAL / "recovered"


def prepare():
    selection = read(BASE / "selection.json.gz")
    rows = [row for row in selection["rows"] if row["humanStatus"] == "held-unknown"]
    assert len(rows) == 199
    for row in rows:
        source = row["source"]
        assert source and digest((ROOT / "3d-viewer" / source["tile"]).read_bytes()) == source["tileSHA256"]
    evidence = {"nativeRun": selection["nativeRun"], "rows": [row["uid"] for row in rows],
                "sources": {row["uid"]: row["source"] for row in rows},
                "native": [row["native"] for row in rows]}
    save(LOCAL / "recovery-inputs.json.gz", evidence)
    hashes = {row["sourceSHA256"] for row in rows}
    cache = OUT / "assets"
    cache.mkdir(parents=True, exist_ok=True)
    copied = set()
    for base in (ROOT / "source-scripts/city", ROOT / "3d-viewer/city/data"):
        for directory, _, files in os.walk(base):
            for name in files:
                if not name.endswith(".glb.gz") or name[:-7] not in hashes or name[:-7] in copied:
                    continue
                source = Path(directory) / name
                if digest(source.read_bytes()) != name[:-7]:
                    continue
                shutil.copyfile(source, cache / name)
                copied.add(name[:-7])
    save(BASE / "held-recovery-preflight.json", {
        "selectionSHA256": digest((BASE / "selection.json.gz").read_bytes()),
        "heldRows": len(rows), "localExactAssets": len(copied),
        "aiCalls": 0, "modelGeometryChanges": 0,
    })
    print(json.dumps({"heldRows": len(rows), "localExactAssets": len(copied)}), flush=True)


def recover():
    preflight = read(BASE / "held-recovery-preflight.json")
    assert preflight["selectionSHA256"] == digest((BASE / "selection.json.gz").read_bytes())
    result = shape_prepare.prepare(LOCAL / "recovery-inputs.json.gz", OUT,
                                   allow_source=True, workers=4, env_file=ROOT / ".env.modelling")
    summary = {"selected": preflight["heldRows"], "recovered": len(result["rows"]),
               "errors": len(result["errors"]),
               "errorReasons": dict(Counter(value.split(":", 1)[0] for value in result["errors"].values())),
               "methods": result["methods"], "aiCalls": 0, "modelGeometryChanges": 0,
               "publication": False}
    save(BASE / "held-recovery-summary.json", summary)
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    {"prepare": prepare, "recover": recover}[sys.argv[1]]()
