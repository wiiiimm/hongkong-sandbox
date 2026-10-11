"""Resume one frozen XL source with indexed original terrain and existing gates.

Explicit fresh batch only. Reuse verified terrain receipts before downloads. This
runner uses explicit original mesh/GeoRef identity instead of the roof-area ratio;
physical acceptance limits, original geometry and publication gates remain unchanged.
"""
import argparse
import importlib.util
import json
import subprocess
import traceback
import uuid
import zipfile
from pathlib import Path

from run import ROOT, HERE, read, save, digest, reservations, connect, jobs, Jsonb, dict_row, NATIVE_RUN
from terrain_source_preflight import SourceSheetIndex, preflight
from government_georef_cell_identity import verify_files, POLICY

TERRAIN_PIPELINE_PATH = HERE / "xl-pending-cell-contact-resolution.py"
import sys
sys.path.insert(0, str(HERE.parent / 'enhancement-screening'))
from shape_prepare import scan, acquire


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def verified_terrain(folder):
    """A directory name alone never establishes provenance or completeness."""
    try:
        receipt = read(folder / 'original/download.json')
        directory = read(folder / 'directory/result.json')
        assert receipt['directorySHA256'] == directory['directorySHA256']
        assert receipt['terrainGeometryIncluded'], 'Receipt does not contain complete terrain geometry'
        assert receipt['sheet'] == directory['sheet'] == folder.name
        files = [e for e in receipt['entries'] if e['name'].startswith('TERRAIN')
                 and e['name'].endswith(('.gltf', '.bin'))]
        assert any(e['name'].endswith('.gltf') for e in files)
        assert all(digest((folder / 'terrain' / e['name']).read_bytes()) == e['sha256'] for e in files)
        return receipt, files
    except (OSError, KeyError, AssertionError, ValueError):
        return None


def terrain_sheet(sheet, local):
    # Search only the established source-cache layout, not source references.
    for folder in sorted((HERE / 'local').glob('*/sheets/' + sheet)):
        proof = verified_terrain(folder)
        if proof:
            receipt, files = proof
            return folder, {'sheet': sheet, 'method': 'verified-local-original-terrain',
                            'cache': str(folder.relative_to(ROOT)), 'transferredBytes': 0,
                            'directorySHA256': receipt['directorySHA256'], 'terrainFiles': files}
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        pinned = con.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1", (sheet,)).fetchone()[0]
    folder = local / 'sheets' / sheet
    directory, _ = scan({'SHEETNO': sheet, 'Format_glTF': pinned['sourceURL'],
                         'REVISIONDATE': pinned['revision']}, folder / 'directory')
    directory['models'] = []
    receipt = acquire(directory, folder / 'directory/zip-directory.bin', folder / 'original', include_terrain=True)
    with zipfile.ZipFile(folder / 'original' / (sheet + '.zip')) as archive:
        for entry in receipt['entries']:
            if entry['name'].startswith('TERRAIN') and entry['name'].endswith(('.gltf', '.bin')):
                target = folder / 'terrain' / entry['name']
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(entry['name']))
    proof = verified_terrain(folder)
    assert proof, 'Recovered terrain lacks an exact complete receipt'
    return folder, {'sheet': sheet, 'method': 'original-government-recovery',
                    'cache': str(folder.relative_to(ROOT)),
                    'transferredBytes': receipt['newThisInvocationBytes'],
                    'directorySHA256': receipt['directorySHA256'], 'terrainFiles': proof[1]}


