"""Audit all XL sources and file only source-bound unresolved import failures.

Never grants installation credit, edits geometry, or interprets AI intent.
Unproven rows stay open. A filed failure concerns the tested original source and
recorded validation contract, not permanent architectural impossibility.
"""
import argparse
from collections import Counter
from pathlib import Path
import uuid
from run import ROOT, read, save, digest, connect, NATIVE_RUN, reservations, jobs, Jsonb, dict_row

STAGE = 'xl-source-disposition-v1'
FIRST_PASS_ID = 'fe103e108561a902feb58a70aecc894844d48a3ab78f5dab20aff19ce93ba541'


def canonical_hash(value):
    return digest(jobs.encode(value).encode())


def reason_group(reasons):
    text = ' '.join(reasons).lower()
    if 'unique' in text or 'identity' in text or 'spatial' in text or 'unrelated' in text:
        return 'source-identity-or-component-coverage'
    if 'support' in text or 'interface' in text:
        return 'component-support'
    if 'neighbour' in text or 'neighbor' in text:
        return 'terrain-affects-neighbours'
    if 'budget' in text or 'runtime' in text:
        return 'runtime-budget'
    if 'terrain' in text or 'ground' in text or 'foundation' in text:
        return 'terrain-or-foundation'
    return 'other-validation-failure'


