"""Exact dyadic plane grouping of actual Float32 terrain, never acceptance.

The grouping includes vertical and reversed triangles. Degenerate originals
are recorded individually. Equal planes alone do not justify deleting faces:
complete finite region, multiplicity, normal, collision and boundary proofs are
still required before a different representation can be used.
"""
from collections import defaultdict
from functools import reduce
from math import gcd
import numpy as np

def groups(triangles):
    t=np.asarray(triangles,dtype=np.float32).astype(np.float64)
    assert t.ndim==3 and t.shape[1:]==(3,3) and np.isfinite(t).all()
    ratios={float(v):float(v).as_integer_ratio() for v in np.unique(t)}
    denominator=max(d for n,d in ratios.values())
    integers={v:n*(denominator//d) for v,(n,d) in ratios.items()}
    result=defaultdict(list);degenerate=[]
    for i,face in enumerate(t):
        p,q,r=[tuple(integers[float(v)] for v in point) for point in face]
        a=tuple(q[j]-p[j] for j in range(3));b=tuple(r[j]-p[j] for j in range(3))
        normal=(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
        if not any(normal):degenerate.append(i);continue
        coefficient=normal+(-sum(normal[j]*p[j] for j in range(3)),)
        divisor=reduce(gcd,coefficient);coefficient=tuple(v//divisor for v in coefficient)
        # Keep winding as a separate key. Opposite-facing duplicate surfaces
        # must not silently acquire cancellation or shared ownership credit.
        orientation=1 if next(v for v in coefficient if v)!=abs(next(v for v in coefficient if v)) else 0
        if orientation:coefficient=tuple(-v for v in coefficient)
        result[(coefficient,orientation)].append(i)
    rows=[{'exactPlaneIntegerCoefficients':list(k[0]),'originalOrientation':k[1],
           'faceIds':ids,'faceCount':len(ids),'vertical':k[0][1]==0}
          for k,ids in sorted(result.items(),key=lambda item:(-len(item[1]),item[0]))]
    return {'coordinateIntegerDenominator':denominator,'faces':len(t),
            'nondegenerateFaces':sum(r['faceCount'] for r in rows),
            'degenerateFaceIds':degenerate,'orientedExactPlaneGroups':len(rows),
            'multiFaceGroups':sum(r['faceCount']>1 for r in rows),
            'facesInMultiFaceGroups':sum(r['faceCount'] for r in rows if r['faceCount']>1),
            'rows':rows,'qualification':'Plane census only. All finite original surfaces and degenerate face IDs retained; no geometry, seam, collision or acceptance credit.'}
