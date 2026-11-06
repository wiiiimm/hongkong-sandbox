"""Acquire authentic Cheung Chau terrain for original-model contact follow-up.

Uses the existing bounded provider directory/member downloader, its transfer caps
and checksum checks. No source edits, publication or model acceptance.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import copy
import json
import shutil
import subprocess
import sys
import uuid
import zipfile
from islands_direct_stage import ROOT, HERE, read, save, sha, rel, module
from run import connect, reservations, jobs, dict_row, Jsonb

BATCH = 'government-islands-cheung-chau-source-terrain-20261106-v1'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH


def owned():
    receipt = read(LOCAL / 'reservation.json'); assert reservations.owns(receipt)
    plan = read(DOC / 'plan.json')
    helper = module('islands_cheung_existing_source', HERE / 'tai-o-exact-pass.py')
    sys.path.insert(0, str(HERE.parent / 'citywide-source'))
    from discover import scan
    def one(item):
        assert shutil.disk_usage(LOCAL).free >= 8 * 1024**3, 'Retain acquisition disk floor'
        folder = LOCAL / 'source-terrain' / item['sheet']
        try:
            with connect() as db:
                db.execute('SET TRANSACTION READ ONLY')
                metadata = db.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1", (item['sheet'],)).fetchone()[0]
            directory, _ = scan({'SHEETNO': item['sheet'], 'Format_glTF': metadata['sourceURL'],
                                 'REVISIONDATE': metadata['revision']}, folder / 'directory')
            directory['models'] = []
            record = helper.native_download.acquire(directory, folder / 'directory/zip-directory.bin', folder / 'original', include_terrain=True)
            members = []
            with zipfile.ZipFile(folder / 'original' / (item['sheet'] + '.zip')) as archive:
                names = [n for n in archive.namelist() if n.startswith('TERRAIN') and n.endswith(('.gltf', '.bin'))]
                assert names, 'No terrain geometry in captured archive; not government-wide absence'
                for name in names:
                    safe = Path(name); assert not safe.is_absolute() and '..' not in safe.parts
                    target = folder / 'decoded' / safe
                    assert not target.exists(); target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.read(name))
                    members.append({'path': rel(target), 'sha256': sha(target), 'bytes': target.stat().st_size})
            return {'sheet': item['sheet'], 'revisionDate': record['revisionDate'], 'sourceETag': record['sourceETag'],
                'directorySHA256': record['directorySHA256'], 'compactArchiveSHA256': record['sha256'],
                'compactArchiveBytes': record['bytes'], 'sourceArchiveBytes': record['sourceArchiveBytes'],
                'receivedBytes': record['receivedBytes'], 'newThisInvocationBytes': record['newThisInvocationBytes'],
                'members': members, 'directory': {'path': rel(folder / 'directory/result.json'), 'sha256': sha(folder / 'directory/result.json')}}
        except Exception as error:
            return {'sheet': item['sheet'], 'error': str(error), 'sourceCorruptionEstablished': False}
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = []
        for result in pool.map(one, plan['sheets']):
            outcomes.append(result); save(DOC / 'partial.json', {'rows': outcomes, 'publication': False})
            print({'terrainSheetsChecked': len(outcomes), 'total': len(plan['sheets']), 'sheet': result['sheet'], 'ok': 'error' not in result}, flush=True)
    assert reservations.owns(receipt)
    report = {'batch': BATCH, 'sheets': [r for r in outcomes if 'error' not in r],
        'errors': [r for r in outcomes if 'error' in r], 'modelGeometryChanges': 0, 'newlyInstalled': 0,
        'publication': False, 'aiCalls': 0, 'planSHA256': sha(DOC / 'plan.json')}
    save(DOC / 'source-terrain.json', report)
    payload = {'path': rel(DOC / 'source-terrain.json'), 'sha256': sha(DOC / 'source-terrain.json')}
    stage = 'islands-original-source-terrain-recovery-v1'
    jobid = jobs.enqueue(BATCH, stage, payload)
    job = jobs.claim(BATCH, receipt['owner'], [stage], lease_seconds=300); assert job and job['id'] == jobid
    result = {**report, 'evidence': payload, 'jobId': jobid}
    with connect() as db:
        db.row_factory = dict_row; db.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
        assert reservations._current(db, receipt)
        assert db.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jobid, job['owner'], job['token'])).rowcount == 1
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s', (jobid,)).fetchone()[0] == result
    save(DOC / 'neon-sync.json', {'jobId': jobid, 'exactResultMatch': True, 'publication': False})
    print({'complete': True, 'terrainSheets': len(report['sheets']), 'errors': len(report['errors']), 'jobId': jobid}, flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--owned', action='store_true'); a = p.parse_args()
    if a.owned: return owned()
    assert not DOC.exists() and not LOCAL.exists()
    index_path = ROOT / 'docs/astra-city/government-import/government-islands-cheung-chau-resume-20261106-v2/recovered-assets.json'
    recovered = read(index_path); assets = recovered['assets']
    rows, pins, missing = [], {rel(index_path): sha(index_path)}, []
    for i in range(4):
        source = ROOT / f'docs/astra-city/government-import/government-islands-cheung-chau-resume-20261106-v2-check-{i}/check-selection.json.gz'
        pins[rel(source)] = sha(source)
        for row in read(source)['rows']:
            digest = row['candidate']['entry']['sha256']
            path = assets.get(digest)
            if path:
                assert sha(ROOT / path) == digest
                row = copy.deepcopy(row); row['candidate']['path'] = path; rows.append(row)
            else: missing.append(row['uid'])
    assert len(rows) == 3403 and not missing
    missing = recovered['missingUids']
    assert len(missing)==17 and len({r['uid'] for r in rows}.union(missing))==3420
    sheets = sorted({r['native']['sheet'] for r in rows})
    assert 0 < len(sheets) <= 49
    save(DOC / 'check-selection.json.gz', {'rows': rows, 'missingUids': missing, 'inputHashes': pins,
         'manifestSHA256': sha(ROOT / '3d-viewer/city/data/manifest.json'), 'publication': False})
    save(DOC / 'plan.json', {'sheets': [{'sheet': s} for s in sheets], 'sourceSelectionSHA256': sha(DOC / 'check-selection.json.gz'),
         'inputHashes': pins, 'sourceGeometryChanges': 0, 'publication': False, 'workers': 2})
    resources = ['source-terrain:' + s for s in sheets]
    claim = reservations.claim('codex-islands-cheung-terrain-' + str(uuid.uuid4()), resources, batch=BATCH, ttl=3600)
    assert claim['ok'], 'Existing owner; no takeover'
    receipt = json.loads(json.dumps(claim['reservation'], default=str)); save(LOCAL / 'reservation.json', receipt)
    try:
        subprocess.run([sys.executable, HERE.parent / 'shared-modelling/reservations.py', 'run', '--lease-file',
            LOCAL / 'reservation.json', '--ttl', '3600', '--', sys.executable, Path(__file__), '--owned'], cwd=ROOT, check=True)
    finally:
        if reservations.owns(receipt): reservations.release(receipt)


if __name__ == '__main__': main()
