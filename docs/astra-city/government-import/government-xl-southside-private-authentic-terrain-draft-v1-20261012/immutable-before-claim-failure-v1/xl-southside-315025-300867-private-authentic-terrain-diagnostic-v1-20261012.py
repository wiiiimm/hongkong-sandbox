"""Unexecuted private authentic terrain diagnostic; no source roles or live writes."""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
import southside_exact_private_terrain_adapter_v1_20261012 as adapter
BASE=ROOT/'docs/astra-city/government-import'
DRAFT=BASE/'government-xl-southside-private-authentic-terrain-draft-v1-20261012'
BATCH='government-xl-southside-315025-300867-private-authentic-terrain-diagnostic-v1-20261012'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
UIDS=['landsd/315025:0','landsd/300867:0'];NATIVE_COUNT=6649
FULL_TIN_SHA='7f4a1b2e43b38c2512cd3f5d44e256b36af1cab07d1e2b37d39db4a7e9da9b66'
INPUT=BASE/'government-xl-southside-315025-300867-current-actual-ground-capture-v1-20261012'
AUTH=BASE/'government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v2-20261012'
NATIVE=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v4-20261012'
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def collect_patches(manifest):
 patches=[];refs=[];seen=set();active=set()
 def visit(data,path,pointer):
  assert path.resolve().is_relative_to(ROOT.resolve())
  key=(str(path.resolve()),pointer);assert key not in active,'terrain-child-cycle';assert key not in seen,'duplicate-terrain-child-reference';active.add(key);seen.add(key)
  patches.append(dict(data=data,path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),jsonPointer=pointer));refs.append(path)
  children=data.get('patches',[]);assert isinstance(children,list)
  for i,child in enumerate(children):
   assert isinstance(child,dict)
   if 'url'in child:
    p=ROOT/'3d-viewer'/child['url'];visit(read(p),p,'')
   else:assert 'meta'in child and 'w'in child;visit(child,path,pointer+f'/patches/{i}')
  active.remove(key)
 for item in manifest['terrainPatches']:
  path=ROOT/'3d-viewer'/item['url'];visit(read(path),path,'')
 return patches,refs

