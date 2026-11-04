"""DRAFT exact source-core/generated-band/current-outer mesh nomination.
All original planes exact before standard Float32 rendering; no building edits.
"""
from fractions import Fraction as F
from collections import defaultdict
import numpy as np
from exact_source_core_ten_metre_transition_domain_v1_20261011 import polygon,atomic,intersection,separated
from exact_original_projection_coverage_v2_20261010 import cross,signed_area,subtract
from exact_atomic_terrain_domain_boundary_ring_v1_20261011 import on,at
class CandidateRejection(AssertionError):
 def __init__(self,reason,evidence):super().__init__(reason);self.evidence=evidence
def require(test,reason,evidence):
 if not test:raise CandidateRejection(reason,evidence)
def faces(a):
 a=np.asarray(a,dtype='<f8');assert a.ndim==3 and a.shape[1:]==(3,3)and len(a)>0 and np.isfinite(a).all()
 return [[tuple(F(float(v))for v in p)for p in f]for f in a]
def project(f):
 p=[(q[0],q[2])for q in f];return polygon(p if signed_area(p)>0 else list(reversed(p)))
def height(f,p):
 x=[(q[0],q[2])for q in f];den=cross(*x);assert den!=0
 return sum(cross(x[(i+1)%3],x[(i+2)%3],p)*f[i][1]for i in range(3))/den
def contains(poly,p):return all(cross(a,b,p)>=0 for a,b in zip(poly,poly[1:]+poly[:1]))
def edge_intersections(a,b,c,d):
 dx,dz=b[0]-a[0],b[1]-a[1];ex,ez=d[0]-c[0],d[1]-c[1];den=dx*ez-dz*ex
 if den:
  qx,qz=c[0]-a[0],c[1]-a[1];t=(qx*ez-qz*ex)/den;u=(qx*dz-qz*dx)/den
  return [at(a,b,t)]if 0<=t<=1 and 0<=u<=1 else []
 return [p for p in [a,b,c,d]if on(a,b,p)is not None and on(c,d,p)is not None]
def outer_segments(boundary,current):
 projected=[project(f)for f in current];rows=[]
 for bi,r in enumerate(boundary['allBoundaryAtoms']):
  e=r['incidences'][0];a,b=e['start'],e['end'];cuts={F(0),F(1)}
  for p in projected:
   for c,d in zip(p,p[1:]+p[:1]):
    for q in edge_intersections(a,b,c,d):cuts.add(on(a,b,q))
  cuts=sorted(cuts)
  for lo,hi in zip(cuts,cuts[1:]):
   u,v=at(a,b,lo),at(a,b,hi);mid=at(a,b,(lo+hi)/2);ids=[i for i,p in enumerate(projected)if contains(p,mid)];require(bool(ids),'Outer finite ground interval uncovered',dict(boundaryAtom=bi,exactInterval=[lo,hi],endpoints=[u,v]))
   values=[[height(current[i],p)for p in [u,v]]for i in ids];require(all(q==values[0]for q in values),'Outer retained planes have incompatible3D heights',dict(boundaryAtom=bi,exactInterval=[lo,hi],endpoints=[u,v],allCurrentPlaneIds=ids,allExactEndpointHeights=values))
   # Closed endpoints can also touch a third existing current plane.
   for p,y in zip([u,v],values[0]):
    node_ids=[i for i,q in enumerate(projected)if contains(q,p)];node_y=[height(current[i],p)for i in node_ids];require(set(node_y)=={y},'Outer closed-node height conflict',dict(boundaryAtom=bi,point=p,allCurrentPlaneIds=node_ids,allExactHeights=node_y))
   rows.append(dict(boundaryAtom=bi,start=u,end=v,exactEndpointY=values[0],allCurrentPlaneIds=ids))
 return rows
def closest(p,edges):
 options=[]
 for i,e in enumerate(edges):
  a,b=e['start'],e['end'];dx,dz=b[0]-a[0],b[1]-a[1];den=dx*dx+dz*dz;assert den>0;t=max(F(0),min(F(1),((p[0]-a[0])*dx+(p[1]-a[1])*dz)/den));q=at(a,b,t);dist=sum((p[k]-q[k])**2 for k in range(2));y=e['exactEndpointY'][0]+t*(e['exactEndpointY'][1]-e['exactEndpointY'][0]);options.append((dist,i,y))
 assert options;dist,i,y=min(options);return dist,y,i
