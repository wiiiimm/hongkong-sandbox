"""Complete current source-bound Ching Hin wall and original grade-root proof.

Preserves three raw wall failures and zero old ordinary roots. Only exact
original exposed wall grade interfaces root the unchanged complete assembly.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from xl_source_stream_binding_20261009 import source_stream_binding
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_20261009 import packed_world_bounds
from unchanged_authored_crossing_wall_role_20261009 import verify_wall_role
from unchanged_closed_column_role_v2_20261009 import canonical_sha
from original_exposed_wall_grade_root_graph_20261009 import verify as verify_grade
from original_bound_facet_wall_context_v3_20261010 import contexts as recompute_contexts
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
BATCH='xl-terrain-recovery-20261010-no1-garden-current-complete-role-v1'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
PHYSICAL=BASE/'government-xl-no1-garden-literal-parent-complete-current-physical-v5-20261010'
GRAPH=BASE/'xl-terrain-recovery-20261010-no1-garden-literal-parent-current-original-support-v3'
FINITE=BASE/'xl-terrain-recovery-20261010-no1-garden-literal-parent-current-complete-paired-column-v3'
CONTEXT=BASE/'xl-terrain-recovery-20261010-no1-garden-literal-parent-finite-wall-grade-context-v4'
PROVIDER=BASE/'xl-terrain-recovery-20261010-no1-garden-provider-wall-role-v1'
GEOMETRY=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz'
OLD_GEOMETRY=HERE/'local/government-xl-no1-garden-complete-current-physical-v3-20261010/runtime-geometry.json.gz'
UID='landsd/304714:0';SOURCE='f06178309a08955ef93e0d5424e864075632670d3bb2902d3c7d9aaee933beca'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def receipt(folder):
 result=read(folder/'result.json')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 return result

def components(tri):
 parent=list(range(len(tri)));edges={}
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for i,face in enumerate(tri):
  for a,b in zip(face,np.roll(face,-1,axis=0)):
   key=tuple(sorted((tuple(a),tuple(b))))
   if key in edges:parent[find(i)]=find(edges[key])
   else:edges[key]=i
 groups={}
 for i in range(len(tri)):groups.setdefault(find(i),[]).append(i)
 return [dict(actorUID=UID,globalOriginalFaces=f,bounds=[tri[f].min(axis=(0,1)).tolist(),tri[f].max(axis=(0,1)).tolist()]) for f in sorted(groups.values(),key=min)]

def recheck():
 receipts={p.name:receipt(p) for p in [PHYSICAL,GRAPH,FINITE,CONTEXT,PROVIDER]};physical=receipts[PHYSICAL.name]
 selected=read(PHYSICAL/'selection.json.gz');assert len(selected['rows'])==1;row=selected['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SOURCE
 manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_ref=ref(manifest);assert manifest_ref['sha256']==selected['manifestSHA256']==read(PHYSICAL/'selection.json.gz')['manifestSHA256']
 # Replay the fresh source/native membership, whole terrain routing and exact
 # unchanged-adjacent seam producer inputs without mutating any file.
 for r in physical['evidenceRefs']:assert ref(ROOT/r['path'])==r,'Current physical input changed: '+r['path']
 proposal=read(PHYSICAL/'explicit-literal-parent-proposal.json');assert proposal['terrainProposalGeometryChanged'] and proposal['sourceGeometryChanges']==0 and not proposal['disjointClaim'] and proposal['retainedChildrenExactlyUnchanged']
 candidates=read(PHYSICAL/'terrain-candidates.json');assert len(candidates)==1 and candidates[0]==proposal['finalCandidate']
 candidate=candidates[0];assert ref(ROOT/candidate['path'])=={k:candidate[k] for k in ('path','sha256')}
 parent_path=ROOT/'3d-viewer'/candidate['replaces']['url'];assert digest(parent_path.read_bytes())==candidate['replaces']['sha256']
 parent=read(parent_path);wrapper=read(ROOT/candidate['path']);child=next(c for c in wrapper['patches'] if c['meta'].get('targetUids')==[UID]);assert [c for c in wrapper['patches'] if c is not child]==parent['patches'] and len(parent['patches'])==8 and wrapper['elev']==parent['elev'] and wrapper.get('renderedElev')==parent.get('renderedElev')
 raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==SOURCE;tri=decode_original_world_triangles(raw);streams=source_stream_binding(raw)
 role=read(PROVIDER/'expected-role.json');assert role['uid']==UID and role['sourceSHA256']==SOURCE and streams==role['providerExteriorProvenanceBinding']['exactPackedSourceStreams'] and digest(tri.tobytes())==role['providerExteriorProvenanceBinding']['completeOriginalWorldTrianglesSHA256']
 g=read(GEOMETRY)['rows'][0];old=read(OLD_GEOMETRY)['rows'][0];assert g['uid']==old['uid']==UID
 for key,dtype in [('position',np.float64),('index',np.uint32)]:assert np.array_equal(np.asarray(g[key],dtype=dtype),np.asarray(old[key],dtype=dtype)),'Frozen numeric source/ground inventory changed: '+key
 p=np.asarray(g['position'],float).reshape(-1,3);idx=np.asarray(g['index'],dtype=np.uint32).reshape(-1,3);world=p[idx];ground=np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3)
 assert world.shape==tri.shape==(821,3,3);roundoff=float(np.max(np.abs(world-tri)));assert roundoff<=1e-9 and roundoff==float(np.max(np.abs(np.asarray(old['position'],float).reshape(-1,3)[np.asarray(old['index'],np.uint32).reshape(-1,3)]-tri)))
 finite=read(FINITE/'diagnostic.json.gz')['rows'][0];assert finite['completeOriginalWorldSHA256']==digest(tri.tobytes()) and finite['completeActualRenderedWorldSHA256']==digest(world.tobytes()) and finite['completeGroundSHA256']==digest(ground.tobytes())
 faces=finite['allFaces'];assert [f['sourceFace'] for f in faces]==list(range(821));assert finite['unprovedActualRenderedFaces']==finite['unprovedOriginalFaces']==role['wallFaces']==[158,159,215]
 assert all(f['completeActualRenderedBoundProved'] and f['completeOriginalBoundProved'] for f in faces if f['sourceFace'] not in role['wallFaces'])
 d=read(CONTEXT/'diagnostic.json.gz');ctx=d['completeCertifiedLowerBoundContexts'];normalized=[]
 for f in faces:
  def cert(key,prior_key):
   c=f[key]
   if c is None:return None
   prior=f['priorCoarseBoundProofVerbatim'][prior_key];assert c['sourceFaceSHA256']==prior['sourceFaceSHA256'] and c['completeCurrentGroundSHA256']==prior['completeCurrentGroundSHA256']
   return {**c,'allProjectedBoundingCandidateOriginalGroundFacets':prior['allProjectedBoundingCandidateOriginalGroundFacets']}
  normalized.append({**f,'pairedExactOriginalFiniteBound':cert('exactOriginalColumnRefinement','completeOriginal'),'pairedExactActualRenderedFiniteBound':cert('exactActualRenderedColumnRefinement','actualRendered')})
 assert normalized==d['normalizedFiniteProofRows'] and canonical_sha(faces)==d['rawFiniteRowsSHA256']
 context_binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeDrawnGroundSHA256=digest(ground.tobytes()),completeFiniteFacetProofRowsSHA256=canonical_sha(normalized));assert recompute_contexts(tri,ground,normalized,expected_binding=context_binding,current_binding=context_binding)==ctx
 assert len(ctx)==821 and d['originalCapPaths']['affectedOriginalWallFaces']==role['wallFaces']
 neighbours=read(PHYSICAL/'neighbour-inputs.json.gz');assert len(neighbours['rows'])==14 and neighbours['candidateIds']==[UID];tile_hashes=neighbours['inputHashes'];forms={}
 for path,sha in tile_hashes.items():
  assert digest((ROOT/path).read_bytes())==sha;forms.update({f['uid']:f for f in read(ROOT/path)['buildings']})
 for nr in neighbours['rows']:assert forms[nr['building']['uid']]==nr['building']
 refs=[];catalogue_hashes={};native_bounds=[];native_entries={};touching=[]
 for url in read(manifest)['officialModelCatalogues']:
  cat=ROOT/'3d-viewer'/url;catalogue_hashes[str(cat.relative_to(ROOT))]=digest(cat.read_bytes());refs.append(ref(cat))
  for e in read(cat)['models']:
   b=np.asarray(e['worldBounds'],float);assert b.shape==(2,3) and np.isfinite(b).all() and (b[1]>=b[0]).all() and e['sha256'];assert e['uid'] not in native_entries
   native_entries[e['uid']]=(cat,e);native_bounds.append(dict(uid=e['uid'],catalogue=url,sourceSHA256=e['sha256'],originalWholeBounds=b.tolist()))
   if any(not(np.any(b[0]>face.max(axis=0)) or np.any(b[1]<face.min(axis=0))) for face in tri[role['wallFaces']]):touching.append(e['uid'])
 assert not touching,'Whole native bounds touch credited walls; exact original meshes required: '+str(touching)
 assert UID not in native_entries
 actors=[];actor_manifest=[]
 for nr in neighbours['rows']:
  form=nr['building'];uid=form['uid']
  if uid==UID:continue
  assert not form.get('modelGeometry'),'Embedded source actor requires full runtime mesh'
  source=dict(currentFormSHA256=canonical_sha(form),currentTileHashes=tile_hashes,completeNeighbourInputs=ref(PHYSICAL/'neighbour-inputs.json.gz'))
  if uid in native_entries:
   cat,e=native_entries[uid];asset=cat.parent/e['asset'];proof=packed_world_bounds(asset.read_bytes());assert proof['sourceSHA256']==e['sha256'] and proof['completeOriginalTriangles']==e['triangles'];assert np.max(np.abs(np.asarray(proof['originalWholeSourceBounds'])-np.asarray(e['worldBounds'])))<.002
   source.update(originalNativeAsset=ref(asset),currentCatalogue=ref(cat),completeNativeNeighbourChecks=ref(PHYSICAL/'native-neighbour-checks.json'),completePackedWorldGeometryProof=proof);refs.append(ref(asset));actors.append(dict(uid=uid,proofType='complete-original-native-bounds',originalWholeSourceBounds=proof['originalWholeSourceBounds'],currentSourceBinding=source));actor_manifest.append(dict(uid=uid,proofType='complete-original-native-bounds',originalWholeSourceBoundsSHA256=canonical_sha(proof['originalWholeSourceBounds']),currentSourceBinding=source))
  else:
   assert not nr['existingNative'];actors.append(dict(uid=uid,proofType='current-basic-full-footprint',originalCurrentRings=form['rings'],currentSourceBinding=source));actor_manifest.append(dict(uid=uid,proofType='current-basic-full-footprint',originalCurrentRingsSHA256=canonical_sha(form['rings']),currentSourceBinding=source))
 boundary=dict(candidateUID=UID,ownedUIDs=[UID],currentScopeUIDs=sorted(nr['building']['uid'] for nr in neighbours['rows']),manifestSHA256=manifest_ref['sha256'],currentFormInputHashes=tile_hashes,nativeCatalogueInputHashes=catalogue_hashes,allNativeOriginalBoundsSHA256=canonical_sha(native_bounds),allNativeOriginalBoundsCount=len(native_bounds),nativeOriginalBoundsTouchingCreditedWalls=touching,currentPhysicalSelection=ref(PHYSICAL/'selection.json.gz'),completeOriginalRuntimeGeometry=ref(GEOMETRY))
 scope=dict(completeCurrentActorScope=True,actors=actors,expectedActorManifest=sorted(actor_manifest,key=lambda a:a['uid']),currentGroupBoundaryBinding=boundary)
 binding={**streams,'decodedWorldTrianglesSHA256':digest(tri.tobytes()),'drawnGroundSHA256':digest(ground.tobytes()),'continuousFaceContextsSHA256':canonical_sha(ctx),'reviewedOriginalWallRoleSHA256':canonical_sha(role),'currentForeignScopeSHA256':canonical_sha({k:scope[k] for k in ['completeCurrentActorScope','expectedActorManifest','currentGroupBoundaryBinding']})}
 wall=verify_wall_role(tri,ground,ctx,expected_binding=binding,current_binding=binding,expected_role=role,foreign_scope=scope);assert wall['verifiedWallRole'],wall['reasons']
 graph=read(GRAPH/'diagnostic.json.gz');actual=components(tri);assert actual==graph['components'] and len(actual)==3;assert canonical_sha(streams)==graph['actors'][0]['originalStreamBindingSHA256']
 original_positions=np.empty_like(p);assigned={}
 for vertices,face in zip(idx,tri):
  for v,point in zip(vertices,face):
   v=int(v)
   if v in assigned:assert np.array_equal(assigned[v],point)
   else:assigned[v]=point;original_positions[v]=point
 assert set(assigned)==set(range(len(p))) and np.array_equal(original_positions[idx],tri)
 indexed=[dict(uid=UID,sourceSHA256=SOURCE,position=original_positions.reshape(-1).tolist(),index=idx.reshape(-1).tolist())];assert canonical_sha(indexed)==graph['binding']['originalIndexedSourcesSHA256']
 ordered_ground=np.unique(ground.reshape(-1,9),axis=0).reshape(-1,3,3);assert digest(ordered_ground.tobytes())==graph['binding']['currentDrawnGroundSHA256'];contacts=[r['globalOriginalFaces'] for r in graph['exactOriginalContacts']]
 grade_binding={**graph['binding'],'completeCurrentFacetContextsSHA256':canonical_sha(ctx),'exactOriginalContactListSHA256':canonical_sha(contacts),'visualOnlyComponentsSHA256':canonical_sha([]),'freshCurrentGeometrySHA256':ref(GEOMETRY)['sha256'],'currentPhysicalResultSHA256':ref(PHYSICAL/'result.json')['sha256'],'currentForeignScopeSHA256':binding['currentForeignScopeSHA256']}
 support=verify_grade(tri,graph['actors'],actual,graph['contactWitnesses'],indexed,ordered_ground,ctx,contacts,[],expected_binding=grade_binding,current_binding=grade_binding);assert support['supportInterfaceAccepted'] and not support['unresolvedOriginalComponents'] and support['exactExposedWallGradeRootComponents']==[0] and not support['ordinaryGroundRootComponents']
 grade_faces=sorted({r['sourceFace'] for r in support['exactCurrentUpperGradeInterfaces']});rendered_grade=exact_upper_ground_interfaces(world,grade_faces,ordered_ground);assert {r['sourceFace'] for r in rendered_grade}==set(grade_faces),'Source grade root absent from actual rendered original'
 metrics=read(PHYSICAL/'metrics.json');foundation=read(PHYSICAL/'foundation.json');validation=read(PHYSICAL/'validation.json');identity=read(PHYSICAL/'owned-source-identity.json');assert len(identity['rows'])==1 and identity['rows'][0]['passed']
 metric=metrics['rows'][0];f=foundation['rows'][0];assert metric['uid']==f['uid']==UID and metric['sourceSHA256']==f['sourceSHA256']==SOURCE and metric['sourcePreserved'] is True
 assert f['strictFoundationAccepted'] is True and f['foundation']['completeTerrainTriangles']==f['foundation']['triangles']==821 and f['foundation']['fullyBuriedTriangles']==f['foundation']['fullyBuriedUpwardTriangles']==0
 spec=importlib.util.spec_from_file_location('no1_numeric',HERE/'acceptance-policy.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy);numeric=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCE,identityProof=identity['rows'][0]['proof']),metric,metrics['profiles']['mobile'])
 assert metric['missingTerrain']==0 and metric['maxSamplerDelta']<=.004 and metric['maxLowGap']<=1 and metric['minLowGap']<=.1
 native=read(PHYSICAL/'native-neighbour-checks.json');expected_native={u for u in native_entries if u in {r['building']['uid'] for r in neighbours['rows']}};assert set(native['resolved'])==set(native['blocked'])==expected_native and all(r['passed'] for r in native['rows']) and len(native['rows'])==len(expected_native)
 checks=read(PHYSICAL/'neighbour-checks.json');assert len(checks['rows'])==14 and not any(r['reasons'] for r in checks['rows']);assert validation['checksPassed']==validation['loaderAccepted']==1 and not validation['exceptions']
 remaining=sorted(set(physical['reasons']+numeric)-{'terrain-intersects-source-over-0.5m',UID+':terrain-intersects-source-over-0.5m'});assert not remaining,remaining
 for folder in [GRAPH,FINITE,CONTEXT,PROVIDER]:refs.extend(ref(folder/n) for n in ['result.json']+(['diagnostic.json.gz'] if folder!=PROVIDER else ['expected-role.json','original-source-provenance.json']))
 refs.extend(physical['evidenceRefs']);refs.extend(ref(p) for p in [Path(__file__),GEOMETRY,OLD_GEOMETRY,PHYSICAL/'metrics.json',PHYSICAL/'foundation.json',PHYSICAL/'validation.json',PHYSICAL/'owned-source-identity.json',PHYSICAL/'neighbour-checks.json',PHYSICAL/'native-neighbour-checks.json',PHYSICAL/'neighbour-inputs.json.gz',PHYSICAL/'selection.json.gz',HERE/'unchanged_authored_crossing_wall_role_20261009.py',HERE/'unchanged_open_exterior_paths_v2_20261009.py',HERE/'original_exposed_wall_grade_root_graph_20261009.py',HERE/'original_ordinary_ground_root_graph_20261009.py',HERE/'original_strict_clear_cap_wall_paths_20261009.py',HERE/'exact_original_upper_ground_interfaces_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'original_bound_facet_wall_context_v3_20261010.py',HERE/'test_original_bound_facet_wall_context_v3_20261010.py',HERE/'original_bound_facet_wall_context_20261010.py',HERE/'test_original_bound_facet_wall_context_20261010.py',HERE/'xl_source_stream_binding_20261009.py',HERE/'exact_packed_world_bounds_20261009.py'])
 refs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path']);assert all(ref(ROOT/r['path'])==r for r in refs);assert ref(manifest)==manifest_ref
 return dict(contract='no1-garden-complete-current-provider-wall-and-exact-grade-root-v1',uid=UID,sourceSHA256=SOURCE,binding=binding,completeOriginalFaces=821,completeOriginalComponents=3,completeOriginalIndexedSourceAndPartitionRecomputed=True,maximumSourceRuntimeTransformRoundoffM=roundoff,sourceToRuntimeEveryFaceCorrespondenceProved=True,freshCompleteFiniteProofRecomputedForChangedDrawnGround=True,originalWallRole=wall,completeOriginalGradeSupport=support,actualRenderedGradeInterfaces=rendered_grade,currentNeighbourFormsAccounted=14,currentNativeNeighboursAccounted=len(expected_native),allCurrentNativeOriginalWholeBoundsChecked=len(native_bounds),strictFoundationAccepted=True,rawPhysicalReasons=physical['reasons'],freshNumericReasons=numeric,unresolvedIndependentPhysicalReasons=remaining,independentPhysicalChecksPassed=True,currentManifest=manifest_ref,terrainProposalChanged=True,wholeLiteralCurrentParentFacetsRestoredForVilla=True,sourceGeometryChanges=0,modelGeometryAI=False,closedSolidCertified=False,installationApproved=False,publication=False,evidenceRefs=refs)

def main():
 assert not DOC.exists();typed=recheck();save(DOC/'typed-role.json.gz',typed)
 spec=importlib.util.spec_from_file_location('f',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-current-source-provider-wall-exact-grade-root-v1',[ROOT/r['path'] for r in typed['evidenceRefs']],dict(uids=[UID],sourceSHA256=SOURCE,completeOriginalFaces=821,completeOriginalComponents=3,independentPhysicalChecksPassed=True,unresolvedIndependentPhysicalReasons=[],rawPhysicalReasons=typed['rawPhysicalReasons'],terrainProposalChanged=True,wholeLiteralCurrentParentFacetsRestoredForVilla=True,fullAcceptance=False,installationApproved=False));print(json.dumps(dict(passed=True,faces=821,components=3,gradeRoots=typed['completeOriginalGradeSupport']['allIndependentGroundRoots'])),flush=True)
if __name__=='__main__':main()
