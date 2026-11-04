"""Draft only: exact Elements complete roles plus fresh regional current fences.

Frozen d152 numerical proofs stay historical. A separately fenced King additive
regional certificate must prove unchanged old catalogues/assets/terrain/modules
and disjoint whole original/literal/two-F32 geometry before current credit.
No native reapproval, source geometry edit, visual support or publication.
"""
from pathlib import Path
import importlib.util,json
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from xl_source_stream_binding_20261009 import source_stream_binding
import elements998_complete_original_role_composition_v3_20261011 as composition
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-elements-pair-complete-current-role-v2';DOC=BASE/BATCH
CURRENT='de8db939e48be0ed3661a9f3bf59454d92ff27f4a1024f34a401b17612e03e54'
BASELINE='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43'
UIDS=composition.UIDS;NATIVES=['landsd/273061:0','landsd/204144:0'];COUNTS=[12129,11680]
PHYSICAL=BASE/'government-xl-terrain-recovery-elements-sun-star-unchanged-current-physical-v1-20261011'
LOCAL=HERE/'local'/PHYSICAL.name
CAPTURE=BASE/'xl-terrain-recovery-20261011-elements-sun-star-two-current-render-attribute-capture-v1'
NATIVE_CAPTURE=BASE/'xl-terrain-recovery-20261011-elements-two-native-current-render-ground-capture-v1'
REGIONAL=BASE/'xl-terrain-recovery-20261011-elements-king-additive-current-regional-proof-v2'
INVENTORY=BASE/'xl-terrain-recovery-20261011-complete-current-native-position-inventory-v10'
VALIDATION=BASE/'xl-terrain-recovery-20261011-elements998-composition-code-validation-v2'
NAMES=dict(graph='elements-complete-owned-original-contact-graph-v1',finite='elements-owned-four-stream-complete-finite-v1',paths='elements-bounded-owned-four-stream-path-replay-v1',caps='elements998-bounded-four-stream-grade-cap-paths-v1',lateral='elements31-complete-lateral-patches-and39-disposition-v1',named24='elements24-named-original-visual-proposals-v1',named4='elements4-named-complete-perimeter-visual-sheet-proposals-v1',named11='elements11-named-original-visual-placement-proposals-v1')

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def fenced(folder,names=()):
 r=read(folder/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for n in names:assert ref(folder/n)in r['evidenceRefs']
 return r

def check_pin(pin,aliases):
 p=ROOT/pin['path']
 if p.exists()and ref(p)==pin:return p
 matches=[a for a in aliases if a['original']==pin];assert len(matches)==1
 archived=ROOT/matches[0]['archive']['path'];assert ref(archived)==matches[0]['archive']and ref(archived)['sha256']==pin['sha256']
 assert pin['path']=='3d-viewer/city/data/manifest.json'and pin['sha256']==BASELINE
 return archived

def recheck(local=None):
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==CURRENT
 regional_receipt=fenced(REGIONAL,('diagnostic.json.gz',));regional=read(REGIONAL/'diagnostic.json.gz')
 assert regional['currentManifest']==start and regional['baselineManifest']['sha256']==BASELINE
 assert regional['soleAddedUID']=='landsd/95691:0'and regional['completeCurrentNativeActors']==6643
 assert all(regional[n]is True for n in ['all6642PriorRawEntriesAndAssetsUnchanged','allPriorCatalogueBytesUnchanged','allPreviousTerrainBytesUnchanged','allCurrentRegionalFormsUnchanged','allProductionModuleBytesUnchanged','completeOwnedAndRetainedOriginalLiteralBothF32RegionCovered','addedCompleteOriginalPOSITIONLiteralBothF32BoundsStrictlyDisjoint'])
 aliases=regional['exactHistoricalManifestAliases'];assert len(aliases)==1
 refs=[ref(Path(__file__)),start,ref(REGIONAL/'result.json'),ref(REGIONAL/'diagnostic.json.gz')]
 # Every old numerical dependency remains recursive and exact. Only the one
 # historical manifest byte version resolves to its explicit original archive.
 for folder,names in [(PHYSICAL,()),(CAPTURE,('actual-render-attributes.json.gz',)),(NATIVE_CAPTURE,('native-render-ground.json.gz',)),(INVENTORY,('inventory.json.gz',))]:
  receipt=fenced(folder,names);refs.append(ref(folder/'result.json'))
  for pin in receipt['evidenceRefs']:refs.append(ref(check_pin(pin,aliases)))
 data={}
 for key,name in NAMES.items():
  folder=BASE/('xl-terrain-recovery-20261011-'+name);receipt=fenced(folder,('diagnostic.json.gz',));data[key]=read(folder/'diagnostic.json.gz');refs.extend([ref(folder/'result.json'),ref(folder/'diagnostic.json.gz')])
  for pin in receipt['evidenceRefs']:refs.append(ref(check_pin(pin,aliases)))
 rows=read(PHYSICAL/'selection.json.gz')['rows'];runtime=read(LOCAL/'runtime-geometry.json.gz')['rows'];actual=read(CAPTURE/'actual-render-attributes.json.gz')['rows'];contexts={r['uid']:r for r in read(PHYSICAL/'context.json.gz')['rows']}
 assert [r['uid']for r in rows]==[r['uid']for r in runtime]==[r['uid']for r in actual]==UIDS and set(contexts)==set(UIDS)
 worlds={m:[]for m in composition.MODES};identities=[];positions=[]
 for row,rt,a,count in zip(rows,runtime,actual,COUNTS):
  uid=row['uid'];source=composition.SOURCE_SHA[uid];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes()
  assert row['uid']==rt['uid']==a['uid']==uid and row['sourceSHA256']==rt['sourceSHA256']==a['sourceSHA256']==digest(raw)==source
  assert row['candidate']['entry']['sha256']==source and row['triangles']==count
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
  identities.append(verify_files(row,contexts[uid],(local or LOCAL)/('typed-current-identity-'+uid.split('/')[1].replace(':','-'))));assert identities[-1]['passed']and identities[-1]['proof']['identityAccepted']
  ix=np.asarray(rt['index'],int).reshape(-1,3);assert len(ix)==count and rt['index']==a['completeOriginalIndex']and np.array_equal(np.asarray(rt['position']),np.asarray(a['completeLiteralWorldPosition']))
  worlds['providerOriginal'].append(decode_original_world_triangles(raw));positions.append(packed_world_bounds(raw));refs.append(ref(asset))
  for mode,key in zip(composition.MODES[1:],['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']):worlds[mode].append(np.asarray(a[key],float).reshape(-1,3)[ix])
 worlds={m:np.concatenate(w)for m,w in worlds.items()}
 # Independently bind all native source/render worlds to the exact bounded
 # grade-cap records. Availability alone supplies no native root or reapproval.
 native_rows=read(NATIVE_CAPTURE/'native-render-ground.json.gz')['rows'];assert [r['uid']for r in native_rows]==NATIVES
 retained=read(PHYSICAL/'current-source-terrain-preflight.json')['completeRetainedNativeEntries']
 native_worlds={m:{}for m in composition.MODES}
 for nr,ncount in zip(native_rows,[203738,11166]):
  pin=next(r for r in retained if r['uid']==nr['uid']);asset=ROOT/pin['source']['path'];raw=asset.read_bytes();assert ref(asset)==pin['source']and digest(raw)==nr['sourceSHA256']==pin['entry']['sha256']and nr['rawCurrentNativeEntry']==pin['entry']
  nix=np.asarray(nr['completeOriginalIndex'],int).reshape(-1,3);assert len(nix)==ncount
  native_worlds['providerOriginal'][nr['uid']]=decode_original_world_triangles(raw)
  for mode,key in zip(composition.MODES[1:],['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']):native_worlds[mode][nr['uid']]=np.asarray(nr[key],float).reshape(-1,3)[nix]
  assert all(native_worlds[m][nr['uid']].shape==(ncount,3,3)and np.isfinite(native_worlds[m][nr['uid']]).all()for m in composition.MODES)
 ground=np.asarray(native_rows[0]['drawnGroundGeometry'],float).reshape(-1,3,3);ground_sha=composition.world_sha(ground)
 assert data['finite']['completeCapturedNativeGroundSHA256']==ground_sha and data['finite']['completeCapturedNativeGroundFaces']==len(ground)
 for mode in composition.MODES:
  cap=next(r for r in data['caps']['rows']if r['mode']==mode);assert cap['completeGroundSHA256']==ground_sha
  for uid,offset,count in zip(UIDS,[0,12129],COUNTS):assert cap['completeWorldSHA256'][uid]==composition.world_sha(worlds[mode][offset:offset+count])
  for uid in NATIVES:assert cap['completeWorldSHA256'][uid]==composition.world_sha(native_worlds[mode][uid])
 bound=composition.binding(worlds=worlds,**data)
 role=composition.verify(worlds=worlds,**data,expected_binding=bound)
 assert role['completeStructuralPathBodies']==866 and role['completeNonstructuralVisualBodies']==132 and role['completeNonzeroOriginalBodies']==998 and len(role['all47OriginalZeroFacetsPreservedUncredited'])==47
 foundations=read(PHYSICAL/'foundation.json')['rows'];metrics=read(PHYSICAL/'metrics.json')['rows'];validation=read(PHYSICAL/'validation.json')
 assert [r['uid']for r in foundations]==[r['uid']for r in metrics]==UIDS
 for uid,count,f,m in zip(UIDS,COUNTS,foundations,metrics):
  assert f['sourceSHA256']==composition.SOURCE_SHA[uid]and f['strictFoundationAccepted']is True and f['foundation']['completeTerrainTriangles']==f['foundation']['triangles']==count and f['foundation']['fullyBuriedUpwardTriangles']==0 and f['foundation']['fullyBuriedAreaFraction']==0
  assert m['sourcePreserved']is True and m['missingTerrain']==0 and m['maxSamplerDelta']<=.004
 assert validation['models']==validation['loaderAccepted']==validation['checksPassed']==2 and validation['exceptions']==0
 assert [r['uid']for r in validation['results']]==UIDS and all(r['outcome']=='runtime-accepted-placement-unreviewed'and r['triangles']==n for r,n in zip(validation['results'],COUNTS))
 checks=read(PHYSICAL/'neighbour-checks.json');inputs=read(PHYSICAL/'neighbour-inputs.json.gz');assert len(checks['rows'])==8 and all(not r['reasons']for r in checks['rows'])
 native=read(PHYSICAL/'native-neighbour-checks.json');assert not(set(native['blocked'])-set(native['resolved']))
 raw=read(PHYSICAL/'result.json')['reasons'];assert set(raw)=={u+':'+r for u in UIDS for r in ['ground-contact-unresolved','sampled-ground-gap-below-model-bottom']}
 assert read(PHYSICAL/'terrain-candidates.json')==[]
 current=read(manifest);entries={};catrefs=[]
 for url in current['officialModelCatalogues']:
  cp=ROOT/'3d-viewer'/url;catrefs.append(ref(cp))
  for e in read(cp)['models']:assert e['uid']not in entries;entries[e['uid']]=(cp,e)
 assert len(entries)==6643 and not set(UIDS)&set(entries)and set(NATIVES)<=set(entries)
 inv=read(INVENTORY/'inventory.json.gz');assert inv['currentManifest']['sha256']==BASELINE and inv['completeNativeActors']==6642 and inv['allOriginalPOSITIONVerticesIncluded']is True
 old={r['uid']:r for r in inv['rows']};assert set(entries)==set(old)|{'landsd/95691:0'}
 for uid,item in old.items():
  cp,e=entries[uid];assert item['rawCurrentEntry']==e and item['catalogue']==ref(cp)and item['sourceSHA256']==e['sha256']and ref(ROOT/item['source']['path'])==item['source'];assert item['completeOriginalPOSITIONProof']['allOriginalPositionVerticesAccounted']is True
 preflight=read(PHYSICAL/'current-source-terrain-preflight.json')
 for item in preflight['completeRetainedNativeEntries']:
  cp,e=entries[item['uid']];assert ref(cp)==item['catalogue']and e==item['entry']and ref(ROOT/item['source']['path'])==item['source']
 assert regional['completeRetainedNativeEntries']==preflight['completeRetainedNativeEntries']
 assert regional['currentWholeSourceTouchUIDs']==sorted(NATIVES)and regional['unchangedCompleteRegionalForeignUIDs']==sorted(r['building']['uid']for r in inputs['rows'])
 refs.extend(catrefs);refs.extend(ref(p)for p in [LOCAL/'runtime-geometry.json.gz',PHYSICAL/'foundation.json',PHYSICAL/'metrics.json',PHYSICAL/'validation.json',PHYSICAL/'neighbour-checks.json',PHYSICAL/'native-neighbour-checks.json',PHYSICAL/'current-source-terrain-preflight.json'])
 for p in sorted(VALIDATION.rglob('*')):
  if p.is_file():refs.append(ref(p))
 assert (VALIDATION/'validation-versions.json').is_file()
 refs.extend(ref(HERE/n)for n in ['elements998_complete_original_role_composition_v1_20261011.py','test_elements998_complete_original_role_composition_v1_20261011.py','elements998_complete_original_role_composition_v2_20261011.py','test_elements998_complete_original_role_composition_v2_20261011.py','elements998_complete_original_role_composition_v3_20261011.py','test_elements998_complete_original_role_composition_v3_20261011.py','exact_packed_world_bounds_v3_20261010.py','exact_original_georef_cell_identity_20261009.py','xl_source_stream_binding_20261009.py'])
 assert all(ref(ROOT/p['path'])==p for p in refs)and ref(manifest)==start
 return dict(contract='elements-two-complete-original-current-regional-and998-typed-role-v2',uids=UIDS,currentManifest=start,numericBaselineManifestSHA256=BASELINE,sourceSHA256ByUID=composition.SOURCE_SHA,completeOriginalFaces=23809,completeOriginalNonzeroBodies=998,complete47OriginalZerosPreservedUncredited=role['all47OriginalZeroFacetsPreservedUncredited'],complete998FourStreamRoleComposition=role,currentOwnedIdentities=identities,completeWholeOriginalPOSITIONProofs=positions,completeOriginalProviderRootAndStreams=[source_stream_binding((ROOT/r['candidate']['path']).read_bytes())for r in rows],completeRegionalCurrentProof=ref(REGIONAL/'diagnostic.json.gz'),completeCurrentNativeWholePOSITIONBaseline=ref(INVENTORY/'inventory.json.gz'),completeCurrentNativeActors=6643,retainedNativeExactEntries=preflight['completeRetainedNativeEntries'],allRawPhysicalReasonsPreserved=raw,sourceGeometryChanges=0,terrainProposal=[],terrainProposalGeometryChanged=False,currentTypedPhysicalAccepted=True,reasons=[],scriptChecksPassed=True,readyForStagedBrowser=True,browserAcceptanceRequired=True,nativeReacceptance=False,visualRootBridgeOrHostCredit=False,explicitArithmeticNotUniversalGPUCameraGuarantee=True,fullAcceptance=False,installationApproved=False,newlyInstalled=0,evidenceRefs=list({p['path']:p for p in refs}.values()))

def main():
 assert not DOC.exists();typed=json.loads(json.dumps(recheck()));save(DOC/'typed-role.json.gz',typed)
 spec=importlib.util.spec_from_file_location('freeze_elements_current_role',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'complete-elements998-four-stream-current-regional-role-v2',[ROOT/p['path']for p in typed['evidenceRefs']]+[DOC/'typed-role.json.gz'],dict(uids=UIDS,completeOriginalFaces=23809,completeOriginalNonzeroBodies=998,currentBrowserAcceptanceRequired=True,scriptChecksPassed=True,installationApproved=False,newlyInstalled=0))
if __name__=='__main__':main()
