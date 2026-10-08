"""Fresh current-ground diagnostic of exact Ocean Walk wall crossings.

No source or acceptance-policy edits. Distinguish emerging vertical walls from
buried floors using every incident original source face and fresh drawn ground.
"""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
BATCH='government-xl-ocean-walk-current-wall-clearance-diagnostic-20261008';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
OLD=HERE/'local/government-xl-ocean-walk-complete-original-tin-diagnostic-20261008';PRIOR=ROOT/'docs/astra-city/government-import/government-xl-ocean-walk-complete-original-tin-diagnostic-20261008';UID='landsd/81743:0'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);prior=read(PRIOR/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
 original=OLD/'original-model.json.gz';expected=next(r for r in prior['evidenceRefs'] if r['path']==str(original.relative_to(ROOT)));assert ref(original)==expected
 models=read(original);assert len(models['rows'])==1 and models['rows'][0]['uid']==UID;manifest=ROOT/'3d-viewer/city/data/manifest.json';models['manifestSHA256']=digest(manifest.read_bytes());save(LOCAL/'original-model.json.gz',models)
 rel=lambda p:str(p.relative_to(ROOT));subprocess.run(['node',str(HERE/'original-source-clearance-diagnostic.mjs'),rel(LOCAL/'original-model.json.gz'),rel(DOC/'clearance.json'),rel(LOCAL/'current-drawn-ground.json.gz')],cwd=ROOT,check=True)
 ground=read(LOCAL/'current-drawn-ground.json.gz');model=models['rows'][0];g=ground['rows'][0];assert g['uid']==UID and g['worldTrianglesSHA256']==model['worldTrianglesSHA256'];tri=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
 save(LOCAL/'current-terrain.json.gz',{'rows':[{'uid':UID,'terrainTriangles':tri.tolist()}]})
 clearance=read(DOC/'clearance.json');record=clearance['rows'][0];save(DOC/'crossing-input.json',{'rows':[{**record,'worldTrianglesSHA256':model['worldTrianglesSHA256'],'failedSamples':g['failedSamples']}]})
 subprocess.run(['node',str(HERE/'run-vertical-wall-ground-crossing-diagnostic.mjs'),rel(LOCAL/'original-model.json.gz'),rel(LOCAL/'current-terrain.json.gz'),rel(DOC/'crossing-input.json'),rel(DOC/'crossings.json')],cwd=ROOT,check=True)
 spec=importlib.util.spec_from_file_location('ocean_current_wall_foundation',HERE/'xl-final-script-pass.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);forms=f.load_forms([model['worldBounds'][0][0]-2,model['worldBounds'][0][2]-2,model['worldBounds'][1][0]+2,model['worldBounds'][1][2]+2]);b=next(b for b,_,_ in forms if b['uid']==UID);foundation=f.foundation_context(np.asarray(model['triangles']),tri,Polygon(b['rings'][0],b['rings'][1:]));save(DOC/'foundation.json',{'uid':UID,'sourceSHA256':model['sourceSHA256'],'foundation':foundation,'installationApproved':False})
 refs=[ref(p) for p in [Path(__file__),PRIOR/'result.json',original,LOCAL/'original-model.json.gz',LOCAL/'current-drawn-ground.json.gz',LOCAL/'current-terrain.json.gz',DOC/'clearance.json',DOC/'crossing-input.json',DOC/'crossings.json',DOC/'foundation.json']];crossings=read(DOC/'crossings.json')
 for report in (clearance,crossings):refs.extend({'path':p,'sha256':h} for p,h in report['inputHashes'].items())
 refs.extend(ref(ROOT/'3d-viewer'/url) for _,_,url in forms);refs=list({r['path']:r for r in refs}.values());allwalls=crossings['rows'][0]['diagnostic']['allFailedSamplesAreExactVerticalWallCrossings'];payload={'uid':UID,'sourceSHA256':model['sourceSHA256'],'manifestSHA256':models['manifestSHA256'],'evidenceRefs':refs};stage='fresh-current-original-wall-ground-crossings-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
 result={**payload,'jobId':jid,'batch':BATCH,'allFailedSamplesAreExactVerticalWallCrossings':allwalls,'rawClearance':record,'foundation':foundation,'newlyInstalled':0,'publication':False,'acceptanceGranted':False,'modelGeometryChanges':0,'terrainGeometryChanges':0,'aiGeometryModelling':False,'scriptExternalAICalls':0,'qualification':'Fresh actual rendered current-ground diagnosis only, preserving raw numeric clearance failure. No acceptance rule or source geometry changed. A future demonstrated wall-versus-visible-surface correction still needs full original identity/loader/neighbour/browser/publication checks.'}
 with connect() as c:
  c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
  for r in refs:assert ref(ROOT/r['path'])==r
  assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
 save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'neonVerified':True,'allExactVerticalWalls':allwalls,'foundation':foundation}),flush=True)
def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists() and not LOCAL.exists();claim=reservations.claim('codex-ocean-current-walls-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
