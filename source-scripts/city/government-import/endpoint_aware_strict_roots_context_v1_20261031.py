"""Recheck existing canonical strict roots by exact endpoint-height class.

No source edits, new roots, geometry joins, tolerance changes or approval.
"""
import argparse
from pathlib import Path

import numpy as np

from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from endpoint_aware_strict_anchor_paths_v1_20261031 import choose_paths


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'attributes', 'support']:
        p.add_argument('--' + key, required=True)
    p.add_argument('--case', action='append', required=True, help='uid,prior-root-path-batch')
    args = p.parse_args()
    base = ROOT / 'docs/astra-city/government-import'
    out = base / args.batch
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    assert not out.exists()
    cases = [s.split(',') for s in args.case]
    assert all(len(s) == 2 for s in cases)
    assert len(cases) == len({s[0] for s in cases}) <= 16
    pins, refs = {}, [Path(__file__)]

    def take(batch, filename):
        assert batch.startswith('government-xl-') and '/' not in batch
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        path = base / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(args.runtime, 'selection.json.gz')
    attrs = {r['uid']: r for r in take(args.attributes, 'attributes.json.gz')['rows']}
    sources = {r['uid']: r for r in selection['rows']}
    needed = {args.support, *(s[0] for s in cases)}
    assert needed <= sources.keys() and needed <= attrs.keys()
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_sha = digest(manifest.read_bytes())
    assert manifest_sha == selection['manifestSHA256']
    refs.append(manifest)
    fields = [('literal', 'completeLiteralWorldPosition'),
              ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
              ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]
    worlds = {}
    for uid in needed:
        row, attr = sources[uid], attrs[uid]
        path = ROOT / row['candidate']['path']
        assert digest(path.read_bytes()) == row['sourceSHA256'] == attr['sourceSHA256']
        refs.append(path)
        ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
        worlds[uid] = dict(original=decode_original_world_triangles(path.read_bytes()),
                          **{mode: np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[ix]
                             for mode, field in fields})
    rows = []
    for uid, prior in cases:
        assert uid != args.support
        summary = take(prior, 'summary.json')
        assert summary['sourceSHA256ByUid'] == {
            u: sources[u]['sourceSHA256'] for u in [uid, args.support]}
        for mode, tri in worlds[uid].items():
            old = take(prior, mode + '.json.gz')
            support = worlds[args.support][mode]
            assert old['sourceWorldSHA256'] == digest(tri.astype('<f8').tobytes())
            assert old['supportWorldSHA256'] == digest(support.astype('<f8').tobytes())
            roots = old['canonicalStrictRoots']
            assert len(roots) == old['canonicalStrictAnchorCount']
            for root in roots:
                provider = root['provider']
                assert np.array_equal(provider['vertices'], support[provider['faceIndex']])
                assert root['supportHeight'] == provider['height']
            targets = [dict(witness=r['witness'], incidentFaces=r['incidentFaces'])
                       for r in old['rows']]
            result = choose_paths(tri, targets, roots)
            assert result['baseline'] == old['rows'], 'Prior canonical paths did not reproduce'
            save(out / uid.split('/')[1] / (mode + '.json.gz'), result)
            before = sum(not r.get('passesExistingEndpointHeight', False)
                         for r in result['baseline'])
            rows.append(dict(uid=uid, supportUid=args.support, mode=mode,
                             targets=len(targets), beforeFailed=before,
                             afterFailed=len(result['remainingIndices']),
                             newlyValidExistingEndpointChoices=before-len(result['remainingIndices']),
                             canonicalStrictRoots=len(roots), supportApproved=False))
    assert digest(manifest.read_bytes()) == manifest_sha
    result = dict(uids=sorted(needed), rows=rows, sourceGeometryChanges=0,
                  sourcePoseChanges=0, newAnchorsCreated=0, intercomponentJoins=0,
                  endpointToleranceChanged=False, supportApproved=False,
                  physicalAcceptance=False, installationApproved=False, publication=False,
                  qualification=__doc__)
    save(out / 'summary.json', result)
    refs += [HERE / n for n in ['endpoint_aware_strict_anchor_paths_v1_20261031.py',
                               'test_endpoint_aware_strict_anchor_paths_v1_20261031.py',
                               'original_face_attachment_minimax_v2_20261024.py',
                               'pool_incident_wall_contacts_v1_20261017.py',
                               'exact_packed_world_geometry_20261009.py']]
    module('endpoint_choice_context', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        args.batch, 'same-source-canonical-strict-root-endpoint-choice-diagnostic', refs, result)
    print(rows, flush=True)


if __name__ == '__main__':
    main()
