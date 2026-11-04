"""Audit original Kowloon Park source faces against government terrain."""

import importlib.util

from run import ROOT, HERE

spec = importlib.util.spec_from_file_location("xl_kowloon_park_foundation", HERE / "xl-phase-one-foundation.py")
foundation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foundation)


if __name__ == "__main__":
    foundation.DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/kowloon-park-administration-terrain-diagnostic-20260927"
    foundation.LOCAL = HERE / "local/government-xl-kowloon-park-administration-terrain-20260927"
    foundation.UID = "landsd/336430:0"
    foundation.OUTPUT = foundation.DOC / "foundation.json"
    foundation.run()
