"""Evaluate Phase 1's complete single-sheet government terrain with scripts only."""

import importlib.util

from run import ROOT, HERE

spec = importlib.util.spec_from_file_location("xl_phase_one_source", HERE / "xl-diocesan-girls-school-terrain-diagnostic.py")
diagnostic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagnostic)


if __name__ == "__main__":
    diagnostic.UID = "landsd/305672:0"
    diagnostic.SHEET = "11-NW-19D"
    diagnostic.TERRAIN_SHEETS = ("11-NW-19D",)
    diagnostic.LOW_TERRAIN_POLICY = "reject"
    diagnostic.DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/phase-one-terrain-diagnostic-20260927"
    diagnostic.LOCAL = HERE / "local/government-xl-phase-one-terrain-20260927"
    diagnostic.run()
