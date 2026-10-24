"""Build a local two-sheet China Merchants patch inside the installed Central terrain."""

import importlib.util

from run import ROOT, HERE

spec = importlib.util.spec_from_file_location("xl_two_sheet_nested", HERE / "xl-diocesan-girls-school-terrain-diagnostic.py")
diagnostic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagnostic)


if __name__ == "__main__":
    diagnostic.UID = "landsd/264206:0"
    diagnostic.SHEET = "11-SW-8A"
    diagnostic.TERRAIN_SHEETS = ("11-SW-8A", "11-SW-8B")
    diagnostic.LOW_TERRAIN_POLICY = "retain-below-clamp"
    diagnostic.PARENT_URL = "city/data/terrain-central-with-hullett.json"
    diagnostic.DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/china-merchants-tower-east-terrain-diagnostic-20260927"
    diagnostic.LOCAL = HERE / "local/government-xl-china-merchants-tower-east-terrain-20260927"
    diagnostic.run()
