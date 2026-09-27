"""Measure how much cached adjacent government TIN closes sampled XL source gaps."""

import importlib.util
import json
import shutil
from pathlib import Path

import numpy as np
import shapely

from run import ROOT, HERE, read, save, digest


spec = importlib.util.spec_from_file_location("xl_adjacent_second", HERE / "xl-second-pass.py")
second = importlib.util.module_from_spec(spec)
spec.loader.exec_module(second)

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
SOURCES = HERE / "local/government-xl-terrain-sources-20260924/sheets"
INPUTS = (HERE / "local/government-xl-remaining-20260923/recovered/geometry-inputs.json",
          HERE / "local/government-xl-remaining-held-20260923/recovered/geometry-inputs.json")
OUT = BASE / "cached-adjacent-sheet-survey-20260927.json"
UIDS = ("landsd/91127:0", "landsd/149020:0", "landsd/264206:0",
        "landsd/293822:0", "landsd/305672:0")


def sha(path):
    return digest(path.read_bytes())


def run():
    gap = {row["uid"]: row for row in read(BASE / "terrain-source-gap-triage-20260927.json")["rows"]}
    selection = {row["uid"]: row for row in read(BASE / "selection.json.gz")["rows"]}
    inputs = {row["uid"]: row for path in INPUTS for row in read(path)["rows"]}
    parent = read(ROOT / "3d-viewer/city/data/terrain.json")
    contexts = {}
    for uid in UIDS:
        model = selection[uid]
        source_path = Path(inputs[uid]["candidate"]["path"])
        assert sha(source_path) == model["sourceSHA256"]
        asset = second.LOCAL / "assets" / (model["sourceSHA256"] + ".glb.gz")
        asset.parent.mkdir(parents=True, exist_ok=True)
        if not asset.exists():
            shutil.copyfile(source_path, asset)
        assert sha(asset) == model["sourceSHA256"]
        triangles = second.glb_triangles(model)
        cells = second.resolution.rectangle_for(model["native"]["model"]["worldBounds"], parent)
        bounds = second.resolution.extent(cells, parent)
        protected = shapely.union_all(shapely.polygons(triangles[:, :, [0, 2]]))
        protected = protected.intersection(shapely.box(*bounds))
        assert protected.area > 0
        contexts[uid] = {"bounds": bounds, "protected": protected, "bySheet": {}}
    for directory in sorted(SOURCES.iterdir()):
        if not directory.is_dir() or not (directory / "original/download.json").exists():
            continue
        download = read(directory / "original/download.json")
        assert download["directorySHA256"] == read(directory / "directory/result.json")["directorySHA256"]
        source_hashes = {entry["name"]: entry["sha256"] for entry in download["entries"]}
        for file in sorted((directory / "terrain").rglob("*.gltf")):
            relative = str(file.relative_to(directory / "terrain"))
            assert sha(file) == source_hashes[relative]
            triangles = second.terrain_triangles(file)
            for uid, context in contexts.items():
                x0, z0, x1, z1 = context["bounds"]
                within = ((triangles[:, :, 0].max(axis=1) >= x0) &
                          (triangles[:, :, 0].min(axis=1) <= x1) &
                          (triangles[:, :, 2].max(axis=1) >= z0) &
                          (triangles[:, :, 2].min(axis=1) <= z1) &
                          (triangles[:, :, 1].min(axis=1) >= 1.2))
                if np.any(within):
                    context["bySheet"].setdefault(directory.name, []).append(triangles[within])
    rows = []
    for uid in UIDS:
        context = contexts[uid]
        target = context["protected"]
        primary = gap[uid]["sheet"]
        by_sheet = {sheet: shapely.union_all(shapely.polygons(np.concatenate(fragments)[:, :, [0, 2]]))
                    for sheet, fragments in context["bySheet"].items()}
        assert primary in by_sheet
        covered = by_sheet[primary]
        original_missing = target.difference(covered).area
        assert abs(original_missing - gap[uid]["missingUnderModelM2"]) <= .1
        contributions = []
        for sheet, projection in sorted(by_sheet.items(), key=lambda item: target.intersection(item[1]).area, reverse=True):
            if sheet == primary:
                continue
            added = target.intersection(projection.difference(covered)).area
            if added > .01:
                contributions.append({"sheet": sheet, "additionalCoverageM2": added,
                                      "directorySHA256": read(SOURCES / sheet / "original/download.json")["directorySHA256"]})
                covered = covered.union(projection)
        remaining = target.difference(covered)
        row = {"uid": uid, "name": gap[uid]["name"], "primarySheet": primary,
               "candidateSheets": contributions, "primaryMissingM2": original_missing,
               "remainingMissingM2": remaining.area,
               "remainingOutsideTwoCentimetreSeamM2": remaining.difference(covered.buffer(.02)).area,
               "routing": "cached-sheets-complete" if remaining.area <= .1 else "further-source-or-contact-work",
               "nextWork": "Build and validate a multi-sheet source-preserving patch, then run identity, contact, neighbour and browser checks." if remaining.area <= .1 else "Find another source sheet or diagnose the remaining footprint gap before patch construction.",
               "requiresAI": False, "requiresHuman": False, "aiCalls": 0,
               "modelGeometryChanges": 0, "publication": False}
        rows.append(row)
        print(json.dumps({"uid": uid, "primaryMissingM2": round(original_missing, 2),
                          "remainingM2": round(remaining.area, 2),
                          "additionalSheets": [item["sheet"] for item in contributions]}), flush=True)
        save(OUT, {"stage": "cached-adjacent-sheet-coverage-v1", "models": len(rows),
                   "complete": len(rows) == len(UIDS), "rows": rows,
                   "sourceInputSHA256": sha(BASE / "terrain-source-gap-triage-20260927.json"),
                   "aiCalls": 0, "modelGeometryChanges": 0, "publication": False})


if __name__ == "__main__":
    run()
