"""Exact constrained Float32 enclosure of a convex residual on its OWN parent.

No epsilon/buffer/bbox substitution. Source meshes never change. ROOT alone
uses this on production masks; tests use synthetic geometry only.
"""
from fractions import Fraction as F
import math,struct
from upton_six_basic_preserved_ground_feasibility_v1_20261012 import orient,area,on_segment
from upton_exact_full_residual_current_coverage_v1_20261014 import cover_whole_polygon
from polyu_five_mask_source_plane_partition_v1_20261014 import points,normal,serial
from southside_saved_local_core_parent_adapter_v3_20261012 import old
SIGN=1<<31;MASK=(1<<32)-1

def bits_value(bits):return struct.unpack('>f',struct.pack('>I',bits))[0]
def value_bits(value):return struct.unpack('>I',struct.pack('>f',value))[0]
def key_bits(bits):return (~bits)&MASK if bits&SIGN else bits|SIGN
def bits_key(key):return key^SIGN if key&SIGN else (~key)&MASK
MINKEY=key_bits(0xff7fffff);MAXKEY=key_bits(0x7f7fffff);MAXVALUE=F(bits_value(0x7f7fffff))

def exact_f32(q):
 q=F(q)
 try:
  v=bits_value(value_bits(float(q)))
  return math.isfinite(v)and F(v)==q
 except (OverflowError,ValueError):return False

def bracket(q):
 q=F(q);assert -MAXVALUE<=q<=MAXVALUE, 'exact rational outside finite Float32 range'
 if exact_f32(q):
  bits=value_bits(float(q));return q,q,dict(exactInput=str(q),lowerBitsHex=f'{bits:08x}',upperBitsHex=f'{bits:08x}',exactlyRepresentable=True,completeAdjacentFiniteFloat32Brackets=True)
 lo,hi=MINKEY,MAXKEY
 while lo<hi:
  mid=(lo+hi)//2
  if F(bits_value(bits_key(mid)))>=q:hi=mid
  else:lo=mid+1
 upper=F(bits_value(bits_key(lo)));lower=F(bits_value(bits_key(lo-1)));assert lower<q<upper
 return lower,upper,dict(exactInput=str(q),lowerBitsHex=f'{bits_key(lo-1):08x}',upperBitsHex=f'{bits_key(lo):08x}',lowerExact=str(lower),upperExact=str(upper),exactlyRepresentable=False,adjacentOrderedKeys=[lo-1,lo],completeAdjacentFiniteFloat32Brackets=True)

def round_nearest(q):
 q=F(q);lo,hi,proof=bracket(q)
 if lo==hi:chosen=int(proof['lowerBitsHex'],16);tie=False
 else:
  dl,du=q-lo,hi-q;tie=dl==du
  chosen=int(proof['lowerBitsHex']if dl<du or(tie and int(proof['lowerBitsHex'],16)%2==0)else proof['upperBitsHex'],16)
 value=bits_value(chosen);assert math.isfinite(value)
 return value,dict(**proof,chosenBitsHex=f'{chosen:08x}',chosenExact=str(F(value)),nearestExactDistancesCompared=True,halfwayTie=tie,tiesToEvenLeastSignificandBit=True,noDoubleRoundingAssumption=True)

def clean_polygon(values):
 raw=[tuple(F(v)for v in p)for p in values];assert all(len(p)==2 for p in raw)
 poly=[]
 for p in raw:
  if not poly or p!=poly[-1]:poly.append(p)
 if len(poly)>1 and poly[0]==poly[-1]:poly.pop()
 assert len(poly)>=3 and area(poly)!=0, 'non-positive residual needs separate degenerate obligations'
 if area(poly)<0:poly.reverse()
 assert all(orient(a,b,c)>=0 for a,b,c in zip(poly,poly[1:]+poly[:1],poly[2:]+poly[:2])), 'nonconvex residual requires exact convex decomposition, never a bbox'
 return raw,poly

def inside(p,triangle):return all(orient(a,b,p)>=0 for a,b in zip(triangle,triangle[1:]+triangle[:1]))

