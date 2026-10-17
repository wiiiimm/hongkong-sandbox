"""Diagnose exact circular-arc lineage without changing source polygons.

ArcGIS `c` segments give endpoint and interior point; start is the previous point.
https://developers.arcgis.com/rest/services-reference/enterprise/geometry-objects/
All anchors, straight segments and radial errors use the existing 2 mm limit.
The differing chord sagittas are explicitly reported, not called sub-2-mm shapes.
"""
import math
import numpy as np
from shapely.geometry import LineString

LIMIT = .002

def _arc(start, end, mid):
    origin=np.asarray(start,dtype=float);a=np.asarray(end,dtype=float)-origin;b=np.asarray(mid,dtype=float)-origin
    matrix=2*np.array([a,b]);assert abs(np.linalg.det(matrix))>1e-10,'degenerate-circle'
    center=origin+np.linalg.solve(matrix,np.array([a@a,b@b]));radius=float(np.linalg.norm(origin-center))
    angle=lambda p:math.atan2(p[1]-center[1],p[0]-center[0])
    first=angle(start);end_ccw=(angle(end)-first)%(2*math.pi);mid_ccw=(angle(mid)-first)%(2*math.pi)
    direction=1 if mid_ccw<end_ccw else -1;sweep=end_ccw if direction==1 else 2*math.pi-end_ccw
    assert radius>LIMIT and 1e-8<sweep<2*math.pi-1e-8,'invalid-circle-sweep'
    return center,radius,first,direction,sweep

def verify_ring(linear, curve):
    points=np.asarray(linear,dtype=float);assert points.ndim==2 and points.shape[1]==2 and len(points)>=4
    assert np.linalg.norm(points[0]-points[-1])<=1e-8,'open-linear-ring';points=points[:-1]
    assert len(curve)>=4 and isinstance(curve[0],list),'invalid-curve-ring'
    primitives=[];start=curve[0]
    for item in curve[1:]:
        if isinstance(item,list):end=item;kind='line';mid=None
        else:
            assert set(item)=={'c'} and len(item['c'])==2,'unsupported-curve';end,mid=item['c'];kind='circle'
        assert len(start)==len(end)==2 and (mid is None or len(mid)==2)
        assert np.linalg.norm(np.asarray(start)-end)>1e-8,'zero-length-primitive'
        primitives.append((start,end,mid,kind));start=end
    assert np.linalg.norm(np.asarray(start)-curve[0])<=1e-8,'open-curve-ring'
    errors=[]
    for reverse in (False,True):
        try:
            ring=points[::-1] if reverse else points
            anchor=np.asarray(curve[0]);dist=np.linalg.norm(ring-anchor,axis=1);assert int(np.sum(dist<=LIMIT))==1,'ambiguous-start-anchor'
            at=int(np.argmin(dist));ordered=np.concatenate([ring[at:],ring[:at],ring[at:at+1]]);cursor=0;rows=[]
            for primitive_index,(start,end,mid,kind) in enumerate(primitives):
                # First matching endpoint after the previous anchor. Other points
                # may not jump over a required anchor or skip a primitive.
                distances=np.linalg.norm(ordered[cursor+1:]-np.asarray(end),axis=1);found=np.flatnonzero(distances<=LIMIT);assert len(found)>0,f'missing-end-anchor:{primitive_index}:{float(distances.min())}';nearest=int(np.argmin(distances));assert int(np.sum(np.abs(distances-distances[nearest])<1e-10))==1,'ambiguous-exact-end-anchor'
                stop=cursor+1+nearest;chain=ordered[cursor:stop+1];assert len(chain)>=2
                anchor_error=max(float(np.linalg.norm(chain[0]-start)),float(np.linalg.norm(chain[-1]-end)))
                assert anchor_error<=LIMIT,'anchor-error'
                if kind=='line':
                    distance=LineString(chain).hausdorff_distance(LineString([start,end]));assert distance<=LIMIT,f'straight-segment-changed:{primitive_index}:{distance}'
                    vector=np.asarray(end)-start;fractions=(chain-np.asarray(start))@vector/(vector@vector)
                    assert np.all(np.diff(fractions)>=-1e-8) and fractions.min()>=-LIMIT/np.linalg.norm(vector) and fractions.max()<=1+LIMIT/np.linalg.norm(vector),'straight-order-changed'
                    row={'kind':kind,'vertices':len(chain),'anchorErrorM':anchor_error,'lineHausdorffM':float(distance)}
                else:
                    assert len(chain)>=3,'arc-has-no-interior-vertex'
                    center,radius,first,direction,sweep=_arc(start,end,mid)
                    radial=np.abs(np.linalg.norm(chain-center,axis=1)-radius);assert radial.max()<=LIMIT,f'circular-radial-error:{primitive_index}:{float(radial.max())}:{len(chain)}'
                    angles=np.arctan2(chain[:,1]-center[1],chain[:,0]-center[0]);progress=direction*np.unwrap(angles-angles[0]);angle_limit=LIMIT/radius
                    assert abs(progress[0])<1e-8 and abs(progress[-1]-sweep)<=2*angle_limit and np.all(np.diff(progress)>0),'circular-order-or-sweep-changed'
                    steps=np.diff(progress);assert steps.max()<math.pi,'arc-chord-crosses-center'
                    sag=radius*(1-np.cos(steps/2))
                    row={'kind':kind,'vertices':len(chain),'anchorErrorM':anchor_error,'maxRadialErrorM':float(radial.max()),'radiusM':radius,'sweepRadians':sweep,'maxChordSagittaM':float(sag.max()),'representationOnly':True}
                rows.append(row);cursor=stop
            assert cursor==len(ordered)-1,'unconsumed-linear-vertices'
            return {'passed':True,'reversed':reverse,'primitives':rows,'linearVertices':len(linear),'toleranceM':LIMIT}
        except (AssertionError,ValueError,np.linalg.LinAlgError) as e:errors.append(str(e))
    return {'passed':False,'errors':errors,'toleranceM':LIMIT}

def verify_polygon(linear_rings, curve_rings):
    if len(linear_rings)!=len(curve_rings):return {'passed':False,'reason':'ring-count-changed'}
    # Preserve exterior versus hole roles; holes can be reordered only through
    # a unique one-to-one full-ring match.
    results=[];used=set()
    for i,ring in enumerate(curve_rings):
        candidates=[(j,verify_ring(linear_rings[j],ring)) for j in range(len(linear_rings)) if j not in used and (j==0)==(i==0)]
        matches=[(j,r) for j,r in candidates if r['passed']]
        if len(matches)!=1:return {'passed':False,'reason':'no-unique-complete-ring-match','curveRing':i,'candidates':candidates}
        j,result=matches[0];used.add(j);results.append({'linearRing':j,'curveRing':i,**result})
    return {'passed':True,'rings':results,'toleranceM':LIMIT,'qualification':'Same ordered straight primitives and circular arcs at vertices; chord sagittas remain separately reported. No claim of 2mm Hausdorff equality between different chord tessellations.'}
