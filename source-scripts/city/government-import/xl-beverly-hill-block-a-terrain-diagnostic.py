"""Evaluate unchanged Beverly Hill Block A against original government TIN."""

import importlib.util

from run import ROOT, HERE

spec = importlib.util.spec_from_file_location("xl_beverly_a_source", HERE / "xl-diocesan-girls-school-terrain-diagnostic.py")
diagnostic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagnostic)


if __name__ == "__main__":
    diagnostic.UID = "landsd/255539:0"
    diagnostic.SHEET = "11-SW-15B"
    diagnostic.TERRAIN_SHEETS = ("11-SW-15B", "11-SW-15D")
    diagnostic.LOW_TERRAIN_POLICY = "retain-below-clamp"
    diagnostic.DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/beverly-hill-block-a-terrain-diagnostic-20260927"
    diagnostic.LOCAL = HERE / "local/government-xl-beverly-hill-block-a-terrain-20260927"
    diagnostic.run()