def interpolated(p,inner,outer):
 def anchors(edges):
  return {e['exactEndpointY'][0]+t*(e['exactEndpointY'][1]-e['exactEndpointY'][0])for e in edges if(t:=on(e['start'],e['end'],p))is not None}
 ih,oh=anchors(inner),anchors(outer);assert len(ih)<=1 and len(oh)<=1,'Multiple anchor heights'
 if ih and oh:assert ih==oh,'Authentic-inner/current-outer pinch conflict'
 if ih or oh:return next(iter(ih or oh))
 di,yi,_=closest(p,inner);do,yo,_=closest(p,outer);assert di>0 and do>0
 return (do*yi+di*yo)/(di+do)
def split(poly,points):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  cuts={F(0)}
  for p in points:
   t=on(a,b,p)
   if t is not None and t<1:cuts.add(t)
  out.extend(at(a,b,t)for t in sorted(cuts))
 return out
def fan(poly,getheight):
 assert signed_area(poly)>0;c=tuple(sum(p[k]for p in poly)/len(poly)for k in range(2));cy=getheight(c);out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  assert cross(c,a,b)>0,'Degenerate fan piece';out.append([(c[0],cy,c[1]),(b[0],getheight(b),b[1]),(a[0],getheight(a),a[1])])
 return out
def mesh_edges(triangles):
 edges=defaultdict(list)
 for i,f in enumerate(triangles):
  for a,b in zip(f,f[1:]+f[:1]):edges[tuple(sorted(((a[0],a[2]),(b[0],b[2]))))].append(dict(face=i,start=a,end=b))
 bad=[];boundary=[]
 for key,inc in sorted(edges.items()):
  if len(inc)==1:boundary.append(dict(edge=key,incidences=inc))
  elif len(inc)!=2 or inc[0]['start']!=inc[1]['end']or inc[0]['end']!=inc[1]['start']:bad.append(dict(edge=key,incidences=inc))
 return dict(completeEdges=len(edges),allBoundaryEdges=boundary,allInvalidInternalIncidences=bad)
def positive_overlap_inventory(triangles):
 polys=[project(f)for f in triangles];boxes=[(min(p[0]for p in q),max(p[0]for p in q),min(p[1]for p in q),max(p[1]for p in q),i)for i,q in enumerate(polys)];boxes.sort();bad=[]
 for pos,a in enumerate(boxes):
  for b in boxes[pos+1:]:
   if b[0]>a[1]:break
   if a[3]<b[2]or b[3]<a[2]:continue
   poly=intersection(polys[a[4]],polys[b[4]]);area=signed_area(poly)
   if area:bad.append(dict(faces=[a[4],b[4]],exactPositiveProjectedOverlapM2=area))
 return bad
