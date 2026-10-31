"""Bind completed assembly intersections to existing two-source diagnostic tools.

Copies authenticated contact bytes; never recalculates contacts, changes source
order, grants acceptance, or modifies original geometry or runtime assets.
"""
import argparse
from copy import deepcopy
from pathlib import Path
import sys
import uuid

import numpy as np

from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


MODES = {'original', 'literal', 'leftF32', 'balancedF32'}


def pair_rows(assembly, uid, peer):
    assert uid != peer and {uid, peer} <= set(assembly['uids'])
    rows = [deepcopy(r) for r in assembly['rows']
            if {r['uid'], r['peerUid']} == {uid, peer}]
    assert len(rows) == 4 and {r['mode'] for r in rows} == MODES
    order = [rows[0]['uid'], rows[0]['peerUid']]
    assert all([r['uid'], r['peerUid']] == order for r in rows)
    assert set(order) == {uid, peer}
    return order, rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'attributes', 'assembly', 'peer']:
        p.add_argument('--' + key, required=True)
    p.add_argument('--uid', action='append', required=True)
    p.add_argument('--owned', action='store_true')
    args = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n
               for n in [args.batch, args.runtime, args.attributes, args.assembly])
    assert 0 < len(args.uid) == len(set(args.uid)) <= 16 and args.peer not in args.uid
    base = ROOT / 'docs/astra-city/government-import'
    out, local = base / args.batch, HERE / 'local' / args.batch
    assert not out.exists()
    actors = [args.peer, *args.uid]
    if not args.owned:
        assert not local.exists()
        claim = reservations.claim('original-pair-rebind-' + str(uuid.uuid4()),
                                   sorted('building:' + u for u in actors),
                                   batch=args.batch, ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'], local / 'reservation.json',
                                [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    refs, pins = [Path(__file__)], {}

    def take(batch, filename):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        path = base / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    assembly = take(args.assembly, 'summary.json')
    selection = take(args.runtime, 'selection.json.gz')
    attrs_path = base / args.attributes / 'attributes.json.gz'
    attrs = {r['uid']: r for r in take(args.attributes, 'attributes.json.gz')['rows']}
    assert digest(attrs_path.read_bytes()) == pins[args.assembly][str(attrs_path.relative_to(ROOT))]
    selection_path = base / args.runtime / 'selection.json.gz'
    assert digest(selection_path.read_bytes()) == pins[args.assembly][str(selection_path.relative_to(ROOT))]
    decoder = HERE / 'exact_packed_world_geometry_20261009.py'
    assert digest(decoder.read_bytes()) == pins[args.assembly][str(decoder.relative_to(ROOT))]
    refs.append(decoder)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_sha = digest(manifest.read_bytes())
    assert manifest_sha == selection['manifestSHA256'] == pins[args.assembly][str(manifest.relative_to(ROOT))]
    refs.append(manifest)
    sources = {r['uid']: r for r in selection['rows']}
    worlds = {}
    fields = [('literal', 'completeLiteralWorldPosition'),
              ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
              ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]
    for uid in actors:
        row, attr = sources[uid], attrs[uid]
        path = ROOT / row['candidate']['path']
        assert digest(path.read_bytes()) == row['sourceSHA256'] == attr['sourceSHA256']
        assert assembly['sourceSHA256ByUid'][uid] == row['sourceSHA256']
        refs.append(path)
        ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
        worlds[uid] = dict(original=decode_original_world_triangles(path.read_bytes()),
                          **{m: np.asarray(attr[k], dtype='<f8').reshape(-1, 3)[ix]
                             for m, k in fields})
    children = []
    for uid in args.uid:
        assert reservations.owns(lease)
        order, measured = pair_rows(assembly, uid, args.peer)
        child = args.batch + '-' + uid.split('/')[1].replace(':', '-')
        folder = base / child
        assert not folder.exists()
        child_refs = list(refs)
        rows = []
        for r in measured:
            mode = r['mode']
            a, b = [worlds[u][mode] for u in order]
            assert len(a) == r['completeSourceFaces'] and len(b) == r['completePeerFaces']
            if r['strictBoundsSeparated']:
                gaps = np.maximum(a.min((0, 1))-b.max((0, 1)), b.min((0, 1))-a.max((0, 1)))
                assert np.any(gaps > 0) and gaps.tolist() == r['axisGapsM']
                raw = dict(contacts=[], trianglePairsTested=0, allPairsExamined=True,
                           sourceFacesOmitted=0, geometryChanges=0, physicalSupportAccepted=False)
                save(folder / (mode + '.json.gz'), raw)
            else:
                old_path = ROOT / r['rawPath']
                assert digest(old_path.read_bytes()) == pins[args.assembly][r['rawPath']]
                raw = read(old_path)
                assert raw['allPairsExamined'] and raw['sourceFacesOmitted'] == 0
                assert all(0 <= c['sourceFaceA'] < len(a) and 0 <= c['sourceFaceB'] < len(b)
                           for c in raw['contacts'])
                destination = folder / (mode + '.json.gz')
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(old_path.read_bytes())
                assert digest(destination.read_bytes()) == digest(old_path.read_bytes())
                child_refs.append(old_path)
            rows.append(dict(mode=mode, sourceWorldSHA256ByUid={
                u: digest(worlds[u][mode].astype('<f8').tobytes()) for u in order},
                completeSourceFaces=len(a), completePeerFaces=len(b)))
        save(folder / 'selection.json.gz', dict(rows=[sources[u] for u in order],
                                                manifestSHA256=manifest_sha))
        result = dict(uids=order, sourceSHA256ByUid={u: sources[u]['sourceSHA256'] for u in order},
                      rows=rows, sourceGeometryChanges=0, recomputedContactPairs=0,
                      installationApproved=False, physicalAcceptance=False, publication=False,
                      qualification=__doc__)
        save(folder / 'summary.json', result)
        assert reservations.owns(lease) and digest(manifest.read_bytes()) == manifest_sha
        module('original_pair_schema_binding', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            child, 'exact-completed-assembly-pair-byte-rebind', child_refs, result)
        children.append(dict(uid=uid, batch=child))
    result = dict(uids=actors, pairs=children, sourceGeometryChanges=0,
                  recomputedContactPairs=0, publication=False, installationApproved=False)
    save(out / 'summary.json', result)
    refs += [base / r['batch'] / 'result.json' for r in children]
    module('original_pair_group_binding', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        args.batch, 'completed-original-assembly-pair-schema-bindings', refs, result)


if __name__ == '__main__':
    main()
