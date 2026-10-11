"""Run full-triangle source, runtime, and native-neighbour gates on new XL masks."""

import importlib.util
import json
import subprocess

from run import ROOT, HERE, read, save, digest


spec = importlib.util.spec_from_file_location("xl_masked_foundation_reusable", HERE / "xl-masked-foundation-eval.py")
foundation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foundation)

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
SOURCE = BASE / "new-disjoint-neighbour-mask-eval-20260927.json"
OUT = BASE / "new-mask-checks-20260927.json"
SITES = (("landsd/91127:0", "cityplaza"),
         ("landsd/149020:0", "tin-shui-wai-station"))


def rel(path):
    return str(path.relative_to(ROOT))


def ref(path):
    return {"path": rel(path), "sha256": digest(path.read_bytes())}


def call(args, allowed=(0,)):
    result = subprocess.run(args, cwd=ROOT)
    assert result.returncode in allowed, (args, result.returncode)


def run():
    candidates = {row["uid"]: row for row in read(SOURCE)["rows"]}
    assert set(candidates) == {uid for uid, _ in SITES}
    assert all(not row["remainingBlockedUids"] for row in candidates.values())
    foundation.SOURCE = SOURCE
    foundation.OUT = BASE / "new-masked-foundation-eval-20260927.json"
    foundation.run()
    audited = {row["uid"]: row for row in read(foundation.OUT)["rows"]}
    rows = []
    for uid, name in SITES:
        doc = BASE / f"{name}-terrain-diagnostic-20260927"
        folder = HERE / "local/government-xl-new-disjoint-mask-eval-20260927" / name
        candidate = candidates[uid]
        assert ref(ROOT / candidate["candidatePatch"]["path"]) == candidate["candidatePatch"]
        neighbour_inputs = read(folder / "neighbour-inputs.json.gz")
        terrain = [{**neighbour_inputs["patches"][0], **candidate["candidatePatch"]}]
        save(folder / "terrain-candidates.json", terrain)
        assets = HERE / "local" / f"government-xl-{name}-terrain-20260927/candidates"
        call(["node", str(HERE / "acceptance-metrics.mjs"),
              "--selection", rel(doc / "selection.json.gz"),
              "--candidates", rel(assets),
              "--terrain-candidates", rel(folder / "terrain-candidates.json"),
              "--out", rel(folder / "metrics.json")])
        call(["node", str(HERE.parent / "building-batch/validate_candidates.mjs"),
              "--candidates", rel(assets), "--source-forms", rel(assets / "source-forms.json"),
              "--terrain-candidates", rel(folder / "terrain-candidates.json"),
              "--out", rel(folder / "validation.json")], allowed=(0, 1))
        call(["node", str(HERE / "check-native-neighbours.mjs"), rel(folder) + "/"])
        metric = read(folder / "metrics.json")["rows"][0]
        validation = read(folder / "validation.json")
        native = read(folder / "native-neighbour-checks.json")
        proof = audited[uid]
        row = {"uid": uid, "site": name,
               "foundationAccepted": proof["strictFoundationAccepted"],
               "fullyBuriedUpwardTriangles": proof["foundation"]["fullyBuriedUpwardTriangles"],
               "fullyBuriedAreaFraction": proof["foundation"]["fullyBuriedAreaFraction"],
               "sourcePreserved": metric["sourcePreserved"],
               "minimumLowRimGapM": metric["minLowGap"],
               "maximumLowRimGapM": metric["maxLowGap"],
               "maxSamplerDeltaM": metric["maxSamplerDelta"],
               "missingTerrainSamples": metric["missingTerrain"],
               "mobileBudgetPassed": all(metric["budget"][key] <= read(folder / "metrics.json")["profiles"]["mobile"][key]
                                         for key in ("triangles", "geometryBytes", "residentBytes")),
               "loaderAccepted": validation["loaderAccepted"],
               "checksPassed": validation["checksPassed"],
               "runtimeConcerns": validation["results"][0].get("concerns", []),
               "blockedNativeNeighbourUids": sorted(set(native.get("blocked", [])) -
                                                    set(native.get("resolved", []))),
               "candidatePatch": candidate["candidatePatch"],
               "foundationEvidence": ref(foundation.OUT),
               "metricsEvidence": ref(folder / "metrics.json"),
               "validationEvidence": ref(folder / "validation.json"),
               "nativeNeighbourEvidence": ref(folder / "native-neighbour-checks.json"),
               "aiCalls": 0, "modelGeometryChanges": 0, "publication": False}
        rows.append(row)
        save(OUT, {"stage": "new-xl-masked-source-runtime-checks-v1", "rows": rows,
                   "complete": len(rows) == len(SITES), "aiCalls": 0,
                   "modelGeometryChanges": 0, "publication": False})
        print(json.dumps({"uid": uid, "foundation": row["foundationAccepted"],
                          "lowRimM": row["minimumLowRimGapM"],
                          "concerns": row["runtimeConcerns"]}), flush=True)


if __name__ == "__main__":
    run()