def finish(args, row, doc, local, reasons):
    receipt = read(local / 'reservation.json')
    assert reservations.owns(receipt)
    refs = [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p.read_bytes())}
            for p in sorted(doc.iterdir()) if p.is_file() and p.name not in ('result.json', 'neon-sync.json', 'README.md')]
    payload = {'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'], 'evidenceRefs': refs,
               'runnerSHA256': digest(Path(__file__).read_bytes()),
               'terrainPipelineSHA256': digest(TERRAIN_PIPELINE_PATH.read_bytes()), 'identityPolicy': POLICY}
    stage = 'full-cell-original-terrain-continuation-v1'
    jobid = jobs.enqueue(args.batch, stage, payload)
    job = jobs.claim(args.batch, receipt['owner'], [stage], lease_seconds=1800)
    assert job and job['id'] == jobid
    result = {**payload, 'jobId': jobid, 'batch': args.batch, 'reasons': sorted(set(reasons)),
              'humanStatus': 'held-unknown' if reasons else 'in-process',
              'scriptChecksPassed': not reasons, 'newlyInstalled': 0, 'publication': False,
              'modelGeometryChanges': 0, 'scriptExternalAICalls': 0, 'activeWorkers': 0,
              'queuedFollowups': 0, 'requiresAI': False, 'requiresHumanDecision': False,
              'nextStep': 'Resolve exact recorded original terrain/source/support blockers with unchanged physical acceptance limits.' if reasons else 'Complete staged and live browser checks, guarded publication and installed ledger.'}
    with connect() as con:
        from pending_original_review import verify
        from psycopg.rows import tuple_row
        con.row_factory = tuple_row
        verify(con, row['uid'], row['sourceSHA256'], row['currentReview'])
        con.row_factory = dict_row
        con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
        assert reservations._current(con, receipt)
        actual = con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, row['native']['cacheKey'])).fetchone()
        assert actual and actual['result_sha'] == row['native']['resultSha']
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jobid, job['owner'], job['token'])).rowcount == 1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s', (jobid,)).fetchone()[0] == result
    save(doc / 'result.json', result)
    save(doc / 'neon-sync.json', {'jobId': jobid, 'resultVerified': True})
    print(json.dumps({'uid': row['uid'], 'checksPassed': not reasons, 'reasons': result['reasons'], 'jobId': jobid, 'neonVerified': True}), flush=True)


