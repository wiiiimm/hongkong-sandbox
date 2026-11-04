"""Freeze actual installed successors and technical XL holds; no diagnostic credit."""
import json,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
BATCH='government-xl-ground-followthrough-checkpoint-20261005'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
BASE=ROOT/'docs/astra-city/government-import'
SOURCES=[('landsd/327153:0','government-xl-unnamed-327153-retained-parent-20261005','installed'),
         ('landsd/102008:0','government-xl-west-kowloon-place-current-recheck-20261005','installed'),
         ('landsd/80343:0','government-xl-science-museum-partial-parent-20261005','held-unknown'),
         ('landsd/227380:0','government-xl-tower3-227380-retained-parent-20261005','held-unknown'),
         ('landsd/30031:0','government-xl-beverly9-ground-followthrough-20261005','held-unknown')]
PHASES=['government-xl-science-museum-partial-parent-20261005','government-xl-science-museum-original-parent-20261005',
'government-xl-unnamed-327153-ground-followthrough-20261005','government-xl-unnamed-327153-retained-terrain-20261005',
'government-xl-unnamed-327153-retained-parent-20261005','government-xl-west-kowloon-place-ground-followthrough-20261005',
'government-xl-west-kowloon-place-partial-parent-20261005','government-xl-west-kowloon-place-original-parent-20261005',
'government-xl-west-kowloon-place-current-recheck-20261005','government-xl-tower3-227380-ground-followthrough-20261005',
'government-xl-tower3-227380-retained-terrain-20261005','government-xl-tower3-227380-current-recheck-20261005',
'government-xl-tower3-227380-published-context-20261005','government-xl-tower3-227380-retained-parent-20261005',
'government-xl-beverly9-ground-followthrough-20261005']
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}
def main():
    assert not DOC.exists(),'Fresh immutable checkpoint only'
    scope=[u for u,_,_ in SOURCES]
    claim=reservations.claim('codex-ground-followthrough-'+str(uuid.uuid4()),['building:'+u for u in scope],batch=BATCH);assert claim['ok'],claim
    lease=claim['reservation']
    try:
        completed=[];refs=[];rows=[]
        for name in PHASES:
            folder=BASE/name;result=read(folder/'result.json');sync=read(folder/'neon-sync.json')
            assert sync['resultVerified'] and sync['jobId']==result['jobId']
            completed.append((result['jobId'],result));refs.extend([ref(folder/'result.json'),ref(folder/'neon-sync.json')])
            for e in result['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256']
            assert not reservations.owns(read(HERE/'local'/name/'reservation.json'))
        for uid,name,status in SOURCES:
            folder=BASE/name;phase=read(folder/'result.json')
            if status=='installed':
                sync=read(folder/'installation/neon-sync.json');assert sync['resultVerified'] and sync['installedUids']==[uid]
                accept=read(folder/'installation/installed-acceptance.json');assert accept['publication'] and accept['sourceSHA256']==phase['sourceSHA256']
                for n in ('staged-browser.json','live-browser.json'):
                    browser=read(folder/'installation'/n);assert not browser['errors'] and len([v for v in browser['views'] if v.get('time')])==4
                refs.extend([ref(folder/'installation/neon-sync.json'),ref(folder/'installation/installed-acceptance.json')])
                rows.append({'uid':uid,'sourceSHA256':phase['sourceSHA256'],'humanStatus':status,'installed':True,'jobId':sync['jobId']})
                assert not reservations.owns(read(HERE/'local'/name/'install-reservation.json'))
            else:
                assert phase['reasons'];rows.append({'uid':uid,'sourceSHA256':phase['sourceSHA256'],'humanStatus':status,
                    'installed':False,'jobId':phase['jobId'],'reasons':phase['reasons'],'requiresAI':False,'requiresHumanDecision':False})
        pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
        cohort={r['uid'] for r in read(BASE/'government-xl-remaining-20260923/selection.json.gz')['rows']};assert len(cohort)==352
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            for id,result in completed:
                actual=con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(id,)).fetchone();assert actual[0]=='complete' and actual[1]==result
            reviews=dict(con.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s',(pointer['snapshotId'],)))
            assert all(reviews.get(r['uid'])=='installed-verified' for r in rows if r['installed'])
            assert all(reviews.get(r['uid'])!='installed-verified' for r in rows if not r['installed'])
            assert all(con.execute('SELECT status FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()[0]=='complete' for r in rows)
        count=sum(reviews.get(u)=='installed-verified' for u in cohort);assert count==44
        payload={'evidenceRefs':refs,'runnerSHA256':digest(Path(__file__).read_bytes()),'reviewSnapshot':pointer['snapshotId']}
        stage='ground-followthrough-installed-checkpoint-v1';id=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==id
        result={**payload,'batch':BATCH,'jobId':id,'rows':rows,'newlyInstalled':2,'primarySources':5,
            'widerXLCheckpoint':{'models':352,'installed':count,'held':352-count},
            'humanCounts':{'installed':2,'to-do':0,'held-human':0,'held-ai':0,'held-unknown':3,'in-process':0},
            'activeWorkers':0,'queuedFollowups':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,
            'progress':read(ROOT/'3d-viewer/city/data/building-progress.json'),
            'qualification':'Installed successors are verified from the current review snapshot, actual publications and staged/live browser evidence. Earlier script-ready phase records grant no duplicate credit. Remaining failures are technical, not established AI/human requirements.'}
        with connect() as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),id,job['owner'],job['token'])).rowcount==1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(id,)).fetchone()[0]==result
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':id,'resultVerified':True,'reviewSnapshot':pointer['snapshotId']})
        print(json.dumps({'newlyInstalled':2,'XL':result['widerXLCheckpoint'],'jobId':id,'neonVerified':True}),flush=True)
    finally:reservations.release(lease)
if __name__=='__main__':main()
