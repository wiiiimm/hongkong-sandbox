"""Exact finite-grade interface and original shared-edge path for one held wall.

Immutable historical source evidence only. Raw clearance failure stays false;
no wall burial role, physical acceptance, changed tolerance or publication credit.
"""
import uuid
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_paths
from exact_original_triangle_pair_column_gap_20261010 import verify as column_gap
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-nam-cheong-wall-grade-path-v1-20261023'
UID = 'landsd/268867:0'
FACE = 11390


def canonical(value):
    import json
    return digest(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    batches = dict(runtime='government-xl-nam-cheong-fu-yun-joint-current-v1-20261023-runtime', attributes='government-xl-nam-cheong-fu-yun-joint-attributes-v1-20261023', continuous='government-xl-nam-cheong-joint-prephysical-v2-20261023-continuous', exact='government-xl-nam-cheong-wall-exact-clearance-v1-20261023')
    for batch in batches.values():
        _, bound = authenticate(BASE / batch)
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha
        refs.append(BASE / batch / 'result.json')

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    source = next(r for r in take(BASE / batches['runtime'] / 'selection.json.gz')['rows'] if r['uid'] == UID)
    geometry = next(r for r in take(HERE / 'local' / batches['runtime'] / 'runtime-geometry.json.gz')['rows'] if r['uid'] == UID)
    attributes = next(r for r in take(BASE / batches['attributes'] / 'attributes.json.gz')['rows'] if r['uid'] == UID)
    context = take(BASE / batches['continuous'] / '268867:0.json.gz')
    raw_negative = take(BASE / batches['exact'] / 'summary.json')
    assert context['continuousAffectedFaces'] == [FACE]
    assert all(not r['unchangedClearancePass'] for r in raw_negative['rows'])
    asset = ROOT / source['candidate']['path']
    assert digest(asset.read_bytes()) == source['sourceSHA256'] == attributes['sourceSHA256'] == 'ad26b1580c54a6700733a28643862ea7939f84c0254de9a2371f5aec91cae12d'
    refs.append(asset)
    ix = np.asarray(attributes['completeOriginalIndex']).reshape(-1, 3)
    modes = {name: np.asarray(attributes[key]).reshape(-1, 3)[ix] for name, key in [('literal', 'completeLiteralWorldPosition'), ('left', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balanced', 'completeExplicitBalancedFloat32WorldPosition')]}
    modes['original'] = decode_original_world_triangles(asset.read_bytes())
    ground = np.asarray(geometry['drawnGroundGeometry']).reshape(-1, 3, 3)
    assert digest(ground.tobytes()) == context['sourceBinding']['drawnGroundSHA256']
    assert digest(modes['literal'].tobytes()) == context['sourceBinding']['decodedWorldTrianglesSHA256']
    binding = dict(completeOriginalWorldTrianglesSHA256=digest(modes['literal'].tobytes()), completeCurrentFacetContextsSHA256=canonical(context['faces']), exactOriginalContactListSHA256=canonical([]))
    # Reuse measured contexts only to discover a candidate path. Every chosen
    # non-wall cap is then checked independently with exact column arithmetic.
    path_report = cap_paths(modes['literal'], context['faces'], [], expected_binding=binding, current_binding=binding)
    candidate = next(r for r in path_report['paths'] if r['sourceFace'] == FACE)
    path = candidate['originalPath']
    save(out / 'candidate-path.json', dict(candidate=candidate, discoveredFromFloatingContexts=True, rootOrBurialRoleCredit=False))
    assert candidate['hasExactOriginalStrictClearCapRoofPath'], 'No original shared-edge cap path found; no approval inferred'
    claim = reservations.claim('nam-cheong-wall-grade-' + str(uuid.uuid4()), ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
    assert claim['ok']
    lease = claim['reservation']
    try:
        rows = []
        xz = ground[:, :, [0, 2]]
        for mode, triangles in modes.items():
            assert len(triangles) == 16377
            edges = []
            for a, b in zip(path, path[1:]):
                shared = sorted(set(map(tuple, triangles[a])) & set(map(tuple, triangles[b])))
                assert len(shared) >= 2 and shared[0] != shared[-1]
                edges.append(dict(originalFaces=[a, b], sharedOriginalEndpoints=[list(p) for p in shared]))
            caps = []
            for index in candidate['strictClearNonWallFaces']:
                face = triangles[index]
                normal = np.cross(face[1] - face[0], face[2] - face[0])
                assert abs(normal[1]) / np.linalg.norm(normal) > .25
                ids = np.flatnonzero(np.all(xz.max(1) >= face[:, [0, 2]].min(0), axis=1) & np.all(xz.min(1) <= face[:, [0, 2]].max(0), axis=1))
                proofs = [dict(groundFace=int(i), proof=column_gap(face, ground[i])) for i in ids]
                gaps = [Fraction(r['proof']['exactMinimumFiniteColumnGapM']) for r in proofs if r['proof']['exactClosedHorizontalProjectionsMeet']]
                assert gaps
                minimum = min(gaps)
                caps.append(dict(sourceFace=index, exactMinimumGapM=str(minimum), ordinaryClearancePass=minimum >= Fraction(-1, 2), completeAABBCandidates=list(map(int, ids)), proofs=proofs))
            grade = exact_upper_ground_interfaces(triangles, [FACE], ground)
            normal = np.cross(triangles[FACE, 1] - triangles[FACE, 0], triangles[FACE, 2] - triangles[FACE, 0])
            record = dict(mode=mode, completeSourceFaces=len(triangles), completeGroundFaces=len(ground), sourceWorldSHA256=digest(triangles.tobytes()), groundSHA256=digest(ground.tobytes()), wallNormalYRatio=float(normal[1] / np.linalg.norm(normal)), originalPath=path, exactSharedEdges=edges, exactNonWallCaps=caps, exactFiniteUpperGradeInterfaces=grade, allChosenCapsOrdinaryClear=bool(caps) and all(r['ordinaryClearancePass'] for r in caps), positiveUpperGradeInterface=bool(grade), rawClearanceFailurePreserved=True, rootOrBurialRoleCredit=False, installationApproved=False)
            save(out / (mode + '.json.gz'), record)
            rows.append({k: v for k, v in record.items() if k not in ['exactNonWallCaps', 'exactFiniteUpperGradeInterfaces', 'exactSharedEdges']})
            assert reservations.heartbeat(lease)['ok']
            print(rows[-1], flush=True)
        refs.extend(HERE / name for name in ['exact_packed_world_geometry_20261009.py', 'original_strict_clear_cap_wall_paths_20261009.py', 'exact_original_triangle_pair_column_gap_20261010.py', 'exact_original_upper_ground_interfaces_20261009.py'])
        summary = dict(uids=[UID], sourceSHA256=source['sourceSHA256'], sourceFace=FACE, rows=rows, sourceGeometryChanges=0, sourcePoseChanges=0, historicalCurrentCaptureOnly=True, currentRegionalRebindRequired=True, rawClearanceFailures=raw_negative['rows'], rawClearanceFailurePreserved=True, physicalAccepted=False, installationApproved=False, permanentRejection=False, qualification='Candidate mesh-edge cap path discovered from prior floating contexts, then chosen cap clearance and finite upper-grade interfaces checked independently with exact arithmetic in all four coordinate streams. No geometry/terrain edit, numerical tolerance change, below-grade wall-role interpretation, structural/root approval, current-map rebind or publication credit.')
        save(out / 'summary.json', summary)
        module('nam_wall_grade_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'original-nam-cheong-wall-finite-grade-cap-path-context', refs, summary)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
