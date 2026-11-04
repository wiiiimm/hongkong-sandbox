"""Identify sampled buried source facets and their original wall/grade context.

This is evidence about the existing Silvercord burial flag, not a new structural
root gate, modified foundation limit, source edit or physical approval.
"""
import sys
import uuid
from collections import defaultdict, deque
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from observed_reserved_runner_v4_20261103 import execute_reserved
from original_assembly_four_world_pair_context_v3_20261101 import represented
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-buried-wall-grade-context-v1-20261103'
LOCAL = HERE / 'local' / BATCH
UID = 'landsd/233997:0'
RUNTIME = 'government-xl-silvercord-lippo-five-original-floor-runtime-v1-20261103'
ATTR = 'government-xl-silvercord-lippo-five-original-attributes-v2-20261103'
FOUNDATION = 'government-xl-silvercord-lippo-complete-floor-foundations-v1-20261103-233997-0'
LOW = 'government-xl-silvercord-lippo-complete-floor-low-faces-v1-20261103-233997-0'
GRADE = 'government-xl-silvercord-lippo-complete-floor-roles-v1-20261103-grade-233997-0'


def wall_grade_paths(triangles, targets, positive_grade_faces):
    """Original nonzero shared edges through wall-like source facets only."""
    tri = np.asarray(triangles, dtype=float)
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    walls = set(np.flatnonzero((lengths > 0) & (np.abs(normals[:, 1]) <= .25 * lengths)).tolist())
    targets, contacts = set(targets), set(positive_grade_faces)
    assert targets <= walls and all(0 <= i < len(tri) for i in contacts)
    roots = walls & contacts
    edges = defaultdict(list)
    for i in sorted(walls):
        for a, z in [(0, 1), (1, 2), (2, 0)]:
            left, right = tuple(tri[i, a]), tuple(tri[i, z])
            if left != right:
                edges[tuple(sorted([left, right]))].append(i)
    adjacency = defaultdict(list)
    for edge, faces in edges.items():
        for left in faces:
            adjacency[left].extend((right, edge) for right in faces if right != left)
    parent = {i: None for i in sorted(roots)}
    queue = deque(sorted(roots))
    while queue:
        face = queue.popleft()
        for other, edge in adjacency[face]:
            if other not in parent:
                parent[other] = (face, edge)
                queue.append(other)
    rows = []
    for target in sorted(targets):
        path, shared = [target], []
        current = target
        if current in parent:
            while parent[current] is not None:
                current, edge = parent[current]
                path.append(current)
                shared.append([list(p) for p in edge])
            assert current in roots
        rows.append(dict(sourceFace=target, reachesActualGradeWall=target in parent,
            originalWallFacePath=path if target in parent else [], sharedNonzeroOriginalEdges=shared,
            actualGradeWallFace=current if target in parent else None))
    return dict(actualGradeWallFaces=sorted(roots), paths=rows,
                unresolvedWallFaces=[r['sourceFace'] for r in rows if not r['reachesActualGradeWall']])


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease) and not (BASE / BATCH).exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, path):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(RUNTIME, BASE / RUNTIME / 'selection.json.gz')
    source = next(r for r in selection['rows'] if r['uid'] == UID)
    attr = next(r for r in take(ATTR, BASE / ATTR / 'attributes.json.gz')['rows'] if r['uid'] == UID)
    g = next(r for r in take(RUNTIME, HERE / 'local' / RUNTIME / 'runtime-geometry.json.gz')['rows'] if r['uid'] == UID)
    asset = ROOT / source['candidate']['path']
    assert digest(asset.read_bytes()) == source['sourceSHA256'] == attr['sourceSHA256'] == g['sourceSHA256']
    refs.append(asset)
    worlds = represented(attr, decode_original_world_triangles(asset.read_bytes()))
    ground = np.asarray(g['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    final = module('silvercord_buried_wall_sample_identity', HERE / 'xl-final-script-pass.py')
    summary = []
    for mode, tri in worlds.items():
        assert reservations.owns(lease)
        old_mode = {'leftF32': 'left', 'balancedF32': 'balanced'}.get(mode, mode)
        foundation_mode = {'leftF32': 'explicitLeftF32', 'balancedF32': 'explicitBalancedF32'}.get(mode, mode)
        low = take(LOW, BASE / LOW / (old_mode + '.json.gz'))
        raw = take(FOUNDATION, BASE / FOUNDATION / (foundation_mode + '.json'))
        grade = take(GRADE, BASE / GRADE / (mode + '.json.gz'))
        assert raw['sourceWorldSHA256'] == low['sourceWorldSHA256'] == grade['sourceWorldSHA256'] == digest(tri.tobytes())
        assert low['groundSHA256'] == grade['completeGroundSHA256'] == digest(ground.tobytes())
        assert grade['proof']['allPairsExamined'] and grade['proof']['sourceFacesOmitted'] == 0
        # The complete continuous partition already bounds every omitted face
        # above-.5m. Re-sample only its416possible-negative faces to identify the
        # original29 flagged by the unchanged foundation sampler.
        ids = np.asarray(sorted(r['sourceFace'] for r in low['rows']), dtype=int)
        assert len(ids) == 416 and len(set(ids)) == len(ids)
        lo, hi = tri.min((0, 1)), tri.max((0, 1))
        native = ground[(ground[:, :, 0].max(1) >= lo[0]-1) & (ground[:, :, 0].min(1) <= hi[0]+1)
                        & (ground[:, :, 2].max(1) >= lo[2]-1) & (ground[:, :, 2].min(1) <= hi[2]+1)]
        polygons = shapely.polygons(native[:, :, [0, 2]])
        valid = shapely.area(polygons) > 1e-10
        native, polygons = native[valid], polygons[valid]
        chosen = tri[ids]
        points = np.concatenate([chosen, chosen.mean(1)[:, None, :]], axis=1)
        heights = final.s.context.shared.samples(points[:, :, [0, 2]].reshape(-1, 2), native,
                                                shapely.STRtree(polygons)).reshape(-1, 4)
        gaps = points[:, :, 1] - heights
        assert np.isfinite(heights).all()
        buried = ids[(gaps < -.5).all(1)]
        normals = np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0])
        area = np.linalg.norm(normals, axis=1)/2
        f = raw['foundation']
        assert len(buried) == f['fullyBuriedTriangles'] == 29
        assert float(area[buried].sum()) == f['fullyBuriedAreaM2']
        assert float(area[buried].sum()/area.sum()) == f['fullyBuriedAreaFraction']
        lengths = 2*area
        walls = [int(i) for i in buried if lengths[i] > 0 and abs(normals[i, 1]) <= .25*lengths[i]]
        downward = sorted(set(map(int, buried))-set(walls))
        assert len(walls) == 23 and downward == [1347, 1348, 1349, 6240, 6241, 6242]
        contacts = [c for c in grade['proof']['contacts'] if c['dimension'] > 0
                    and c['sourcePrimitiveDimensionA'] == c['sourcePrimitiveDimensionB'] == 2]
        paths = wall_grade_paths(tri, walls, [c['sourceFaceA'] for c in contacts])
        record = dict(mode=mode, sourceWorldSHA256=digest(tri.tobytes()), completeGroundSHA256=digest(ground.tobytes()),
            sampledPossibleNegativeFaces=416, fullSourceFaces=len(tri), allOriginalBuriedFaceIds=buried.tolist(),
            originalBuriedWallFaceIds=walls, originalBuriedDownwardFaceIds=downward,
            rawFoundation=f, originalWallGradeContext=paths,
            positiveGradeContacts=[c for c in contacts if c['sourceFaceA'] in paths['actualGradeWallFaces']],
            sourceRoleAccepted=False, physicalAcceptance=False, installationApproved=False)
        save(BASE / BATCH / (mode + '.json.gz'), record)
        row = dict(mode=mode, originalBuriedFaces=29, originalBuriedAreaM2=f['fullyBuriedAreaM2'],
            originalBuriedAreaFraction=f['fullyBuriedAreaFraction'], buriedWalls=23, buriedDownwardFaces=6,
            actualGradeWallFaces=len(paths['actualGradeWallFaces']), wallOnlyPaths=sum(p['reachesActualGradeWall'] for p in paths['paths']),
            unresolvedWallFaceIds=paths['unresolvedWallFaces'])
        summary.append(row)
        print(row, flush=True)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.extend([manifest, HERE / 'xl-final-script-pass.py'])
    result = dict(uids=[UID], sourceSHA256=source['sourceSHA256'], rows=summary,
        allBuriedWallFacetsReachActualGradeViaOriginalWalls=all(not r['unresolvedWallFaceIds'] for r in summary),
        rawOrdinaryFoundationLimitStillFails=True, numericalGuardsChanged=False, sourceGeometryChanges=0,
        sourcePoseChanges=0, sourceRoleAccepted=False, physicalAcceptance=False, installationApproved=False,
        publication=False, qualification=__doc__ + ' Raw29facet/46.1328m2 burial accounting is reproduced exactly. '
        'Only416already proven possible-negative facets are sampled; no complete foundation calculation is repeated. '
        'Wall-only paths are original surface/actual-grade context, not new support roots or an engineering requirement.')
    save(BASE / BATCH / 'summary.json', result)
    module('buried_source_wall_actual_grade_context', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'four-world-exact-flagged-original-facet-wall-and-grade-context', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('silvercord-buried-wall-context-' + str(uuid.uuid4()),
            ['building:' + UID, 'immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
