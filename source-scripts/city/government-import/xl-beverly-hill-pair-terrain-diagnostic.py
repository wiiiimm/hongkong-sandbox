"""Evaluate unchanged Beverly Hill Block A and its complete podium against original government TIN."""

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
    diagnostic.DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/beverly-hill-pair-terrain-diagnostic-20260928"
    diagnostic.LOCAL = HERE / "local/government-xl-beverly-hill-pair-terrain-20260928"
    diagnostic.SUPPORT_SELECTION = HERE / "local/government-xl-beverly-hill-podium-20260927/support-runtime.json.gz"
    diagnostic.run()
