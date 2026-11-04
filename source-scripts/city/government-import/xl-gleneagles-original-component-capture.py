"""Capture three unchanged native originals and exact unresolved rim points."""
import json,subprocess,uuid,os
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
BATCH='government-xl-gleneagles-original-component-capture-20261008';DOC=ROOT/'docs/astra-city/government-import'/BATCH;OLD=ROOT/'docs/astra-city/government-import/government-xl-gleneagles-three-original-closure-20261008'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();prior=read(OLD/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
 for v in prior['evidenceRefs']:assert ref(ROOT/v['path'])==v
 rows=read(OLD/'selection.json.gz')['rows'];assert {r['uid'] for r in rows}=={'landsd/194912:0','landsd/195848:0','landsd/195849:0'};parts=[];hashes={str((OLD/'result.json').relative_to(ROOT)):digest((OLD/'result.json').read_bytes())};forms=[r['source']['building'] for r in rows]
 for r in rows:
  parts.append({'uid':r['uid'],'name':r['name'],'modelId':r['modelId'],'sourceSHA256':r['sourceSHA256'],'assetPath':r['candidate']['path'],'worldBounds':r['native']['model']['worldBounds'],'triangles':r['triangles'],'forms':forms});hashes['3d-viewer/'+r['source']['tile']]=digest((ROOT/'3d-viewer'/r['source']['tile']).read_bytes());hashes[r['candidate']['path']]=r['sourceSHA256']
 primary=next(p for p in parts if p['uid']=='landsd/195849:0');primary['originalComponents']=[p for p in parts if p is not primary];primary['failedSamples']=[v for r in read(OLD/'support-checks.json.gz')['rows'] for v in r['interface']['unresolved']];hashes[str((OLD/'support-checks.json.gz').relative_to(ROOT))]=digest((OLD/'support-checks.json.gz').read_bytes());save(DOC/'inputs.json',{'models':[primary],'inputHashes':hashes})
 claim=reservations.claim('codex-gleneagles-capture-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH);assert claim['ok'],claim;lease=claim['reservation'];job=None
 try:
  subprocess.run(['node',str(HERE/'render-original-component-evidence.mjs'),'--inputs',str((DOC/'inputs.json').relative_to(ROOT)),'--out',str(DOC.relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},check=True);render=read(DOC/'render.json');refs=[ref(Path(__file__)),ref(DOC/'render.json'),*[ref(ROOT/v['image']['path']) for v in render['views']]];refs.extend({'path':p,'sha256':h} for p,h in render['inputHashes'].items());refs=list({v['path']:v for v in refs}.values());payload={'evidenceRefs':refs,'sourceSHA256s':{r['uid']:r['sourceSHA256'] for r in rows}};stage='three-original-component-support-evidence-capture-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'batch':BATCH,'jobId':jid,'capturedOriginalComponents':3,'unresolvedRimSamples':len(primary['failedSamples']),'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'aiGeometryModelling':False,'architectureReview':False,'qualification':'Unmodified original source bytes and native poses, distinct diagnostic material colours, current exact footprints and raw failed rim points. Capture only; no architectural interpretation, source identity, support or installation acceptance.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for v in refs:assert ref(ROOT/v['path'])==v
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'neonVerified':True,'components':3,'failedSamples':len(primary['failedSamples'])}),flush=True)
 except Exception as e:
  if job:assert jobs.finish(job,error=str(e))
  raise
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
