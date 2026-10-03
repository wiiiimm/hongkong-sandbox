"""Measure original government TIN coverage under held XL model projections.

This is a routing diagnostic, not an installation or a terrain repair. It
keeps the source GLB and TIN unchanged and reports protected gaps that exceed
the existing 2 cm numerical-seam allowance.
"""

import importlib.util
import json
import shutil
import sys
import uuid
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import Polygon

from run import ROOT, HERE, read, save, digest, connect, jobs, reservations, Jsonb, dict_row

spec = importlib.util.spec_from_file_location("xl_second_gap", HERE / "xl-second-pass.py")
second = importlib.util.module_from_spec(spec)
spec.loader.exec_module(second)

BASE = ROOT / "docs/astra-city/government-import/government-xl-remaining-20260923"
OUT = BASE / "terrain-source-gap-triage-20260927.json"
RECEIPT = BASE / "terrain-source-gap-triage-20260927-neon.json"
BATCH = "government-xl-terrain-source-gap-triage-20260927"
SOURCES = HERE / "local/government-xl-terrain-sources-20260924/sheets"
INPUTS = (HERE / "local/government-xl-remaining-20260923/recovered/geometry-inputs.json",
          HERE / "local/government-xl-remaining-held-20260923/recovered/geometry-inputs.json")
UIDS = ("landsd/91127:0", "landsd/149020:0", "landsd/257352:0",
        "landsd/264206:0", "landsd/273672:0", "landsd/293822:0",
        "landsd/305672:0")


def sha(path):
    return digest(Path(path).read_bytes())


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def run():
    selected = {row["uid"]: row for row in read(BASE / "selection.json.gz")["rows"]}
    holds = {row["uid"]: row for row in read(BASE / "reconciliation.json.gz")["rows"]}
    inputs = {row["uid"]: row for path in INPUTS for row in read(path)["rows"]}
    context = {row["uid"]: row for path in (BASE / "context.json", BASE / "context-held.json")
               for row in read(path)["rows"]}
    parent = read(ROOT / "3d-viewer/city/data/terrain.json")
    manifest = read(ROOT / "3d-viewer/city/data/manifest.json")
    installed = [(entry["url"], read(ROOT / "3d-viewer" / entry["url"])["coarseCells"])
                 for entry in manifest["terrainPatches"]]
    rows = []
    for uid in UIDS:
        hold, model, identity = holds[uid], selected[uid], context[uid]["identity"]
        assert hold["primaryHold"] == "terrain-contact"
        assert identity["exactObjectAndCSUID"] and identity["unrelatedIntersectingForms"] == 0
        sheet = hold["sourceSheet"]
        directory = SOURCES / sheet
        download = read(directory / "original/download.json")
        assert download["directorySHA256"] == read(directory / "directory/result.json")["directorySHA256"]
        source_path = Path(inputs[uid]["candidate"]["path"])
        assert sha(source_path) == model["sourceSHA256"]
        target = second.LOCAL / "assets" / (model["sourceSHA256"] + ".glb.gz")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copyfile(source_path, target)
        assert sha(target) == model["sourceSHA256"]
        triangles = second.glb_triangles(model)
        projection = shapely.union_all(shapely.polygons(triangles[:, :, [0, 2]]))
        cells = second.resolution.rectangle_for(model["native"]["model"]["worldBounds"], parent)
        bounds = second.resolution.extent(cells, parent)
        overlaps = [url for url, extent in installed if second.resolution.terrain.overlap(cells, extent)]
        fragments = []
        source_files = []
        for entry in download["entries"]:
            if entry["name"].startswith("TERRAIN") and entry["name"].endswith((".gltf", ".bin")):
                file = directory / "terrain" / entry["name"]
                assert sha(file) == entry["sha256"]
                source_files.append({"path": str(file.relative_to(ROOT)), "sha256": entry["sha256"]})
        for file in sorted((directory / "terrain").rglob("*.gltf")):
            native = second.terrain_triangles(file)
            within = ((native[:, :, 0].max(axis=1) >= bounds[0]) &
                      (native[:, :, 0].min(axis=1) <= bounds[2]) &
                      (native[:, :, 2].max(axis=1) >= bounds[1]) &
                      (native[:, :, 2].min(axis=1) <= bounds[3]) &
                      (native[:, :, 1].min(axis=1) >= 1.2))
            fragments.append(native[within])
        native = np.concatenate(fragments)
        assert len(native)
        native_projection = shapely.union_all(shapely.polygons(native[:, :, [0, 2]]))
        protected = projection.intersection(shapely.box(*bounds))
        missing = protected.difference(native_projection)
        outside = missing.difference(native_projection.buffer(.02))
        rings = model["source"]["building"]["rings"]
        target_projection = Polygon(rings[0], rings[1:])
        missing_inside_target = missing.intersection(target_projection).area
        parts = [part for part in shapely.get_parts(missing) if part.area > 1e-8]
        row = {"uid": uid, "name": hold["name"], "sheet": sheet,
               "modelSHA256": model["sourceSHA256"],
               "sourceDirectorySHA256": download["directorySHA256"],
               "sourceFiles": source_files, "cells": cells,
               "overlappingInstalledPatches": overlaps,
               "sourceModelTriangles": len(triangles), "sourceTerrainTriangles": len(native),
               "protectedProjectionAreaM2": protected.area,
               "missingUnderModelM2": missing.area,
               "missingInsideTargetFootprintM2": missing_inside_target,
               "missingOutsideTargetFootprintM2": missing.area - missing_inside_target,
               "missingFraction": missing.area / protected.area,
               "outsideTwoCentimetreSeamM2": outside.area,
               "largestMissingComponentM2": max((part.area for part in parts), default=0),
               "routing": "no-material-source-gap" if outside.area < 1e-8 else "source-terrain-gap-needs-contact-resolution",
               "humanStatus": "held-unknown", "primaryHold": "terrain-contact",
               "requiresAI": False, "requiresHuman": False,
               "nextWork": ("Run the full model contact and neighbour gates against the complete source TIN."
                            if outside.area < 1e-8 else
                            "Check adjacent government TIN sheets, then resolve the footprint gap using a source-preserving terrain method and rerun full contact, neighbour and browser gates."),
               "aiCalls": 0, "modelGeometryChanges": 0}
        rows.append(row)
        print(json.dumps({"uid": uid, "missingM2": round(missing.area, 3),
                          "outsideSeamM2": round(outside.area, 3),
                          "overlappingPatches": len(overlaps)}), flush=True)
        save(OUT, {"batch": BATCH, "stage": "source-terrain-gap-routing-v1",
                   "models": len(rows), "complete": len(rows) == len(UIDS), "rows": rows,
                   "inputEvidence": [ref(BASE / "reconciliation.json.gz"),
                                     ref(BASE / "selection.json.gz"),
                                     ref(ROOT / "3d-viewer/city/data/manifest.json"),
                                     ref(ROOT / "3d-viewer/city/data/terrain.json")],
                   "qualification": "This measures source TIN coverage from the primary sheet only. Adjacent sheets and safe contact repair have not been ruled out; no install decision follows from this routing pass.",
                   "aiCalls": 0, "modelGeometryChanges": 0, "publication": False})


