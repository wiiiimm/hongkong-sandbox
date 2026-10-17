"""Give every original XL hold a verified installed or explicit deferred receipt.

Keep immutable original inventory and earlier failures. Exact component routing
can reconcile existing publications; it never grants new publication authority.
"""
import importlib.util
import uuid
from collections import Counter
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, jobs, reservations, Jsonb, dict_row, NATIVE_RUN
from component_type_resolution import resolve

BATCH = 'government-xl-held-second-pass-dispositions-20261008'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
PRIOR = ROOT / 'docs/astra-city/government-import/government-xl-terminal-dispositions-20261008'
RECOVERY = ROOT / 'docs/astra-city/government-import/government-xl-held-component-recovery-20261008'
HOI_TAI_DISPOSITION = '5f5dcd64607b950137ec90dea9a8e591c970e29e94d3958dba63768ead51780d'

def ref(path): return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}
def canonical(value): return digest(jobs.encode(value).encode())
def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result

def main():
    assert not DOC.exists(), 'Completed receipts are immutable; use a new stage for changed inputs'
    helpers = module('held_disposition_groups', 'xl-disposition-audit.py')
    audit = read(PRIOR / 'audit.json.gz'); previous = read(PRIOR / 'result.json')
    original = [r for r in audit['rows'] if r['disposition'] == 'filed-cannot-install']
    assert len(original) == 331
    routing = read(RECOVERY / 'routing.json')
    frozen = read(RECOVERY / 'selection.json.gz')
    physical = read(RECOVERY / 'current-checks.json')
    revised = read(RECOVERY / 'revised-physical-checks/current-checks.json')
    assert physical['checked'] == 54 and revised['checked'] == 5
    assert not physical['passes'] and not revised['passes'], 'Positive candidates require publication follow-through'
    routed = {r['sourceKey']: r for r in routing['rows']}
    selected = {r['sourceKey']: r for r in frozen['rows']}
    checks = {r['sourceKey']: r for r in physical['rows'] + revised['rows']}
    assert len(checks) == 59
    pointerpath = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    pointer = read(pointerpath); manifest = read(manifestpath)
    assert pointer['snapshotId'] == audit['reviewSnapshotId'] == frozen['snapshotId']
    assert digest(manifestpath.read_bytes()) == frozen['manifestSHA256']
    for evidence in audit['evidenceRefs']:
        assert ref(ROOT / evidence['path']) == evidence
    installed = {m['uid']: (m, ROOT / '3d-viewer' / url)
        for url in manifest['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / url)['models']}
    with connect() as con:
        con.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        for result in [previous, routing, physical, revised]:
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (result['jobId'],)).fetchone() == ('complete', result)
        filings = {j: r for j, r in con.execute('SELECT id,result FROM astra_modelling.jobs WHERE id=ANY(%s) AND status=%s',
            ([r['terminalNeonJobId'] for r in original], 'complete'))}
        reviews = {u: (state, sha, result) for u, state, sha, result in con.execute(
            'SELECT uid,review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE snapshot_id=%s', (pointer['snapshotId'],))}
        profiles = con.execute("SELECT cache_key,model_id,viewer_uid,source_result_sha FROM astra_modelling.native_model_sizes WHERE run_id=%s AND size_group='xl'", (NATIVE_RUN,)).fetchall()
        assert {k+'/'+m: (u, sha) for k,m,u,sha in profiles} == {r['sourceKey']: (r['uid'],r['nativeResultSHA256']) for r in audit['rows']}
        assert not con.execute("SELECT id FROM astra_modelling.jobs WHERE batch LIKE 'government-xl-%%' AND status IN ('pending','running')").fetchall()
        hoi_tai = con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (HOI_TAI_DISPOSITION,)).fetchone()
        assert hoi_tai[0] == 'complete' and hoi_tai[1]['sourceSHA256'] == next(r['sourceSHA256'] for r in original if r['uid']=='landsd/229881:0')
    resources = ['native-model:' + r['sourceKey'] for r in original]
    resources += ['building:' + u for u in sorted({r.get('uid') for r in original + routing['rows'] if r.get('uid')})]
    resources += ['xl-disposition-inventory:' + NATIVE_RUN]
    claim = reservations.claim('codex-xl-explicit-held-dispositions-' + str(uuid.uuid4()), resources, ttl=3600, batch=BATCH)
    assert claim['ok'], claim
    lease = claim['reservation']
    outcomes = []
    try:
        refs = [ref(PRIOR / 'audit.json.gz'), ref(PRIOR / 'result.json'), ref(RECOVERY / 'routing.json'),
            ref(RECOVERY / 'current-checks.json'), ref(RECOVERY / 'revised-physical-checks/current-checks.json'),
            ref(pointerpath), ref(manifestpath), ref(Path(__file__).resolve()), ref(HERE / 'component_type_resolution.py')]
        for row in original:
            prior = filings[row['terminalNeonJobId']]
            assert canonical(prior) == row['terminalNeonResultSHA256']
            assert prior['sourceSHA256'] == row['sourceSHA256'] and prior['reasons']
            route = routed.get(row['sourceKey']); checked = checks.get(row['sourceKey'])
            uid = (route or {}).get('uid') or row['uid']
            outcome = {**row, 'originalUid': row['uid'], 'uid': uid,
                'priorDispositionJobId': row['terminalNeonJobId'], 'priorDispositionSHA256': canonical(prior),
                'newlyInstalled': 0, 'publication': False, 'modelGeometryChanges': 0,
                'requiresHumanDecision': False, 'needsHumanDecision': False,
                'needsAIProcessing': None, 'requiresAI': None,
                'qualification': 'Source-bound validation hold, not corruption or permanent impossibility. No AI necessity or user decision is established.'}
            if route:
                outcome['componentRoutingJobId'] = routing['jobId']
                outcome['componentRouting'] = route
            if route and route['state'] == 'installed-existing-source-verified':
                model, catalogue = installed[uid]; state, sha, result = reviews[uid]
                assert state == 'installed-verified' and sha == model['sha256'] == row['sourceSHA256']
                assert digest((catalogue.parent / model['asset']).read_bytes()) == sha
                assert ref(ROOT / result['evidence']) == route['reviewEvidence']
                assert result['sha256'] == route['reviewEvidence']['sha256']
                outcome.update(state='installed-existing-source-verified', disposition='installed',
                    humanStatus='installed', displayStatus='Installed', installed=True, reasons=[], reasonGroup=None,
                    needsAIProcessing=False, requiresAI=False, needsComputeProcessing=False,
                    reviewSnapshotId=pointer['snapshotId'], runtimeAsset=ref(catalogue.parent / model['asset']),
                    runtimeCatalogue=ref(catalogue), currentReview={'state': state, 'sourceSHA256': sha, 'result': result},
                    qualification='Existing exact original source publication and current review reconciled. Zero new model assets or runtime/review changes.')
            else:
                outcome.update(state='held-for-second-pass', disposition='held', humanStatus='held-unknown',
                    displayStatus='Held — revisit later', installed=False, deferred=True, revisitLater=True,
                    permanentRejection=False, nextPass=2, retainCurrentModel=True,
                    needsComputeProcessing=None, computeOnlyWorkCompleted=True,
                    automaticRetryWithoutChangedEvidence=False,
                    blockedBy='recorded-source-specific-validation-or-authoritative-evidence',
                    nextStep=row['revisitTrigger'])
                if checked:
                    selected_row = selected[row['sourceKey']]
                    assert resolve(selected_row['native']['model'], [selected_row['source']]) == selected_row['routing']
                    reasons = checked['reasons'][:]
                    # The legacy geometry helper only selected a sole official candidate.
                    # Routing has a unique exact ObjectID/CSUID; correct metadata without
                    # discarding independent spatial/contact/foundation failures.
                    if 'exact-current-source-identity' in reasons:
                        reasons.remove('exact-current-source-identity')
                        outcome['exactCurrentObjectAndCSUID'] = True
                        outcome['metadataCorrection'] = 'Use uniquely type-qualified official candidate among multiple candidates; frozen native model unchanged.'
                    if checked['metric'].get('error') == 'Official model does not fit its matched footprint':
                        reasons = ['runtime-original-footprint-fit-failed']
                    assert reasons, 'A reason-free candidate requires complete follow-through'
                    outcome.update(reasons=reasons, reasonGroup=helpers.reason_group(reasons),
                        completeCurrentChecks=checked,
                        currentChecksJobId=physical['jobId'] if row['sourceKey'] in {r['sourceKey'] for r in physical['rows']} else revised['jobId'],
                        nextStep='Changed authoritative component/footprint/source or terrain evidence, or a demonstrated code correction resolving the recorded failures; rerun complete identity/contact/foundation/runtime/neighbour/browser gates.')
                elif route:
                    outcome.update(reasons=route['reasons'], reasonGroup='source-identity-or-component-coverage',
                        nextStep='Resolve an exact authoritative component match or validate a separately versioned current source. Preserve any existing verified runtime publication.')
                if uid == 'landsd/229881:0':
                    outcome.update(hoiTaiDispositionJobId=HOI_TAI_DISPOSITION,
                        blockedBy=hoi_tai[1]['blockedBy'], nextStep=hoi_tai[1].get('revisitTrigger') or row['revisitTrigger'])
            stage = 'installed-existing-xl-source-reconciliation-v1' if outcome['installed'] else 'held-source-deferred-disposition-v1'
            payload = {'sourceKey': row['sourceKey'], 'uid': uid, 'sourceSHA256': row['sourceSHA256'],
                'decisionSHA256': canonical(outcome), 'evidenceRefs': refs}
            jid = canonical([BATCH, stage, payload]); outcome.update(jobId=jid, batch=BATCH, stage=stage)
            outcomes.append((payload, outcome))
        counts = dict(Counter(r['humanStatus'] for _,r in outcomes))
        assert counts == {'installed': 4, 'held-unknown': 327} or counts == {'held-unknown': 327, 'installed': 4}
        with connect() as con:
            con.row_factory = dict_row; con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            assert reservations._current(con, lease)
            assert read(pointerpath) == pointer and digest(manifestpath.read_bytes()) == frozen['manifestSHA256']
            for evidence in refs: assert ref(ROOT / evidence['path']) == evidence
            for payload, result in outcomes:
                if result['installed']:
                    assert con.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',
                        (pointer['snapshotId'],result['uid'])).fetchone() == {'review_state':'installed-verified','source_sha256':result['sourceSHA256']}
                con.execute("INSERT INTO astra_modelling.jobs(id,batch,stage,payload,status,result) VALUES(%s,%s,%s,%s,'complete',%s) ON CONFLICT(id) DO NOTHING",
                    (result['jobId'],BATCH,result['stage'],Jsonb(payload),Jsonb(result)))
                assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (result['jobId'],)).fetchone() == {'status':'complete','result':result}
        with connect() as con:
            got = con.execute('SELECT id,status,result FROM astra_modelling.jobs WHERE id=ANY(%s)', ([r['jobId'] for _,r in outcomes],)).fetchall()
        assert {j:canonical(r) for j,s,r in got if s=='complete'} == {r['jobId']:canonical(r) for _,r in outcomes}
        rows = [r for _,r in outcomes]
        report = {'rows':rows,'originalHeldScope':331,'counts':counts,'fullIndexedXLScope':521,
            'fullXLCounts':{'installedVerified':194,'held':327,'open':0,'inProcess':0},
            'heldReasonGroups':dict(Counter(r['reasonGroup'] for r in rows if not r['installed'])),
            'existingInstallRecordsReconciled':4,'newRuntimeAssetsInstalled':0,'newlyInstalled':0,
            'recoveredExactOriginalAssets':59,'checkedRecoveredOriginals':59,'installationPasses':0,
            'evidenceRefs':refs,'scriptExternalAICalls':0,'modelGeometryChanges':0,
            'qualification':'Every original hold has an exact source-bound installed or held receipt, verified by fresh Neon readback. The 327 holds preserve reasons, completed work and second-pass triggers; AI necessity and permanent impossibility are not asserted.'}
        save(DOC / 'dispositions.json.gz', report)
        stage = 'all-xl-explicit-held-second-pass-audit-v1'
        payload = {'nativeRun':NATIVE_RUN,'scope':331,'report':ref(DOC / 'dispositions.json.gz')}
        jid = canonical([BATCH,stage,payload]); result = {k:v for k,v in report.items() if k not in ['rows','evidenceRefs']}
        result.update(jobId=jid,batch=BATCH,stage=stage,report=payload['report'])
        with connect() as con:
            con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,)); assert reservations._current(con,lease)
            con.execute("INSERT INTO astra_modelling.jobs(id,batch,stage,payload,status,result) VALUES(%s,%s,%s,%s,'complete',%s)",
                (jid,BATCH,stage,Jsonb(payload),Jsonb(result)))
        with connect() as con: assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(DOC/'result.json',result); save(DOC/'neon-sync.json',{'jobId':jid,'freshReadbackVerified':True,'sourceDispositionsVerified':331})
        print(result,flush=True)
    finally: assert reservations.release(lease)

if __name__ == '__main__': main()
