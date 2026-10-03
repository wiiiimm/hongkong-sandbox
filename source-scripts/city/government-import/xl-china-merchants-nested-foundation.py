"""Audit all original China Merchants source faces against its native terrain."""

import importlib.util

from run import ROOT, HERE

spec = importlib.util.spec_from_file_location("xl_china_foundation", HERE / "xl-phase-one-foundation.py")
foundation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foundation)


if __name__ == "__main__":
    foundation.DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/china-merchants-tower-east-terrain-diagnostic-20260927"
    foundation.LOCAL = HERE / "local/government-xl-china-merchants-tower-east-terrain-20260927"
    foundation.BASE = foundation.DOC
    foundation.UID = "landsd/264206:0"
    foundation.OUTPUT = foundation.DOC / "foundation.json"
    foundation.run()
