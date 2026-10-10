"""Measure every missing Man Hei region against literal upward Man Fuk floors.

Read-only source investigation. This neither accepts paired identity nor grants
support, collision, terrain, or installation credit. Old identity failures stay.
"""
import importlib.util
import json
from pathlib import Path

import numpy as np
import shapely

from run import ROOT, HERE, read, save, digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_slab_projection_coverage_20261010 import slab_coverage
from exact_original_polygon_triangle_partition_20261010 import exact_partition
from source_closed_components import components

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-man-hei-original-platform-missing-floor-diagnostic-20261010'
DOC = BASE / BATCH
UPPER = BASE / 'government-xl-man-fuk-nine-current-identity-75694-0-20261010'
PLATFORM = BASE / 'government-xl-man-fuk-complete-retained-original-physical-v5-20261010'
SHA = {'landsd/75694:0': '88baf17aa03fad5a07e68830b3ada8ba1cbda14160e82e97408b9b07acc7db01',
       'landsd/266062:0': '22b458321ca483c53324ee152cb27c382e5ac4dfd745974f169b1c551ac8a6c1'}


def main():
    assert not DOC.exists()
    upper_row = read(UPPER / 'selection.json.gz')['rows'][0]
    platform_row = read(PLATFORM / 'selection.json.gz')['rows'][0]
    arrays = []
    assets = []
    for row, count in [(upper_row, 2286), (platform_row, 10661)]:
        raw_path = ROOT / row['candidate']['path']
        raw = raw_path.read_bytes()
        assert digest(raw) == row['sourceSHA256'] == SHA[row['uid']]
        tri = decode_original_world_triangles(raw)
        assert tri.shape == (count, 3, 3) and np.isfinite(tri).all()
        arrays.append(tri)
        assets.append(raw_path)
    upper, platform = arrays
    target = shapely.GeometryCollection()
    for ring in upper_row['source']['building']['rings']:
        target = target.symmetric_difference(shapely.Polygon(ring))
    assert target.is_valid and target.area > 0
    projection = shapely.union_all(shapely.polygons(upper[:, :, [0, 2]]))
    missing = target.difference(projection)
    assert not missing.is_empty
    normal = np.cross(platform[:, 1] - platform[:, 0], platform[:, 2] - platform[:, 0])
    suppliers = [i for i, t in enumerate(platform) if normal[i, 1] > 0
                 and shapely.Polygon(t[:, [0, 2]]).intersection(missing).area > 0]
    assert suppliers
    topology = components(platform)['components']
    owner = {i: k for k, part in enumerate(topology) for i in part['faceIndices']}
    rows = []
    for polygon in shapely.get_parts(missing):
        assert polygon.geom_type == 'Polygon'
        rings = [list(polygon.exterior.coords)[:-1]] + [list(h.coords)[:-1] for h in polygon.interiors]
        proof_triangles = [np.asarray(t.exterior.coords)[:3] for t in
                           shapely.get_parts(shapely.constrained_delaunay_triangles(polygon))]
        partition = exact_partition(rings, [t.tolist() for t in proof_triangles])
        facets = []
        for t in proof_triangles:
            literal = np.column_stack([t[:, 0], np.zeros(3), t[:, 1]])
            facets.append({'literalMissingRegionProofFacet': literal.tolist(),
                           'completeOriginalUpwardFloorCoverage': slab_coverage(literal, platform[suppliers])})
        rows.append({'literalReportedMissingRegion': json.loads(shapely.to_geojson(polygon)),
                     'independentLiteralBoundaryPartition': partition, 'allFiniteFacets': facets})
    files = [Path(__file__), UPPER / 'selection.json.gz', UPPER / 'identity.json',
             PLATFORM / 'selection.json.gz', *assets,
             HERE / 'exact_original_slab_projection_coverage_20261010.py',
             HERE / 'exact_original_polygon_triangle_partition_20261010.py',
             HERE / 'exact_packed_world_geometry_20261009.py', HERE / 'source_closed_components.py']
    result = dict(uid=upper_row['uid'], requiredOriginalPlatformUID=platform_row['uid'],
                  sourceSHA256s=SHA, completeOriginalFaceCounts=[2286, 10661],
                  rawStandaloneIdentity=read(UPPER / 'identity.json'),
                  rawMissingCurrentTargetAreaM2=missing.area,
                  allOriginalSupplyingUpwardFaces=[dict(sourceFace=i, originalComponent=owner[i],
                      completeLiteralOriginalTriangle=platform[i].tolist()) for i in suppliers],
                  completeMissingRegionDispositions=rows,
                  allLiteralMissingRegionFacetsCovered=all(f['completeOriginalUpwardFloorCoverage']['exactProjectionCovered']
                      for r in rows for f in r['allFiniteFacets']),
                  sourceGeometryChanges=0, identityAccepted=False, physicalAccepted=False,
                  installationApproved=False, supportOrTerrainCredit=False,
                  qualification='Exact proofs apply to every literal reported difference polygon and its complete boundary partition. Current/provider paired identity, complete original positive contacts and metadata floor span still need independent checks.',
                  evidenceRefs=[dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())) for p in files])
    save(DOC / 'diagnostic.json.gz', result)
    spec = importlib.util.spec_from_file_location('freeze_man_hei_missing', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    freeze = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(freeze)
    freeze.freeze(BATCH, 'complete-original-man-hei-missing-upward-floor-diagnostic-v1', files,
                  dict(uids=sorted(SHA), allLiteralMissingRegionFacetsCovered=result['allLiteralMissingRegionFacetsCovered'],
                       identityAccepted=False, physicalAccepted=False, installationApproved=False, sourceGeometryChanges=0))
    print(json.dumps(dict(missingAreaM2=missing.area, supplyingFaces=len(suppliers),
                          completeMissingRegions=len(rows), allCovered=result['allLiteralMissingRegionFacetsCovered'])), flush=True)


if __name__ == '__main__':
    main()
