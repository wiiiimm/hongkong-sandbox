"""Plan a source-bounded terrain edit that excludes four unrelated BASIC forms.

No terrain is constructed or changed here. Every original building primitive,
including vertical/degenerate projections, contributes to the protected core.
"""
import argparse
import sys
import uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-southside-source-bound-terrain-mask-v1-20261028'
DOC, LOCAL = BASE/BATCH, HERE/'local'/BATCH
LEASE = LOCAL/'reservation.json'
CAP = BASE/'government-xl-southside-project-original-recovery-v1-20261028'
SUPPORT = BASE/'government-xl-southside-basic-podium-support-diagnostic-v1-20261028'
REGRESSION = BASE/'government-xl-southside-six-partition-basic-regressions-v1-20261028'
SCOPE = BASE/'government-xl-southside-six-partition-current-scope-v2-20261028'


def owned():
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    refs, pins = [Path(__file__), HERE/'exact_packed_world_geometry_20261009.py'], {}
    for batch in [CAP, SUPPORT, REGRESSION, SCOPE]:
        _, bound = authenticate(batch)
        refs.append(batch/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(CAP/'selection.json.gz')
    outside = [r['uid'] for r in take(SUPPORT/'summary.json')['rows'] if r['podiumProjectionCoverageM2'] == 0]
    assert len(selection['rows']) == 17 and len(outside) == 4
    required = {r['uid'] for r in selection['rows']} | set(outside)
    assert {'building:' + u for u in required} <= set(lease['resources'])
    geometries, source_rows, vertices = [], [], []
    for row in selection['rows']:
        asset = ROOT/row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256']
        refs.append(asset)
        tri = decode_original_world_triangles(asset.read_bytes())
        assert len(tri) == row['triangles']
        xz = tri[:, :, [0, 2]]
        polygons = shapely.polygons(xz)
        areas = shapely.area(polygons)
        geometries.extend(polygons[areas > 0])
        # A zero-area projected original face still has finite extent. Include
        # all three projected vertices/edges instead of silently discarding it.
        geometries.extend(shapely.linestrings(xz[areas == 0]))
        vertices.append(xz.reshape(-1, 2))
        source_rows.append(dict(uid=row['uid'], sourceSHA256=row['sourceSHA256'],
                                originalWorldSHA256=digest(tri.astype('<f8').tobytes()),
                                faces=len(tri), degenerateProjectedFaces=int((areas == 0).sum())))
    projection = shapely.union_all(geometries)
    core = projection.buffer(1.0)
    outer = core.buffer(10.0)
    assert core.is_valid and outer.is_valid and core.covers(projection)
    points = shapely.points(np.concatenate(vertices))
    assert shapely.covers(core, points).all()
    scope = take(SCOPE/'scope.json')
    domain = shapely.box(*scope['regionalParentExtent'])
    assert domain.covers(outer), 'New domain needed; do not silently truncate original-source core'
    forms = {r['building']['uid']: r['building'] for r in take(REGRESSION/'neighbour-inputs.json.gz')['rows']}
    rows = []
    for uid in outside:
        shape = shapely.GeometryCollection()
        for ring in forms[uid]['rings']:
            shape = shape.symmetric_difference(shapely.Polygon(ring))
        rows.append(dict(uid=uid, name=forms[uid].get('name'),
                         distanceFromCompleteSourceProjectionM=shape.distance(projection),
                         distanceFromProposedEditM=shape.distance(outer),
                         intersectionAreaM2=shape.intersection(outer).area,
                         disjointFromProposedEdit=shape.disjoint(outer)))
    result = dict(uids=sorted(r['uid'] for r in selection['rows']), sourceRows=source_rows,
                  outsideForms=rows, allFourOutsideFormsDisjoint=all(r['disjointFromProposedEdit'] for r in rows),
                  allOriginalVerticesInsideCore=True, coreHaloM=1.0, transitionWidthM=10.0,
                  sourceProjectionWKT=projection.wkt, nativeCoreWKT=core.wkt, proposedOuterEditWKT=outer.wkt,
                  originalDomainExtent=scope['regionalParentExtent'], terrainConstructed=False,
                  terrainGeometryChanges=0, sourceGeometryChanges=0, identityAccepted=False,
                  physicalAccepted=False, installationApproved=False,
                  qualification='Mask preflight only. Union of every original projected primitive across17 exact source units plus1m core halo and10m proposed transition. Disjoint outside forms can retain the original parent surface without clipping a required original building primitive. No terrain mesh, interpolation, source-height, root-boundary, seam, current-map, neighbour or browser acceptance is implied; any constructed candidate requires new evidence.')
    save(DOC/'summary.json', result)
    assert reservations.owns(lease)
    module('southside_source_bound_terrain_mask_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'complete-original-source-terrain-edit-mask-preflight', list(dict.fromkeys(refs)), result)
    print(dict(allOriginalVerticesInsideCore=True, outsideForms=rows, noTerrainConstructed=True), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    if args.owned:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    authenticate(CAP); authenticate(SUPPORT)
    resources = {r['uid'] for r in read(CAP/'selection.json.gz')['rows']}
    resources.update(r['uid'] for r in read(SUPPORT/'summary.json')['rows'] if r['podiumProjectionCoverageM2'] == 0)
    claim = reservations.claim('southside-source-bound-mask-' + str(uuid.uuid4()),
                               ['building:' + u for u in sorted(resources)], batch=BATCH, ttl=3600)
    assert claim['ok']
    execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])


if __name__ == '__main__':
    main()
