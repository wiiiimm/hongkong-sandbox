"""Fresh bounded two-tower current role composition, never legacy-native approval.

Complete originals, all finite owned faces, actual roots, exact exposed carrier
interfaces, named visual-only details and current full foreign/runtime gates.
Deterministic recheck has no writes/lease acquisition; root alone publishes.
"""
import importlib.util,json,collections
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from xl_source_stream_binding_20261009 import source_stream_binding
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_rational_interface_segment_clearance_20261011 import verify as segment_clearance
from exact_original_shared_edge_component_census_v2_20261011 import census,exact_nonrendering
from cullinan_original_named_visual_details_v2_20261010 import verify as visual,sha,canonical,PARTS
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-cullinan-west-complete-current-role-v2';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-cullinan-west-three-complete-original-current-probe-v2-20261010';GRAPH=BASE/'xl-terrain-recovery-20261010-cullinan-west-three-current-original-complete-support-v1';FINITE=BASE/'xl-terrain-recovery-20261010-cullinan-west-three-current-original-literal-complete-finite-v1';INVENTORY=BASE/'xl-terrain-recovery-20261011-complete-current-native-position-inventory-v4'
CHAIN=BASE/'xl-terrain-recovery-20261011-cullinan-west-complete-owned-current-carrier-paths-v1';EXPOSE=BASE/'xl-terrain-recovery-20261011-cullinan-west-current-carrier-interface-exposure-v1';CAPS=BASE/'xl-terrain-recovery-20261010-cullinan-west-current-carrier-chain-finite-v3';ROOTS=[BASE/f'government-xl-terrain-recovery-cullinan-west-literal-ordinary-rendered-root-{i}-v2-20261011'for i in [11,51]]
EDGE=BASE/'xl-terrain-recovery-20261011-cullinan-west-credited-complete-shared-edge-census-v2';ROOTFINITE=BASE/'xl-terrain-recovery-20261011-cullinan-west-root51-complete-finite-v1'
PHYS=[BASE/f'government-xl-terrain-recovery-cullinan-west-{t}-unchanged-current-terrain-physical-v2-20261010'for t in ['tower3','tower5']];UIDS=['landsd/262871:0','landsd/161931:0','landsd/120158:0'];CURRENT='3a2f56f7980954ff3493aba5e8a015ca79153f81da55bb580e26bf5b2cdb2ee8'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def fenced(folder,numeric=None):
 r=read(folder/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 if numeric:assert ref(folder/numeric)in r['evidenceRefs'],'Exact fenced numerical output binding required'
 return r

def recheck():
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==CURRENT;current=read(manifest);catalogues={u:ref(ROOT/'3d-viewer'/u)for u in current['officialModelCatalogues']}
 refs=[ref(Path(__file__)),start];tables=[(PROBE,None),(GRAPH,'diagnostic.json.gz'),(FINITE,'diagnostic.json.gz'),(INVENTORY,'inventory.json.gz'),(CHAIN,'diagnostic.json.gz'),(EXPOSE,'diagnostic.json.gz'),(CAPS,'diagnostic.json.gz'),(EDGE,'diagnostic.json.gz'),(ROOTFINITE,'diagnostic.json.gz'),*[(p,'diagnostic.json.gz')for p in ROOTS]]
 for p,n in tables:fenced(p,n);refs.append(ref(p/'result.json'));refs.extend([ref(p/n)]if n else[])
 probe=fenced(PROBE)
 for r in probe['evidenceRefs']:assert ref(ROOT/r['path'])==r,'Fresh current probe input changed';refs.append(r)
 selected=read(PROBE/'selection.json.gz')['rows'];assert [r['uid']for r in selected]==UIDS;runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';runtime=read(runtimepath);assets=[ROOT/r['candidate']['path']for r in selected]
 for row,p in zip(selected,assets):assert digest(p.read_bytes())==row['sourceSHA256'];assert row['candidate']['entry']['sha256']==row['sourceSHA256']
 original=np.concatenate([decode_original_world_triangles(p.read_bytes())for p in assets]);literal=np.concatenate([np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in runtime['rows']]);ground=np.asarray(runtime['rows'][0]['drawnGroundGeometry']).reshape(-1,3,3);assert original.shape==literal.shape==(154603,3,3)
 g=read(GRAPH/'diagnostic.json.gz');assert sha(original)==g['binding']['completeOriginalWorldTrianglesSHA256'];assert sorted(f for c in g['components']for f in c['globalOriginalFaces'])==list(range(154603));assert len(g['components'])==296
 allfinite=read(FINITE/'diagnostic.json.gz')['rows'];finiteowned=[]
 for uid,t,r in zip(UIDS,np.split(original,[132291,142843]),runtime['rows']):
  f=next(x for x in allfinite if x['uid']==uid);actual=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];gr=np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3)
  assert f['completeOriginalWorldSHA256']==sha(t) and f['completeActualRenderedWorldSHA256']==sha(actual) and f['completeGroundSHA256']==sha(gr);assert [x['sourceFace']for x in f['allFaces']]==list(range(len(t)))
  if uid!=UIDS[0]:
   assert not f['unprovedOriginalFaceBounds']and not f['unprovedActualRenderedFaceBounds']
   for i,row in enumerate(f['allFaces']):
    for mode,tri in [('completeOriginal',t),('actualRendered',actual)]:
     p=row[mode];assert p['existingOrdinaryClearanceBoundProved']is True and p['groundProjectionCovered']is True;assert p['sourceFaceSHA256']==sha(tri[i]) and p['completeCurrentGroundSHA256']==sha(gr) and F(p['exactCertifiedLowerClearanceM'])>=F(-1,2)
   finiteowned.append(dict(uid=uid,completeFaces=len(t),completeSourceLiteralFiniteClearance=True,groundSHA256=sha(gr)))
 roots=[read(p/'diagnostic.json.gz')for p in ROOTS]
 for p,r in zip(ROOTS,roots):
  # Fresh root producer is CLI-bound. Stored root input is independently pinned
  # and literal source/terrain/component data must equal this fresh full probe.
  inp=read(ROOT/r['input']['path']);assert ref(ROOT/r['input']['path'])==r['input'];assert r['completeLiteralRenderedWorldSHA256']==sha(literal[:132291]) and r['completeDrawnGroundSHA256']==sha(ground);assert r['ordinaryLiteralSampleRootVerified']and r['component']in [11,51]
  proof=r['independentLiteralOrdinarySamples'];assert proof['supportInterfaceAccepted'] and proof['ordinaryGroundRootComponents']==[0];assert inp['part']['originalFaceIds']==g['components'][r['component']]['globalOriginalFaces'];assert np.array_equal(np.asarray(inp['part']['position']).reshape(-1,3)[np.asarray(inp['part']['index']).reshape(-1,3)],literal[inp['part']['originalFaceIds']])
 context=dict(independentLiteralOrdinaryNativeRoots=[11,51],literalRootProofs=roots,providerSourceRootStreams=[source_stream_binding(p.read_bytes())for p in assets],baselineManifestSHA256=CURRENT,postMetadataMutationRequiresFreshCurrentCapture=False)
 binding=dict(originalWorldSHA256=sha(original),literalWorldSHA256=sha(literal),float32WorldSHA256=sha(literal.astype(np.float32).astype(float)),strictGraphSHA256=canonical(g),frozenContextSHA256=canonical(context),originalProviderSourceSHA256s=[r['sourceSHA256']for r in selected])
 visualproof=visual(original,literal,literal.astype(np.float32).astype(float),g,frozen_context=context,expected_binding=binding,current_binding=binding);assert visualproof['proposalVerified'] and not visualproof['fullAcceptance']
 edge=read(EDGE/'diagnostic.json.gz');edge_bodies={};nonrendering=[]
 for mode,t in [('providerOriginal',original),('actualLiteral',literal)]:
  saved=next(r for r in edge['rows']if r['mode']==mode);assert saved['completeWorldSHA256']==sha(t);assert saved['allCreditedOriginalFaces']==129544
  by_component={}
  for record in saved['rows']:
   component=record['historicalVertexComponent'];faceids=g['components'][component]['globalOriginalFaces'];proof=census(t,faceids);assert canonical(proof)==canonical(record['sharedEdgeProof']);assert len(proof['sharedEdgeConnectedComponents'])==1,'Point-only or degenerate structural bridges forbidden'
   body=set(proof['sharedEdgeConnectedComponents'][0]);zero=set(proof['exactNonrenderingOriginalFaces']);assert body|zero==set(faceids)and not body&zero;assert all(exact_nonrendering(original[i])and exact_nonrendering(literal[i])and exact_nonrendering(literal[i].astype(np.float32).astype(float))for i in zero),'No nonrendering credit if F32 projection has nonzero area'
   by_component[component]=body;nonrendering.append(dict(mode=mode,historicalComponent=component,exactZeroAreaFaces=sorted(zero),allOriginalLiteralFloat32ZeroAreaVerified=True,rootOrBridgeCredit=False))
  assert set(by_component)==set(range(264,296))|{0,25,51};edge_bodies[mode]=by_component
 rootfinite=read(ROOTFINITE/'diagnostic.json.gz')
 for row in rootfinite['rows']:
  t=original[:132291]if row['mode']=='providerOriginal'else literal[:132291];assert row['completeWorldSHA256']==sha(t)and row['completeGroundSHA256']==sha(ground);assert row['allCompleteFiniteOrdinaryClearanceProved'];assert row['completeOriginalRootFaces']==g['components'][51]['globalOriginalFaces'];assert len(row['all49FacetProofs'])==49
  for p in row['all49FacetProofs']:
   i=p['globalOriginalFace'];proof=p['proof'];assert proof['sourceFaceSHA256']==sha(t[i])and proof['completeCurrentGroundSHA256']==sha(ground)and proof['groundProjectionCovered']and F(proof['exactCertifiedLowerClearanceM'])>=F(-1,2)
 paths=read(CHAIN/'diagnostic.json.gz');assert paths['completeOriginalWorldSHA256']==sha(original)and paths['completeLiteralWorldSHA256']==sha(literal);owned={i for i,c in enumerate(g['components'])if c['actorUID']!=UIDS[0]};assert len(owned)==32;allowed=(owned-set(PARTS))|{0,25,51};parent={int(k):v for k,v in paths['completeOwnedParents'].items()};assert set(parent)==allowed and parent[51]is None;assert set(paths['independentlySupportedOwnedStructuralComponents'])==owned-set(PARTS)
 exposure=[]
 for p in paths['completeQualifiedPositivePaths']:
  a,b=p['globalOriginalFaces'];assert p['child']in allowed and parent[p['child']]==p['parent'];assert a in g['components'][p['components'][0]]['globalOriginalFaces'] and b in g['components'][p['components'][1]]['globalOriginalFaces']
  for name,t in [('providerOriginal',original),('actualLiteral',literal)]:
   assert a in edge_bodies[name][p['components'][0]]and b in edge_bodies[name][p['components'][1]],'Credited endpoint must belong actual nonzero edge body'
   points=intersection_points(rational_face(t[a]),rational_face(t[b]));assert len(points)>=2;stored=next(m for m in p['independentSourceAndLiteralContacts']if m['mode']==name);assert [[str(x)for x in q]for q in points]==stored['exactPositiveInterfacePoints']
   if any(i in {0,25,51}for i in p['components']):
    assert len(points)==2;clear=segment_clearance(points,ground);assert clear['strictlyExposedWholePositiveInterface'];exposure.append(dict(mode=name,components=p['components'],wholeRationalSegmentProof=clear))
 for component in owned-set(PARTS):
  seen=set();cursor=component
  while cursor!=51:assert cursor not in seen and cursor in parent;seen.add(cursor);cursor=parent[cursor]
 cap=read(CAPS/'diagnostic.json.gz')
 for row in cap['rows']:
  assert row['allTwoCarrierCapsStrictlyExposed'];assert row['completeWorldSHA256']==sha(original if row['mode']=='providerOriginal'else literal)
  for c in row['faceProofs']:
   if c['globalOriginalFace']in [77581,78233]:assert c['globalOriginalFace']in edge_bodies[row['mode']][0];assert c['strictlyAboveCompleteFiniteGround'] and F(c['completeFiniteProof']['exactCertifiedLowerClearanceM'])>0 and c['completeFiniteProof']['completeCurrentGroundSHA256']==sha(ground)
 raw=[];physical=[];identities=[];allforms=set()
 for folder,uid in zip(PHYS,UIDS[1:]):
  receipt=fenced(folder);assert receipt['manifestSHA256']==CURRENT and set(receipt['reasons'])=={'ground-contact-unresolved','sampled-ground-gap-below-model-bottom'};refs.append(ref(folder/'result.json'))
  for pin in receipt['evidenceRefs']:assert ref(ROOT/pin['path'])==pin;refs.append(pin)
  row=read(folder/'selection.json.gz')['rows'][0];ctx=read(folder/'context.json.gz')['rows'][0];identity=verify_files(row,ctx,HERE/'local'/folder.name/'identity-current');assert identity['passed'];identities.append(identity)
  rt=read(HERE/'local'/folder.name/'runtime-geometry.json.gz')['rows'][0];probe_rt=next(x for x in runtime['rows']if x['uid']==uid)
  for k in ['position','index','drawnGroundGeometry']:assert np.array_equal(np.asarray(rt[k]),np.asarray(probe_rt[k]))
  f=read(folder/'foundation.json')['rows'][0];assert f['uid']==uid and f['strictFoundationAccepted'];assert f['foundation']['completeTerrainTriangles']==f['foundation']['triangles']==row['triangles'] and not f['foundation']['fullyBuriedUpwardTriangles']
  checks=read(folder/'neighbour-checks.json');assert all(r['passed']and not r['reasons']for r in checks['rows']);native=read(folder/'native-neighbour-checks.json');assert set(native['blocked'])==set(native['resolved'])=={UIDS[0]} and all(r['passed'] and not r['newlyBuried']for r in native['rows'])
  ni=read(folder/'neighbour-inputs.json.gz');allforms.update(r['building']['uid']for r in ni['rows']);assert set(r['building']['uid']for r in ni['rows'])==set(UIDS)
  for n in ['selection.json.gz','context.json.gz','identity-proofs.json','foundation.json','neighbour-inputs.json.gz','neighbour-checks.json','native-neighbour-checks.json','metrics.json','validation.json','current-source-terrain-preflight.json','terrain-candidates.json','production-module-closure.json']:refs.append(ref(folder/n))
  raw.append(dict(uid=uid,originalPhysicalReasons=receipt['reasons']));physical.append(dict(uid=uid,fullIdentityFoundationRuntimeBasicNativePassed=True,completeCurrentForms=len(ni['rows'])))
 inv=read(INVENTORY/'inventory.json.gz');assert inv['currentManifest']==start and inv['completeNativeActors']==6634;mapping={r['uid']:r for r in inv['rows']};assert len(mapping)==6634;currententries={e['uid']:(ROOT/'3d-viewer'/url,e)for url in current['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']};assert set(currententries)==set(mapping)
 fullbounds=[]
 for row,p,rt in zip(selected,assets,runtime['rows']):
  bounds=packed_world_bounds(p.read_bytes());assert bounds['sourceSHA256']==row['sourceSHA256'];pos=np.asarray(rt['position']).reshape(-1,3);f32=pos.astype(np.float32).astype(float);bb=np.asarray(bounds['originalWholeSourceBounds']);fullbounds.append(dict(uid=row['uid'],providerCompletePOSITIONProof=bounds,literalCompletePositionBounds=[pos.min(axis=0).tolist(),pos.max(axis=0).tolist()],float32CompletePositionBounds=[f32.min(axis=0).tolist(),f32.max(axis=0).tolist()]));refs.append(ref(p))
 ownlo=np.min([b['providerCompletePOSITIONProof']['originalWholeSourceBounds'][0]for b in fullbounds[1:]]+[b['literalCompletePositionBounds'][0]for b in fullbounds[1:]]+[b['float32CompletePositionBounds'][0]for b in fullbounds[1:]],axis=0);ownhi=np.max([b['providerCompletePOSITIONProof']['originalWholeSourceBounds'][1]for b in fullbounds[1:]]+[b['literalCompletePositionBounds'][1]for b in fullbounds[1:]]+[b['float32CompletePositionBounds'][1]for b in fullbounds[1:]],axis=0);touch=[]
 for uid,(catalogue,e)in currententries.items():
  item=mapping[uid];assert item['rawCurrentEntry']==e and item['catalogue']==ref(catalogue) and e['sha256']==item['sourceSHA256'];assert ref(ROOT/item['source']['path'])==item['source'];bb=np.asarray(item['completeOriginalPOSITIONProof']['originalWholeSourceBounds']);assert item['completeOriginalPOSITIONProof']['allOriginalPositionVerticesAccounted']
  if np.all(bb[1,[0,2]]>=ownlo[[0,2]])and np.all(bb[0,[0,2]]<=ownhi[[0,2]]):touch.append(uid)
 assert touch==[UIDS[0]],'Additional whole-original foreign actor requires fresh complete physical check';assert allforms==set(UIDS)
 refs.extend(catalogues.values());refs.extend(ref(HERE/n)for n in ['exact_packed_world_bounds_v3_20261010.py','exact_packed_world_geometry_20261009.py','xl_source_stream_binding_20261009.py','cullinan_original_named_visual_details_v2_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_rational_interface_segment_clearance_20261011.py','exact_original_edge_finite_facade_distance_band_v2_20261010.py','exact_original_edge_finite_facade_distance_band_20261010.py','xl-terrain-recovery-20261011-cullinan-west-literal-ordinary-native-roots-v2.py','exact_original_shared_edge_component_census_v2_20261011.py','test_exact_original_shared_edge_component_census_v2_20261011.py'])
 for p in [manifest,*[ROOT/'3d-viewer'/u for u in current['officialModelCatalogues']]]:assert ref(p)==(start if p==manifest else catalogues[str(p.relative_to(ROOT/'3d-viewer'))])
 for r in {r['path']:r for r in refs}.values():assert ref(ROOT/r['path'])==r
 nativeentry=currententries[UIDS[0]][1];acquisition=dict(selected[0]['candidate']['entry']);assert acquisition.pop('datasetId')=='landsd_rcd_1742809441342_98380';assert acquisition.pop('coordinatePolicy')=='Unchanged native source nodes/float bits; one city translation, no terrain draping or vertical multiplier';assert acquisition==nativeentry and nativeentry['sha256']==selected[0]['sourceSHA256'] and nativeentry['publicationApproved']is False and nativeentry['buildingCSUID']=='3389220874P20180705'
 support=dict(uid=UIDS[0],csuid=nativeentry['buildingCSUID'],sourceSHA256=nativeentry['sha256'],completeOriginalFaces=132291,qualification='current-native-availability-with-source-bound-exposed-interface-support-only',installedVerified=False,wholeNativeReaccepted=False)
 return dict(completeCurrentInstalledNativeEntryPreserved=nativeentry,mandatoryInstalledNativeSupport=support,currentOwnedIdentities=identities,currentTypedPhysicalAccepted=True,reasons=[],completeOriginalFaces=22312,completeOriginalComponents=32,completeCurrentNeighbourForms=3,currentNativeReacceptance=False,terrainProposal=[],terrainProposalGeometryChanged=False,contract='cullinan-two-owned-complete-current-source-qualified-original-native-support-and-visual-accounting-v2',uids=UIDS[1:],retainedNativeUID=UIDS[0],currentManifest=start,scriptChecksPassed=True,readyForStagedBrowser=True,browserAcceptanceRequired=True,installationApproved=False,newlyInstalled=0,wholeOwnedOriginalFaces=22312,wholeOwnedComponents=32,independentlyRootedStructuralOwnedComponents=29,visualOnlyOwnedComponents=[270,294,295],completeSourceLiteralFiniteOwnedProofs=finiteowned,exactNonzeroEdgeBodyProof=ref(EDGE/'diagnostic.json.gz'),originalLiteralFloat32NonrenderingAccounting=nonrendering,completeNativeCarrierRenderableFaces=len(edge_bodies['providerOriginal'][0]),completeNativeRoot49FiniteProof=ref(ROOTFINITE/'diagnostic.json.gz'),completeWholeOriginalLiteralFloat32ProtectedActors=fullbounds,completeFreshForeignNativeCensus=touch,completeCurrentForms=sorted(allforms),completeCurrentPhysical=physical,rawPhysicalReasonsPreserved=raw,rawNativeConservativeUnprovedFaces=len(allfinite[0]['unprovedOriginalFaceBounds']),rawNativeUnrootedComponents=paths['all90NativeUnresolvedComponentsPreserved'],nativeReacceptance=False,sourceGeometryChanges=0,terrainProposalChanges=0,addedRoots=[],addedLoadBearingBridges=[],namedVisualProof=visualproof,independentCompletePositiveInterfaceExposure=exposure,fullAcceptance=False,evidenceRefs=list({r['path']:r for r in refs}.values()))

def main():
 assert not DOC.exists();result=recheck();save(DOC/'typed-role.json.gz',result);s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-fresh-current-cullinan-two-original-qualified-native-support-and-named-visual-role-v2',[ROOT/r['path']for r in result['evidenceRefs']]+[DOC/'typed-role.json.gz'],dict(uids=result['uids'],scriptChecksPassed=True,wholeOwnedOriginalFaces=22312,completeOwnedComponents=32,ownedVisualComponents=[270,294,295],nativeReacceptance=False,installationApproved=False,newlyInstalled=0))
if __name__=='__main__':main()
