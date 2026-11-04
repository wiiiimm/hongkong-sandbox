"""Replay ten unchanged Man Fuk originals against complete current evidence.

Ordinary original roots/contact graph and five independently rendered anchors
remain separate from full finite clearance, original/actual exposed wall paths,
all current/other-proposed foreign bodies, full foundations and runtime budgets.
No original face/actor or failed diagnostic is omitted; browser still required.
"""
import importlib.util,json,subprocess
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from original_ordinary_ground_root_graph_20261009 import verify as structural
from original_bound_facet_wall_context_20261010 import canonical
from exact_original_georef_cell_identity_20261009 import verify_files as ordinary_identity
from man_hei_current_bound_mandatory_platform_identity_v2_20261010 import verify_files as pair_identity
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-man-fuk-ten-current-complete-typed-role-v1-20261010';DOC=BASE/BATCH
PHYS=BASE/'government-xl-man-fuk-ten-original-coupled-physical-v3-20261010'
FINITE=BASE/'government-xl-man-fuk-ten-v10-complete-finite-column-refinement-v1-20261010'
CONTEXT=BASE/'government-xl-man-fuk-ten-v10-complete-finite-wall-contexts-v1-20261010'
WALL=BASE/'government-xl-man-fuk-ten-v10-exact-contact-clear-cap-wall-paths-v2-20261010'
GRAPH=BASE/'government-xl-man-fuk-ten-v10-complete-original-support-20261010'
LITERAL=BASE/'government-xl-man-fuk-ten-v10-literal-all-five-ground-roots-v1-20261010'
FOREIGN=BASE/'government-xl-man-fuk-ten-current-complete-foreign-wall-scope-v1-20261010'
PAIR=BASE/'government-xl-man-hei-current-bound-mandatory-platform-promotion-v3-20261010'
PODIUM='landsd/266062:0';ORDINARY=[75412,75413,75414,75693,76093,76126,76279,76282]
UIDS={PODIUM,'landsd/75694:0'}|{'landsd/'+str(i)+':0' for i in ORDINARY}
RETAINED={'landsd/75697:0'}
MANIFEST='44c9e80ec3999285616bb12a3fdfbe142a15855db7aa7c3216bffab3500f991a'
TERRAIN='422644c1c173dac0bad0a616a9ee9ef10a385a3787eacfa648c500c6986a93cc'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def checked(folder):
 r=read(folder/'result.json')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 assert len({x['path'] for x in r['evidenceRefs']})==len(r['evidenceRefs'])
 for x in r['evidenceRefs']:assert ref(ROOT/x['path'])==x,x['path']
 return r
