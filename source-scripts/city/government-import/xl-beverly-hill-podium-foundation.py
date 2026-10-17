"""Audit recovered Beverly Hill podium faces against Block A's original TIN."""

import importlib.util

from run import ROOT, HERE, read, save

spec = importlib.util.spec_from_file_location("xl_beverly_podium_foundation", HERE / "xl-phase-one-foundation.py")
foundation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foundation)


if __name__ == "__main__":
    doc = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923/beverly-hill-block-a-terrain-diagnostic-20260927"
    support = read(HERE / "local/government-xl-beverly-hill-podium-20260927/support-runtime.json.gz")["rows"][0]
    assert support["uid"] == "landsd/233218:0"
    selection = doc / "support-selection.json.gz"
    save(selection, {"rows": [support], "aiCalls": 0, "modelGeometryChanges": 0})
    foundation.DOC = doc
    foundation.LOCAL = HERE / "local/government-xl-beverly-hill-podium-foundation-20260927"
    foundation.UID = support["uid"]
    foundation.SELECTION = selection
    foundation.OUTPUT = doc / "support-foundation.json"
    foundation.run()