def hull(points):
 ps=sorted(set(points));assert len(ps)>=3
 def half(values):
  out=[]
  for p in values:
   while len(out)>=2 and orient(out[-2],out[-1],p)<=0:out.pop()
   out.append(p)
  return out
 result=half(ps)[:-1]+half(list(reversed(ps)))[:-1];assert len(result)>=3 and area(result)>0
 return result

def edge_cell_interval(a,b,bounds):
 lo,hi=F(0),F(1)
 for k in range(2):
  lower,upper=bounds[k],bounds[k+2];d=b[k]-a[k]
  if d==0:
   if not lower<=a[k]<=upper:return None
  else:
   u,v=(lower-a[k])/d,(upper-a[k])/d;lo=max(lo,min(u,v));hi=min(hi,max(u,v))
   if lo>hi:return None
 return lo,hi

def edge_nodes(a,b,limit,pulse):
 axes=[]
 for k in range(2):
  if a[k]==b[k]:continue
  assert exact_f32(a[k])and exact_f32(b[k]);l=key_bits(value_bits(float(min(a[k],b[k]))));h=key_bits(value_bits(float(max(a[k],b[k]))));axes.append((h-l+1,k,l,h))
 assert axes;count,axis,l,h=min(axes)
 if count>limit:raise ValueError('Declared exact Float32 edge enumeration bound exceeded; no absence or geometry credit')
 nodes={}
 for key in range(l,h+1):
  value=F(bits_value(bits_key(key)));t=(value-a[axis])/(b[axis]-a[axis]);assert 0<=t<=1
  p=tuple(a[k]+t*(b[k]-a[k])for k in range(2))
  if all(exact_f32(v)for v in p):nodes[t]=p
  if (key-l)%256==0:pulse()
 ordered=sorted(nodes.items());assert ordered[0][0]==0 and ordered[-1][0]==1
 return ordered,dict(enumeratedAxis=axis,completeOrderedIEEEKeyRange=[l,h],completeEnumeratedKeyCount=count,allOtherCoordinateRepresentabilityTestedExactly=True,completeExactCollinearFloat32Nodes=[dict(parameter=str(t),exactXZ=list(map(str,p)))for t,p in ordered],noNearCollinearOrToleranceCredit=True)

