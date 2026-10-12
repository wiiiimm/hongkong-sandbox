"""Unexecuted conservative original-sheet comparison, no renderer changes."""
import importlib.util,json,sys,subprocess,uuid,types
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
from exact_original_paired_finite_clearance_20261010 import verify as paired
BASE=ROOT/'docs/astra-city/government-import'
INPUT=BASE/'government-xl-southside-315025-300867-current-actual-ground-capture-v1-20261012'
GRADE=BASE/'government-xl-southside-315025-300867-current-grade-source-context-v1-20261012'
CONTEXT=BASE/'government-xl-southside-315025-300867-upward-current-failures-context-v2-20261012'
DRAFT=BASE/'government-xl-southside-unfiltered-original-sheets-comparison-draft-v1-20261012'
BATCH='government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v1-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
UIDS=['landsd/315025:0','landsd/300867:0'];COUNTS={UIDS[0]:11699,UIDS[1]:1191}
SOURCES={UIDS[0]:'85be44e7ab9410c850d3b7d59d05df2cd45fc1072ec2f984ddbb7b43c4d9ff7c',UIDS[1]:'2293ba8925406abcdbd848486a772dfa8baa01caf0cfe96e749d5a3cd51210f1'}
MODES=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
SHEETS=['11-SW-24C','11-SW-24D','15-NW-4A','15-NW-4B'];MANIFEST='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
CONTRACT_SHA='58cfb261ce852455a535443605355c56a8c7675e4f306737284a9c2e38f7d66d'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def imported_files(*extras):
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
def declared_scene_faces(data):
 seen=set();count=0
 def visit(i):
  nonlocal count
  assert i not in seen;seen.add(i);node=data['nodes'][i]
  if 'mesh'in node:
   for primitive in data['meshes'][node['mesh']]['primitives']:
    assert primitive.get('mode',4)==4
    index=primitive['indices']if 'indices'in primitive else primitive['attributes']['POSITION'];n=data['accessors'][index]['count'];assert n%3==0;count+=n//3
  for child in node.get('children',[]):visit(child)
 for i in data['scenes'][data.get('scene',0)]['nodes']:visit(i)
 return count

def preflight():
 assert not DOC.exists();refs=[Path(__file__),DRAFT/'METHOD.md',DRAFT/'no-worker-schema-validation.json',DRAFT/'original-sheet-input-contract.json'];receipts=[]
 for folder,job in [(INPUT,'3aa11a60f740759f78677d151fa2f9c34f494d935b7a208958164e23273f84d9'),(GRADE,'7269234ae78ade5d10223502841ee35aba9e9d844d72c59d186ae56ee45cda71'),(CONTEXT,'3dbf6e58936ce433ab0d14bd2af45934b71c93c6a5834b41c6b3da09b93aaf0d')]:
  receipt=read(folder/'result.json');assert receipt['jobId']==job and not receipt['currentAcceptance'];receipts.append(receipt);refs.append(folder/'result.json')
  for pin in receipt['evidenceRefs']:
   p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 contract=read(DRAFT/'original-sheet-input-contract.json');assert digest((DRAFT/'original-sheet-input-contract.json').read_bytes())==CONTRACT_SHA and contract['completeFourSheets']==SHEETS and [s['sheet']for s in contract['sheets']]==SHEETS
 historical=ROOT/contract['historicalSourceReceiptPath'];assert digest(historical.read_bytes())==contract['historicalSourceReceiptSHA256'];refs.append(historical)
 for sheet in contract['sheets']:
  folder=ROOT/sheet['folder'];a=ROOT/sheet['originalReceiptPath'];b=ROOT/sheet['directoryReceiptPath'];assert digest(a.read_bytes())==sheet['originalReceiptSHA256']and digest(b.read_bytes())==sheet['directoryReceiptSHA256'];refs.extend([a,b]);download=read(a);directory=read(b);assert download['sheet']==directory['sheet']==sheet['sheet']and download['terrainGeometryIncluded']and download['directorySHA256']==directory['directorySHA256']==sheet['directorySHA256']
  files=[e for e in download['entries']if e['name'].startswith('TERRAIN')and e['name'].endswith(('.gltf','.bin'))];assert files==sheet['allOriginalTerrainFiles'];declared=0
  for record in files:
   p=folder/'terrain'/record['name'];assert len(p.read_bytes())==record['bytes']and digest(p.read_bytes())==record['sha256'];refs.append(p)
   if p.suffix=='.gltf':declared+=declared_scene_faces(read(p))
  assert declared==sheet['declaredCompleteSceneTerrainFacets']
 capture=read(INPUT/'capture-inputs.json.gz');forms=capture['completeCurrentForms'];assert len(forms)==46 and len({q['uid']for q in forms})==46;expected=sorted(set(['building:'+u for u in UIDS]+[('building:'+f['uid'])if f['uid'].startswith('landsd/')else('source-form:'+f['uid'])for f in forms]+['terrain-patch:'+u for u in UIDS]));assert capture['canonicalResources']==expected and len(expected)==48;resources=sorted(set(expected+['immutable-source-sheet:'+s for s in SHEETS]));assert len(resources)==52
 assert capture['manifestSHA256']==MANIFEST and digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 data=read(INPUT/'complete-two-actor-four-stream-ground-inputs.json.gz')['rows'];grade=read(GRADE/'diagnostic.json.gz');rows={(q['uid'],q['arithmetic']):q for q in grade['rows']};assert set(data)==set(UIDS)and len(rows)==8
 for uid in UIDS:
  actual=read(INPUT/('complete-current-actual-source-and-ground-'+uid.split('/')[1].replace(':','-')+'.json.gz'));assert actual['completeOriginalPOSITIONProof']['allOriginalPositionVerticesAccounted']and actual['sourceSHA256']==data[uid]['sourceSHA256']==SOURCES[uid];bounds=np.asarray([actual['completeOriginalPOSITIONProof']['originalWholeSourceBounds'],*actual['completeWholeUnusedVertexBounds']],dtype='<f8');assert bounds.shape==(4,2,3)and np.isfinite(bounds).all()
  for mode in MODES:
   stream=data[uid]['completeWorldStreams'][mode];world=np.asarray(stream['completeWorldTriangles'],dtype='<f8');q=rows[uid,mode];assert world.shape==(COUNTS[uid],3,3)and digest(world.tobytes())==q['completeWorldSHA256']==stream['completeWorldTriangleSHA256']and len(q['allCompleteOriginalFiniteRecords'])==COUNTS[uid]
 decoder=module('southside_unfiltered_sheet_decoder',HERE/'xl-second-pass.py');decoder.LOCAL=LOCAL;freezer=module('southside_unfiltered_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');refs.extend(imported_files(decoder,freezer));validation=read(DRAFT/'no-worker-schema-validation.json');assert validation['callerSHA256']==digest(Path(__file__).read_bytes())and validation['methodSHA256']==digest((DRAFT/'METHOD.md').read_bytes())
 return receipts,refs,{str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs},contract,capture,data,rows,decoder,freezer,resources

