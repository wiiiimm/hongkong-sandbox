"""Measure unchanged BASIC footings against complete unapproved original peers.

No grounding edits, skip credit or support/root acceptance follows this probe.
"""
import argparse
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['batch', 'runtime', 'attributes', 'contacts']:
        p.add_argument('--'+name, required=True)
    p.add_argument('--uid', action='append', required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    assert 0 < len(a.uid) == len(set(a.uid)) <= 8
    base = ROOT/'docs/astra-city/government-import'
    doc, local = base/a.batch, HERE/'local'/a.batch
    leasepath = local/'reservation.json'
    pins, refs = {}, [Path(__file__), HERE/'exact_packed_world_geometry_20261009.py']
    for name in [a.runtime, a.attributes, a.contacts]:
        _, bound = authenticate(base/name)
        refs.append(base/name/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selected = take(base/a.runtime/'selection.json.gz')['rows']
    attrs = take(base/a.attributes/'attributes.json.gz')
    assert attrs['startEndAllInputsVerified']
    attrs = {r['uid']: r for r in attrs['rows']}
    basic = take(base/a.contacts/'basic.json')
    assert basic['startAndEndInputHashesVerified']
    forms = {r['uid']: r for r in basic['rows'] if r['uid'] in a.uid}
    assert set(forms) == set(a.uid) and not set(forms)&{r['uid'] for r in selected}
    if not a.owned:
        assert not doc.exists() and not local.exists()
        resources = sorted('building:'+u for u in set(forms)|{r['uid'] for r in selected})
        claim = reservations.claim('basic-candidate-support-'+str(uuid.uuid4()), resources, batch=a.batch, ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'], leasepath, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(leasepath)
    assert reservations.owns(lease) and not doc.exists()
    worlds = {mode: [] for mode in ['original', 'literal', 'leftF32', 'balancedF32']}
    roster = []
    offset = 0
    for row in sorted(selected, key=lambda r: r['uid']):
        uid = row['uid']
        attr = attrs[uid]
        path = ROOT/row['candidate']['path']
        raw = path.read_bytes()
        assert digest(raw) == row['sourceSHA256'] == attr['sourceSHA256']
        refs.append(path)
        ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
        worlds['original'].append(decode_original_world_triangles(raw))
        for mode, field in [('literal', 'completeLiteralWorldPosition'), ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]:
            worlds[mode].append(np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[ix])
        assert all(len(worlds[m][-1]) == row['triangles'] for m in worlds)
        roster.append(dict(uid=uid, sourceSHA256=row['sourceSHA256'], sourceFaceRange=[offset, offset+row['triangles']]))
        offset += row['triangles']
    worlds = {m: np.concatenate(parts) for m, parts in worlds.items()}
    inputs = []
    for uid, row in sorted(forms.items()):
        building = row['currentBuilding']
        tile = ROOT/'3d-viewer/city/data/tiles'/(building['tile']+'.json')
        assert [f for f in read(tile)['buildings'] if f['uid'] == uid] == [building]
        refs.append(tile)
        position = np.asarray(row['position'], dtype='<f8').reshape(-1, 3)
        for mode, tri in worlds.items():
            inputs.append(dict(uid=uid, mode=mode, source=dict(position=row['position'], index=row['index']),
                sourceMinimumY=float(position[:, 1].min()),
                support=dict(position=tri.reshape(-1).tolist(), index=list(range(tri.size//3))),
                sourceWorldSHA256=digest(position.tobytes()), supportWorldSHA256=digest(tri.astype('<f8').tobytes())))
    save(doc/'input.json.gz', dict(rows=inputs))
    tool = HERE/'original_neighbour_rim_contacts_v1_20261028.mjs'
    refs.append(tool)
    with (doc/'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), str((doc/'input.json.gz').relative_to(ROOT)), str((doc/'contacts.json.gz').relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    report = read(doc/'contacts.json.gz')
    assert len(report['rows']) == len(forms)*4
    assert {(r['uid'], r['mode']) for r in report['rows']} == {(u, m) for u in forms for m in worlds}
    for path, sha in report['inputHashes'].items():
        assert digest((ROOT/path).read_bytes()) == sha
        refs.append(ROOT/path)
    result = dict(uids=sorted(set(forms)|{r['uid'] for r in selected}), basicUIDs=sorted(forms),
        candidateSourceRoster=roster, rows=[{k: v for k, v in r.items() if k not in ['rawInterface', 'mapped']} for r in report['rows']],
        sourceGeometryChanges=0, basicGeometryChanges=0, physicalSupportAccepted=False,
        installationApproved=False, qualification='Unchanged current BASIC arrays and complete original/four-world candidate streams under existing rim/wall kernel. Candidate peers are unapproved and may be unrooted. Every raw failure retained; no earth-gap waiver, new dependency, source ownership, root, scene or publication approval.')
    save(doc/'summary.json', result)
    assert reservations.owns(lease)
    module('basic_candidate_support_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'unchanged-basic-versus-complete-candidate-support-diagnostic', list(dict.fromkeys(refs)), result)
    print(result['rows'], flush=True)


if __name__ == '__main__':
    main()
