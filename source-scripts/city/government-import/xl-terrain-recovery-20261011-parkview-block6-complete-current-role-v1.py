"""Typed unchanged Block6 current roles; nonpublishing complete pinned recheck."""
import importlib.util,json,collections
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import finite_intersection_points
from exact_original_shell_intersections_20261009 import rational_face
from exact_original_component_contacts_20261009 import contact_measure
from complete_original_lower_opening_mounts_v3_20261011 import verify as opening_verify,binding
B=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-parkview-block6-current-role-v1';DOC=B/BATCH
UID='landsd/255438:0';NATIVE='landsd/254491:0';SOURCE='363c8df82ecf39c7a9d1f6948e2b2aec06af28820642fdeeab45f9d08da36bae';CURRENT='cb79525c2c95d96eb0c9868158bfe04c21a60135ec5a8e755ccea106c972b402';RETAINED=['landsd/254491:0','landsd/255439:0','landsd/255647:0','landsd/256112:0','landsd/256114:0']
P=B/'government-xl-parkview-block6-fresh-current-physical-capture-v1-20261011';C=B/'government-xl-parkview-block6-fresh-current-carrier-capture-v1-20261011';FINITE=B/'government-xl-parkview-block6-current-four-stream-source-proofs-v1-20261011';OPEN=B/'government-xl-parkview-block6-current-four-opening-guards-v3-20261011';REBIND=B/'government-xl-parkview-block6-fresh-current-bounded-route-binding-v1-20261011';REC=B/'government-xl-parkview-block6-current-role-reconciliation-v1-20261011';GRAPH=B/'government-xl-parkview-block6-complete-original-support-paths-v1-20261011';ROUTE=B/'government-xl-parkview-block6-bounded-eligible-native-route-v2-20261011';CAP=B/'government-xl-parkview-block6-bounded-original-clear-cap-probe-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def normal(v):return json.loads(json.dumps(v))
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def fenced(doc,verify_current=False):
 receipt=read(doc/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 if verify_current:
  for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 return receipt
def capture(doc):
 row=read(doc/'selection.json.gz')['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==row['candidate']['entry']['sha256'];a=read(doc/'actual-render-geometry.json.gz');assert a['startEndAllInputsVerified']and a['completeRecursiveProductionModuleClosure'];a=a['row'];assert a['uid']==row['uid']and a['sourceSHA256']==row['sourceSHA256'];rt=read(HERE/'local'/doc.name/'runtime-geometry.json.gz')['rows'][0];assert rt['uid']==row['uid']and rt['index']==a['completeOriginalIndex'];assert np.array_equal(np.asarray(rt['position']),np.asarray(a['completeLiteralWorldPosition']));idx=np.asarray(a['completeOriginalIndex']).reshape(-1,3);worlds=[decode_original_world_triangles(asset.read_bytes())]+[np.asarray(a[k]).reshape(-1,3)[idx]for k in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']];ground=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3);return row,a,worlds,ground

