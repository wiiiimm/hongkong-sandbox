"""UNEXECUTED private source-preserving TIN/current-ring join nomination.
No live terrain write, original geometry/pose edit, source/root/native approval.
"""
from pathlib import Path
from fractions import Fraction as F
import copy,json,sys,time,uuid,subprocess,hashlib,ast
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations,connect
from upton_original_tin_current_ring_join_nomination_v1_20261012 import split_rectangle,triangulate,nonzero,packed,boundary_edges,nominated_upper_join,protected_core
from upton_parent_tin_regression_bookkeeping_v1_20261012 import sha,closed_face_scope,finite_record
from upton_captured_ground_tuple_representation_v1_20261012 import adapt_captured_ground
from upton_whole_current_facet_protection_v1_20261012 import nominate,exact_overlap_attribution
from upton_six_basic_preserved_ground_feasibility_draft_v1_20261012 import load_inputs as load_saved_worlds
from upton_six_basic_preserved_ground_feasibility_v1_20261012 import projected_mask,area,masked_current_pair
from upton_inherited_overlap_boundary_v1_20261012 import source_attribution
from upton_actual_candidate_clearance_audit_v1_20261012 import measured_projection,candidate_surface,verify_drawn_multiset
from upton_two_original_six_mask_partition_v1_20261012 import partition as partition_regions,mask,interface_edges,same_triplet
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-upton-two-original-whole-current-facet-protection-v3-20261012'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PROPOSAL=BASE/(BATCH+'-proposal');METHOD=PROPOSAL/'METHOD.md';VALIDATION=PROPOSAL/'join-helper-validation.json';PREFLIGHT=PROPOSAL/'unexecuted-schema-pin-check.json'
CAP=BASE/'government-xl-upton-whole-parent-current-domain-capture-v2-20261012'
REG=BASE/'government-xl-upton-whole-parent-original-tin-regression-v2-20261012'
NAT=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v4-20261012'
HELPER=HERE/'upton_whole_current_facet_protection_v1_20261012.py';TEST=HERE/'test_upton_whole_current_facet_protection_v1_20261012.py'
RUNTIME=HERE/'upton_two_original_whole_current_facet_runtime_draft_v3_20261012.mjs'
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
UIDS=['landsd/338946:0','landsd/12728:0'];SECONDARY='landsd/12662:0';NATIVE='landsd/79882:0';FOREIGN='landsd/254809:0'
NINE={'landsd/214971:0':[30,39,50,54,56,57],'landsd/231778:0':[68,73,76]}
DOMAIN=[-2477.5,-37.5,-2267.5,102.5];CELLS=[457,449,460,451]
def ref(p):return {'path':str(p.resolve().relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def exact_records(value):
 if isinstance(value,F):return str(value)
 if isinstance(value,dict):return {k:exact_records(v)for k,v in value.items()}
 if isinstance(value,(list,tuple)):return [exact_records(v)for v in value]
 return value
def check(q):
 p=ROOT/q['path'];assert ref(p)==q,q;return p
def load_module(p,name):
 import importlib.util
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
FEAS=BASE/'government-xl-upton-six-basic-saved-current-ground-feasibility-v1-20261012'
GUARD=BASE/'government-xl-upton-six-basic-existing-guard-samples-full-source-columns-v1-20261012'
MAIN=BASE/'government-xl-upton-main12728-four-world-grade-cap-interfaces-v1-20261012'
RESIDUAL=BASE/'government-xl-upton-746-residual-saved-source-role-reconciliation-v1-20261012'
def schema_only():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 inp=read(CAP/'input.json.gz');attrs=read(CAP/'whole-domain-current-actors.json.gz');at=read(CAP/'whole-domain-actual-parent-attribution.json.gz')
 assert inp['domain']==DOMAIN and inp['rederivedCoarseCells']==CELLS and inp['expectedNativeCount']==6649 and len(attrs['rows'])==3 and len(attrs['nativeContextRows'])==1 and len(attrs['basicContextRows'])==1911
 assert [r['uid']for r in attrs['rows']]==UIDS+[SECONDARY]and attrs['nativeContextRows'][0]['uid']==NATIVE
 assert np.asarray(at['rows'][0]['completeActualDrawnTriplets']).shape==(9214,9)
 m=read(FEAS/'complete-six-current-protection-masks.json.gz');assert len(m['rows'])==6 and sum(r['completeActualBasicFacets']for r in m['rows'])==280
 assert all(len(v['exactXZ'])==3 and all(len(x)==2 for x in v['exactXZ'])for r in m['rows']for v in r['exactMasks'])
 old=read(GUARD/'actual-six-guard-samples-and-boundaries.json');assert len(old['rows'])==6 and sum(len(r['rows'])for r in old['rows'])==516
 assert {r['uid']for r in old['rows']}=={r['uid']for r in m['rows']}
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
 return dict(passed=True,caller=ref(Path(__file__)),method=ref(METHOD),completeOwnedSourceFaces=13312,secondaryForeignSourceFaces=392,currentDrawnFaces=9214,completeCurrentBASICActors=1911,protectionMaskActors=6,originalGuardSamples=516,noDBLeasePartitionJoinOrFiniteMath=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 schema_only();pre=read(PREFLIGHT);assert pre['passed']and pre['caller']==ref(Path(__file__))and pre['method']==ref(METHOD)
 closure=read(PROPOSAL/'literal-runtime-closure-preflight.json');assert closure['schema']=='exact-literal-static-dynamic-resource-closure-v1'and closure['computedImportsRejected']and closure['unsupportedDynamicImports']==0 and closure['entryPath']==str(RUNTIME.relative_to(ROOT));[check(dict(path=k,sha256=v))for k,v in closure['inputHashes'].items()]
 v=read(VALIDATION);assert v['exitCode']==0 and v['passedTests']==12 and v['failedTests']==0 and v['helper']==ref(HELPER)and v['test']==ref(TEST);check(v['log'])
 refs=[ref(Path(__file__)),ref(HELPER),ref(TEST),ref(RUNTIME),ref(METHOD),ref(PREFLIGHT),ref(VALIDATION),v['log'],ref(FREEZER),ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'literal-runtime-closure-preflight.json')]+[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()]
 # Actual present local import graph is pinned before loading dynamic modules.
 folders=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',HERE.parent/'assembly-support-review']
 todo=[Path(__file__),FREEZER];seen=set()
 while todo:
  p=todo.pop().resolve()
  if p in seen:continue
  seen.add(p);refs.append(ref(p))
  for n in ast.walk(ast.parse(p.read_text())):
   names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
   for name in names:
    for folder in folders:
     q=folder/(name.replace('.','/')+'.py')
     if q.is_file():todo.append(q)
 receipts=[]
 for folder,job,resultsha in [(CAP,'69916bb92558c08c4c5c1838f7c34f963f0e888b7ef14cb489d995ab9bc36727','91d90929b7a8f3694239ba7d5ec97ab5bc1018d52e8d205c08542a820735f120'),(REG,'3046002072e7956b8d862a6a0ed14a66055fa962bfa3ccbef9401286910b4899','93579719eb26a37bd28fc6aadf019d305a0940e5f279f4b329c86751fbda439a'),(NAT,read(PROPOSAL/'draft-pins.json')['nativeReceipt']['jobId'],read(PROPOSAL/'draft-pins.json')['nativeReceipt']['result']['sha256']),(FEAS,'04df198e74f3924c79a56129a9ec41036b2134d948daeb4e75596b48f6c4e883','c49773f2b1f5a940f9d025e2f87924b74a5b366395992345c82ce530098b3ca1'),(GUARD,'d9a167b3fa8775af3a17c6355616a3181e483a7e78d97554ff595d8654fd333e','e58905de5c8cb079af70d1ae4748821d52623db577f8d7e11abbf0fb0010ddbc'),(MAIN,'857e666c1721fbce507712fc0948dc933124d80b3755eac49ca56c3d4dca3f2b','c235bc813ff97828e54353856b9b3be5f0a9a9f6bc0a69ae915844013811204f'),(RESIDUAL,'833861983a261e8ba85626f3fc794042d76c8426b2b3fc48db6363f6d3efc8b3','a6469797b39ceb0f6b5532e87a89de07fb6f583c6bf2387bb6fa874f3d29583f')]:
  receipt=read(folder/'result.json');assert receipt['jobId']
  if 'status'in receipt:assert receipt['status']=='complete'
  if job:assert receipt['jobId']==job and ref(folder/'result.json')['sha256']==resultsha
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for q in receipt['evidenceRefs']+[ref(folder/'result.json')]:check(q);refs.append(q);pulse()
  receipts.append(receipt)
 # Bind the saved complete world inputs and both failed-constructor/replay jobs.
 for pinned in read(PROPOSAL/'draft-pins.json')['receipts']:
  receipt=read(check(pinned['result']));assert receipt['jobId']==pinned['jobId']
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for q in receipt['evidenceRefs']+[pinned['result']]:check(q);refs.append(q);pulse()
 refs +=read(PROPOSAL/'draft-pins.json')['inputRefs']
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(True)
 fence();inp=read(CAP/'input.json.gz');attrs=read(CAP/'whole-domain-current-actors.json.gz');attribution=read(CAP/'whole-domain-actual-parent-attribution.json.gz');reg=read(REG/'diagnostic.json.gz');src=read(REG/'untouched-source-tin.json.gz')
 assert inp['expectedNativeCount']==6649 and inp['currentManifest']['sha256']==CURRENT and inp['domain']==DOMAIN and inp['rederivedCoarseCells']==CELLS
 assert attrs['startEndAllInputsVerified']and attribution['startEndAllInputsVerified']and len(attribution['rows'])==1
 current,representation=adapt_captured_ground(attribution['rows'][0],expected_faces=9214,expected_ground_sha='b4916dac0a7c911a5b20e7dde729fa9a99fca63fa01896db8380523e6158670a',expected_source_counts=[('3d-viewer/city/data/terrain.json',32),('3d-viewer/city/data/government-native-79882-0.json',9182)])
 source=np.asarray(src['allOriginalTriplets'],dtype='<f8');assert source.shape==(122721,3,3)and sha(source)==src['completeSourceSHA256']=='3ace7f401040b2109fd196c603f506d42f0238292742e528c3c46f786b2d93e6'
 base=read(ROOT/'3d-viewer/city/data/terrain.json');g=base['meta']['georef'];assert [g['bE']+CELLS[0]*g['aE']-834500,816500-(g['bN']+CELLS[1]*g['aN']),g['bE']+CELLS[2]*g['aE']-834500,816500-(g['bN']+CELLS[3]*g['aN'])]==DOMAIN
 old=read(check(inp['retainedParent']));assert old==inp['retainedParentExactCurrentData']and old['coarseCells']==[457,449,459,451]
 actor_rows=attrs['rows']+attrs['nativeContextRows'];assert [r['uid']for r in actor_rows]==UIDS+[SECONDARY,NATIVE]
 allbounds=[]
 for row in [r for r in actor_rows if r['uid']in UIDS]:
  allbounds.append(row['completeOriginalPOSITIONProof']['originalWholeSourceBounds'])
  allbounds += [row[k]for k in ['completeLiteralWorldBounds','completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds','completeExplicitBalancedFloat32ModelMatrixWorldBounds']]
 maskdata=read(FEAS/'complete-six-current-protection-masks.json.gz');assert len(maskdata['rows'])==6 and len({r['currentForm']['parent']for r in maskdata['rows']})==6
 masks=[mask(m['exactXZ'])for r in maskdata['rows']for m in r['exactMasks']]
 feasibility=read(FEAS/'diagnostic.json.gz');assert len([r for r in feasibility['rows']if r['uid']in UIDS])==8 and all(not r['actualOrdinaryRestorationConflictWitnesses']for r in feasibility['rows']if r['uid']in UIDS)
 core=protected_core(allbounds,DOMAIN);DOC.mkdir(parents=True);selection=nominate(current.tolist(),masks,DOMAIN);selected={q['currentFace']:q for q in selection['selected']};masks=selection['expandedMasks'];current_attribution=source_attribution(current,attribution['rows'][0]['completeAttributedSources']);save(DOC/'whole-current-facet-protection-nominations.json.gz',exact_records(selection));assert not selection['wholeFacetOutsideCapturedDomainHolds'],'Whole protected current facet exceeds captured domain; preserve nomination and stop'
 save(DOC/'input.json.gz',dict(currentManifest=inp['currentManifest'],domain=DOMAIN,coarseCells=CELLS,core=list(map(float,core)),wholeBounds=allbounds,retainedParent=inp['retainedParent'],allCurrentInputRefs=inp['evidenceRefs'],captureInput=ref(CAP/'input.json.gz'),exactOldGuardSamples=ref(GUARD/'actual-six-guard-samples-and-boundaries.json'),completeSixMasks=ref(FEAS/'complete-six-current-protection-masks.json.gz'),secondaryHeldAsForeign=SECONDARY,candidateOnly=True))
 faces=[];provenance=[];source_inventory=[];current_inventory=[];joins=[]
 def append(face,record,unchanged=False):
  value=np.asarray(face,dtype='<f8')if unchanged else packed(face);assert value.shape==(3,3)and np.isfinite(value).all()
  faces.append(value);provenance.append({**record,'candidateFace':len(faces)-1,'savedInputByteExact':unchanged,'rawNominationFaceSHA256':sha(value)})
 edges={}
 def partition(array,kind):
  inventory=[]
  for i,face in enumerate(array):
   start=len(faces)
   if kind=='capturedCurrent'and i in selected:
    append(face,dict(kind='capturedCurrentRing',region='wholeCurrentProtectionFacet',originalFace=i,completeOriginalMaskIDs=selected[i]['completeOriginalMaskIDs'],completeCurrentSourceAttribution=current_attribution[i],computedFragment=False),True);regions=[]
   else:regions=partition_regions(face.tolist(),DOMAIN,core,masks,kind)
   for q in regions:
    for f in triangulate(q['polygon']):
     unchanged=same_triplet(f,face.tolist());append(face if unchanged else f,dict(kind='originalTIN'if kind=='originalTIN'else'capturedCurrentRing',region=q['region'],protectionMask=q['mask'],originalFace=i,completeCurrentSourceAttribution=current_attribution[i]if kind=='capturedCurrent'else None,computedFragment=not unchanged,exactOriginalPlanePoints=None if unchanged else [[str(v)for v in p]for p in f]),unchanged)
    if kind=='originalTIN':
     for edge,causes in interface_edges(q['polygon'],core,masks):
      # Pack endpoints exactly as renderer source fragments; record both forms.
      pe=packed([edge[0],edge[1],edge[1]])[:2];key=tuple(sorted(tuple(F(float(v))for v in p)for p in pe));edges.setdefault(key,[]).append(dict(originalSourceFace=i,exactCutEdge=[[str(v)for v in p]for p in edge],cutCauses=causes))
   inventory.append(dict(originalFace=i,originalFaceSHA256=sha(face),exactNonrendering=not nonzero(face.tolist()),uncreditedDegenerate=not nonzero(face.tolist()),emittedCandidateFaces=list(range(start,len(faces))),completeOriginalTripletRetainedInSavedInput=True))
   if i%256==0:pulse();print(json.dumps(dict(phase='partition',surface=kind,processed=i,total=len(array))),flush=True)
  return inventory
 source_inventory=partition(source,'originalTIN');current_inventory=partition(current,'capturedCurrent')
 # Every retained current candidate cell, including expanded fragments/layers,
 # is checked against complete owned worlds under the unchanged ordinary -.5.
 saved_ground,_,worlds,_,_=load_saved_worlds();assert sha(saved_ground)==sha(current)
 retention=[(i,f,p)for i,(f,p)in enumerate(zip(faces,provenance))if p['kind']=='capturedCurrentRing'];save(DOC/'packed-source-current-before-compatibility.json.gz',dict(candidateRawPositionTriplets=[f.tolist()for f in faces],candidateFaceProvenance=provenance,wholeSourceOriginalFaceInventory=source_inventory,wholeCurrentFaceInventory=current_inventory,completeCurrentAttribution=current_attribution));compatibility=[];cache={}
 for uid,mode,w,census,_ in worlds:
  if uid not in UIDS:continue
  lo=w[:,:,[0,2]].min(1);hi=w[:,:,[0,2]].max(1);body={i:k for k,ids in enumerate(census['sharedEdgeConnectedComponents'])for i in ids};rows=[];failures=[]
  for ci,face,provenance_row in retention:
   m=projected_mask(face)
   if area(m)==0:rows.append(dict(candidateFace=ci,projectedCollapsedUncredited=True));continue
   gl=np.asarray(face)[:,[0,2]].min(0);gh=np.asarray(face)[:,[0,2]].max(0);ids=np.flatnonzero(np.all(hi>=gl,1)&np.all(lo<=gh,1));pairs=[]
   for si in ids:
    key=(sha(w[si]),sha(face))
    if key not in cache:cache[key]=masked_current_pair(w[si],face,m)
    proof=cache[key]
    if not proof.get('closedMaskedProjectionDisjoint'):pairs.append(dict(sourceFace=int(si),originalBody=body.get(int(si)),proof=proof))
    if proof.get('violatesExistingOrdinaryBound'):failures.append(dict(candidateFace=ci,currentOriginalFace=provenance_row['originalFace'],sourceFace=int(si),originalBody=body.get(int(si)),proof=proof))
   rows.append(dict(candidateFace=ci,currentOriginalFace=provenance_row['originalFace'],allClosedBoundsSelectedOwnedFaceIDs=ids.tolist(),allOtherOwnedFacesStrictBoundsOutside=True,completeExactPairs=pairs));pulse()
  compatibility.append(dict(uid=uid,mode=mode,wholeWorldSHA256=sha(w),completeFaces=len(w),allRetainedCells=rows,actualOrdinaryFailures=failures,noCoverageSupportRoleCredit=True));print(json.dumps(dict(phase='expanded-current-cell-compatibility',uid=uid,mode=mode,failures=len(failures))),flush=True)
 save(DOC/'complete-expanded-current-owned-ordinary-compatibility.json.gz',dict(rows=compatibility,existingOrdinaryLowerBoundM='-1/2',allFourWorldsAndWholeOwnedFacesRetained=True))
 assert len(compatibility)==8
 if any(q['actualOrdinaryFailures']for q in compatibility):
  save(DOC/'diagnostic.json.gz',dict(expandedCurrentCellsConflict=True,noCandidateRuntimeStarted=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0));refs +=[ref(p)for p in DOC.iterdir()if p.is_file()];fence();load_module(FREEZER,'upton_expansion_conflict_freezer').freeze(BATCH,'whole-current-facet-expanded-cell-ordinary-conflict',[check(q)for q in {(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=UIDS+[NATIVE],sourceOnly=True,candidateOnly=True,currentManifest=inp['currentManifest'],completeOwnedFaces=13312,physicalAccepted=False,newlyInstalled=0));return
 fence()
 for edge,origins in sorted(edges.items()):
  if edge[0]==edge[1]or(edge[0][0],edge[0][2])==(edge[1][0],edge[1][2]):
   joins.append(dict(packedSourceEdge=exact_records(edge),origins=origins,collapsedConnectorUncredited=True,completeUpperEnvelopeNomination=dict(complete=False,reason='Packed cut edge collapsed',joinNominations=[])));continue
  proof=nominated_upper_join(edge,current);joins.append(dict(origins=origins,packedSourceEdge=exact_records(edge),completeUpperEnvelopeNomination=proof))
  if proof['complete']:
   for q in proof['joinNominations']:
    for f in q['ruled']['allPositiveGeneratedJoinFaces']:append(f,dict(kind='computedVerticalRuledJoin',origins=origins,currentSurfaceFace=q['currentFace'],exactParameterInterval=q['exactParameterInterval'],exactOriginalPlanePoints=[[str(v)for v in p]for p in f]))
  pulse()
 assert edges,'No complete core boundary was nominated'
 candidate=np.asarray(faces,dtype='<f8').reshape(-1,3,3);assert np.isfinite(candidate).all()
 save(DOC/'complete-nominations-before-guards.json.gz',dict(domain=DOMAIN,core=list(map(float,core)),wholeSourceOriginalFaceInventory=source_inventory,wholeCurrentFaceInventory=current_inventory,candidateRawPositionTriplets=candidate.tolist(),candidateFaceProvenance=provenance,completeCoreBoundaryNominations=exact_records(joins),allSourceOriginalTriplets=ref(REG/'untouched-source-tin.json.gz'),allCurrentTriplets=ref(CAP/'whole-domain-actual-parent-attribution.json.gz'),noOriginalSourceEdits=True,noRoleRootBridgeCredit=True))
 # Entire original body/facet identities are retained for full candidate checks.
 basic={r['uid']:r for r in attrs['basicContextRows']};affected=[r for r in reg['completeBasicRows']if 'affectedComparisons'in r];assert len(basic)==1911 and len(affected)==52
 scope=[]
 for row in affected:
  raw=basic[row['uid']];vtx=np.asarray(raw['position'],dtype='<f8').reshape(-1,3);idx=np.asarray(raw['index'],dtype=np.int64).reshape(-1,3);world=vtx[idx];saved=row['affectedComparisons']['worlds'][0];assert sha(world)==saved['wholeWorldSHA256']
  ids=closed_face_scope(world,DOMAIN)['selectedFaceIDs'];assert ids==saved['selectedFaceIDs']
  scope.append(dict(uid=row['uid'],wholeActorFacets=len(world),selectedWholeFaceIDs=ids,selectedWholeTriplets=world[ids].tolist(),completeUnusedBounds=[vtx.min(0).tolist(),vtx.max(0).tolist()],strictOutsideWholeFaceIDs=saved['fullClosedDomainFaceScope']['strictOutsideFaceIDs']if 'strictOutsideFaceIDs'in saved['fullClosedDomainFaceScope']else [i for i in range(len(world))if i not in set(ids)],outsideProtectionRequiresRuntimeExteriorEquality=True,priorOrdinaryFailuresRetained=saved['allWholeFacetComparisons']))
 assert sum(len(s['selectedWholeFaceIDs'])for s in scope)==2114
 for uid,ids in NINE.items():
  s=next(s for s in scope if s['uid']==uid);assert set(ids)<=set(s['selectedWholeFaceIDs'])
 native=read(NAT/'inventory.json.gz');assert native['completeNativeActors']==native['successfullyCapturedActors']==6649 and not native['errors']and native['startAndEndInputHashesVerified']
 nominees=[];outside=[]
 for r in native['rows']:
  bb=[r['completeOriginalPOSITIONProof']['originalWholeSourceBounds'],r['completeLiteralBounds'],r['completeLeftAssociatedF32Bounds'],r['completeBalancedF32Bounds']]
  touches=any(not(b[1][0]<DOMAIN[0]or b[0][0]>DOMAIN[2]or b[1][2]<DOMAIN[1]or b[0][2]>DOMAIN[3])for b in bb)
  (nominees if touches else outside).append(dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],allWholeUnusedBounds=bb))
 save(DOC/'complete-affected-scope.json.gz',dict(ownedAndRetained=UIDS+[NATIVE],secondaryHeldAsForeign=SECONDARY,completeSecondarySourceFaceCount=392,secondaryCurrentFormsMustBeIncludedInFreshForeignPhysicalChecks=True,completeBasicRows=1911,affectedBasic=scope,requiredNineWholeFacets=NINE,completeNativeActors=6649,wholeDomainTouchingNativeNominees=nominees,strictBoundsOutsideNativeActors=outside,otherTouchingNativeCompleteActualStreamsUnqualified=[r['uid']for r in nominees if r['uid']!=NATIVE],allHistoricalZeroAnd23CrossingObligations=reg['allHistoricalZeroForeignCrossingRootObligationsRetained'],allFacetAndBodyRoleObligationsRemain=True))
 save(DOC/'geometry-nomination.json.gz',dict(candidateRawPositionTriplets=candidate.tolist(),domain=DOMAIN,core=list(map(float,core)),allBoundaryFiniteNominationsComplete=all(j['completeUpperEnvelopeNomination']['complete']for j in joins),originalSourceFaces=122721,currentCapturedFaces=9214,candidatePackedFacets=len(candidate),computedFacesHaveSeparateProvenance=True,unpublished=True))
 # Production replay supplies actual grid alignment/renderer winding/draw scope,
 # exterior-preservation scalar hashes and real sampler findings. No publisher.
 log=DOC/'actual-production-replay.log'
 with log.open('wb')as out:subprocess.run(['node',str(RUNTIME),str(DOC.relative_to(ROOT))],cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,check=True)
 replay=read(DOC/'actual-production-replay.json.gz');assert replay['currentManifestSHA256']==CURRENT and replay['startEndAllInputsVerified']
 for path,h in replay['inputHashes'].items():refs.append(dict(path=path,sha256=h))
 # This caller records the real validator outcome without adding stale overlap
 # or fallback approvals. Any failure is a candidate hold, never waived.
 validator_path=HERE.parent/'island-detail-integration/native_terrain_validation.py';refs.append(ref(validator_path));validator=load_module(validator_path,'upton_private_join_real_native_validator')
 validator_failure=None
 try:validator.validate_native_mesh(read(DOC/'private-native-terrain-candidate.json.gz'),base)
 except AssertionError as e:validator_failure=str(e)
 save(DOC/'real-validator-outcome.json',dict(passed=validator_failure is None,actualAssertion=validator_failure,unchangedValidator=ref(validator_path),noApprovalOrToleranceChanges=True,notExactSeamCertificate=True))
 # Fresh geometry-bound overlap attribution, without adding overlap approval.
 patch=read(DOC/'private-native-terrain-candidate.json.gz');measured=measured_projection(patch,provenance,DOMAIN,old);actual=candidate_surface(patch,provenance);drawn=np.asarray(replay['after']['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3);multiset=verify_drawn_multiset(actual,drawn)
 exact_pairs=[]
 for q in measured['allProjectedIntersectingPairs']:
  i,j=q['leftFace'],q['rightFace'];a,b=provenance[i],provenance[j];old_a=current[a['originalFace']]if a['kind']=='capturedCurrentRing'else None;old_b=current[b['originalFace']]if b['kind']=='capturedCurrentRing'else None
  exact_pairs.append(dict(leftFace=i,rightFace=j,leftProvenance=a,rightProvenance=b,measuredProjectedDimension=q['projectedDimension'],proof=exact_overlap_attribution(actual[i],actual[j],old_a,old_b)));pulse()
 save(DOC/'new-geometry-measured-overlap-and-exact-height-attribution.json.gz',dict(measured=measured,exactMeasuredPairNominations=exact_pairs,drawnMultiset=multiset,measuredPairBroadphaseIsNotExactCompletePairCensus=True,allSampledHeightsAreNotProductionRayApproval=True,noCopiedOverlapApproval=True))
 save(DOC/'diagnostic.json.gz',dict(currentManifest=inp['currentManifest'],domain=DOMAIN,core=list(map(float,core)),candidateNomination=ref(DOC/'geometry-nomination.json.gz'),affectedScope=ref(DOC/'complete-affected-scope.json.gz'),realValidator=ref(DOC/'real-validator-outcome.json'),runtime=ref(DOC/'actual-production-replay.json.gz'),completeWholeOwnedFourStreamFiniteStillRequired=True,complete52BasicCandidateRegressionStillRequired=True,completeNativeNomineeStreamsAndRegressionStillRequired=True,allNinePriorFullFacetsRemainObligations=True,noExactPackingCoverageOrSeamApproval=True,sourceGeometryChanges=0,sourcePoseChanges=0,currentTerrainGeometryChanges=0,privateComputedTerrainNomination=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 refs += [ref(p)for p in sorted(DOC.iterdir())if p.is_file()];fence()
 load_module(FREEZER,'upton_private_join_freezer').freeze(BATCH,'private-source-preserving-original-TIN-current-ring-join-nomination',[check(q)for q in {(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=UIDS+[NATIVE],sourceOnly=True,candidateOnly=True,physicalAccepted=False,newlyInstalled=0,currentManifest=inp['currentManifest'],completeOwnedFaces=13312,completeAffectedBasicActors=52,wholeSourceFacets=122721))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--generate-whole-current-facet-private-nomination-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 uids=UIDS+[SECONDARY,NATIVE,FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-original-current-ring-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