def preflight():
 assert not DOC.exists()and not(LOCAL/'private-terrain.json').exists()
 contract=read(DRAFT/'input-contract.json');refs=[Path(__file__),HERE/'southside_exact_private_terrain_adapter_v1_20261012.py',HERE/'test_southside_exact_private_terrain_adapter_v1_20261012.py',DRAFT/'METHOD.md',DRAFT/'input-contract.json'];receipts=[]
 for pin in contract['completeReceipts']:
  path=ROOT/pin['path'];assert digest(path.read_bytes())==pin['sha256'];q=read(path);assert q['jobId']==pin['jobId'];refs.append(path);receipts.append(q)
  for p in q['evidenceRefs']:
   f=ROOT/p['path'];assert digest(f.read_bytes())==p['sha256'];refs.append(f)
 for p in contract['pins']:
  path=ROOT/p['path'];assert digest(path.read_bytes())==p['sha256'];refs.append(path)
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifestpath.read_bytes())==CURRENT;manifest=read(manifestpath);refs.append(manifestpath)
 capture=read(INPUT/'capture-inputs.json.gz');assert capture['manifestSHA256']==CURRENT and len(capture['completeCurrentForms'])==46 and len(capture['canonicalResources'])==48
 bounds=[]
 for uid in UIDS:
  p=INPUT/('complete-current-actual-source-and-ground-'+uid.split('/')[1].replace(':','-')+'.json.gz');actual=read(p);refs.append(p)
  assert actual['uid']==uid and actual['startAndEndInputsVerified']and actual['completeOriginalPOSITIONProof']['allOriginalPositionVerticesAccounted']
  bounds.extend([actual['completeOriginalPOSITIONProof']['originalWholeSourceBounds'],*actual['completeWholeUnusedVertexBounds']])
  for path,sha in actual['inputHashes'].items():f=ROOT/path;assert digest(f.read_bytes())==sha;refs.append(f)
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);assert not parent.get('nativeMesh')and not parent.get('patches');refs.append(parentpath)
 cells,bb,core=adapter.nominate_cells(bounds,parent);packed=[[min(bb[0],adapter.f32(bb[0])),0,min(bb[1],adapter.f32(bb[1]))],[max(bb[2],adapter.f32(bb[2])),0,max(bb[3],adapter.f32(bb[3]))]]
 patches,patchrefs=collect_patches(manifest);refs.extend(patchrefs);intersections=adapter.parent_child_obligations([packed[0][0],packed[0][2],packed[1][0],packed[1][2]],patches)
 nativeinput=read(NATIVE/'input.json.gz');native=read(NATIVE/'inventory.json.gz');assert nativeinput['currentManifest']['sha256']==CURRENT and nativeinput['completeNativeActors']==NATIVE_COUNT and native['startAndEndInputHashesVerified']
 for path,sha in native['inputHashes'].items():p=ROOT/path;assert digest(p.read_bytes())==sha;refs.append(p)
 entries={}
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;refs.append(path)
  for entry in read(path)['models']:assert entry['uid']not in entries;entries[entry['uid']]=entry
 assert len(entries)==6649 and {r['uid']for r in nativeinput['rows']}==set(entries)and not set(UIDS)&set(entries)
 assert native['completeRecursiveProductionModuleClosure']['schema']=='exact-literal-static-dynamic-resource-closure-v1'
 actual_native_by={q['uid']:q for q in native['rows']}
 for r in nativeinput['rows']:
  assert r['rawCurrentEntry']==entries[r['uid']]and r['source']['sha256']==entries[r['uid']]['sha256']and r['currentBuilding']==nativeinput['currentAllNativeSourceForms'][r['uid']]
  actual=actual_native_by[r['uid']];assert actual['sourceSHA256']==r['source']['sha256']and actual['completeOriginalPOSITIONProof']==r['completeOriginalPOSITIONProof']and actual['completeFaces']==entries[r['uid']]['triangles']
 native_obligations=adapter.nominate_natives(packed,native)
 # Full original viewer forms in every tile touched by the changed domain are
 # retained conservatively; no BASIC exclusion is proved from metadata rings.
 tile_forms=[];tiles=[];own_forms={q['uid']:q for q in capture['completeCurrentForms']}
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];data=read(path);refs.append(path)
  # Keep a tile if any exact source-ring bound touches the proposed domain.
  hits=[]
  for form in data['buildings']:
   points=[p for ring in form['rings']for p in ring];assert points
   b=[min(p[0]for p in points),min(p[1]for p in points),max(p[0]for p in points),max(p[1]for p in points)]
   if adapter.closed_xz_touch(b,[packed[0][0],packed[0][2],packed[1][0],packed[1][2]]):hits.append(form['uid'])
  if hits:
   refs.append(path);tiles.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),rawRingNominationIds=hits))
   tile_forms.extend(data['buildings'])
  for form in data['buildings']:
   if form['uid']in own_forms:assert form==own_forms[form['uid']]
 forms={}
 for q in [*tile_forms,*capture['completeCurrentForms']]:
  if q['uid']in forms:assert forms[q['uid']]==q
  forms[q['uid']]=q
 assert set(own_forms)<=set(forms)
 resources=sorted(set(capture['canonicalResources']+['immutable-source-sheet:'+s for s in contract['completeFourSheets']]+['terrain-parent:city/data/terrain.json']+['building:'+q['uid']for q in native_obligations['nominated']]+[('building:'+u)if u.startswith('landsd/')else('source-form:'+u)for u in forms]+['terrain-parent:'+p['path'] for p in intersections]))
 sheetcontract=read(ROOT/contract['sourceSheetContract']['path']);assert sum(s['declaredCompleteSceneTerrainFacets']for s in sheetcontract['sheets'])==774477
 for s in sheetcontract['sheets']:
  for pin in [dict(path=s['originalReceiptPath'],sha256=s['originalReceiptSHA256']),dict(path=s['directoryReceiptPath'],sha256=s['directoryReceiptSHA256'])]+[dict(path=str(Path(s['folder'])/'terrain'/p['name']),sha256=p['sha256'])for p in s['allOriginalTerrainFiles']]:
   path=ROOT/pin['path'];assert digest(path.read_bytes())==pin['sha256'];refs.append(path)
 pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
 return contract,refs,pins,receipts,capture,parent,parentpath,cells,bb,core,packed,intersections,native_obligations,forms,tiles,resources,sheetcontract

