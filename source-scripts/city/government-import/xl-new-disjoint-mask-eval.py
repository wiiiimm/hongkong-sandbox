"""Preserve parent terrain under disjoint neighbours of two new XL candidates."""

import importlib.util

from run import ROOT, HERE, read


spec = importlib.util.spec_from_file_location("xl_disjoint_reusable", HERE / "xl-disjoint-neighbour-mask-eval.py")
mask = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mask)

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
SITES = (("cityplaza", "landsd/91127:0"),
         ("tin-shui-wai-station", "landsd/149020:0"))


def run():
    checks = {row["uid"]: row for row in read(BASE / "new-two-sheet-checks-20260927.json")["rows"]}
    for name, uid in SITES:
        assert checks[uid]["state"] == "checks-complete" and checks[uid]["blockedNeighbourUids"]
        assert checks[uid]["sourcePreserved"] and not checks[uid]["runtimeConcerns"]
    mask.SITES = SITES
    mask.REQUIRE_SHARED = False
    mask.LOCAL = HERE / "local/government-xl-new-disjoint-mask-eval-20260927"
    mask.OUTPUT = BASE / "new-disjoint-neighbour-mask-eval-20260927.json"
    mask.run()


if __name__ == "__main__":
    run()
