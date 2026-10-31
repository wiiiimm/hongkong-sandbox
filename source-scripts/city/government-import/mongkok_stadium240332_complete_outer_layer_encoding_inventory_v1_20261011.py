"""DRAFT complete outer layer/encoding inventory; no mesh or acceptance.
Retain exact plane conflicts, independently compare literal Float32 node encodings.
ROOT full-read before execution. Uses frozen complete current capture, no browser.
"""
from fractions import Fraction as F
from pathlib import Path
import numpy as np,time
from run import ROOT,HERE,read,save,digest,connect
from exact_compute_transition_mesh_v1_20261011 import faces,project,height,contains,edge_intersections
from exact_atomic_terrain_domain_boundary_ring_v1_20261011 import on,at
from exact_source_core_ten_metre_transition_domain_v1_20261011 import intersection,separated
from exact_original_projection_coverage_v2_20261010 import signed_area
B=ROOT/'docs/astra-city/government-import';PRE=B/'government-xl-mongkok-stadium240332-ten-metre-clipped-transition-candidate-v1-20261011';DOC=B/'government-xl-mongkok-stadium240332-complete-outer-layer-encoding-inventory-v1-20261011';PIN='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def restore(x):
 if isinstance(x,list):return [restore(v)for v in x]
 if isinstance(x,dict):return {k:restore(v)for k,v in x.items()}
 if isinstance(x,str):
  try:return F(x)
  except (ValueError,ZeroDivisionError):return x
 return x

def serial(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,(list,tuple)):return [serial(v)for v in x]
 if isinstance(x,dict):return {k:serial(v)for k,v in x.items()}
 return x

def f32node(p,y):
 a=np.asarray([float(p[0]),float(y),float(p[1])],dtype='<f4');assert np.isfinite(a).all();return dict(bytesHex=a.tobytes().hex(),actualPosition=a.astype('<f8').tolist())

