"""Measure exact projected identity and neighbouring forms for recovered XL sources."""

import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run import ROOT, HERE, read, save, digest

spec = importlib.util.spec_from_file_location("xl_context", HERE / "xl-final-script-pass.py")
context = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context)
BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
DIRECT_ASSETS = HERE / "local/government-xl-remaining-20260923/recovered"
HELD_ASSETS = HERE / "local/government-xl-remaining-held-20260923/recovered"


def run(only_ready=False, held=False):
    context.s.LOCAL = HELD_ASSETS if held else DIRECT_ASSETS
    output_path = BASE / ("context-held.json" if held else "context.json")
    selection = read(BASE / "selection.json.gz")
    results = read(BASE / "results.json.gz")
    recovered = read(context.s.LOCAL / "geometry-inputs.json")
    available = {row["uid"] for row in recovered["rows"]}
    ready = {row["uid"] for row in results["rows"] if row["humanStatus"] == "in-process"}
    rows = [row for row in selection["rows"] if row["uid"] in available and (not only_ready or row["uid"] in ready)]
    assert len(rows) == (len(ready) if only_ready else len(available))
    output = read(output_path) if output_path.exists() else {"rows": [], "errors": {}}
    done = {row["uid"] for row in output["rows"]} | set(output["errors"])
    for source in rows:
        uid = source["uid"]
        if uid in done:
            continue
        try:
            triangles = context.s.glb_triangles(source)
            lo, hi = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
            forms = context.load_forms([lo[0] - 2, lo[2] - 2, hi[0] + 2, hi[2] + 2])
            identity = context.identity_context(source, triangles, forms)
            output["rows"].append({
                "uid": uid, "name": source.get("name"), "sourceSHA256": source["sourceSHA256"],
                "sourceSheet": source["native"]["sheet"], "triangles": len(triangles),
                "identity": identity,
            })
            print(json.dumps({"uid": uid, "targetCoverage": identity["targetCoveredBySourceProjection"],
                              "sourceInsideTarget": identity["sourceProjectionInsideTarget"],
                              "otherForms": len(identity["intersectingForms"]) - 1}), flush=True)
        except Exception as error:
            output["errors"][uid] = f"{type(error).__name__}: {str(error)[:200]}"
            print(json.dumps({"uid": uid, "error": output["errors"][uid]}), flush=True)
        output["rows"].sort(key=lambda item: item["uid"])
        output["inputSHA256"] = {
            "selection": digest((BASE / "selection.json.gz").read_bytes()),
            "results": digest((BASE / "results.json.gz").read_bytes()),
        }
        save(output_path, output)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only-ready", action="store_true")
    parser.add_argument("--held", action="store_true")
    args = parser.parse_args()
    result = run(args.only_ready, args.held)
    print(json.dumps({"analysed": len(result["rows"]), "errors": len(result["errors"])}), flush=True)
