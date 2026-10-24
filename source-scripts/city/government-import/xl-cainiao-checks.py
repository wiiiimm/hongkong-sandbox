"""Run exact-source identity, runtime and neighbour gates on Cainiao's coastal patch."""

import importlib.util

from run import ROOT, HERE


spec = importlib.util.spec_from_file_location("xl_new_two_sheet_checks", HERE / "xl-new-two-sheet-checks.py")
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


if __name__ == "__main__":
    checks.SITES = (("landsd/293822:0", "cainiao-smart-gateway"),)
    checks.OUT = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/cainiao-checks-20260927.json"
    checks.run()
