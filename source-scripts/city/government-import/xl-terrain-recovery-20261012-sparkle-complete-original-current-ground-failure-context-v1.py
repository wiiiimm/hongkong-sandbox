"""UNEXECUTED complete original source/current terrain context, not a role rule.

Keep 230 ordinary failures, all 25 original body obligations and all 150 zeros.
No clipping, construction, source edits, contact searches or accepted roles.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter,defaultdict
import gzip,struct,importlib.util,json,subprocess,sys,time,uuid
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from exact_original_shared_edge_component_census_v2_20261011 import census
from sparkle_current_native_renderer_winding_20261011 import drawn_native_faces

BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261012-sparkle-complete-original-current-ground-failure-context-v1'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
FINITE=BASE/'xl-terrain-recovery-20261012-sparkle-complete-current-drawn-ground-finite-v1'
CENSUS=BASE/'xl-terrain-recovery-20261011-sparkle-tower-podium-original-contact-census-v2'
ATTR=BASE/'xl-terrain-recovery-20261011-sparkle-tower-podium-two-current-render-attribute-capture-v1'
NATIVE=BASE/'xl-terrain-recovery-20261011-sparkle-retained-market-two-current-render-ground-capture-v2'
UIDS=['landsd/242198:0','landsd/228000:0','landsd/113733:0','landsd/138091:0']
COUNTS=[12875,6806,15641,25224];CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
MODES=[('originalSource',None),('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedFloat32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedFloat32','completeExplicitBalancedFloat32WorldPosition')]
REUSE='xl-terrain-recovery-20261012-sparkle-authentic-retained-market-terrain-candidate-v4.py'
HELPERS=['exact_packed_world_geometry_20261009.py','exact_packed_world_bounds_v3_20261010.py',
 'exact_original_shared_edge_component_census_v2_20261011.py','sparkle_current_native_renderer_winding_20261011.py',
 'xl-popcorn-source-investigations-checkpoints-20261009.py']
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=digest(p.read_bytes()))
def verify(pin):
 p=ROOT/pin['path'];assert p.is_file()and ref(p)==pin;return p
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def source_gltf(raw,expected):
 data=gzip.decompress(raw);magic,version,total=struct.unpack_from('<III',data)
 assert magic==0x46546c67 and version==2 and total==len(data)
 size,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a
 doc=json.loads(data[20:20+size]);binary_size,binary_kind=struct.unpack_from('<II',data,20+size)
 assert binary_kind==0x004e4942 and 28+size+binary_size==len(data)
 rows=[];cursor=0
 def visit(i,parent,path):
  nonlocal cursor
  assert i not in path;node=doc['nodes'][i];assert not any(k in node for k in ['translation','rotation','scale'])
  local=np.asarray(node.get('matrix',np.eye(4).reshape(-1,order='F').tolist()),float).reshape(4,4,order='F')
  assert np.isfinite(local).all()and np.array_equal(local[3],[0.,0.,0.,1.]);transform=parent@local
  if 'mesh'in node:
   for pi,p in enumerate(doc['meshes'][node['mesh']]['primitives']):
    assert p.get('mode',4)==4 and 'indices'in p
    index=doc['accessors'][p['indices']];position=doc['accessors'][p['attributes']['POSITION']]
    assert index['count']%3==0;count=index['count']//3
    rows.append(dict(node=i,nodePath=path+[i],mesh=node['mesh'],primitive=pi,completeActorLocalFaceRange=[cursor,cursor+count],
     completeOriginalIndexAccessor=index,completeOriginalPOSITIONAccessor=position,originalPrimitive=p,
     originalProviderNode=node,providerParentTimesChildMatrixFloat64=transform.tolist(),
     existingProviderToViewerOffsetOnly=[-834500,0,816500],additionalAgentScaleOrYOffsetApplied=False))
    cursor+=count
  for child in node.get('children',[]):visit(child,transform,path+[i])
 for root in doc['scenes'][doc.get('scene',0)]['nodes']:visit(root,np.eye(4),[])
 assert cursor==expected
 return dict(completeOriginalGLTFDocument=doc,completePrimitiveRanges=rows,
  sourceUnitMetadataOnly=dict(asset=doc.get('asset'),extras=doc.get('extras')),
  sourceUnitsNotInferredFromBoundingBox=True,noSourceOriginElevationOrProviderMatrixChanged=True)
def edge_inventory(world,ids):
 edges=defaultdict(list)
 for fi in ids:
  for a,b in zip(world[fi],np.roll(world[fi],-1,axis=0)):edges[tuple(sorted((tuple(a),tuple(b))))].append(fi)
 return [dict(completeEdge=[list(v)for v in e],completeActorLocalFaces=faces,incidence=len(faces))for e,faces in sorted(edges.items())]
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
 refs=[ref(Path(__file__)),ref(HERE/REUSE),*[ref(HERE/p)for p in HELPERS]]
 assert ref(HERE/REUSE)['sha256']=='02182a7a60b21282c0c912587b3c8fd0fa29be7bc974b0c8d1124eb6e04d4b5a'
 reuse=module('sparkle_original_context_current_inputs',REUSE);manifest=ROOT/'3d-viewer/city/data/manifest.json'
 start,current,rebind=reuse.current_rebind(manifest,refs);assert start['sha256']==CURRENT
 for folder,job in [(FINITE,'8ea68d031e3c9ff45936804eb6440db7c2fcb4dd6630cf8876578f8522a57dc3'),
  (CENSUS,'37bc98c07be9da3f8ea4499d39ec048ee3d24784bc6263f73ec76ff9a31fd49d'),
  (ATTR,'80b48d4b97a689b19e34ace263ab907be1f5ebaa7b7a7be57dda9892d656487c'),
  (NATIVE,'4832a8e05527b49eca61ff04478d7ce4d9a3a8dcc315fdf1756171293ab144b9')]:reuse.completed(folder,job,refs)
 finite=read(FINITE/'diagnostic.json.gz');captured=read(FINITE/'actual-current-drawn-ground-union.json.gz')
 assert ref(FINITE/'diagnostic.json.gz')['sha256']=='abbb2799e8223ca5bc7c24c4720d058659aebaf62e0ef32a022d9b14f628f460'
 assert ref(FINITE/'actual-current-drawn-ground-union.json.gz')['sha256']=='8e0babf7e553d3ba4e07a0b8f1d01d8dabe7366f3d2c1cb63369fb756da8e9cb'
 assert finite['completeOwnedOriginalFaces']==19681 and finite['completeOriginalBodies']==25 and len(finite['rows'])==8
 source=read(CENSUS/'diagnostic.json.gz');attrs=read(ATTR/'actual-render-attributes.json.gz')['rows'];inputs=read(ATTR/'literal-source-inputs.json.gz')['rows']
 native_inputs=read(NATIVE/'native-render-inputs.json.gz')['rows'];native_attrs=read(NATIVE/'native-render-ground.json.gz')['rows']
 assert [r['uid']for r in inputs]==[r['uid']for r in attrs]==UIDS[:2]
 assert [r['uid']for r in native_inputs]==[r['uid']for r in native_attrs]==UIDS[2:]
 ground=np.asarray(captured['drawnGroundGeometry'],float).reshape(-1,3,3)
 assert ground.shape==(3865,3,3)and digest(ground.tobytes())==finite['completeCurrentDrawnUnionSHA256']
 bodies=source['bodies'];zeros=source['exactNonrenderingGlobalFacesRetainedUncredited'];assert len(bodies)==25 and len(zeros)==150
 worlds={};originals=[];source_records=[]
 for i,(uid,count)in enumerate(zip(UIDS,COUNTS)):
  if i<2:asset=ROOT/inputs[i]['path'];attribute=attrs[i]
  else:asset=ROOT/native_inputs[i-2]['sourceAsset']['path'];attribute=native_attrs[i-2]
  raw=asset.read_bytes();assert digest(raw)==attribute['sourceSHA256'];refs.append(ref(asset))
  original=decode_original_world_triangles(raw);assert original.shape==(count,3,3);originals.append(original)
  meta=source_gltf(raw,count);position=packed_world_bounds(raw)
  source_records.append(dict(uid=uid,sourceAsset=ref(asset),completeOriginalPOSITIONProof=position,**meta,
   rawEntry=inputs[i]['entry']if i<2 else native_inputs[i-2]['rawEntry'],
   actualRenderMeshMatricesAndAttributesVerbatim=attribute['actualRenderMeshes']))
  if i<2:
   idx=np.asarray(attribute['completeOriginalIndex'],int)
   for mode,key in MODES:
    world=original if key is None else np.asarray(attribute[key],float).reshape(-1,3)[idx].reshape(-1,3,3)
    saved=next(r for r in finite['rows']if r['uid']==uid and r['mode']==mode)
    assert world.shape==(count,3,3)and digest(world.tobytes())==saved['completeWorldSHA256'];worlds[uid,mode]=world
 pair=np.concatenate(originals[:2]);assert digest(pair.tobytes())==source['completeOriginalWorldSHA256']
 membership={f:b for b,body in enumerate(bodies)for f in body['globalOriginalFaces']}
 assert set(membership).isdisjoint(zeros)and set(membership)|set(zeros)==set(range(19681))
 layer_by_id={l['layerID']:l for l in captured['layers']};face_provenance={}
 assert len(layer_by_id)==557
 # Attribute/index matching is exact. Native identity is not guessed from
 # the repeated generic layer name. Grid/hydro lineage remains explicitly
 # unresolved beyond the complete captured layer and frozen input closure.
 native_locations=[]
 def visit_patch(data,pin,pointer):
  if 'nativeMesh'in data:
   _,w=drawn_native_faces(data['nativeMesh'])
   native_locations.append(dict(sourceFile=pin,jsonPointer=pointer,completePOSITIONFloat32SHA256=w['unchangedCompleteFloat32POSITIONSHA256'],
    completeRenderedIndexSHA256=w['renderedIndexSHA256'],coarseCells=data.get('coarseCells'),georef=data.get('meta',{}).get('georef'),
    targetUids=data.get('targetUids'),rawNativeMeshMetadata=data['nativeMesh'].get('meta'),nativeReapproval=False))
  for i,child in enumerate(data.get('patches',[])):visit_patch(child,pin,pointer+'/patches/'+str(i))
 for url in ['city/data/terrain.json']+[p['url']for p in current['terrainPatches']]:
  path=ROOT/'3d-viewer'/url;pin=ref(path);refs.append(pin);visit_patch(read(path),pin,'')
 for layer in captured['layers']:
  matches=[p for p in native_locations if p['completePOSITIONFloat32SHA256']==layer['completePOSITION']['sha256']and layer['completeIndex']is not None and p['completeRenderedIndexSHA256']==layer['completeIndex']['sha256']]
  for entry in layer['selectedFacets']:
   fi=entry['unionFacetID'];assert fi not in face_provenance
   face_provenance[fi]=dict(completeCapturedLayerID=layer['layerID'],originalSelectedDrawnFacetVerbatim=entry,
    exactNativePatchAttributeIndexMatchIDs=[native_locations.index(p)for p in matches],gridOrHydroSpecificPatchLineageNotClaimed=not matches)
 assert set(face_provenance)==set(range(3865))
 last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 failrows=[];bodyrows=[];source_fail_ids=None
 for mode,_ in MODES:
  p=next(r for r in finite['rows']if r['uid']==UIDS[1]and r['mode']==mode);ids=p['ordinaryUnprovedFaces']
  assert len(ids)==230 and p['uncoveredCurrentUnionFaces']==[]
  source_fail_ids=ids if source_fail_ids is None else source_fail_ids;assert ids==source_fail_ids
  failures=[p['allFaces'][i]for i in ids];assert Counter(r['orientation']for r in failures)=={'upward':201,'vertical':24,'downward':5}
  for proof in failures:
   fi=proof['actorLocalFaceID'];candidates=proof['rawCoarseProofVerbatim']['allProjectedBoundingCandidateOriginalGroundFacets']
   assert candidates and all(i in face_provenance for i in candidates)
   primitive=next(v for v in source_records[1]['completePrimitiveRanges']if v['completeActorLocalFaceRange'][0]<=fi<v['completeActorLocalFaceRange'][1])
   failrows.append(dict(uid=UIDS[1],mode=mode,actorLocalOriginalFace=fi,globalOriginalFace=12875+fi,originalBody=membership[12875+fi],
    originalPrimitiveIdentity=primitive,completeActualWorldFacet=worlds[UIDS[1],mode][fi].tolist(),fullFiniteProofVerbatim=proof,
    completeNominatedCurrentGroundFacetIDs=candidates,allActualGroundWitnessesRemainInsideVerbatimPairedProof=True,
    orientationIsNotArchitecturalRole=True,noRoleOrRootCredit=True));pulse()
  for body_id,body in enumerate(bodies):
   uid=body['actorUID'];saved=next(r for r in finite['rows']if r['uid']==uid and r['mode']==mode);faces=body['actorLocalFaces'];world=worlds[uid,mode]
   exact=census(world,faces);assert sorted(exact['exactNonrenderingOriginalFaces']+[f for part in exact['sharedEdgeConnectedComponents']for f in part])==faces
   bodyrows.append(dict(originalBody=body_id,uid=uid,mode=mode,completeOriginalGlobalFaceIDs=body['globalOriginalFaces'],
    completeActorLocalFaces=faces,wholeBodyWorldSHA256=digest(world[faces].tobytes()),completeActualArithmeticEdgeCensus=exact,
    completeAuthoredEdgeIncidence=edge_inventory(world,faces),completeWorldBounds=[world[faces].min((0,1)).tolist(),world[faces].max((0,1)).tolist()],
    ordinaryUnprovedFaces=[fi for fi in faces if not saved['allFaces'][fi]['existingOrdinaryClearanceBoundProved']],
    minimumCertifiedFiniteClearanceM=str(min(F(saved['allFaces'][fi]['exactCertifiedLowerClearanceM'])for fi in faces)),
    completeFiniteCoveredDoesNotProveGroundRoot=True,sourceFloorRoofFoundationFunctionNotAssigned=True,
    allZeroAndArithmeticCollapsedFacesRetainedUncredited=True,noRoleRootContactOrSupportCredit=True));pulse()
 assert len(failrows)==920 and len(bodyrows)==100
 assert set(r['originalBody']for r in failrows)=={19,20,22,23,24}
 for pin in refs:verify(pin)
 DOC.mkdir(parents=True);(DOC/'actual-current-manifest.json').write_bytes(manifest.read_bytes());save(DOC/'current-input-rebind.json',rebind)
 # All arrays stay complete. Axis framing is an image crop, never a mesh edit.
 # Annotation colours distinguish actors/failures; they are not imported
 # materials, architectural categorisation or proposed model colours.
 views=[('complete-pair-retained-terrain-plan',90,-90,None),('complete-pair-retained-terrain-oblique',25,-55,None),
  ('complete-pair-retained-terrain-side',0,-90,None)]
 for body_id in [19,20,22,23,24]:views.extend([(f'podium-original-body-{body_id}-plan',90,-90,body_id),(f'podium-original-body-{body_id}-oblique',24,-55,body_id)])
 images=[]
 for label,elevation,azimuth,body_id in views:
  pulse(True);fig=plt.figure(figsize=(22,12),dpi=100);ax=fig.add_subplot(111,projection='3d')
  if body_id is None:
   points=np.concatenate([a.reshape(-1,3)for a in originals]+[ground.reshape(-1,3)]);lo=points.min(0);hi=points.max(0);focus=pair[[12875+i for i in source_fail_ids]]
  else:
   focus=pair[bodies[body_id]['globalOriginalFaces']];lo=focus.min((0,1));hi=focus.max((0,1));pad=np.maximum((hi-lo)*.18,[3.,2.,3.]);lo=lo-pad;hi=hi+pad
  center=(lo+hi)/2
  def draw(a,color,alpha,lw):ax.add_collection3d(Poly3DCollection((a-center)[:,:,[0,2,1]],facecolors=color,edgecolors=color,alpha=alpha,linewidths=lw))
  draw(ground,'#608f55',.27,.04)
  for a,color in zip(originals,['#819ac1','#bc956e','#9aa1a8','#8e959c']):draw(a,color,.3,.03)
  draw(focus,'#cf2c33',.94,.3)
  display=(np.asarray([lo,hi])-center)[:,[0,2,1]];extent=display[1]-display[0]
  ax.set_xlim(display[:,0]);ax.set_ylim(display[:,1]);ax.set_zlim(display[:,2]);ax.set_box_aspect(extent);ax.view_init(elevation,azimuth)
  ax.set_xlabel('X relative to diagnostic centre X (m)');ax.set_ylabel('Z relative to diagnostic centre Z (m)');ax.set_zlabel('Y relative to diagnostic centre Y (m)')
  ax.set_title('Complete original Sparkle T/P + retained market originals + actual current terrain\nRed: exact failed original faces/body; annotation colours only; no roof/floor/foundation/function or root classification\nAbsolute HKPD Y = plotted vertical + diagnostic centre Y ('+repr(float(center[1]))+' m)')
  path=DOC/(label+'-2200x1200.png');fig.tight_layout();fig.savefig(path);plt.close(fig);images.append(dict(image=ref(path),originalBody=body_id,
   completeOriginalActors=UIDS,completeOriginalBuildingFacets=60546,completeCurrentDrawnTerrainFacets=3865,
   completeSourceMeshArraysRenderedBeforeAxisCrop=True,geographicCropBounds=[lo.tolist(),hi.tolist()],diagnosticCentreOriginalXYZ=center.tolist(),
   absoluteHKPDYFromPlottedVertical='plotted vertical + diagnosticCentreOriginalXYZ[1]',allPlotAxesRelativeToRecordedDiagnosticCentre=True,
   noVisualRoleAcceptance=True));refs.append(ref(path));pulse(True)
 for pin in refs:verify(pin)
 assert ref(manifest)==start;pulse(True)
 save(DOC/'source-gltf-documents-and-provider-poses.json.gz',dict(rows=source_records,providerToViewerOffsetOnly=[-834500,0,816500],sourceCoordinateScaleUnmodified=True))
 save(DOC/'complete-ground-facet-provenance.json.gz',dict(completeActualGroundFaces=ground.tolist(),completeCapturedLayers=captured['layers'],
  completeGroundFacetProvenance=face_provenance,completeCurrentNativePatchLocations=native_locations,
  noGenericLayerNameUsedAsPatchIdentity=True,unresolvedGridHydroPatchLineagesExplicit=True))
 save(DOC/'diagnostic.json.gz',dict(uids=UIDS,currentManifest=start,completeOwnedOriginalFaces=19681,completeRetainedOriginalBuildingFacets=40865,
  completeOriginalBodies=25,completeOriginalZeroGlobalFacesRetainedUncredited=zeros,completePairOriginalWorld=pair.tolist(),
  completeRetainedOriginalBuildingWorlds=[a.tolist()for a in originals[2:]],failureRows=failrows,bodyWorldRows=bodyrows,images=images,
  all230OrdinaryFailingFacesFourWorldSameIDs=source_fail_ids,completeCurrentTerrainTriangles=3865,
  sourceUnitProviderMatrixAndElevationNotAltered=True,noRoofFloorFoundationOrOtherFunctionAssignment=True,
  noGeometryOrTerrainChanges=True,noRoleRootOrNativeAcceptance=True,currentAcceptance=False,newlyInstalled=0))
 freeze=module('sparkle_original_context_freeze',HELPERS[-1]);freeze.freeze(BATCH,'sparkle-all230-original-failure-and-all25body-current-terrain-context-v1',
  [verify(r)for r in {r['path']:r for r in refs}.values()]+[DOC/'source-gltf-documents-and-provider-poses.json.gz',DOC/'complete-ground-facet-provenance.json.gz',DOC/'diagnostic.json.gz'],
  dict(uids=UIDS,completeOwnedOriginalFaces=19681,completeOriginalBodies=25,completeOriginalZeroFacets=150,completeOrdinaryFailedFaceWorldRows=920,
   sourceOnly=True,currentAcceptance=False,noRoleRootOrNativeAcceptance=True,newlyInstalled=0))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();resources=['building:'+u for u in UIDS]+['terrain-patch:'+u for u in UIDS]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('sparkle-original-failure-context-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok']
 save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned','--current-manifest-sha',CURRENT],cwd=ROOT,check=True)
if __name__=='__main__':main()
