"""Persist fresh contact diagnostics without changing reviews or installed totals."""
import json
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row

BATCH='government-xl-fresh-original-33-preview-checkpoint-20261007'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
BASE=DOC.parent
PAIRS=[('government-xl-fresh-original-terrain-20-preview-20261007','government-xl-original-surfaces-20-current-inputs-20261007'),
       ('government-xl-fresh-original-terrain-13-reviewed-preview-20261007','government-xl-thirteen-reviewed-original-diagnostic-inputs-20261007')]


def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}


def main():
    assert not DOC.exists()
    groups=[];refs=[];uids=[];pinned=[]
    for preview,freeze in PAIRS:
        p=BASE/preview/'result.json';r=read(p)
        assert r['diagnosticOnly'] and not r['publication'] and r['newlyInstalled']==r['modelGeometryChanges']==r['scriptExternalAICalls']==0
        assert ref(ROOT/r['geometry']['path'])==r['geometry']
        for name,sha in r['inputHashes'].items():assert digest((ROOT/name).read_bytes())==sha
        for field in ('source','parent'):assert ref(ROOT/r[field]['path'])==r[field]
        selection=read(BASE/freeze/'check-selection.json.gz')
        assert {row['uid'] for row in selection['rows']}=={row['uid'] for row in r['rows']}
        for row in selection['rows']:
            if row.get('currentReview'):pinned.append(row['currentReview'])
        refs += [ref(p),ref(BASE/freeze/'check-selection.json.gz'),ref(BASE/freeze/'context.json.gz'),ref(BASE/freeze/'preflight.json')]
        groups.append({'previewBatch':preview,'freezeBatch':freeze,'rows':r['rows']})
        uids.extend(row['uid'] for row in r['rows'])
    assert len(uids)==len(set(uids))==33 and len(pinned)==13
    claim=reservations.claim('codex-fresh-contact-checkpoint-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=BATCH);assert claim['ok']
    lease=claim['reservation']
    try:
        pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            for expected in pinned:
                assert con.execute('SELECT snapshot_id,review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE uid=%s ORDER BY updated_at DESC LIMIT 1',(expected['uid'],)).fetchone()==(expected['snapshotId'],expected['state'],expected['sourceSHA256'],expected['result'])
        save(DOC/'diagnostics.json',{'groups':groups,'diagnosticOnly':True,'priorReviewsPreserved':True,'newlyInstalled':0})
        refs += [ref(DOC/'diagnostics.json'),ref(Path(__file__)),ref(HERE/'xl-fresh-original-terrain-preview.py'),ref(HERE/'xl-freeze-thirteen-reviewed-diagnostics.py')]
        stage='fresh-original-contact-preview-checkpoint-v1';payload={'uids':uids,'evidenceRefs':refs,'reviewSnapshot':pointer['snapshotId']}
        jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
        result={**payload,'jobId':jid,'batch':BATCH,'models':len(uids),'standaloneContactPreviewPasses':sum(row['originalDTMContactPreviewPass'] or row['originalParentContactPreviewPass'] for g in groups for row in g['rows']),
                'pointwiseTwoOriginalsPositive':sum(row['pointwiseTwoSourcePositive'] for g in groups for row in g['rows']),
                'newlyInstalled':0,'publication':False,'diagnosticOnly':True,'priorReviewsPreserved':True,
                'modelGeometryChanges':0,'scriptExternalAICalls':0,'activeWorkers':0,'queuedFollowups':0,
                'qualification':'All vertices, face centres and low rim edge samples in exact current production poses; original DTM and root terrain only. Original government TIN not exhausted by this preview. No installation, skip or architectural-review credit.'}
        with connect() as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
            for r in refs:assert ref(ROOT/r['path'])==r
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True})
        print(json.dumps({k:result[k] for k in ('jobId','models','standaloneContactPreviewPasses','pointwiseTwoOriginalsPositive','newlyInstalled')}),flush=True)
    finally:reservations.release(lease)


if __name__=='__main__':main()
