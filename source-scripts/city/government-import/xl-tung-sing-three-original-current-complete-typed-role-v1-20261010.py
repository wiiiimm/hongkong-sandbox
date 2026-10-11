"""Complete current three untouched source assets, rooted bodies and two visual sleeves.

Read-only replay of every frozen source/identity/facet/current foreign gate.
No source pose/geometry or acceptance threshold changes; browser still required.
"""
import importlib.util,json,subprocess,numpy as np
from pathlib import Path
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from original_multi_actor_support_graph_20261009 import verify as support
from original_bound_facet_wall_context_v2_20261010 import contexts as certified_contexts
from original_bound_facet_wall_context_20261010 import canonical
from original_strict_clear_cap_wall_paths_20261009 import verify as clear_paths
from tung_sing_original_single_end_visual_sleeves_v2_20261010 import verify_current_visual_roles
from tung_sing_mandatory_three_original_collection_identity_v2_20261010 import verify_files as identity_verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tung-sing-three-original-current-complete-typed-role-v1-20261010';DOC=BASE/BATCH
PHYS=BASE/'government-xl-tung-sing-three-original-literal-parent-physical-v2-20261010';FINITE=BASE/'government-xl-tung-sing-three-original-complete-paired-finite-clearance-v1-20261010';GRAPH=BASE/'government-xl-tung-sing-three-original-current-root-graph-v3-20261010';VISUAL=BASE/'government-xl-tung-sing-three-original-current-rendered-visual-roles-v4-20261010';WALL=BASE/'government-xl-tung-sing-three-original-current-certified-wall-paths-v2-20261010';FOREIGN=BASE/'government-xl-tung-sing-three-original-current-complete-foreign-wall-scope-v3-20261010'
MANIFEST='a3a28145511e3ce6f0b0255d490e1219ad05c643030d00f3e4d9844cdf784b64'
SOURCES={'landsd/53800:0':'01b2b8a50351975e57fa036e8c358f72b93209c684a29194b5bcfeebaa2de60c','landsd/126434:0':'368ec3bcb2b011f8db942a2e294f500043762b15851e55113c95443a48ff5f15','landsd/254604:0':'584d51298a5394f6805284ff87c9d7b12796feac3dbe8950ff55549b1c0cb133'}
COUNTS={'landsd/53800:0':11445,'landsd/126434:0':432,'landsd/254604:0':874}
WALLS={'landsd/53800:0':[7736,7737,8677,8679,8680,10103,10104,10110,10111,10112,10131,10132,10133,10134,10873,10874],'landsd/126434:0':[28,29,30,61,62,67,71,73,74,75,344,358,359,360,361,362,363,364,366,367,368],'landsd/254604:0':[]}
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def checked(folder):
 r=read(folder/'result.json')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 assert len({x['path'] for x in r['evidenceRefs']})==len(r['evidenceRefs'])
 for x in r['evidenceRefs']:assert ref(ROOT/x['path'])==x,x['path']
 return r
