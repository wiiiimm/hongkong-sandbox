"""UNEXECUTED historical6648 intrinsic source ledger + ONE fresh actual installed Heya actor.
No old receipt aliases, scene changes, native reapproval or physical credit.
"""
import argparse,json,subprocess,sys,uuid,re
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from upton_exact_actual_history_archive_bindings_draft_v1_20261011 import load_contract,exact_ref
from upton_three_original_complete_current_runtime_capture_draft_v4_20261012 import state,module,ref
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-complete-native-actual-position-post-heya-delta-draft-v2-20261012';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=B/'government-xl-complete-current-native-actual-position-matrix-bounds-v3-20261011';EXPORTER=HERE/'xl-complete-native-actual-position-post-heya-delta-draft-v2-20261012.mjs'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540';UID='landsd/184286:0';PROTECTED=[UID,'landsd/184285:0']
HISTORY='docs/astra-city/government-import/government-xl-upton-actual-pre-heya-source-history-root-v1-20261011/root-actual-history-contract.json';HISTORY_SHA='51b1ae85bd5cf3bf59e6e0fb1daa921a85835f2fe793d4d2ed00a9e0a5ee5a68'
CAP=B/'government-xl-upton-three-original-complete-current-runtime-capture-v4-20261012'
INTEGRATION_HISTORY=B/'government-xl-upton-post-integration-current-capture-finite-proposal-v1-20261012/actual-before-integration-history-contract.json'
INTEGRATION_HISTORY_SHA='987e458b0b50d21ae8c4dbba4e6b4dc01e7d60277e2cd6d375ce784e3434b531'
FINITE=B/'government-xl-upton-three-original-complete-current-finite-ground-v5-20261012'

