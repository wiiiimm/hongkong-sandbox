"""Revalidate the same immutable private terrain candidate against a fresh current capture."""
import argparse, copy
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'patch', 'capture']:
        ap.add_argument('--' + key, required=True)
    a = ap.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / a.batch, HERE / 'local' / a.batch
    assert not doc.exists() and not local.exists()
    receipt, pp = authenticate(base / a.patch)
    _, cp = authenticate(base / a.capture)
    refs = [Path(__file__), base / a.patch / 'result.json', base / a.capture / 'result.json']
    def take(path, pins):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    assert receipt['status'] == 'private-terrain-validator-passed'
    candidate = receipt['candidate']
    oldpath = ROOT / candidate['path']
    old = take(oldpath, pp)
    scope = take(base / a.patch / 'scope.json', pp)
    selected = take(base / a.capture / 'selection.json.gz', cp)
    source_uids = {r['uid'] for r in selected['rows']}
    assert set(receipt['uids']) == source_uids
    assert len(source_uids) == len(selected['rows'])
    assert {r['uid']: r['sourceSHA256'] for r in selected['rows']} == receipt['sourceSHA256ByUid']
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selected['manifestSHA256']
    current = read(manifest)
    replaced = candidate['replaces']
    assert sum(r['url'] == replaced['url'] for r in current['terrainPatches']) == 1
    active = ROOT / '3d-viewer' / replaced['url']
    assert digest(active.read_bytes()) == replaced['sha256']
    assert set(read(active)['meta']['targetUids']) == set(replaced['retainedUids'])
    assert set(old['meta']['targetUids']) == source_uids | set(replaced['retainedUids'])
    refs.extend([manifest, active])
    geometry = take(HERE / 'local' / a.capture / 'runtime-geometry.json.gz', cp)
    assert {r['uid'] for r in geometry['rows']} == source_uids
    x0, z0, x1, z1 = scope['bounds']
    for row in geometry['rows']:
        p = np.asarray(row['position']).reshape(-1, 3)
        assert np.all(p[:, 0] >= x0) and np.all(p[:, 0] <= x1)
        assert np.all(p[:, 2] >= z0) and np.all(p[:, 2] <= z1)
    for row in selected['rows']:
        path = ROOT / row['candidate']['path']
        assert digest(path.read_bytes()) == row['sourceSHA256']
        refs.append(path)
    patch = copy.deepcopy(old)
    assert patch['meta']['targetUids'] == old['meta']['targetUids']
    patch['nativeMesh'].pop('sourceOverlap', None)
    overlap = module('source_scope_overlap', HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py')
    overlap.DOC = doc
    overlap.overlap_proof(patch, [oldpath, base / a.capture / 'selection.json.gz', Path(__file__)])
    assert patch['nativeMesh']['position'] == old['nativeMesh']['position']
    assert patch['nativeMesh']['index'] == old['nativeMesh']['index']
    parent = ROOT / '3d-viewer/city/data/terrain.json'
    builder = module('source_scope_validator', HERE / 'validated_parent_roundoff_template_v2.py')
    builder.validate_patch(patch, read(parent))
    refs.append(parent)
    assert digest(manifest.read_bytes()) == selected['manifestSHA256']
    assert digest(active.read_bytes()) == replaced['sha256']
    save(doc / 'scope.json', {**scope, 'uids': sorted(source_uids)})
    path = local / 'candidate-terrain.json'
    save(path, patch)
    meshsha = digest(np.asarray(patch['nativeMesh']['position'], dtype='<f8').tobytes() + np.asarray(patch['nativeMesh']['index'], dtype='<u4').tobytes())
    report = dict(uids=sorted(source_uids), status='private-terrain-validator-passed',
                  candidate=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()), replaces=candidate['replaces']),
                  sourceSHA256ByUid={r['uid']: r['sourceSHA256'] for r in selected['rows']},
                  sourceTerrainGeometryUnchanged=True, targetSetUnchanged=True,
                  historicalApprovalTransferred=False, currentManifestSHA256=selected['manifestSHA256'], terrainMeshSHA256=meshsha,
                  terrainTriangles=len(patch['nativeMesh']['index']) // 3,
                  sourceGeometryChanges=0, installationApproved=False,
                  qualification='Exact prior private candidate mesh and target set retained byte-for-value; active replacement parent verified unchanged against the fresh current scene. Overlap provenance rebound and normal native validation rerun. Neither source is declared supported or accepted; full current source/identity/support/neighbour/four-world/browser gates remain.')
    save(doc / 'summary.json', report)
    refs += [path, HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py', HERE / 'validated_parent_roundoff_template_v2.py']
    module('terrain_source_scope_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'explicit-unchanged-terrain-current-scene-revalidation', refs, report)


if __name__ == '__main__':
    main()
