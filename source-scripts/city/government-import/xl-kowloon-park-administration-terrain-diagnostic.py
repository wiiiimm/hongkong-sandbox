"""Evaluate original Kowloon Park Administration Building model and TIN."""

import importlib.util

from run import ROOT, HERE

spec = importlib.util.spec_from_file_location("xl_kowloon_park_source", HERE / "xl-diocesan-girls-school-terrain-diagnostic.py")
diagnostic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagnostic)


if __name__ == "__main__":
    diagnostic.UID = "landsd/336430:0"
    diagnostic.SHEET = "11-NW-24D"
    diagnostic.TERRAIN_SHEETS = ("11-NW-24D",)
    diagnostic.LOW_TERRAIN_POLICY = "retain-below-clamp"
    diagnostic.DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/kowloon-park-administration-terrain-diagnostic-20260927"
    diagnostic.LOCAL = HERE / "local/government-xl-kowloon-park-administration-terrain-20260927"
    diagnostic.run()
