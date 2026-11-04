# V4 expands only diagnostic assembly capacity16→24; exact source/cache parity,
# pair completeness, contact math and lease/approval guards remain unchanged.
"""Extend exact source assemblies, reusing only identical complete pair inputs.

No source-role, scene, physical or publication approval transfers with a cache hit.
"""
import argparse
import sys
import uuid
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np

from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module


MODES = [('literal', 'completeLiteralWorldPosition'),
         ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
         ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]


def require_same_worlds(current, cached):
    assert set(current) == set(cached) == {'original', *(m for m, _ in MODES)}
    for mode in current:
        left, right = current[mode], cached[mode]
        assert left.dtype == right.dtype and left.shape == right.shape
        assert left.tobytes() == right.tobytes(), 'Complete represented pair input changed: ' + mode


def represented(attr, original):
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    return {'original': original, **{m: np.asarray(attr[f], dtype='<f8').reshape(-1, 3)[ix]
                                    for m, f in MODES}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['batch', 'runtime', 'attributes']:
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--reuse', action='append', default=[],
                        help='completed-pair-batch,its-source-attributes-batch')
    parser.add_argument('--lease')
    args = parser.parse_args()
    reuse = [v.split(',') for v in args.reuse]
    assert all(len(v) == 2 for v in reuse)
    names = [args.batch, args.runtime, args.attributes, *[n for pair in reuse for n in pair]]
    assert all(n.startswith('government-xl-') and '/' not in n for n in names)
    base = ROOT / 'docs/astra-city/government-import'
    out, local = base / args.batch, HERE / 'local' / args.batch
    assert not out.exists()
    if not args.lease:
        assert not local.exists()
        selection = read(base / args.runtime / 'selection.json.gz')
        uids = [r['uid'] for r in selection['rows']]
        assert 2 <= len(uids) == len(set(uids)) <= 24
        claim = reservations.claim('cached-original-pairs-' + str(uuid.uuid4()),
                                   ['building:' + u for u in uids], batch=args.batch, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], local / 'reservation.json',
                                [sys.executable, __file__, *sys.argv[1:],
                                 '--lease', str(local / 'reservation.json')])
    lease = read(Path(args.lease))
    pins, refs = {}, [Path(__file__)]

    def take(batch, path):
        if batch not in pins:
            _, pins[batch] = authenticate(base / batch)
            refs.append(base / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(args.runtime, base / args.runtime / 'selection.json.gz')
    attributes = take(args.attributes, base / args.attributes / 'attributes.json.gz')
    assert attributes['startEndAllInputsVerified']
    attrs = {r['uid']: r for r in attributes['rows']}
    sources, worlds = {}, {}
    assert reservations.owns(lease)
    for row in selection['rows']:
        uid = row['uid']
        assert 'building:' + uid in lease['resources'] and uid not in worlds
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == attrs[uid]['sourceSHA256']
        refs.append(asset)
        worlds[uid] = represented(attrs[uid], decode_original_world_triangles(asset.read_bytes()))
        assert all(len(t) == row['triangles'] for t in worlds[uid].values())
        sources[uid] = row['sourceSHA256']
    assert 2 <= len(worlds) <= 24
    cache = {}
    for batch, attribute_batch in reuse:
        previous = take(batch, base / batch / 'summary.json')
        old_attrs = take(attribute_batch, base / attribute_batch / 'attributes.json.gz')
        assert old_attrs['startEndAllInputsVerified']
        old_attrs = {r['uid']: r for r in old_attrs['rows']}
        decoder = HERE / 'exact_packed_world_geometry_20261009.py'
        assert pins[batch][str(decoder.relative_to(ROOT))] == digest(decoder.read_bytes())
        for uid, sha in previous['sourceSHA256ByUid'].items():
            assert sources[uid] == sha == old_attrs[uid]['sourceSHA256']
            require_same_worlds(worlds[uid], represented(old_attrs[uid], worlds[uid]['original']))
        for old in previous['rows']:
            # Explicit-pair and complete-assembly receipts keep their raw A/B orientation.
            u, v = (old['uid'], old['peerUid']) if 'uid' in old else previous['uids']
            mode = old['mode']
            a, b = worlds[u][mode], worlds[v][mode]
            hashes = {u: digest(a.tobytes()), v: digest(b.tobytes())}
            if 'sourceWorldSHA256ByUid' in old:
                assert old['sourceWorldSHA256ByUid'] == hashes
            row = dict(uid=u, peerUid=v, mode=mode, completeSourceFaces=len(a),
                       completePeerFaces=len(b), sourceWorldSHA256ByUid=hashes,
                       reusedFrom=batch, approvalTransferred=False)
            if old.get('strictBoundsSeparated'):
                gaps = np.maximum(a.min((0, 1)) - b.max((0, 1)), b.min((0, 1)) - a.max((0, 1)))
                assert np.any(gaps > 0) and gaps.tolist() == old['axisGapsM']
                assert len(a) == old['completeSourceFaces'] and len(b) == old['completePeerFaces']
                row.update(strictBoundsSeparated=True, axisGapsM=gaps.tolist())
            else:
                path = ROOT / old['rawPath'] if 'rawPath' in old else base / batch / (mode + '.json.gz')
                raw = take(batch, path)
                assert raw['allPairsExamined'] and raw['sourceFacesOmitted'] == 0
                expected = old['finiteContactPairs'] if 'finiteContactPairs' in old else sum(old['contactDimensions'].values())
                assert len(raw['contacts']) == expected
                row.update(strictBoundsSeparated=False, rawPath=str(path.relative_to(ROOT)),
                           contactDimensions=dict(Counter(str(c['dimension']) for c in raw['contacts'])),
                           positiveSurfaceContacts=sum(c['dimension'] > 0 and c['sourcePrimitiveDimensionA'] == c['sourcePrimitiveDimensionB'] == 2 for c in raw['contacts']))
            key = (frozenset([u, v]), mode)
            assert key not in cache, 'Duplicate cached pair declaration'
            cache[key] = row
    rows, newly_solved = [], 0
    for u, v in combinations(sorted(worlds), 2):
        assert reservations.owns(lease)
        for mode in ['original', *(m for m, _ in MODES)]:
            key = (frozenset([u, v]), mode)
            if key in cache:
                rows.append(cache[key])
                continue
            a, b = worlds[u][mode], worlds[v][mode]
            gaps = np.maximum(a.min((0, 1)) - b.max((0, 1)), b.min((0, 1)) - a.max((0, 1)))
            row = dict(uid=u, peerUid=v, mode=mode, completeSourceFaces=len(a), completePeerFaces=len(b),
                       sourceWorldSHA256ByUid={u: digest(a.tobytes()), v: digest(b.tobytes())})
            if np.any(gaps > 0):
                row.update(strictBoundsSeparated=True, axisGapsM=gaps.tolist())
            else:
                raw = exact_finite_contacts(a, range(len(a)), b, range(len(b)))
                assert raw['allPairsExamined'] and raw['sourceFacesOmitted'] == 0
                path = out / (u.split('/')[1] + '--' + v.split('/')[1] + '--' + mode + '.json.gz')
                save(path, raw)
                row.update(strictBoundsSeparated=False, rawPath=str(path.relative_to(ROOT)),
                           contactDimensions=dict(Counter(str(c['dimension']) for c in raw['contacts'])),
                           positiveSurfaceContacts=sum(c['dimension'] > 0 and c['sourcePrimitiveDimensionA'] == c['sourcePrimitiveDimensionB'] == 2 for c in raw['contacts']))
                newly_solved += 1
            rows.append(row)
        print(dict(pair=[u, v], reusedModes=sum('reusedFrom' in r for r in rows[-4:])), flush=True)
    expected = {(frozenset(pair), mode) for pair in combinations(worlds, 2) for mode in worlds[next(iter(worlds))]}
    assert len(rows) == len(expected) and {(frozenset([r['uid'], r['peerUid']]), r['mode']) for r in rows} == expected
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] and reservations.owns(lease)
    result = dict(uids=sorted(worlds), sourceSHA256ByUid=sources, rows=rows,
                  completeUnorderedPairs=len(worlds) * (len(worlds) - 1) // 2, coordinateModes=4,
                  reusedPairModeRows=len(cache), newFinitePairModeComputations=newly_solved,
                  installationApproved=False, physicalAcceptance=False, sourceGeometryChanges=0,
                  qualification='Every pair covered in four worlds. Reuse requires exact source SHA, unchanged decoder and byte-identical complete represented indexed arrays; saved raw contacts and canonical source A/B orientation retained. Only newly introduced pair inputs are solved. No prior scene, support, source-role, identity or publication approval transfers.')
    save(out / 'summary.json', result)
    refs.extend([manifest, HERE / 'exact_packed_world_geometry_20261009.py',
                 HERE / 'exact_original_finite_triangle_contacts_20261010.py'])
    module('cached_four_world_pair_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        args.batch, 'complete-four-world-original-pairs-with-identical-input-reuse', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
