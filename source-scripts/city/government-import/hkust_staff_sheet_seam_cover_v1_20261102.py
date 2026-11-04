"""Apply the existing 20mm source-sheet seam route to the measured HKUST seam.

This is separate from the unchanged 2mm Float32 repair. The exact measured
missing domain and its two-sheet provenance must match. No model is modified;
all final terrain, source, neighbour and publication checks remain mandatory.
"""
import json
import numpy as np
import shapely
from run import ROOT, HERE, read, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from native_patch_resolution import _height_on_source_edge
from original_source_plane_clipping_v1_20261101 import from_original_facet

CONTEXT = ROOT / 'docs/astra-city/government-import/government-xl-hkust-staff-three-terrain-gap-v1-20261102'
SOURCES = {
    'landsd/309822:0': '56fe512572733202ce049360e08fe0effc15919bec6e296ac667e06f867c957f',
    'landsd/232155:0': '411cf6b0ee4ec5ab1df5fadcb0e62ad79ac41a377df39525f4e63d4a05565732',
    'landsd/29031:0': '8c9fa611c9fefff0823e3acc12a6fe4db342b61f249fde30d601ae314a80d1e1',
}


def cover(source, projection):
    receipt, pins = authenticate(CONTEXT)
    assert receipt['sourceSHA256ByUid'] == SOURCES
    refs = []
    for name in ['summary.json', 'gap-context.json', 'missing-geometry.json']:
        path = CONTEXT / name
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == pins[str(manifest.relative_to(ROOT))]
    source = np.asarray(source, dtype='<f8')
    assert source.ndim == 3 and source.shape[1:] == (3, 3) and np.isfinite(source).all()
    polygons = shapely.polygons(source[:, :, [0, 2]])
    assert np.all(shapely.area(polygons) > 0)
    union = shapely.union_all(polygons)
    missing = projection.difference(union)
    measured = shapely.from_geojson((CONTEXT / 'missing-geometry.json').read_text())
    assert missing.symmetric_difference(measured).area < 1e-8, 'Not the exact measured source-sheet gap'
    assert 0 < missing.area <= .25
    # Both pinned terrain records meet at this northing. Restrict this route to
    # the recorded sheet boundary, rather than admitting arbitrary model holes.
    assert missing.difference(shapely.box(-1e9, -5700.02, 1e9, -5699.98)).area < 1e-8
    tolerance = .02  # Existing fill_narrow_source_seam default, unchanged.
    assert missing.difference(union.buffer(tolerance)).area < 1e-8
    tree = shapely.STRtree(polygons)
    additions, planes, domains = [], [], []
    for triangle in shapely.get_parts(shapely.constrained_delaunay_triangles(missing)):
        if triangle.geom_type != 'Polygon':
            assert triangle.area == 0
            continue
        assert triangle.area > 0
        face = np.asarray([[x, _height_on_source_edge(shapely.Point(x, z), source, polygons, tree), z]
                           for x, z in list(triangle.exterior.coords)[:3]], dtype='<f8')
        assert face[:, 1].min() >= 1.2
        coefficients = np.asarray(from_original_facet(face), dtype=float)
        assert np.isfinite(coefficients).all()
        additions.append(face)
        planes.append(coefficients)
        domains.append(triangle)
    assert additions and shapely.union_all(domains).symmetric_difference(missing).area < 1e-10
    result = np.concatenate([source, np.asarray(additions)])
    assert np.array_equal(result[:len(source)], source)
    after = projection.difference(shapely.union_all(shapely.polygons(result[:, :, [0, 2]])))
    assert after.area < 1e-6
    proof = dict(policy='Existing 20mm source-sheet nearest-provider-edge repair, restricted to exact measured HKUST two-sheet boundary gap. Separate from the unchanged 2mm Float32 repair.',
                 sourceSheetSeamToleranceM=tolerance, maximumSeamAreaM2=.25,
                 beforeMissingAreaM2=float(missing.area), afterMissingAreaM2=float(after.area),
                 retainedProviderFaces=len(source), addedTerrainFaces=len(additions),
                 measuredGapJobId=receipt['jobId'], sourceSHA256ByUid=SOURCES,
                 evidenceRefs=[dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes()))
                               for p in refs + [CONTEXT / 'result.json', HERE / 'native_patch_resolution.py']],
                 buildingGeometryChanges=0, installationApproved=False)
    return result, planes, proof
