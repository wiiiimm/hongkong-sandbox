"""Close every pair in the complete five-original assembly without repeating proofs."""
import sys
import uuid
from itertools import combinations
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from observed_reserved_runner_v4_20261103 import execute_reserved
from original_assembly_four_world_pair_context_v3_20261101 import represented
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-five-complete-original-pairs-v1-20261103'
LOCAL = HERE / 'local' / BATCH
RUNTIME = 'government-xl-silvercord-lippo-five-original-floor-runtime-v1-20261103'
ATTR = 'government-xl-silvercord-lippo-five-original-attributes-v2-20261103'
UIDS = ['landsd/233997:0', 'landsd/231645:0', 'landsd/237843:0', 'landsd/238659:0', 'landsd/239032:0']
OLD_PAIRS = ['government-xl-silvercord-lippo-original-contacts-v1-20261101'] + [
    'government-xl-silvercord-lippo-' + key + '-exact-podium-contacts-v1-20261103'
    for key in ['237843-0', '238659-0', '239032-0']]


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease) and not (BASE / BATCH).exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        path = BASE / batch / name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(RUNTIME, 'selection.json.gz')
    attributes = take(ATTR, 'attributes.json.gz')
    assert attributes['startEndAllInputsVerified']
    assert {r['uid'] for r in selection['rows']} == set(UIDS)
    attrs = {r['uid']: r for r in attributes['rows']}
    worlds, bounds, sources = {}, {}, {}
    for row in selection['rows']:
        uid = row['uid']
        asset = ROOT / row['candidate']['path']
        raw = asset.read_bytes()
        assert digest(raw) == row['sourceSHA256'] == attrs[uid]['sourceSHA256']
        refs.append(asset)
        sources[uid] = row['sourceSHA256']
        worlds[uid] = represented(attrs[uid], decode_original_world_triangles(raw))
        original_bounds = np.asarray(packed_world_bounds(raw)['originalWholeSourceBounds'])
        complete_positions = [np.asarray(attrs[uid][name]).reshape(-1, 3) for name in [
            'completeLiteralWorldPosition', 'completeExplicitLeftAssociatedFloat32WorldPosition',
            'completeExplicitBalancedFloat32WorldPosition']]
        points = np.concatenate([original_bounds, *complete_positions])
        assert np.isfinite(points).all()
        bounds[uid] = np.asarray([points.min(0), points.max(0)])
    cached = {}
    for name in OLD_PAIRS:
        data = take(name, 'summary.json')
        pair = tuple(data['uids'])
        assert len(pair) == 2 and len(set(pair)) == 2 and set(pair) <= set(UIDS)
        assert data['sourceSHA256ByUid'] == {uid: sources[uid] for uid in pair}
        key = frozenset(pair)
        assert key not in cached
        assert {r['mode'] for r in data['rows']} == {'original', 'literal', 'leftF32', 'balancedF32'}
        proof_rows = []
        for row in data['rows']:
            mode = row['mode']
            assert row['sourceWorldSHA256ByUid'] == {uid: digest(worlds[uid][mode].tobytes()) for uid in pair}
            proof = take(name, mode + '.json.gz')
            assert proof['allPairsExamined'] and proof['sourceFacesOmitted'] == 0
            assert len(proof['contacts']) == row['finiteContactPairs']
            proof_rows.append(dict(mode=mode, completeSourceFaces=[len(worlds[u][mode]) for u in pair],
                sourceWorldSHA256ByUid=row['sourceWorldSHA256ByUid'], finiteContactPairs=len(proof['contacts']),
                originalProof=dict(path=str((BASE / name / (mode + '.json.gz')).relative_to(ROOT)),
                                   sha256=pins[name][str((BASE / name / (mode + '.json.gz')).relative_to(ROOT))])))
        cached[key] = dict(uids=list(pair), method='reused-exact-complete-four-world-finite-proof',
                           rawProofBatch=name, modes=proof_rows)
    results, computed = [], 0
    for left, right in combinations(sorted(UIDS), 2):
        assert reservations.owns(lease)
        key = frozenset([left, right])
        if key in cached:
            results.append(cached[key])
            continue
        a, b = bounds[left], bounds[right]
        gaps = np.maximum(a[0] - b[1], b[0] - a[1])
        if np.any(gaps > 0):
            results.append(dict(uids=[left, right], method='strict-complete-four-world-POSITION-bounds-separation',
                completeBoundsByUid={left: a.tolist(), right: b.tolist()}, strictAxisGapsM=gaps.tolist()))
            continue
        modes = []
        for mode in worlds[left]:
            x, y = worlds[left][mode], worlds[right][mode]
            proof = exact_finite_contacts(x, range(len(x)), y, range(len(y)))
            assert proof['allPairsExamined'] and proof['sourceFacesOmitted'] == 0
            name = left.split('/')[1] + '--' + right.split('/')[1] + '--' + mode + '.json.gz'
            save(BASE / BATCH / name, proof)
            modes.append(dict(mode=mode, completeSourceFaces=[len(x), len(y)],
                sourceWorldSHA256ByUid={left: digest(x.tobytes()), right: digest(y.tobytes())},
                finiteContactPairs=len(proof['contacts'])))
        results.append(dict(uids=[left, right], method='fresh-complete-four-world-finite-proof', modes=modes))
        computed += 1
    assert len(results) == 10 and len({frozenset(r['uids']) for r in results}) == 10
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    refs.extend(HERE / n for n in ['original_assembly_four_world_pair_context_v3_20261101.py',
        'exact_packed_world_geometry_20261009.py', 'exact_packed_world_bounds_v3_20261010.py',
        'exact_original_finite_triangle_contacts_20261010.py'])
    result = dict(uids=UIDS, sourceSHA256ByUid=sources, completeUnorderedPairs=10, rows=results,
        reusedExactFinitePairs=len(cached), newlyComputedFinitePairs=computed,
        strictlySeparatedPairs=sum(r['method'].startswith('strict-') for r in results),
        rawContactsPreserved=True, sourceGeometryChanges=0, sourcePoseChanges=0,
        physicalAcceptance=False, installationApproved=False, publication=False, qualification=__doc__ +
        ' Every historical finite proof matches complete current four-world source hashes. Separation uses all original POSITION bounds and all literal/Float32 positions, including unused vertices. No contact or role approval transfers.')
    save(BASE / BATCH / 'summary.json', result)
    module('five_complete_original_pairs', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'complete-five-original-all-pairs-with-exact-reuse', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('five-complete-original-pairs-' + str(uuid.uuid4()),
            ['building:' + u for u in UIDS] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
