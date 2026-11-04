"""Probe an exact current shared-parent surveyed podium under unchanged rules.

No dependency or identity approval. Current BASIC before/after clearance and
the complete original/four-world source geometry remain distinct evidence.
"""
import argparse
import subprocess
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'attributes', 'neighbours', 'uid', 'support-uid']:
        p.add_argument('--'+key, required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT/'docs/astra-city/government-import'
    doc = base/a.batch
    assert not doc.exists() and a.uid != a.support_uid
    refs, pins = [Path(__file__), HERE/'exact_packed_world_geometry_20261009.py'], {}
    for name in [a.runtime, a.attributes, a.neighbours]:
        _, bound = authenticate(base/name)
        refs.append(base/name/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    rows = take(base/a.runtime/'selection.json.gz')['rows']
    row = next(r for r in rows if r['uid'] == a.uid)
    attrs = take(base/a.attributes/'attributes.json.gz')
    assert attrs['startEndAllInputsVerified']
    attr = next(r for r in attrs['rows'] if r['uid'] == a.uid)
    neighbours = take(base/a.neighbours/'neighbour-inputs.json.gz')
    support = next(r for r in neighbours['rows'] if r['building']['uid'] == a.support_uid)
    assert support['existingNative'] is False
    b = support['building']
    assert b['structureType'] == 'Podium' and not b.get('modelGeometry')
    assert b['parent'] and b['parent'] == row['source']['building'].get('parent')
    assert b['baseHeightHKPD'] == b['base'] and b['topHeightHKPD'] == b['base']+b['height']
    standard = next(r for r in take(base/a.neighbours/'neighbour-checks.json')['rows'] if r['uid'] == a.support_uid)
    assert not standard['reasons'] and standard['existingNative'] is False
    manifestpath = ROOT/'3d-viewer/city/data/manifest.json'
    manifest = take(manifestpath)
    assert not any(m['uid'] == a.support_uid for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models'])
    tile = ROOT/'3d-viewer/city/data/tiles'/(b['tile']+'.json')
    assert [f for f in read(tile)['buildings'] if f['uid'] == b['uid']] == [b]
    refs.append(tile)
    claim = reservations.claim('shared-parent-surveyed-support-'+str(uuid.uuid4()),
        sorted({'building:'+a.uid, 'building:'+a.support_uid, 'terrain:city/data/terrain.json'}), batch=a.batch, ttl=1800)
    assert claim['ok']
    lease = claim['reservation']
    try:
        ref = lambda path: dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))
        save(doc/'support-input.json', dict(uid=b['uid'], csuid=b['buildingCSUID'], building=b, refs=[ref(p) for p in refs]))
        capture = HERE/'capture_current_surveyed_support_v1.mjs'
        subprocess.run(['node', str(capture), str((doc/'support-input.json').relative_to(ROOT)), str((doc/'support-attributes.json.gz').relative_to(ROOT))], cwd=ROOT, check=True)
        basic = read(doc/'support-attributes.json.gz')
        refs.extend([capture, HERE/'surveyed_fallback_support_geometry_v1.mjs'])
        for path, sha in basic['inputHashes'].items():
            assert digest((ROOT/path).read_bytes()) == sha
            refs.append(ROOT/path)
        asset = ROOT/row['candidate']['path']
        raw = asset.read_bytes()
        assert digest(raw) == row['sourceSHA256'] == attr['sourceSHA256']
        refs.append(asset)
        ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
        worlds = dict(original=decode_original_world_triangles(raw), **{mode: np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[ix] for mode, field in [('literal', 'completeLiteralWorldPosition'), ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]})
        inputs = []
        for mode, tri in worlds.items():
            assert len(tri) == row['triangles']
            inputs.append(dict(uid=a.uid, mode=mode, source=dict(position=tri.reshape(-1).tolist(), index=list(range(tri.size//3))),
                sourceMinimumY=float(tri[:, :, 1].min()), support=dict(position=basic['position'], index=basic['index']),
                sourceWorldSHA256=digest(tri.astype('<f8').tobytes()), supportWorldSHA256=digest(np.asarray(basic['position'], dtype='<f8').tobytes())))
        save(doc/'input.json.gz', dict(rows=inputs))
        tool = HERE/'original_neighbour_rim_contacts_v1_20261028.mjs'
        refs.append(tool)
        with (doc/'worker.log').open('w') as log:
            subprocess.run(['node', str(tool), str((doc/'input.json.gz').relative_to(ROOT)), str((doc/'contacts.json.gz').relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
        proof = read(doc/'contacts.json.gz')
        assert len(proof['rows']) == 4 and {r['mode'] for r in proof['rows']} == set(worlds)
        for path, sha in proof['inputHashes'].items():
            assert digest((ROOT/path).read_bytes()) == sha
            refs.append(ROOT/path)
        result = dict(uids=[a.uid, a.support_uid], candidateUid=a.uid, supportUid=a.support_uid,
            sourceSHA256=row['sourceSHA256'], supportCSUID=b['buildingCSUID'], sharedParent=b['parent'],
            supportBasicBeforeAfterClear=True, rows=[{k: v for k, v in r.items() if k not in ['rawInterface', 'mapped']} for r in proof['rows']],
            sourceGeometryChanges=0, dependencyApproved=False, sourceIdentityAccepted=False, physicalAccepted=False,
            installationApproved=False, qualification='Exact current shared-parent surveyed BASIC podium, complete production geometry and unchanged before/after terrain checks. Existing strict/wall rim kernel in all four source streams. This does not create a dependency, suppress/import the podium, clear source-coverage negatives, establish a structural root or grant publication approval.')
        save(doc/'summary.json', result)
        assert reservations.owns(lease)
        module('shared_parent_surveyed_support_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'exact-shared-parent-surveyed-podium-four-world-support-probe', list(dict.fromkeys(refs)), result)
        print(result['rows'], flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
