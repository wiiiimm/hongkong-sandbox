"""Preserve exact existing parent terrain outside new and retained original meshes.

Dedicated retained native replacement route: verifies the complete previous Neon
receipt, current original runtime meshes and replacement source bytes. The parent
mask excludes every new and retained original face projection; full physical
and runtime checks are mandatory for all models after preparation.

Fresh continuation only. Compare an explicit original-parent mask; never change any acceptance limit. Re-run complete
source, foundation, runtime and neighbour gates; no geometry or tolerance waiver.
"""
import argparse
import importlib.util
import json
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, reservations, connect


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


def owned(args, doc, local):
    lease = read(local / 'reservation.json'); assert reservations.owns(lease)
    previous = ROOT / args.previous
    old_selection = read(previous / 'selection.json.gz'); rows = old_selection['rows']
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest_path.read_bytes()) == old_selection['manifestSHA256']
    identity_record=read(previous/'identity-proof.json')
    from government_georef_cell_identity import POLICY
    assert identity_record['method']==POLICY
    positive=read(previous/'owned-source-identity.json')
    assert positive['passed'] and positive==read(previous/'owned-source-identity-contact.json')
    assert identity_record['ownedSourceProofSHA256']==digest((previous/'owned-source-identity.json').read_bytes())
    save(doc/'owned-source-identity.json',positive)
    save(doc/'owned-source-identity-contact.json',positive)
    preflight=read(previous/'indexed-preflight.json')
    assert preflight['uid']==rows[0]['uid'] and preflight['sourceSHA256']==rows[0]['sourceSHA256'] and preflight['identity']['method']==POLICY
    for path,sha in preflight['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
    save(doc/'indexed-preflight.json',preflight)
    original = read(previous / 'terrain-candidates.json')[0]
    assert digest((ROOT / original['path']).read_bytes()) == original['sha256']
    replacement = original['replaces']
    assert replacement['url'] in {p['url'] for p in read(manifest_path)['terrainPatches']}
    assert digest((ROOT/'3d-viewer'/replacement['url']).read_bytes()) == replacement['sha256']
    prior=read(previous/'result.json'); sync=read(previous/'neon-sync.json')
    assert sync['resultVerified'] and sync['jobId']==prior['jobId']
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
    for ref in prior['evidenceRefs']: assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
    retained_ref=read(previous/'retained-native-geometry-inputs.json')
    geometry_ref=retained_ref['geometry']
    assert digest((ROOT/geometry_ref['path']).read_bytes())==geometry_ref['sha256']
    retained_geometry=read(ROOT/geometry_ref['path'])
    assert {r['uid'] for r in retained_geometry['rows']}==set(replacement['retainedUids'])
    for path,sha in retained_geometry['inputHashes'].items(): assert digest((ROOT/path).read_bytes())==sha
    assert args.mask=='outside-source', 'Retained originals require source-disjoint parent preservation'
    save(doc/'retained-native-geometry-inputs.json',retained_ref)
    save(doc/'retained-routing.json',read(previous/'retained-routing.json'))
    inputs = read(previous / 'neighbour-inputs.json.gz')
    for path, sha in inputs['inputHashes'].items(): assert digest((ROOT / path).read_bytes()) == sha
    second = module('disjoint_source_triangles', 'xl-second-pass.py'); second.LOCAL = local
    patches = module('disjoint_original_parent', 'native_patch_resolution.py')
    final = module('disjoint_full_foundation', 'xl-final-script-pass.py')
    bodies = []
    for row in rows:
        raw = (ROOT / row['candidate']['path']).read_bytes(); assert digest(raw) == row['sourceSHA256']
        destination = local / 'assets' / (row['sourceSHA256'] + '.glb.gz')
        destination.parent.mkdir(parents=True, exist_ok=True); destination.write_bytes(raw)
        row['candidate']['path'] = str(destination.relative_to(ROOT)); bodies.append(second.glb_triangles(row))
    source_projection = shapely.union_all([shapely.MultiPoint(face[:, [0, 2]]).convex_hull for body in bodies for face in body])
    retained_projections=[]
    for retained in retained_geometry['rows']:
        positions=np.asarray(retained['position']).reshape(-1,3)
        faces=positions[np.asarray(retained['index']).reshape(-1,3)]
        retained_projections.extend(shapely.MultiPoint(face[:,[0,2]]).convex_hull for face in faces)
    source_projection=shapely.union_all([source_projection,*retained_projections])
    by_uid = {r['building']['uid']: r for r in inputs['rows']}
    native = read(previous / 'native-neighbour-checks.json'); resolved = set(native['resolved'])
    protect, rejected = [], []
    for check in read(previous / 'neighbour-checks.json')['rows']:
        if not check['reasons'] or check['uid'] in resolved: continue
        row = by_uid[check['uid']]; b = row['building']; protected = Polygon(b['rings'][0], b['rings'][1:]).buffer(.01, join_style='mitre')
        area = float(protected.intersection(source_projection).area)
        if row['existingNative']:
            rejected.append({'uid': b['uid'], 'bufferedSourceIntersectionM2': area,
                             'reason': 'full-native-neighbour-required' if row['existingNative'] else 'overlapping-source-projection'})
        else:
            # Preserve only outside all original face projections. The buffer
            # protects Float32 boundaries as well as vertical line/point faces.
            clipped = protected if args.mask == 'complete-basic-footprint' else protected.difference(source_projection.buffer(.01, join_style='mitre'))
            if clipped.area > 1e-8:
                protect.append((b['uid'], clipped))
            if area >= 1e-8:
                rejected.append({'uid': b['uid'], 'bufferedSourceIntersectionM2': area,
                    'reason': 'whole-footprint-test-requires-all-source-foundation-contact-gates' if args.mask == 'complete-basic-footprint' else 'overlapping-portion-excluded-from-parent-preservation',
                    'preservedAreaM2': float(clipped.area)})
    assert protect, 'No source-disjoint portion of a failing basic neighbour to preserve'
    protected = shapely.union_all([p for _, p in protect])
    if args.mask == 'outside-source': assert protected.intersection(source_projection).area < 1e-8
    patch = read(ROOT / original['path']); bounds = original['bounds']
    parent = read(ROOT / '3d-viewer/city/data/terrain.json')
    sampler = second.resolution.terrain.fine.DemSampler(parent, rendered=True)
    terrain = read(previous / 'terrain.json')
    for source in terrain['sourceFiles']: assert digest((ROOT / source['path']).read_bytes()) == source['sha256']
    proof = patches.preserve_parent_under_projection(patch, bounds, protected, sampler)
    proof.update(protectedUids=[u for u, _ in protect], rejected=rejected,
                 mask=args.mask, policy='Exact original parent planes within the explicit mask; no invented heights. Entire source contact, foundation and all neighbour/runtime gates remain required.',
                 sourceProjectionIntersectionM2=float(protected.intersection(source_projection).area),
                 minimumDistanceFromSourceM=float(protected.distance(source_projection)))
    missing = patches.projected_context(patch, bounds)[2]
    if missing.intersection(source_projection).area >= 1e-6:
        patches.fill_narrow_source_seam(patch, bounds, source_projection, sampler, tolerance=.02)
    else:
        patches.fill_parent_only_holes(patch, parent, bounds, source_projection, sampler)
    patch['nativeMesh']['source']['finalBoundarySnap'] = patches.snap_boundary_to_parent(patch, bounds, sampler)
    path = local / Path(original['path']).name; save(path, patch)
    if patches.projected_context(patch, bounds)[3] > 1e-8:
        patches.approve_original_overlap(patch, path, doc / 'protected-overlap.json', terrain['sourceFiles'])
        patches.finalize_overlap_evidence(patch, doc / 'protected-overlap.json')
    else: patch['nativeMesh'].pop('sourceOverlap', None)
    second.resolution.validate_patch(patch, parent); save(path, patch)
    candidate = {**original, 'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes()),
                 'triangles': len(patch['nativeMesh']['index']) // 3}
    save(doc / 'terrain-candidates.json', [candidate])
    save(doc / 'terrain.json', {**terrain, 'patch': candidate})
    inputs['patches'] = [candidate]; save(doc / 'neighbour-inputs.json.gz', inputs)
    save(doc / 'selection.json.gz', {**old_selection, 'batch': args.batch, 'rows': rows})
    catalogue = read(HERE / 'local' / previous.name / 'catalogue.json')
    save(local / 'catalogue.json', catalogue); save(local / 'catalogue-index.json', {'models': len(rows), 'catalogues': ['catalogue.json']})
    save(local / 'source-forms.json', {r['uid']: r['source'] for r in rows})
    refs = [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p.read_bytes())}
            for p in sorted(previous.iterdir()) if p.is_file() and p.suffix in ('.json', '.gz')]
    save(doc / 'parent-preservation.json', {'previousEvidenceRefs': refs, 'previousPatch': original,
                                           'candidatePatch': candidate, 'proof': proof,
                                           'runner': {'path': str(Path(__file__).relative_to(ROOT)), 'sha256': digest(Path(__file__).read_bytes())},
                                           'modelGeometryChanges': 0, 'scriptExternalAICalls': 0, 'publication': False})
    def call(command, allowed=(0,)):
        assert subprocess.run(command, cwd=ROOT).returncode in allowed
        assert reservations.owns(lease)
    rel = lambda p: str(p.relative_to(ROOT))
    call(['node', str(HERE / 'acceptance-metrics.mjs'), '--selection', rel(doc / 'selection.json.gz'),
          '--candidates', rel(local), '--terrain-candidates', rel(doc / 'terrain-candidates.json'),
          '--out', rel(doc / 'metrics.json'), '--geometry-out', rel(local / 'runtime-geometry.json.gz')])
    call(['node', str(HERE.parent / 'building-batch/validate_candidates.mjs'), '--candidates', rel(local),
          '--source-forms', rel(local / 'source-forms.json'), '--terrain-candidates', rel(doc / 'terrain-candidates.json'),
          '--out', rel(doc / 'validation.json')], (0, 1))
    call(['node', str(HERE / 'check-neighbours.mjs'), rel(doc) + '/'])
    call(['node', str(HERE / 'check-native-neighbours.mjs'), rel(doc) + '/'])
    runtime = {r['uid']: r for r in read(local / 'runtime-geometry.json.gz')['rows']}; foundations = []
    for row in rows:
        geometry = runtime[row['uid']]; triangles = np.asarray(geometry['position']).reshape(-1, 3)[np.asarray(geometry['index']).reshape(-1, 3)]
        ground = np.asarray(geometry['drawnGroundGeometry']).reshape(-1, 3, 3); b = row['source']['building']
        foundation = final.foundation_context(triangles, ground, Polygon(b['rings'][0], b['rings'][1:]))
        foundations.append({'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'], 'foundation': foundation,
                            'strictFoundationAccepted': foundation['completeTerrainTriangles'] == foundation['triangles'] and not foundation['fullyBuriedUpwardTriangles'] and foundation['fullyBuriedAreaFraction'] == 0})
    save(doc / 'foundation.json', {'rows': foundations, 'modelGeometryChanges': 0})
    assert len(rows) == 1
    identity = read(previous / 'identity-proof.json'); assert identity['sourceSHA256'] == rows[0]['sourceSHA256']
    save(doc / 'identity-proof.json', identity)
    metrics = read(doc / 'metrics.json'); policy = module('disjoint_existing_policy', 'acceptance-policy.py')
    for path, sha in metrics['inputHashes'].items(): assert digest((ROOT / path).read_bytes()) == sha
    reasons = policy.reasons({'state': 'runtime-validated-awaiting-acceptance', 'sourceSHA256': rows[0]['sourceSHA256'],
                              'identityProof': identity['proof']}, metrics['rows'][0], metrics['profiles']['mobile'])
    if not foundations[0]['strictFoundationAccepted']: reasons.append('whole-source-foundation')
    reasons.extend(read(doc / 'validation.json')['results'][0].get('concerns', []))
    native = read(doc / 'native-neighbour-checks.json'); resolved = set(native['resolved'])
    reasons.extend('native-neighbour-regression:' + u for u in set(native['blocked']) - resolved)
    reasons.extend('terrain-regresses-neighbour:' + r['uid'] for r in read(doc / 'neighbour-checks.json')['rows'] if r['reasons'] and r['uid'] not in resolved)
    print(json.dumps({'protected': proof['protectedUids'], 'overlappingStillBlocked': rejected}), flush=True)
    module('disjoint_neon_result', 'xl-cell-indexed-terrain-continuation.py').finish(args, rows[0], doc, local, reasons)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--previous', required=True); parser.add_argument('--batch', required=True)
    parser.add_argument('--mask', choices=['outside-source', 'complete-basic-footprint'], default='outside-source')
    parser.add_argument('--owned', action='store_true', help=argparse.SUPPRESS); args = parser.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    doc = ROOT / 'docs/astra-city/government-import' / args.batch; local = HERE / 'local' / args.batch
    if args.owned: owned(args, doc, local); return
    assert not doc.exists(), 'Fresh continuation only'
    previous = ROOT / args.previous; inputs = read(previous / 'neighbour-inputs.json.gz')
    uids = {r['building']['uid'] for r in inputs['rows']} | {r['uid'] for r in read(previous / 'selection.json.gz')['rows']}
    replacement=read(previous/'terrain-candidates.json')[0]['replaces']
    uids.update(replacement['retainedUids'])
    resources = [('building:' if u.startswith('landsd/') else 'source-form:') + u for u in sorted(uids)]
    resources += ['terrain-surface:'+replacement['url']]
    claim = reservations.claim('codex-xl-partial-parent-' + str(uuid.uuid4()), resources, batch=args.batch); assert claim['ok'], claim
    save(local / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(local / 'reservation.json'),
                    '--', sys.executable, __file__, '--previous', args.previous, '--batch', args.batch, '--mask', args.mask, '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__': main()