def owned(args, doc, local):
    assert reservations.owns(read(local / 'reservation.json'))
    base = ROOT / args.base
    selected = read(base / 'check-selection.json.gz')
    row = next(r for r in selected['rows'] if r['uid'] == args.uid)
    context = next(r for r in read(base / 'context.json.gz')['rows'] if r['uid'] == args.uid)
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    assert not any(m['uid'] == args.uid for url in manifest['officialModelCatalogues']
                   for m in read(ROOT / '3d-viewer' / url)['models']), 'Already installed'
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        from pending_original_review import verify
        pending = verify(con, args.uid, row['sourceSHA256'], row['currentReview'])
    save(doc / 'pending-review-continuation.json', {'current': pending, 'pinned': row['currentReview'], 'modelGeometryChanges': 0, 'publication': False})
    assert digest((ROOT / row['candidate']['path']).read_bytes()) == row['sourceSHA256']
    assert digest((ROOT / '3d-viewer' / row['source']['tile']).read_bytes()) == row['source']['tileSHA256']
    for path, sha in context['neighbourTileHashes'].items():
        assert digest((ROOT / '3d-viewer' / path).read_bytes()) == sha
    index_path = ROOT / 'source-scripts/city/landmark-acquisition/index.json'
    routing = preflight(row, context, SourceSheetIndex(read(index_path)))
    positive = verify_files(row, context, local / 'identity-precheck')
    save(doc / 'owned-source-identity.json', positive)
    routing['legacyProjectionIdentity'] = routing['identity']
    routing['identity'] = {'passed': positive['passed'], 'proof': positive['proof'],
                           'reasons': positive['reasons'], 'method': POLICY}
    routing['canStartTerrainWork'] = positive['passed'] and routing['primarySheetIntersects']
    routing['qualification'] = 'Explicit positive original government ownership/GeoRef identity route; all downstream original terrain, foundation, neighbour and runtime checks required.'
    routing['inputHashes'] = {str(index_path.relative_to(ROOT)): digest(index_path.read_bytes()),
                              str((base / 'check-selection.json.gz').relative_to(ROOT)): digest((base / 'check-selection.json.gz').read_bytes()),
                              str((base / 'context.json.gz').relative_to(ROOT)): digest((base / 'context.json.gz').read_bytes()),
                              str((HERE / 'terrain_source_preflight.py').relative_to(ROOT)): digest((HERE / 'terrain_source_preflight.py').read_bytes())}
    for filename in ['government_georef_cell_identity.py', 'original_source_ownership.py',
                     'test_government_georef_cell_identity.py', 'xl-second-pass.py',
                     'pending_original_review.py', 'test_pending_original_review.py']:
        path = HERE / filename
        routing['inputHashes'][str(path.relative_to(ROOT))] = digest(path.read_bytes())
    save(doc / 'indexed-preflight.json', routing)
    if not routing['canStartTerrainWork']:
        finish(args, row, doc, local, routing['identity']['reasons'] or ['source-sheet-identity'])
        return
    recovered = [terrain_sheet(s['sheet'], local) for s in routing['indexedSheets']]
    save(doc / 'source-recovery.json', {'uid': args.uid, 'sourceSHA256': row['sourceSHA256'],
                                       'sheets': [r[1] for r in recovered], 'publication': False,
                                       'modelGeometryChanges': 0, 'scriptExternalAICalls': 0})
    fresh = local / 'frozen-inputs'
    save(fresh / 'check-selection.json.gz', {**selected, 'rows': [row],
                                           'previousManifestSHA256': selected['manifestSHA256'],
                                           'manifestSHA256': digest((ROOT / '3d-viewer/city/data/manifest.json').read_bytes())})
    save(fresh / 'context.json.gz', {'rows': [context]})
    resolution = module('pending_original_contact', 'xl-pending-cell-contact-resolution.py')
    resolution.BATCH = args.batch; resolution.BASE = fresh; resolution.DOC = doc; resolution.LOCAL = local
    resolution.UIDS = [args.uid]
    resolution.SOURCE = next(folder for folder, proof in recovered if proof['sheet'] == routing['primarySheet'])
    resolution.ADJACENT_SOURCES = [folder for folder, proof in recovered if proof['sheet'] != routing['primarySheet']]
    try:
        resolution.owned()
    except AssertionError as error:
        save(doc / 'guard-failure.json', {'error': str(error), 'traceback': traceback.format_exc(), 'publication': False, 'modelGeometryChanges': 0})
        finish(args, row, doc, local, ['terrain-construction-guard:' + str(error)])
        return
    metrics = read(doc / 'metrics.json')
    for path, pinned in metrics['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == pinned
    policy = module('indexed_existing_acceptance', 'acceptance-policy.py')
    proof = routing['identity']['proof']
    save(doc / 'identity-proof.json', {'uid': args.uid, 'sourceSHA256': row['sourceSHA256'], 'proof': proof,
                                      'method': POLICY, 'ownedSourceProofSHA256': digest((doc / 'owned-source-identity.json').read_bytes()),
                                      'preflightSHA256': digest((doc / 'indexed-preflight.json').read_bytes())})
    reasons = policy.reasons({'state': 'runtime-validated-awaiting-acceptance',
                              'sourceSHA256': row['sourceSHA256'], 'identityProof': proof},
                             metrics['rows'][0], metrics['profiles']['mobile'])
    if not read(doc / 'foundation.json')['rows'][0]['strictFoundationAccepted']:
        reasons.append('whole-source-foundation')
    reasons.extend(read(doc / 'validation.json')['results'][0].get('concerns', []))
    native = read(doc / 'native-neighbour-checks.json')
    resolved = set(native['resolved'])
    reasons.extend('native-neighbour-regression:' + uid for uid in set(native['blocked']) - resolved)
    reasons.extend('terrain-regresses-neighbour:' + r['uid'] for r in read(doc / 'neighbour-checks.json')['rows'] if r['reasons'] and r['uid'] not in resolved)
    finish(args, row, doc, local, reasons)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--uid', required=True)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--base', default='docs/astra-city/government-import/government-xl-next-100-20261005')
    parser.add_argument('--owned', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and Path(args.batch).name == args.batch
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    local = HERE / 'local' / args.batch
    if args.owned:
        owned(args, doc, local)
        return
    assert not doc.exists(), 'Use a fresh explicit continuation batch; never overwrite completed evidence'
    claim = reservations.claim('codex-xl-owned-indexed-terrain-' + str(uuid.uuid4()),
                               ['building:' + args.uid, 'terrain-patch:' + args.uid], batch=args.batch)
    assert claim['ok'], claim
    save(local / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run',
                    '--lease-file', str(local / 'reservation.json'), '--', sys.executable, __file__,
                    '--uid', args.uid, '--batch', args.batch, '--base', args.base, '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
