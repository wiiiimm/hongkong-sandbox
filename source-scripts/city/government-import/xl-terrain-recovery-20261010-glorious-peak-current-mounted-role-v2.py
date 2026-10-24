"""Current complete Glorious Peak original support and separately mounted visuals.

Every old negative stays immutable. Fresh current identities/actor scope are
bound through an exact disjoint manifest rebind; no geometry or tolerance edits.
"""
import importlib.util,json,uuid
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from glorious_peak_original_mounted_detail_roles_v2_20261010 import verify as mounted,canonical,SOURCES
from original_ordinary_ground_root_graph_20261009 import verify as ordinary_graph
from original_exposed_wall_grade_root_graph_20261009 import verify as grade_graph
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from exact_original_paired_finite_clearance_20261010 import verify as paired_clearance
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-glorious-peak-current-mounted-role-v2';DOC=BASE/BATCH
PHYSICAL=BASE/'government-xl-terrain-recovery-glorious-peak-original-pair-current-physical-v2-20261010';SUPPORT=BASE/'xl-terrain-recovery-20261010-glorious-peak-wall-grade-source-v1';PROVIDER=BASE/'xl-terrain-recovery-20261010-glorious-peak-provider-mounted-roles-v1';REBIND=BASE/'xl-terrain-recovery-20261010-glorious-peak-post-ko-fung-current-rebind-v1';CLEARANCE=BASE/'xl-terrain-recovery-20261010-glorious-peak-complete-paired-finite-clearance-v1';ORDINARY=BASE/'xl-terrain-recovery-20261010-glorious-peak-original-current-support-v1';GEOMETRY=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';UIDS=list(SOURCES);MANIFEST=ROOT/'3d-viewer/city/data/manifest.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def normalized(d):return json.loads(json.dumps(d))
def archived_or_current(r):
 p=ROOT/r['path']
 if r['path']==str(MANIFEST.relative_to(ROOT)) and r['sha256']!=digest(MANIFEST.read_bytes()):assert r['sha256']==digest((REBIND/'historical-manifest.json').read_bytes())
 else:assert ref(p)==r,'Changed frozen input:'+r['path']
def receipt(doc):
 r=read(doc/'result.json');assert read(doc/'neon-sync.json')==dict(jobId=r['jobId'],resultVerified=True)
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p in r['evidenceRefs']:archived_or_current(p)
 return r
