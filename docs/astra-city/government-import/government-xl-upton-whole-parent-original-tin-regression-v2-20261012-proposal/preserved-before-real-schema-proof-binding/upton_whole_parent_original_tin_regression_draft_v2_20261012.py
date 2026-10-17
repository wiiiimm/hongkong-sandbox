"""UNEXECUTED source-only original TIN/current parent finite regression.
No terrain join/candidate, physical acceptance, source edits or root credit.
"""
from pathlib import Path
import ast,importlib.util,json,subprocess,sys,time,uuid,zlib
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from upton_parent_tin_regression_bookkeeping_v1_20261012 import MODES,sha,triangles,closed_face_scope,ground_roi,finite_record,comparison
from upton_captured_ground_tuple_representation_v1_20261012 import adapt_captured_ground
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-upton-whole-parent-original-tin-regression-v2-20261012'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
CAP=BASE/'government-xl-upton-whole-parent-current-domain-capture-v2-20261012'
OLD=BASE/'government-xl-upton-podiums-untouched-sheet-failures-v1-20261012'
FINITE=BASE/'government-xl-upton-three-original-complete-current-finite-ground-v5-20261012'
SHEET=HERE/'local/government-xl-50-second-20260913/sheets/11-SW-7A'
METHOD=BASE/(BATCH+'-proposal')/'METHOD.md';PREFLIGHT=METHOD.parent/'unexecuted-schema-pin-check.json'
PRIOR_PROPOSAL=BASE/'government-xl-upton-whole-parent-original-tin-regression-v1-20261012-proposal'
VALIDATION=PRIOR_PROPOSAL/'bookkeeping-validation.json'
REP_VALIDATION=METHOD.parent/'representation-validation.json'
REP_HELPER=HERE/'upton_captured_ground_tuple_representation_v1_20261012.py';REP_TEST=HERE/'test_upton_captured_ground_tuple_representation_v1_20261012.py'
FAILED=PRIOR_PROPOSAL/'failed-attempt'
HELPER=HERE/'upton_parent_tin_regression_bookkeeping_v1_20261012.py';TEST=HERE/'test_upton_parent_tin_regression_bookkeeping_v1_20261012.py'
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
UIDS=['landsd/338946:0','landsd/12728:0','landsd/12662:0'];NATIVE='landsd/79882:0';FOREIGN='landsd/254809:0'
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(pin):
 p=ROOT/pin['path'];assert ref(p)==pin,pin;return p
