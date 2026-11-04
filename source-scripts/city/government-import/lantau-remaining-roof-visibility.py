"""Measure upward original mesh faces above source terrain for Discovery Bay holds."""
import gzip
import importlib.util
import json
from pathlib import Path
import numpy as np
import shapely

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BATCH = "government-discovery-bay-1103-20260921"
LOCAL = HERE / "local" / BATCH
DOC = ROOT / "docs/astra-city/government-import" / BATCH
IDS = ("landsd/176056:0", "landsd/190939:0", "landsd/192500:0", "landsd/288285:0")

def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith(".gz") else raw)

def main():
    spec = importlib.util.spec_from_file_location("exact", HERE / "discovery-bay-exact-pass.py")
    exact = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exact)
    rows = {r["uid"]: r for r in read(LOCAL / "geometry.json.gz")["rows"]}
    proofs = {r["uid"]: r for r in read(DOC / "exact-pass-results.json.gz")["rows"]}
    result = []
    for uid in IDS:
        triangles = exact.geometry_triangles(rows[uid])
        sheet = proofs[uid]["sourceSheet"]
        terrain = np.concatenate([exact.context.triangles(path) for path in sorted((LOCAL / "source-terrain" / sheet / "decoded").rglob("*.gltf"))])
        lo, hi = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
        nearby = terrain[
            (terrain[:, :, 0].max(axis=1) >= lo[0] - 1)
            & (terrain[:, :, 0].min(axis=1) <= hi[0] + 1)
            & (terrain[:, :, 2].max(axis=1) >= lo[2] - 1)
            & (terrain[:, :, 2].min(axis=1) <= hi[2] + 1)
        ]
        polygons = shapely.polygons(nearby[:, :, [0, 2]])
        valid = shapely.area(polygons) > 1e-10
        nearby, polygons = nearby[valid], polygons[valid]
        points = np.concatenate([triangles, triangles.mean(axis=1)[:, None, :]], axis=1)
        heights = exact.context.shared.samples(points[:, :, [0, 2]].reshape(-1, 2), nearby,
                                               shapely.STRtree(polygons)).reshape(-1, 4)
        gaps = points[:, :, 1] - heights
        cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
        area = np.linalg.norm(cross, axis=1) / 2
        upward = cross[:, 1] > 0.25 * np.linalg.norm(cross, axis=1)
        finite = np.isfinite(gaps).all(axis=1)
        visible = finite & (gaps > 0.25).all(axis=1)
        partial = finite & (gaps > 0.25).any(axis=1)
        row = {"uid": uid, "sourceSheet": sheet, "triangles": len(triangles),
               "upwardTriangles": int(upward.sum()),
               "upwardAreaM2": float(area[upward].sum()),
               "fullyVisibleUpwardAreaM2": float(area[upward & visible].sum()),
               "partlyVisibleUpwardAreaM2": float(area[upward & partial].sum()),
               "minimumUpwardGapM": float(gaps[upward & finite].min()) if (upward & finite).any() else None,
               "maximumUpwardGapM": float(gaps[upward & finite].max()) if (upward & finite).any() else None,
               "aiCalls": 0, "geometryChanges": 0}
        result.append(row)
    out = DOC / "remaining-roof-visibility.json"
    out.write_text(json.dumps({"rows": result, "sourceGeometryPreserved": True}, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
