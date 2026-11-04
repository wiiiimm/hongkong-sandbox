"""Check current held XL archive headers; fetch no directory or model bodies.

ETag equality only permits reusing a prior source-directory receipt. It provides
no model acceptance, skip or installation credit. A changed ETag needs a fresh
directory audit and separate acquisition/validation.
"""
import argparse
import importlib.util
import json
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from run import ROOT, read, save, digest, connect, reservations, jobs, Jsonb, dict_row

DIR = ROOT / 'source-scripts/city/government-import'
BASE = ROOT / 'docs/astra-city/government-import'

def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--previous', required=True)
    args = parser.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    previous = (ROOT / args.previous).resolve()
    assert previous.is_relative_to(BASE)
    doc, local = BASE / args.batch, DIR / 'local' / args.batch
    assert not doc.exists(), 'Fresh external-state check; reuse completed receipts'
    prior = read(previous / 'result.json')
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (prior['jobId'],)).fetchone() == ('complete', prior)
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    selection_path = BASE / 'government-xl-remaining-20260923/selection.json.gz'
    manifest = read(manifest_path)
    catalogues = [ROOT / '3d-viewer' / url for url in manifest['officialModelCatalogues']]
    installed = {r['uid'] for path in catalogues for r in read(path)['models']}
    held = [r for r in read(selection_path)['rows'] if r['uid'] not in installed]
    assert held
    sheets = sorted({r['native']['sheet'] for r in held})
    receipts = {}
    for evidence in prior['evidenceRefs']:
        path = ROOT / evidence['path']
        if path.name == 'result.json' and path.parent.name == 'directory':
            assert ref(path) == evidence
            receipt = read(path)
            receipts[receipt['sheet']] = (path, receipt)
    assert set(sheets).issubset(receipts)
    refs = [ref(Path(__file__)), ref(previous / 'result.json'), ref(manifest_path),
            ref(selection_path), *[ref(path) for path in catalogues],
            *[ref(receipts[sheet][0]) for sheet in sheets]]
    acquisition_path = DIR.parent / 'landmark-acquisition/acquire.py'
    spec = importlib.util.spec_from_file_location('xl_headers_acquisition', acquisition_path)
    acquisition = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(acquisition)
    refs.append(ref(acquisition_path))
    network = acquisition.Network(local / 'transfer.json', cap=0)
    def check(sheet):
        _, previous_receipt = receipts[sheet]
        try:
            _, headers = network.get(previous_receipt['sourceURL'], 0, method='HEAD')
            etag = headers.get('ETag')
            size = int(headers['Content-Length'])
            assert etag and size > 0
            same = etag == previous_receipt['etag'] and size == previous_receipt['archiveBytes']
            return {'sheet': sheet, 'sourceURL': previous_receipt['sourceURL'],
                    'previousETag': previous_receipt['etag'], 'currentETag': etag,
                    'previousArchiveBytes': previous_receipt['archiveBytes'], 'currentArchiveBytes': size,
                    'headers': headers, 'status': 'unchanged-header' if same else 'changed-header',
                    'currentDirectoryVerified': False, 'installationApproved': False}
        except Exception as error:
            return {'sheet': sheet, 'status': 'header-unavailable', 'error': str(error)[:300],
                    'currentDirectoryVerified': False, 'installationApproved': False}
    rows = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        pending = {pool.submit(check, sheet): sheet for sheet in sheets}
        for future in as_completed(pending):
            rows.append(future.result())
            if len(rows) % 20 == 0 or len(rows) == len(sheets):
                print(json.dumps({'checkedSheets': len(rows), 'totalSheets': len(sheets)}), flush=True)
    rows.sort(key=lambda row: row['sheet'])
    assert network.data['receivedBytes'] == network.data['chargedBytes'] == 0
    save(doc / 'headers.json', {'rows': rows, 'heldUids': sorted(r['uid'] for r in held),
                               'checkedAt': acquisition.now(), 'receivedBodyBytes': 0})
    refs.extend([ref(doc / 'headers.json'), ref(local / 'transfer.json')])
    for evidence in refs:
        assert ref(ROOT / evidence['path']) == evidence
    claim = reservations.claim('codex-xl-source-headers-' + str(uuid.uuid4()),
                               ['building:' + r['uid'] for r in held], batch=args.batch)
    assert claim['ok']
    lease = claim['reservation']
    try:
        payload = {'uids': sorted(r['uid'] for r in held), 'evidenceRefs': refs}
        stage = 'held-xl-original-source-header-recheck-v1'
        jid = jobs.enqueue(args.batch, stage, payload)
        job = jobs.claim(args.batch, lease['owner'], [stage], lease_seconds=1800)
        assert job and job['id'] == jid
        counts = {status: sum(r['status'] == status for r in rows)
                  for status in ['unchanged-header', 'changed-header', 'header-unavailable']}
        result = {**payload, 'batch': args.batch, 'jobId': jid, 'counts': counts,
                  'changedSheets': [r['sheet'] for r in rows if r['status'] == 'changed-header'],
                  'modelsChecked': len(held), 'sheetsChecked': len(sheets), 'receivedBodyBytes': 0,
                  'newlyInstalled': 0, 'publication': False, 'modelGeometryChanges': 0,
                  'scriptExternalAICalls': 0, 'activeWorkers': 0, 'queuedFollowups': 0,
                  'qualification': 'Live official archive headers only. Matching ETag and length allow reuse of the pinned source-directory receipt, not model acceptance. Changes require fresh directory and original-source validation. Failed requests provide no unchanged-source proof.'}
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
        print(json.dumps({'jobId': jid, 'counts': counts, 'modelsChecked': len(held)}), flush=True)
    finally:
        reservations.release(lease)

if __name__ == '__main__':
    main()
