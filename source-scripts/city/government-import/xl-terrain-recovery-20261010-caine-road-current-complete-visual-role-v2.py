"""Complete fresh current two-source structural + nonstructural visual replay.

Only exact pinned authored visual details replace their own root demands.
Every ordinary root/contact, provider/native identity, foreign actor, source
facet/foundation and actual runtime gate remains independent and unchanged.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from original_ordinary_ground_root_graph_20261009 import verify as structural
from exact_original_georef_cell_identity_20261009 import verify_files as identity_verify
from caine_road_original_named_projecting_details_v1_20261010 import verify as visual,canonical,WORLD,SOURCES,DETAILS
BASE=ROOT/'docs/astra-city/government-import'
PHYS=BASE/'government-xl-terrain-recovery-unnamed-268032-nested-original-pair-current-physical-v5-20261010'
GRAPH=BASE/'xl-terrain-recovery-20261010-unnamed-268032-v5-complete-original-support-v1'
FINITE=BASE/'xl-terrain-recovery-20261010-unnamed-268032-v5-complete-paired-finite-clearance-v1'
PROVIDER=BASE/'xl-terrain-recovery-20261010-caine-road-provider-visual-roles-v1'
RETAINED=BASE/'xl-terrain-recovery-20261010-caine-road-complete-retained-native-v1'
BATCH='government-xl-terrain-recovery-caine-road-current-complete-visual-role-v2-20261010';DOC=BASE/BATCH
MANIFEST='44c9e80ec3999285616bb12a3fdfbe142a15855db7aa7c3216bffab3500f991a'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def receipt(folder):
 r=read(folder/'result.json')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 assert len({x['path'] for x in r['evidenceRefs']})==len(r['evidenceRefs'])
 for x in r['evidenceRefs']:assert ref(ROOT/x['path'])==x,'Frozen physical/finite/provider dependency changed: '+x['path']
 return r

def recheck():
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST
 receipts=[receipt(p) for p in [PHYS,GRAPH,FINITE,PROVIDER,RETAINED]];physics=receipts[0]
 expected_raw=['landsd/268032:0:ground-contact-unresolved','landsd/268032:0:sampled-ground-gap-below-model-bottom'];assert physics['reasons']==expected_raw
 selected=read(PHYS/'selection.json.gz');rows=selected['rows'];assert selected['manifestSHA256']==MANIFEST and {r['uid']:r['sourceSHA256'] for r in rows}==SOURCES
 contexts=read(HERE/'local'/PHYS.name/'frozen-inputs/context.json.gz')['rows'];geometry=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';runtime=read(geometry);assert [r['uid'] for r in runtime['rows']]==list(SOURCES)
 for p,h in runtime['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,'Current drawn runtime input changed: '+p
 candidates=read(PHYS/'terrain-candidates.json');assert len(candidates)==1 and candidates[0]['uids']==list(SOURCES)
 candidate=candidates[0];assert ref(ROOT/candidate['path'])=={k:candidate[k] for k in ('path','sha256')}
 parentpath=ROOT/'3d-viewer'/candidate['replaces']['url'];assert ref(parentpath)['sha256']==candidate['replaces']['sha256'] and candidate['replaces']['url']=='city/data/terrain-central-no1-literal-villa-parent-current.json'
 parent=read(parentpath);wrapper=read(ROOT/candidate['path']);assert wrapper['elev']==parent['elev'] and wrapper.get('renderedElev')==parent.get('renderedElev') and len(parent['patches'])==9 and len(wrapper['patches'])==10
 for old,new in zip(parent['patches'],wrapper['patches'][:9]):
  for k in ['elev','renderedElev']:assert old.get(k)==new.get(k)
  for k in ['position','index']:assert old.get('nativeMesh',{}).get(k)==new.get('nativeMesh',{}).get(k)
 child=wrapper['patches'][-1];assert child['meta']['targetUids']==list(SOURCES)
 restoration=read(PHYS/'complete-disjoint-foreign-parent-preservation.json');assert restoration['uids']==['landsd/98932:0','landsd/98933:0'] and restoration['strictDisjointness'] and restoration['completeLiteralFootprintCovered'] and restoration['outerCoverCoordinatesFloat32Exact'] and restoration['coverConstructionIsNotToleranceCredit'] and restoration['terrainProposalGeometryChanged'] and restoration['sourceGeometryChanges']==0
 final=module('caine_current_forms','xl-final-script-pass.py');forms=final.load_forms(candidate['bounds']);neighbours=read(PHYS/'neighbour-inputs.json.gz');assert [r['building'] for r in neighbours['rows']]==[b for b,_,_ in forms] and len(forms)==18 and neighbours['candidateIds']==sorted(SOURCES)
 formhashes={str((ROOT/'3d-viewer'/u).relative_to(ROOT)):digest((ROOT/'3d-viewer'/u).read_bytes()) for _,_,u in forms};assert formhashes==neighbours['inputHashes']
 for uid,form in restoration['completeForeignForms'].items():assert next(b for b,_,_ in forms if b['uid']==uid)==form
 checks=read(PHYS/'neighbour-checks.json');assert len(checks['rows'])==18 and not any(r['reasons'] for r in checks['rows'])
 native=read(PHYS/'native-neighbour-checks.json');assert not set(native['blocked'])-set(native['resolved'])
 for p,h in native.get('inputHashes',native.get('hashes',{})).items():assert digest((ROOT/p).read_bytes())==h
 foundation=read(PHYS/'foundation.json')['rows'];validation=read(PHYS/'validation.json');metrics=read(PHYS/'metrics.json');assert validation['checksPassed']==validation['loaderAccepted']==2 and validation['exceptions']==0
 g=read(GRAPH/'diagnostic.json.gz');finite=read(FINITE/'diagnostic.json.gz');roles=read(PROVIDER/'provider-role.json.gz');provider=read(PROVIDER/'source-provider-provenance.json')
 pieces=[];literal=[];groundpieces=[];indexed=[];actors=[];identities=[];assets=[];cursor=0
 for row in rows:
  uid=row['uid'];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SOURCES[uid];assets.append(asset);tri=decode_original_world_triangles(raw);rt=next(r for r in runtime['rows'] if r['uid']==uid);pos=np.asarray(rt['position'],float).reshape(-1,3);idx=np.asarray(rt['index'],np.uint32).reshape(-1,3);world=pos[idx];ground=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3);assert np.array_equal(tri,world)
  f=next(r for r in finite['rows'] if r['uid']==uid);assert f['completeOriginalWorldSHA256']==digest(tri.tobytes()) and f['completeActualRenderedWorldSHA256']==digest(world.tobytes()) and f['completeGroundSHA256']==digest(ground.tobytes())
  stream=source_stream_binding(raw);assert provider['completeOriginalProviderRootAndStreams'][uid]==stream
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
  identity=identity_verify(row,next(c for c in contexts if c['uid']==uid),HERE/'local'/PHYS.name/'current-identity-recheck'/uid.split('/')[1]);assert identity['passed'] and identity==next(r for r in read(PHYS/'owned-source-identity.json')['rows'] if r['uid']==uid);identities.append(identity)
  assigned={};originalpos=np.empty_like(pos)
  for ids,face in zip(idx,tri):
   for i,v in zip(ids,face):
    i=int(i)
    if i in assigned:assert np.array_equal(assigned[i],v)
    else:assigned[i]=v;originalpos[i]=v
  assert set(assigned)==set(range(len(pos))) and np.array_equal(originalpos[idx],tri)
  actors.append(dict(uid=uid,sourceSHA256=SOURCES[uid],originalStreamBindingSHA256=canonical(stream),globalFaceRange=[cursor,cursor+len(tri)],completeOriginalFaceCount=len(tri),originalWorldTrianglesSHA256=digest(tri.tobytes())));indexed.append(dict(uid=uid,sourceSHA256=SOURCES[uid],position=originalpos.reshape(-1).tolist(),index=idx.reshape(-1).tolist()));pieces.append(tri);literal.append(world);groundpieces.append(ground);cursor+=len(tri)
  ff=next(r for r in foundation if r['uid']==uid);q=ff['foundation'];assert ff['strictFoundationAccepted'] is True and q['completeTerrainTriangles']==q['triangles']==len(tri) and q['fullyBuriedTriangles']==q['fullyBuriedUpwardTriangles']==0
  m=next(r for r in metrics['rows'] if r['uid']==uid);assert m['sourceSHA256']==SOURCES[uid] and m['sourcePreserved'] is True and m['missingTerrain']==0 and m['maxSamplerDelta']<=.004
  if uid=='landsd/101781:0':assert m['minSurfaceGap']>=-.5 and m['minLowGap']<=.1 and m['maxLowGap']<=1
 tri=np.concatenate(pieces);world=np.concatenate(literal);ground=np.unique(np.concatenate(groundpieces).reshape(-1,9),axis=0).reshape(-1,3,3);assert digest(tri.tobytes())==digest(world.tobytes())==WORLD and actors==g['actors']
 binding=dict(completeOriginalWorldTrianglesSHA256=WORLD,currentDrawnGroundSHA256=digest(ground.tobytes()),groundInterfacesInputSHA256=ref(geometry)['sha256'],supportScope='complete-current-drawn-ground-only',originalIndexedSourcesSHA256=canonical(indexed));assert binding==g['binding']
 graph=json.loads(json.dumps(structural(tri,actors,g['components'],g['contactWitnesses'],indexed,ground,expected_binding=binding,current_binding=binding)))
 for k,v in graph.items():assert g[k]==v,'Complete current ordinary graph differs: '+k
 vb=dict(completeOriginalWorldSHA256=WORLD,completeLiteralWorldSHA256=WORLD,completeGraphSHA256=canonical(g),completeFiniteContextsSHA256=canonical(finite),providerRolesSHA256=canonical(roles));visualproof=visual(tri,world,g,finite,roles,expected_binding=vb,current_binding=vb);assert visualproof['allComponentsAccounted'] and visualproof['visualDetailsSupplyNoStructuralRootsOrBridges']
 detailids=sorted(i for ids in DETAILS.values() for i in ids);detail=tri[detailids];projections=[]
 for t in detail:
  polygon=shapely.Polygon(t[:,[0,2]]);projections.append(polygon if polygon.area else shapely.LineString(t[:,[0,2]]))
 closed=shapely.union_all(projections);foreign=[]
 for form,_,_ in forms:
  if form['uid'] in SOURCES:continue
  assert not form.get('modelGeometry'),'Embedded foreign geometry requires full actual mesh'
  footprint=shapely.Polygon(form['rings'][0],form['rings'][1:]);assert not closed.intersects(footprint),'Actual current foreign projection touches visual details: '+form['uid'];foreign.append(dict(uid=form['uid'],completeCurrentFormSHA256=canonical(form),strictClosedProjectionDisjoint=True,distanceM=closed.distance(footprint)))
 native_bounds=[];catalogue_refs=[];installed=set()
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;catalogue_refs.append(ref(p))
  for entry in read(p)['models']:
   assert entry['uid'] not in installed;installed.add(entry['uid']);bounds=np.asarray(entry['worldBounds'],float);assert bounds.shape==(2,3) and np.isfinite(bounds).all() and np.all(bounds[1]>=bounds[0])
   assert all(np.any(bounds[0]>face.max(axis=0)) or np.any(bounds[1]<face.min(axis=0)) for face in detail),'Current whole native bounds touch visual detail: '+entry['uid']
   native_bounds.append(dict(uid=entry['uid'],sourceSHA256=entry['sha256'],catalogueSHA256=ref(p)['sha256'],completeOriginalWorldBounds=bounds.tolist()))
 assert not installed&set(SOURCES)
 retained_scope=read(RETAINED/'retained-scope.json');retained_checks=read(RETAINED/'native-neighbour-checks.json');retained_inputs=read(RETAINED/'neighbour-inputs.json.gz');dependency_bindings=read(RETAINED/'current-native-dependency-bindings.json')
 expected_retained=sorted({u for c in parent['patches'] for u in c['meta']['targetUids']}|{r['building']['uid'] for r in neighbours['rows'] if r['existingNative']})
 assert retained_scope['retainedNativeUids']==expected_retained and retained_scope['currentManifest']==start and retained_scope['parent']==ref(parentpath) and retained_scope['physicalResult']==ref(PHYS/'result.json') and retained_scope['allNineChildrenPinned'] is True
 assert receipts[-1]['allCurrentRetainedNativeChecksPassed'] is True and receipts[-1]['rawFailedNativeUids']==[] and receipts[-1]['retainedNativeUids']==expected_retained
 assert sorted(retained_checks['blocked'])==sorted(retained_checks['resolved'])==expected_retained and sorted(r['uid'] for r in retained_checks['rows'])==expected_retained and all(r['passed'] is True for r in retained_checks['rows'])
 for path,sha in retained_checks['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha,'Current complete retained native input changed: '+path
 current_native={e['uid']:e for url in read(manifest)['officialModelCatalogues'] for e in read(ROOT/'3d-viewer'/url)['models']};expected_forms={r['building']['uid']:r['building'] for r in neighbours['rows']};expected_hashes=dict(neighbours['inputHashes'])
 for uid in expected_retained:
  assert uid in current_native;lo,hi=current_native[uid]['worldBounds']
  for form,_,url in final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]):expected_forms[form['uid']]=form;expected_hashes[str((ROOT/'3d-viewer'/url).relative_to(ROOT))]=digest((ROOT/'3d-viewer'/url).read_bytes())
 assert retained_scope['originalScopeForms']==len(expected_forms)==76 and retained_inputs['rows']==[dict(building=f,existingNative=u in current_native,patchIndexes=[0]) for u,f in sorted(expected_forms.items())] and retained_inputs['inputHashes']==expected_hashes
 expected_patches=json.loads(json.dumps(neighbours['patches']));expected_patches[0]['replaces']['retainedUids']=expected_retained
 assert retained_inputs['patches']==expected_patches and retained_inputs['candidateIds']==sorted(SOURCES)
 assert dependency_bindings['currentManifest']==start
 for record in dependency_bindings['rows']:
  owner=record['ownerUID'];support=record['supportUID'];assert owner=='landsd/263590:0' and support=='landsd/232907:0' and record['originalRecordedDependency']==dict(uid=support,state='candidate') and record['currentSupportIsUniquelyInstalled'] is True and current_native[owner]['supportDependencies']==[record['originalRecordedDependency']]
  for field,uid in [('owner',owner),('support',support)]:
   e=current_native[uid];cat=next(ROOT/'3d-viewer'/url for url in read(manifest)['officialModelCatalogues'] if any(x['uid']==uid for x in read(ROOT/'3d-viewer'/url)['models']));asset=cat.parent/e['asset'];assert record[field]==dict(sourceSHA256=e['sha256'],buildingCSUID=e['buildingCSUID'],modelId=e['modelId'],catalogue=ref(cat),originalSource=ref(asset))
 assert len(dependency_bindings['rows'])==1
 assert ref(manifest)==start
 dependencies=[Path(__file__),geometry,parentpath,manifest,ROOT/candidate['path'],HERE/'caine_road_original_named_projecting_details_v1_20261010.py',HERE/'test_caine_road_original_named_projecting_details_v1_actual_20261010.py',HERE/'mei_yat_original_named_visual_mounts_v1_20261010.py',HERE/'exact_shell_context_accelerated_20261009.py',HERE/'original_local_perpendicular_boundary_diagnostic_20261010.py',HERE/'exact_original_perpendicular_edge_facet_band_20261010.py',HERE/'test_exact_original_perpendicular_edge_facet_band_20261010.py',HERE/'original_ordinary_ground_root_graph_20261009.py',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl_source_stream_binding_20261009.py',*assets]
 refs=[ref(p) for p in dependencies]+catalogue_refs
 for folder in [PHYS,GRAPH,FINITE,PROVIDER,RETAINED]:refs.extend(ref(p) for p in sorted(folder.iterdir()) if p.is_file())
 refs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path'])
 return dict(contract='complete-current-caine-road-original-structural-plus-two-named-visual-roles-v2',uids=sorted(SOURCES),currentManifest=start,sourceSHA256s=SOURCES,completeOriginalFaces=10947,completeOriginalComponents=204,completeCurrentNeighbourForms=18,completeCurrentSourceIdentities=identities,fullOrdinaryOriginalAndRenderedClearanceProved=True,completeStrictStructuralGraph=graph,namedVisualMountProof=visualproof,allComponentsAccounted=True,strictWholeSourceFoundationsPreserved=True,allCurrentForeignVisualScopes=foreign,allCurrentOriginalNativeWholeBounds=native_bounds,allForeignCurrentActorsRetained=True,completeCurrentRetainedNativeScope=retained_scope,allCurrentRetainedNativeChecksPassed=True,completeCurrentRetainedNativeChecks=retained_checks,currentRecordedNativeDependencyBindings=dependency_bindings,rawPhysicalReasonsPreserved=expected_raw,replacedDiagnosticReasonsOnly=expected_raw,currentTypedPhysicalAccepted=True,reasons=[],terrainProposalGeometryChanged=True,terrainProposal=candidates,parentAllNineOriginalChildrenAndGridUnchanged=True,completeForeignDyadicParentPreservation=restoration,sourceGeometryChanges=0,aiGeometryModelling=False,visualStructuralCredit=False,publication=False,newlyInstalled=0,installationApproved=False,evidenceRefs=refs)
def main():
 assert not DOC.exists();r=recheck();save(DOC/'typed-role.json.gz',r);f=module('freeze_caine_current','xl-popcorn-source-investigations-checkpoints-20261009.py');f.freeze(BATCH,'complete-current-original-two-source-structural-and-pinned-visual-roles-v2',[ROOT/x['path'] for x in r['evidenceRefs']],dict(uids=sorted(SOURCES),currentTypedPhysicalAccepted=True,reasons=[],sourceGeometryChanges=0,terrainProposalGeometryChanged=True,completeOriginalFaces=10947,completeOriginalComponents=204,typedRole=ref(DOC/'typed-role.json.gz'),browserRequired=True,publication=False,newlyInstalled=0));print(json.dumps(dict(passed=True,faces=10947,parts=204,foreign=18)),flush=True)
if __name__=='__main__':main()
