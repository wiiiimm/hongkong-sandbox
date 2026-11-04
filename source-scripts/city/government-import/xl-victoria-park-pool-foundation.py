"""Audit original Victoria Park pool faces against its government terrain."""

import importlib.util

from run import ROOT, HERE

spec = importlib.util.spec_from_file_location("xl_victoria_pool_foundation", HERE / "xl-phase-one-foundation.py")
foundation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foundation)


if __name__ == "__main__":
    foundation.DOC = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/victoria-park-pool-terrain-diagnostic-20260927"
    foundation.LOCAL = HERE / "local/government-xl-victoria-park-pool-terrain-20260927"
    foundation.UID = "landsd/72324:0"
    foundation.OUTPUT = foundation.DOC / "foundation.json"
    foundation.run()