def module(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def code_paths():
 folders=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',ROOT/'docs/astra-city/mui-wo-buildings/review',HERE.parent/'assembly-support-review']
 todo=[Path(__file__),FREEZER,HERE/'pending-context.py'];seen=set()
 while todo:
  p=todo.pop().resolve()
  if p in seen:continue
  seen.add(p)
  for n in ast.walk(ast.parse(p.read_text())):
   names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
   for name in names:
    for folder in folders:
     q=folder/(name.replace('.','/')+'.py')
     if q.is_file():todo.append(q)
 return sorted(seen)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pre=read(PREFLIGHT);assert pre['passed']and pre['caller']==ref(Path(__file__))and pre['method']==ref(METHOD)
 v=read(VALIDATION);assert v['exitCode']==0 and v['passedTests']==13 and v['failedTests']==0 and v['helper']==ref(HELPER)and v['test']==ref(TEST);check(v['log'])
 rv=read(REP_VALIDATION);assert rv['exitCode']==0 and rv['passedTests']==13 and rv['failedTests']==0 and rv['helper']==ref(REP_HELPER)and rv['test']==ref(REP_TEST);check(rv['log'])
 refs=[ref(p)for p in code_paths()]+[ref(METHOD),ref(PREFLIGHT),ref(VALIDATION),ref(TEST),v['log'],ref(REP_VALIDATION),ref(REP_TEST),rv['log']]+[ref(p)for p in sorted(FAILED.iterdir())if p.is_file()]
 for folder,jid,expected_sha in[(CAP,'69916bb92558c08c4c5c1838f7c34f963f0e888b7ef14cb489d995ab9bc36727','91d90929b7a8f3694239ba7d5ec97ab5bc1018d52e8d205c08542a820735f120'),(OLD,'5cbc9ae94ef9766bce923334408dcfbf55abc75bcabe8c8df1628fe404ce92fd',None),(FINITE,'7b2c30c7df3cca9f42d7d3e8cee90f98525d0939c49ad396d900a256d8f4f325',None)]:
  receipt=read(folder/'result.json');assert receipt['jobId']==jid
  if expected_sha:assert ref(folder/'result.json')['sha256']==expected_sha
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',receipt)
  for pin in receipt['evidenceRefs']+[ref(folder/'result.json')]:check(pin);refs.append(pin);pulse()
 kernel_refs=[ref(HERE/n)for n in ['exact_original_face_conservative_clearance_v5_20261010.py','exact_original_paired_finite_clearance_v3_20261011.py','exact_original_paired_finite_clearance_v2_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_original_triangle_pair_column_gap_20261010.py','exact_original_closed_projection_intersection_20261010.py']]
 old_receipt=read(OLD/'result.json');oldpins={p['path']:p['sha256']for p in old_receipt['evidenceRefs']}
 for pin in kernel_refs:assert oldpins[pin['path']]==pin['sha256']
 refs+=kernel_refs
 def fence():
  for pin in refs:check(pin);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(True)
 fence();inp=read(CAP/'input.json.gz');attrs=read(CAP/'whole-domain-current-actors.json.gz');terrain=read(CAP/'whole-domain-actual-parent-attribution.json.gz')
 assert inp['expectedNativeCount']==6649 and inp['currentManifest']['sha256']==CURRENT and inp['rederivedCoarseCells']==[457,449,460,451]
 assert inp['domain']==[-2477.5,-37.5,-2267.5,102.5]and len(inp['basicRows'])==len(attrs['basicContextRows'])==1911
 assert [r['uid']for r in attrs['rows']]==UIDS and [r['uid']for r in attrs['nativeContextRows']]==[NATIVE]
 assert attrs['startEndAllInputsVerified']and terrain['startEndAllInputsVerified'];assert len(terrain['rows'])==1
 tr=terrain['rows'][0];assert tr['uid']=='whole-parent-domain'and tr['completeAttributionMultisetMatchedActual']
 current,current_representation=adapt_captured_ground(tr,expected_faces=9214,expected_ground_sha='b4916dac0a7c911a5b20e7dde729fa9a99fca63fa01896db8380523e6158670a',expected_source_counts=[('3d-viewer/city/data/terrain.json',32),('3d-viewer/city/data/government-native-79882-0.json',9182)]);assert len(current)==9214
 # Re-derive the complete future affected domain from the current coarse parent,
 # without generating a patch or changing its retained source semantics.
 base=read(ROOT/'3d-viewer/city/data/terrain.json');g=base['meta']['georef'];cells=inp['rederivedCoarseCells']
 box=[g['bE']+cells[0]*g['aE']-834500,816500-(g['bN']+cells[1]*g['aN']),g['bE']+cells[2]*g['aE']-834500,816500-(g['bN']+cells[3]*g['aN'])];assert box==inp['domain']
 assert ref(check(inp['retainedParent']))==inp['retainedParent']and inp['retainedParentExactCurrentData']['coarseCells']==[457,449,459,451]
 recovery=read(SHEET/'recovery.json');source=recovery['source'];assert source['sheet']=='11-SW-7A'and source['terrainGeometryIncluded']
 directory=SHEET/'directory/zip-directory.bin';assert ref(directory)['sha256']==source['directorySHA256']=='69d5f9f3635581f732caae3e71ce503c4dd8f50e21053e0042795cd5b78d01aa'
 refs+=[ref(SHEET/'recovery.json'),ref(directory)];gltfs=[]
 for e in source['entries']:
  if not e['name'].startswith('TERRAIN(TB)/'):continue
  p=SHEET/'terrain'/e['name'];raw=p.read_bytes();assert len(raw)==e['bytes']and digest(raw)==e['sha256']and zlib.crc32(raw)&0xffffffff==e['sourceCRC32'];refs.append(ref(p))
  if p.suffix=='.gltf':gltfs.append(p)
 assert len(gltfs)==1;full=triangles(module(HERE/'pending-context.py','upton_regression_unfiltered_source').triangles(gltfs[0]));assert len(full)==122721 and sha(full)=='3ace7f401040b2109fd196c603f506d42f0238292742e528c3c46f786b2d93e6'
 old=read(OLD/'source-only-failure-comparison.json.gz');reusable={}
 for row in old['rows']:
  for q in row['sourceOnlyFailureComparison']:
   key=(q['coarse']['sourceFaceSHA256'],q['coarse']['completeCurrentGroundSHA256'])
   if key in reusable:
    for field in ['coarse','paired','projectionCovered','ordinaryBoundProved']:assert reusable[key][field]==q[field]
   else:reusable[key]=q
 DOC.mkdir(parents=True);save(DOC/'captured-ground-representation-proof.json',current_representation);save(DOC/'untouched-source-tin.json.gz',dict(completeUnfilteredFacets=122721,completeSourceSHA256=sha(full),allOriginalTriplets=full.tolist(),noSlopeAreaDegenerateFilter=True))
 output=[];cache={};affected_basic=[];gov_sources={r['uid']:r for r in inp['ownedRows']+inp['nativeRows']};basic_inputs={r['uid']:r for r in inp['basicRows']}
 def assess_actor(uid,role,worlds,bounds,census_by_mode):
  lo=np.min([np.asarray(b)[0]for b in bounds.values()],0)-1;hi=np.max([np.asarray(b)[1]for b in bounds.values()],0)+1;ids,original=ground_roi(full,[lo,hi]);gh=sha(original)
  save(DOC/(uid.replace('/','-').replace(':','-')+'-source-roi.json.gz'),dict(wholeSourceFacets=122721,selectedWholeSourceFaceIDs=ids.tolist(),selectedSourceTriplets=original.tolist(),strictClosedBoundsDisjointSourceFaceCount=122721-len(ids),allUnusedBounds=bounds,sourceROIHash=gh))
  labelled=[];unique={}
  for mode,world in worlds.items():
   world=triangles(world);scope=closed_face_scope(world,box);wh=sha(world)
   # Government actors retain every facet. BASIC outside facets are explicitly
   # accounted as unchanged-domain-disjoint; no full BASIC footprint shortcut.
   selected=list(range(len(world)))if role!='current-basic-constructor-context'else scope['selectedFaceIDs']
   if role!='current-basic-constructor-context':assert len(selected)==len(world)
   identity=(wh,sha(current),gh,tuple(selected));reused=identity in unique
   if not reused:
    rows=[]
    for i in selected:
     face=world[i];record=[]
     for kind,ground in [('currentCapturedUnion',current),('originalUnfilteredTIN',original)]:
      key=(sha(face),sha(ground));saved=cache.get(key)
      if saved is None:
       historic=reusable.get(key)if kind=='originalUnfilteredTIN'else None;saved=finite_record(face,ground,historic);cache[key]=saved
      record.append(saved)
     rows.append(dict(face=i,current=record[0],originalTIN=record[1],comparison=comparison(*record,scope['wholeFaceWithinCapturedDomain'][i])))
     pulse()
     if len(rows)%64==0:
      save(LOCAL/'progress'/uid.replace('/','-').replace(':','-')/(mode+'.json.gz'),dict(complete=False,wholeWorldSHA256=wh,completeCurrentGroundSHA256=sha(current),completeOriginalROISHA256=gh,processedFaces=len(rows),expectedFaces=len(selected),rows=rows));print(json.dumps(dict(uid=uid,mode=mode,processedFaces=len(rows),expectedFaces=len(selected))),flush=True)
    unique[identity]=dict(rows=rows,currentUnprovedOriginalTINClear=[r['face']for r in rows if r['comparison']['currentUnprovedOriginalTINClear']],currentClearOriginalTINUnproved=[r['face']for r in rows if r['comparison']['currentClearOriginalTINUnproved']],currentUncovered=[r['face']for r in rows if not r['current']['projectionCovered']],sourceTINUncovered=[r['face']for r in rows if not r['originalTIN']['projectionCovered']],bothOrdinaryUnproved=[r['face']for r in rows if r['comparison']['bothOrdinaryUnproved']])
   labelled.append(dict(mode=mode,wholeWorldSHA256=wh,wholeCurrentGroundSHA256=sha(current),wholeOriginalROISHA256=gh,completeFaces=len(world),fullClosedDomainFaceScope=scope,selectedFaceIDs=selected,allWholeFacetComparisons=unique[identity],exactFullTupleReuse=reused,bodyCensus=census_by_mode.get(mode),noRootGradeOrRoleCredit=True))
   pulse(True)
  return dict(uid=uid,role=role,sourceROIHash=gh,sourceROIFaceIDs=ids.tolist(),worlds=labelled,wholeSourcePreserved=True)
 for row in attrs['rows']+attrs['nativeContextRows']:
  uid=row['uid'];s=gov_sources[uid];raw=check(dict(path=s['path'],sha256=row['sourceSHA256'])).read_bytes();original=triangles(decode_original_world_triangles(raw));proof=row['completeOriginalPOSITIONProof'];assert sha(original)==proof['worldTrianglesSHA256']
  index=np.asarray(row['completeOriginalIndex'],dtype=np.int64).reshape(-1,3);assert len(index)==len(original)==s['entry']['triangles'];worlds={'original':original};bounds={'original':proof['originalWholeSourceBounds']};topologies={'original':census(original,list(range(len(original))))}
  for mode,key in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
   vertices=np.asarray(row[key],dtype='<f8').reshape(-1,3);assert len(vertices)==proof['completeOriginalPositionVertices']and index.min()>=0 and index.max()<len(vertices);worlds[mode]=vertices[index];bounds[mode]=[vertices.min(0).tolist(),vertices.max(0).tolist()];topologies[mode]=census(worlds[mode],list(range(len(original))))
  output.append(assess_actor(uid,'owned-original'if uid in UIDS else'installed-native-regression-only',worlds,bounds,topologies));pulse(True)
 assert sum(len(output[i]['worlds'][0]['selectedFaceIDs'])for i in range(3))==13704
 # Captured BASIC rows are production-constructor context, not independently
 # captured model-matrix arithmetic: do not invent original/F32 world labels.
 for row in attrs['basicContextRows']:
  uid=row['uid'];assert row['currentForm']==basic_inputs[uid]['building']and row['geometryConstructorContextOnly']and not row['physicalAccepted'];assert row['identityModelMatrix']==[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
  v=np.asarray(row['position'],dtype='<f8').reshape(-1,3);index=np.asarray(row['index'],dtype=np.int64).reshape(-1,3);assert np.isfinite(v).all()
  if index.size:assert index.min()>=0 and index.max()<len(v)
  world=v[index];scope=closed_face_scope(world,box)
  summary=dict(uid=uid,completeUnusedPositionVertices=len(v),completeFacets=len(world),emptyConstructorReceivesNoPhysicalOrSupportCredit=not bool(len(world)),completeWorldSHA256=sha(world),scope=scope,rawCurrentFormUnchanged=True,notWholeActualDrawOrPhysicalCredit=True)
  if scope['selectedFaceIDs']:summary['affectedComparisons']=assess_actor(uid,'current-basic-constructor-context',{'capturedConstructorFloat32World':world},{'capturedConstructorFloat32World':[v.min(0).tolist(),v.max(0).tolist()]},{})
  affected_basic.append(summary);pulse()
 assert len(affected_basic)==1911 and FOREIGN in{r['uid']for r in affected_basic}
 save(DOC/'diagnostic.json.gz',dict(currentManifest=inp['currentManifest'],wholeDomain=box,coarseCells=cells,wholeSourceTINFacets=122721,wholeSourceTINWorldSHA256=sha(full),wholeCurrentDrawnGroundFacets=9214,wholeCurrentDrawnGroundSHA256=sha(current),actors=output,completeBasicRows=affected_basic,prior335PodiumFailuresRetained=ref(OLD/'source-only-failure-comparison.json.gz'),allHistoricalZeroForeignCrossingRootObligationsRetained=ref(FINITE/'diagnostic.json.gz'),existingOrdinaryLimitM='-1/2',originalTINComparisonNotUntouchedCurrentTerrain=True,sourceOnly=True,physicalAccepted=False,installationApproved=False,gradeRootProved=False,newTerrainJoinConstructed=False,sourceGeometryChanges=0,terrainGeometryChanges=0))
 refs+=[ref(DOC/'diagnostic.json.gz'),ref(DOC/'untouched-source-tin.json.gz'),ref(DOC/'captured-ground-representation-proof.json')];fence()
 module(FREEZER,'upton_regression_freezer').freeze(BATCH,'whole-parent-original-TIN-current-actor-regression-only',[check(p)for p in{(r['path'],r['sha256']):r for r in refs}.values()],dict(uids=UIDS+[NATIVE],sourceOnly=True,physicalAccepted=False,newlyInstalled=0,newTerrainJoinConstructed=False,currentManifest=inp['currentManifest'],completeOwnedFaces=13704,completeBasicContextRows=1911,wholeSourceFacets=122721))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();uids=UIDS+[NATIVE,FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-TIN-regression-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
