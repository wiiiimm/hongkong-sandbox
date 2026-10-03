"""Test parent terrain retention under Cainiao's disjoint neighbour and podium."""

import importlib.util

from run import ROOT, HERE, read


BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
UID = "landsd/293822:0"
NAME = "cainiao-smart-gateway"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def run():
    checks = read(BASE / "cainiao-checks-20260927.json")["rows"][0]
    assert checks["uid"] == UID and checks["state"] == "checks-complete"
    assert set(checks["blockedNeighbourUids"]) == {"way/102137667:0", "landsd/327178:0"}
    assert checks["sourcePreserved"] and checks["missingTerrainSamples"] == 0
    disjoint = module("xl_cainiao_disjoint", HERE / "xl-disjoint-neighbour-mask-eval.py")
    disjoint.SITES = ((NAME, UID),)
    disjoint.LOCAL = HERE / "local/government-xl-cainiao-disjoint-mask-20260927"
    disjoint.OUTPUT = BASE / "cainiao-disjoint-mask-eval-20260927.json"
    disjoint.run()
    shared = module("xl_cainiao_shared", HERE / "xl-shared-neighbour-mask-eval.py")
    shared.SOURCE = disjoint.OUTPUT
    shared.LOCAL = HERE / "local/government-xl-cainiao-shared-mask-20260927"
    shared.OUTPUT = BASE / "cainiao-shared-mask-eval-20260927.json"
    shared.run()


if __name__ == "__main__":
    run()
