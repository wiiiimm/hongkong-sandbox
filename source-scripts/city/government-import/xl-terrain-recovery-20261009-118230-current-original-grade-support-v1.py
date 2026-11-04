"""Current source-bound exact wall-grade roots and complete unchanged assembly.

Preserves all original global-bottom failures and every unresolved component.
No installation credit or geometry edits; support result may remain negative.
"""
import importlib.util,json,uuid,collections
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_exposed_wall_grade_root_graph_20261009 import verify,canonical
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261009-118230-current-original-grade-support-v1';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261009-118230-original-world-current-support-v1'
SOURCE_CONTACTS=BASE/'government-xl-two-harbourfront-complete-original-roof-paths-20261009'
CURB=BASE/'xl-terrain-recovery-20261009-118230-current-annular-curb-role-v1'
spec=importlib.util.spec_from_file_location('current_harbourfront_curb',HERE/'xl-terrain-recovery-20261009-118230-current-annular-curb-role-v1.py');curb=importlib.util.module_from_spec(spec);spec.loader.exec_module(curb)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def complete_components(tri,uid):
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
 return [dict(actorUID=uid,globalOriginalFaces=faces,bounds=[tri[faces].min(axis=(0,1)).tolist(),tri[faces].max(axis=(0,1)).tolist()]) for faces in sorted(groups.values(),key=min)]
