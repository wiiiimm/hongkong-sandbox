"""Classify SAVED exact contact witnesses; never recompute intersections."""
from fractions import Fraction as F
from exact_original_shell_intersections_20261009 import rational_face,cross,sub,dot
from exact_original_component_contacts_20261009 import contact_measure
from exact_original_finite_triangle_contacts_20261010 import point_in_hull,point_in_triangle
from science_museum_original_open_sided_contact_topology_attribution_v1_20261011 import relative_interior

def classify(saved,a,b):
 a,b=rational_face(a),rational_face(b);points=[tuple(F(x)for x in p)for p in saved['exactPoints']];assert points
 assert all(point_in_hull(p,a)and point_in_hull(p,b)for p in points),'Saved witness off actual finite source facets'
 m=contact_measure(points);assert m['dimension']==saved['dimension'];na=cross(sub(a[1],a[0]),sub(a[2],a[0]));nb=cross(sub(b[1],b[0]),sub(b[2],b[0]));cop=bool(any(na)and any(nb)and not any(cross(na,nb))and dot(na,sub(b[0],a[0]))==0);assert cop==saved['nonzeroExactCoplanarPlanes']
 mid=tuple(sum(p[k]for p in points)/len(points)for k in range(3));insideA=bool(any(na)and relative_interior(a,mid));insideB=bool(any(nb)and relative_interior(b,mid));proper=bool(not cop and m['dimension']==1 and insideA and insideB)
 return dict(savedDimension=m['dimension'],exactCoplanar=cop,noncoplanarBothRelativeInteriorSegment=proper,sourceRelativeInteriorAtWitnessMean=insideA,actorRelativeInteriorAtWitnessMean=insideB,exactEqualWholeFiniteTriangleVertexSets=bool(cop and set(a)==set(b)),entireSourceTriangleContainedInActorTriangle=bool(cop and all(point_in_triangle(v,b)for v in a)),entireActorTriangleContainedInSourceTriangle=bool(cop and all(point_in_triangle(v,a)for v in b)),sourcePlaneClass='vertical'if any(na)and na[1]==0 else'horizontal'if any(na)and na[0]==na[2]==0 else'oblique-or-degenerate',sourceWorldYRange=[str(min(v[1]for v in a)),str(max(v[1]for v in a))],properSurfaceCrossingIsNotSolidPenetrationOrInvalidArchitecture=True,ownershipOrAttachmentOrRootProved=False)
