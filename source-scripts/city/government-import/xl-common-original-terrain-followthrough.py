"""Prepare an explicit source-bound common original terrain candidate, then run all physical gates.

This replaces the old terrain candidate in diagnostics; it does not retain its
rendered surface by assertion or publish anything. Existing installed meshes are
unchanged and explicitly require full before/after native neighbor checks.
"""
import argparse
import importlib.util
import json
import subprocess
import sys
import traceback
import uuid
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import box
from run import ROOT, read, save, digest, reservations, connect
from government_georef_cell_identity import verify_files, POLICY

DIR = ROOT / 'source-scripts/city/government-import'
UID = 'landsd/338637:0'
OLD_URL = 'city/data/government-native-338638-0.json'
BASE = ROOT / 'docs/astra-city/government-import/government-xl-sustained-131-inputs-20261006'
SOURCE_DOC = ROOT / 'docs/astra-city/government-import/government-xl-three-retained-exact-footprints-20261007-338637-0'
AUDIT = ROOT / 'docs/astra-city/government-import/government-xl-held-current-directory-audit-20261007'


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, DIR / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def prepare(args, doc, local):
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = read(manifest_path)
    if OLD_URL: assert OLD_URL in {r['url'] for r in manifest['terrainPatches']}
    old_path = ROOT / '3d-viewer' / OLD_URL if OLD_URL else None
    old = read(old_path) if old_path else None
    if old: assert old.get('nativeMesh') and not old.get('patches')
    selected = read(BASE / 'check-selection.json.gz')
    row = next(r for r in selected['rows'] if r['uid'] == UID)
    context = next(r for r in read(BASE / 'context.json.gz')['rows'] if r['uid'] == UID)
    assert row['currentReview'] is None
    entries = {m['uid']: m for url in manifest['officialModelCatalogues']
               for m in read(ROOT / '3d-viewer' / url)['models']}
    assert UID not in entries
    retained = old['meta']['targetUids'] if old else []
    assert all(uid in entries for uid in retained)
    pointer = read(ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json')
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT review_state FROM astra_modelling.model_reviews WHERE uid=%s ORDER BY updated_at DESC LIMIT 1', (UID,)).fetchone() is None
        for uid in retained:
            assert con.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s', (pointer['snapshotId'], uid)).fetchone() == ('installed-verified', entries[uid]['sha256'])
    identity = verify_files(row, context, local / 'identity')
    assert identity['passed'], identity['reasons']
    assert identity['policy'] == POLICY
    save(doc / 'owned-source-identity.json', identity)
    save(doc / 'owned-source-identity-contact.json', identity)
    save(doc / 'identity-proof.json', {'uid': UID, 'sourceSHA256': row['sourceSHA256'], 'proof': identity['proof'], 'method': POLICY, 'ownedSourceProofSHA256':ref(doc/'owned-source-identity.json')['sha256']})
    raw = (ROOT / row['candidate']['path']).read_bytes()
    assert digest(raw) == row['sourceSHA256']
    asset = local / 'assets' / (row['sourceSHA256'] + '.glb.gz')
    asset.parent.mkdir(parents=True, exist_ok=True)
    asset.write_bytes(raw)
    row['candidate']['path'] = str(asset.relative_to(ROOT))
    old_local = DIR / 'local' / SOURCE_DOC.name
    for name in ('catalogue.json', 'catalogue-index.json', 'source-forms.json'):
        save(local / name, read(old_local / name))
    save(doc / 'selection.json.gz', {**selected, 'batch': args.batch, 'rows': [row], 'previousManifestSHA256': selected['manifestSHA256'], 'manifestSHA256': digest(manifest_path.read_bytes())})
    second = module('alto_original_decoder', 'xl-second-pass.py')
    patches = module('alto_original_patch', 'native_patch_resolution.py')
    final = module('alto_forms', 'xl-final-script-pass.py')
    indexed = module('alto_receipt', 'xl-cell-indexed-terrain-continuation.py')
    recovery = read(SOURCE_DOC / 'source-recovery.json')
    assert len(recovery['sheets']) == 1
    route = recovery['sheets'][0]
    folder = ROOT / route['cache']
    receipt, files = indexed.verified_terrain(folder)
    assert receipt['directorySHA256'] == route['directorySHA256']
    audit = read(AUDIT / 'result.json')
    # The source audit row is an exact official directory receipt, not a guessed revision.
    source_rows = audit.get('rows', [])
    if not source_rows:
        source_rows = read(AUDIT / 'audit.json')['rows']
    current = next(r for r in source_rows if r['uid'] == UID)
    assert route['directorySHA256'] in json.dumps(current)
    source_refs = [ref(folder / 'terrain' / item['name']) for item in files]
    native = np.concatenate([second.terrain_triangles(p) for p in sorted((folder / 'terrain').rglob('*.gltf'))])
    parent_path = ROOT / '3d-viewer/city/data/terrain.json'
    parent = read(parent_path)
    own = row['native']['model']['worldBounds']
    cells = second.resolution.rectangle_for(own, parent)
    if old: cells = [min(cells[0], old['coarseCells'][0]), min(cells[1], old['coarseCells'][1]), max(cells[2], old['coarseCells'][2]), max(cells[3], old['coarseCells'][3])]
    bounds = second.resolution.extent(cells, parent)
    for item in manifest['terrainPatches']:
        if item['url'] == OLD_URL:
            continue
        assert box(*bounds).intersection(box(*patches._patch_bounds(read(ROOT / '3d-viewer' / item['url'])))).area < 1e-8
    world = [own] + [entries[uid]['worldBounds'] for uid in retained]
    core = [min(b[0][0] for b in world)-1, min(b[0][2] for b in world)-1, max(b[1][0] for b in world)+1, max(b[1][2] for b in world)+1]
    assert box(*bounds).covers(box(*core))
    native = native[(native[:, :, 0].max(axis=1) >= bounds[0]) & (native[:, :, 0].min(axis=1) <= bounds[2]) & (native[:, :, 2].max(axis=1) >= bounds[1]) & (native[:, :, 2].min(axis=1) <= bounds[3])]
    used = [{'sheet': folder.name, 'revision': receipt['revisionDate'], 'sourceETag': receipt['sourceETag'], 'directorySHA256': receipt['directorySHA256'], 'sourceFiles': source_refs}]
    validator = second.resolution.validate_patch
    second.resolution.validate_patch = lambda *_: None
    try:
        patch = second.resolution.make_patch({'uids': [UID, *retained], 'cells': cells}, parent, native, used, native_core=core, terrain_triangle_budget=100000, allow_native_below_clamp=bool((native[:, :, 1] < 1.2).any()), parent_url='city/data/terrain.json', parent_sha256=digest(parent_path.read_bytes()))
    finally:
        second.resolution.validate_patch = validator
    sampler = second.resolution.terrain.fine.DemSampler(parent, rendered=True)
    # Holes may use the unchanged parent only outside every original model box.
    protected = shapely.union_all([box(b[0][0], b[0][2], b[1][0], b[1][2]) for b in world])
    fill = patches.fill_parent_only_holes(patch, parent, bounds, protected, sampler)
    remaining = float(patches.projected_context(patch, bounds)[2].area)
    maximum = max(.25, (bounds[2]-bounds[0])*(bounds[3]-bounds[1])*1e-3)
    assert remaining <= maximum
    if remaining > 1e-8:
        patch['nativeMesh']['source']['numericalCoverageGap'] = {'policy': 'parent-grid-fallback', 'measuredAreaM2': remaining, 'maximumAreaM2': maximum, 'maximumFraction': 1e-3}
    patch['nativeMesh']['source']['finalBoundarySnap'] = patches.snap_boundary_to_parent(patch, bounds, sampler)
    path = local / (patch['id']+'.json')
    save(path, patch)
    if patches.projected_context(patch, bounds)[3] > 1e-8:
        patches.approve_original_overlap(patch, path, doc / 'native-overlap.json', source_refs)
        patches.finalize_overlap_evidence(patch, doc / 'native-overlap.json')
    validator(patch, parent)
    save(path, patch)
    candidate = {**ref(path), 'uids': [UID], 'bounds': bounds, 'triangles': len(patch['nativeMesh']['index'])//3}
    if old: candidate['replaces'] = {'url': OLD_URL, 'sha256': digest(old_path.read_bytes()), 'retainedUids': retained}
    save(doc / 'terrain-candidates.json', [candidate])
    save(doc / 'terrain.json', {'patch': candidate, 'sourceFiles': source_refs, 'parentHoleFill': fill, 'modelGeometryChanges': 0})
    neighbors = final.load_forms(bounds)
    save(doc / 'neighbour-inputs.json.gz', {'rows': [{'building': b, 'patchIndexes': [0], 'existingNative': b['uid'] in entries or bool(b.get('modelGeometry'))} for b, _, _ in neighbors], 'inputHashes': {str((ROOT/'3d-viewer'/url).relative_to(ROOT)): digest((ROOT/'3d-viewer'/url).read_bytes()) for _, _, url in neighbors}, 'candidateIds': [UID], 'patches': [candidate]})
    save(doc / 'common-original-terrain-proof.json', {'uid': UID, 'retainedUids': retained, 'currentSnapshot': pointer['snapshotId'], 'sourceFiles': source_refs, 'inputRefs': [ref(Path(__file__)), ref(manifest_path), *([ref(old_path)] if old_path else []), ref(AUDIT/'result.json'), ref(SOURCE_DOC/'source-recovery.json')], 'bounds': bounds, 'nativeCore': core, 'oldRenderedTerrainPreserved': False, 'qualification': 'Candidate replaces the old terrain using original government facets. Every retained native model requires full physical checks; no disjointness or compatibility is inferred.', 'publication': False, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0})
    assert reservations.owns(lease)
    print(json.dumps({'prepared': args.batch, 'retained': retained, 'triangles': candidate['triangles']}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', required=True)
    parser.add_argument('--owned', action='store_true')
    parser.add_argument('--uid',required=True)
    parser.add_argument('--base',required=True)
    parser.add_argument('--source',required=True)
    parser.add_argument('--replaces')
    args = parser.parse_args()
    global UID,BASE,SOURCE_DOC,OLD_URL
    UID=args.uid;BASE=(ROOT/args.base).resolve();SOURCE_DOC=(ROOT/args.source).resolve();OLD_URL=args.replaces
    assert UID.startswith('landsd/') and BASE.is_relative_to(ROOT/'docs/astra-city/government-import') and SOURCE_DOC.is_relative_to(ROOT/'docs/astra-city/government-import')
    assert args.batch.startswith('government-xl-') and Path(args.batch).name == args.batch
    doc = ROOT / 'docs/astra-city/government-import' / (args.batch+'-prepared')
    local = DIR / 'local' / doc.name
    if args.owned:
        try:
            prepare(args, doc, local)
        except Exception:
            save(doc/'construction-failure.json', {'traceback': traceback.format_exc(), 'publication': False, 'newlyInstalled': 0})
            raise
        return
    assert not doc.exists(), 'Fresh attempt only'
    final = module('alto_scope', 'xl-final-script-pass.py')
    old = read(ROOT/'3d-viewer'/OLD_URL) if OLD_URL else None
    row=next(r for r in read(BASE/'check-selection.json.gz')['rows'] if r['uid']==UID)
    lo,hi=row['native']['model']['worldBounds'];bounds=[lo[0]-100,lo[2]-100,hi[0]+100,hi[2]+100]
    if old:
        other=module('common_scope_bounds','native_patch_resolution.py')._patch_bounds(old)
        bounds=[min(bounds[0],other[0]-100),min(bounds[1],other[1]-100),max(bounds[2],other[2]+100),max(bounds[3],other[3]+100)]
    scope={UID,*(old['meta']['targetUids'] if old else []),*(b['uid'] for b,_,_ in final.load_forms(bounds))}
    claim = reservations.claim('codex-alto-common-'+str(uuid.uuid4()), [('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope)]+(['terrain-surface:'+OLD_URL] if OLD_URL else ['terrain-patch:'+UID]), batch=args.batch)
    assert claim['ok'], claim
    save(local/'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(DIR.parent/'shared-modelling/reservations.py'), 'run', '--lease-file', str(local/'reservation.json'), '--', sys.executable, __file__, '--batch', args.batch, '--uid',UID,'--base',args.base,'--source',args.source,*(['--replaces',OLD_URL] if OLD_URL else []),'--owned'], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(DIR/'xl-cell-installation-recheck.py'), '--previous', str(doc.relative_to(ROOT)), '--batch', args.batch,'--base',args.base], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
