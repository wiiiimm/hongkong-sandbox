"""File-bound complete Mount pair current qualification, staged browser required.

Every original source face/body is retained. Main podium finite grade and clear
caps ground only the 764 independently nonvisual paths; 204+2 backing details
and three complete open-bottom roof perimeters remain separate named roles.
Original source geometry/root/pose stays unchanged. No live publication occurs.
"""
from pathlib import Path
import importlib.util,json
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from xl_source_stream_binding_20261009 import source_stream_binding
from exact_original_georef_cell_identity_20261009 import verify_files
from mount_verdant_current_pair_role_composition_v1_20261011 import verify as compose,canonical,sha,SOURCE_T,SOURCE_P
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-mount-verdant-pair-complete-current-role-v1';DOC=BASE/BATCH
CURRENT='b61c0bc2d706793c7d436ef3334ccb41e93675d3d50c29818a2dca3b56f8830e'
UIDS=['landsd/261717:0','landsd/75782:0'];SOURCES=[SOURCE_T,SOURCE_P]
PHYSICAL=BASE/'government-xl-terrain-recovery-mount-verdant-pair-authentic-current-v1-20261011'
INPUT=BASE/'xl-terrain-recovery-20261011-mount-verdant-pair-current-inputs-v1'
CAPTURE=BASE/'xl-terrain-recovery-20261011-mount-verdant-two-current-render-attribute-capture-v2'
FINITE=BASE/'xl-terrain-recovery-20261011-mount-verdant-pair-current-four-stream-finite-grade-v1'
GRAPH=BASE/'xl-terrain-recovery-20261011-mount-verdant-complete-original-edge-contact-graph-v1'
RESTRICTED=BASE/'xl-terrain-recovery-20261011-mount-verdant-four-stream-restricted-source-contacts-v1'
ROOFS=BASE/'xl-terrain-recovery-20261011-mount-verdant-three-open-bottom-four-stream-roof-perimeters-v1'
BACKS=BASE/'xl-terrain-recovery-20261011-mount-verdant-204-four-stream-named-back-visual-proposals-v1'
INVENTORY=BASE/'xl-terrain-recovery-20261011-complete-current-native-position-inventory-v9'
VALIDATION=BASE/'xl-terrain-recovery-20261011-mount-verdant-pair-composition-code-validation-v1'

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def fenced(folder,names=()):
 r=read(folder/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for name in names:assert ref(folder/name) in r['evidenceRefs']
 return r

def recheck():
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==CURRENT;current=read(manifest);refs=[ref(Path(__file__)),start]
 for folder,names in [(PHYSICAL,()),(INPUT,('check-selection.json.gz','context.json.gz')),(CAPTURE,('actual-render-attributes.json.gz',)),(FINITE,('diagnostic.json.gz',)),(GRAPH,('diagnostic.json.gz',)),(RESTRICTED,('diagnostic.json.gz',)),(ROOFS,('diagnostic.json.gz',)),(BACKS,('diagnostic.json.gz',)),(INVENTORY,('inventory.json.gz',))]:
  fenced(folder,names);refs.append(ref(folder/'result.json'));refs.extend(ref(folder/n) for n in names)
 # Fresh physical/capture inputs remain pinned. Older source-only numerical
 # receipts are reused only after the exact complete representation checks below.
 for folder in [PHYSICAL,INPUT,CAPTURE]:
  for pin in read(folder/'result.json')['evidenceRefs']:assert ref(ROOT/pin['path'])==pin;refs.append(pin)
 rows=read(PHYSICAL/'selection.json.gz')['rows'];rtpath=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';runtime=read(rtpath)['rows'];actual=read(CAPTURE/'actual-render-attributes.json.gz')['rows'];contexts={r['uid']:r for r in read(INPUT/'context.json.gz')['rows']}
 assert [r['uid'] for r in rows]==[r['uid'] for r in runtime]==[r['uid'] for r in actual]==UIDS and set(contexts)==set(UIDS)
 worlds=[[],[],[],[]];positions=[];identity=[]
 for k,(row,rt,a,count,source) in enumerate(zip(rows,runtime,actual,[14938,641],SOURCES)):
  assert row['uid']==rt['uid']==a['uid']==UIDS[k] and row['sourceSHA256']==rt['sourceSHA256']==a['sourceSHA256']==source
  asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==row['candidate']['entry']['sha256']==source;refs.append(ref(asset));positions.append(packed_world_bounds(asset.read_bytes()))
  identity.append(verify_files(row,contexts[row['uid']],HERE/'local'/PHYSICAL.name/('typed-exact-identity-'+str(k))))
  assert identity[-1]['passed'] and identity[-1]['proof']['identityAccepted']
  ix=np.asarray(rt['index'],int).reshape(-1,3);assert len(ix)==count and rt['index']==a['completeOriginalIndex'];assert np.array_equal(np.asarray(rt['position']),np.asarray(a['completeLiteralWorldPosition']))
  worlds[0].append(decode_original_world_triangles(asset.read_bytes()))
  for j,key in enumerate(['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition'],1):worlds[j].append(np.asarray(a[key],float).reshape(-1,3)[ix])
 worlds=[np.concatenate(p) for p in worlds];assert all(w.shape==(15579,3,3) and np.isfinite(w).all() for w in worlds)
 g=read(GRAPH/'diagnostic.json.gz');assert g['binding']['completeOriginalWorldSHA256']==sha(worlds[0])
 finite=read(FINITE/'diagnostic.json.gz');restricted=read(RESTRICTED/'diagnostic.json.gz');roofs=read(ROOFS/'diagnostic.json.gz')
 roles=[];modes=['providerOriginal','capturedLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'];roofmodes=['untouched-provider-original','captured-literal','explicit-left-associated-Float32','explicit-balanced-Float32']
 pground=np.asarray(runtime[1]['drawnGroundGeometry'],float).reshape(-1,3,3)
 for mode,roofmode,world in zip(modes,roofmodes,worlds):
  f=[next(r for r in finite['rows'] if r['uid']==uid and r['mode']==mode) for uid in UIDS]
  for i,r in enumerate(f):assert r['completeActualDrawnGroundSHA256']==sha(np.asarray(runtime[i]['drawnGroundGeometry'],float).reshape(-1,3,3))
  r=next(p for p in restricted['rows'] if p['mode']==mode);assert r['complete15579WorldSHA256']==sha(world)
  roof=[p for p in roofs['allThreeCompleteOpenBottomsEveryFourStreams'] if p['mode']==roofmode]
  bind=dict(sourceSHA256ByUID=dict(zip(UIDS,SOURCES)),complete15579WorldSHA256=sha(world),complete973ComponentsSHA256=canonical(g['components']),completeZeroFaceIDsSHA256=canonical(g['exactNonrenderingGlobalFacesRetained']),completeCurrentFiniteRowsSHA256=canonical(f),restrictedNonvisualSourceGraphSHA256=canonical(r),completeRoofPerimeterTemplatesSHA256=canonical(roof),completeActualPodiumGroundSHA256=sha(pground))
  roles.append(compose(world,mode,g['components'],g['exactNonrenderingGlobalFacesRetained'],f,r,roof,pground,expected_binding=bind,current_binding=bind))
 foundations=read(PHYSICAL/'foundation.json')['rows'];metrics=read(PHYSICAL/'metrics.json')['rows'];checks=read(PHYSICAL/'validation.json')
 assert [r['uid'] for r in foundations]==[r['uid'] for r in metrics]==UIDS
 for uid,source,count,f,m in zip(UIDS,SOURCES,[14938,641],foundations,metrics):
  assert f['uid']==m['uid']==uid and f['sourceSHA256']==source and f['strictFoundationAccepted'] is True
  assert f['foundation']['completeTerrainTriangles']==f['foundation']['triangles']==count and f['foundation']['fullyBuriedUpwardTriangles']==0
  assert m['sourcePreserved'] is True and m['missingTerrain']==0 and m['maxSamplerDelta']<=.004
 assert type(checks['models']) is int and checks['models']==checks['loaderAccepted']==checks['checksPassed']==2 and checks['exceptions']==0
 assert [r['uid'] for r in checks['results']]==UIDS and all(r['outcome']=='runtime-accepted-placement-unreviewed' and r['triangles']==count for r,count in zip(checks['results'],[14938,641]))
 neighbours=read(PHYSICAL/'neighbour-checks.json');inputs=read(PHYSICAL/'neighbour-inputs.json.gz');assert len(neighbours['rows'])==len(inputs['rows'])==13
 assert all(not r['reasons'] for r in neighbours['rows']) and not any(r['existingNative'] for r in inputs['rows'])
 native=read(PHYSICAL/'native-neighbour-checks.json');assert not native['blocked'] and not native['resolved'] and not native['rows']
 candidate=read(PHYSICAL/'terrain-candidates.json');assert len(candidate)==1 and candidate[0]['uids']==UIDS;c=candidate[0];assert ref(ROOT/c['path'])['sha256']==c['sha256']=='00afbe63bb404dc325923596687ccb398f8c4600703b465cbfcb94dbad13468b';assert 'replaces' not in c
 # Complete current POSITION/source inventory, not catalogue metadata bounds.
 inv=read(INVENTORY/'inventory.json.gz');assert inv['currentManifest']==start and inv['completeNativeActors']==6640 and inv['allOriginalPOSITIONVerticesIncluded'] is True
 entries={};cats=[]
 for url in current['officialModelCatalogues']:
  cp=ROOT/'3d-viewer'/url;cats.append(ref(cp))
  for entry in read(cp)['models']:assert entry['uid'] not in entries;entries[entry['uid']]=(cp,entry)
 assert len(entries)==6640 and not set(UIDS)&set(entries);mapping={r['uid']:r for r in inv['rows']};assert set(mapping)==set(entries)
 touched=[]
 for uid,(cp,e) in entries.items():
  item=mapping[uid];assert item['rawCurrentEntry']==e and item['catalogue']==ref(cp) and item['sourceSHA256']==e['sha256'];assert ref(ROOT/item['source']['path'])==item['source']
  b=item['completeOriginalPOSITIONProof'];assert b['sourceSHA256']==e['sha256'] and b['allOriginalPositionVerticesAccounted'] is True
  bb=np.asarray(b['originalWholeSourceBounds']);region=c['bounds']
  if bb[1,0]>=region[0] and bb[0,0]<=region[2] and bb[1,2]>=region[1] and bb[0,2]<=region[3]:touched.append(uid)
 assert not touched,'A whole original native source touches candidate terrain but has no complete current check'
 raw=read(PHYSICAL/'current-pair-physical-diagnostic.json')['rawReasons'];assert set(raw)=={'landsd/261717:0:ground-contact-unresolved','landsd/261717:0:sampled-ground-gap-below-model-bottom','landsd/75782:0:sampled-terrain-above-model-bottom','landsd/75782:0:terrain-intersects-source-over-0.5m'}
 refs.extend(cats);refs.extend(ref(p) for p in [rtpath,ROOT/c['path'],PHYSICAL/'terrain-candidates.json',PHYSICAL/'current-pair-physical-diagnostic.json',VALIDATION/'validation-versions.json'])
 for p in VALIDATION.iterdir():assert p.is_file();refs.append(ref(p))
 helpers=['mount_verdant_current_pair_role_composition_v1_20261011.py','test_mount_verdant_current_pair_role_composition_v1_20261011.py','mount_verdant_204_original_complete_back_visual_proposals_v1_20261011.py','mount_verdant_204_exact_original_back_visual_proposal_membership_v1_20261011.json','mount_verdant_original_two_back_mounted_visual_proposals_v1_20261011.py','original_open_roof_perimeter_band_accounting_20261009.py','exact_packed_world_bounds_v3_20261010.py','xl_source_stream_binding_20261009.py']
 refs.extend(ref(HERE/n) for n in helpers);assert all(ref(ROOT/p['path'])==p for p in refs) and ref(manifest)==start
 return dict(contract='mount-verdant-complete-current-original-literal-two-explicit-float32-pair-typed-qualification-v1',uids=UIDS,currentManifest=start,sourceSHA256ByUID=dict(zip(UIDS,SOURCES)),completeOriginalFaces=15579,completeOriginalNonzeroBodies=973,exactNonrenderingOriginalFacesUncredited=g['exactNonrenderingGlobalFacesRetained'],completeFourStreamComposition=roles,currentOwnedIdentities=identity,completeWholeOriginalPOSITIONProofs=positions,completeOriginalProviderRootAndStreams=[source_stream_binding((ROOT/r['candidate']['path']).read_bytes()) for r in rows],completeCurrentNativeWholePOSITIONInventory=ref(INVENTORY/'inventory.json.gz'),wholeOriginalNativeTerrainTouchCensus=touched,completeCurrentForeignForms=13,allRawPhysicalReasonsPreserved=raw,currentTypedPhysicalAccepted=True,reasons=[],scriptChecksPassed=True,readyForStagedBrowser=True,browserAcceptanceRequired=True,terrainProposal=candidate,terrainProposalGeometryChanged=True,sourceGeometryChanges=0,visualRootOrBridgeCredit=False,nativeReacceptance=False,explicitArithmeticNotUniversalGPUCameraGuarantee=True,fullAcceptance=False,installationApproved=False,newlyInstalled=0,evidenceRefs=list({p['path']:p for p in refs}.values()))

def main():
 assert not DOC.exists();result=json.loads(json.dumps(recheck()));save(DOC/'typed-role.json.gz',result)
 spec=importlib.util.spec_from_file_location('freeze_mount_current_pair',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'complete-current15579-973body-four-stream-main-podium-grade-restricted-nonvisual-roof-and-backing-role-v1',[ROOT/p['path'] for p in result['evidenceRefs']]+[DOC/'typed-role.json.gz'],dict(uids=UIDS,scriptChecksPassed=True,completeOriginalFaces=15579,completeOriginalNonzeroBodies=973,sourceGeometryChanges=0,currentBrowserAcceptanceRequired=True,installationApproved=False,newlyInstalled=0))

if __name__=='__main__':main()
