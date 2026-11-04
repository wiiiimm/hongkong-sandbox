"""Retry only XL source sheets that failed with transient HTTP 502 errors."""

import json
import sys
from collections import Counter

from run import ROOT, HERE, read, save, digest

sys.path.insert(0, str(HERE.parent / "enhancement-screening"))
import shape_prepare

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
LOCAL = HERE / "local/government-xl-source-http-retry-20260924"


def run():
    selection = read(BASE / "selection.json.gz")
    source = {row["uid"]: row for row in selection["rows"]}
    first = read(HERE / "local/government-xl-remaining-held-20260923/recovered/geometry-inputs.json")
    errors = first["errors"]
    uids = sorted(uid for uid, error in errors.items() if error.startswith("HTTPError: HTTP Error 502"))
    assert len(uids) == 10 and len({source[uid]["native"]["sheet"] for uid in uids}) == 4
    frozen = {"nativeRun": selection["nativeRun"], "rows": uids,
              "sources": {uid: source[uid]["source"] for uid in uids},
              "native": [source[uid]["native"] for uid in uids]}
    for uid in uids:
        record = source[uid]["source"]
        assert digest((ROOT / "3d-viewer" / record["tile"]).read_bytes()) == record["tileSHA256"]
    save(LOCAL / "recovery-inputs.json.gz", frozen)
    result = shape_prepare.prepare(LOCAL / "recovery-inputs.json.gz", LOCAL / "recovered",
                                   allow_source=True, workers=4, env_file=ROOT / ".env.modelling")
    recovered = {row["uid"] for row in result["rows"]}
    assert recovered | set(result["errors"]) == set(uids)
    summary = {"batch": "government-xl-source-http-retry-20260924",
               "selectionSHA256": digest((BASE / "selection.json.gz").read_bytes()),
               "previousErrorSHA256": digest((HERE / "local/government-xl-remaining-held-20260923/recovered/geometry-inputs.json").read_bytes()),
               "attempted": len(uids), "recovered": len(recovered),
               "remainingErrors": len(result["errors"]),
               "reasons": dict(Counter(value.split(":", 1)[0] for value in result["errors"].values())),
               "uids": [{"uid": uid, "name": source[uid]["name"], "sheet": source[uid]["native"]["sheet"],
                         "state": "recovered-needs-identity-and-terrain-checks" if uid in recovered
                         else "source-recovery-held", "error": result["errors"].get(uid)} for uid in uids],
               "aiCalls": 0, "geometryChanges": 0, "publication": False}
    save(BASE / "http-retry-20260924.json", summary)
    print(json.dumps({"attempted": len(uids), "recovered": len(recovered),
                      "remainingErrors": len(result["errors"]), "reasons": summary["reasons"]}), flush=True)


if __name__ == "__main__":
    run()
