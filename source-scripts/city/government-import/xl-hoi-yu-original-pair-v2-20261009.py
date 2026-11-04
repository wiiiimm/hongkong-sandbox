"""Recover exact Hoi Yu original and measure its Hoi Fu interface; no approval."""
import importlib.util
import json
import subprocess
import sys
import uuid
import zipfile
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, reservations, jobs, Jsonb, dict_row, NATIVE_RUN

BATCH = 'government-xl-hoi-yu-original-pair-v2-20261009'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH
UID = 'landsd/177605:0'
SUPPORT = 'landsd/177604:0'
PRIOR = ROOT / 'docs/astra-city/government-import/government-xl-direct-shared-osm-official-context-20261009/physical-selection.json.gz'


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    prior = read(PRIOR)
    historical_manifest = prior['manifestSHA256']
    current_manifest = digest(manifest.read_bytes())
    podium = next(r for r in prior['rows'] if r['uid'] == SUPPORT)
    inp = read(ROOT / 'docs/astra-city/government-import/government-xl-direct-osm-hoi-fu-native-parent-20261009-177604-0/neighbour-inputs.json.gz')
    b = next(r['building'] for r in inp['rows'] if r['building']['uid'] == UID)
    source = None
    current_podium = None
    for tile in read(manifest)['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        if tile.get('id') not in {b.get('tile'), podium['source']['building'].get('tile')}:
            continue
        actual_podium = [f for f in read(path)['buildings'] if f['uid'] == SUPPORT]
        if actual_podium:
            assert current_podium is None and len(actual_podium) == 1
            assert actual_podium[0] == podium['source']['building']
            assert digest(path.read_bytes()) == podium['source']['tileSHA256']
            current_podium = actual_podium[0]
        found = [f for f in read(path)['buildings'] if f['uid'] == UID]
        if found:
            assert source is None and len(found) == 1 and found[0] == b
            source = {'building': b, 'tile': tile['url'], 'tileSHA256': digest(path.read_bytes())}
    assert source and current_podium
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        pn = podium['native']
        assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, pn['cacheKey'])).fetchone() == (pn['resultSha'],)
        profiles = con.execute('SELECT DISTINCT cache_key,sheet FROM astra_modelling.native_model_sizes WHERE run_id=%s AND model_id LIKE %s',
                               (NATIVE_RUN, 'B' + b['buildingCSUID'][:10] + '%')).fetchall()
        matches = []
        for key, sheet in profiles:
            sha, data = con.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, key)).fetchone()
            for model in data['models']:
                if model['modelId'][1:11] == b['buildingCSUID'][:10] and any(v['objectId'] == b['objectId'] and v['buildingCSUID'] == b['buildingCSUID'] for v in model.get('matching', {}).get('officialCandidates', [])):
                    matches.append({'cacheKey': key, 'resultSha': sha, 'sheet': sheet, 'model': model})
        assert len(matches) == 1
    native = matches[0]
    helper = module('hoi_yu_exact_recovery', 'xl-next-support-recovery-20261005.py')
    entry, basis = helper.diagnostic_entry(native, b)
    tower = {'uid': UID, 'source': source, 'native': native, 'modelId': native['model']['modelId'],
             'sourceSHA256': native['model']['asset']['sha256'], 'candidate': {'entry': entry}, 'sourceLookupBasis': basis}
    sha = tower['sourceSHA256']
    cached = None
    for folder in [HERE / 'local', ROOT / '3d-viewer/city/data/official-models']:
        for path in folder.rglob(sha + '.glb.gz'):
            if digest(path.read_bytes()) == sha:
                cached = path
                break
        if cached:
            break
    if cached:
        raw = cached.read_bytes()
        recovery = {'method': 'verified-local-original', 'transferredBytes': 0}
    else:
        sheet = native['sheet']
        folder = LOCAL / 'sheets' / sheet
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            pinned = con.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1", (sheet,)).fetchone()[0]
        directory, _ = helper.scan({'SHEETNO': sheet, 'Format_glTF': pinned['sourceURL'], 'REVISIONDATE': pinned['revision']}, folder / 'directory')
        directory['models'] = [m for m in directory['models'] if m['modelId'] == tower['modelId']]
        assert len(directory['models']) == 1
        receipt = helper.acquire(directory, folder / 'directory/zip-directory.bin', folder / 'original')
        packed = folder / 'packed'
        packed.mkdir(exist_ok=True)
        with zipfile.ZipFile(folder / 'original' / (sheet + '.zip')) as archive:
            converted = helper._convert_one(archive, archive.getinfo(native['model']['sourceEntry']), folder / 'decoded', packed, {}, {'modelId': tower['modelId']})
            raw = helper.canonical_bytes((packed / converted['asset']['asset']).read_bytes(), sha)
        recovery = {'method': 'exact-original-government-recovery', 'transferredBytes': receipt['newThisInvocationBytes']}
    assert digest(raw) == sha and len(raw) == native['model']['asset']['bytes']
    destination = LOCAL / 'assets' / (sha + '.glb.gz')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)
    tower['candidate']['path'] = str(destination.relative_to(ROOT))
    tower['candidate']['entry']['asset'] = 'assets/' + destination.name
    assert digest((ROOT / podium['candidate']['path']).read_bytes()) == podium['sourceSHA256']
    sources = [podium, tower]
    save(DOC / 'selection.json.gz', {'rows': sources, 'manifestSHA256': digest(manifest.read_bytes()), 'nativeRun': NATIVE_RUN, 'historicalManifestSHA256': historical_manifest, 'currentTargetFormsRebound': True})
    save(DOC / 'recovery.json', {'uid': UID, 'sourceSHA256': sha, **recovery, 'modelGeometryChanges': 0})
    save(DOC / 'support-inputs.json', {'sources': sources, 'pairs': [{'uid': UID, 'supportUid': SUPPORT}]})
    runner = HERE / 'original-support-closure-interfaces-incremental.mjs'
    subprocess.run(['node', str(runner), str(DOC.relative_to(ROOT)) + '/'], cwd=ROOT, check=True)
    check = read(DOC / 'support-checks.json.gz')
    assert len(check['rows']) == 1
    refs = [ref(p) for p in sorted(DOC.iterdir()) if p.is_file()]
    refs += [ref(Path(__file__)), ref(HERE / 'xl-next-support-recovery-20261005.py'), ref(PRIOR), ref(manifest)]
    refs += [{'path': p, 'sha256': h} for p, h in check['inputHashes'].items()]
    refs += [ref(ROOT / source['tile']) if source['tile'].startswith('3d-viewer/') else ref(ROOT / '3d-viewer' / source['tile'])]
    refs = list({r['path']: r for r in refs}.values())
    assert digest(manifest.read_bytes()) == current_manifest
    payload = {'uids': [SUPPORT, UID], 'evidenceRefs': refs}
    stage = 'hoi-yu-current-form-original-source-interface-v2'
    jid = jobs.enqueue(BATCH, stage, payload)
    job = jobs.claim(BATCH, lease['owner'], [stage], lease_seconds=1800)
    assert job and job['id'] == jid
    result = {**payload, 'jobId': jid, 'batch': BATCH, 'rows': check['rows'], 'newlyInstalled': 0,
              'publication': False, 'installationApproved': False, 'modelGeometryChanges': 0,
              'aiGeometryModelling': False, 'qualification': 'Exact original tower/podium diagnostic only. Full identity, terrain, foundation, neighbour and browser checks remain required; raw interface failures are preserved.'}
    with connect() as con:
        con.row_factory = dict_row
        con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
        assert reservations._current(con, lease)
        for item in refs:
            assert ref(ROOT / item['path']) == item
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', result)
    save(DOC / 'result.json', result)
    save(DOC / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
    print(json.dumps({'jobId': jid, 'row': check['rows'][0]}, default=str)[:1800], flush=True)


def main():
    if '--owned' in sys.argv:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim = reservations.claim('codex-hoi-yu-pair-' + str(uuid.uuid4()), ['building:' + UID, 'building:' + SUPPORT], batch=BATCH)
    assert claim['ok'], claim
    save(LOCAL / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(LOCAL / 'reservation.json'), '--', sys.executable, __file__, '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