def sync():
    report = read(OUT)
    assert report["complete"] and report["models"] == len(UIDS)
    claim = reservations.claim("codex-xl-source-gap-" + str(uuid.uuid4()),
                               ["building:" + uid for uid in UIDS], batch=BATCH)
    assert claim["ok"], claim
    receipt = claim["reservation"]
    try:
        job_id = jobs.enqueue(BATCH, report["stage"], {"evidence": ref(OUT), "aiCalls": 0})
        job = jobs.claim(BATCH, receipt["owner"], [report["stage"]], lease_seconds=1800)
        assert job and job["id"] == job_id
        recorded = {**report, "evidence": ref(OUT)}
        with connect() as connection:
            connection.row_factory = dict_row
            connection.execute("SELECT pg_advisory_xact_lock(%s)", (reservations.LOCK_ID,))
            assert reservations._current(connection, receipt)
            assert connection.execute(
                "UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() "
                "WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
                (Jsonb(recorded), job_id, job["owner"], job["token"])).rowcount == 1
        with connect() as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            assert connection.execute("SELECT result FROM astra_modelling.jobs WHERE id=%s",
                                      (job_id,)).fetchone()[0] == recorded
        save(RECEIPT, {"jobId": job_id, "evidence": ref(OUT), "resultVerified": True})
        print(json.dumps({"jobId": job_id, "models": len(UIDS), "aiCalls": 0}), flush=True)
    finally:
        reservations.release(receipt)


if __name__ == "__main__":
    sync() if len(sys.argv) > 1 and sys.argv[1] == "sync" else run()