def preflight():
 contract=load_contract(ROOT,HISTORY,HISTORY_SHA);integration_history=load_contract(ROOT,str(INTEGRATION_HISTORY.relative_to(ROOT)),INTEGRATION_HISTORY_SHA)
 combined=dict(actualHistoricalBytesOnly=True,historicalArchives=contract['historicalArchives']+integration_history['historicalArchives'])
 assert len(combined['historicalArchives'])==len({(e['originalPath'],e['historicalSHA256'])for e in combined['historicalArchives']})
 capture=read(CAP/'result.json');assert ref(CAP/'result.json')['sha256']=='a460d9f7ba768dec6b32d7d8a845c3c6b8775ade98c4476e3e522b3810ec55c5'and capture['jobId']=='4af6addb43b6b94fd2e5e61c868fbd62c84d06a365dc2e19b79d6856ce054502'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(capture['jobId'],)).fetchone()==('complete',capture)
 for e in capture['evidenceRefs']:assert ref(ROOT/e['path'])==e
 for path,h in read(CAP/'capture-scope.json')['inputHashes'].items():assert ref(ROOT/path)['sha256']==h
 finite_result=read(FINITE/'result.json');assert ref(FINITE/'result.json')['sha256']=='da991e5d24f25fa086ed82758dc726d39a0078cc446295fcedc15bc4227e01fc'and finite_result['jobId']=='7b2c30c7df3cca9f42d7d3e8cee90f98525d0939c49ad396d900a256d8f4f325'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(finite_result['jobId'],)).fetchone()==('complete',finite_result)
 for e in finite_result['evidenceRefs']:assert ref(ROOT/e['path'])==e
 diagnostic=read(FINITE/'diagnostic.json.gz');ordinary=coverage=0
 for actor in diagnostic['actors']:
  source=actor['allFourStreamBindings']['original']['wholeWorldSHA256'];proof=actor['distinctCompleteFiniteProofs'][source];ordinary+=len(proof['ordinaryFailingFaces']);coverage+=len(proof['coverageFailingFaces'])
 assert ordinary==335 and coverage==34 and diagnostic['all23ProperSourceCrossingsRetained']and not diagnostic['physicalAccepted']
 receipt=read(PRIOR/'result.json');assert receipt['jobId']=='08bf24d405bee841b6b02729e091986ac0043a6e94f002af2f078db2dc316a1f'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 bindings=[exact_ref(ROOT,e,combined)for e in receipt['evidenceRefs']];oldinput=read(PRIOR/'input.json.gz');old=read(PRIOR/'inventory.json.gz');assert len(oldinput['currentAllNativeSourceForms'])==6763;assert old['completeNativeActors']==old['successfullyCapturedActors']==6648 and not old['errors']and old['startAndEndInputHashesVerified']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';pin=ref(manifest);assert pin['sha256']==CURRENT;m=read(manifest);oldmanifest=read(ROOT/exact_ref(ROOT,oldinput['currentManifest'],contract)['actualVerifiedFile']['path'])
 assert oldmanifest['tiles']==m['tiles']and oldmanifest['terrainPatches']==m['terrainPatches'];oldhashbindings=[]
 for path,h in old['inputHashes'].items():
  r=dict(path=path,sha256=h)
  if path==str(manifest.relative_to(ROOT)):oldhashbindings.append(exact_ref(ROOT,r,combined))
  else:
   binding=exact_ref(ROOT,r,combined);oldhashbindings.append(binding)
   if binding['historicalArchiveUsed']:assert (r['path'],r['sha256'])in {(e['originalPath'],e['historicalSHA256'])for e in integration_history['historicalArchives']},'Only actual pre-integration module archives can qualify a changed historical input'
 models={};sources={};cats=[]
 for url in m['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;cats.append(dict(**ref(path),originalPath=str(path.relative_to(ROOT))))
  for e in read(path)['models']:assert e['uid']not in models;models[e['uid']]=e;sources[e['uid']]=path.parent/e['asset']
 assert len(models)==6649;oldids={r['uid']for r in oldinput['rows']};assert len(oldids)==6648 and set(models)-oldids=={UID}
 for r in oldinput['rows']:assert models[r['uid']]==r['rawCurrentEntry']and ref(sources[r['uid']])==r['source']
 requested=set(oldinput['currentAllNativeSourceForms'])|{UID};dependencies=set()
 for e in models.values():
  for x in e.get('supportDependencies',[]):dependencies.add(x if isinstance(x,str)else x['uid'])
 requested|=dependencies;forms={};tiles={}
 for tile in m['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];hits=[f for f in read(path)['buildings']if f['uid']in requested]
  if hits:
   tiles[str(path.relative_to(ROOT))]=ref(path)['sha256']
   for f in hits:assert f['uid']not in forms;forms[f['uid']]=f
 assert requested<=set(forms)
 for uid,f in oldinput['currentAllNativeSourceForms'].items():assert forms[uid]==f
 proof=packed_world_bounds(sources[UID].read_bytes());assert proof['sourceSHA256']==models[UID]['sha256']and proof['completeOriginalTriangles']==models[UID]['triangles']and proof['allOriginalPositionVerticesAccounted']
 # Preserve prior rows exactly; intrinsic provider POSITION facts do not transfer runtime approval.
 assert len(old['rows'])==6648 and {r['uid']for r in old['rows']}==oldids
 for row in old['rows']:
  assert row['sourceSHA256']==models[row['uid']]['sha256']==row['completeOriginalPOSITIONProof']['sourceSHA256']
  assert row['wholeUnusedPositionVerticesIncluded']and row['completeOriginalPOSITIONProof']['allOriginalPositionVerticesAccounted']
 assert not models[UID].get('variantId')and models[UID].get('verticalPlacementOffsetHKPD',0)==0
 assert ref(manifest)==pin
 return dict(receipt=receipt,oldinput=oldinput,old=old,manifest=pin,models=models,sources=sources,catalogues=cats,forms=forms,tileHashes=tiles,proof=proof,historyBindings=bindings,oldManifestBindings=oldhashbindings,capturePins=read(CAP/'capture-scope.json')['inputHashes'])

def main():
 a=argparse.ArgumentParser();a.add_argument('--owned',action='store_true');args=a.parse_args();p=preflight()
 if not args.owned:
  assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('heya-native-delta-'+str(uuid.uuid4()),['building:'+u for u in PROTECTED],batch=BATCH,ttl=1800);assert claim['ok'],claim;save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();before=state(PROTECTED)
 walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','native_heya_delta_source_closure');paths=set();walker.local_imports(Path(__file__),paths);paths.update([EXPORTER,ROOT/HISTORY,PRIOR/'result.json',PRIOR/'input.json.gz',PRIOR/'inventory.json.gz',INTEGRATION_HISTORY,CAP/'result.json',CAP/'capture-scope.json',CAP/'actual-render-geometry.json.gz',FINITE/'result.json',FINITE/'diagnostic.json.gz']);paths.update(ROOT/b['actualVerifiedFile']['path']for b in p['historyBindings']);pins={str(x.relative_to(ROOT)):ref(x)['sha256']for x in paths};pins[p['manifest']['path']]=p['manifest']['sha256'];pins.update(p['capturePins'])
 paths.update(ROOT/b['actualVerifiedFile']['path']for b in p['oldManifestBindings'])
 for x in paths:pins[str(x.relative_to(ROOT))]=ref(x)['sha256']
 for e in p['catalogues']:pins[e['path']]=e['sha256']
 pins.update(p['tileHashes']);pins.update({str(x.relative_to(ROOT)):ref(x)['sha256']for x in p['sources'].values()})
 declared=p['oldinput']['declaredDependencyUIDSourceHashes']
 def fence():
  for path,h in pins.items():assert ref(ROOT/path)['sha256']==h,path
  assert state(PROTECTED)==before and reservations.owns(lease)
 fence();save(DOC/'exact-prior-current-tuple-rebind.json',dict(priorJobId=p['receipt']['jobId'],historicalBindings=p['historyBindings'],historicalInputManifestBindings=p['oldManifestBindings'],currentManifest=p['manifest'],all6648RawEntriesSourcesEqual=True,all6763RequestedFormsEqual=True,historicalModuleBindingsVerifiedOnly=True,allPriorRecursiveProductionModuleInputsEqual=False,oldRuntimeApprovalTransferred=False,sourceOnly=True,physicalAccepted=False,rawUptonFiniteHolds=ref(FINITE/'result.json'),ordinaryFailingSourceFaces=335,coverageFailingSourceFaces=34,all23SourceCrossingsPreserved=True))
 row=dict(uid=UID,source=ref(p['sources'][UID]),rawCurrentEntry=p['models'][UID],currentBuilding=p['forms'][UID],completeOriginalPOSITIONProof=p['proof'])
 save(DOC/'input.json.gz',dict(currentBoundOnly=True,completeNativeActors=6649,currentManifest=p['manifest'],currentCatalogueRefs=p['catalogues'],currentNativeViewerTileHashes=p['tileHashes'],declaredDependencyUIDSourceHashes=declared,currentAllNativeSourceForms=p['forms'],rows=[row],evidenceRefs=[ref(DOC/'exact-prior-current-tuple-rebind.json')]))
 subprocess.run(['node','--expose-gc',str(EXPORTER)],cwd=ROOT,check=True);fence();delta=read(DOC/'delta.json.gz');assert delta['expectedDeltaActors']==delta['successfullyCapturedActors']==1 and delta['rows'][0]['uid']==UID and not delta['errors']and delta['startAndEndInputHashesVerified']
 for path,h in delta['inputHashes'].items():assert ref(ROOT/path)['sha256']==h
 historical=p['old']['rows'];fresh=delta['rows'][0];merged=historical+[fresh];assert len(merged)==len({r['uid']for r in merged})==6649 and {r['uid']for r in merged}==set(p['models'])
 # Fresh whole UNUSED positions/actual four world bounds, never catalogue bounds.
 attrs=read(CAP/'actual-render-geometry.json.gz')['rows'];source_rows=read(CAP/'selection.json.gz')['rows'];rectangles=[]
 for a,r in zip(attrs,source_rows):
  assert a['uid']==r['uid']and a['loadedGroupScale']==[1,1,1];original=packed_world_bounds((ROOT/r['candidate']['path']).read_bytes())['originalWholeSourceBounds']
  worlds=dict(original=original)
  for name,key in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
   v=np.asarray(a[key],dtype=float).reshape(-1,3);assert np.isfinite(v).all();worlds[name]=[v.min(0).tolist(),v.max(0).tolist()]
  for name,b in worlds.items():rectangles.append(dict(uid=a['uid'],world=name,bounds=b))
 heya_worlds=dict(original=p['proof']['originalWholeSourceBounds'],literal=fresh['completeLiteralBounds'],explicitLeftF32=fresh['completeLeftAssociatedF32Bounds'],explicitBalancedF32=fresh['completeBalancedF32Bounds']);disjoint=[]
 for name,h in heya_worlds.items():
  for u in rectangles:
   b=u['bounds'];axes=[k for k in (0,2)if h[1][k]<b[0][k]or b[1][k]<h[0][k]]
   disjoint.append(dict(heyaWorld=name,uptonUID=u['uid'],uptonWorld=u['world'],strictlyDisjointXZ=bool(axes),separatingAxes=axes,pointAndBoundaryTouchesAreNotDisjoint=True))
 save(DOC/'fresh-heya-upton-whole-position-disjointness.json',dict(freshCaptureResult=ref(CAP/'result.json'),freshHeyaWorldBounds=heya_worlds,completeUptonUnusedPositionWorldBounds=rectangles,all48WorldPairs=disjoint,all48StrictlyDisjointXZ=all(x['strictlyDisjointXZ']for x in disjoint),disjointBoundsAreNotSupportOrRootApproval=True,sourceOnly=True))
 save(DOC/'inventory.json.gz',dict(currentBoundOnly=False,completeUIDSourceRevisionPartition=6649,rows=merged,historical6648RowsPreservedExactly=True,historicalRuntimeRowsAreNotCurrentApproval=True,currentAll6649RuntimeBoundsProved=False,exactCurrent6648EntrySourceFormsEqual=True,freshHeyaInstalledEntryActualLoad=True,priorReceipt=ref(PRIOR/'result.json'),exactTupleProof=ref(DOC/'exact-prior-current-tuple-rebind.json'),freshDelta=ref(DOC/'delta.json.gz'),freshDisjointness=ref(DOC/'fresh-heya-upton-whole-position-disjointness.json'),sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAccepted=False,installationApproved=False,noNativeReapproval=True))
 paths.update([DOC/'input.json.gz',DOC/'exact-prior-current-tuple-rebind.json',DOC/'delta.json.gz',DOC/'inventory.json.gz',DOC/'fresh-heya-upton-whole-position-disjointness.json']);paths.update(ROOT/path for path in pins);paths.update(ROOT/path for path in delta['inputHashes']);fence()
 frozen=walker.F.freeze(BATCH,'historical6648-intrinsic-source-ledger-plus-fresh-installed-heya-current-bounds',sorted(paths),dict(uids=[UID],sourceOnly=True,currentManifestSHA256=CURRENT,completeUIDSourceRevisionPartition=6649,freshActualRuntimeActors=1,historicalIntrinsicActors=6648,currentAll6649RuntimeBoundsProved=False,ordinaryFailingUptonSourceFaces=335,coverageFailingUptonSourceFaces=34,all23UptonProperSourceCrossingsPreserved=True,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,modelReviewWrites=0))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(frozen['jobId'],)).fetchone()==('complete',frozen)
 for e in frozen['evidenceRefs']:assert ref(ROOT/e['path'])==e
 fence();print(json.dumps(dict(jobId=frozen['jobId'],completeUIDSourceRevisionPartition=6649,freshActualRuntimeActors=1,historicalIntrinsicActors=6648,currentAll6649RuntimeBoundsProved=False,physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
