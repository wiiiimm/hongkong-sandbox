"""Acquire original terrain only and compare unchanged source faces; no publication."""
import importlib.util,uuid,zipfile
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-unmapped-native-terrain-v1-20261015';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
REC=HERE/'local/government-xl-unmapped-exact-source-recovery-v1-20261015'
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not LOCAL.exists()
 prior=read(BASE/'government-xl-unmapped-whole-context-v1-20261015/result.json');rows=list({r['modelId']:r for r in prior['rows']}.values());resources=['native-model:'+r['sourceKey']for r in rows]
 claim=reservations.claim('unmapped-native-terrain-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();LOCAL.mkdir(parents=True);stage='unchanged-source-native-terrain-diagnostic-v1';jid=jobs.enqueue(BATCH,stage,{'sourceKeys':[r['sourceKey']for r in rows]});job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=3600);assert job and job['id']==jid
  spec=importlib.util.spec_from_file_location('unmapped_native_context',HERE/'xl-final-script-pass.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.s.LOCAL=LOCAL
  stages=read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/input-bindings.json')['stages'];recovered={r['modelId']:r for r in read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows']};bindings=read(BASE/'government-xl-unmapped-two-primary-evidence-v1-20261015/viewer-bindings.json')['rows'];outputs=[];refs=[ref(Path(__file__))]
  for r in rows:
   sheet=stages[r['sourceKey'].split('/')[0]][0];cached=REC/sheet/'directory';directory=read(cached/'result.json');directory['models']=[];folder=LOCAL/sheet;record=f.s.acquire(directory,cached/'zip-directory.bin',folder/'original',include_terrain=True)
   paths=[]
   with zipfile.ZipFile(folder/'original'/(sheet+'.zip'))as z:
    for name in z.namelist():
     if name.startswith('TERRAIN')and name.endswith(('.gltf','.bin')):
      p=folder/'terrain'/f.s.safe(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name));refs.append(ref(p))
      if name.endswith('.gltf'):paths.append(p)
   assert paths;ground=np.concatenate([f.s.terrain_triangles(p)for p in paths]);asset=ROOT/recovered[r['modelId']]['asset']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());bound=next(b for b in bindings if b['modelId']==r['modelId']);building=bound['bindings'][0]['viewerForm'];foundation=f.foundation_context(tri,ground,f.form_polygon(building))
   output={'modelId':r['modelId'],'sourceKey':r['sourceKey'],'sourceSHA256':r['sourceSHA256'],'sheet':sheet,'terrainSource':record,'terrainPaths':[str(p.relative_to(ROOT))for p in paths],'nativeTerrainFaces':len(ground),'foundationDiagnostic':foundation,'installationApproved':False};outputs.append(output);save(DOC/(r['modelId']+'.json'),output);refs.extend([ref(folder/'original/download.json'),ref(cached/'result.json'),ref(cached/'zip-directory.bin'),ref(asset)]);assert reservations.heartbeat(lease)['ok'];print(r['modelId'],foundation,flush=True)
  refs.extend(ref(p)for p in DOC.iterdir()if p.is_file());refs.extend(ref(p)for p in (LOCAL/'terrain-repairs').rglob('*')if p.is_file())
  for p in refs:assert ref(ROOT/p['path'])==p
  result={'jobId':jid,'rows':outputs,'evidenceRefs':refs,'newlyInstalled':0,'sourceGeometryChanges':0,'publicationApproved':False,'qualification':'Original native terrain comparison only; four samples per source face are diagnostic, not continuous acceptance. No live terrain or source elevation changed.'}
  with connect()as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease);assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);print('COMPLETE',jid,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