def enclose(values,parent,*,edge_enumeration_limit=262144,pulse=lambda:None):
 source,parent_ccw=points(parent),[(F(p[0]),F(p[2]))for p in parent];assert len(source)==3
 assert all(exact_f32(v)for p in source for v in p), 'whole source parent must already be saved Float32'
 if area(parent_ccw)<0:parent_ccw.reverse()
 assert area(parent_ccw)>0;original,mask=clean_polygon(values)
 assert all(inside(p,parent_ccw)for p in mask), 'fresh residual is outside its authenticated complete parent'
 seeds=[];cells=[];edges=[];edge_cache={}
 original_edges=[((p[0],p[2]),(q[0],q[2]))for p,q in zip(source,source[1:]+source[:1])]
 for i,p in enumerate(mask):
  lx,hx,bx=bracket(p[0]);lz,hz,bz=bracket(p[1]);corners=list(dict.fromkeys([(x,z)for x in [lx,hx]for z in [lz,hz]]));included=[q for q in corners if inside(q,parent_ccw)];seeds.extend(included);cell=dict(maskVertex=i,exactMaskVertex=list(map(str,p)),xBracket=bx,zBracket=bz,closedExactBounds=list(map(str,(lx,lz,hx,hz))),includedOwnParentFloat32Corners=[list(map(str,q))for q in included],excludedOutsideOwnParentCorners=[list(map(str,q))for q in corners if q not in included])
  # All corners inside gives an exact containing cell; no parent-edge widening.
  if len(included)!=len(corners):
   for edge,(a,b)in enumerate(original_edges):
    interval=edge_cell_interval(a,b,(lx,lz,hx,hz))
    if interval is None:continue
    if edge not in edge_cache:edge_cache[edge]=edge_nodes(a,b,edge_enumeration_limit,pulse)
    nodes,proof=edge_cache[edge];left=max((q for q in nodes if q[0]<=interval[0]),key=lambda q:q[0]);right=min((q for q in nodes if q[0]>=interval[1]),key=lambda q:q[0]);seeds.extend([left[1],right[1]])
    edges.append(dict(maskVertex=i,originalParentEdge=edge,exactCellEdgeIntersectionParameterInterval=list(map(str,interval)),exactEnclosingRepresentableParameters=[str(left[0]),str(right[0])],ownOriginalEdgeNodes=[list(map(str,left[1])),list(map(str,right[1]))],completeOwnEdgeRepresentabilityCertificate=proof))
  cells.append(cell);pulse()
 enclosed=hull(seeds);assert all(inside(p,parent_ccw)for p in enclosed)
 vertex_proofs=[dict(maskVertex=i,allHullClosedHalfPlanes=[str(orient(a,b,p))for a,b in zip(enclosed,enclosed[1:]+enclosed[:1])])for i,p in enumerate(mask)]
 assert all(all(F(v)>=0 for v in r['allHullClosedHalfPlanes'])for r in vertex_proofs), 'certified source-constrained lattice seeds do not enclose the whole residual'
 n=normal(source);assert n[1]!=0;lifted=[];nodeproofs=[]
 for x,z in enclosed:
  ideal_y=source[0][1]-(n[0]*(x-source[0][0])+n[2]*(z-source[0][2]))/n[1];y,yp=round_nearest(ideal_y);p=(float(x),y,float(z));assert F(p[0])==x and F(p[2])==z
  residual=sum(n[k]*(F(p[k])-source[0][k])for k in range(3));lifted.append(p);nodeproofs.append(dict(exactOwnPlanePoint=list(map(str,(x,ideal_y,z))),actualPackedXYZ=p,actualPackedXYZBitsHex=[f'{value_bits(v):08x}'for v in p],yPackingCertificate=yp,exactPackedOwnPlaneResidual=str(residual),allPackedXZByteIdentityCertified=True,noOtherHeightLayerYUsed=True))
 faces=[];projected=[];skipped=[]
 for i,t in enumerate(old.fan(lifted)):
  A,B,C=t;det=(B[2]-C[2])*(A[0]-C[0])+(C[0]-B[0])*(A[2]-C[2]);xz=[(F(p[0]),F(p[2]))for p in t];exact_det=orient(xz[0],xz[1],xz[2]);assert exact_det!=0
  row=dict(localFacet=i,actualPackedTriplet=t,exactProjectedDeterminant=str(exact_det),productionBinary64HeightIndexDeterminant=det,productionHeightIndexIncludesFacet=abs(det)>=1e-10,existingDeterminantThresholdM2=1e-10,noThresholdWaiver=True);faces.append(row)
  if abs(det)>=1e-10:
   if area(xz)<0:xz.reverse()
   projected.append((i,xz))
  else:skipped.append(i)
 assert projected, 'no certified packed enclosure facets are production height indexed'
 coverage=cover_whole_polygon(mask,projected);assert coverage['wholeClosedResidualCovered'], 'height-indexed ACTUAL packed triangles do not enclose every residual boundary'
 return dict(exactInputResidualVerbatim=serial(original),normalizedConvexResidual=serial(mask),wholeOriginalOwnParentTriplet=serial(source),completeAdjacentFloat32VertexCells=cells,completeOriginalParentEdgeCertificates=edges,exactEnclosingHullXZ=serial(enclosed),completeVertexClosedHullCertificates=vertex_proofs,allHullVerticesWithinOriginalParent=True,allOriginalResidualVerticesEdgesAreaEnclosed=True,completeOwnPlanePackedNodeCertificates=nodeproofs,actualPackedFacetRecords=faces,productionHeightIndexSkippedFacetsPreservedNoCredit=skipped,actualHeightIndexedWholeClosedMaskCoverage=serial(coverage),noEpsilonBufferBBoxSubstituteOrOtherLayerY=True,notWholeActorFiniteOrPhysicalAcceptance=True)
