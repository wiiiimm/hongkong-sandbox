"""Classify authenticated full native contacts in all four exact coordinate worlds.

Geometric roles/locus are diagnostic; no architectural or collision acceptance.
"""
import argparse
from collections import Counter
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face
from exact_contact_role_context_v1_20261023 import contact_role


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'attributes', 'contacts']:
        parser.add_argument('--' + key, required=True)
    a = parser.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        p = base / batch / name
        assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)

    selection = take(a.runtime, 'selection.json.gz')
    sources = {r['uid']: r for r in selection['rows']}
    attrs = {r['uid']: r for r in take(a.attributes, 'attributes.json.gz')['rows']}
    contacts = take(a.contacts, 'summary.json')
    native_rows = {r['uid']: r for r in take(a.contacts, 'native-input.json.gz')['rows']}
    native_attrs = {r['uid']: r for r in take(a.contacts, 'native-attributes.json.gz')['rows']}
    modes = {'original': None, 'literal': 'completeLiteralWorldPosition',
             'leftF32': 'completeExplicitLeftAssociatedFloat32WorldPosition',
             'balancedF32': 'completeExplicitBalancedFloat32WorldPosition'}
    results = []
    for pair in contacts['rows']:
        uid, nuid = pair['uid'], pair['nativeUid']
        source, native = sources[uid], native_rows[nuid]
        assert source['sourceSHA256'] == pair['sourceSHA256'] == attrs[uid]['sourceSHA256']
        assert native['entry'] == pair['rawCurrentNativeEntry']
        assert native['entry']['sha256'] == pair['nativeSHA256'] == native_attrs[nuid]['sourceSHA256']
        source_path, native_path = ROOT / source['candidate']['path'], ROOT / native['path']
        assert digest(source_path.read_bytes()) == pair['sourceSHA256']
        assert digest(native_path.read_bytes()) == pair['nativeSHA256']
        refs.extend([source_path, native_path])
        original = [decode_original_world_triangles(p.read_bytes()) for p in [source_path, native_path]]
        by_mode = {r['mode']: r for r in pair['modes']}
        assert set(by_mode) == set(modes)
        for mode, field in modes.items():
            worlds = original if field is None else [np.asarray(attr[field]).reshape(-1, 3)[np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)] for attr in [attrs[uid], native_attrs[nuid]]]
            proof = take(a.contacts, uid.split('/')[1] + '--' + nuid.split('/')[1] + '--' + mode + '.json.gz')
            assert proof['allPairsExamined'] and proof['sourceFacesOmitted'] == 0
            assert len(proof['contacts']) == by_mode[mode]['finiteContactPairs']
            assert len(worlds[0]) == by_mode[mode]['sourceFaces'] and len(worlds[1]) == by_mode[mode]['nativeFaces']
            classified, points = [], []
            for c in proof['contacts']:
                exact = [tuple(Fraction(v) for v in q) for q in c['exactPoints']]
                left, right = rational_face(worlds[0][c['sourceFaceA']]), rational_face(worlds[1][c['sourceFaceB']])
                role = contact_role(left, right, exact, c['dimension'], [c['sourcePrimitiveDimensionA'], c['sourcePrimitiveDimensionB']])
                classified.append(dict(c, contactRole=role))
                points.extend(exact)
            save(out / (uid.split('/')[1] + '--' + nuid.split('/')[1] + '--' + mode + '.json.gz'), classified)
            row = dict(uid=uid, nativeUid=nuid, mode=mode, sourceSHA256=pair['sourceSHA256'],
                       nativeSHA256=pair['nativeSHA256'], contactCount=len(classified),
                       sourceWorldSHA256=digest(worlds[0].astype('<f8').tobytes()),
                       nativeWorldSHA256=digest(worlds[1].astype('<f8').tobytes()),
                       roles=dict(Counter(c['contactRole'] for c in classified)))
            if points:
                lo = [min(q[i] for q in points) for i in range(3)]
                hi = [max(q[i] for q in points) for i in range(3)]
                row.update(exactContactBounds=[[str(v) for v in lo], [str(v) for v in hi]],
                           contactBounds=[[float(v) for v in lo], [float(v) for v in hi]])
            results.append(row)
            print({k: row[k] for k in ['uid', 'nativeUid', 'mode', 'contactCount', 'roles']}, flush=True)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == pins[a.contacts][str(manifest.relative_to(ROOT))]
    refs.extend([manifest, HERE / 'exact_packed_world_geometry_20261009.py', HERE / 'exact_original_shell_intersections_20261009.py', HERE / 'exact_contact_role_context_v1_20261023.py'])
    result = dict(uids=contacts['uids'], rows=results, sourceGeometryChanges=0, nativeMetadataChanges=0,
                  architecturalRoleAccepted=False, physicalAcceptance=False, installationApproved=False,
                  qualification='Full authenticated finite-contact streams classified using exact rational primitive/triangle predicates in each separately bound world. Raw contact points/counts retained. Shared-plane and transverse classifications alone prove neither architectural intent nor acceptable interpenetration.')
    save(out / 'summary.json', result)
    module('native_contact_roles_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'complete-original-native-four-world-contact-roles-diagnostic', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