def recheck():
 visual=curb.recheck();curb_receipt=curb.receipt(CURB);recorded_visual=read(CURB/'typed-role.json.gz');assert visual==recorded_visual
 receipt=curb.receipt(GRAPH);graph=read(GRAPH/'diagnostic.json.gz');cap_receipt=curb.receipt(SOURCE_CONTACTS)
 physical=curb.PHYSICAL;row=read(physical/'selection.json.gz')['rows'][0];raw=(ROOT/row['candidate']['path']).read_bytes();tri=decode_original_world_triangles(raw);geom=read(curb.GEOMETRY);g=geom['rows'][0];p=np.asarray(g['position'],float).reshape(-1,3);idx=np.asarray(g['index'],dtype=np.uint32).reshape(-1,3);world=p[idx]
 assert digest(raw)==curb.SOURCE and world.shape==tri.shape and np.max(np.abs(world-tri))<=1e-9
 assert digest(tri.tobytes())==graph['binding']['completeOriginalWorldTrianglesSHA256'] and graph['actors'][0]['originalWorldTrianglesSHA256']==digest(tri.tobytes())
 actual_components=complete_components(tri,curb.UID);assert actual_components==graph['components'] and len(actual_components)==446
 original_positions=np.empty_like(p);assigned={}
 for vertices,face in zip(idx,tri):
  for v,point in zip(vertices,face):
   v=int(v)
   if v in assigned:assert np.array_equal(assigned[v],point)
   else:assigned[v]=point;original_positions[v]=point
 assert set(assigned)==set(range(len(p))) and np.array_equal(original_positions[idx],tri)
 indexed=[dict(uid=curb.UID,sourceSHA256=curb.SOURCE,position=original_positions.reshape(-1).tolist(),index=idx.reshape(-1).tolist())]
 assert canonical(indexed)==graph['binding']['originalIndexedSourcesSHA256']
 ground=np.unique(np.asarray(g['drawnGroundGeometry'],float).reshape(-1,9),axis=0).reshape(-1,3,3);assert digest(ground.tobytes())==graph['binding']['currentDrawnGroundSHA256']
 ctx=read(curb.CONTEXT);source_graph=read(SOURCE_CONTACTS/'diagnostic.json.gz');assert source_graph['sourceSHA256']==curb.SOURCE and source_graph['decodedWorldTrianglesSHA256']==digest(tri.tobytes())
 contacts=[r['originalFaces'] for r in source_graph['exactCylinderInterfaces'] if r['dimension']>0]
 visual_components=[k for k,c in enumerate(actual_components) if c['globalOriginalFaces']==curb.PART];assert len(visual_components)==1
 neighbours=read(physical/'neighbour-inputs.json.gz');wall_projection=shapely.union_all([shapely.MultiPoint(face[:,[0,2]]).convex_hull for face in tri[ctx['affectedWallFaces']]])
 foreign=[]
 for nr in neighbours['rows']:
  f=nr['building']
  if f['uid']==curb.UID:continue
  assert not nr['existingNative'] and not f.get('modelGeometry');shape=shapely.Polygon(f['rings'][0],f['rings'][1:]);assert shape.is_valid and shape.disjoint(wall_projection)
  foreign.append(dict(uid=f['uid'],fullCurrentFormSHA256=canonical(f),fullCurrentFootprintSHA256=digest(shape.wkb),strictDistanceFromAllCreditedWallsM=float(shape.distance(wall_projection))))
 native_count=0;native_mesh_separation=[];native_refs=[]
 for url in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues']:
  catalogue=ROOT/'3d-viewer'/url
  for e in read(catalogue)['models']:
   b=np.asarray(e['worldBounds'],float);assert b.shape==(2,3) and np.isfinite(b).all() and (b[1]>=b[0]).all()
   if not wall_projection.disjoint(shapely.box(b[0,0],b[0,2],b[1,0],b[1,2])):
    native_asset=catalogue.parent/e['asset'];native_raw=native_asset.read_bytes();assert digest(native_raw)==e['sha256'];native_tri=decode_original_world_triangles(native_raw);assert len(native_tri)==e['triangles']
    measured=np.asarray([native_tri.min(axis=(0,1)),native_tri.max(axis=(0,1))]);assert np.max(np.abs(measured-b))<.002
    native_projection=shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in native_tri]);assert wall_projection.disjoint(native_projection),'Actual original native/source walls touch'
    native_mesh_separation.append(dict(uid=e['uid'],sourceSHA256=e['sha256'],completeOriginalFaces=len(native_tri),completeDecodedWorldTrianglesSHA256=digest(native_tri.tobytes()),completeOriginalProjectionIncludingVerticalCollapsedSHA256=digest(native_projection.wkb),strictDistanceFromCreditedWallsM=float(wall_projection.distance(native_projection)),originalWholeBoundsOverlapPreserved=True,projectionNoPaddingNoTolerance=True))
    native_refs.extend([ref(catalogue),ref(native_asset)])
   native_count+=1
 binding=dict(graph['binding'],completeCurrentFacetContextsSHA256=canonical(ctx['faces']),exactOriginalContactListSHA256=canonical(contacts),visualOnlyComponentsSHA256=canonical(visual_components),currentCurbRoleReceiptSHA256=digest((CURB/'result.json').read_bytes()),currentFullPhysicalSHA256=digest((physical/'result.json').read_bytes()),currentNativeWholeBoundsScopeSHA256=visual['binding']['allNativeOriginalBoundsSHA256'],currentForeignCreditedWallScopeSHA256=canonical(foreign))
 typed=verify(tri,graph['actors'],actual_components,graph['contactWitnesses'],indexed,ground,ctx['faces'],contacts,visual_components,expected_binding=binding,current_binding=binding)
 # Every credited source wall has the same real grade interface in the
 # rendered world, independently of the small source/runtime roundoff.
 grade_faces=sorted(set(r['sourceFace'] for r in typed['exactCurrentUpperGradeInterfaces']));rendered_interfaces=exact_upper_ground_interfaces(world,grade_faces,ground)
 assert set(r['sourceFace'] for r in rendered_interfaces)==set(grade_faces),'Original grade anchor absent from actual rendered world'
 refs=visual['evidenceRefs']+graph['evidenceRefs']+native_refs+[ref(p) for p in [Path(__file__),GRAPH/'result.json',GRAPH/'diagnostic.json.gz',CURB/'result.json',CURB/'typed-role.json.gz',SOURCE_CONTACTS/'result.json',SOURCE_CONTACTS/'diagnostic.json.gz',HERE/'original_exposed_wall_grade_root_graph_20261009.py',HERE/'test_original_exposed_wall_grade_root_graph_20261009.py']]
 typed.update(uid=curb.UID,sourceSHA256=curb.SOURCE,binding=binding,completeOriginalComponentsPartitionRecomputed=True,completeSourceToRenderedFaceIndexCorrespondenceVerified=True,currentRenderedWorldSHA256=digest(world.tobytes()),maximumSourceRenderedRoundoffM=float(np.max(np.abs(world-tri))),actualRenderedWallGradeInterfaces=rendered_interfaces,completeCurrentForeignWallsScope=foreign,allCurrentNativeOriginalWholeBoundsChecked=native_count,completeCurrentNativeMeshSeparation=native_mesh_separation,rawCurrentPhysicalReasons=read(physical/'result.json')['reasons'],sourceCurrentWholeFoundationAndNeighboursPassed=True,evidenceRefs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path']))
 return typed
def main():
 assert not DOC.exists();claim=reservations.claim('harbourfront-original-grade-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=json.loads(json.dumps(claim['reservation'],default=str))
 try:
  typed=recheck();save(DOC/'typed-support.json.gz',typed)
  spec=importlib.util.spec_from_file_location('harbourfront_grade_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.freeze(BATCH,'current-source-specific-exact-wall-upper-grade-root-graph-v1',[ROOT/r['path'] for r in typed['evidenceRefs']],dict(uids=[curb.UID],sourceSHA256=curb.SOURCE,supportInterfaceAccepted=typed['supportInterfaceAccepted'],ordinaryGroundRoots=typed['ordinaryGroundRootComponents'],exactWallGradeRoots=typed['exactExposedWallGradeRootComponents'],resolvedOriginalComponents=typed['resolvedOriginalComponents'],unresolvedOriginalComponents=typed['unresolvedOriginalComponents'],visualOnlyComponents=typed['visualOnlyComponents'],visualOnlyRootOrBridgeCredit=False,fullAcceptance=False,installationApproved=False,nextStep='Resolve every remaining original component with independently proved source roles/attachments, then full staged/live browser and guarded publication.'))
  print(json.dumps(dict(roots=typed['allIndependentGroundRoots'],resolved=len(typed['resolvedOriginalComponents']),unresolved=typed['unresolvedOriginalComponents'],supportInterfaceAccepted=typed['supportInterfaceAccepted'],fullAcceptance=False)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
