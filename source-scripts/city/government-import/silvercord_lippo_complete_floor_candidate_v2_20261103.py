"""Assemble the exact private floor return without flattening the retained grid.

This is a private candidate, not an accepted terrain recipe. Existing cycle
markers remain historical and require fresh complete coordinated validation.
"""
import copy
import sys
import uuid
import subprocess
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from one_peking_nested_cycle_boundary_v3_20261101 import refined_new_metadata
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from retained_bounded_floor_work_v1_20261102 import inset
import shapely

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-complete-floor-candidate-v2-20261103'
TRIAL = 'government-xl-silvercord-lippo-private-source-floor-trial-v1-20261103'
MAPPING = 'government-xl-silvercord-lippo-rendered-floor-parent-lookup-v1-20261103'
NATIVE = 'government-xl-silvercord-lippo-floor-parent-faces-v2-20261103'
PARENT = 'city/data/government-xl-one-peking-cycle-original-terrain-20261101.json'
LOCAL = HERE / 'local' / BATCH
UIDS = ['landsd/233997:0', 'landsd/231645:0']


def face_key(face): return tuple(sorted(tuple(float(v) for v in p) for p in face))


def owned():
    lease = read(LOCAL / 'reservation.json'); assert reservations.owns(lease)
    refs = [Path(__file__), HERE / 'one_peking_nested_cycle_boundary_v3_20261101.py']; pins = {}
    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]; refs.append(BASE / batch / 'result.json')
        path = BASE / batch / name; assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    historical = take(TRIAL, '231645-0/private-ground.json.gz')
    prior_mapping = take(MAPPING, 'complete-rendered-parent-lookup.json')
    parent_path = ROOT / '3d-viewer' / PARENT
    assert digest(parent_path.read_bytes()) == prior_mapping['inputHashes'][str(parent_path.relative_to(ROOT))]
    parent = read(parent_path)
    runtime = 'government-xl-silvercord-lippo-current-floor-sequence-v1-20261103-runtime'
    selection = take(runtime, 'selection.json.gz')
    row = next(r for r in selection['rows'] if r['uid']=='landsd/231645:0')
    asset = ROOT / row['candidate']['path']; assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
    original = decode_original_world_triangles(asset.read_bytes());source=original[historical['sourceFaceIndices']]
    outer = shapely.union_all(shapely.polygons(source[:,:,[0,2]])).buffer(1.,join_style='mitre').buffer(3.,join_style='mitre')
    bounds = list(outer.bounds);g=parent['meta']['georef'];x0=g['bE']-834500;z0=816500-g['bN'];step=g['aE']
    assert bounds[0]>x0 and bounds[1]>z0 and bounds[2]<x0+(parent['w']-1)*step and bounds[3]<z0+(parent['h']-1)*step,'Full floor work reaches outer parent; additional exact parent is required'
    scope=BASE/BATCH/'full-work-capture-scope.json';save(scope,dict(parentURL=PARENT,bounds=bounds,sourceFaceIndices=historical['sourceFaceIndices'],coreBufferM=1,returnBufferM=3))
    capture_path=LOCAL/'full-work-parent-facets.json';tool=HERE/'source_floor_complete_parent_capture_v1_20261103.mjs';refs.append(tool)
    subprocess.run(['node',str(tool),str(scope.relative_to(ROOT)),str(capture_path.relative_to(ROOT))],cwd=ROOT,check=True)
    captured=read(capture_path);refs.append(capture_path)
    for name,sha in captured['inputHashes'].items():assert digest((ROOT/name).read_bytes())==sha;refs.append(ROOT/name)
    before=np.asarray([r['triangle']for r in captured['rows']]);after,proof=inset(before,source);lineage=proof['outputLineage']
    changed=set(proof['changedTerrainFaceIndices']);assert changed
    trial=dict(before=before.tolist(),after=after.tolist(),sourceFaceIndices=historical['sourceFaceIndices'])
    save(BASE/BATCH/'231645-0/private-ground.json.gz',trial);save(BASE/BATCH/'231645-0/return-proof.json.gz',proof)
    owners={i:dict(url=PARENT,**{k:captured['rows'][i][k]for k in ['meshPath','meshName','renderedFace']})for i in changed}
    native_rows={i:[]for i in changed}
    lookup={face_key(before[i]):i for i in changed}
    assert len(lookup)==len(changed)
    for index,node in enumerate(parent['patches']):
        if not node.get('nativeMesh'):continue
        mesh=node['nativeMesh'];positions=np.asarray(mesh['position'],dtype='<f4').astype('<f8').reshape(-1,3);tri=positions[np.asarray(mesh['index']).reshape(-1,3)]
        for face,t in enumerate(tri):
            captured_id=lookup.get(face_key(t))
            if captured_id is not None:native_rows[captured_id].append(dict(url=PARENT,node='/patches/'+str(index),face=face))
    mapped=dict(inputHashes=prior_mapping['inputHashes'])
    parent_path = ROOT / '3d-viewer' / PARENT; old_raw = parent_path.read_bytes(); parent_sha = digest(old_raw)
    assert parent_sha == mapped['inputHashes'][str(parent_path.relative_to(ROOT))]; refs.append(parent_path)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'; mh = digest(manifest.read_bytes()); refs.append(manifest)
    parent = read(parent_path); candidate = copy.deepcopy(parent); grid = {}; native_groups = {}
    g = parent['meta']['georef']; step = g['aE']; assert step == -g['aN'] == 5
    x_origin, z_origin = g['bE'] - 834500, 816500 - g['bN']
    for captured, owner in owners.items():
        if owner['meshName'] == 'Lands Department · 5 m terrain':
            assert owner['meshPath'] == '/children/0' and not native_rows[captured]
            t = before[captured]; x0, z0 = t[:, [0, 2]].min(0); x1, z1 = t[:, [0, 2]].max(0)
            c, r = (x0 - x_origin) / step, (z0 - z_origin) / step
            assert c == round(c) and r == round(r) and x1-x0 == z1-z0 == step
            grid.setdefault((int(c), int(r)), set()).add(captured)
        else:
            matches = native_rows[captured]; assert len(matches) == 1 and matches[0]['url'] == PARENT
            index = int(matches[0]['node'].split('/')[-1]); assert index in [15, 17]
            native_groups.setdefault(index, {})[captured] = matches[0]['face']
    assert set(native_groups) == {15, 17}
    binding = dict(privateTrial=str((BASE / BATCH / '231645-0/return-proof.json.gz').relative_to(ROOT)),
                   privateTrialSHA256=digest((BASE / BATCH / '231645-0/return-proof.json.gz').read_bytes()),
                   originalParent=dict(url=PARENT, sha256=parent_sha), sourceFaceIndices=trial['sourceFaceIndices'],
                   sourceGeometryChanges=0, sourcePoseChanges=0, physicalAcceptance=False, installationApproved=False)
    for index, faces in native_groups.items():
        node = candidate['patches'][index]; mesh = node['nativeMesh']; positions = np.asarray(mesh['position']).reshape(-1, 3)
        indices = np.asarray(mesh['index']).reshape(-1, 3); rendered = positions.astype('<f4').astype('<f8')[indices]
        assert len(faces.values()) == len(set(faces.values()))
        for captured, native_face in faces.items(): assert face_key(before[captured]) == face_key(rendered[native_face])
        retained = [i for i in range(len(indices)) if i not in set(faces.values())]
        output = after[[r['parentFace'] in faces for r in lineage]]
        start = len(positions); appended = output.reshape(-1, 3)
        mesh['position'] = np.concatenate([positions, appended]).reshape(-1).tolist()
        mesh['index'] = np.concatenate([indices[retained], np.arange(start, start+len(appended)).reshape(-1, 3)]).reshape(-1).tolist()
        assert mesh['position'][:positions.size] == parent['patches'][index]['nativeMesh']['position']
        assert np.array_equal(np.asarray(mesh['index']).reshape(-1, 3)[:len(retained)], indices[retained])
        mesh['source']['privateSourceFloorReturn'] = binding
    c0, r0 = np.min(list(grid), axis=0); c1, r1 = np.max(list(grid), axis=0) + 1
    bounds = [x_origin+c0*step, z_origin+r0*step, x_origin+c1*step, z_origin+r1*step]
    scope = BASE / BATCH / 'grid-capture-scope.json'; save(scope, dict(parentURL=PARENT, bounds=bounds))
    capture = LOCAL / 'current-grid.json'; tool = HERE / 'one_peking_root_grid_capture_v1_20261101.mjs'; refs.append(tool)
    subprocess.run(['node', str(tool), str(scope.relative_to(ROOT)), str(capture.relative_to(ROOT))], cwd=ROOT, check=True)
    root_grid = read(capture); refs.append(capture)
    for path, sha in root_grid['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha; refs.append(ROOT / path)
    exact_grid = {face_key(t): np.asarray(t) for t in root_grid['triangles']}
    captured_by_key = {}
    for i, t in enumerate(before): captured_by_key.setdefault(face_key(t), []).append(i)
    added = []
    for (c, r), changed_faces in sorted(grid.items()):
        cells = [c, r, c+1, r+1]
        assert 0 <= c < parent['w']-1 and 0 <= r < parent['h']-1
        for child in parent['patches']:
            a, b, A, B = child['coarseCells']; assert not (min(c+1, A)>max(c, a) and min(r+1, B)>max(r, b))
        x, z = x_origin+c*step, z_origin+r*step
        old_faces = [t for t in exact_grid.values() if t[:, 0].min()==x and t[:, 0].max()==x+step and t[:, 2].min()==z and t[:, 2].max()==z+step]
        assert len(old_faces) == 2
        capture_ids = set()
        for t in old_faces:
            matches = captured_by_key.get(face_key(t), []); assert len(matches) == 1; capture_ids.add(matches[0])
        assert changed_faces <= capture_ids and len(capture_ids) == 2
        output = after[[r['parentFace'] in capture_ids for r in lineage]]; assert len(output) >= 2
        meta = dict(georef=dict(aE=step, aN=-step, bE=x+834500, bN=816500-z, W=2, H=2),
                    parentTerrain=PARENT, parentSha256=parent_sha, targetUids=UIDS,
                    source=dict(provider='Lands Department/HKSAR', crs='EPSG:2326', verticalDatum='HKPD',
                                nativeSources=copy.deepcopy(parent['meta']['source'].get('nativeSources', [])),
                                privateSourceFloorReturn=binding))
        node = dict(id='private-lippo-source-floor-'+str(c)+'-'+str(r), w=2, h=2, cell=step,
                    elev=[1.2]*4, renderedElev=[1.2]*4, vegetation=[0]*4, coarseCells=cells, meta=meta,
                    nativeMesh=dict(position=output.reshape(-1).tolist(), index=list(range(output.size//3)),
                                    source=dict(verticalDatum='HKPD', verticalScale=1, privateSourceFloorReturn=binding)))
        node = refined_new_metadata(node, parent); candidate['patches'].append(node)
        added.append(dict(cells=cells, capturedFaces=sorted(capture_ids), outputFaces=len(output)))
    for index, old in enumerate(parent['patches']):
        if index not in native_groups: assert candidate['patches'][index] == old
    for field in ['w','h','cell','elev','renderedElev','vegetation','coarseCells']:
        assert candidate.get(field) == parent.get(field)
    candidate['meta']['targetUids'] = sorted(set(parent['meta']['targetUids']) | set(UIDS))
    candidate['meta']['source']['privateSourceFloorReturn'] = binding
    path = LOCAL / 'candidate-terrain.json'; save(path, candidate); refs.append(path)
    summary = dict(uids=UIDS, status='private-coordinated-floor-candidate-assembled', candidate=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())),
                   currentManifestSHA256=mh, replacedParent=dict(url=PARENT, sha256=parent_sha),
                   existingChildrenPreservedExcept=[15,17], existingCycleMembersRequiringFreshValidation=[12,15,17], fullFloorWorkEnvelope=list(outer.bounds), fullWorkCaptureFaces=len(before), changedParentFaces=len(changed),
                   addedGridChildren=added, fullGridArraysUnchanged=True, fullParentNotFlattened=True,
                   sourceGeometryChanges=0, sourcePoseChanges=0, physicalAcceptance=False, terrainValidatorPassed=False,
                   installationApproved=False, publication=False,
                   next='Revalidate complete effective coordinated graph, Float32 edges/coverage/overlap, fresh full affected native/BASIC/source scope and runtime. Historical cycle markers are not renewed by this private constructor.')
    save(BASE / BATCH / 'summary.json', summary)
    assert reservations.owns(lease) and digest(parent_path.read_bytes()) == parent_sha and digest(manifest.read_bytes()) == mh
    module('pair_coordinated_floor_candidate_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'private-exact-source-floor-lineage-partition-across-retained-grid-native-parent', list(dict.fromkeys(refs)), summary)
    print(dict(assembled=True, addedGridChildren=len(added), installationApproved=False), flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv: owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        parent = read(ROOT / '3d-viewer' / PARENT)
        keys = {'building:'+u for u in parent['meta']['targetUids']+UIDS} | {'terrain:'+PARENT, 'immutable-source-proof:'+BATCH}
        claim = reservations.claim('pair-coordinated-source-floor-' + str(uuid.uuid4()), sorted(keys), batch=BATCH, ttl=3600)
        assert claim['ok']
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
