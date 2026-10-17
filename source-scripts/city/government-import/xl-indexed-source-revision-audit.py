"""Check previously unaudited indexed XL originals against live official directories.

This also covers source keys without a unique viewer UID. No UID is invented,
and directory CRC/length equality is routing evidence, not packed-byte proof.
Old native results, model reviews, assets and runtime files remain unchanged.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import re
import subprocess
import sys
import urllib.parse
import uuid

from run import ROOT, HERE, read, save, digest, connect, jobs, reservations, Jsonb, dict_row, NATIVE_RUN
sys.path.insert(0, str(HERE.parent / 'citywide-source'))
from discover import scan, ac


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def archive_identity(directory):
    return digest(json.dumps([directory['sourceURL'], directory['etag'],
                              directory['directorySHA256']], separators=(',', ':')).encode())


def classify(model_id, previous, current):
    matches = [m for m in current if m['modelId'][:-1] == model_id[:-1]]
    if len(matches) != 1:
        return {'status': 'missing-or-ambiguous', 'matches': len(matches)}
    latest = matches[0]
    members = lambda m: sorted((x['name'], x['crc32'], x['decodedBytes']) for x in m['members'])
    unchanged = latest['modelId'] == model_id and members(previous) == members(latest)
    return {'status': 'member-metadata-unchanged' if unchanged else 'changed-original-members',
            'currentModelId': latest['modelId'], 'memberMetadata': latest,
            'packedByteIdentityProven': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count', required=True)
    parser.add_argument('--previous-audit', required=True)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    assert 1 <= args.workers <= 4
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    count_path, previous_path = ROOT / args.count, ROOT / args.previous_audit
    count, previous = read(count_path), read(previous_path)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == count['manifestSHA256']
    assert count['nativeRun'] == NATIVE_RUN
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                           (previous['jobId'],)).fetchone() == ('complete', previous)
    # Prior audit is historical evidence; its manifest is intentionally not
    # rebound to the current manifest. Only identical source keys are reused.
    for item in previous['evidenceRefs']:
        assert ref(ROOT / item['path']) == item
    covered = {(r['uid'], r['previousSourceSHA256']) for r in previous['rows']}
    remaining = [r for r in count['rows'] if not r['installedVerified']]
    rows = [r for r in remaining if (r['uid'], r['indexedSourceSHA256']) not in covered]
    assert rows and len({r['sourceKey'] for r in rows}) == len(rows)
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    local = HERE / 'local' / args.batch
    lease_path = local / 'reservation.json'
    if not args.owned:
        assert not doc.exists() and not local.exists(), 'Fresh immutable audit required'
        # Unknown viewer identities receive no fabricated building reservation.
        # Those rows only read archive metadata; no model-specific writes occur.
        resources = ['building:' + uid for uid in sorted({r['uid'] for r in rows if r['uid']})]
        claim = reservations.claim('codex-xl-indexed-revision-' + str(uuid.uuid4()),
                                   resources, batch=args.batch)
        assert claim['ok'], claim
        save(lease_path, json.loads(json.dumps(claim['reservation'], default=str)))
        subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'),
                        'run', '--lease-file', str(lease_path), '--', sys.executable,
                        __file__, *sys.argv[1:], '--owned'], cwd=ROOT, check=True)
        return
    lease = read(lease_path)
    assert reservations.owns(lease)
    keys = sorted({r['sourceKey'].split('/')[0] for r in rows})
    with connect() as con:
        con.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        records = {key: (item, result_sha, result) for key, item, result_sha, result in con.execute(
            'SELECT i.cache_key,i.input_json,r.result_sha,r.result FROM astra_modelling.native_stage_inputs i '
            'JOIN astra_modelling.native_stage_results r USING(cache_key) '
            'JOIN astra_modelling.native_stage_members m USING(cache_key) '
            'WHERE m.run_id=%s AND i.cache_key=ANY(%s)', (NATIVE_RUN, keys)).fetchall()}
        assert set(records) == set(keys)
        sheets = sorted({item['sheet'] for item, _, _ in records.values()})
        directories = [d for (d,) in con.execute(
            'SELECT result FROM astra_modelling.city_source_directories WHERE sheet=ANY(%s)', (sheets,)).fetchall()]
    by_archive = {archive_identity(d): d for d in directories}
    originals = {}
    for row in rows:
        key, model_id = row['sourceKey'].split('/')
        item, result_sha, result = records[key]
        matches = [m for m in result['models'] if m['modelId'] == model_id]
        assert len(matches) == 1 and matches[0]['asset']['sha256'] == row['indexedSourceSHA256']
        old = by_archive[item['sourceSha256']]
        assert old['sheet'] == item['sheet']
        old_models = [m for m in old['models'] if m['modelId'] == model_id]
        assert len(old_models) == 1
        originals[row['sourceKey']] = {'sheet': item['sheet'], 'nativeResultSHA256': result_sha,
            'archiveSourceSHA256': item['sourceSha256'], 'model': old_models[0]}
    save(doc / 'audit-inputs.json.gz', {'count': ref(count_path), 'previousAudit': ref(previous_path),
        'manifestAtStart': ref(manifest), 'nativeRun': NATIVE_RUN, 'selected': rows,
        'priorAuditReusedSources': len(remaining) - len(rows), 'originals': originals,
        'nativeInputs': {k: v[0] for k, v in records.items()},
        'oldDirectories': {sha: by_archive[sha] for sha in {v[0]['sourceSha256'] for v in records.values()}},
        'runner': ref(Path(__file__))})
    # Refresh source URLs/revision dates from the official sheet index too.
    # No current OBJECTID is inferred from historical building OBJECTIDs.
    network = ac.Network(local / 'index-transfer.json', cap=16_000_000)
    attributes = {}
    for start in range(0, len(sheets), 25):
        chunk = sheets[start:start + 25]
        assert all(re.fullmatch(r'[0-9A-Za-z-]+', s) for s in chunk)
        params = {'f': 'json', 'where': 'SHEETNO IN (' + ','.join("'" + s + "'" for s in chunk) + ')',
            'outFields': 'OBJECTID,SHEETNO,REVISIONDATE,Format_glTF', 'returnGeometry': 'false',
            'orderByFields': 'OBJECTID', 'resultRecordCount': 1000}
        page = network.json(ac.SERVICE + '/query?' + urllib.parse.urlencode(params), 5_000_000)
        assert not page.get('exceededTransferLimit')
        found = [f['attributes'] for f in page['features']]
        assert len({v['SHEETNO'] for v in found}) == len(found)
        assert {v['SHEETNO'] for v in found} == set(chunk)
        attributes.update({v['SHEETNO']: v for v in found})
    save(doc / 'current-sheet-index.json', {'checkedAt': ac.now(), 'sheets': attributes,
        'completeRequestedSheets': True, 'requestedSheets': sheets})
    current, errors = {}, {}
    def inspect(sheet):
        return scan(attributes[sheet], local / 'sheets' / sheet / 'directory', refresh=True)[0]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending = {pool.submit(inspect, sheet): sheet for sheet in sheets}
        for future in as_completed(pending):
            assert reservations.owns(lease)
            sheet = pending[future]
            try:
                current[sheet] = future.result()
            except Exception as error:
                errors[sheet] = type(error).__name__ + ': ' + str(error)[:200]
            if (len(current) + len(errors)) % 5 == 0 or len(current) + len(errors) == len(sheets):
                print(json.dumps({'sheetsChecked': len(current) + len(errors),
                                  'sheets': len(sheets), 'errors': len(errors)}), flush=True)
    outcomes = []
    for row in rows:
        original = originals[row['sourceKey']]
        sheet = original['sheet']
        out = {**row, 'sheet': sheet, 'previousModelId': row['sourceKey'].split('/')[1],
               'nativeResultSHA256': original['nativeResultSHA256']}
        if sheet in errors:
            out.update(status='directory-unavailable', error=errors[sheet])
        else:
            fresh = current[sheet]
            out.update(classify(out['previousModelId'], original['model'], fresh['models']))
            out.update(currentDirectory=ref(local / 'sheets' / sheet / 'directory/result.json'),
                currentDirectorySHA256=fresh['directorySHA256'], currentETag=fresh['etag'],
                currentRevision=fresh['revision'])
        outcomes.append(out)
    save(doc / 'directory-audit.json', {'rows': outcomes, 'errors': errors})
    paths = [count_path, previous_path, manifest, Path(__file__), doc / 'audit-inputs.json.gz',
        doc / 'current-sheet-index.json', doc / 'directory-audit.json', local / 'index-transfer.json',
        HERE.parent / 'citywide-source/discover.py', HERE.parent / 'landmark-acquisition/acquire.py']
    paths += [local / 'sheets' / s / 'directory' / n for s in current
              for n in ['result.json', 'zip-directory.bin', 'transfer.json']]
    refs = [ref(p) for p in paths]
    assert digest(manifest.read_bytes()) == count['manifestSHA256']
    payload = {'sourceKeys': [r['sourceKey'] for r in rows], 'evidenceRefs': refs}
    stage = 'indexed-xl-previously-unaudited-live-original-directories-v1'
    jid = jobs.enqueue(args.batch, stage, payload)
    job = jobs.claim(args.batch, lease['owner'], [stage], lease_seconds=1800)
    assert job and job['id'] == jid
    result = {**payload, 'jobId': jid, 'batch': args.batch, 'rows': outcomes, 'errors': errors,
        'counts': dict(Counter(r['status'] for r in outcomes)), 'sheetsChecked': len(current),
        'priorAuditReusedSources': len(remaining) - len(rows), 'fullXLCounts': count['counts'],
        'newlyInstalled': 0, 'publication': False, 'downloadedModelPayloads': 0,
        'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
        'qualification': 'New live official directory metadata for previously unaudited exact indexed sources. Prior audit remains explicitly historical. CRC/length equality does not prove packed-byte identity; changed/missing/ambiguous sources need separate acquisition and complete acceptance. No invented viewer identities or installation credit.'}
    with connect() as con:
        con.row_factory = dict_row
        con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
        assert reservations._current(con, lease)
        for item in refs:
            assert ref(ROOT / item['path']) == item
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
            (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                           (jid,)).fetchone() == ('complete', result)
    save(doc / 'result.json', result)
    save(doc / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
    print(json.dumps({'jobId': jid, 'counts': result['counts'], 'newlyInstalled': 0}), flush=True)


if __name__ == '__main__':
    main()
