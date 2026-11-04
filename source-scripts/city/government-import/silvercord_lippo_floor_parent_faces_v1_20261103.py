"""Map changed captured terrain faces to exact current native parent facets."""
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v3_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
TRIAL = 'government-xl-silvercord-lippo-private-source-floor-trial-v1-20261103'
RUNTIME = 'government-xl-silvercord-lippo-current-floor-sequence-v1-20261103-runtime'
BATCH = 'government-xl-silvercord-lippo-floor-parent-faces-v1-20261103'
LOCAL = HERE / 'local' / BATCH
UIDS = ['landsd/233997:0', 'landsd/231645:0']


def key(triangle): return tuple(sorted(tuple(float(v) for v in point) for point in triangle))


def owned():
    lease = read(LOCAL / 'reservation.json'); assert reservations.owns(lease)
    refs = [Path(__file__), ROOT / '3d-viewer/city/native-terrain.js', ROOT / '3d-viewer/city/world.js']; pins = {}
    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]; refs.append(BASE / batch / 'result.json')
        path = BASE / batch / name; assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    trial = take(TRIAL, 'summary.json'); ground = np.asarray(take(TRIAL, '231645-0/private-ground.json.gz')['before'], dtype='<f8')
    proof = take(TRIAL, '231645-0/return-proof.json.gz'); ids = proof['changedTerrainFaceIndices']
    assert len(ids) == len(set(ids)) and set(ids) < set(range(len(ground)))
    targets = {i: ground[i] for i in ids}; matches = {i: [] for i in ids}; lookup = {}
    for i, tri in targets.items(): lookup.setdefault(key(tri), []).append(i)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'; expected = take(RUNTIME, 'selection.json.gz')['manifestSHA256']
    assert digest(manifest.read_bytes()) == expected; refs.append(manifest)
    low = ground[ids].min((0, 1))[[0, 2]]; high = ground[ids].max((0, 1))[[0, 2]]
    parents = []; native_faces_examined = 0
    for entry in read(manifest)['terrainPatches']:
        path = ROOT / '3d-viewer' / entry['url']; raw = path.read_bytes(); terrain = read(path)
        def visit(node, node_path):
            nonlocal native_faces_examined
            if node.get('nativeMesh'):
                mesh = node['nativeMesh']; position = np.asarray(mesh['position'], dtype='<f4').reshape(-1, 3).astype('<f8')
                indices = np.asarray(mesh['index'], dtype=np.int64).reshape(-1, 3)
                triangles = position[indices]; native_faces_examined += len(triangles)
                xz = triangles[:, :, [0, 2]]
                candidates = np.flatnonzero(np.all(xz.max(1) >= low, axis=1) & np.all(xz.min(1) <= high, axis=1))
                for face in candidates:
                    for target in lookup.get(key(triangles[face]), []):
                        matches[target].append(dict(url=entry['url'], sha256=digest(raw), node=node_path, face=int(face)))
            for index, child in enumerate(node.get('patches', [])): visit(child, node_path + '/patches/' + str(index))
        visit(terrain, '')
        refs.append(path); parents.append(dict(url=entry['url'], sha256=digest(raw)))
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == expected
    rows = [dict(capturedFace=i, capturedVertices=targets[i].tolist(), nativeParentMatches=matches[i]) for i in ids]
    result = dict(uids=UIDS, currentManifestSHA256=expected, changedCapturedFaces=len(ids), rows=rows,
                  completeCurrentParentsScanned=parents, completeNativeFacesExamined=native_faces_examined,
                  uniquelyMatched=sum(len(v) == 1 for v in matches.values()),
                  unmatched=[i for i, v in matches.items() if not v], ambiguous=[i for i, v in matches.items() if len(v) > 1],
                  sourceGeometryChanges=0, physicalAcceptance=False, retainedParentAcceptance=False, installationApproved=False,
                  qualification='Exact unordered vertex triples of the actual Float32 native renderer. Winding and coarse/non-native ownership are not resolved by this source-only mapping. No unmatched face is dropped and no parent replacement or publication is approved.')
    save(BASE / BATCH / 'summary.json', result)
    module('pair_floor_parent_faces_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'exact-current-native-parent-facet-mapping-for-private-source-floor-return', list(dict.fromkeys(refs)), result)
    print({k: result[k] for k in ['changedCapturedFaces', 'uniquelyMatched', 'unmatched', 'ambiguous']}, flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv: owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('pair-floor-parent-faces-' + str(uuid.uuid4()), ['building:' + u for u in UIDS] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok']
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