def recheck():
 current_sha=digest(MANIFEST.read_bytes());physical=receipt(PHYSICAL);sr=receipt(SUPPORT);ordinary_receipt=receipt(ORDINARY);pr=receipt(PROVIDER);rr=receipt(REBIND);cr=receipt(CLEARANCE);rebinding=read(REBIND/'diagnostic.json.gz');assert current_sha==rebinding['currentManifestSHA256'] and rebinding['verifiedDisjointGlobalManifestRebind'] and rebinding['allFrozenNumericAndSourceInputHashesUnchanged']
 selected=read(PHYSICAL/'selection.json.gz');rows=selected['rows'];assert [r['uid'] for r in rows]==UIDS and selected['manifestSHA256']==rebinding['oldManifestSHA256'];identities=rebinding['completeCurrentIdentities'];assert {r['uid'] for r in identities}==set(UIDS) and all(r['passed'] and r['exactRouteManifestSHA256']==current_sha for r in identities)
 geometry=read(GEOMETRY);gs={g['uid']:g for g in geometry['rows']};assert set(gs)==set(UIDS)
 for p,sha in geometry['inputHashes'].items():archived_or_current(dict(path=p,sha256=sha))
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in rows:assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,r['native']['cacheKey'])).fetchone()==(r['native']['resultSha'],)
 graph=read(SUPPORT/'diagnostic.json.gz');role=read(PROVIDER/'expected-role.json');provenance=read(PROVIDER/'original-source-provenance.json');streams={};pieces=[];worldpieces=[];indexed=[];contexts=[];meshes={};cursor=0;refs=[]
 for r in rows:
  uid=r['uid'];asset=ROOT/r['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SOURCES[uid]==r['sourceSHA256']==gs[uid]['sourceSHA256'];streams[uid]=source_stream_binding(raw);decoded=decode_original_world_triangles(raw);g=gs[uid];positions=np.asarray(g['position']).reshape(-1,3);indices=np.asarray(g['index'],np.uint32).reshape(-1,3);world=positions[indices];assert decoded.shape==world.shape and np.max(np.abs(decoded-world))<=1e-9
  original=np.empty_like(positions);assigned={}
  for ids,face in zip(indices,decoded):
   for i,v in zip(ids,face):
    i=int(i)
    if i in assigned:assert np.array_equal(assigned[i],v)
    else:assigned[i]=v;original[i]=v
  assert set(assigned)==set(range(len(original))) and np.array_equal(original[indices],decoded);indexed.append(dict(uid=uid,sourceSHA256=r['sourceSHA256'],position=original.reshape(-1).tolist(),index=indices.reshape(-1).tolist()));pieces.append(decoded);worldpieces.append(world);meshes[uid]=decoded
  cp=BASE/f"xl-terrain-recovery-20261010-glorious-peak-{uid.split('/')[1].split(':')[0]}-complete-context-v1"/'diagnostic.json.gz';d=read(cp);assert d['sourceSHA256']==r['sourceSHA256'] and len(d['faces'])==len(decoded) and all(c['sourceFace']==i for i,c in enumerate(d['faces']));contexts.extend({**c,'sourceFace':cursor+i} for i,c in enumerate(d['faces']));cursor+=len(decoded);refs.extend(d['evidenceRefs']+[ref(cp),ref(asset)])
 tri=np.concatenate(pieces);world=np.concatenate(worldpieces);ground=np.unique(np.concatenate([np.asarray(gs[u]['drawnGroundGeometry']).reshape(-1,9) for u in UIDS]),axis=0).reshape(-1,3,3);gb=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),currentDrawnGroundSHA256=digest(ground.tobytes()),groundInterfacesInputSHA256=digest(GEOMETRY.read_bytes()),supportScope='complete-current-drawn-ground-only',originalIndexedSourcesSHA256=canonical(indexed));original_graph=read(ORDINARY/'diagnostic.json.gz');assert gb==original_graph['binding']
 replay=normalized(ordinary_graph(tri,original_graph['actors'],original_graph['components'],original_graph['contactWitnesses'],indexed,ground,expected_binding=gb,current_binding=gb));assert all(replay[k]==original_graph[k] for k in replay),'Complete original ordinary graph differs'
 grade_binding={**gb,'completeCurrentFacetContextsSHA256':canonical(contexts),'exactOriginalContactListSHA256':canonical([]),'visualOnlyComponentsSHA256':canonical([])};assert grade_binding==graph['binding']
 grade_replay=normalized(grade_graph(tri,original_graph['actors'],original_graph['components'],original_graph['contactWitnesses'],indexed,ground,contexts,[],[],expected_binding=grade_binding,current_binding=grade_binding));assert all(grade_replay[k]==graph[k] for k in grade_replay),'Complete original exposed-wall grade/support graph differs'
 grade_faces=sorted({r['sourceFace'] for r in graph['exactCurrentUpperGradeInterfaces']});actual_grade=exact_upper_ground_interfaces(world,grade_faces,ground);assert normalized(actual_grade)==graph['actualRenderedWallGradeInterfaces'] and {r['sourceFace'] for r in actual_grade}==set(grade_faces)
 assert len(graph['components'])==365 and len(graph['resolvedOriginalComponents'])==359
 assert role['sources']==SOURCES and role['providerRootAndStreams']==streams==provenance['providerRootAndStreams'] and role['providerRootAndStreamsSHA256']==canonical(streams) and role['completeOriginalWorldTrianglesSHA256']==digest(tri.tobytes()) and role['completeIndexedOriginalGraph']==ref(SUPPORT/'diagnostic.json.gz')
 for c in role['allNamedOriginalVisualComponents']:assert graph['components'][c['component']]['actorUID']==c['actorUID'] and graph['components'][c['component']]['globalOriginalFaces']==c['allOriginalFaces'] and digest(tri[c['allOriginalFaces']].tobytes())==c['completeOriginalVerticesSHA256']
 finite=read(CLEARANCE/'diagnostic.json.gz');assert len(finite['rows'])==2;affected=set(graph['exactOriginalClearRoofPaths']['affectedOriginalWallFaces']);assert affected==set(range(18662,18944)[i] for i in [56,57,79,80,83,108,109,144,172]);cursor=0
 for r in finite['rows']:
  uid=r['uid'];g=gs[uid];actual_ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);actual_world=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert r['sourceSHA256']==SOURCES[uid] and r['completeOriginalWorldSHA256']==digest(meshes[uid].tobytes()) and r['completeActualRenderedWorldSHA256']==digest(actual_world.tobytes()) and r['completeGroundSHA256']==digest(actual_ground.tobytes()) and len(r['allFaces'])==len(meshes[uid])
  assert {cursor+i for i in r['unprovedOriginalFaces']}<=affected and {cursor+i for i in r['unprovedActualRenderedFaces']}<=affected
  for i,f in enumerate(r['allFaces']):
   assert f['sourceFace']==i and f['priorClippedConservativeProofVerbatim']['coarseOriginalAndRenderedProofVerbatim']['completeOriginal']['sourceFaceSHA256']==digest(meshes[uid][i].tobytes()) and f['priorClippedConservativeProofVerbatim']['coarseOriginalAndRenderedProofVerbatim']['actualRendered']['sourceFaceSHA256']==digest(actual_world[i].tobytes())
   for mode,face,key,oldkey in [('Original',meshes[uid][i],'pairedExactOriginalFiniteBound','completeOriginalBoundProved'),('ActualRendered',actual_world[i],'pairedExactActualRenderedFiniteBound','completeActualRenderedBoundProved')]:
    old=f['priorClippedConservativeProofVerbatim'][oldkey];new=f[key]
    if new is not None:assert normalized(paired_clearance(face,actual_ground))==new,'Paired exact finite source/ground proof changed'
    assert f[oldkey]==(old or bool(new and new['existingOrdinaryClearanceBoundProved']))
   if cursor+i not in affected:assert f['completeOriginalBoundProved'] and f['completeActualRenderedBoundProved'],'Ordinary whole-facet clearance fails outside verified exposed wall role'
  cursor+=len(meshes[uid])
 wanted=[c['component'] for c in role['allNamedOriginalVisualComponents']];faces=[i for k in wanted for i in graph['components'][k]['globalOriginalFaces']];projection=shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in tri[faces]])
 neighbours=read(PHYSICAL/'neighbour-inputs.json.gz');forms={}
 for path,sha in neighbours['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;forms.update({f['uid']:f for f in read(ROOT/path)['buildings']})
 foreign=[]
 for r in neighbours['rows']:
  f=r['building'];assert forms[f['uid']]==f
  if f['uid'] in UIDS:continue
  shape=shapely.Polygon(f['rings'][0],f['rings'][1:]);assert shape.is_valid and shape.disjoint(projection) and not f.get('modelGeometry');foreign.append(dict(uid=f['uid'],completeCurrentFormSHA256=canonical(f),completeCurrentFootprintSHA256=digest(shape.wkb),strictProjectedDistanceM=float(shape.distance(projection))))
 bounds=[];catalogues={};manifest=read(MANIFEST)
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;catalogues[str(path.relative_to(ROOT))]=digest(path.read_bytes());refs.append(ref(path))
  for e in read(path)['models']:
   b=np.asarray(e['worldBounds']);assert b.shape==(2,3) and np.isfinite(b).all() and (b[1]>=b[0]).all();assert projection.disjoint(shapely.box(b[0,0],b[0,2],b[1,0],b[1,2])),'Current native whole bounds touch mounted detail; complete original triangle route required';bounds.append(dict(uid=e['uid'],sourceSHA256=e['sha256'],completeOriginalWorldBounds=b.tolist()))
 for k in wanted:
  c=graph['components'][k];part=tri[c['globalOriginalFaces']]
  for uid in UIDS:
   if uid==c['actorUID']:continue
   other=meshes[uid];assert all(np.any(f.max(axis=0)<other.min(axis=(0,1))) or np.any(f.min(axis=0)>other.max(axis=(0,1))) for f in part),'Visual detail touches another owned actor'
 scope=dict(completeCurrentActorScope=True,currentFormsCount=len(neighbours['rows']),currentForeignForms=foreign,currentOwnedUIDs=UIDS,currentTileHashes=neighbours['inputHashes'],allCurrentNativeWholeBoundsSHA256=canonical(bounds),allCurrentNativeWholeBoundsCount=len(bounds),allCurrentNativeCatalogueHashes=catalogues,manifestSHA256=current_sha)
 binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeActualRenderedWorldSHA256=digest(world.tobytes()),completeCurrentDrawnGroundSHA256=digest(ground.tobytes()),completeContinuousContextsSHA256=canonical(contexts),completeRootedOriginalGraphSHA256=canonical(graph),frozenProviderRoleSHA256=canonical(role),actualProviderRootAndStreamsSHA256=canonical(streams),completeCurrentPhysicalSHA256=digest((PHYSICAL/'result.json').read_bytes()),completeCurrentForeignScopeSHA256=canonical(scope),currentManifestSHA256=current_sha,wholeOriginalAndRenderedClearanceReceiptSHA256=digest((CLEARANCE/'result.json').read_bytes()),currentRegionalRebindReceiptSHA256=digest((REBIND/'result.json').read_bytes()))
 visual=mounted(tri,contexts,graph,ground,world,expected_role=role,expected_binding=binding,current_binding=binding);assert visual['allComponentsAccounted'] and not visual['visualGroundRootCredit'] and not visual['visualStructuralBridgeCredit']
 foundation=read(PHYSICAL/'foundation.json');assert len(foundation['rows'])==2
 for r in foundation['rows']:assert r['strictFoundationAccepted'] and r['foundation']['completeTerrainTriangles']==r['foundation']['triangles']==len(meshes[r['uid']]) and r['foundation']['fullyBuriedTriangles']==r['foundation']['fullyBuriedUpwardTriangles']==0
 checks=read(PHYSICAL/'neighbour-checks.json');assert len(checks['rows'])==len(neighbours['rows'])==20 and not any(r['reasons'] for r in checks['rows']);native=read(PHYSICAL/'native-neighbour-checks.json');assert {r['uid'] for r in native['rows']}=={'landsd/9698:0'} and all(r['passed'] for r in native['rows']) and not(set(native['blocked'])-set(native['resolved']))
 validation=read(PHYSICAL/'validation.json');assert validation['checksPassed']==validation['loaderAccepted']==2 and not validation['exceptions'];metrics=read(PHYSICAL/'metrics.json');assert len(metrics['rows'])==2
 spec=importlib.util.spec_from_file_location('glorious_peak_policy',HERE/'acceptance-policy.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy);decisions=[];remaining=[]
 for m in metrics['rows']:
  uid=m['uid'];assert m['sourcePreserved'] and not m['missingTerrain'] and m['maxSamplerDelta']<=.004;identity=next(i for i in identities if i['uid']==uid);numeric=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=m['sourceSHA256'],identityProof=identity['proof']),m,metrics['profiles']['mobile']);raw=[r[len(uid)+1:] for r in physical['reasons'] if r.startswith(uid+':')];eligible={'ground-contact-unresolved','sampled-ground-gap-below-model-bottom'} if uid==UIDS[0] else {'terrain-intersects-source-over-0.5m'};allreasons=set(numeric+raw);remaining.extend(uid+':'+r for r in sorted(allreasons-eligible));decisions.append(dict(uid=uid,freshNumericReasons=numeric,rawPhysicalReasons=raw,sourceBoundResolvedReasons=sorted(allreasons&eligible)))
 remaining.extend(r for r in physical['reasons'] if not any(r.startswith(uid+':') for uid in UIDS));assert not remaining,remaining
 for doc in [PHYSICAL,SUPPORT,ORDINARY,PROVIDER,REBIND,CLEARANCE]:refs.extend(receipt(doc)['evidenceRefs']+[ref(doc/'result.json')])
 refs.extend([ref(p) for p in [Path(__file__),GEOMETRY,MANIFEST,REBIND/'historical-manifest.json',PROVIDER/'expected-role.json',PROVIDER/'original-source-provenance.json',SUPPORT/'diagnostic.json.gz',CLEARANCE/'diagnostic.json.gz',HERE/'glorious_peak_original_mounted_detail_roles_v2_20261010.py',HERE/'test_glorious_peak_original_mounted_detail_roles_v3_20261010.py',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'test_exact_original_paired_finite_clearance_20261010.py',HERE/'exact_original_face_conservative_clearance_v4_20261010.py',HERE/'test_exact_original_face_conservative_clearance_v4_20261010.py',HERE/'exact_original_closed_projection_intersection_20261010.py',HERE/'test_exact_original_closed_projection_intersection_20261010.py']]);refs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path'])
 for r in refs:archived_or_current(r)
 assert digest(MANIFEST.read_bytes())==current_sha
 return normalized(dict(uids=UIDS,manifestSHA256=current_sha,completeOriginalFaces=18944,completeOriginalComponents=365,completeStructuralSupportGraph=graph,completeVerifiedMountedVisualRoles=visual,completeOriginalGradeSupportGraphReplayed=True,completeCurrentRenderedGradeInterfaces=actual_grade,sourceBoundExposedWallFaces=sorted(affected),wholeOriginalAndActualRenderedFiniteClearance=ref(CLEARANCE/'diagnostic.json.gz'),rawNegativeFiniteContextsPreserved=True,completeCurrentIdentities=identities,completeCurrentForeignScope=scope,sourceDecisions=decisions,unresolvedIndependentPhysicalReasons=remaining,independentPhysicalChecksPassed=True,currentNeighbourFormsAccounted=20,currentRetainedNativeUIDs=['landsd/9698:0'],sourceGeometryChanges=0,installationApproved=False,publication=False,historicalManifestAlias=dict(originalPath=str(MANIFEST.relative_to(ROOT)),sha256=rebinding['oldManifestSHA256'],archive=ref(REBIND/'historical-manifest.json')),evidenceRefs=refs))
def main():
 assert not DOC.exists();claim=reservations.claim('glorious-peak-current-mounted-role-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  typed=recheck();save(DOC/'typed-role.json.gz',typed);spec=importlib.util.spec_from_file_location('glorious_peak_current_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-current-original-glorious-peak-grade-support-and-mounted-visual-roles-v2',[ROOT/r['path'] for r in typed['evidenceRefs']],dict(uids=UIDS,manifestSHA256=typed['manifestSHA256'],completeOriginalFaces=18944,completeOriginalComponents=365,independentPhysicalChecksPassed=True,typedRole=ref(DOC/'typed-role.json.gz'),unresolvedIndependentPhysicalReasons=[],installationApproved=False));print(dict(independentPhysicalChecksPassed=True,completeOriginalFaces=18944,sourceGeometryChanges=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
