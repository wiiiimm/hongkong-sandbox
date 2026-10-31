"""Bind Ocean Walk's exact original wall/TIN crossings and whole foundation."""
import importlib.util,json,subprocess,uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
BATCH='government-xl-ocean-walk-original-wall-contact-evidence-20261008';DOC=ROOT/'docs/astra-city/government-import'/BATCH
ORIGINAL=ROOT/'docs/astra-city/government-import/government-xl-ocean-walk-complete-original-tin-diagnostic-20261008';LOCAL=HERE/'local/government-xl-ocean-walk-complete-original-tin-diagnostic-20261008'
CURRENT=ROOT/'docs/astra-city/government-import/government-xl-ocean-walk-current-terrain-complete-scope-20261008';UID='landsd/81743:0'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();original=read(ORIGINAL/'result.json');current=read(CURRENT/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in [original,current]:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for r in [original,current]:
  for item in r['evidenceRefs']:assert ref(ROOT/item['path'])==item
 models=LOCAL/'original-model.json.gz';terrains=LOCAL/'original-terrain.json.gz'
 subprocess.run(['node',str(HERE/'run-vertical-wall-ground-crossing-diagnostic.mjs'),str(models.relative_to(ROOT)),str(terrains.relative_to(ROOT)),str((ORIGINAL/'clearance.json').relative_to(ROOT)),str((DOC/'crossings.json').relative_to(ROOT))],cwd=ROOT,check=True)
 m=read(models)['rows'][0];t=read(terrains)['rows'][0];row=read(CURRENT/'selection.json.gz')['rows'][0];assert row['uid']==m['uid']==t['uid']==UID
 spec=importlib.util.spec_from_file_location('ocean_exact_foundation',HERE/'xl-final-script-pass.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
 b=row['source']['building'];foundation=f.foundation_context(np.asarray(m['triangles']),np.asarray(t['terrainTriangles']),Polygon(b['rings'][0],b['rings'][1:]));save(DOC/'foundation.json',{'uid':UID,'sourceSHA256':m['sourceSHA256'],'foundation':foundation,'originalTINOnly':True,'installationApproved':False})
 crossings=read(DOC/'crossings.json');assert crossings['rows'][0]['diagnostic']['allFailedSamplesAreExactVerticalWallCrossings']
 refs=[ref(p) for p in [Path(__file__),ORIGINAL/'result.json',CURRENT/'result.json',CURRENT/'selection.json.gz',DOC/'crossings.json',DOC/'foundation.json']]
 refs+=[{'path':p,'sha256':sha} for p,sha in crossings['inputHashes'].items()];refs=list({r['path']:r for r in refs}.values())
 claim=reservations.claim('codex-ocean-wall-evidence-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH);assert claim['ok'],claim;lease=claim['reservation'];job=None
 try:
  payload={'uid':UID,'sourceSHA256':m['sourceSHA256'],'evidenceRefs':refs};stage='original-vertical-wall-ground-crossing-evidence-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'all15PenetratingSamplesAreExactVerticalWallCrossings':True,'originalWholeFoundation':foundation,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'terrainGeometryChanges':0,'acceptanceGranted':False,'installationApproved':False,'scriptExternalAICalls':0,'sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'rawClearanceFailurePreserved':True,'nextStep':'Evaluate a demonstrated vertical-wall versus exposed-surface contact-test correction with full original-TIN/runtime/neighbour checks. The raw 0.636m penetration remains failed under the current numeric policy; diagnostic evidence alone grants no acceptance.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for item in refs:assert ref(ROOT/item['path'])==item
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'neonVerified':True,'foundation':foundation}),flush=True)
 except Exception as e:
  if job:assert jobs.finish(job,error=str(e))
  raise
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
