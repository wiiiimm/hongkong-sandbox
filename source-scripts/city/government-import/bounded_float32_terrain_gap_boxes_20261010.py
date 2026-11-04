"""Exact dyadic clipping for construction only; full finite proof is mandatory.

Split complete polygon rings by closed Float32 halfplanes. Exact signed areas
account every positive fragment; zero-area ring records are retained. Output
boxes respect the unchanged .0001 m² piece/.1 m² box limits. No terrain or source
acceptance is inferred from this constructor.
"""
from fractions import Fraction as F
import math
import numpy as np
import shapely
MAX_GAP_AREA=F(1,10000)
MAX_BOX_AREA=F(1,10)

def rational(v):
    if isinstance(v,F):return v
    v=float(v)
    if not math.isfinite(v):raise ValueError('nonfinite coordinate')
    return F.from_float(v)

def round_out(v,positive):
    v=rational(v)
    if abs(v)>F.from_float(float(np.finfo(np.float32).max)):raise ValueError('Float32 overflow')
    q=np.float32(float(v));f=F.from_float(float(q))
    if (positive and f<v) or (not positive and f>v):
        q=np.nextafter(q,np.float32(np.inf if positive else -np.inf))
    return float(q)
def down(v):return round_out(v,False)
def up(v):return round_out(v,True)

def signed_area(ring):
    return sum((a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1])),F(0))/2 if ring else F(0)
def area(rings):
    return abs(signed_area(rings[0]))-sum((abs(signed_area(r)) for r in rings[1:]),F(0))
def clip(ring,axis,at,lower):
    if not ring:return []
    out=[]
    for a,b in zip(ring[-1:]+ring[:-1],ring):
        ain=a[axis]<=at if lower else a[axis]>=at
        bin=b[axis]<=at if lower else b[axis]>=at
        if ain!=bin:
            t=(at-a[axis])/(b[axis]-a[axis]);out.append(tuple(a[i]+t*(b[i]-a[i]) for i in range(2)))
        if bin:out.append(b)
    return out

def encoded(rings):return [[[str(v) for v in p] for p in ring] for ring in rings]

def bounded_boxes(polygon,max_pieces=10000):
    if polygon.geom_type!='Polygon' or polygon.is_empty or not polygon.is_valid:raise ValueError('complete valid nonempty polygon required')
    rings=[[tuple(rational(v) for v in p) for p in list(polygon.exterior.coords)[:-1]]]
    rings += [[tuple(rational(v) for v in p) for p in list(r.coords)[:-1]] for r in polygon.interiors]
    initial=area(rings)
    if initial<=0:raise ValueError('positive exact area required')
    queue=[(rings,0)];output=[];zero=[];splits=0
    while queue:
        rings,depth=queue.pop();a=area(rings)
        if a<0:raise ValueError('negative clipped area')
        if a==0:zero.append(encoded(rings));continue
        if depth>64 or len(queue)+len(output)>max_pieces:raise ValueError('bounded subdivision budget exceeded')
        x0=min(p[0] for p in rings[0]);x1=max(p[0] for p in rings[0]);z0=min(p[1] for p in rings[0]);z1=max(p[1] for p in rings[0])
        bounds=[down(x0),down(z0),up(x1),up(z1)]
        ba=(rational(bounds[2])-rational(bounds[0]))*(rational(bounds[3])-rational(bounds[1]))
        if a<MAX_GAP_AREA and ba<MAX_BOX_AREA:
            for ring in rings:
                for x,z in ring:
                    if not rational(bounds[0])<=x<=rational(bounds[2]) or not rational(bounds[1])<=z<=rational(bounds[3]):raise ValueError('outward box misses exact vertex')
            output.append((dict(exactClippedRings=encoded(rings),exactPositiveAreaM2=str(a),positiveAreaM2=float(a)),shapely.box(*bounds)));continue
        axis=0 if x1-x0>=z1-z0 else 1;lo,hi=(x0,x1) if axis==0 else (z0,z1)
        middle=rational(float(np.float32(float(lo+(hi-lo)/2))))
        if not lo<middle<hi:raise ValueError('Float32 split stalled')
        children=[[clip(r,axis,middle,lower) for r in rings] for lower in (True,False)]
        aa=[area(r) for r in children]
        if any(v<0 for v in aa) or sum(aa,F(0))!=a:raise ValueError('exact positive area not conserved')
        if max(aa)>=a:raise ValueError('subdivision failed to reduce scope')
        queue.extend((r,depth+1) for r in reversed(children));splits+=1
    total=sum((F(p['exactPositiveAreaM2']) for p,b in output),F(0))
    if total!=initial:raise ValueError('complete exact area not accounted')
    return output,dict(splits=splits,positivePieces=len(output),zeroAreaClippedRingRecords=zero,
        exactInputAreaM2=str(initial),exactOutputAreaM2=str(total),closedHalfplanePartition=True,
        exactFiniteAcceptance=False,maxGapAreaM2=float(MAX_GAP_AREA),maxBoxAreaM2=float(MAX_BOX_AREA))
