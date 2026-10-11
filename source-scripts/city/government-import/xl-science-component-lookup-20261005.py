"""Trace Science Museum's remaining exact source component in containing sheets."""
import json
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row, NATIVE_RUN
from terrain_source_preflight import SourceSheetIndex
sys.path.insert(0, str(HERE.parent / 'enhancement-screening'))
from shape_prepare import scan

BATCH = 'government-xl-science-component-lookup-20261005'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH
PREVIOUS = ROOT / 'docs/astra-city/government-import/government-xl-science-museum-disjoint-parent-20261005'
UID = 'landsd/83471:0'


def run():
    assert not DOC.exists(), 'Reuse completed exact source lookup'
    claim = reservations.claim('codex-xl-science-source-' + str(uuid.uuid4()), ['building:' + UID], batch=BATCH)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        inputs = read(PREVIOUS / 'neighbour-inputs.json.gz')
        assert read(PREVIOUS / 'result.json')['reasons'] == ['terrain-regresses-neighbour:' + UID]
        for path, sha in inputs['inputHashes'].items(): assert digest((ROOT / path).read_bytes()) == sha
        b = next(r['building'] for r in inputs['rows'] if r['building']['uid'] == UID)
        coordinates = [p for ring in b['rings'] for p in ring]
        bounds = [[min(p[0] for p in coordinates), b['base'], min(p[1] for p in coordinates)],
                  [max(p[0] for p in coordinates), b['base'] + b['height'], max(p[1] for p in coordinates)]]
        index_path = ROOT / 'source-scripts/city/landmark-acquisition/index.json'
        indexed = SourceSheetIndex(read(index_path)).covering_sheets(bounds)
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            profiles = con.execute('SELECT cache_key,model_id,sheet,source_state,viewer_uid,source_hold_reason FROM astra_modelling.native_model_sizes WHERE run_id=%s AND model_id LIKE %s', (NATIVE_RUN, 'B' + b['buildingCSUID'][:10] + '%')).fetchall()
            fingerprint = con.execute('SELECT source_digest FROM astra_modelling.native_model_size_runs WHERE run_id=%s', (NATIVE_RUN,)).fetchone()[0]
            pinned = dict(con.execute("SELECT DISTINCT ON(sheet) sheet,result-'models' FROM astra_modelling.city_source_directories WHERE sheet=ANY(%s) ORDER BY sheet,created_at DESC", ([s['sheet'] for s in indexed],)))
        rows = []
        for hit in indexed:
            sheet = hit['sheet']; metadata = pinned[sheet]; folder = LOCAL / 'sheets' / sheet
            directory, _ = scan({'SHEETNO': sheet, 'Format_glTF': metadata['sourceURL'],
                                 'REVISIONDATE': metadata['revision']}, folder / 'directory')
            matches = [m for m in directory['models'] if m['modelId'][1:11] == b['buildingCSUID'][:10]]
            rows.append({'sheet': sheet, 'intersectionM2': hit['intersectionM2'],
                         'completeDirectoryEntries': directory['completeEntries'], 'modelEntries': len(directory['models']),
                         'matchingGeoRefEntries': matches, 'directorySHA256': directory['directorySHA256'],
                         'revision': directory['revision'], 'sourceETag': directory['etag'],
                         'directoryChanged': directory['directorySHA256'] != metadata['directorySHA256'],
                         'sourceCachePath': str(folder.relative_to(ROOT))})
            assert reservations.owns(lease)
        inputs_sha = {str((PREVIOUS / name).relative_to(ROOT)): digest((PREVIOUS / name).read_bytes())
                      for name in ['result.json', 'neighbour-inputs.json.gz', 'parent-preservation.json']}
        inputs_sha[str(index_path.relative_to(ROOT))] = digest(index_path.read_bytes())
        payload = {'uid': UID, 'objectId': b['objectId'], 'buildingCSUID': b['buildingCSUID'],
                   'worldBounds': bounds, 'sourceIndexDigest': fingerprint, 'inputHashes': inputs_sha,
                   'runnerSHA256': digest(Path(__file__).read_bytes())}
        stage = 'exact-science-component-directory-lookup-v1'; jobid = jobs.enqueue(BATCH, stage, payload)
        job = jobs.claim(BATCH, lease['owner'], [stage], lease_seconds=1800); assert job and job['id'] == jobid
        result = {**payload, 'batch': BATCH, 'jobId': jobid, 'preparedIndexRecords': profiles,
                  'rows': rows, 'matchingDirectoryEntries': sum(len(r['matchingGeoRefEntries']) for r in rows),
                  'humanStatus': 'held-unknown', 'newlyInstalled': 0, 'requiresAI': False,
                  'requiresHumanDecision': False, 'activeWorkers': 0, 'queuedFollowups': 0,
                  'scriptExternalAICalls': 0, 'modelGeometryChanges': 0, 'publication': False,
                  'nextStep': 'Retain this basic source form. Investigate any further exact source/component coverage without guessing identities or suppressing it. Its overlap prevents disjoint parent preservation.',
                  'qualification': 'Lookup covers only exact GeoRef records and indexed containing government source directories. No nearby name assignment, architecture judgement, global source-absence claim or installation credit.'}
        with connect() as con:
            con.row_factory = dict_row; con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,)); assert reservations._current(con, lease)
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jobid, job['owner'], job['token'])).rowcount == 1
        # DB adapter emits tuple profiles; normalise them before exact JSON readback.
        expected = json.loads(json.dumps(result))
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY'); assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s', (jobid,)).fetchone()[0] == expected
        save(DOC / 'result.json', expected); save(DOC / 'neon-sync.json', {'jobId': jobid, 'resultVerified': True})
        print(json.dumps({'jobId': jobid, 'containingSheets': [r['sheet'] for r in rows], 'preparedIndexRecords': len(profiles), 'matchingDirectoryEntries': result['matchingDirectoryEntries'], 'neonVerified': True}), flush=True)
    finally: reservations.release(lease)


if __name__ == '__main__': run()
