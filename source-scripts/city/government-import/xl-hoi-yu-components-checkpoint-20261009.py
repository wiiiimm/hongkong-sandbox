"""Bind complete unchanged source component census and corrected capture."""
import json
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect, jobs, Jsonb, dict_row

BATCH = 'government-xl-hoi-yu-source-components-20261009'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH

def ref(p):
    return {'path': str(p.relative_to(ROOT)), 'sha256': digest(p.read_bytes())}

def main():
    assert not (DOC / 'result.json').exists()
    census = read(DOC / 'components.json.gz')
    render = read(DOC / 'corrected-capture/render.json')
    assert census['completeFaceAccounting'] and census['sourceTriangles'] == 8775
    assert len(census['components']) == 32
    indices = [i for c in census['components'] for i in c['originalSourceFaces']]
    assert sorted(indices) == list(range(8775))
    assert len(render['views']) == 1 and not render['errors']
    view = render['views'][0]
    assert view['uid'] == census['uid'] and view['sourceSHA256'] == census['sourceSHA256']
    refs = [ref(DOC / p) for p in ['components.json.gz', 'inputs.json', 'corrected-capture/render.json']]
    refs += [ref(HERE / p) for p in ['xl-hoi-yu-source-components-20261009.py', Path(__file__).name]]
    refs += [{'path': p, 'sha256': h} for p, h in render['inputHashes'].items()]
    refs += [view['image']]
    refs = list({r['path']: r for r in refs}.values())
    claim = reservations.claim('hoi-yu-components-checkpoint-' + str(uuid.uuid4()),
        ['building:landsd/177604:0', 'building:landsd/177605:0'], batch=BATCH, ttl=1800)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        stage = 'complete-original-components-corrected-source-capture-v1'
        payload = {'uids': ['landsd/177604:0', 'landsd/177605:0'], 'evidenceRefs': refs}
        jid = jobs.enqueue(BATCH, stage, payload)
        job = jobs.claim(BATCH, lease['owner'], [stage], lease_seconds=1800)
        assert job and job['id'] == jid
        result = {**payload, 'jobId': jid, 'batch': BATCH, 'stage': stage,
            'componentCount': 32, 'sourceTriangles': 8775, 'components': census['components'],
            'newlyInstalled': 0, 'publication': False, 'installationApproved': False,
            'modelGeometryChanges': 0, 'aiGeometryModelling': False,
            'qualification': 'Complete original face membership and inspected correctly labelled capture. Lowest points belong to two thin full-height open components; this is not structural classification or footing approval. Original eight interface failures are preserved. Fresh full identity, support, terrain, neighbours and runtime checks remain required. Initial capture used unrelated hardcoded labels and is retained solely as an unapproved historical diagnostic.'}
        with connect() as c:
            c.row_factory = dict_row
            c.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            assert reservations._current(c, lease)
            for item in refs:
                assert ref(ROOT / item['path']) == item
            assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', result)
        save(DOC / 'result.json', result)
        save(DOC / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
        print(json.dumps({'jobId': jid, 'neonVerified': True, 'components': 32, 'newlyInstalled': 0}), flush=True)
    finally:
        assert reservations.release(lease)['ok']

if __name__ == '__main__':
    main()