def audit(doc):
    pointer = read(ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json')
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = read(manifest_path)
    catalogues = [ROOT / '3d-viewer' / p for p in manifest['officialModelCatalogues']]
    installed = {m['uid']: (m, p) for p in catalogues for m in read(p)['models']}
    with connect() as con:
        con.row_factory = dict_row
        con.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        profiles = con.execute("SELECT * FROM astra_modelling.native_model_sizes WHERE run_id=%s AND size_group='xl' ORDER BY cache_key,model_id", (NATIVE_RUN,)).fetchall()
        keys = sorted({r['cache_key'] for r in profiles})
        native = con.execute("SELECT r.cache_key,r.result_sha,x FROM astra_modelling.native_stage_results r CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') x WHERE r.cache_key=ANY(%s) AND (x->>'triangles')::bigint>=10000 AND (x->>'triangles')::bigint<50000", (keys,)).fetchall()
        native = {(r['cache_key'], r['x']['modelId']): r for r in native}
        uids = [r['viewer_uid'] for r in profiles if r['viewer_uid']]
        reviews = con.execute('SELECT uid,review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)', (pointer['snapshotId'], uids)).fetchall()
        reviews = {r['uid']: r for r in reviews}
        # Most recent actual reason-bearing individual result for each UID and source hash.
        individual = con.execute("SELECT DISTINCT ON(result->>'uid',result->>'sourceSHA256') id,batch,stage,result,updated_at FROM astra_modelling.jobs WHERE status='complete' AND result->>'uid'=ANY(%s) AND result->>'sourceSHA256' IS NOT NULL AND jsonb_typeof(result->'reasons')='array' AND jsonb_array_length(result->'reasons')>0 AND stage NOT IN ('held-source-deferred-disposition-v1',%s) ORDER BY result->>'uid',result->>'sourceSHA256',updated_at DESC,id DESC", (uids, STAGE)).fetchall()
        individual = {(r['result']['uid'], r['result']['sourceSHA256']): r for r in individual}
        first = con.execute('SELECT id,batch,stage,status,result FROM astra_modelling.jobs WHERE id=%s', (FIRST_PASS_ID,)).fetchone()
        assert first and first['status'] == 'complete'
        first_rows = {r['uid']: r for r in first['result']['rows']}
        active = con.execute("SELECT id,batch,stage,status FROM astra_modelling.jobs WHERE status IN ('pending','running') AND batch LIKE 'government-xl-%'").fetchall()
        header = con.execute("SELECT id,result FROM astra_modelling.jobs WHERE id=%s AND status='complete'", ('c2977d524d1eb81d3738eead1151a396c484396a502a0a28cc56fa3f99ae85fe',)).fetchone()
    assert len(profiles) == 521 and not active, 'Do not close work owned by active XL workers'
    rows = []
    for p in profiles:
        key = (p['cache_key'], p['model_id'])
        n = native[key]
        assert p['source_result_sha'] == n['result_sha']
        model = n['x']
        uid = p['viewer_uid']
        assert uid == (model.get('candidate') or {}).get('uid')
        sha = (model.get('asset') or {}).get('sha256')
        assert sha and len(sha) == 64
        row = {
            'sourceKey': p['cache_key'] + '/' + p['model_id'], 'nativeRun': NATIVE_RUN,
            'nativeCacheKey': p['cache_key'], 'nativeResultSHA256': p['source_result_sha'],
            'modelId': p['model_id'], 'sheet': p['sheet'], 'uid': uid,
            'name': (model.get('candidate') or {}).get('label'), 'triangles': p['triangles'],
            'sourceSHA256': sha, 'permanentRejection': False, 'newlyInstalled': 0,
            'publication': False, 'modelGeometryChanges': 0,
        }
        if uid in installed:
            deployed, catalogue = installed[uid]
            path = catalogue.parent / deployed['asset']
            assert digest(path.read_bytes()) == deployed['sha256']
            review = reviews.get(uid)
            verified = review and review['review_state'] == 'installed-verified' and review['source_sha256'] == deployed['sha256']
            row.update(disposition='installed' if verified else 'open',
                       reasons=[] if verified else ['published-model-lacks-current-installed-verification'],
                       installedSourceSHA256=deployed['sha256'],
                       reviewSnapshotId=pointer['snapshotId'], currentReview=review,
                       runtimeEvidence={'path': str(catalogue.relative_to(ROOT)), 'sha256': digest(catalogue.read_bytes())},
                       installedAsset={'path': str(path.relative_to(ROOT)), 'sha256': deployed['sha256']})
        elif not uid:
            assert model['state'] == 'source-match-held' and model.get('holdReason') == p['source_hold_reason']
            row.update(disposition='filed-cannot-install', reasons=['no-unique-explicit-viewer-polygon-match'],
                       observation=p['source_hold_reason'],
                       evidence={'nativeModel': model, 'nativeResultSHA256': n['result_sha']},
                       revisitTrigger='An exact unique viewer match established from authoritative identity and component coverage.')
        else:
            phase = individual.get((uid, sha))
            first_row = first_rows.get(uid)
            if phase:
                result = phase['result']
                assert not result.get('passed') and not result.get('installationApproved') and not result.get('publication')
                row.update(disposition='filed-cannot-install', reasons=result['reasons'],
                           observation='The exact original source has unresolved recorded validation failures; no verified safe installation is available. Filing preserves the failed contract and does not prove permanent impossibility.',
                           evidence={'jobId': phase['id'], 'batch': phase['batch'], 'stage': phase['stage'],
                                     'resultSHA256': canonical_hash(result), 'result': result},
                           firstPassEvidence=first_row,
                           revisitTrigger='Changed source/terrain/component evidence or a verified code correction addressing these specific failures; rerun all acceptance gates before installation.')
            else:
                # Do not convert first-pass proxy warnings or sparse terrain samples into terminal rejection.
                row.update(disposition='open', reasons=['needs-source-bound-detailed-disposition'],
                           firstPassEvidence=first_row, nativeTerrainDiagnostic=model.get('terrainCheck'),
                           nextStep='Find a completed detailed source-bound receipt or run the missing detailed checks; initial proxy warnings do not establish rejection.')
        row['reasonGroup'] = reason_group(row['reasons']) if row['reasons'] else None
        rows.append(row)
    counts = dict(Counter(r['disposition'] for r in rows))
    inputs = [manifest_path, ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json', Path(__file__).resolve(), *catalogues]
    refs = [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p.read_bytes())} for p in inputs]
    report = {'scope': 'All 521 XL government sources in the indexed native run, including unmatched sources and Lantau.',
              'nativeRun': NATIVE_RUN, 'sizeGroup': 'xl', 'reviewSnapshotId': pointer['snapshotId'],
              'models': len(rows), 'counts': counts, 'rows': rows, 'evidenceRefs': refs,
              'openUids': [r['uid'] for r in rows if r['disposition'] == 'open'],
              'filedReasonGroups': dict(Counter(r['reasonGroup'] for r in rows if r['disposition'] == 'filed-cannot-install')),
              'scriptExternalAICalls': 0, 'newlyInstalled': 0, 'modelGeometryChanges': 0,
              'qualification': 'Source-specific filing under the tested contract, not a global impossibility bound. Only exact current installed verification counts as installed. Open rows remain required work. No acceptance, runtime or review-state changes.'}
    save(doc / 'audit.json.gz', report)
    return report


