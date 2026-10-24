"""UNEXECUTED saved-input restoration feasibility; no terrain constructor/acceptance."""
from pathlib import Path
import ast,json,sys,time,uuid,subprocess
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
from upton_geometry_bound_inherited_overlap_replay_draft_v1_20261012 import ref,check,module,CURRENT,UIDS,FOREIGN,FREEZER
from upton_captured_ground_tuple_representation_v1_20261012 import adapt_captured_ground
from upton_parent_tin_regression_bookkeeping_v1_20261012 import MODES,sha,triangles
from upton_six_basic_preserved_ground_feasibility_v1_20261012 import polygon_masks,projected_mask,area,nonzero,masked_current_pair
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-six-basic-saved-current-ground-feasibility-v1-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LEASE=LOCAL/'reservation.json'
CAP=BASE/'government-xl-upton-whole-parent-current-domain-capture-v2-20261012';RUNTIME=BASE/'government-xl-upton-three-original-complete-current-runtime-capture-v4-20261012';AUD=BASE/'government-xl-upton-actual-candidate-clearance-measured-overlap-v2-20261012';FINITE=BASE/'government-xl-upton-three-original-complete-current-finite-ground-v5-20261012';RAW=BASE/'government-xl-upton-three-original-qualified-candidate-raw-physical-v3-20261012';NOM=BASE/'government-xl-upton-original-tin-current-ring-join-nomination-v2-20261012'
FOLDERS=[CAP,RUNTIME,AUD,FINITE,RAW,NOM];BASIC=[254809,254810,254813,254815,255022,255024];FIELDS=['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']
def code_paths(entry=None):
 roots=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',HERE.parent/'assembly-support-review'];seen=set();todo=[Path(entry or __file__),FREEZER]
 while todo:
  p=todo.pop().resolve()
  if p in seen:continue
  seen.add(p)
  for n in ast.walk(ast.parse(p.read_text())):
   names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
   for name in names:
    for root in roots:
     q=root/(name.replace('.','/')+'.py')
     if q.is_file():todo.append(q)
 return sorted(seen)
