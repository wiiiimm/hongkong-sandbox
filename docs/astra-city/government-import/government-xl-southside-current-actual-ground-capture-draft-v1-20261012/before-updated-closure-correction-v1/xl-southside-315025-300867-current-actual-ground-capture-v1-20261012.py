"""DRAFT: fresh unchanged Southside/station four-stream current ground capture only.
Historical identity and 19 source support holds are retained without current credit.
Preflight performs no database access, lease claim or production JS import.
"""
import copy,importlib.util,json,subprocess,sys,uuid,types
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BASE=ROOT/'docs/astra-city/government-import'
DRAFT=BASE/'government-xl-southside-current-actual-ground-capture-draft-v1-20261012'
CONTRACT=DRAFT/'input-contract.json';METHOD=DRAFT/'METHOD.md'
BATCH='government-xl-southside-315025-300867-current-actual-ground-capture-v1-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
JS=HERE/'xl-southside-315025-300867-current-actual-ground-geometry-v1-20261012.mjs'
UIDS=['landsd/315025:0','landsd/300867:0'];MANIFEST='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
HELPERS=['run.py','exact_packed_world_geometry_20261009.py','exact_packed_world_bounds_v3_20261010.py','xl-final-script-pass.py','literal_production_module_dependency_closure_20261010.mjs','actual_float32_model_matrix_bounds_20261011.mjs','current_geometry_capture_preflight_20261011.mjs','xl-popcorn-source-investigations-checkpoints-20261009.py']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,path):
 s=importlib.util.spec_from_file_location(name,HERE/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def imported_local_files(*extras):
 queue=list(sys.modules.values())+list(extras);seen=set();files=set()
 while queue:
  m=queue.pop()
  if not isinstance(m,types.ModuleType)or id(m)in seen:continue
  seen.add(id(m));name=getattr(m,'__file__',None)
  if not name:continue
  p=Path(name).resolve()
  if ROOT not in p.parents or not p.is_file():continue
  files.add(p);queue.extend(v for v in vars(m).values()if isinstance(v,types.ModuleType))
 return sorted(files)

def preflight():
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==MANIFEST
 contract=read(CONTRACT);assert contract['manifestSHA256']==MANIFEST and contract['completeCurrentNativeActors']==6649 and not contract['currentAcceptance']
 assert [r['uid']for r in contract['sourceActors']]==UIDS
 refs=[Path(__file__),JS,CONTRACT,METHOD]+[HERE/n for n in HELPERS]+[HERE.parent/'shared-modelling'/n for n in ['db.py','jobs.py','reservations.py']]
 for pin in [contract['sourceSelection']]+contract['historicalReceipts']+contract['historicalIdentityDirectRefs']+contract['historicalContextPins']:
  p=ROOT/pin['path'];assert ref(p)==pin;refs.append(p)
 historical=[read(ROOT/p['path'])for p in contract['historicalReceipts']]
 assert historical[0]['jobId']=='fed92957487a3da510ea33fa392594489f6534953aa820d520b2c18bc57d96f5' and historical[0]['identityAccepted'] and not historical[0]['physicalAccepted']
 assert historical[0]['rawRelatedStationOverlapRetained']==contract['historicalOnlyObligations']['rawRelatedStationOverlapRetained']
 assert historical[1]['completeOriginalComponents']==208 and historical[1]['unattachedOriginalComponents']==19 and not historical[1]['supportAccepted']
 assert historical[2]['unresolvedOriginalComponents']==19 and historical[2]['completeCoordinateBandPositiveComponents']==0
 source=read(ROOT/contract['sourceSelection']['path']);rows=[];originals={};positions={}
 for actor in contract['sourceActors']:
  matches=[r for r in source['rows']if r['uid']==actor['uid']];assert len(matches)==1;row=copy.deepcopy(matches[0]);entry=row['candidate']['entry'];n=actor['completeFaces'];uid=actor['uid']
  assert row['sourceSHA256']==actor['sourceSHA256']==entry['sha256'] and row['modelId']==actor['modelId']
  assert entry==actor['originalCandidateEntry'] and row['native']==actor['originalNative'] and entry['uid']==uid and entry['buildingCSUID']==actor['csuid']
  assert entry['triangles']==row['native']['model']['triangles']==n and entry['rootTranslation']==[-834500,0,816500]
  asset=ROOT/row['candidate']['path'];assert ref(asset)==actor['asset'];raw=asset.read_bytes();refs.append(asset)
  originals[uid]=decode_original_world_triangles(raw);assert originals[uid].shape==(n,3,3)and np.isfinite(originals[uid]).all();positions[uid]=packed_world_bounds(raw)
  row['historicalSourceFormVerbatim']=copy.deepcopy(row['source']);row['triangles']=n;rows.append(row)
 bounds=[p['originalWholeSourceBounds']for p in positions.values()];region=[min(b[0][0]for b in bounds)-4,min(b[0][2]for b in bounds)-4,max(b[1][0]for b in bounds)+4,max(b[1][2]for b in bounds)+4]
 final=module('southside_current_forms','xl-final-script-pass.py');forms=final.load_forms(region);assert len(forms)==len({f['uid']for f,_,_ in forms});by={f['uid']:(f,t)for f,_,t in forms}
 for row,actor in zip(rows,contract['sourceActors']):
  assert row['uid']in by;f,t=by[row['uid']];assert f['buildingCSUID']==actor['csuid'] and f['objectId']==int(row['uid'].split('/')[1].split(':')[0])
  row['source']=dict(building=f,tile=t,tileSHA256=digest((ROOT/'3d-viewer'/t).read_bytes()))
 tiles={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms};catalogues=[];native=[]
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;catalogues.append(ref(p));native.extend(read(p)['models'])
 assert len(native)==len({r['uid']for r in native})==6649 and not set(UIDS)&{r['uid']for r in native}
 freezer=module('southside_capture_freezer_preflight','xl-popcorn-source-investigations-checkpoints-20261009.py');refs.extend(imported_local_files(final,freezer));pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
 resources=sorted(set(['building:'+u for u in UIDS]+[('building:'+f['uid'])if f['uid'].startswith('landsd/')else('source-form:'+f['uid'])for f,_,_ in forms]+['terrain-patch:'+u for u in UIDS]))
 assert manifest.read_bytes()==before
 return before,contract,historical,refs,pins,rows,originals,positions,region,forms,tiles,catalogues,resources

def main():
 state=preflight()
 if '--preflight-only'in sys.argv:
  print(json.dumps(dict(noWorker=True,noDB=True,noLease=True,manifestSHA256=MANIFEST,currentNativeActors=6649,completeCurrentForms=len(state[9]),canonicalResources=state[-1],sourceFaces={a['uid']:a['completeFaces']for a in state[1]['sourceActors']},historicalIdentityOnly=True,unresolvedHistoricalSourceComponents=19,currentAcceptance=False)),flush=True);return
 assert not DOC.exists(),'Immutable completed/failed attempt'
 if '--owned'not in sys.argv:
  assert not LOCAL.exists();claim=reservations.claim('southside-current-actual-ground-'+str(uuid.uuid4()),state[-1],batch=BATCH,ttl=3600);assert claim['ok'],claim
  save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
  subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True);return
 before,contract,historical,refs,pins,rows,originals,positions,region,forms,tiles,catalogues,resources=state;lease=read(LEASE);assert lease['resources']==resources and reservations.owns(lease)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for receipt in historical:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for row in rows:
   n=row['native'];found=c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,n['cacheKey'])).fetchall();assert found==[(n['resultSha'],)]
 DOC.mkdir();(DOC/'captured-manifest.json').write_bytes(before)
 save(DOC/'selection.json.gz',dict(batch=BATCH,manifestSHA256=MANIFEST,rows=rows,currentIdentityAccepted=False))
 save(DOC/'historical-obligations-verbatim.json',dict(receipts=historical,obligations=contract['historicalOnlyObligations'],historicalOnly=True,currentApprovalTransferred=False))
 save(DOC/'all-current-catalogues.json',dict(rows=catalogues,completeNativeActors=6649))
 save(DOC/'capture-inputs.json.gz',dict(rows=rows,completeCurrentForms=[f for f,_,_ in forms],completeCurrentFormBounds=region,neighbourTileHashes=tiles,completeCurrentCatalogueRefs=catalogues,inputHashes=pins,manifestSHA256=MANIFEST,canonicalResources=resources,currentAcceptance=False,physicalAccepted=False,installationApproved=False))
 captures={};streams={}
 for row in rows:
  uid=row['uid'];slug=uid.split('/')[1].replace(':','-');save(DOC/('whole-original-position-proof-'+slug+'.json'),positions[uid])
  status=subprocess.run(['node',str(JS),uid],cwd=ROOT,capture_output=True,text=True);save(DOC/('export-'+slug+'-log.json'),dict(exitCode=status.returncode,stdout=status.stdout,stderr=status.stderr));assert status.returncode==0,status.stderr
  capture=read(DOC/('complete-current-actual-source-and-ground-'+slug+'.json.gz'));n=row['triangles'];assert capture['uid']==uid and capture['sourceSHA256']==row['sourceSHA256'] and capture['entry']==row['candidate']['entry']and capture['completeFaces']==n and capture['startAndEndInputsVerified']and capture['completeOriginalPOSITIONProof']==positions[uid]
  index=np.asarray(capture['completeOriginalIndex'],dtype=np.int64).reshape(-1,3);worlds={'providerOriginal':originals[uid]}
  for mode,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(capture[key],dtype='<f8').reshape(-1,3)[index]
  assert all(w.shape==(n,3,3)and np.isfinite(w).all()for w in worlds.values())
  ground=np.asarray(capture['currentDrawnGround']['completeRegionalPosition'],dtype='<f8').reshape(-1,3,3);assert len(ground)==capture['currentDrawnGround']['completeRegionalFaces']and np.isfinite(ground).all()and digest(ground.tobytes())==capture['currentDrawnGround']['worldTriangleSHA256']
  streams[uid]=dict(uid=uid,sourceSHA256=row['sourceSHA256'],completeWorldStreams={m:dict(completeFaces=n,completeWorldTriangleSHA256=digest(w.astype('<f8').tobytes()),completeWorldTriangles=w.tolist())for m,w in worlds.items()},completeDrawnGround=ground.tolist(),completeDrawnGroundSHA256=digest(ground.tobytes()),currentAcceptance=False,physicalAccepted=False,installationApproved=False)
  captures[uid]=capture;refs.extend(ROOT/p for p in capture['inputHashes'])
 assert captures[UIDS[0]]['completeRecursiveLoaderModuleClosure']==captures[UIDS[1]]['completeRecursiveLoaderModuleClosure'] and captures[UIDS[0]]['completeRecursiveTerrainModuleClosure']==captures[UIDS[1]]['completeRecursiveTerrainModuleClosure']
 save(DOC/'complete-two-actor-four-stream-ground-inputs.json.gz',dict(rows=streams,allSlopesAndZeroProjectionGroundRetained=True,noHistoricalRuntimeProofTransfer=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False))
 assert reservations.owns(lease)and(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 for capture in captures.values():
  for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 for t,h in tiles.items():assert digest((ROOT/'3d-viewer'/t).read_bytes())==h
 for pin in catalogues:assert ref(ROOT/pin['path'])==pin
 refs.extend(p for p in DOC.rglob('*')if p.is_file());freezer=module('southside_capture_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py')
 out=freezer.freeze(BATCH,'southside-fresh-pair-whole-original-four-world-current-ground-no-role-credit',refs,dict(uids=UIDS,completeSourceFaces={r['uid']:r['triangles']for r in rows},currentNativeActors=6649,completeCurrentForms=len(forms),historicalOverlapRetained=contract['historicalOnlyObligations']['rawRelatedStationOverlapRetained'],historicalUnresolvedComponents=19,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
 print(json.dumps(dict(jobId=out['jobId'],currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
