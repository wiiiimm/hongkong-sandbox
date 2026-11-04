"""UNEXECUTED exact saved point attribution; no geometry/guard changes."""
from fractions import Fraction as F
import numpy as np
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from polyu_nine_basic_saved_height_context_draft_v1_20261013 import complete_closed_projection_member,exact_plane_height,xz_cross,on_segment
from polyu_face891_saved_packed_closed_coverage_v1_draft_20261014 import production_determinant


def point(values):return tuple(F(v)for v in values)


def convex_member(xz,poly):
    p=[(F(v[0]),F(v[2]))for v in poly]
    area=sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(p,p[1:]+p[:1]))
    if not area:
        return any(on_segment(a,b,xz)for a,b in zip(p,p[1:]+p[:1]))
    return all(xz_cross(a,b,xz)*area>=0 for a,b in zip(p,p[1:]+p[:1]))


def raw_ring_location(xz,rings):
    def locate(ring):
        vertices=[point(v[:2])for v in ring];inside=False
        for a,b in zip(vertices,vertices[1:]+vertices[:1]):
            if on_segment(a,b,xz):return 'boundary'
            if (a[1]>xz[1])!=(b[1]>xz[1]):
                crossing=a[0]+(xz[1]-a[1])*(b[0]-a[0])/(b[1]-a[1])
                if xz[0]<crossing:inside=not inside
        return 'inside'if inside else'outside'
    locations=[locate(r)for r in rings]
    return dict(ringLocations=locations,closedRawGISSupport=bool(locations and
        (any(q=='boundary'for q in locations)or locations[0]=='inside'and not any(q=='inside'for q in locations[1:]))))


def probe(xz,ground,complete=None,native_admission=False):
    a=np.asarray(ground,dtype='<f8');assert a.ndim==3 and a.shape[1:]==(3,3)and np.isfinite(a).all()
    if not len(a):return dict(completeFaces=0,selection=None,closedMembers=[],admittedNativeMembers=[])
    complete=complete or CompleteGround(a);ids,binding=complete.select([(xz[0],F(0),xz[1])]);rows=[]
    for i in ids:
        t=a[int(i)].tolist()
        if not complete_closed_projection_member(xz,t):continue
        determinant=production_determinant(t)
        height=exact_plane_height(xz,t)
        rows.append(dict(face=int(i),triplet=t,closedProjectedSetMember=True,
            exactAffineHeightM=str(height)if height is not None else None,
            productionBinary64Determinant=determinant,
            nativeHeightIndexAdmitted=bool(height is not None and abs(determinant)>=1e-10),
            zeroOrVerticalProjectionReceivesNoHeightCredit=height is None))
    return dict(completeFaces=len(a),selection=binding,closedMembers=rows,
        admittedNativeMembers=[r for r in rows if r['nativeHeightIndexAdmitted']]if native_admission else None,
        nativeAdmissionFlagOnlyAppliesToNativeTerrainSurface=native_admission,
        noBufferOrNegativeBarycentricTolerance=True,noWholeCoverageOrMAXClaim=True)