def recheck():
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST
 folders=[PHYS,FINITE,CONTEXT,WALL,GRAPH,LITERAL,FOREIGN,PAIR]
 receipts=[checked(p) for p in folders];physics=receipts[0]
 selected=read(PHYS/'selection.json.gz');rows=selected['rows'];assert selected['manifestSHA256']==MANIFEST and {r['uid'] for r in rows}==UIDS
 sources={r['uid']:r['sourceSHA256'] for r in rows};counts={r['uid']:r['triangles'] for r in rows};assert sum(counts.values())==29125
 runtimepath=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';runtime=read(runtimepath)
 assert {r['uid'] for r in runtime['rows']}==UIDS
 for p,h in runtime['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 terrain=read(PHYS/'terrain-candidates.json');assert len(terrain)==1 and terrain[0]['sha256']==TERRAIN and ref(ROOT/terrain[0]['path'])['sha256']==TERRAIN
 patch=read(ROOT/terrain[0]['path']);assert patch.get('nativeMesh') and len(patch['nativeMesh']['index'])//3==10495
 replacement=terrain[0]['replaces'];assert set(replacement['retainedUids'])==RETAINED and ref(ROOT/'3d-viewer'/replacement['url'])['sha256']==replacement['sha256']
 forms=module('man_fuk_live_forms','xl-final-script-pass.py').load_forms(terrain[0]['bounds']);neighbours=read(PHYS/'neighbour-inputs.json.gz')
 assert len(forms)==70 and [r['building'] for r in neighbours['rows']]==[b for b,_,_ in forms] and set(neighbours['candidateIds'])==UIDS
 assert neighbours['inputHashes']=={str((ROOT/'3d-viewer'/url).relative_to(ROOT)):digest((ROOT/'3d-viewer'/url).read_bytes()) for _,_,url in forms}
 basicchecks=read(PHYS/'neighbour-checks.json');assert len(basicchecks['rows'])==70 and {r['uid'] for r in basicchecks['rows']}=={b['uid'] for b,_,_ in forms}
 for r in basicchecks['rows']:assert r['reasons']==(['existing-native-neighbour-requires-full-mesh-check'] if r['uid'] in RETAINED else [])
 native=read(PHYS/'native-neighbour-checks.json');assert set(native['blocked'])==set(native['resolved'])==RETAINED and {r['uid'] for r in native['rows']}==RETAINED and all(r['passed'] is True for r in native['rows'])
 for p,h in native['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 validation=read(PHYS/'validation.json');assert validation['checksPassed']==validation['loaderAccepted']==10 and validation['exceptions']==0
 foundations=read(PHYS/'foundation.json')['rows'];assert {r['uid'] for r in foundations}==UIDS
 for f in foundations:
  x=f['foundation'];assert f['sourceSHA256']==sources[f['uid']] and f['strictFoundationAccepted'] and x['completeTerrainTriangles']==x['triangles']==counts[f['uid']] and x['fullyBuriedUpwardTriangles']==0 and x['fullyBuriedAreaFraction']==0
 identities=[];deps=[Path(__file__),manifest,runtimepath,ROOT/terrain[0]['path']]
 for n in ORDINARY:
  folder=BASE/f'government-xl-man-fuk-eight-current-identity-{n}-v2-20261010';checked(folder);folders.append(folder)
  row=read(folder/'selection.json.gz')['rows'][0];ctx=read(folder/'context.json.gz')['rows'][0]
  assert row['sourceSHA256']==sources[row['uid']]
  identity=ordinary_identity(row,ctx,HERE/'local'/BATCH/'identity-recheck'/str(n));assert identity==read(folder/'identity.json') and identity['passed'] and identity['reasons']==[];identities.append(identity);print(dict(freshIdentity=identity['uid'],passed=True),flush=True)
 pairrows=read(PAIR/'selection.json.gz')['rows'];paircontexts=read(PAIR/'context.json.gz')['rows'];pairsaved=read(PAIR/'identities.json.gz')['rows']
 for row in pairrows:
  assert row['sourceSHA256']==sources[row['uid']]
  identity=pair_identity(row,next(c for c in paircontexts if c['uid']==row['uid']),HERE/'local'/BATCH/'identity-recheck'/row['uid'].split('/')[1])
  assert identity==next(x for x in pairsaved if x['uid']==row['uid']) and identity['passed'] and identity['reasons']==[] and set(identity['mandatoryOriginalRuntimeUIDs'])=={PODIUM,'landsd/75694:0'} and identity['standaloneOriginalImportAccepted'] is False;identities.append(identity)
 assert {r['uid'] for r in identities}==UIDS
 graph=read(GRAPH/'diagnostic.json.gz');finite=read(FINITE/'diagnostic.json.gz');contexts=read(CONTEXT/'diagnostic.json.gz');wall=read(WALL/'diagnostic.json.gz')
 adapter=module('man_fuk_context_adapter','xl-complete-multi-source-finite-wall-contexts-v1-20261010.py');paths=module('man_fuk_exact_contacts','xl-man-fuk-ten-v10-exact-contact-clear-cap-wall-paths-v2-20261010.py')
 original={};actual={};grounds={};indexed=[];actors=[];cursor=0;wallproofs=[];wallids={}
 for row in rows:
  uid=row['uid'];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==sources[uid];deps.append(asset)
  with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
  tri=original[uid]=decode_original_world_triangles(raw);rt=next(r for r in runtime['rows'] if r['uid']==uid);pos=np.asarray(rt['position'],float).reshape(-1,3);idx=np.asarray(rt['index'],np.uint32).reshape(-1,3);world=actual[uid]=pos[idx];ground=grounds[uid]=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3)
  assert tri.shape==world.shape==(counts[uid],3,3) and np.max(np.abs(tri-world))<=1e-9
  cached=next(r for r in finite['rows'] if r['uid']==uid);assert cached['completeOriginalWorldSHA256']==digest(tri.tobytes()) and cached['completeActualRenderedWorldSHA256']==digest(world.tobytes()) and cached['completeGroundSHA256']==digest(ground.tobytes())
  actor=dict(uid=uid,sourceSHA256=sources[uid],originalStreamBindingSHA256=canonical(source_stream_binding(raw)),globalFaceRange=[cursor,cursor+len(tri)],completeOriginalFaceCount=len(tri),originalWorldTrianglesSHA256=digest(tri.tobytes()));actors.append(actor)
  sourcepos=np.empty_like(pos);assigned={}
  for ids,face in zip(idx,tri):
   for i,v in zip(ids,face):
    i=int(i)
    if i in assigned:assert np.array_equal(assigned[i],v)
    else:assigned[i]=v;sourcepos[i]=v
  assert set(assigned)==set(range(len(pos))) and np.array_equal(sourcepos[idx],tri)
  indexed.append(dict(uid=uid,sourceSHA256=sources[uid],position=sourcepos.reshape(-1).tolist(),index=idx.reshape(-1).tolist()))
  contacts=[[i-cursor for i in c['globalOriginalFaces']] for c in graph['contactWitnesses'] if all(cursor<=i<cursor+len(tri) for i in c['globalOriginalFaces'])]
  priorctx=next(r for r in contexts['rows'] if r['uid']==uid);priorwall=next(r for r in wall['rows'] if r['uid']==uid)
  for mode,t,isactual in [('completeOriginal',tri,False),('actualRendered',world,True)]:
   fresh=json.loads(json.dumps(adapter.analyse(t,ground,cached,raw,isactual)));assert fresh==priorctx[mode] and not fresh['buriedUpwardFaces']
   proof,binding,inventory=json.loads(json.dumps(paths.contact_paths(t,fresh['completeCertifiedLowerBoundContexts'],contacts)))
   stored=next(x for x in priorwall['sourceAndLiteralActualProofs'] if x['representation']==mode)
   assert proof==stored['strictClearCapWallPaths'] and binding==stored['binding'] and inventory==stored['independentExactContactInventory'] and proof['allAffectedHavePaths'] and not proof['rawExposureFailures']
   wallids.setdefault(uid,proof['affectedOriginalWallFaces']);assert wallids[uid]==proof['affectedOriginalWallFaces'];wallproofs.append(dict(uid=uid,representation=mode,proof=proof,binding=binding));print(dict(completeFacetAndWallReplay=uid,representation=mode,faces=len(t),passed=True),flush=True)
  cursor+=len(tri)
 assert actors==graph['actors'];whole=np.concatenate(list(original.values()));ground=np.unique(np.concatenate(list(grounds.values())).reshape(-1,9),axis=0).reshape(-1,3,3)
 binding=dict(completeOriginalWorldTrianglesSHA256=digest(whole.tobytes()),currentDrawnGroundSHA256=digest(ground.tobytes()),groundInterfacesInputSHA256=ref(runtimepath)['sha256'],supportScope='complete-current-drawn-ground-only',originalIndexedSourcesSHA256=canonical(indexed));assert binding==graph['binding']
 verified=json.loads(json.dumps(structural(whole,actors,graph['components'],graph['contactWitnesses'],indexed,ground,expected_binding=binding,current_binding=binding)))
 for k,v in verified.items():assert graph[k]==v,k
 assert verified['supportInterfaceAccepted'] and verified['reasons']==[] and verified['resolvedOriginalComponents']==list(range(131)) and verified['ordinaryGroundRootComponents']==[2,3,4,5,105]
 anchors=read(LITERAL/'diagnostic.json.gz');assert anchors['manifestSHA256']==MANIFEST and anchors['strictAllFiveLiteralRenderedCurrentGroundAnchors'] and anchors['arithmeticParityCredit'] is False and {r['component'] for r in anchors['rows']}=={2,3,4,5,105}
 for a in anchors['rows']:
  p=ROOT/a['input']['path'];assert ref(p)==a['input'];inp=read(p);uid=a['uid'];assert inp['manifestSHA256']==MANIFEST and inp['sourceSHA256']==sources[uid]
  assert np.array_equal(np.asarray(inp['part']['position']).reshape(-1,3,3),actual[uid][a['originalFaceIds']]) and np.array_equal(np.asarray(inp['terrain']['position']).reshape(-1,3,3),grounds[uid])
  result=json.loads(subprocess.check_output(['node',str(HERE/'xl-tung-sing-three-original-footing-readonly-replay-20261010.mjs'),str(p)],cwd=ROOT,text=True));assert result==a['result'] and result['passed'] is True
 foreign=read(FOREIGN/'diagnostic.json.gz');assert foreign['manifestSHA256']==MANIFEST and foreign['allThirdPartyForeignSourceAndRenderedCrossingWallsClear'] and foreign['everyOtherProposedOriginalCheckedAsForeignForCreditedWalls'] and not foreign['foreignNativeBoundsTouchingWalls'] and not foreign['allExactSourceAuthoredMutualWallIntersectionsRetained']
 pieces=[]
 for uid in original:
  for t in [original[uid],actual[uid]]:
   for face in t[wallids[uid]]:
    xz=face[:,[0,2]];p=Polygon(xz);pieces.append(p if p.area else LineString(xz) if len(set(map(tuple,xz)))>1 else Point(xz[0]))
 projection=unary_union(pieces);assert projection.wkt==foreign['completeOriginalAndRenderedWallProjectionWKT']
 bybasic={r['uid']:r for r in foreign['completeActualForeignBasicForms']};bynative={r['uid']:r for r in foreign['retainedCurrentNativeFormsIndependentlyWholeBoundChecked']};assert len(bybasic)==59 and set(bynative)==RETAINED
 for r in neighbours['rows']:
  b=r['building'];uid=b['uid']
  if uid in UIDS:continue
  record=(bynative if r['existingNative'] else bybasic)[uid];assert record['completeActualCurrentForm']==b and record['currentFormSHA256']==canonical(b)
  if not r['existingNative']:assert not b.get('modelGeometry') and Polygon(b['rings'][0],b['rings'][1:]).disjoint(projection)
 walls=np.concatenate([t[wallids[u]] for u in original for t in [original[u],actual[u]]]);nativebounds=[]
 for url in read(manifest)['officialModelCatalogues']:
  cat=ROOT/'3d-viewer'/url;deps.append(cat)
  for e in read(cat)['models']:
   b=np.asarray(e['worldBounds'],float);assert b.shape==(2,3) and np.isfinite(b).all() and np.all(b[1]>=b[0]) and e['uid'] not in UIDS
   assert all(np.any(b[0]>f.max(0)) or np.any(b[1]<f.min(0)) for f in walls)
   nativebounds.append(dict(uid=e['uid'],catalogue=url,sourceSHA256=e['sha256'],completeWholeSourceBounds=b.tolist(),strictlyDisjointFromEveryOriginalAndRenderedCrossingWall=True))
 assert nativebounds==foreign['completeCurrentNativeWholeSourceBounds'];trials=[]
 for wm,group in [('source',original),('literalRendered',actual)]:
  for uid,tri in group.items():
   for om,others in [('source',original),('literalRendered',actual)]:
    for other,mesh in others.items():
     if uid==other:continue
     lo=mesh.min(1);hi=mesh.max(1);pairs=0
     for i in wallids[uid]:
      face=tri[i];ids=np.flatnonzero(np.all(hi>=face.min(0),axis=1)&np.all(lo<=face.max(0),axis=1));pairs+=len(ids)
      for j in ids:assert not intersection_points(rational_face(face),rational_face(mesh[j]))
     trials.append(dict(wallUID=uid,otherOriginalUID=other,wallRepresentation=wm,otherRepresentation=om,wholeOtherOriginalFaces=len(mesh),allWallFaces=wallids[uid],completeWallWorldSHA256=digest(tri.tobytes()),completeOtherWorldSHA256=digest(mesh.tobytes()),completeClosedAABBCandidatePairs=pairs,exactFiniteIntersections=0))
 assert sorted(trials,key=canonical)==sorted(foreign['allProposedOtherOriginalSourceAndLiteralWorldWallTrials'],key=canonical)
 metrics=read(PHYS/'metrics.json');policy=module('man_fuk_numeric_policy','acceptance-policy.py');resolved=[]
 for m in metrics['rows']:
  uid=m['uid'];identity=next(x for x in identities if x['uid']==uid);assert m['sourceSHA256']==sources[uid] and m['sourcePreserved'] and m['missingTerrain']==0 and m['maxSamplerDelta']<=.004 and m['missingDrawnTerrain']==dict(count=0,minRuntimeClearance=None)
  assert m['samplerDisagreement']==dict(count=0,minDelta=0,maxDelta=0,minDrawnClearance=None,minRuntimeClearance=None)
  raw=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=sources[uid],identityProof=identity['proof']),m,metrics['profiles']['mobile'])
  assert set(raw)<={'ground-contact-unresolved','terrain-intersects-source-over-0.5m'} and ('terrain-intersects-source-over-0.5m' not in raw or wallids[uid])
  concerns=next(v for v in validation['results'] if v['uid']==uid).get('concerns',[]);assert set(concerns)<={'sampled-terrain-above-model-bottom','sampled-ground-gap-below-model-bottom'}
  resolved.append(dict(uid=uid,rawNumericReasonsVerbatim=raw,rawGlobalBottomWarningsVerbatim=concerns,onlyVerifiedExposedOriginalAndRenderedWallFacesReceiveGradeRole=wallids[uid],completeOriginalStructuralGraphAndIndependentLiteralAnchorsRequired=True))
 assert {r['uid'] for r in metrics['rows']}==UIDS and ref(manifest)==start
 deps.extend(HERE/n for n in ['xl-complete-multi-source-finite-wall-contexts-v1-20261010.py','xl-man-fuk-ten-v10-exact-contact-clear-cap-wall-paths-v2-20261010.py','original_ordinary_ground_root_graph_20261009.py','original_strict_clear_cap_wall_paths_20261009.py','original_bound_facet_wall_context_v3_20261010.py','exact_original_georef_cell_identity_20261009.py','man_hei_current_bound_mandatory_platform_identity_v2_20261010.py','xl-tung-sing-three-original-footing-readonly-replay-20261010.mjs','support-interface.mjs','acceptance-policy.py'])
 for folder in folders:deps.extend(p for p in folder.iterdir() if p.is_file())
 return dict(contract='complete-current-man-fuk-ten-unchanged-original-ordinary-structural-and-exposed-grade-wall-role-v1',uids=sorted(UIDS),sourceSHA256s=sources,currentManifest=start,completeOriginalFaces=29125,completeOriginalComponents=131,completeCurrentNeighbourForms=70,currentForeignBasicForms=59,allCurrentNativeCatalogueBounds=len(nativebounds),completeCurrentSourceIdentities=identities,completeCurrentOriginalGroundGraph=verified,independentLiteralRenderedStrictFootings=anchors,completeCertifiedSourceAndLiteralWallPaths=wallproofs,allOrdinaryOriginalAndActualRenderedFacesStrictClear=True,allCurrentThirdPartyAndOtherProposedOriginalCrossingWallCollisionsStrictClear=True,rawNumericAndGlobalBottomReasonsPreserved=resolved,rawPhysicalResultPreserved=physics,strictWholeSourceFoundationsPreserved=True,allComponentsAccounted=True,currentTypedPhysicalAccepted=True,reasons=[],terrainProposalGeometryChanged=True,terrainProposal=terrain,sourceGeometryChanges=0,aiGeometryModelling=False,publication=False,newlyInstalled=0,installationApproved=False,evidenceRefs=[ref(p) for p in sorted(set(deps))])
def main():
 assert not DOC.exists();r=recheck();save(DOC/'typed-role.json.gz',r);module('man_fuk_complete_role_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-ten-unchanged-original-ordinary-structural-and-grade-wall-role-v1',[ROOT/x['path'] for x in r['evidenceRefs']],dict(uids=sorted(UIDS),currentTypedPhysicalAccepted=True,reasons=[],completeOriginalFaces=29125,completeOriginalComponents=131,sourceGeometryChanges=0,terrainProposalGeometryChanged=True,browserRequired=True,publication=False,newlyInstalled=0));print(dict(currentTypedPhysicalAccepted=True,faces=29125,parts=131,browserRequired=True),flush=True)
if __name__=='__main__':main()
