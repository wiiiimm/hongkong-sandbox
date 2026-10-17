"""Source-bounded Parkview current acceptance; no whole native approval.

Only the exact exposed grade wall60989→cap57951→owned face0 native path is
credited. All 80 structural owned parts independently connect by unchanged
positive-dimensional original contacts through wholly clear owned faces.
The 72-face unit324 retains its complete source topology as visual-only.
"""
import importlib.util,json,collections
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from xl_source_stream_binding_20261009 import source_stream_binding
from exact_original_shared_edge_component_census_v2_20261011 import census,exact_nonrendering
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
from exact_original_georef_cell_identity_20261009 import verify_files
from parkview_original_roof_unit324_visual_accounting_v1_20261011 import verify as unit,canonical,sha,FACES,SOURCE
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-parkview-block11-current-role-v1';DOC=BASE/BATCH
CURRENT='aba0edb60daac0497b98c78d21507461b13b20a4ddcc177ca0526fabeaa86eef';UID='landsd/255647:0';NATIVE='landsd/254491:0';RETAINED=['landsd/254491:0','landsd/255439:0','landsd/256112:0','landsd/256114:0']
PHYSICAL=BASE/'government-xl-terrain-recovery-parkview-block11-authentic-retained-current-physical-v2-20261011';PROBE=BASE/'government-xl-terrain-recovery-parkview-block11-complete-original-proposed-current-probe-v4-20261011';FINITE=BASE/'xl-terrain-recovery-20261011-parkview-owned-current-four-stream-finite-v1';ACTUAL=BASE/'xl-terrain-recovery-20261011-parkview-owned-actual-render-capture-v1';CARRIER=BASE/'xl-terrain-recovery-20261011-parkview-current-bounded-carrier-grade-cap-v1'
GRAPH=BASE/'xl-terrain-recovery-20261010-parkview-block11-complete-original-support-v1';PATHS=BASE/'xl-terrain-recovery-20261011-parkview-owned-complete-edge-carrier-paths-v1';UNIT=BASE/'xl-terrain-recovery-20261011-parkview-original-roof-unit324-interface-v1';INVENTORY=BASE/'xl-terrain-recovery-20261011-complete-current-native-position-inventory-v5';PROPOSAL=BASE/'xl-terrain-recovery-20261011-parkview-authentic-foreign-preserved-terrain-proposal-v4';BOUNDS=BASE/'xl-terrain-recovery-20261011-parkview-authentic-current-retained-terrain-proposal-v3'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def fenced(folder,numeric=None):
 r=read(folder/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 if numeric:
  if folder==GRAPH:assert all(k in r and canonical(r[k])==canonical(v)for k,v in read(folder/numeric).items())
  else:assert ref(folder/numeric)in r['evidenceRefs']
 return r

def recheck():
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==CURRENT;current=read(manifest);catrefs={u:ref(ROOT/'3d-viewer'/u)for u in current['officialModelCatalogues']};refs=[ref(Path(__file__)),start]
 for p,n in [(PHYSICAL,None),(PROBE,None),(FINITE,'diagnostic.json.gz'),(ACTUAL,'actual-render-geometry.json.gz'),(CARRIER,'diagnostic.json.gz'),(GRAPH,'diagnostic.json.gz'),(PATHS,'diagnostic.json.gz'),(UNIT,'diagnostic.json.gz'),(INVENTORY,'inventory.json.gz'),(PROPOSAL,'diagnostic.json.gz'),(BOUNDS,'diagnostic.json.gz')]:
  fenced(p,n);refs.append(ref(p/'result.json'));refs.extend([ref(p/n)]if n else[])
 # Every fresh actual current capture/physical/proposal input is unchanged.
 for p in [PHYSICAL,PROBE,PROPOSAL,BOUNDS]:
  for pin in read(p/'result.json')['evidenceRefs']:assert ref(ROOT/pin['path'])==pin;refs.append(pin)
 rows=read(PROBE/'selection.json.gz')['rows'];assert [r['uid']for r in rows]==[NATIVE,UID];assets=[ROOT/r['candidate']['path']for r in rows]
 for row,a in zip(rows,assets):assert digest(a.read_bytes())==row['sourceSHA256'];assert row['candidate']['entry']['sha256']==row['sourceSHA256']
 assert rows[1]['sourceSHA256']==SOURCE
 rtpath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';rt=read(rtpath)['rows'];assert [r['uid']for r in rt]==[NATIVE,UID]
 original=np.concatenate([decode_original_world_triangles(a.read_bytes())for a in assets]);literal=np.concatenate([np.asarray(r['position'],float).reshape(-1,3)[np.asarray(r['index'],int).reshape(-1,3)]for r in rt]);assert original.shape==literal.shape==(73812,3,3)
 actual=read(ACTUAL/'actual-render-geometry.json.gz')['row'];assert rt[1]['uid']==actual['uid']==rows[1]['uid']==UID and actual['sourceSHA256']==SOURCE
 nativebounds=read(BOUNDS/'current-native-bounds.json');nr=next(r for r in nativebounds['rows']if r['uid']==NATIVE);ix=np.asarray(actual['completeOriginalIndex'],int).reshape(-1,3)
 worlds=[original,literal]
 for nk,ok in [('leftAssociatedPerMultiplyAddFloat32WorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedPerMultiplyAddFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition')]:
  native=np.concatenate([np.asarray(m[nk],float).reshape(-1,3)[np.asarray(m['completeOriginalIndex'],int).reshape(-1,3)]for m in nr['actualRenderMeshes']]);own=np.asarray(actual[ok],float).reshape(-1,3)[ix];worlds.append(np.concatenate([native,own]))
 assert all(w.shape==(73812,3,3)and np.isfinite(w).all()for w in worlds)
 g=read(GRAPH/'diagnostic.json.gz');assert g['binding']['completeOriginalWorldTrianglesSHA256']==sha(original);assert len(g['components'])==366 and sorted(i for c in g['components']for i in c['globalOriginalFaces'])==list(range(73812))
 assert all(g['components'][i]['actorUID']==UID for i in range(285,366));assert g['components'][324]['globalOriginalFaces']==FACES
 carrier_module=module('parkview_current_carrier_replay','xl-terrain-recovery-20261011-parkview-current-bounded-carrier-grade-cap-v1.py');carrier=carrier_module.recheck();assert canonical(carrier)==canonical(read(CARRIER/'diagnostic.json.gz'))
 allfinite=read(FINITE/'diagnostic.json.gz');savedpaths=read(PATHS/'diagnostic.json.gz');unitdiag=read(UNIT/'diagnostic.json.gz');roles=[];resolved_components=set(range(285,366))-{324}
 for mode,world,finite_row in zip(['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'],worlds,allfinite['rows']):
  assert sha(world[63133:])==finite_row['completeWorldSHA256']and finite_row['completeOriginalFaces']==10679 and not finite_row['unprovedFaces'];contexts=[dict(sourceFace=i)for i in range(73812)]
  for i,p in enumerate(finite_row['allFaces']):
   proof=p['proof'];assert p['sourceFace']==i and proof['sourceFaceSHA256']==sha(world[63133+i])and proof['groundProjectionCovered']is True and proof['existingOrdinaryClearanceBoundProved']is True and F(proof['exactCertifiedLowerClearanceM'])>=F(-1,2);contexts[63133+i]={**proof,'sourceFace':63133+i}
  # No whole-native edge-body qualification: selected root/path faces only.
  cp=next(p for p in carrier['rows']if p['mode']==mode);assert cp['completeNativeWorldSHA256']==sha(world[:63133])and cp['completeOwnedWorldSHA256']==sha(world[63133:]);assert cp['strictClearCapWholeFiniteProof']['groundProjectionCovered']is True and F(cp['strictClearCapWholeFiniteProof']['exactCertifiedLowerClearanceM'])>0 and cp['wallToCapOriginalSharedEdge']['strictlyExposedWholePositiveInterface']is True
  assert cp['exactPositiveUpperGroundInterfaces']and F(cp['completeOriginalVertexExposure']['exactExposureLowerBoundM'])>0
  prior=next(p for p in savedpaths['rows']if p['completeCombinedWorldSHA256']==sha(world));body={};nonrender=[]
  for i in range(285,366):
   faces=g['components'][i]['globalOriginalFaces'];proof=census(world,faces);record=next(p for p in prior['completeOwnedComponentEdgeCensus']if p['historicalVertexComponent']==i);assert canonical(proof)==canonical(record['sharedEdgeProof']);assert len(proof['sharedEdgeConnectedComponents'])==1
   body[i]=set(proof['sharedEdgeConnectedComponents'][0]);zeros=proof['exactNonrenderingOriginalFaces'];assert all(all(exact_nonrendering(w[j])for w in worlds)for j in zeros);nonrender.extend(zeros)
  contacts=[];adj={i:set()for i in resolved_components}
  for p in prior['allRestrictedContactRecords']:
   a,b=p['components'];x,y=p['globalOriginalFaces']
   if a==170 or b==170:
    # Only the independently strict exposed cap→owned main interface is used.
    if p['globalOriginalFaces']!=[57951,63133]:continue
    assert p['components']==[170,285];assert cp['capToOwnedFace0OriginalContact']['exactIntersectionPoints']==p['exactContactPoints'];continue
   if a not in resolved_components or b not in resolved_components:continue
   assert x in body[a]and y in body[b];points=intersection_points(rational_face(world[x]),rational_face(world[y]));assert contact_measure(points)['dimension']>0 and [[str(v)for v in q]for q in points]==p['exactContactPoints'];contacts.append(p);adj[a].add(b);adj[b].add(a)
  parent={285:None};todo=collections.deque([285])
  while todo:
   i=todo.popleft()
   for j in sorted(adj[i]):
    if j not in parent:parent[j]=i;todo.append(j)
  assert set(parent)==resolved_components,'A structural owned part lacks a complete positive-dimensional safe owned path'
  provider_template=unitdiag['rows'][0];assert provider_template['completeCombinedWorldSHA256']==sha(world)
  template=dict(component=324,hostComponent=285,kind='parkview-original-mounted-roof-appendage-324',completeEveryOriginalBoundary=[e['originalBoundaryEdge']for e in provider_template['completeEveryOriginalBoundaryEdge']],completeOriginalTripleIncidences=provider_template['originalMoreThanTwoFaceIncidences'])
  support=dict(hostComponent=285,hostGroundedIndependentlyOfUnit324=True,creditedRootOrBridgeComponents=sorted(parent),exactCurrentNativeGradeCapRoute=ref(CARRIER/'diagnostic.json.gz'),completeCurrentStructuralParents=parent,qualification='Only exact current native wall60989 grade interface→strict exposed edge→cap57951→owned63133 and positive-dimensional wholly clear owned paths; no native body root credit')
  bind=dict(ownedSourceSHA256=SOURCE,completeWorldSHA256=sha(world),completeComponentFacesSHA256=canonical(FACES),completeFacetContextsSHA256=canonical(contexts),completeHostFacesSHA256=canonical(g['components'][285]['globalOriginalFaces']),independentHostSupportSHA256=canonical(support),sourceRoleTemplateSHA256=canonical(template));uv=unit(world,FACES,contexts,g['components'][285]['globalOriginalFaces'],support,template,expected_binding=bind,current_binding=bind);assert not uv['addedRootOrBridgeCredit']and not uv['closedSolidCertified']
  roles.append(dict(mode=mode,completeWorldSHA256=sha(world),completeOwnedFacetFinite=ref(FINITE/'diagnostic.json.gz'),creditedNativeFacePath=[60989,57951],creditedNativeToOwnedInterface=[57951,63133],allOtherNativeFacesUncredited=True,completeStructuralOwnedComponents=sorted(parent),completeStructuralOwnedParents=parent,positiveDimensionalSafeOwnedContacts=contacts,exactNonrenderingOriginalFacesRetained=nonrender,visualOnlyUnit324=uv,all81OwnedComponentsAccounted=True))
 receipt=read(PHYSICAL/'result.json');assert receipt['manifestSHA256']==CURRENT;row=read(PHYSICAL/'selection.json.gz')['rows'][0];ctx=read(PHYSICAL/'context.json.gz')['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SOURCE;identity=verify_files(row,ctx,HERE/'local'/PHYSICAL.name/'identity-current');assert identity['passed']
 physicalruntime=read(HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz')['rows'][0];assert physicalruntime['uid']==actual['uid']==row['uid']==UID
 for k in ['position','index','drawnGroundGeometry']:assert np.array_equal(np.asarray(physicalruntime[k]),np.asarray(rt[1][k]))
 ownGround=np.asarray(physicalruntime['drawnGroundGeometry'],float).reshape(-1,3,3)
 for p in allfinite['rows']:assert p['completeGroundSHA256']==sha(ownGround)
 foundation=read(PHYSICAL/'foundation.json')['rows'][0];assert foundation['uid']==UID and foundation['strictFoundationAccepted']is True;f=foundation['foundation'];assert f['completeTerrainTriangles']==f['triangles']==10679 and f['fullyBuriedUpwardTriangles']==0
 nativechecks=read(PHYSICAL/'native-neighbour-checks.json');assert set(nativechecks['blocked'])==set(nativechecks['resolved'])==set(RETAINED)and len(nativechecks['rows'])==4;assert all(p['passed']is True and p['terrain']['newlyWhollyBuried']==p['terrain']['newlyUpwardWhollyBuried']==0 for p in nativechecks['rows'])
 neighbours=read(PHYSICAL/'neighbour-checks.json');assert all(not p['reasons']for p in neighbours['rows']if not p['existingNative']);neighbourinputs=read(PHYSICAL/'neighbour-inputs.json.gz');assert len(neighbourinputs['rows'])==26
 metrics=read(PHYSICAL/'metrics.json')['rows'][0];assert metrics['uid']==UID and metrics['sourcePreserved']is True and metrics['maxSamplerDelta']<=.004 and metrics['missingTerrain']==0
 validation=read(PHYSICAL/'validation.json');assert validation['loaderAccepted']is True and validation['checksPassed']is True
 expected={'ground-contact-unresolved','sampled-ground-gap-below-model-bottom','sampled-terrain-above-model-bottom'}|{f'neighbour:{u}:{r}'for u in [NATIVE,'landsd/256112:0','landsd/256114:0']for r in ['existing-native-neighbour-requires-full-mesh-check','increased-neighbour-ground-gap']};assert set(receipt['reasons'])==expected
 candidate=read(PROPOSAL/'terrain-candidates.json');assert len(candidate)==1;c=candidate[0];assert c['replaces']['url']=='city/data/government-native-255439-0.json'and c['replaces']['retainedUids']==['landsd/255439:0'];patch=read(ROOT/c['path']);assert ref(ROOT/c['path'])['sha256']==c['sha256'] and patch['meta']['targetUids']==['landsd/255439:0',UID]
 inv=read(INVENTORY/'inventory.json.gz');assert inv['currentManifest']==start and len(inv['rows'])==inv['completeNativeActors']==6636;mapping={p['uid']:p for p in inv['rows']};entries={e['uid']:(ROOT/'3d-viewer'/url,e)for url in current['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']};assert set(mapping)==set(entries)and UID not in entries
 fullpositions=[packed_world_bounds(a.read_bytes())for a in assets];ownbounds=np.asarray(fullpositions[1]['originalWholeSourceBounds']);position=np.asarray(physicalruntime['position'],float).reshape(-1,3);explicit=[np.asarray(actual[k],float).reshape(-1,3)for k in ['completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']];boxes=[ownbounds,np.asarray([position.min(axis=0),position.max(axis=0)]),*[np.asarray([p.min(axis=0),p.max(axis=0)])for p in explicit]];lo=np.min([b[0]for b in boxes],axis=0);hi=np.max([b[1]for b in boxes],axis=0);region=c['bounds'];touch=[]
 for uid,(catalogue,e)in entries.items():
  item=mapping[uid];assert item['rawCurrentEntry']==e and item['catalogue']==ref(catalogue)and item['sourceSHA256']==e['sha256'];assert ref(ROOT/item['source']['path'])==item['source'];bb=np.asarray(item['completeOriginalPOSITIONProof']['originalWholeSourceBounds']);assert item['completeOriginalPOSITIONProof']['allOriginalPositionVerticesAccounted']is True
  if bb[1,0]>=region[0]and bb[0,0]<=region[2]and bb[1,2]>=region[1]and bb[0,2]<=region[3]:touch.append(uid)
 assert set(touch)==set(RETAINED),'Unaccounted whole original native actor intersects actual proposed terrain'
 for captured in nativebounds['rows']:
  cp,e=entries[captured['uid']];assert captured['rawCurrentEntry']==e and captured['sourceSHA256']==e['sha256']and captured['currentCatalogue']==ref(cp)
  for key in ['completeLiteralWorldBounds','completeFloat32CastWorldBounds','completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds','completeExplicitBalancedFloat32ModelMatrixWorldBounds']:
   bb=captured[key];assert region[0]<=bb[0][0]<=bb[1][0]<=region[2]and region[1]<=bb[0][2]<=bb[1][2]<=region[3]
 refs.extend(catrefs.values());refs.extend(ref(p)for p in [*assets,rtpath,PHYSICAL/'selection.json.gz',PHYSICAL/'context.json.gz',ACTUAL/'actual-render-geometry.json.gz',BOUNDS/'current-native-bounds.json',PROPOSAL/'terrain-candidates.json',PROPOSAL/'terrain.json',ROOT/c['path']]);refs.extend(ref(HERE/n)for n in ['xl-terrain-recovery-20261011-parkview-current-bounded-carrier-grade-cap-v1.py','parkview_original_roof_unit324_visual_accounting_v1_20261011.py','test_parkview_original_roof_unit324_visual_accounting_v1_20261011.py','exact_packed_world_bounds_v3_20261010.py','exact_packed_world_geometry_20261009.py','xl_source_stream_binding_20261009.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py'])
 for pin in refs:assert ref(ROOT/pin['path'])==pin
 assert ref(manifest)==start
 mandatory=dict(uid=NATIVE,csuid=entries[NATIVE][1]['buildingCSUID'],sourceSHA256=entries[NATIVE][1]['sha256'],completeOriginalFaces=63133,qualification='current-native-availability-with-bounded-exposed-grade-wall-clear-cap-support-only',installedVerified=False,wholeNativeReaccepted=False)
 return dict(contract='parkview-block11-complete-current-four-stream-finite-bounded-native-grade-cap-and-named-roof-unit-v1',uids=[UID],currentManifest=start,currentOwnedIdentities=[identity],currentTypedPhysicalAccepted=True,reasons=[],scriptChecksPassed=True,readyForStagedBrowser=True,browserAcceptanceRequired=True,installationApproved=False,fullAcceptance=False,newlyInstalled=0,completeOriginalFaces=10679,completeOriginalComponents=81,independentlySupportedStructuralOwnedComponents=80,visualOnlyOwnedComponents=[324],completeFourStreamRoleAccounting=roles,mandatoryInstalledNativeSupport=mandatory,completeCurrentInstalledNativeEntriesPreserved={u:entries[u][1]for u in RETAINED},retainedNativeUIDs=RETAINED,completeCurrentNeighbourForms=26,completeWholeCurrentNativeInventory=ref(INVENTORY/'inventory.json.gz'),completeProposedTerrainNativeCensus=touch,completeOwnedWholePOSITIONLiteralExplicitF32ProtectedBounds=dict(originalPOSITION=fullpositions[1],literal=[position.min(axis=0).tolist(),position.max(axis=0).tolist()],explicitLeftAndBalanced=[[p.min(axis=0).tolist(),p.max(axis=0).tolist()]for p in explicit],union=[lo.tolist(),hi.tolist()]),providerSourceRootAndStreams=[source_stream_binding(a.read_bytes())for a in assets],terrainProposal=candidate,terrainProposalGeometryChanged=True,rawPhysicalReasonsPreserved=receipt['reasons'],rawNativeFaceFailuresPreserved=carrier['rawWholeNativeFailuresRef'],allOtherNativeFacesAndComponentsUncredited=True,nativeReacceptance=False,sourceGeometryChanges=0,namedRoofUnitRootOrBridgeCredit=False,explicitArithmeticNotUniversalGPUCameraGuarantee=True,evidenceRefs=list({p['path']:p for p in refs}.values()))
def main():
 assert not DOC.exists();result=json.loads(json.dumps(recheck()));save(DOC/'typed-role.json.gz',result);m=module('parkview_current_role_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');m.freeze(BATCH,'complete-current-original-literal-two-explicit-render-F32-parkview-owned-bounded-native-cap-and-unit324-role-v1',[ROOT/p['path']for p in result['evidenceRefs']]+[DOC/'typed-role.json.gz'],dict(uids=[UID],scriptChecksPassed=True,wholeOwnedOriginalFaces=10679,completeOwnedComponents=81,structuralOwnedComponents=80,visualOnlyComponents=[324],nativeReacceptance=False,installationApproved=False,newlyInstalled=0))
if __name__=='__main__':main()