def file_rows(doc, report):
    rows = [r for r in report['rows'] if r['disposition'] == 'filed-cannot-install']
    resources = ['building:' + r['uid'] if r['uid'] else 'native-model:' + r['sourceKey'] for r in rows]
    claim = reservations.claim('codex-xl-dispositions-' + str(uuid.uuid4()), resources, batch=doc.name)
    assert claim['ok'], claim
    lease = claim['reservation']
    written = []
    try:
        with connect() as con:
            con.row_factory = dict_row
            con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            assert reservations._current(con, lease)
            for evidence in report['evidenceRefs']:
                assert digest((ROOT / evidence['path']).read_bytes()) == evidence['sha256']
            for row in rows:
                if row.get('evidence', {}).get('jobId'):
                    ev = row['evidence']
                    actual = con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (ev['jobId'],)).fetchone()
                    assert actual['status'] == 'complete' and actual['result'] == ev['result']
                else:
                    actual = con.execute("SELECT result_sha,x FROM astra_modelling.native_stage_results r CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') x WHERE cache_key=%s AND x->>'modelId'=%s", (row['nativeCacheKey'], row['modelId'])).fetchone()
                    assert actual['result_sha'] == row['nativeResultSHA256'] and actual['x'] == row['evidence']['nativeModel']
                payload = {'sourceKey': row['sourceKey'], 'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'], 'decisionSHA256': canonical_hash(row)}
                jid = canonical_hash([doc.name, STAGE, payload])
                result = {**row, 'state': 'filed-cannot-install', 'deferred': True, 'revisitLater': True,
                          'retainCurrentModel': True, 'requiresHumanDecision': False, 'requiresAI': None,
                          'batch': doc.name, 'stage': STAGE, 'jobId': jid}
                con.execute("INSERT INTO astra_modelling.jobs(id,batch,stage,payload,status,result) VALUES(%s,%s,%s,%s,'complete',%s) ON CONFLICT(id) DO NOTHING", (jid, doc.name, STAGE, Jsonb(payload), Jsonb(result)))
                assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == {'status': 'complete', 'result': result}
                written.append({'sourceKey': row['sourceKey'], 'uid': row['uid'], 'jobId': jid, 'sourceSHA256': row['sourceSHA256'], 'resultSHA256': canonical_hash(result)})
        with connect() as con:
            got = con.execute('SELECT id,status,result FROM astra_modelling.jobs WHERE id=ANY(%s)', ([r['jobId'] for r in written],)).fetchall()
        assert {j: canonical_hash(r) for j,s,r in got if s == 'complete' and r['state'] == 'filed-cannot-install' and r['revisitLater']} == {r['jobId']: r['resultSHA256'] for r in written}
        save(doc / 'neon-sync.json', {'rows': written, 'modelsFiled': len(written), 'freshReadbackVerified': True, 'ledger': 'astra_modelling.jobs', 'stage': STAGE})
    finally:
        assert reservations.release(lease)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--file', action='store_true')
    args = parser.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    assert not doc.exists(), 'Reuse immutable completed audit; choose a fresh batch for changed inputs'
    report = audit(doc)
    if args.file:
        file_rows(doc, report)
    print({k: report[k] for k in ('models', 'counts', 'filedReasonGroups', 'openUids')})

if __name__ == '__main__':
    main()