def main():
 started=time.monotonic();assert not DOC.exists();r=read(PRE/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 before=ref(ROOT/'3d-viewer/city/data/manifest.json');assert before['sha256']==PIN
 d=restore(read(PRE/'exact-domain.json.gz'));g=read(PRE/'complete-current-ground.json.gz');current=faces(np.asarray([x['actualTriangle']for x in g['completeClosedDomainAABBActualGroundFacets']],dtype='<f8').reshape(-1,3,3));polys=[project(f)for f in current];assert len(current)==2282 and g['startEndAllInputsVerified']
 refs=[ref(p)for p in [Path(__file__),PRE/'result.json',PRE/'diagnostic.json.gz',PRE/'exact-domain.json.gz',PRE/'complete-current-ground.json.gz',ROOT/'3d-viewer/city/world.js',ROOT/'3d-viewer/city/native-terrain.js',ROOT/'3d-viewer/city/geo.js',ROOT/'3d-viewer/city/data/terrain.json',ROOT/'3d-viewer/city/data/government-native-240527-0.json',HERE/'test_mongkok_stadium240332_outer_layer_node_encoding_v1_20261011.py',B/'government-xl-mongkok-stadium240332-complete-outer-layer-encoding-method-v1-20261011/METHOD.md']]+[before]+[dict(path=p,sha256=h)for p,h in g['inputHashes'].items()]
 # Bind protected240527 layer completely to actual production attributes/facet.
 patch=read(ROOT/'3d-viewer/city/data/government-native-240527-0.json');pos=np.asarray(patch['nativeMesh']['position'],dtype='<f4').reshape(-1,3);idx=np.asarray(patch['nativeMesh']['index'],dtype='<u4').reshape(-1,3)
 for i,f in enumerate(idx):
  a,b,c=pos[f].astype('<f8');y=(b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2])
  if y<0:idx[i,1],idx[i,2]=idx[i,2],idx[i,1]
 mesh=g['completeGlobalActualMeshes'][175];assert mesh['meshOrdinal']==175 and len(idx)==16297 and digest(pos.tobytes())==mesh['actualPositionAttributeSHA256']and digest(idx.tobytes())==mesh['actualIndexAttributeSHA256'];assert np.array_equal(pos[idx[4029]].astype('<f8').reshape(-1),g['completeClosedDomainAABBActualGroundFacets'][826]['actualTriangle'])
 parent=read(ROOT/'3d-viewer/city/data/terrain.json');georef=parent['meta']['georef'];p=current[1];cell_nodes=[]
 for x,y,z in p:
  col=(x+834500-F(georef['bE']))/F(georef['aE']);row=(816500-z-F(georef['bN']))/F(georef['aN']);assert col.denominator==row.denominator==1;i=int(row)*parent['w']+int(col);rendered=parent.get('renderedElev',[]);v=rendered[i]if rendered else None;expected=v if v is not None else(max(1.2,parent['elev'][i])if parent['elev'][i]>0 else -4);assert F(float(np.float32(expected)))==y;cell_nodes.append([int(col),int(row)])
 assert sorted(cell_nodes)==[[510,388],[511,387],[511,388]];assert patch['coarseCells']==[510,388,514,390];parent_cell=[510,387];assert not(510<=parent_cell[0]<514 and 388<=parent_cell[1]<390)
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');top_patches=[read(ROOT/'3d-viewer'/e['url'])for e in manifest['terrainPatches']];all_root_masks=[p['coarseCells']for p in top_patches]+parent.get('patchExclusions',[]);assert not any(a<=510<c and b<=387<e for a,b,c,e in all_root_masks)
 bindings=dict(nativeMeshOrdinal=175,completeFacets=16297,completePositionSHA256=digest(pos.tobytes()),completeIndexSHA256=digest(idx.tobytes()),nativeFacet4029CompleteByteEquality=True,patch=ref(ROOT/'3d-viewer/city/data/government-native-240527-0.json'),patchTargetUIDs=patch['meta']['targetUids'],coarseCells=patch['coarseCells'],parentMeshOrdinal=0,parentFacet328473ExactGridNodes=cell_nodes,parentCell=parent_cell,parentCellOutsideThisPatchCoarseMask=True,parentCellOutsideAllRootCoarseMasks=True,completeRootCoarseMasks=all_root_masks,sharedBoundaryZ='-8615/2',wholeParentNativeFacetPositiveOverlapM2=str(signed_area(intersection(polys[1],polys[826]))))
 intervals=[];nodes={};edges=d['combinedAtomicBoundary']['allBoundaryAtoms']
 for bi,r in enumerate(edges):
  e=r['incidences'][0];a,b=e['start'],e['end'];cuts={F(0),F(1)}
  for poly in polys:
   if separated([a,b],poly):continue
   for c,q in zip(poly,poly[1:]+poly[:1]):
    cuts.update(on(a,b,v)for v in edge_intersections(a,b,c,q))
  cuts=sorted(cuts)
  for lo,hi in zip(cuts,cuts[1:]):
   u,v=at(a,b,lo),at(a,b,hi);mid=at(a,b,(lo+hi)/2);ids=[i for i,poly in enumerate(polys)if contains(poly,mid)];values=[[height(current[i],q)for q in [u,v]]for i in ids];encodings=[[f32node(q,y)for q,y in zip([u,v],ys)]for ys in values]
   intervals.append(dict(boundaryAtom=bi,exactInterval=[lo,hi],endpoints=[u,v],allCapturedCurrentPlaneIds=ids,allGlobalFacetIds=[{k:g['completeClosedDomainAABBActualGroundFacets'][i][k]for k in ['meshOrdinal','originalMeshFacet']}for i in ids],allExactEndpointHeights=values,allLiteralFloat32EndpointEncodings=encodings,uncovered=not ids,exactPlaneEndpointHeightsEqual=bool(ids)and all(q==values[0]for q in values),literalFloat32EndpointBytesEqual=bool(ids)and all([x['bytesHex']for x in q]==[x['bytesHex']for x in encodings[0]]for q in encodings)))
   for q in [u,v]:nodes[q]=None
 for q in nodes:
  ids=[i for i,poly in enumerate(polys)if contains(poly,q)];ys=[height(current[i],q)for i in ids];cast=[F(float(np.float32(float(t))))for t in q];cast_ids=[i for i,poly in enumerate(polys)if contains(poly,cast)];cast_ys=[height(current[i],cast)for i in cast_ids];enc=[f32node(q,y)for y in ys];nodes[q]=dict(exactXZ=q,allCapturedCurrentPlaneIds=ids,allExactHeights=ys,allLiteralFloat32NodeEncodings=enc,exactHeightsEqual=bool(ids)and len(set(ys))==1,literalFloat32NodeBytesEqual=bool(ids)and len({x['bytesHex']for x in enc})==1,actualFloat32XZ=cast,allFiniteCurrentPlanesAtActualCastXZ=cast_ids,allExactCurrentHeightsAtActualCastXZ=cast_ys,qualification='Node encoding equality only; finite full rendered edge/domain/actor proof remains unqualified. Re-evaluated castXZ records describe unchanged actual current planes, not a fabricated y snap.')
 # Complete positive-area layer ownership over the domain. Count each face once;
 # per-face areas are descriptive/nonadditive where actual layers overlap.
 combined=d['originalCorePolygons']+d['computeBandPolygons'];active=[]
 for i,poly in enumerate(polys):
  pieces=[intersection(poly,q)for q in combined if not separated(poly,q)];area=sum(signed_area(q)for q in pieces)
  if area:active.append(dict(capturedCurrentPlane=i,exactProjectedDomainAreaM2=area))
 overlaps=[]
 for ai,x in enumerate(active):
  i=x['capturedCurrentPlane']
  for y in active[:ai]:
   j=y['capturedCurrentPlane']
   if separated(polys[i],polys[j]):continue
   overlap=intersection(polys[i],polys[j])
   if not signed_area(overlap):continue
   pieces=[intersection(overlap,q)for q in combined if not separated(overlap,q)];area=sum(signed_area(q)for q in pieces)
   if area:overlaps.append(dict(capturedPlanes=[j,i],meshOrdinals=[g['completeClosedDomainAABBActualGroundFacets'][k]['meshOrdinal']for k in [j,i]],exactPositiveProjectedOverlapInsideDomainM2=area))
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')==before and all(ref(ROOT/e['path'])==e for e in refs)
 save(DOC/'diagnostic.json.gz',serial(dict(uid='landsd/240332:0',sourceOnly=True,currentAcceptance=False,terrainCandidateCreated=False,layerProvenance=bindings,completeCurrentFaces=len(current),completeOuterAtomicEdges=len(edges),completeOuterIntervals=intervals,completeOuterNodes=list(nodes.values()),allCurrentFacetsWithPositiveDomainArea=active,allPositiveCurrentLayerOverlapsInsideDomain=overlaps,allExactPlaneHeightNegativesPreserved=True,noNumericToleranceUsed=True,liveTerrainChanges=0,sourceGeometryChanges=0,evidenceRefs=refs,elapsedSeconds=time.monotonic()-started,qualification='Complete frozen-domain current layer/finite outer interval and node encoding inventory only. Literal Float32 equality is exact byte equality, not a height epsilon; exact rational mismatches remain negative. No mesh, new boundary, role/identity/support/current approval. Existing retained layer edges are not sourcebuilding failures. Any later renderer-seam candidate requires independent complete actualFloat32 shared-edge/incidence/overlap and all protected240527/source/foreign/native/water/runtime regressions.')))
if __name__=='__main__':main()