def load_inputs():
 captured=read(CAP/'whole-domain-current-actors.json.gz');original=read(RUNTIME/'original-full-source-root-context.json.gz');proof=read(AUD/'complete-candidate-clearance.json.gz');census=read(FINITE/'diagnostic.json.gz')
 row=read(CAP/'whole-domain-actual-parent-attribution.json.gz')['rows'][0]
 ground,representation=adapt_captured_ground(row,expected_faces=9214,expected_ground_sha='b4916dac0a7c911a5b20e7dde729fa9a99fca63fa01896db8380523e6158670a',expected_source_counts=[('3d-viewer/city/data/terrain.json',32),('3d-viewer/city/data/government-native-79882-0.json',9182)])
 assert sha(ground)==proof['currentGroundSHA256']and captured['startEndAllInputsVerified'];worlds=[]
 for r in captured['rows']:
  o=next(x for x in original['rows']if x['uid']==r['uid']);p=next(x for x in proof['actors']if x['uid']==r['uid']);c=next(x for x in census['actors']if x['uid']==r['uid']);idx=np.asarray(r['completeOriginalIndex'],np.uint32).reshape(-1,3)
  ws=[triangles(o['completeOriginalBinary64WorldTriangles'])]+[triangles(np.asarray(r[k],float).reshape(-1,3)[idx])for k in FIELDS]
  assert o['sourceSHA256']==r['sourceSHA256']==c['sourceSHA256']and len(ws[0])==len(idx)and sha(ws[0])==o['completeOriginalWorldSHA256']
  for mode,w in zip(MODES,ws):
   prior=next(x for x in p['worlds']if x['mode']==mode);assert prior['wholeWorldSHA256']==sha(w)and prior['completeFaces']==len(w);worlds.append((r['uid'],mode,w,c['originalBodyCensus'],prior))
 assert [r['uid']for r in captured['rows']]==UIDS[:3]and sum(len(w)for _,m,w,_,_ in worlds if m=='original')==13704
 basic=[next(r for r in captured['basicContextRows']if r['currentForm']['objectId']==i)for i in BASIC];assert len({r['currentForm']['parent']for r in basic})==6
 assert sum(len(r['index'])//3 for r in basic)==280
 return ground,representation,worlds,basic,row

def schema_only():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['inputRefs']+pins['codeRefs']:check(q)
 for folder in FOLDERS:assert ref(folder/'result.json')in pins['inputRefs']
 ground,rep,worlds,basic,row=load_inputs();assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
 return dict(passed=True,caller=ref(Path(__file__)),fullCurrentDrawnGround=9214,completeOwnedFaces=13704,labelledWorldRows=len(worlds),sixDistinctParentWays=6,completeBasicFaces=280,representation=rep,noDBLeaseOrFiniteMath=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic();refs=[ref(p)for p in code_paths()]+[ref(PROPOSAL/n)for n in ['METHOD.md','draft-pins.json','schema-preflight.json','helper-validation.json']]
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic();print(json.dumps(dict(heartbeat=True)),flush=True)
 schema_only();v=read(PROPOSAL/'helper-validation.json');assert v['passedTests']==16 and v['failedTests']==0 and v['exitCode']==0
 for q in v['executedCodeRefs']+[v['actualLog']]:check(q);refs.append(q)
 assert ref(HERE/'upton_six_basic_preserved_ground_feasibility_v1_20261012.py')in v['executedCodeRefs']and ref(HERE/'test_upton_six_basic_preserved_ground_feasibility_v1_20261012.py')in v['executedCodeRefs']
 for folder in FOLDERS:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for q in r['evidenceRefs']+[ref(folder/'result.json')]:check(q);refs.append(q);pulse()
 refs+=read(PROPOSAL/'draft-pins.json')['inputRefs']
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(True)
 fence();ground,rep,worlds,basic,attribution=load_inputs();DOC.mkdir(parents=True);masks=[]
 for r in basic:
  f=r['currentForm'];assert len(f['rings'])==1;part=[]
  for i,m in enumerate(polygon_masks(f['rings'][0])):part.append((m,dict(kind='exactCurrentSingleRingEar',ring=0,ear=i)))
  pos=np.asarray(r['position'],float).reshape(-1,3);idx=np.asarray(r['index'],np.uint32).reshape(-1,3);zero=[]
  for i,t in enumerate(pos[idx]):
   m=projected_mask(t)
   if area(m)==0:zero.append(i)
   else:part.append((m,dict(kind='actualIndexedBasicFacetProjection',face=i)))
  unique={}
  for m,origin in part:
   key=tuple(sorted(map(tuple,m)));unique.setdefault(key,dict(mask=m,origins=[]))['origins'].append(origin)
  masks.append(dict(uid=r['uid'],currentForm=f,completeActualBasicFacets=len(idx),wholeUnusedPositionVertices=len(pos),projectedCollapsedBasicFaceIDs=zero,exactMasks=[dict(exactXZ=[[str(v)for v in p]for p in m['mask']],origins=m['origins'])for m in unique.values()],basicArithmeticMode='capturedConstructorFloat32World'))
 save(DOC/'complete-six-current-protection-masks.json.gz',dict(rows=masks,noTerrainGeometryCreated=True));results=[];cache={};gxz=ground[:,:,[0,2]];glo=gxz.min(1);ghi=gxz.max(1)
 for uid,mode,w,census,prior in worlds:
  sxz=w[:,:,[0,2]];slo=sxz.min(1);shi=sxz.max(1);body={i:k for k,ids in enumerate(census['sharedEdgeConnectedComponents'])for i in ids};actor=[]
  for b in masks:
   completed=[]
   for mi,m in enumerate(b['exactMasks']):
    mask=[[__import__('fractions').Fraction(v)for v in p]for p in m['exactXZ']];bounds=np.asarray([[float(v)for v in p]for p in mask]);lo=bounds.min(0);hi=bounds.max(0)
    si=np.flatnonzero(np.all(shi>=lo,1)&np.all(slo<=hi,1));gi=np.flatnonzero(np.all(ghi>=lo,1)&np.all(glo<=hi,1));pairs=[]
    for i in si:
     cand=gi[np.all(ghi[gi]>=slo[i],1)&np.all(glo[gi]<=shi[i],1)]
     for j in cand:
      key=(sha(w[i]),sha(ground[j]),tuple(map(tuple,mask)))
      if key not in cache:cache[key]=masked_current_pair(w[i],ground[j],mask)
      q=cache[key]
      if not q.get('closedMaskedProjectionDisjoint'):pairs.append(dict(sourceFace=int(i),originalBody=body.get(int(i)),currentGroundFace=int(j),proof=q))
      pulse()
    completed.append(dict(mask=mi,allClosedBoundsSelectedSourceFaceIDs=si.tolist(),strictBoundsOutsideSourceFaceIDs=np.setdiff1d(np.arange(len(w)),si).tolist(),allClosedBoundsSelectedCurrentGroundFaceIDs=gi.tolist(),allExactPairs=pairs))
   actor.append(dict(basicUID=b['uid'],masks=completed));save(LOCAL/(uid.replace('/','-').replace(':','-')+'-'+mode+'-progress.json.gz'),dict(completeActor=False,completedBasicActors=actor,wholeWorldSHA256=sha(w),groundSHA256=sha(ground)));pulse(True)
  failures=[dict(basicUID=b['basicUID'],mask=m['mask'],**p)for b in actor for m in b['masks']for p in m['allExactPairs']if p['proof'].get('violatesExistingOrdinaryBound')]
  results.append(dict(uid=uid,mode=mode,wholeWorldSHA256=sha(w),completeFaces=len(w),sourceOriginalZeroFaceIDs=census['exactNonrenderingOriginalFaces'],exactCurrentWorldZeroFaceIDs=[i for i,t in enumerate(w)if not nonzero(t)],priorCandidateOrdinaryProofReusedByReference=ref(AUD/'complete-candidate-clearance.json.gz'),completeSixActorMasks=actor,actualOrdinaryRestorationConflictWitnesses=failures,restorationFamilyHasConflict=bool(failures),coverageRootRoleOrAcceptanceCredit=False));print(json.dumps(dict(uid=uid,mode=mode,restorationConflicts=len(failures))),flush=True)
 save(DOC/'diagnostic.json.gz',dict(rows=results,groundRepresentation=rep,currentGroundSourceAttribution=attribution['completeAttributedSources'],groundSHA256=sha(ground),completeCurrentGroundFaces=len(ground),rawSixUpperGapFailures=ref(RAW/'neighbour-checks.json'),allCurrentRawSurfaceLayersRetained=True,noTerrainConstructed=True,noPermanentSourceCorruptionInference=True,physicalAccepted=False,newlyInstalled=0))
 refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()]+[ref(p)for p in LOCAL.glob('*progress.json.gz')];fence();module(FREEZER,'upton_six_saved_ground_freezer').freeze(BATCH,'saved-six-basic-current-ground-restoration-feasibility',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=UIDS[:3],currentManifestSHA256=CURRENT,sourceOnly=True,newlyInstalled=0,terrainGeometryChanges=0,physicalAccepted=False))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--check-saved-restoration-feasibility-only'in sys.argv and not DOC.exists()and not LOCAL.exists();resources=['building:'+u for u in UIDS+[FOREIGN]]+['terrain-patch:'+u for u in UIDS+[FOREIGN]]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-six-current-ground-feasibility-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
