"""File Cullinan's fresh failure and prove terminal coverage of the full XL run.

Completion requires every indexed XL source to be currently installed-verified
or have a persisted source-specific cannot-install filing. No open rows pass.
"""
import uuid
from pathlib import Path
from collections import Counter
from run import ROOT,read,save,digest,connect,jobs,reservations,Jsonb,dict_row,NATIVE_RUN
from importlib.util import spec_from_file_location,module_from_spec
DIR=Path(__file__).resolve().parent
spec=spec_from_file_location('terminal_audit_helpers',DIR/'xl-disposition-audit.py');helpers=module_from_spec(spec);spec.loader.exec_module(helpers)
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-terminal-dispositions-20261008'
DOC=BASE/BATCH


def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}


def main():
    assert not DOC.exists()
    previous_path=BASE/'government-xl-all-source-disposition-followthrough-20261007/audit.json.gz'
    previous=read(previous_path);rows=previous['rows'];by_uid={r['uid']:r for r in rows if r['uid']}
    cullinan_path=BASE/'government-xl-cullinan5-final-disposition-current-20261007/result.json'
    cullinan=read(cullinan_path);assert cullinan['uid']=='landsd/120158:0' and cullinan['reasons'] and not cullinan['scriptChecksPassed']
    pointerpath=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointerpath)
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath)
    installed={m['uid']:(m,ROOT/'3d-viewer'/url) for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    with connect() as con:
        con.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(cullinan['jobId'],)).fetchone()==('complete',cullinan)
        profiles=con.execute("SELECT cache_key,model_id,viewer_uid,triangles,source_result_sha FROM astra_modelling.native_model_sizes WHERE run_id=%s AND size_group='xl' ORDER BY cache_key,model_id",(NATIVE_RUN,)).fetchall()
        reviews=con.execute('SELECT uid,review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(pointer['snapshotId'],list(by_uid))).fetchall()
        latest=con.execute("SELECT DISTINCT ON(payload->>'sourceKey') id,payload,result FROM astra_modelling.jobs WHERE status='complete' AND stage='xl-source-disposition-v1' ORDER BY payload->>'sourceKey',updated_at DESC,id DESC").fetchall()
        active=con.execute("SELECT id,batch,stage,status FROM astra_modelling.jobs WHERE status IN ('pending','running') AND batch LIKE 'government-xl-%%'").fetchall()
    assert len(profiles)==len(rows)==521 and len({r['sourceKey'] for r in rows})==521
    assert {k+'/'+m:(u,t,s) for k,m,u,t,s in profiles}=={r['sourceKey']:(r['uid'],r['triangles'],r['nativeResultSHA256']) for r in rows}
    assert not active,'Cannot complete while any XL job remains pending/running'
    reviews={u:(s,h,r) for u,s,h,r in reviews};filings={p['sourceKey']:(j,p,r) for j,p,r in latest if p.get('sourceKey')}
    claim=reservations.claim('codex-xl-terminal-audit-'+str(uuid.uuid4()),['building:landsd/120158:0','xl-disposition-inventory:'+NATIVE_RUN],batch=BATCH)
    assert claim['ok'],claim
    lease=claim['reservation']
    try:
        row=by_uid[cullinan['uid']]
        assert row['sourceSHA256']==cullinan['sourceSHA256']
        for evidence in cullinan['evidenceRefs']:assert ref(ROOT/evidence['path'])==evidence
        row.update(disposition='filed-cannot-install',reasons=cullinan['reasons'],reasonGroup='component-support',
                   observation='Fresh current-input checks find 648/652 strict original support contacts; four remain unresolved, with contact and compound foundation failures. No safe installation is established.',
                   evidence={'jobId':cullinan['jobId'],'resultSHA256':helpers.canonical_hash(cullinan),'result':cullinan},
                   revisitTrigger='Corrected official support/interface/source evidence or a verified correction resolving all failed contact/foundation checks; revalidate before installation.')
        payload={'sourceKey':row['sourceKey'],'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'decisionSHA256':helpers.canonical_hash(row)}
        jid=helpers.canonical_hash([BATCH,helpers.STAGE,payload]);result={**row,'state':'filed-cannot-install','deferred':True,'revisitLater':True,'retainCurrentModel':True,'requiresHumanDecision':False,'requiresAI':None,'batch':BATCH,'stage':helpers.STAGE,'jobId':jid}
        with connect() as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
            con.execute("INSERT INTO astra_modelling.jobs(id,batch,stage,payload,status,result) VALUES(%s,%s,%s,%s,'complete',%s) ON CONFLICT(id) DO NOTHING",(jid,BATCH,helpers.STAGE,Jsonb(payload),Jsonb(result)))
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()=={'status':'complete','result':result}
        filings[row['sourceKey']]=(jid,payload,result)
        for row in rows:
            uid=row['uid']
            if uid in installed:
                model,cat=installed[uid]
                state,sha,review_result=reviews[uid]
                assert state=='installed-verified' and sha==model['sha256'],uid
                assert digest((cat.parent/model['asset']).read_bytes())==sha
                assert review_result and review_result.get('evidence') and review_result.get('sha256'),uid
                review_evidence=ROOT/review_result['evidence']
                assert digest(review_evidence.read_bytes())==review_result['sha256'],uid
                # Older ledger results bind the source in model_reviews.source_sha256.
                # Newer results repeat that binding inside the result as well.
                if 'source_sha256' in review_result:assert review_result['source_sha256']==sha,uid
                row.update(disposition='installed',reasons=[],reasonGroup=None,reviewSnapshotId=pointer['snapshotId'],
                           installedSourceSHA256=sha,currentReview={'state':state,'sourceSHA256':sha,'result':review_result},
                           runtimeEvidence=ref(cat),installedAsset=ref(cat.parent/model['asset']),reviewEvidence=ref(review_evidence),
                           sourceBinding='current-review-row-and-runtime-asset')
            else:
                j,p,r=filings[row['sourceKey']]
                assert r['uid']==uid and r['sourceSHA256']==row['sourceSHA256'] and p['sourceSHA256']==row['sourceSHA256']
                assert r['disposition']==r['state']=='filed-cannot-install' and r['reasons'] and r['deferred'] and r['revisitLater']
                assert not r['permanentRejection'] and not r['newlyInstalled'] and not r['publication'] and not r['modelGeometryChanges']
                row.update(disposition='filed-cannot-install',reasons=r['reasons'],reasonGroup=r['reasonGroup'],
                           terminalNeonJobId=j,terminalNeonResultSHA256=helpers.canonical_hash(r))
        counts=dict(Counter(r['disposition'] for r in rows));assert counts=={'filed-cannot-install':331,'installed':190} or counts=={'installed':190,'filed-cannot-install':331}
        report={**previous,'rows':rows,'counts':counts,'openUids':[],'reviewSnapshotId':pointer['snapshotId'],
                'filedReasonGroups':dict(Counter(r['reasonGroup'] for r in rows if r['disposition']=='filed-cannot-install')),
                'completionVerified':True,'models':521,'matchedModels':453,'unmatchedModels':68,
                'activeWorkers':0,'queuedFollowups':0,'newRuntimeModelsInstalledThisCompletionPass':0,
                'legacyPublicationsNewlyVerified':2,'evidenceRefs':[ref(previous_path),ref(cullinan_path),ref(pointerpath),ref(manifestpath),ref(Path(__file__).resolve())],
                'qualification':'Every XL source in the frozen indexed native run is currently installed-verified or explicitly filed in Neon as cannot install under the recorded original-source checks. Filings retain source-specific reasons and revisit triggers; none claims permanent impossibility. No source geometry changes, acceptance waivers or new runtime models in this completion pass.'}
        save(DOC/'audit.json.gz',report)
        payload={'nativeRun':NATIVE_RUN,'models':521,'snapshotId':pointer['snapshotId'],'audit':ref(DOC/'audit.json.gz')};stage='all-xl-terminal-completion-audit-v1'
        finalid=helpers.canonical_hash([BATCH,stage,payload]);summary={**payload,'batch':BATCH,'stage':stage,'jobId':finalid,'counts':counts,'filedReasonGroups':report['filedReasonGroups'],'completionVerified':True,'openModels':0,'activeWorkers':0,'queuedFollowups':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,'newlyInstalled':0,'publication':False}
        with connect() as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
            for row in rows:
                if row['disposition']=='installed':
                    actual=con.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(pointer['snapshotId'],row['uid'])).fetchone()
                    assert actual=={'review_state':'installed-verified','source_sha256':row['installedSourceSHA256']}
                else:
                    actual=con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(row['terminalNeonJobId'],)).fetchone()
                    assert actual['status']=='complete' and helpers.canonical_hash(actual['result'])==row['terminalNeonResultSHA256']
            assert read(pointerpath)==pointer and digest(manifestpath.read_bytes())==report['evidenceRefs'][3]['sha256']
            con.execute("INSERT INTO astra_modelling.jobs(id,batch,stage,payload,status,result) VALUES(%s,%s,%s,%s,'complete',%s)",(finalid,BATCH,stage,Jsonb(payload),Jsonb(summary)))
        with connect() as con:
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(finalid,)).fetchone()==('complete',summary)
        save(DOC/'result.json',summary);save(DOC/'neon-sync.json',{'jobId':finalid,'resultVerified':True,'modelsVerified':521,'openModels':0,'cullinanDispositionJobId':jid})
        print(summary)
    finally:assert reservations.release(lease)

if __name__=='__main__':main()
