"""Bind verified successor acquisition to the existing fresh-source receipt contract."""
import argparse
import json
import sys
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row,NATIVE_RUN
sys.path.insert(0,str(HERE.parent/'citywide-native'))
from convert import converter_dependencies


def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',required=True);parser.add_argument('--batch',required=True);args=parser.parse_args()
    assert Path(args.batch).name==args.batch and args.batch.startswith('government-xl-')
    source=(ROOT/args.source).resolve();base=ROOT/'docs/astra-city/government-import';assert source.parent==base
    doc=base/args.batch;assert not doc.exists()
    prior=read(source/'result.json');assert prior['diagnosticOnly'] and not prior['publication'] and prior['newlyInstalled']==0
    selected=read(source/'check-selection.json.gz');assert len(selected['rows'])==1
    row=selected['rows'][0];uid=row['uid'];native=row['native'];assert native['model']['modelId']==row['modelId']
    predecessor=row['successorOf'];assert predecessor['modelId']!=row['modelId'] and predecessor['sourceSHA256']!=row['sourceSHA256']
    assert predecessor['modelId'][:-1]==row['modelId'][:-1]
    assert all(native['model']['runtimeFormatChecks'].values()) and native['model']['bitPreservation']
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==native['model']['asset']['sha256']
    claim=reservations.claim('codex-successor-receipt-'+str(uuid.uuid4()),['building:'+uid],batch=args.batch);assert claim['ok'];lease=claim['reservation']
    try:
        for evidence in prior['evidenceRefs']:assert ref(ROOT/evidence['path'])==evidence
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT stage,status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('official-successor-readonly-diagnostic-v1','complete',prior)
            assert not con.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=%s',(uid,)).fetchall()
            old=next(r for r in read(base/'government-xl-remaining-20260923/selection.json.gz')['rows'] if r['uid']==uid)
            assert old['modelId']==predecessor['modelId'] and old['sourceSHA256']==predecessor['sourceSHA256']
            assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,old['native']['cacheKey'])).fetchone()==(old['native']['resultSha'],)
        download=asset.parent.parent.parent/'original/download.json'
        record=read(download);assert record['sheet']==native['sheet']
        assert native['model']['sourceEntry'] in {r['name'] for r in record['entries']}
        directory_ref=next(r for r in prior['evidenceRefs'] if r['path'].endswith('/directory/result.json'))
        directory=read(ROOT/directory_ref['path']);assert record['directorySHA256']==directory['directorySHA256']
        assert row['modelId'] in {m['modelId'] for m in directory['models']} and predecessor['modelId'] not in {m['modelId'] for m in directory['models']}
        for member,sha in native['model']['sourceHashes'].items():assert next(r for r in record['entries'] if r['name']==member)['sha256']==sha
        acquired={'uid':uid,'source':row['source'],'priorModelId':predecessor['modelId'],'priorSourceSHA256':predecessor['sourceSHA256'],
                  'modelId':row['modelId'],'sourceSHA256':row['sourceSHA256'],'assetPath':str(asset.relative_to(ROOT)),'model':native['model']}
        save(doc/'current-originals.json',{'rows':[acquired],'errors':{}})
        save(doc/'revisions.json',[{'sheet':native['sheet'],'directory':directory_ref['path'],'directorySHA256':directory['directorySHA256'],
             'sourceETag':directory['etag'],'download':str(download.relative_to(ROOT)),'archiveSHA256':record['sha256']}])
        refs=[ref(source/'result.json'),ref(doc/'current-originals.json'),ref(doc/'revisions.json'),ref(asset),ref(download),ref(Path(__file__))]
        refs.extend(ref(path) for path in converter_dependencies())
        payload={'uids':[uid],'evidenceRefs':refs};stage='explicit-current-government-revision-acquisition-v1'
        jid=jobs.enqueue(args.batch,stage,payload);job=jobs.claim(args.batch,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
        result={**payload,'batch':args.batch,'jobId':jid,'rows':[acquired],'errors':{},'acquired':1,'publication':False,'newlyInstalled':0,
                'modelGeometryChanges':0,'scriptExternalAICalls':0,'qualification':'Read-back verified official successor acquisition, byte-preserved packing and exact predecessor native result. Existing fresh revision receipt contract; no identity/physical/publication waiver.'}
        with connect() as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
            for evidence in refs:assert ref(ROOT/evidence['path'])==evidence
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(doc/'result.json',result);save(doc/'neon-sync.json',{'jobId':jid,'resultVerified':True})
        print(json.dumps({'uid':uid,'jobId':jid,'acquired':1,'newlyInstalled':0}),flush=True)
    finally:reservations.release(lease)


if __name__=='__main__':main()