def owned(state):
 contract,refs,pins,receipts,capture,parent,parentpath,cells,bb,core,packed,intersections,native_obligations,forms,tiles,resources,sheetcontract=state;lease=read(LEASE);assert reservations.owns(lease)and lease['resources']==resources
 v=read(DRAFT/'immutable-test-validation-v1/validation.json');assert v['tests']==26 and v['passed']is True and v['exitCode']==0
 required={str(p.relative_to(ROOT))for p in [Path(__file__),HERE/'southside_exact_private_terrain_adapter_v1_20261012.py',HERE/'test_southside_exact_private_terrain_adapter_v1_20261012.py',DRAFT/'METHOD.md',DRAFT/'input-contract.json']}
 assert len(v['codePins'])==5 and {p['path']for p in v['codePins']}==required
 for p in v['codePins']:assert digest((ROOT/p['path']).read_bytes())==p['sha256']
 log=DRAFT/'immutable-test-validation-v1/tests.log';assert digest(log.read_bytes())==v['testLogSHA256'];refs.extend([log,DRAFT/'immutable-test-validation-v1/validation.json'])
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for q in receipts:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(q['jobId'],)).fetchone()==('complete',q)
 decoder=module('southside_private_original_decoder',HERE/'xl-second-pass.py');decoder.LOCAL=LOCAL/'faithful-schema-preparation';pieces=[];inventory=[];offset=0
 original=read(AUTH/'complete-unfiltered-authenticated-source-ground.json.gz');assert original['completeAllOriginalSheetFacetSHA256']==FULL_TIN_SHA
 for s in sheetcontract['sheets']:
  count=0
  for f in s['allOriginalTerrainFiles']:
   p=ROOT/s['folder']/'terrain'/f['name']
   if p.suffix!='.gltf':continue
   t=np.asarray(decoder.terrain_triangles(p),dtype='<f8');assert t.ndim==3 and t.shape[1:]==(3,3)and np.isfinite(t).all()
   item=dict(sheet=s['sheet'],sourceGltfPath=str(p.relative_to(ROOT)),sourceGltfSHA256=f['sha256'],completeDecodedFacets=len(t),completeDecodedFacetSHA256=digest(t.tobytes()),globalOriginalFacetStart=offset,globalOriginalFacetEndExclusive=offset+len(t));assert item==original['completeOriginalSourceInventory'][len(inventory)]
   pieces.append(t);inventory.append(item);offset+=len(t);count+=len(t)
  assert count==s['declaredCompleteSceneTerrainFacets']
 whole=np.concatenate(pieces);assert len(whole)==774477 and digest(whole.tobytes())==FULL_TIN_SHA
 # Existing-patch overlap is recorded, never transformed into a native waiver.
 if intersections:
  proposal=None;account=adapter.blocked_inventory(whole,expected_sha256=FULL_TIN_SHA);account.update(sourceInventoryVerbatim=inventory,blockedBeforeConstructionByParentChildIntersections=intersections,physicalAccepted=False,installationApproved=False)
 else:
  proposal,account=adapter.construct(whole,parent,cells,bb,core,expected_sha256=FULL_TIN_SHA);proposal['meta'].update(parentTerrain='city/data/terrain.json',parentSha256=digest(parentpath.read_bytes()));proposal['meta']['source']=dict(nativeSources=sheetcontract['sheets'],verticalDatum='HKPD',policy='Unfiltered original source inventory, exact clipped core, explicitly changed10m parent transition; all qualification pending.')
  actual=account['wholeAlteredDomainAllPackedAndUnusedGridBounds'];assert actual[0][0]>=packed[0][0]and actual[0][2]>=packed[0][2]and actual[1][0]<=packed[1][0]and actual[1][2]<=packed[1][2]
  validator=module('southside_private_unchanged_validation',HERE/'resolve-pass-indexed-parent-clipping.py')
  try:validator.validate_patch(proposal,parent);account['ordinaryPatchValidatorDiagnostic']=dict(passed=True,physicalAccepted=False)
  except(AssertionError,ValueError)as error:account['ordinaryPatchValidatorDiagnostic']=dict(passed=False,errorType=type(error).__name__,message=str(error),originalGuardUnchanged=True,physicalAccepted=False)
  save(LOCAL/'private-terrain.json',proposal);account['privateCandidatePath']=str((LOCAL/'private-terrain.json').relative_to(ROOT));account['privateCandidateSHA256']=digest((LOCAL/'private-terrain.json').read_bytes())
 save(DOC/'source-terrain-inventory-and-proposal-account.json.gz',dict(account=account,fullOriginalInventoryVerbatim=inventory,all46FormsVerbatim=capture['completeCurrentForms'],allConservativelyRetainedTileForms=forms,fullWholeTileBASICGeometryQualificationPending=True,rawRingNominationIsNotActualBASICBoundsExclusion=True,globalBASICActualExtentNominationAndBeforeAfterQualificationPending=True,parentChildIntersections=intersections,wholeAlteredDomainProposedPackedBounds=packed,complete6649NativeNomination=native_obligations,stationForeignOverlapAnd34FacetsVerbatim=read(INPUT/'historical-obligations-verbatim.json'),all19RoleAndWholeModelQualificationPending=True,facet11034Unqualified=True,face3009Unqualified=True,sourceGeometryChanges=0,terrainExplicitlyChanged=proposal is not None,sourceRoleAccepted=False,currentAcceptance=False,physicalAccepted=False,installationApproved=False))
 assert reservations.owns(lease)and digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==CURRENT
 for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha
 previous=module('southside_original_local_module_inventory',HERE/'xl-southside-315025-300867-source-role-reconciliation-v1-20261012.py');refs.extend(previous.local_modules(decoder));refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');refs.extend(p for p in DOC.rglob('*')if p.is_file())
 freezer=module('southside_private_terrain_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');refs.extend(previous.local_modules(freezer));q=freezer.freeze(BATCH,'southside-private-authentic-terrain-proposal-complete-source-native-obligations-no-approval',refs,dict(uids=UIDS,completeInputFacets=774477,completeNativeActors=6649,currentAcceptance=False,newlyInstalled=0));print(json.dumps(dict(jobId=q['jobId'],privateCandidateCreated=proposal is not None,currentAcceptance=False)),flush=True)
def main():
 state=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(noWorker=True,noDB=True,noLease=True,noOriginalTerrainDecodeOrClipping=True,declaredOriginalFacets=774477,resources=state[-2],parentChildIntersections=state[11],nominatedCurrentNatives=[q['uid']for q in state[12]['nominated']],completeOriginalFormsRetained=len(state[13]),capturedFormsRetained=46,currentAcceptance=False)),flush=True);return
 if '--owned'in sys.argv:return owned(state)
 assert not LOCAL.exists();claim=reservations.claim('southside-private-authentic-terrain-'+str(uuid.uuid4()),state[-2],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
