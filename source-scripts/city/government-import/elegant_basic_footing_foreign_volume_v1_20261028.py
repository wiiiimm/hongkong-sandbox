"""Check the proposed BASIC footing against complete current foreign surfaces.

Includes all candidate originals in four captured coordinate streams, every
regional BASIC form, and all installed native bounds. No geometry/approval edits.
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
from exact_footing_prism_contacts_v1_20261028 import surface_contacts

BASE = ROOT/'docs/astra-city/government-import'
PREFIX = 'government-xl-elegant-garden-'
SCOPE = PREFIX+'sixteen-original-updated-scope-v1-20261028'
RUNTIME = PREFIX+'sixteen-original-updated-runtime-v1-20261028'
ATTRS = PREFIX+'sixteen-original-final-attributes-v1-20261028'
PROPOSAL = PREFIX+'unnamed-basic-podium-footing-v1-20261028'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert a.batch.startswith(PREFIX) and '/' not in a.batch
    out, local = BASE/a.batch, HERE/'local'/a.batch
    assert not out.exists()
    rp = BASE/(PREFIX+'sixteen-original-updated-terrain-plan-v1-20261028.json')
    resources = set(read(rp)['resources'])
    lp = local/'reservation.json'
    if not a.owned:
        assert not local.exists()
        claim = reservations.claim('basic-footing-foreign-volume-'+str(uuid.uuid4()),
                                   sorted(resources), batch=a.batch, ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'], lp,
                                [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(lp)
    assert reservations.owns(lease) and resources <= set(lease['resources'])
    refs, pins = [Path(__file__), rp, HERE/'exact_footing_prism_contacts_v1_20261028.py'], {}

    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE/batch)[1]
            refs.append(BASE/batch/'result.json')
        path = BASE/batch/name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    scope = take(SCOPE, 'scope.json')
    forms = take(SCOPE, 'form-obligations.json.gz')
    natives = take(SCOPE, 'native-obligations.json.gz')
    selection = take(RUNTIME, 'selection.json.gz')
    attr_report = take(ATTRS, 'attributes.json.gz')
    assert attr_report['startEndAllInputsVerified']
    attrs = {r['uid']: r for r in attr_report['rows']}
    assert set(attrs) == set(scope['uids']) == {r['uid'] for r in selection['rows']}
    geometry = take(PROPOSAL, 'geometry.json.gz')
    target = take(PROPOSAL, 'input.json')['building']
    take(PROPOSAL, 'render-proof.json')
    uid = target['uid']
    assert uid == 'landsd/213586:0' and target in forms
    before, after = geometry['before'], geometry['after']
    assert after['position'][:len(before['position'])] == before['position']
    assert after['index'][:len(before['index'])] == before['index']
    triangles = np.asarray(after['position']).reshape(-1, 3)[np.asarray(after['index']).reshape(-1, 3)]
    added = triangles[len(before['index'])//3:]
    bottom, top = float(added[:, :, 1].min()), float(added[:, :, 1].max())
    assert np.all((added[:, :, 1] == bottom) | (added[:, :, 1] == top))
    cap_ids = np.flatnonzero((added[:, :, 1] == top).all(1))
    caps = added[cap_ids]
    assert len(caps) == 3 and len(added) == 16
    assert np.all(np.cross(caps[:, 1]-caps[:, 0], caps[:, 2]-caps[:, 0])[:, 1] != 0)
    manifest_path = ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest_path.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest_path)
    tile_hashes, basic_rows = {}, []
    for form in forms:
        tile = ROOT/'3d-viewer/city/data/tiles'/(form['tile']+'.json')
        assert digest(tile.read_bytes()) == pins[SCOPE][str(tile.relative_to(ROOT))]
        assert [b for b in read(tile)['buildings'] if b['uid'] == form['uid']] == [form]
        tile_hashes[str(tile.relative_to(ROOT))] = digest(tile.read_bytes())
        refs.append(tile)
        basic_rows.append(dict(building=form, tile=str(tile.relative_to(ROOT))))
    save(out/'basic-inputs.json', dict(manifestSHA256=selection['manifestSHA256'],
                                     currentInputHashes=tile_hashes, rows=basic_rows))
    tool = HERE/'xl-one-peking-current-foreign-basic-tower-geometry-v1-20261010.mjs'
    with (out/'capture.log').open('w') as log:
        subprocess.run(['node', str(tool), str((out/'basic-inputs.json').relative_to(ROOT)),
                        str((out/'basic.json').relative_to(ROOT))], cwd=ROOT,
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    refs.append(tool)
    basics = read(out/'basic.json')
    assert basics['startAndEndInputHashesVerified'] and len(basics['rows']) == len(forms) == 156
    rows = []

    def check(other, role, mode, tri):
        proof = surface_contacts(tri, caps, bottom, top)
        name = other.split('/')[1]+'--'+role+'--'+mode+'.json.gz'
        save(out/name, proof)
        rows.append(dict(uid=other, role=role, mode=mode,
                         worldSHA256=digest(np.asarray(tri, dtype='<f8').tobytes()),
                         completeFaces=len(tri), closedFootingVolumeContacts=len(proof['contacts']),
                         proof=name, reverseSolidContainmentProved=False))
        if proof['contacts']:
            print(dict(uid=other, role=role, mode=mode, contactPrisms=len(proof['contacts'])), flush=True)

    for row in selection['rows']:
        other, attr = row['uid'], attrs[row['uid']]
        path = ROOT/row['candidate']['path']
        assert digest(path.read_bytes()) == row['sourceSHA256'] == attr['sourceSHA256']
        refs.append(path)
        check(other, 'candidate-original', 'original', decode_original_world_triangles(path.read_bytes()))
        index = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
        for mode, field in [('literal', 'completeLiteralWorldPosition'),
                            ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
                            ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]:
            check(other, 'candidate-original', mode, np.asarray(attr[field]).reshape(-1, 3)[index])
    for row in basics['rows']:
        if row['uid'] == uid:
            assert row['position'] == before['position'] and row['index'] == before['index']
            continue
        tri = np.asarray(row['position']).reshape(-1, 3)[np.asarray(row['index']).reshape(-1, 3)]
        check(row['uid'], 'current-basic', 'productionFloat32', tri)
    lo, hi = added.min((0, 1)), added.max((0, 1))
    native_rows = []
    for row in natives:
        bounds = np.asarray(row['completeFourWorldBounds']).reshape(-1, 3)
        gaps = np.maximum(bounds.min(0)-hi, lo-bounds.max(0))
        native_rows.append(dict(**row, strictSeparatingAxisGapsM=gaps.tolist(),
                                completeFourWorldBoundsSeparated=bool(np.any(gaps > 0))))
    for path, sha in basics['inputHashes'].items():
        assert digest((ROOT/path).read_bytes()) == sha
        refs.append(ROOT/path)
    result = dict(uids=[uid, *scope['uids']], status='private-complete-foreign-surface-footing-volume-context',
                  uid=uid, sourceGeometryChanges=0, governmentGeometryChanges=0,
                  currentBasicForms=156, testedForeignBasicForms=155, candidateOriginals=16,
                  originalCoordinateStreams=4, completeAddedFootingFaces=len(added),
                  renderedFootingBottom=bottom, renderedFootingTop=top,
                  originalFootingCapFaces=cap_ids.tolist(), rows=rows, nativeRows=native_rows,
                  surfaceVolumeContactRows=sum(r['closedFootingVolumeContacts'] > 0 for r in rows),
                  nativeBoundsPending=sum(not r['completeFourWorldBoundsSeparated'] for r in native_rows),
                  reverseSolidContainmentProved=False, collisionReviewApproved=False,
                  visualReviewApproved=False, installationApproved=False,
                  qualification='Every complete candidate source surface in all four captured streams and all155foreign regional BASIC production meshes is clipped against the CLOSED prisms of the actual Float32 footing top-cap triangles at actual added-mesh heights. No face or contained-triangle omission, projection-only credit or epsilon exclusion. All9native complete four-world bounds are reported; overlapping bounds require actual geometry. Contact absence does not prove reverse solid containment absence. BASIC counterparts of proposed originals remain explicit diagnostic contexts, not simultaneous detailed-scene actors. No role/collision/visual/publication acceptance, source or geometry edits.')
    save(out/'summary.json', result)
    assert reservations.owns(lease)
    refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('basic_footing_foreign_volume_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'complete-current-foreign-surface-in-basic-footing-volume-context', list(dict.fromkeys(refs)), result)
    print(dict(rows=len(rows), contactRows=result['surfaceVolumeContactRows'], nativePending=result['nativeBoundsPending']), flush=True)


if __name__ == '__main__':
    main()