def recheck():
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST;receipts=[checked(p) for p in [PHYS,FINITE,VISUAL,WALL,FOREIGN]];physics=receipts[0];rows=read(PHYS/'selection.json.gz')['rows'];assert {r['uid']:r['sourceSHA256'] for r in rows}==SOURCES;current_contexts=read(PHYS/'context.json.gz')['rows'];runtime_path=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';runtime=read(runtime_path);assert {r['uid'] for r in runtime['rows']}==set(SOURCES)
 for p,h in runtime.get('inputHashes',{}).items():assert digest((ROOT/p).read_bytes())==h
 terrain=read(PHYS/'terrain-candidates.json');assert len(terrain)==1 and set(terrain[0]['uids'])==set(SOURCES) and terrain[0]['triangles']==92211<=100000 and ref(ROOT/terrain[0]['path'])['sha256']==terrain[0]['sha256'];patch=read(ROOT/terrain[0]['path']);assert patch.get('nativeMesh') and not patch.get('patches') and not patch.get('hydro');assert len(patch['nativeMesh']['index'])//3==92211
 forms=module('tung_complete_current_forms','xl-final-script-pass.py').load_forms(terrain[0]['bounds']);neighbours=read(PHYS/'neighbour-inputs.json.gz');assert [r['building'] for r in neighbours['rows']]==[r[0] for r in forms] and set(neighbours['candidateIds'])==set(SOURCES);assert neighbours['inputHashes']=={str((ROOT/'3d-viewer'/u).relative_to(ROOT)):digest((ROOT/'3d-viewer'/u).read_bytes()) for _,_,u in forms};assert len(forms)==40;assert all(not r['reasons'] for r in read(PHYS/'neighbour-checks.json')['rows']);native=read(PHYS/'native-neighbour-checks.json');assert set(native['blocked'])==set(native['resolved'])=={'landsd/12851:0','landsd/12852:0','landsd/12854:0','landsd/163705:0'}
 for p,h in native.get('inputHashes',native.get('hashes',{})).items():assert digest((ROOT/p).read_bytes())==h
 validation=read(PHYS/'validation.json');assert validation['checksPassed']==validation['loaderAccepted']==3 and validation['exceptions']==0;foundations=read(PHYS/'foundation.json')['rows'];assert {f['uid'] for f in foundations}==set(SOURCES)
 for f in foundations:
  x=f['foundation'];assert f['sourceSHA256']==SOURCES[f['uid']] and f['strictFoundationAccepted'] and x['completeTerrainTriangles']==x['triangles']==COUNTS[f['uid']] and x['fullyBuriedUpwardTriangles']==0 and x['fullyBuriedAreaFraction']==0
 captured=read(GRAPH/'diagnostic.json.gz');assert captured['manifestSHA256']==MANIFEST and captured['freshCurrentLiveBindingAccepted']
 for p,h in captured['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 original={};actual={};grounds={};streams={};identities=[];assetpaths=[];finite=read(FINITE/'diagnostic.json.gz');wall=read(WALL/'diagnostic.json.gz');wall_proofs=[]
 for row in rows:
  uid=row['uid'];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SOURCES[uid];assetpaths.append(asset);original[uid]=decode_original_world_triangles(raw);streams[uid]=source_stream_binding(raw);r=next(x for x in runtime['rows'] if x['uid']==uid);actual[uid]=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];grounds[uid]=np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3);assert original[uid].shape==actual[uid].shape==(COUNTS[uid],3,3)
  with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
  ctx=next(x for x in current_contexts if x['uid']==uid);identity=identity_verify(row,ctx,HERE/'local'/BATCH/'identity-recheck');saved=next(x for x in read(PHYS/'owned-source-identity.json')['rows'] if x['uid']==uid);assert identity==saved and identity['passed'] and set(identity['mandatoryOriginalRuntimeUIDs'])==set(SOURCES) and identity['standaloneOriginalImportAccepted'] is False;identities.append(identity)
  f=next(x for x in finite['rows'] if x['uid']==uid);assert digest(original[uid].tobytes())==f['completeOriginalWorldSHA256'] and digest(actual[uid].tobytes())==f['completeActualRenderedWorldSHA256'] and digest(grounds[uid].tobytes())==f['completeGroundSHA256'];saved_wall=next(x for x in wall['rows'] if x['uid']==uid)
  actor=next(x for x in captured['completeOriginalActors'] if x['uid']==uid);off=actor['globalFaceRange'][0];assert actor['sourceSHA256']==SOURCES[uid] and actor['originalStreamBindingSHA256']==canonical(streams[uid]) and actor['originalWorldTrianglesSHA256']==digest(original[uid].tobytes());contacts=[[i-off for i in c['globalOriginalFaces']] for c in captured['contactWitnesses'] if all(off<=i<off+COUNTS[uid] for i in c['globalOriginalFaces'])]
  for mode,t in [('completeOriginal',original[uid]),('actualRendered',actual[uid])]:
   prepared=[{'sourceFace':c['sourceFace'],'priorCoarseBoundProofVerbatim':{'sourceFace':c['sourceFace'],'completeOriginal':c['priorCoarseBoundProofVerbatim'][mode]},'pairedExactOriginalFiniteBound':c['pairedExactOriginalFiniteBound' if mode=='completeOriginal' else 'pairedExactActualRenderedFiniteBound'],'completeOriginalBoundProved':c['completeOriginalBoundProved' if mode=='completeOriginal' else 'completeActualRenderedBoundProved']} for c in f['allFaces']];cb={'completeOriginalWorldTrianglesSHA256':digest(t.tobytes()),'completeDrawnGroundSHA256':digest(grounds[uid].tobytes()),'completeFiniteFacetProofRowsSHA256':canonical(prepared)};contexts=certified_contexts(t,grounds[uid],prepared,expected_binding=cb,current_binding=cb);wb={'completeOriginalWorldTrianglesSHA256':digest(t.tobytes()),'completeCurrentFacetContextsSHA256':canonical(contexts),'exactOriginalContactListSHA256':canonical(contacts)};proof=clear_paths(t,contexts,contacts,expected_binding=wb,current_binding=wb);assert proof['allAffectedHavePaths'] and not proof['rawExposureFailures'] and proof['affectedOriginalWallFaces']==WALLS[uid];stored=next(x for x in saved_wall['sourceAndLiteralActualProofs'] if x['representation']==mode);assert canonical(contexts)==canonical(stored['completeCertifiedLowerBoundContexts']) and proof==stored['strictClearCapWallPaths'];wall_proofs.append({'uid':uid,'representation':mode,'proof':proof,'completeCertifiedFiniteContextsSHA256':canonical(contexts)})
 alltri=np.concatenate([original[a['uid']] for a in captured['completeOriginalActors']]);graph=support(alltri,captured['completeOriginalActors'],captured['completeOriginalComponents'],captured['currentOriginalGroundInterfaces'],captured['contactWitnesses'],expected_binding=captured['binding'],current_binding=captured['binding']);graph=json.loads(json.dumps(graph));assert canonical(graph)==canonical(captured['completeCurrentOriginalGraph']);assert graph['genuineGroundAnchorComponents']==[361,365] and set(graph['resolvedOriginalComponents'])|{343,344}==set(range(387)) and graph['reasons']==['unresolved-original-component:343','unresolved-original-component:344']
 for folder,uid,part in [('government-xl-tung-sing-three-original-current-anchor-v2-20261010','landsd/126434:0',0),('government-xl-tung-sing-three-original-current-tower-footing-v2-20261010','landsd/53800:0',361)]:
  inputpath=BASE/folder/'complete-current-original-platform-anchor-input.json.gz';inp=read(inputpath);saved=read(BASE/folder/'complete-current-original-platform-anchor.json.gz');assert digest(inputpath.read_bytes())==saved['inputSHA256'] and inp['manifestSHA256']==MANIFEST and inp['sourceSHA256']==SOURCES[uid];assert np.array_equal(np.asarray(inp['terrain']['position']).reshape(-1,3,3),grounds[uid]);assert np.array_equal(np.asarray(inp['part']['position']).reshape(-1,3,3),original[uid][inp['part']['originalFaceIds']]);r=json.loads(subprocess.check_output(['node',str(HERE/'xl-tung-sing-three-original-footing-readonly-replay-20261010.mjs'),str(inputpath)],cwd=ROOT,text=True));assert r==saved['result'] and saved['strictOriginalCurrentGroundAnchor'] and inp['part']['component']==part
 visual_saved=read(VISUAL/'diagnostic.json.gz');vb=visual_saved['binding'];assert vb['currentManifestSHA256']==MANIFEST and vb['completeCurrentPhysicalSHA256']==digest((PHYS/'result.json').read_bytes()) and vb['completeCurrentForeignActorScopeSHA256']==digest((PHYS/'neighbour-inputs.json.gz').read_bytes());visual=verify_current_visual_roles(original['landsd/53800:0'],actual['landsd/53800:0'],grounds['landsd/53800:0'],graph,streams['landsd/53800:0'],expected_binding=vb,current_binding=vb);assert visual==visual_saved['completeLiteralCurrentVisualRoles'] and visual['typedOriginalVisualRoleAccepted']
 foreign=read(FOREIGN/'diagnostic.json.gz');assert foreign['manifestSHA256']==MANIFEST and foreign['everyOtherProposedOriginalCheckedAsForeignForCreditedWalls'] and not foreign['allExactSourceAuthoredMutualWallIntersectionsRetained'];pieces=[]
 for uid in SOURCES:
  for t in [original[uid],actual[uid]]:
   for face in t[WALLS[uid]]:
    xz=face[:,[0,2]];poly=Polygon(xz);pieces.append(poly if poly.area else LineString(xz) if len(set(map(tuple,xz)))>1 else Point(xz[0]))
 projection=unary_union(pieces);assert projection.wkt==foreign['completeOriginalAndRenderedWallProjectionWKT'];foreign_forms={x['uid']:x for x in foreign['completeActualForeignBasicForms']};native_forms={x['uid']:x for x in foreign['retainedCurrentNativeFormsIndependentlyWholeBoundChecked']};assert len(foreign_forms)==33 and set(native_forms)==set(native['resolved'])
 for nr in neighbours['rows']:
  uid=nr['building']['uid']
  if uid in SOURCES:continue
  record=(native_forms if nr['existingNative'] else foreign_forms)[uid];assert record['completeActualCurrentForm']==nr['building'] and record['currentFormSHA256']==canonical(nr['building'])
  if not nr['existingNative']:
   rings=nr['building']['rings'];poly=Polygon(rings[0],rings[1:]);assert poly.is_valid and poly.area>0 and poly.disjoint(projection)
 walls=np.concatenate([t[WALLS[uid]] for uid in SOURCES for t in [original[uid],actual[uid]]]);native_bounds=[]
 for url in read(manifest)['officialModelCatalogues']:
  for e in read(ROOT/'3d-viewer'/url)['models']:
   b=np.asarray(e['worldBounds'],float);assert b.shape==(2,3) and np.isfinite(b).all() and np.all(b[1]>=b[0]) and e['uid'] not in SOURCES;assert all(np.any(b[0]>face.max(0)) or np.any(b[1]<face.min(0)) for face in walls);native_bounds.append({'uid':e['uid'],'catalogue':url,'sourceSHA256':e['sha256'],'completeWholeSourceBounds':b.tolist(),'strictlyDisjointFromEveryOriginalAndRenderedCrossingWall':True})
 assert native_bounds==foreign['completeCurrentNativeWholeSourceBounds']
 from exact_original_shell_intersections_20261009 import rational_face,intersection_points
 trials=[]
 for wm,group in [('source',original),('literalRendered',actual)]:
  for uid,tri in group.items():
   for om,others in [('source',original),('literalRendered',actual)]:
    for other,mesh in others.items():
     if uid==other:continue
     lo=mesh.min(1);hi=mesh.max(1);pairs=0
     for i in WALLS[uid]:
      face=tri[i];ids=np.flatnonzero(np.all(hi>=face.min(0),axis=1)&np.all(lo<=face.max(0),axis=1));pairs+=len(ids)
      for j in ids:assert not intersection_points(rational_face(face),rational_face(mesh[j])),'Another original source body intersects credited wall'
     trials.append({'wallUID':uid,'otherOriginalUID':other,'wallRepresentation':wm,'otherRepresentation':om,'wholeOtherOriginalFaces':len(mesh),'allWallFaces':WALLS[uid],'completeWallWorldSHA256':digest(tri.tobytes()),'completeOtherWorldSHA256':digest(mesh.tobytes()),'completeClosedAABBCandidatePairs':pairs,'exactFiniteIntersections':0})
 assert sorted(trials,key=canonical)==sorted(foreign['allProposedOtherOriginalSourceAndLiteralWorldWallTrials'],key=canonical)
 metrics=read(PHYS/'metrics.json');policy=module('tung_all_numeric_policy','acceptance-policy.py');resolved=[];remaining=[]
 for m in metrics['rows']:
  uid=m['uid'];assert uid in SOURCES and m['sourceSHA256']==SOURCES[uid] and m['sourcePreserved'] and m['missingTerrain']==m['missingDrawnTerrain']==0 and m['maxSamplerDelta']<=.004 and m['samplerDisagreement']==0;identity=next(r for r in identities if r['uid']==uid);raw=policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':SOURCES[uid],'identityProof':identity['proof']},m,metrics['profiles']['mobile']);assert set(raw)==({'ground-contact-unresolved'} if not WALLS[uid] else {'ground-contact-unresolved','terrain-intersects-source-over-0.5m'});v=next(x for x in validation['results'] if x['uid']==uid);assert set(v.get('concerns',[]))=={'sampled-terrain-above-model-bottom','sampled-ground-gap-below-model-bottom'};resolved.append({'uid':uid,'rawNumericReasonsVerbatim':raw,'rawGlobalBottomWarningsVerbatim':v['concerns'],'groundContactDiagnosticReplacedByComplete387SourceComponentCurrentFootingsAndVisualRole':True,'groundCrossingResolvedOnlyForExactVerifiedWallFaces':WALLS[uid],'globalBottomRemoteFootprintWarningsResolvedOnlyByCompleteFiniteAllOriginalAndRenderedFacesAndRootedSourceParts':True})
 assert set(metrics_uid['uid'] for metrics_uid in metrics['rows'])==set(SOURCES);assert ref(manifest)==start
 deps=[Path(__file__),manifest,runtime_path,HERE/'xl-tung-sing-three-original-footing-readonly-replay-20261010.mjs',HERE/'tung_sing_mandatory_three_original_collection_identity_v2_20261010.py',HERE/'tung_sing_original_single_end_visual_sleeves_v2_20261010.py',HERE/'original_multi_actor_support_graph_20261009.py',HERE/'original_strict_clear_cap_wall_paths_20261009.py',HERE/'original_bound_facet_wall_context_v2_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',*assetpaths,ROOT/terrain[0]['path']]
 for folder in [PHYS,FINITE,GRAPH,VISUAL,WALL,FOREIGN]:deps.extend(p for p in folder.iterdir() if p.is_file())
 return {'uids':sorted(SOURCES),'contract':'complete-current-tung-sing-mandatory-three-original-grounded-body-and-named-visual-role-v1','currentManifest':start,'completeOriginalFaces':12751,'completeOriginalComponents':387,'completeCurrentNeighbourForms':40,'currentForeignBasicForms':33,'allCurrentNativeCatalogueBounds':len(native_bounds),'completeCurrentSourceIdentities':identities,'completeCurrentOriginalGroundGraph':graph,'completeCurrentLiteralVisualRoles':visual,'completeCertifiedSourceAndLiteralWallPaths':wall_proofs,'allOrdinaryOriginalAndActualRenderedFacesStrictClear':True,'allCurrentThirdPartyAndOtherProposedOriginalCrossingWallCollisionsStrictClear':True,'rawNumericAndGlobalBottomReasonsPreserved':resolved,'rawPhysicalReasonsPreserved':physics['reasons'],'replacedDiagnosticReasonsOnly':physics['reasons'],'strictWholeSourceFoundationsPreserved':True,'allComponentsAccounted':True,'currentTypedPhysicalAccepted':True,'reasons':remaining,'terrainProposalGeometryChanged':True,'terrainProposal':terrain,'sourceGeometryChanges':0,'aiGeometryModelling':False,'visualStructuralCredit':False,'publication':False,'newlyInstalled':0,'installationApproved':False,'evidenceRefs':[ref(p) for p in sorted(set(deps))]}
def main():
 assert not DOC.exists();role=recheck();save(DOC/'typed-role.json.gz',role);m=module('tung_complete_role_fence','xl-popcorn-source-investigations-checkpoints-20261009.py');m.freeze(BATCH,'complete-current-three-original-certified-wall-and-visual-role-v1',[ROOT/r['path'] for r in role['evidenceRefs']],{'uids':sorted(SOURCES),'currentTypedPhysicalAccepted':True,'reasons':role['reasons'],'completeOriginalFaces':12751,'completeOriginalComponents':387,'sourceGeometryChanges':0,'terrainProposalGeometryChanged':True,'browserRequired':True,'installationApproved':False,'publication':False,'newlyInstalled':0});print({'currentTypedPhysicalAccepted':True,'reasons':role['reasons'],'browserRequired':True},flush=True)
if __name__=='__main__':main()
