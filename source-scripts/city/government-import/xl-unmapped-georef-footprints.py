"""Fetch exact GeoRef footprint candidates for XL sources without viewer identities.

No geometry editing, identity acceptance, UID reassignment or publication. Current
official OBJECTIDs are retained separately from historical viewer OBJECTIDs.
"""
import argparse
import json
from pathlib import Path
import re
import sys
import urllib.parse
import uuid

from run import ROOT, HERE, read, save, digest, connect, reservations, jobs, Jsonb, dict_row, NATIVE_RUN
sys.path.insert(0, str(HERE.parent / 'citywide-source'))
from discover import ac
sys.path.insert(0, str(HERE.parent / 'landsd-territory'))
from source import BASE


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count', required=True)
    parser.add_argument('--batch', required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and Path(args.batch).name == args.batch
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    local = HERE / 'local' / args.batch
    assert not doc.exists() and not local.exists(), 'Fresh immutable evidence required'
    count_path = ROOT / args.count
    count = read(count_path)
    assert count['nativeRun'] == NATIVE_RUN
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest_path.read_bytes()) == count['manifestSHA256']
    rows = [r for r in count['rows'] if not r['installedVerified'] and r['uid'] is None]
    assert 1 <= len(rows) <= 25
    keys = sorted({r['sourceKey'].split('/')[0] for r in rows})
    georefs = sorted({r['sourceKey'].split('/')[1][1:11] for r in rows})
    assert all(re.fullmatch(r'[0-9]{10}', r) for r in georefs)
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        native = {key: (sha, data) for key, sha, data in con.execute(
            'SELECT r.cache_key,r.result_sha,r.result FROM astra_modelling.native_stage_results r '
            'JOIN astra_modelling.native_stage_members m USING(cache_key) '
            'WHERE m.run_id=%s AND r.cache_key=ANY(%s)', (NATIVE_RUN, keys)).fetchall()}
    assert set(native) == set(keys)
    original = {}
    for row in rows:
        key, model_id = row['sourceKey'].split('/')
        sha, data = native[key]
        models = [m for m in data['models'] if m['modelId'] == model_id]
        assert len(models) == 1 and models[0]['asset']['sha256'] == row['indexedSourceSHA256']
        original[row['sourceKey']] = {'nativeResultSHA256': sha, 'model': models[0]}
    claim = reservations.claim('codex-xl-unmapped-georef-' + str(uuid.uuid4()),
        ['native-model:' + r['sourceKey'] for r in rows], batch=args.batch)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        save(local / 'reservation.json', json.loads(json.dumps(lease, default=str)))
        params = {'f': 'json', 'where': 'GeoRefNo IN (' + ','.join("'" + r + "'" for r in georefs) + ')',
                  'outFields': '*', 'returnGeometry': 'true', 'outSR': 2326,
                  'returnTrueCurves': 'false', 'resultRecordCount': 1000, 'orderByFields': 'OBJECTID'}
        network = ac.Network(local / 'transfer.json', cap=6_000_000)
        raw, headers = network.get(BASE + '/0/query?' + urllib.parse.urlencode(params), 5_000_000)
        data = json.loads(raw)
        assert not data.get('error') and not data.get('exceededTransferLimit')
        features = data['features']
        assert len({f['attributes']['OBJECTID'] for f in features}) == len(features)
        assert {str(f['attributes']['GeoRefNo']) for f in features}.issubset(set(georefs))
        doc.mkdir(parents=True)
        (doc / 'official-query.json').write_bytes(raw)
        save(doc / 'official-query-receipt.json', {'parameters': params, 'headers': headers,
            'rawSHA256': digest(raw), 'checkedAt': ac.now(), 'completeRequestedGeoRefs': True})
        # Search the entire viewer by stable CSUID/GeoRef, never current OBJECTID.
        forms, refs = [], [ref(count_path), ref(manifest_path), ref(Path(__file__))]
        for tile in read(manifest_path)['tiles']:
            path = ROOT / '3d-viewer' / tile['url']
            matches = [b for b in read(path)['buildings'] if str(b.get('buildingCSUID', ''))[:10] in georefs]
            if matches:
                refs.append(ref(path))
                forms.extend({'building': b, 'tile': tile['url']} for b in matches)
        outcomes = []
        for row in rows:
            model_id = row['sourceKey'].split('/')[1]
            geo = model_id[1:11]
            expected_type = {'01': 'Tower', '02': 'Podium'}[model_id[11:13]]
            official = [f for f in features if str(f['attributes']['GeoRefNo']) == geo]
            candidates = []
            for feature in official:
                attrs = feature['attributes']
                csuid = attrs['BuildingCSUID']
                stable_matches = [f for f in forms if f['building']['buildingCSUID'] == csuid]
                candidates.append({'officialAttributes': attrs, 'geometry': feature.get('geometry'),
                    'sourceTypeMatches': attrs['BuildingBlockType'] == expected_type,
                    'currentViewerStableCSUIDMatches': stable_matches})
            outcomes.append({**row, 'modelId': model_id, 'geoRefNo': geo,
                'expectedStructureType': expected_type, 'officialCandidates': candidates,
                'currentViewerGeoRefMatches': [f for f in forms if f['building']['buildingCSUID'][:10] == geo],
                'original': original[row['sourceKey']], 'identityAccepted': False,
                'installationApproved': False,
                'nextStep': 'Exact type-qualified metadata joins may route full original identity and physical checks; a GeoRef or type match alone does not approve an installation.'})
        save(doc / 'routing.json.gz', {'rows': outcomes})
        refs += [ref(doc / 'official-query.json'), ref(doc / 'official-query-receipt.json'),
                 ref(doc / 'routing.json.gz'), ref(local / 'transfer.json'),
                 ref(HERE.parent / 'citywide-source/discover.py'), ref(HERE.parent / 'landmark-acquisition/acquire.py')]
        payload = {'sourceKeys': [r['sourceKey'] for r in rows], 'evidenceRefs': refs}
        stage = 'unmapped-xl-live-exact-georef-footprint-candidates-v1'
        jid = jobs.enqueue(args.batch, stage, payload)
        job = jobs.claim(args.batch, lease['owner'], [stage], lease_seconds=1800)
        assert job and job['id'] == jid
        summary = [{'sourceKey': r['sourceKey'], 'officialCandidates': len(r['officialCandidates']),
            'typeQualifiedCandidates': sum(f['sourceTypeMatches'] for f in r['officialCandidates']),
            'viewerGeoRefMatches': len(r['currentViewerGeoRefMatches'])} for r in outcomes]
        result = {**payload, 'jobId': jid, 'batch': args.batch, 'rows': summary,
            'sources': len(rows), 'officialObjects': len(features), 'fullXLCounts': count['counts'],
            'newlyInstalled': 0, 'publication': False, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
            'qualification': 'Exact live GeoRef query and current stable-CSUID metadata joins only. No invented UID, source pose/geometry edits, identity acceptance, physical proof or installation credit.'}
        with connect() as con:
            con.row_factory = dict_row
            con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            assert reservations._current(con, lease)
            for item in refs:
                assert ref(ROOT / item['path']) == item
            for key, (sha, _) in native.items():
                assert con.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s', (key,)).fetchone()['result_sha'] == sha
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
                (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', result)
        save(doc / 'result.json', result)
        save(doc / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
        print(json.dumps(result), flush=True)
    finally:
        reservations.release(lease)


if __name__ == '__main__':
    main()
