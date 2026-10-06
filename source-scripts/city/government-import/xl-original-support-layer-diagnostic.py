"""Fence a bounded original support-layer diagnostic in Neon; no acceptance credit."""
import argparse,json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,dict_row,Jsonb
from publication_lock import locked_publication

def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def inputs(paths):
 sources={};pairs=[];refs=[]
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY')
  for path in paths:
   result=read(path/'result.json');sync=read(path/'neon-sync.json')
   assert sync['resultVerified'] and sync['jobId']==result['jobId']
   assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
   for evidence in result['evidenceRefs']:assert ref(ROOT/evidence['path'])==evidence
   original=read(path/'support-inputs.json')
   for row in original['sources']:
    if row['uid'] in sources:assert sources[row['uid']]['sourceSHA256']==row['sourceSHA256']
    else:sources[row['uid']]=row
   pairs.extend({**pair,'previousChecks':str((path/'support-checks.json.gz').relative_to(ROOT))} for pair in original['pairs'])
   refs.extend(ref(path/n) for n in ['result.json','neon-sync.json','support-inputs.json','support-checks.json.gz'])
 assert len(pairs)==len({(r['uid'],r['supportUid']) for r in pairs})
 return {'sources':list(sources.values()),'pairs':pairs,'previousEvidenceRefs':refs,'publication':False,'modelGeometryChanges':0}
def main():
 p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--source',action='append',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert Path(a.batch).name==a.batch and a.batch.startswith('government-xl-')
 paths=[(ROOT/s).resolve() for s in a.source];assert all(s.is_relative_to(ROOT/'docs/astra-city/government-import') for s in paths)
 data=inputs(paths);doc=ROOT/'docs/astra-city/government-import'/a.batch;local=HERE/'local'/a.batch
 if not a.owned:
  assert not doc.exists(),'Fresh evidence only'
  claim=reservations.claim('codex-xl-layer-diagnostic-'+str(uuid.uuid4()),['building:'+r['uid'] for r in data['sources']],batch=a.batch);assert claim['ok'],claim
  save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
  subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),'--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True);return
 with locked_publication(ROOT):
  lease=read(local/'reservation.json');assert reservations.owns(lease)
  save(doc/'diagnostic-inputs.json',data)
  subprocess.run(['node',str(HERE/'original-support-layer-diagnostic.mjs'),str(doc.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
  layers=read(doc/'layer-checks.json.gz')
  assert len(layers['rows'])==len(data['pairs'])
  for path,sha in layers['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
  refs=[ref(doc/n) for n in ['diagnostic-inputs.json','layer-checks.json.gz']]+[ref(Path(__file__))]
  payload={'evidenceRefs':refs,'batch':a.batch};stage='original-unresolved-support-layers-diagnostic-v1'
  jid=jobs.enqueue(a.batch,stage,payload);job=jobs.claim(a.batch,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'rows':layers['rows'],'inputHashes':layers['inputHashes'],'newlyInstalled':0,'activeWorkers':0,'queuedFollowups':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,'publication':False,'qualification':layers['qualification']}
  with connect() as con:
   con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
   assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as con:
   con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(doc/'result.json',result);save(doc/'neon-sync.json',{'jobId':jid,'resultVerified':True})
  print(json.dumps({'jobId':jid,'neonVerified':True,'pairs':len(layers['rows']),'newlyInstalled':0}),flush=True)
if __name__=='__main__':main()
