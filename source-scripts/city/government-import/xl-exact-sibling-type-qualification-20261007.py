"""Check hard government model/form type identity before downloading siblings."""
import uuid
from pathlib import Path
from run import ROOT, read, save, digest, connect, reservations, jobs, Jsonb, dict_row
from government_georef_cell_identity import geographic_cell

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-exact-sibling-type-qualification-20261007'

def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}

def main():
    doc = BASE / BATCH
    assert not doc.exists()
    previous = BASE / 'government-xl-held-exact-georef-sibling-inventory-20261007'
    prior = read(previous / 'result.json')
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (prior['jobId'],)).fetchone() == ('complete', prior)
    for evidence in prior['evidenceRefs']:
        assert ref(ROOT / evidence['path']) == evidence
    selected = {r['uid']: r for r in read(BASE / 'government-xl-remaining-20260923/selection.json.gz')['rows']}
    rows = []
    refs = [ref(Path(__file__)), ref(Path(__file__).with_name('government_georef_cell_identity.py')),
            ref(previous / 'result.json'), ref(previous / 'lookup.json')]
    for entry in read(previous / 'lookup.json')['rows']:
        if not entry['exactObjectAndCSUIDSiblingCandidates']:
            continue
        row = selected[entry['uid']]
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert digest(tile.read_bytes()) == row['source']['tileSHA256']
        refs.append(ref(tile))
        current = next(f for f in read(tile)['buildings'] if f['uid'] == row['uid'])
        for sibling in entry['exactObjectAndCSUIDSiblingCandidates']:
            reasons = []
            try:
                geographic_cell(sibling['modelId'], current['buildingCSUID'], current['structureType'])
            except ValueError as error:
                reasons.append('geographic-cell-proof:' + str(error))
            rows.append({'uid': row['uid'], 'modelId': sibling['modelId'], 'sourceSHA256': sibling['sourceSHA256'],
                         'buildingCSUID': current['buildingCSUID'], 'structureType': current['structureType'],
                         'hardTypeIdentityPassed': not reasons, 'reasons': reasons,
                         'originalAssetDownloaded': False, 'identityAccepted': False, 'installationApproved': False})
    assert rows
    claim = reservations.claim('codex-xl-sibling-type-' + str(uuid.uuid4()), ['building:' + u for u in sorted({r['uid'] for r in rows})], batch=BATCH)
    assert claim['ok']
    lease = claim['reservation']
    try:
        payload = {'uids': sorted({r['uid'] for r in rows}), 'evidenceRefs': refs}
        stage = 'exact-government-sibling-hard-type-qualification-v1'
        jid = jobs.enqueue(BATCH, stage, payload)
        job = jobs.claim(BATCH, lease['owner'], [stage], lease_seconds=1800)
        assert job and job['id'] == jid
        result = {**payload, 'jobId': jid, 'batch': BATCH, 'rows': rows, 'newlyInstalled': 0,
                  'publication': False, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
                  'activeWorkers': 0, 'queuedFollowups': 0,
                  'qualification': 'Hard model/form type identity only. No asset acquisition, geometry, form classification or acceptance changes. Passing this metadata check alone could not establish full identity or installation.'}
        with connect() as con:
            con.row_factory = dict_row
            con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            assert reservations._current(con, lease)
            for evidence in refs:
                assert ref(ROOT / evidence['path']) == evidence
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', result)
        save(doc / 'result.json', result)
        save(doc / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
        print({'jobId': jid, 'rows': rows}, flush=True)
    finally:
        reservations.release(lease)

if __name__ == '__main__':
    main()
