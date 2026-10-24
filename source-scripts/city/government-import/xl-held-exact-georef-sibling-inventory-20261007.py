"""Bounded exact-identity component lookup in the pinned original inventory.

An indexed sibling is a lookup candidate only. Current directory acquisition,
original byte/pose/identity, support, physical and browser gates stay mandatory.
"""
import json
import uuid
from pathlib import Path
from run import ROOT, read, save, digest, connect, NATIVE_RUN, reservations, jobs, Jsonb, dict_row

BATCH = 'government-xl-held-exact-georef-sibling-inventory-20261007'
BASE = ROOT / 'docs/astra-city/government-import'

def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}

def main():
    doc = BASE / BATCH
    assert not doc.exists()
    selection_path = BASE / 'government-xl-remaining-20260923/selection.json.gz'
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = read(manifest_path)
    refs = [ref(Path(__file__)), ref(selection_path), ref(manifest_path)]
    installed = set()
    for url in manifest['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        refs.append(ref(path))
        installed.update(r['uid'] for r in read(path)['models'])
    rows = [r for r in read(selection_path)['rows'] if r['uid'] not in installed]
    assert len(rows) == 261
    prefixes = sorted({r['source']['building']['buildingCSUID'][:10] for r in rows})
    stages = {}
    matches = {}
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        profiles = con.execute('SELECT DISTINCT cache_key,sheet,model_id FROM astra_modelling.native_model_sizes WHERE run_id=%s AND substring(model_id FROM 2 FOR 10)=ANY(%s) ORDER BY cache_key,sheet,model_id', (NATIVE_RUN, prefixes)).fetchall()
        assert len(profiles) <= 5000
        by_cache = {}
        for key, sheet, model_id in profiles:
            by_cache.setdefault(key, []).append((sheet, model_id))
        for key, values in by_cache.items():
            pinned = con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, key)).fetchone()
            assert pinned
            stages[key] = pinned[0]
            model_ids = [mid for _, mid in values]
            data = con.execute("SELECT model->>'modelId',model->'matching'->'officialCandidates',model->'asset'->>'sha256' FROM astra_modelling.native_stage_results, jsonb_array_elements(result->'models') model WHERE cache_key=%s AND model->>'modelId'=ANY(%s)", (key, model_ids)).fetchall()
            assert {mid for mid, _, _ in data} == set(model_ids)
            sheets = {mid: sheet for sheet, mid in values}
            for mid, candidates, sha in data:
                matches.setdefault(mid[1:11], []).append({'cacheKey': key, 'sheet': sheets[mid], 'modelId': mid, 'sourceSHA256': sha, 'stageResultSHA256': pinned[0], 'officialCandidates': candidates})
    out = []
    for row in rows:
        form = row['source']['building']
        family = matches.get(form['buildingCSUID'][:10], [])
        exact = [m for m in family if any(c.get('objectId') == form['objectId'] and c.get('buildingCSUID') == form['buildingCSUID'] for c in m['officialCandidates'])]
        siblings = [m for m in exact if m['modelId'] != row['modelId']]
        out.append({'uid': row['uid'], 'name': row['name'], 'objectId': form['objectId'], 'buildingCSUID': form['buildingCSUID'],
                    'frozenModelId': row['modelId'], 'frozenSourceSHA256': row['sourceSHA256'],
                    'sameGeoRefInventory': family, 'exactObjectAndCSUIDSiblingCandidates': siblings,
                    'primaryPresentInPinnedInventory': any(m['modelId'] == row['modelId'] for m in exact)})
    save(doc / 'lookup.json', {'rows': out, 'nativeRun': NATIVE_RUN, 'profiles': len(profiles), 'inventoryOnly': True,
                             'qualification': 'Pinned historical original inventory lookup. Same GeoRef alone does not identify a support. Exact ObjectID/CSUID candidates still require fresh current original directory and all existing acceptance checks. No ready, skip or installation credit.'})
    refs.append(ref(doc / 'lookup.json'))
    claim = reservations.claim('codex-xl-exact-components-' + str(uuid.uuid4()), ['building:' + r['uid'] for r in rows], batch=BATCH)
    assert claim['ok']
    lease = claim['reservation']
    try:
        payload = {'uids': sorted(r['uid'] for r in rows), 'evidenceRefs': refs, 'nativeRun': NATIVE_RUN, 'stageResultHashes': stages}
        stage = 'exact-original-georef-sibling-inventory-v1'
        jid = jobs.enqueue(BATCH, stage, payload)
        job = jobs.claim(BATCH, lease['owner'], [stage], lease_seconds=1800)
        assert job and job['id'] == jid
        candidates = [r['uid'] for r in out if r['exactObjectAndCSUIDSiblingCandidates']]
        result = {**payload, 'batch': BATCH, 'jobId': jid, 'modelsChecked': len(out), 'exactSiblingCandidateUids': candidates,
                  'newlyInstalled': 0, 'publication': False, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
                  'activeWorkers': 0, 'queuedFollowups': 0, 'inventoryOnly': True}
        with connect() as con:
            con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            for key, sha in stages.items():
                assert con.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s', (key,)).fetchone() == (sha,)
            for evidence in refs:
                assert ref(ROOT / evidence['path']) == evidence
            con.row_factory = dict_row
            assert reservations._current(con, lease)
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', result)
        save(doc / 'result.json', result)
        save(doc / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
        print(json.dumps({'jobId': jid, 'modelsChecked': len(out), 'profiles': len(profiles), 'exactSiblingCandidateUids': candidates}), flush=True)
    finally:
        reservations.release(lease)

if __name__ == '__main__':
    main()