def nominate(core_faces,current_faces,d):
 core,current=faces(core_faces),faces(current_faces);assert len(core)==len(d['originalCorePolygons'])
 inner=[]
 for r in d['sourceCoreAtomicBoundary']['allBoundaryAtoms']:
  e=r['incidences'][0];inner.append(dict(start=e['start'],end=e['end'],exactEndpointY=[height(core[e['piece']],p)for p in [e['start'],e['end']]]))
 # Every original source-core internal atomic edge must be exactly continuous.
 for r in d['sourceCoreAtomicBoundary']['allAtomicEdges']:
  if len(r['incidences'])==2:
   x,y=r['incidences'];require(all(height(core[x['piece']],p)==height(core[y['piece']],p)for p in r['endpoints']),'Authentic source-core internal height conflict',dict(atomicEdge=r,sourceHeightPairs=[[height(core[e['piece']],p)for p in r['endpoints']]for e in [x,y]]))
 outer=outer_segments(d['combinedAtomicBoundary'],current);combined=d['originalCorePolygons']+d['computeBandPolygons'];retained=[];changed=[]
 for i,f in enumerate(current):
  p=project(f);remaining=[p]
  for q in combined:
   remaining=[v for old in remaining for v in subtract(old,q)]
   if not remaining:break
  area=sum(signed_area(q)for q in remaining)
  if area!=signed_area(p):changed.append(i);retained.extend(dict(currentPlane=i,polygon=q)for q in remaining)
 points={p for poly in combined for p in poly}|{p for r in retained for p in r['polygon']}|{p for r in outer for p in [r['start'],r['end']]};cache={}
 def generated(p):
  if p not in cache:cache[p]=interpolated(p,inner,outer)
  return cache[p]
 output=[];roles=[]
 for i,p in enumerate(d['originalCorePolygons']):
  rows=fan(split(p,points),lambda q:height(core[i],q));output.extend(rows);roles.extend(dict(role='authentic-source-planar-core',sourceCoreFacet=i)for _ in rows)
 for i,p in enumerate(d['computeBandPolygons']):
  rows=fan(split(p,points),generated);output.extend(rows);roles.extend(dict(role='compute-generated-ten-metre-L1-transition',bandPiece=i)for _ in rows)
 exact_edges=mesh_edges(output);assert not exact_edges['allInvalidInternalIncidences'],'Generated/core internal3D seam failure'
 # Every new mesh outer edge must match complete finite current planes exactly.
 for r in exact_edges['allBoundaryEdges']:
  e=r['incidences'][0]
  for p in [e['start'],e['end']]:assert generated((p[0],p[2]))==p[1]
 outside=[];outside_roles=[]
 for r in retained:
  i=r['currentPlane'];rows=fan(split(r['polygon'],points),lambda p:height(current[i],p));outside.extend(rows);outside_roles.extend(dict(role='clipped-retained-exact-current-plane',currentPlane=i)for _ in rows)
 # Preserve all original current vertices; only clipped renderer pieces are nominated.
 world=np.asarray([[tuple(float(v)for v in p)for p in f]for f in output],dtype='<f4');assert np.isfinite(world).all();f32=faces(world)
 for f in f32:assert cross(*[(p[0],p[2])for p in f])<0,'Float32 collapsed/reversed generated facet'
 f32_edges=mesh_edges(f32);assert not f32_edges['allInvalidInternalIncidences'],'ActualFloat32 generated internal seam failure'
 overlap=positive_overlap_inventory(output);f32_overlap=positive_overlap_inventory(f32);assert not overlap and not f32_overlap,'New exact/Float32 projected overlap'
 outside32=faces(np.asarray([[tuple(float(v)for v in p)for p in f]for f in outside],dtype='<f4'))if outside else []
 for f in outside32:assert cross(*[(p[0],p[2])for p in f])<0,'Float32 collapsed/reversed clipped current facet'
 full32_overlaps=positive_overlap_inventory(f32+outside32);new32_overlaps=[r for r in full32_overlaps if min(r['faces'])<len(f32)];assert not new32_overlaps,'ActualFloat32 generated/retained overlap'
 current32_residuals=[]
 for i,f in enumerate(outside32):
  original=current[outside_roles[i]['currentPlane']]
  for j,p in enumerate(f):
   delta=p[1]-height(original,(p[0],p[2]))
   if delta:current32_residuals.append(dict(clippedFacet=i,vertex=j,currentPlane=outside_roles[i]['currentPlane'],exactActualFloat32MinusOriginalCurrentPlaneM=delta))
 outedge=defaultdict(list)
 for f in outside32:
  for a,b in zip(f,f[1:]+f[:1]):outedge[tuple(sorted(((a[0],a[2]),(b[0],b[2]))))].append((a,b))
 for r in f32_edges['allBoundaryEdges']:
  e=r['incidences'][0];assert any(a==e['end']and b==e['start']for a,b in outedge[r['edge']]),'ActualFloat32 generated-to-clipped-current outer seam failure'
 return dict(exactSourceCoreAndGeneratedBandFacets=output,allFacetRoles=roles,actualFloat32SourceCoreAndGeneratedBandFacets=world.tolist(),exactClippedRetainedCurrentFacets=outside,allRetainedFacetRoles=outside_roles,actualFloat32ClippedRetainedCurrentFacets=np.asarray(outside,dtype='<f4').tolist(),allAffectedOriginalCurrentFacetIndices=changed,allExactCurrentOuterFiniteSegments=outer,exactInternalSeams=exact_edges,actualFloat32InternalSeams=f32_edges,allExactPositiveOverlaps=overlap,allActualFloat32PositiveOverlaps=f32_overlap,allActualFloat32GeneratedRetainedOverlaps=new32_overlaps,allActualFloat32RetainedOnlyOverlapContext=[r for r in full32_overlaps if min(r['faces'])>=len(f32)],allActualFloat32ClippedCurrentOriginalPlaneResiduals=current32_residuals,terrainCandidateApproved=False,fullProtectedActorRegressionsDischarged=False)
