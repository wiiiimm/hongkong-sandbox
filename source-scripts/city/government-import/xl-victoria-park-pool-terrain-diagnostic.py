"""Evaluate Victoria Park Swimming Pool against original government TIN."""

import importlib.util

from run import ROOT, HERE

spec = importlib.util.spec_from_file_location("xl_victoria_pool_source", HERE / "xl-diocesan-girls-school-terrain-diagnostic.py")
diagnostic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagnostic)


if __name__ == "__main__":
    diagnostic.UID = "landsd/72324:0"
    diagnostic.SHEET = "11-SE-6C"
    diagnostic.TERRAIN_SHEETS = ("11-SE-6C",)
    diagnostic.LOW_TERRAIN_POLICY = "retain-below-clamp"
    diagnostic.DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/victoria-park-pool-terrain-diagnostic-20260927"
    diagnostic.LOCAL = HERE / "local/government-xl-victoria-park-pool-terrain-20260927"
    diagnostic.run()