def recheck():
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==CURRENT;current=read(manifest);refs=[ref(Path(__file__)),start]
 for d in [P,C,FINITE,OPEN,REBIND,REC]:fenced(d,True);refs.append(ref(d/'result.json'))
 for d in [GRAPH,ROUTE,CAP]:fenced(d);refs.append(ref(d/'result.json'))
 row,a,worlds,ground=capture(P);cr,ca,natives,nground=capture(C);assert row['uid']==UID and cr['uid']==NATIVE and row['sourceSHA256']==SOURCE;assert ground.shape==(210,3,3)and nground.shape==(25167,3,3);assert all(w.shape==(11041,3,3)and np.isfinite(w).all()for w in worlds);assert all(w.shape==(63133,3,3)and np.isfinite(w).all()for w in natives)
 g=read(GRAPH/'diagnostic.json.gz');parts=g['completeSourceEdgeBodyFaces'];parents={int(k):v for k,v in g['completeConditionalParents'].items()};visual=g['unreachedBodies'];assert len(parts)==85 and len(parents)==81 and visual==[78,79,80,83]and parents[0]is None;hostfaces=sorted(f for i in parents for f in parts[i]);assert len(hostfaces)==10953;assert sorted(f for fs in parts for f in fs)==list(range(11041));assert not set(visual)&set(parents)
 finite=read(FINITE/'diagnostic.json.gz');op=read(OPEN/'diagnostic.json.gz');rb=read(REBIND/'diagnostic.json.gz');route=read(ROUTE/'diagnostic.json.gz');cap=read(CAP/'diagnostic.json.gz');paired=read(CAP/'paired-cap-refinement.json.gz');assert paired['strictWholeCapClear']and F(paired['pairedProof']['exactCertifiedLowerClearanceM'])>0 and paired['pairedProof']['groundProjectionCovered'];assert paired['pairedProof']['sourceFaceSHA256']==digest(natives[0][58400].tobytes());assert route['boundedOriginalPathProved']and route['qualifiedGenuineGradeFace']==60333;path=route['qualifiedOriginalPathToStrictCap'];assert path==[60333,38937,38936,54398,54397,54396,54656,54655,58400];assert 54320 not in path and [52248,52249]not in [path[i:i+2]for i in range(len(path)-1)]
 assert digest(nground.tobytes())==route['completePinnedGroundSHA256']==cap['completeCurrentGroundSHA256']==paired['pairedProof']['completeCurrentGroundSHA256'];grade=next(p for p in route['allExaminedFaceProofs']if p['face']==60333);assert grade['eligible']and grade['genuineGrade']and grade['exactPositiveUpperGroundInterfaces']and F(grade['completeGradeVertexExposure']['exactExposureLowerBoundM'])>0
 for f in path[1:-1]:
  p=next(p for p in route['allExaminedFaceProofs']if p['face']==f);assert p['eligible']and p['strictClear']and F(p['exactLowerM'])>0
 for f,h in zip(path,path[1:]):
  p=next(p for p in route['allExaminedWholeSharedEdgeProofs']if set(p['faces'])=={f,h});assert p['eligible']and p['completeGroundSHA256']==digest(nground.tobytes());q=p['originalSubsetProof'];assert q['strictlyExposedWholePositiveInterface']and q['closedWholeSegmentProjectionCovered']and F(q['exactMinimumGapM'])>0
 modes=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'];roles=[]
 for mode,t,nt in zip(modes,worlds,natives):
  th=digest(t.tobytes());nh=digest(nt.tobytes());assert th==cap['completeOriginalOwnedWorldSHA256']and nh==route['completeOriginalNativeWorldSHA256'];fr=next(p for p in finite['rows']if p['mode']==mode);orr=next(p for p in op['rows']if p['mode']==mode);rbr=next(p for p in rb['rows']if p['mode']==mode);assert fr['completeWorldSHA256']==orr['completeWorldSHA256']==rbr['completeOwnedWorldSHA256']==th and rbr['completeCarrierWorldSHA256']==nh;assert fr['completeGroundSHA256']==digest(ground.tobytes());assert not fr['unprovedWholeFacetIDs']and len(fr['all11041WholeFacetFiniteProofs'])==11041
  for i,p in enumerate(fr['all11041WholeFacetFiniteProofs']):
   q=p['proof'];assert p['sourceFace']==i and q['sourceFaceSHA256']==digest(t[i].tobytes())and q['completeCurrentGroundSHA256']==digest(ground.tobytes())and q['groundProjectionCovered']and q['existingOrdinaryClearanceBoundProved']and F(q['exactCertifiedLowerClearanceM'])>=F(-1,2)
  same=next((p for p in roles if p['completeOwnedWorldSHA256']==th and p['completeNativeWorldSHA256']==nh),None)
  if same:roles.append({**same,'mode':mode,'identicalCompleteSourceAndNativeAndGroundProofsReusedFrom':same['mode']});continue
  bodies=[]
  for i,fs in enumerate(parts):
   proof=census(t,fs);assert len(proof['sharedEdgeConnectedComponents'])==1 and not proof['exactNonrenderingOriginalFaces'];assert normal(proof)==next(p['proof']for p in fr['complete85OriginalBodyEdgeCensuses']if p['originalBody']==i);bodies.append(dict(originalBody=i,proof=proof))
  contacts=[];adj={i:set()for i in parents}
  for witness in fr['original81BodyPositiveContactPaths']:
   f,h=witness['originalFaces'];x,y=witness['bodies'];assert x in parents and y in parents;assert f in parts[x]and h in parts[y]or f in parts[y]and h in parts[x];points=finite_intersection_points(rational_face(t[f]),rational_face(t[h]));measure=contact_measure(points);assert measure['dimension']>0 and normal(measure)=={k:witness[k]for k in measure};adj[x].add(y);adj[y].add(x);contacts.append(witness)
  assert len(contacts)==80;proved={0:None};todo=collections.deque([0])
  while todo:
   i=todo.popleft()
   for j in sorted(adj[i]):
    if j not in proved:proved[j]=i;todo.append(j)
  assert set(proved)==set(parents)
  capcontacts=cap['completeOwnedToOneCapContacts']['contacts'];positive=[p for p in capcontacts if p['dimension']>0];assert len(positive)==19 and cap['reachedOwnedEdgeBodyIDs']==[0]
  for w in positive:
   f,h=w['sourceFaceA'],w['sourceFaceB'];assert f==58400 and h in parts[0];m=contact_measure(finite_intersection_points(rational_face(nt[f]),rational_face(t[h])));assert m['dimension']>0 and m['exactPoints']==w['exactPoints']
  openings=[]
  for i in visual:
   proof=normal(opening_verify(t,parts[i],hostfaces,expected_binding=binding(t,parts[i],hostfaces)));saved=next(p['proof']for p in orr['completeFourOpeningProofs']if p['originalBody']==i);assert proof==saved and proof['completeLowerOpeningAssociated']and not proof['structuralRootCredit']and not proof['structuralBridgeCredit']and not proof['closedSolidCertified'];openings.append(dict(originalBody=i,proof=proof))
  roles.append(dict(mode=mode,completeOwnedWorldSHA256=th,completeNativeWorldSHA256=nh,completeOwnedCurrentGroundSHA256=digest(ground.tobytes()),completeCarrierCurrentGroundSHA256=digest(nground.tobytes()),completeOriginal85BodyEdgeCensuses=bodies,completeStructuralOwnedParents=proved,all80PositiveOriginalContactWitnesses=contacts,all19PositiveOriginalCapContacts=positive,qualifiedNativeFacePath=path,allOtherNativeFacesUncredited=True,visualOnlyOriginalRoofBodies=openings,complete11041FacePartitionAccounted=True))
 identity=read(P/'identity-proofs.json')['rows'][0];assert identity['passed']and identity['worldTrianglesSHA256']==digest(worlds[0].tobytes());assert identity['proof']['exactObjectId']and identity['proof']['exactBuildingCSUID']and identity['proof']['uniqueViewerMatch']and identity['exactWholeCellCoverage']['covered'];assert identity['freshCurrentIdentity']['unrelatedIntersectingForms']==0;assert read(P/'source-preflight.json')['completeCurrentForeignFormScope']==23;neighbourinputs=read(P/'neighbour-inputs.json.gz');neighbours=read(P/'neighbour-checks.json');assert len(neighbourinputs['rows'])==len(neighbours['rows'])==23 and not any(p['reasons']for p in neighbours['rows']);assert read(P/'terrain-candidates.json')==neighbourinputs['patches']==[]
 foundation=read(P/'foundation.json')['rows'][0];assert foundation['strictFoundationAccepted']and foundation['foundation']['triangles']==foundation['foundation']['completeTerrainTriangles']==11041 and not foundation['foundation']['fullyBuriedUpwardTriangles']
 nativechecks=read(P/'native-neighbour-checks.json');assert set(nativechecks['blocked'])==set(nativechecks['resolved'])==set(RETAINED)and len(nativechecks['rows'])==5;assert all(p['passed']and p['terrain']['newlyWhollyBuried']==p['terrain']['newlyUpwardWhollyBuried']==0 for p in nativechecks['rows'])
 metric=read(P/'metrics.json')['rows'][0];assert metric['uid']==UID and metric['sourcePreserved']and metric['sourceSHA256']==SOURCE and metric['maxSamplerDelta']<=.004 and not metric['missingTerrain'];validation=read(P/'validation.json');assert all(type(validation[k])is int for k in ['models','loaderAccepted','checksPassed','exceptions']);assert validation['models']==validation['loaderAccepted']==validation['checksPassed']==1 and validation['exceptions']==0 and len(validation['results'])==1 and validation['results'][0]['uid']==UID and validation['results'][0]['triangles']==11041 and validation['results'][0]['outcome']=='runtime-accepted-placement-unreviewed'
 raw=read(P/'current-raw-outcome.json');assert raw['reasons']==['ground-contact-unresolved','sampled-ground-gap-below-model-bottom'];policy=module('block6_current_role_policy',HERE/'acceptance-policy.py');found=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCE,identityProof=identity['proof']),metric,read(P/'metrics.json')['profiles']['mobile']);assert found==['ground-contact-unresolved'];assert read(P/'diagnostic-resolutions.json')['rows'][0]['remaining']==['sampled-ground-gap-below-model-bottom']
 entries={};catrefs=[];retainedassets={}
 for url in current['officialModelCatalogues']:
  cp=ROOT/'3d-viewer'/url;catrefs.append(ref(cp))
  for e in read(cp)['models']:
   assert e['uid']not in entries;entries[e['uid']]=e
   if e['uid']in RETAINED:
    asset=cp.parent/e['asset'];assert digest(asset.read_bytes())==e['sha256'];retainedassets[e['uid']]=ref(asset)
 assert UID not in entries and set(retainedassets)==set(RETAINED);nativeentry=entries[NATIVE];assert nativeentry['sha256']==cr['sourceSHA256'];refs+=catrefs+list(retainedassets.values());nativeentries={u:entries[u]for u in RETAINED};positions=[np.asarray(a[k],float).reshape(-1,3)for k in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']];protected=[[float(min(p[:,i].min()for p in positions))for i in range(3)],[float(max(p[:,i].max()for p in positions))for i in range(3)]]
 assert ref(manifest)==start
 return dict(uids=[UID],currentManifest=start,sourceSHA256=SOURCE,completeOriginalFaces=11041,completeOriginalComponents=85,completeCurrentNeighbourForms=23,independentlySupportedStructuralOwnedComponents=81,visualOnlyOwnedComponents=visual,roles=roles,currentOwnedIdentities=[identity],completeCurrentInstalledNativeEntriesPreserved=nativeentries,completeCurrentInstalledNativeAssetRefsPreserved=retainedassets,completeOwnedWholePOSITIONLiteralExplicitF32ProtectedBounds=dict(union=protected),mandatoryInstalledNativeSupport=dict(uid=NATIVE,sourceSHA256=nativeentry['sha256'],installedVerified=False,currentNativeAvailabilityVerified=True,wholeNativeReaccepted=False,qualifiedNativeFacePath=path),rawReasonsPreserved=raw['reasons'],narrowlyReconciledReasons=dict(groundContact='81 genuine original contact bodies reach independently qualified current native grade-wall/whole-exposed-edge/strict-clear-cap and positive dimensional original contact; four complete original lower openings associate visually only',sampledGroundGap='direct terrain gap is preserved; complete original grounded source contact path supplies the candidate support route'),currentTypedPhysicalAccepted=True,scriptChecksPassed=True,reasons=[],terrainProposal=[],terrainProposalGeometryChanged=False,nativeReacceptance=False,namedRoofUnitRootOrBridgeCredit=False,publication=False,newlyInstalled=0,installationApproved=False,aiGeometryModelling=False,scriptExternalAICalls=0,explicitArithmeticNotUniversalGPUCameraGuarantee=True,stagedBrowserAndPublisherMandatory=True,evidenceRefs=refs)
def main():
 assert not DOC.exists();role=recheck();save(DOC/'typed-role.json.gz',role);save(DOC/'REVIEW.json',dict(currentTypedPhysicalAccepted=True,nonpublishing=True,rawReasonsPreserved=role['rawReasonsPreserved'],stagedBrowserAndPublisherMandatory=True));paths=[ROOT/p['path']for p in role['evidenceRefs']]+[DOC/'typed-role.json.gz',DOC/'REVIEW.json',HERE/'complete_original_lower_opening_mounts_v3_20261011.py',HERE/'test_complete_original_lower_opening_mounts_v3_20261011.py'];f=module('block6_typed_role_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f.freeze(BATCH,'complete-current-typed-original-source-role-v1',paths,dict(uids=role['uids'],currentTypedPhysicalAccepted=True,scriptChecksPassed=True,reasons=[],rawReasonsPreserved=role['rawReasonsPreserved'],currentAcceptance=False,scriptFullAcceptancePassed=False,stagedBrowserAndPublisherMandatory=True))
if __name__=='__main__':main()
