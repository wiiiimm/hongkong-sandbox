"""Ocean Walk full fresh current-terrain pass; retain every other component.

No metadata restoration, source/terrain changes, publication or tolerance edits.
"""
import importlib.util,json,subprocess,sys,uuid,traceback
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
from ocean_walk_complete_source_identity import verify_files,POLICY
from terrain_diagnostic_resolution import resolve_global_bottom_warning
BATCH='government-xl-ocean-walk-current-terrain-complete-scope-20261008';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;UID='landsd/81743:0'
SOURCE=ROOT/'docs/astra-city/government-import/government-xl-22-complete-group-official-context-v2-20261008/physical-selection.json.gz'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def frozen():
 row=next(r for r in read(SOURCE)['rows'] if r['uid']==UID);row['currentReview']=None
 final=module('ocean_current_forms','xl-final-script-pass.py');lo,hi=row['native']['model']['worldBounds'];forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
 context={'uid':UID,'sourceSHA256':row['sourceSHA256'],'neighbourTileHashes':{url:digest((ROOT/'3d-viewer'/url).read_bytes()) for _,_,url in forms}}
 return row,context,forms

def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);row,context,forms=frozen();manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifest_path);manifest_sha=digest(manifest_path.read_bytes())
 stage='ocean-walk-current-terrain-complete-footprint-physical-v1';payload={'uid':UID,'sourceSHA256':row['sourceSHA256'],'manifestSHA256':manifest_sha};jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=3600);assert job and job['id']==jid
 try:
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert not c.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=%s',(UID,)).fetchall()
  proof=verify_files(row,context,LOCAL/'identity-current');assert proof['passed'],proof['reasons'];save(DOC/'owned-source-identity.json',proof)
  raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];dest=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);row['candidate']['path']=str(dest.relative_to(ROOT));row['candidate']['entry'].update(footprintScope=UID,suppressesBuildingUids=[])
  assert row['candidate']['entry']['recordedBaseHeight']==4.7 and row['candidate']['entry']['recordedTopHeight']==21.4
  catalogue=read(HERE/'accepted/government-xxl-20260911/catalogue.json');catalogue.update(area=BATCH,models=[row['candidate']['entry']],counts={'packedModels':1});save(LOCAL/'catalogue.json',catalogue);save(LOCAL/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']})
  save(LOCAL/'source-forms.json',{b['uid']:{**row['source'],'building':b} for b in proof['completeGroupForms']})
  save(DOC/'selection.json.gz',{'rows':[row],'batch':BATCH,'manifestSHA256':manifest_sha});save(DOC/'terrain-candidates.json',[]);save(DOC/'terrain.json',{'patches':[],'terrainGeometryChanges':0,'modelGeometryChanges':0})
  native={m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
  assert UID not in native
  save(DOC/'neighbour-inputs.json.gz',{'rows':[{'building':b,'patchIndexes':[],'existingNative':b['uid'] in native or bool(b.get('modelGeometry'))} for b,_,_ in forms],'inputHashes':{str((ROOT/'3d-viewer'/url).relative_to(ROOT)):digest((ROOT/'3d-viewer'/url).read_bytes()) for _,_,url in forms},'candidateIds':[UID],'patches':[]})
  rel=lambda p:str(p.relative_to(ROOT))
  def call(args,allowed=(0,)):
   assert subprocess.run(args,cwd=ROOT).returncode in allowed;assert reservations.owns(lease)
  call(['node',str(HERE/'acceptance-metrics-footprint-scope.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
  call(['node',str(HERE.parent/'building-batch/validate_candidates_footprint_scope.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],(0,1))
  call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),rel(DOC)+'/'])
  geometry=read(LOCAL/'runtime-geometry.json.gz')['rows'];reasons=[];foundation=[]
  if len(geometry)==1:
   g=geometry[0];triangles=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=row['source']['building'];f=module('ocean_foundation','xl-final-script-pass.py').foundation_context(triangles,ground,Polygon(b['rings'][0],b['rings'][1:]));foundation=[{'uid':UID,'sourceSHA256':row['sourceSHA256'],'foundation':f,'strictFoundationAccepted':f['completeTerrainTriangles']==f['triangles'] and not f['fullyBuriedUpwardTriangles'] and f['fullyBuriedAreaFraction']==0}]
  save(DOC/'foundation.json',{'rows':foundation,'untested':not foundation})
  metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');metric=metrics['rows'][0]
  reasons+=module('ocean_numeric_policy','acceptance-policy.py').reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':row['sourceSHA256'],'identityProof':proof['proof']},metric,metrics['profiles']['mobile'])
  if foundation:
   diagnostic=resolve_global_bottom_warning(validation['results'][0],metric,foundation[0]);save(DOC/'diagnostic-resolution.json',diagnostic);reasons+=diagnostic['remaining']
  if not foundation or not foundation[0]['strictFoundationAccepted']:reasons.append('whole-source-foundation')
  if validation['checksPassed']!=1 or validation['loaderAccepted']!=1 or validation['exceptions']:reasons.append('runtime-validation')
  neighbours=read(DOC/'neighbour-checks.json');assert all(not r['reasons'] and r['maxGroundChange']==0 for r in neighbours['rows'])
  native_check=read(DOC/'native-neighbour-checks.json');reasons+=['native-neighbour-regression:'+u for u in set(native_check['blocked'])-set(native_check['resolved'])]
  refs=[ref(p) for p in sorted(DOC.iterdir()) if p.is_file()]+[ref(p) for p in [Path(__file__),HERE/'ocean_walk_complete_source_identity.py',ROOT/'3d-viewer/city/official-model-footprint-scopes-ocean-walk.js',ROOT/'3d-viewer/city/official-model-footprint-scopes.js',LOCAL/'catalogue.json',LOCAL/'source-forms.json',LOCAL/'runtime-geometry.json.gz',SOURCE]]
  refs += [{'path':p,'sha256':sha} for p,sha in metrics['inputHashes'].items()];refs=list({r['path']:r for r in refs}.values())
  result={**payload,'jobId':jid,'batch':BATCH,'evidenceRefs':refs,'reasons':sorted(set(reasons)),'scriptChecksPassed':not reasons,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'terrainGeometryChanges':0,'retainedGroupUids':[b['uid'] for b in proof['completeGroupForms'] if b['uid']!=UID],'scriptExternalAICalls':0,'sourceIdentityReviewUsedAI':True,'aiGeometryModelling':False,'qualification':'Complete footprint context only; no other component is suppressed or exempted from neighbour checks. Every numeric and foundation/runtime gate remains; no browser or installation approval.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   assert digest(manifest_path.read_bytes())==manifest_sha
   for item in refs:assert ref(ROOT/item['path'])==item
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'scriptChecksPassed':not reasons,'reasons':result['reasons'],'neonVerified':True}),flush=True)
 except Exception as e:
  save(DOC/'error.json',{'error':str(e),'traceback':traceback.format_exc(),'publication':False});assert jobs.finish(job,error=str(e));raise
if __name__=='__main__':
 if '--owned' in sys.argv:owned()
 else:
  assert not DOC.exists() and not LOCAL.exists();row,context,forms=frozen();scope={b['uid'] for b,_,_ in forms}
  claim=reservations.claim('codex-ocean-current-'+str(uuid.uuid4()),['building:'+u for u in sorted(scope|{UID})],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
  subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
