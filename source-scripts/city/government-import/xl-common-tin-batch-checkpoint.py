"""Fence the installed Alto receipt and complete original-TIN diagnostic batches."""
import uuid
from pathlib import Path
from run import ROOT, read, save, digest, reservations, jobs, connect, Jsonb, dict_row
DIR=ROOT/'source-scripts/city/government-import'
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-common-tin-batch-checkpoint-20261007'
PHASES=['government-xl-alto6-common-original-terrain-20261007','government-xl-alto6-common-preserved-terrain-20261007','government-xl-alto6-common-original-installed-20261007']
PREVIEWS=['government-xl-remaining-historical-current-tin-preview-20261007','government-xl-refreshed-current-tin-preview-20261007']

def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}

def main():
    doc=BASE/BATCH;assert not doc.exists();refs=[];uids=set();phases=[];previews=[];context=[]
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        for name in PHASES:
            p=BASE/name;r=read(p/'result.json');sync=read(p/'neon-sync.json')
            assert sync['resultVerified'] and sync['jobId']==r['jobId']
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
            for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
            refs.extend([ref(p/'result.json'),ref(p/'neon-sync.json')]);uids.add('landsd/338637:0');phases.append({'batch':name,'jobId':r['jobId'],'reasons':r.get('reasons',[]),'alreadyInstalled':r.get('installedUids',[])})
    for name in PREVIEWS:
        p=BASE/name/'result.json';r=read(p);assert r['diagnosticOnly'] and not r['publication'] and r['newlyInstalled']==r['modelGeometryChanges']==r['scriptExternalAICalls']==0
        for path,sha in r['inputHashes'].items():
            actual=ref(ROOT/path)['sha256']
            if actual!=sha:
                assert name==PREVIEWS[0] and path=='3d-viewer/city/data/manifest.json'
                context.append({'batch':name,'path':path,'historicalSHA256':sha,'currentSHA256':actual,'qualification':'Historical terrain context only, never current acceptance.'})
        refs.append(ref(p));uids.update(row['uid'] for row in r['rows']);previews.append({'batch':name,'rows':r['rows'],'skipped':r['skipped']})
    fresh=BASE/'government-xl-refreshed-current-tin-preview-20261007-inputs'
    receipt=read(fresh/'result.json');assert receipt['freshProductionGeometry'] and len(receipt['rows'])==90
    for e in receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e
    refs.extend([ref(fresh/'result.json'),ref(fresh/'refresh-inputs.json'),ref(fresh/'check-selection.json.gz'),ref(fresh/'context.json.gz'),ref(Path(__file__))])
    for name in ['xl-historical-current-tin-preview.py','xl-refresh-original-tin-inputs.py','xl-fresh-current-tin-preview.py','original_tin_point_diagnostic.py','test_original_tin_point_diagnostic.py']:refs.append(ref(DIR/name))
    pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';snapshot=read(pointer)['snapshotId'];refs.append(ref(pointer))
    installed=read(BASE/PHASES[-1]/'result.json');assert installed['snapshotId']==snapshot and installed['installedUids']==['landsd/338637:0']
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,'landsd/338637:0')).fetchone()==('installed-verified',installed['sourceSHA256'])
    scope=sorted(uids);claim=reservations.claim('codex-common-tin-checkpoint-'+str(uuid.uuid4()),['building:'+u for u in scope],batch=BATCH);assert claim['ok'];lease=claim['reservation']
    try:
        save(doc/'phases.json',{'phases':phases,'previews':previews,'historicalContextChanges':context,'publication':False,'newlyInstalled':0});refs.append(ref(doc/'phases.json'))
        stage='completed-original-tin-batch-diagnostics-v1';payload={'uids':scope,'evidenceRefs':refs};jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
        result={**payload,'jobId':jid,'batch':BATCH,'alreadyInstalled':['landsd/338637:0'],'highestTINPositive':[r['uid'] for p in previews for r in p['rows'] if r['highestOriginalTINPositive']],'mixedPointwisePositive':[r['uid'] for p in previews for r in p['rows'] if r['mixedOriginalPointwisePositive']],'freshProductionMeshes':90,'historicalCurrentMeshes':21,'historicalContextChanges':context,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'qualification':'Alto installation is already credited. Completed original TIN point diagnostics and refreshed current geometry grant no additional installation or review credit; fresh complete acceptance remains mandatory.'}
        with connect() as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
            for e in refs:assert ref(ROOT/e['path'])==e
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(doc/'result.json',result);save(doc/'neon-sync.json',{'jobId':jid,'resultVerified':True});print({'jobId':jid,'highestTINPositive':result['highestTINPositive'],'newlyInstalled':0},flush=True)
    finally:reservations.release(lease)

if __name__=='__main__':main()
