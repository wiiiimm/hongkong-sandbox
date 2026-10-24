"""Exhaust deterministic identity and foundation checks for 16 Lantau landmarks."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "docs/astra-city/government-import/government-lantau-landmarks-16-20260916"
DOC = BASE / "second-pass"
LOCAL = HERE / "local/government-lantau-landmarks-16-second-20260916"
OUT = DOC / "final-script-pass"

spec = importlib.util.spec_from_file_location("xl_final", HERE / "xl-final-script-pass.py")
final = importlib.util.module_from_spec(spec)
spec.loader.exec_module(final)
final.s.BASE = BASE
final.s.DOC = DOC
final.s.LOCAL = LOCAL
final.s.BATCH = "government-lantau-landmarks-16-second-20260916"
final.DOC = DOC
final.OUT = OUT


def remaining_rows():
    original = final.s.read(BASE / "selection.json.gz")["rows"]
    installed = final.installed_source_hashes()
    rows = [row for row in original if row["sourceSHA256"] not in installed]
    assert len(rows) == 16, f"Expected 16 uninstalled landmark sources, found {len(rows)}"
    diagnostics = {row["modelId"]: row for row in final.s.read(DOC / "diagnostics.json")["rows"]}
    assert set(diagnostics) == {row["modelId"] for row in rows}
    for row in rows:
        yield row, diagnostics[row["modelId"]]


def main():
    final.remaining_rows = remaining_rows
    final.main()
    report = final.s.read(OUT / "results.json.gz")
    report.update(
        batch="government-lantau-landmarks-16-final-script-pass-20260916",
        qualification=(
            "All 16 named Lantau XL/L sources received exact identifier, projected assembly, "
            "vertical-neighbour and connected below-grade source-face checks against seven pinned "
            "government terrain sheets. No AI calls or geometry changes."
        ),
    )
    final.s.save(OUT / "results.json.gz", report)
    final.s.save(OUT / "summary.json", {
        "batch": report["batch"],
        "stage": report["stage"],
        "models": len(report["rows"]),
        "publicationCandidates": sum(row["publicationCandidate"] for row in report["rows"]),
        "scriptedWorkComplete": sum(row["scriptedWorkComplete"] for row in report["rows"]),
        "held": sum(bool(row["reasons"]) for row in report["rows"]),
        "aiCalls": 0,
        "modelGeometryChanges": 0,
    })


if __name__ == "__main__":
    main()