def owned(state):
 receipts,refs,pins,contract,capture,data,oldrows,decoder,freezer,resources=state;lease=read(LEASE);assert reservations.owns(lease)and lease['resources']==resources;before=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for receipt in receipts:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 fragments=[];inventory=[];offset=0
 for sheet in contract['sheets']:
  sheet_count=0
  for record in sheet['allOriginalTerrainFiles']:
   path=ROOT/sheet['folder']/'terrain'/record['name']
   if path.suffix!='.gltf':continue
   triangles=decoder.terrain_triangles(path);assert triangles.ndim==3 and triangles.shape[1:]==(3,3)and np.isfinite(triangles).all()and len(triangles)==declared_scene_faces(read(path));triangles=np.asarray(triangles,dtype='<f8');fragments.append(triangles);inventory.append(dict(sheet=sheet['sheet'],sourceGltfPath=str(path.relative_to(ROOT)),sourceGltfSHA256=record['sha256'],completeDecodedFacets=len(triangles),completeDecodedFacetSHA256=digest(triangles.tobytes()),globalOriginalFacetStart=offset,globalOriginalFacetEndExclusive=offset+len(triangles)));offset+=len(triangles);sheet_count+=len(triangles)
  assert sheet_count==sheet['declaredCompleteSceneTerrainFacets']
 whole=np.concatenate(fragments);assert len(whole)==sum(s['declaredCompleteSceneTerrainFacets']for s in contract['sheets']);whole_sha=digest(whole.tobytes());rows=[];ground_records=[];cache={}
 for uid in UIDS:
  actual=read(INPUT/('complete-current-actual-source-and-ground-'+uid.split('/')[1].replace(':','-')+'.json.gz'));bounds=np.asarray([actual['completeOriginalPOSITIONProof']['originalWholeSourceBounds'],*actual['completeWholeUnusedVertexBounds']],dtype='<f8');low,high=bounds[:,0].min(0),bounds[:,1].max(0);keep=(whole[:,:,0].max(1)>=low[0])&(whole[:,:,0].min(1)<=high[0])&(whole[:,:,2].max(1)>=low[2])&(whole[:,:,2].min(1)<=high[2]);ids=np.flatnonzero(keep).tolist();ground=whole[keep];assert len(ground)>0;gsha=digest(ground.tobytes());ground_records.append(dict(uid=uid,sourceSHA256=data[uid]['sourceSHA256'],completeAllFourUnusedPOSITIONBounds=bounds.tolist(),completeBoundsUnion=[low.tolist(),high.tolist()],selectedGlobalOriginalFacetIds=ids,completeSelectedFacets=ground.tolist(),completeSelectedFacetSHA256=gsha,closedAABBWholeFacetSelection=True,allSlopesVerticalAndCollapsedProjectionFacetsRetained=True,noHeightAreaOrSlopeFilter=True))
  for mode in MODES:
   world=np.asarray(data[uid]['completeWorldStreams'][mode]['completeWorldTriangles'],dtype='<f8');old=oldrows[uid,mode];records=[]
   for i,face in enumerate(world):
    fsha=digest(face.tobytes());assert old['allCompleteOriginalFiniteRecords'][i]['sourceFace']==i and old['allCompleteOriginalFiniteRecords'][i]['completeOriginalFacetSHA256']==fsha;key=(fsha,gsha)
    if key not in cache:
     a=coarse(face,ground);b=None if a['existingOrdinaryClearanceBoundProved']else paired(face,ground);cache[key]=dict(coarse=a,paired=b,completeFiniteOrdinaryBoundProved=bool(a['existingOrdinaryClearanceBoundProved']or(b and b['existingOrdinaryClearanceBoundProved'])))
    records.append(dict(sourceFace=i,completeOriginalFacetSHA256=fsha,orientationDescriptiveOnly=old['allCompleteOriginalFiniteRecords'][i]['exactOrientationDiagnostic'],currentDrawnGroundComparisonRetainedVerbatim=old['allCompleteOriginalFiniteRecords'][i]['currentDrawnGroundComparison'],unfilteredAuthenticatedOriginalGroundComparison=cache[key]))
    if i%2000==0:print(json.dumps(dict(uid=uid,mode=mode,completedSourceFacets=i,unfilteredSelectedTerrainFacets=len(ground))),flush=True)
   failed=[q['sourceFace']for q in records if not q['unfilteredAuthenticatedOriginalGroundComparison']['completeFiniteOrdinaryBoundProved']];upward=[q['sourceFace']for q in records if q['sourceFace']in failed and q['orientationDescriptiveOnly']=='upward-nonsteep'];row=dict(uid=uid,sourceSHA256=data[uid]['sourceSHA256'],arithmetic=mode,completeWorldSHA256=digest(world.tobytes()),completeUnfilteredSelectedGroundSHA256=gsha,completeOriginalFaceComparisons=records,allAuthenticatedGroundFailuresRetained=failed,authenticatedGroundUpwardFailuresRetained=upward,allCurrentFailuresRetainedVerbatim=old['allRawFailedFaces'],noCurrentFiniteRecomputation=True,currentAcceptance=False,currentGroundReplacementProposed=False);rows.append(row);save(LOCAL/('completed-'+uid.split('/')[1].replace(':','-')+'-'+mode+'.json.gz'),row);print(json.dumps(dict(uid=uid,mode=mode,authenticatedFailures=len(failed),authenticatedUpwardFailures=len(upward))),flush=True)
 save(DOC/'complete-unfiltered-authenticated-source-ground.json.gz',dict(uids=UIDS,completeAllOriginalSheetFacets=len(whole),completeAllOriginalSheetFacetSHA256=whole_sha,completeOriginalSourceInventory=inventory,actorConservativeGrounds=ground_records,sourceCoordinateTransformsUnchanged=True,currentRendererGround=False,terrainGeometryChanges=0))
 save(DOC/'diagnostic.json.gz',dict(uids=UIDS,rows=rows,originalSheetContractVerbatim=contract,allHistoricalObligationsVerbatim=read(INPUT/'historical-obligations-verbatim.json'),all46CurrentFormsRetainedVerbatim=capture['completeCurrentForms'],sourceGeometryChanges=0,terrainGeometryChanges=0,sourceOnly=True,noRoleRootOrFoundationInterpretation=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False))
 assert reservations.owns(lease)and(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before
 for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');refs.extend([DOC/'complete-unfiltered-authenticated-source-ground.json.gz',DOC/'diagnostic.json.gz']);out=freezer.freeze(BATCH,'southside-complete-four-original-sheet-unfiltered-four-stream-comparison-no-current-credit',refs,dict(uids=UIDS,sourceOnly=True,completeAllOriginalSheetFacets=len(whole),currentAcceptance=False,newlyInstalled=0));print(json.dumps(dict(jobId=out['jobId'],currentAcceptance=False)),flush=True)
def main():
 state=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(noWorker=True,noDB=True,noLease=True,noTerrainDecodeOrFinitePredicatesRun=True,completeFourSheetDeclaredFacets=sum(s['declaredCompleteSceneTerrainFacets']for s in state[3]['sheets']),resources=state[-1],currentAcceptance=False)),flush=True);return
 if '--owned'in sys.argv:return owned(state)
 assert not LOCAL.exists();claim=reservations.claim('southside-unfiltered-source-comparison-'+str(uuid.uuid4()),state[-1],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
