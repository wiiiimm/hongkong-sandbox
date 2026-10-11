"""User-authorized exact scripted terrain representation consolidation.

All geometry certifying calculations use unbounded Python integers. Only
terrain is re-triangulated with existing unchanged Float32 vertices. Government
building meshes are never inputs. Unproved, degenerate, branched, holed and
overlapping edge-chain regions retain every original terrain face unchanged.
"""
from collections import defaultdict
import numpy as np
from exact_coplanar_boundary_census_20261010 import census

def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def area(poly):return sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(poly,poly[1:]+poly[:1]))
def on_segment(a,b,p):return cross(a,b,p)==0 and all(min(a[k],b[k])<=p[k]<=max(a[k],b[k]) for k in range(2))
def intersects(a,b,c,d):
    ac,ad,ca,cb=cross(a,b,c),cross(a,b,d),cross(c,d,a),cross(c,d,b)
    proper=((ac>0)!=(ad>0) and ac!=0 and ad!=0 and (ca>0)!=(cb>0) and ca!=0 and cb!=0)
    return proper or any(v==0 and on_segment(p,q,r) for v,p,q,r in [(ac,a,b,c),(ad,a,b,d),(ca,c,d,a),(cb,c,d,b)])
def simple(poly):
    if len(set(poly))!=len(poly):return False
    n=len(poly)
    for i in range(n):
        for j in range(i+1,n):
            if j==(i+1)%n or i==(j+1)%n:continue
            if intersects(poly[i],poly[(i+1)%n],poly[j],poly[(j+1)%n]):return False
    return True
def ears(poly):
    assert simple(poly);sign=1 if area(poly)>0 else -1;left=list(range(len(poly)));output=[]
    while len(left)>3:
        for j,b in enumerate(left):
            a,c=left[j-1],left[(j+1)%len(left)]
            if sign*cross(poly[a],poly[b],poly[c])<=0:continue
            if any(all(sign*cross(poly[u],poly[v],poly[p])>=0 for u,v in [(a,b),(b,c),(c,a)]) for p in left if p not in [a,b,c]):continue
            output.append([a,b,c]);del left[j];break
        else:raise ValueError('exact-ear-triangulation-unresolved')
    assert sign*cross(*(poly[i] for i in left))>0;output.append(left)
    assert sum(cross(*(poly[i] for i in f)) for f in output)==area(poly)
    return output

def consolidate(triangles):
    original=np.asarray(triangles,dtype=np.float32).astype(np.float64);diagnostic=census(original)
    denominator=max(float(v).as_integer_ratio()[1] for v in np.unique(original))
    def integer(p):return tuple(float(v).as_integer_ratio()[0]*(denominator//float(v).as_integer_ratio()[1]) for v in p)
    output=[];proofs=[];processed=set()
    for part in diagnostic['components']:
        ids=part['faceIds'];start=len(output);processed.update(ids);replacement=None;reason=part['state']
        if part['saving']>0 and reason=='single-simple-boundary':
            points={integer(p):p for p in original[ids].reshape(-1,3)};edges=defaultdict(list)
            for i in ids:
                p=[integer(v) for v in original[i]]
                for a,b in zip(p,p[1:]+p[:1]):edges[tuple(sorted((a,b)))].append((a,b))
            boundary={e[0][0]:e[0][1] for e in edges.values() if len(e)==1};loop=[];p=min(boundary)
            while p not in loop:loop.append(p);p=boundary[p]
            assert p==loop[0] and len(loop)==len(boundary)
            clean=[]
            for a,b,c in zip(loop[-1:]+loop[:-1],loop,loop[1:]+loop[:1]):
                u=tuple(b[k]-a[k] for k in range(3));v=tuple(c[k]-b[k] for k in range(3));n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
                if any(n) or sum(u[k]*v[k] for k in range(3))<=0:clean.append(b)
            normal=part['exactPlaneIntegerCoefficients'][:3];drop=max(range(3),key=lambda k:abs(normal[k]));axes=[k for k in range(3) if k!=drop];poly=[tuple(p[k] for k in axes) for p in clean]
            original_area=sum(cross(*(tuple(integer(p)[k] for k in axes) for p in original[i])) for i in ids)
            if not simple(poly) or area(poly)!=original_area:reason='exact-simple-boundary-or-oriented-area-unproved'
            else:
                try:
                    indices=ears(poly);replacement=np.asarray([[points[clean[k]] for k in face] for face in indices],float)
                    for face in replacement:assert all(sum(normal[k]*integer(p)[k] for k in range(3))+part['exactPlaneIntegerCoefficients'][3]==0 for p in face)
                    assert np.array_equal(replacement,replacement.astype(np.float32).astype(np.float64))
                    reason='exact-oriented-single-boundary-area-and-ear-certificate'
                except ValueError:reason='exact-ear-unresolved-originals-retained'
        output.extend(original[ids] if replacement is None else replacement)
        proofs.append({'originalFaceIds':ids,'outputFaceRange':[start,len(output)],'reason':reason,
            'originalFaces':len(ids),'outputFaces':len(output)-start,'vertical':part.get('vertical'),
            'exactPlane':part.get('exactPlaneIntegerCoefficients'),'sourceVerticesOnly':True,
            'completeOriginalOrientedEdgeChainPreserved':replacement is not None,
            'sameFinitePlaneSurfaceCertified':replacement is not None})
    assert processed|set(diagnostic['degenerateFaceIds'])==set(range(len(original)))
    for i in diagnostic['degenerateFaceIds']:
        start=len(output);output.append(original[i]);proofs.append({'originalFaceIds':[i],'outputFaceRange':[start,len(output)],'reason':'original-exact-degenerate-retained-unchanged','sourceVerticesOnly':True})
    return np.asarray(output,float),{'originalFaces':len(original),'outputFaces':len(output),'savedFaces':len(original)-len(output),
        'coordinateIntegerDenominator':denominator,'allOriginalFacesAccounted':True,'allDegenerateOriginalsRetained':True,
        'components':proofs,'physicalAccepted':False,'qualification':'Exact integer plane/oriented manifold edge-chain, simple boundary, oriented area and ear-triangulation certificates. Terrain only, unchanged original Float32 vertices; unproved regions remain literal originals. Actor/support/seam/runtime acceptance remains independent.'}
