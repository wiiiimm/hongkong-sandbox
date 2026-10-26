"""Measure an expanded assembly, reusing exact authenticated pair streams only.

Disjoint complete bounds prove absence of contacts. Overlapping bounds use the
existing exact finite-triangle checker, retaining all raw primitive contacts.
"""
import argparse
import itertools
import shutil
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'attributes']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--prior-contacts', required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    out = base / args.batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, filename):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        path = base / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(args.runtime, 'selection.json.gz')
    attributes = take(args.attributes, 'attributes.json.gz')
    assert attributes['startEndAllInputsVerified']
    attrs = {r['uid']: r for r in attributes['rows']}
    uids = [r['uid'] for r in selection['rows']]
    assert 2 <= len(uids) == len(set(uids)) <= 12
    assert set(uids) == set(attrs)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_sha = selection['manifestSHA256']
    assert digest(manifest.read_bytes()) == manifest_sha
    refs.append(manifest)
    fields = dict(literal='completeLiteralWorldPosition',
                  leftF32='completeExplicitLeftAssociatedFloat32WorldPosition',
                  balancedF32='completeExplicitBalancedFloat32WorldPosition')
    worlds, hashes = {}, {}
    for row in selection['rows']:
        uid, attr = row['uid'], attrs[row['uid']]
        path = ROOT / row['candidate']['path']
        hashes[uid] = digest(path.read_bytes())
        assert hashes[uid] == row['sourceSHA256'] == attr['sourceSHA256']
        refs.append(path)
        index = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
        worlds[uid] = dict(original=decode_original_world_triangles(path.read_bytes()))
        for mode, field in fields.items():
            worlds[uid][mode] = np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[index]
        assert all(len(t) == row['triangles'] and np.isfinite(t).all()
                   for t in worlds[uid].values())
    prior = take(args.prior_contacts, 'summary.json')
    assert prior['pairCount'] == len(prior['rows']) == len(prior['uids']) * (len(prior['uids']) - 1) // 2
    assert set(prior['uids']) < set(uids)
    assert all(hashes[u] == sha for u, sha in prior['sourceSHA256ByUid'].items())
    previous = {frozenset([r['left'], r['right']]): r for r in prior['rows']}
    assert len(previous) == prior['pairCount']
    rows, reused = [], []
    for left, right in itertools.combinations(uids, 2):
        key = frozenset([left, right])
        if key in previous:
            pair = previous[key]
            assert (pair['left'], pair['right']) == (left, right), 'Reversed source face indexing must not be reused'
            assert len(pair['modes']) == 4 and {m['mode'] for m in pair['modes']} == {'original', *fields}
            for m in pair['modes']:
                mode = m['mode']; a, b = worlds[left][mode], worlds[right][mode]
                assert m['sourceFaces'] == [len(a), len(b)]
                assert m['sourceWorldSHA256ByUid'] == {left: digest(a.tobytes()), right: digest(b.tobytes())}
                if m['method'] == 'strict-complete-bounds-separation':
                    gaps = np.maximum(b.min((0, 1)) - a.max((0, 1)), a.min((0, 1)) - b.max((0, 1)))
                    assert np.any(gaps > 0) and gaps.tolist() == m['strictSeparatingAxisGapsM']
                    assert m['finiteContactPairs'] == m['positiveSurfaceContactPairs'] == m['areaContactPairs'] == 0
                else:
                    assert m['method'] == 'complete-exact-finite-triangle-contacts'
                    filename = left.split('/')[1] + '--' + right.split('/')[1] + '--' + mode + '.json.gz'
                    proof = take(args.prior_contacts, filename)
                    assert proof['allPairsExamined'] and proof['sourceFacesOmitted'] == 0
                    assert len(proof['contacts']) == m['finiteContactPairs']
                    assert sum(c['dimension'] > 0 for c in proof['contacts']) == m['positiveSurfaceContactPairs']
                    assert sum(c['dimension'] == 2 for c in proof['contacts']) == m['areaContactPairs']
                    out.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(base / args.prior_contacts / filename, out / filename)
            rows.append(pair); reused.append(dict(left=left, right=right))
            print(dict(left=left, right=right, reusedExactWorldStreams=True), flush=True)
            continue
        modes = []
        for mode in ['original', *fields]:
            a, b = worlds[left][mode], worlds[right][mode]
            gaps = np.maximum(b.min((0, 1)) - a.max((0, 1)),
                              a.min((0, 1)) - b.max((0, 1)))
            summary = dict(mode=mode, sourceFaces=[len(a), len(b)],
                           sourceWorldSHA256ByUid={left: digest(a.tobytes()), right: digest(b.tobytes())})
            if np.any(gaps > 0):
                summary.update(strictSeparatingAxisGapsM=gaps.tolist(),
                               finiteContactPairs=0, positiveSurfaceContactPairs=0,
                               areaContactPairs=0, method='strict-complete-bounds-separation')
            else:
                proof = exact_finite_contacts(a, range(len(a)), b, range(len(b)))
                assert proof['allPairsExamined'] and proof['sourceFacesOmitted'] == 0
                save(out / (left.split('/')[1] + '--' + right.split('/')[1] + '--' + mode + '.json.gz'), proof)
                summary.update(finiteContactPairs=len(proof['contacts']),
                               positiveSurfaceContactPairs=sum(c['dimension'] > 0 for c in proof['contacts']),
                               areaContactPairs=sum(c['dimension'] == 2 for c in proof['contacts']),
                               method='complete-exact-finite-triangle-contacts')
            modes.append(summary)
        rows.append(dict(left=left, right=right, modes=modes))
        print(dict(left=left, right=right, positive=[r['positiveSurfaceContactPairs'] for r in modes]), flush=True)
    assert len(rows) == len(uids) * (len(uids) - 1) // 2
    assert digest(manifest.read_bytes()) == manifest_sha
    result = dict(uids=uids, sourceSHA256ByUid=hashes, currentManifestSHA256=manifest_sha,
                  pairCount=len(rows), coordinateModes=4, rows=rows, reusedPairs=reused,
                  priorContacts=args.prior_contacts, currentSceneAcceptanceTransferred=False,
                  sourceGeometryChanges=0, sourcePoseChanges=0,
                  installationApproved=False, physicalAcceptance=False, publication=False,
                  qualification='Complete unordered original-source pair coverage in four representations; prior streams reused only with exact complete source/world hashes, unchanged pair orientation and verified raw proof bytes. No historical scene acceptance transferred. Strict complete bounds or existing exact finite contacts; no epsilon exclusion, omitted source faces, geometry edits, architectural interpretation, support acceptance or publication permission.')
    save(out / 'summary.json', result)
    refs.extend(HERE / name for name in ['exact_packed_world_geometry_20261009.py',
                                        'exact_original_finite_triangle_contacts_20261010.py'])
    module('expanded_assembly_pair_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        args.batch, 'complete-original-assembly-all-pair-four-world-contacts', refs, result)


if __name__ == '__main__':
    main()
