"""Audit original Beverly Hill Block A faces against its two-sheet TIN."""

import importlib.util

from run import ROOT, HERE

spec = importlib.util.spec_from_file_location("xl_beverly_a_foundation", HERE / "xl-phase-one-foundation.py")
foundation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foundation)


if __name__ == "__main__":
    foundation.DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/beverly-hill-block-a-terrain-diagnostic-20260927"
    foundation.LOCAL = HERE / "local/government-xl-beverly-hill-block-a-terrain-20260927"
    foundation.UID = "landsd/255539:0"
    foundation.OUTPUT = foundation.DOC / "foundation.json"
    foundation.run()
