"""Computed terrain only: exact bad-region exclusion and new-piece compatibility."""
from fractions import Fraction as F
import numpy as np
from polyu_face891_outside_float32_cell_enclosure_v1_draft_20261014 import cell,convex_hull,source_plane,enclose
from upton_six_basic_preserved_ground_feasibility_v1_20261012 import masked_current_pair,projected_mask

def forbidden_projection(proof):
    """Closed conservative projection of source gap <= -.5 in saved convex pair."""
    assert proof['violatesExistingOrdinaryBound']and proof['existingOrdinaryLowerBoundM']=='-1/2'
    poly=[tuple(F(v)for v in r['exactOriginalSourcePoint'])+(F(r['exactGapM'])+F(1,2),)
          for r in proof['completeConvexMaskedPairVertices']]
    assert poly and min(v[3]for v in poly)<0
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ia,ib=a[3]<=0,b[3]<=0
        if ia:out.append(a)
        if ia!=ib:
            t=a[3]/(a[3]-b[3]);out.append(tuple(a[k]+t*(b[k]-a[k])for k in range(4)))
    points=sorted(set((v[0],v[2])for v in out));assert points
    return points

def strictly_enclosing_f32_hull(points):
    """Immediate representable cells, not an arbitrary physical-distance buffer."""
    corners=[];cells=[]
    for x,z in points:
        row=[]
        for value in [x,z]:
            lo,hi=cell(value)
            if lo==value:lo=F(float(np.nextafter(np.float32(float(lo)),np.float32(-np.inf))))
            if hi==value:hi=F(float(np.nextafter(np.float32(float(hi)),np.float32(np.inf))))
            assert lo<F(value)<hi;row.append((lo,hi))
        (xl,xh),(zl,zh)=row;corners.extend([(xl,zl),(xl,zh),(xh,zl),(xh,zh)])
        cells.append(dict(sourceXZ=list(map(str,(x,z))),strictXCell=list(map(str,(xl,xh))),strictZCell=list(map(str,(zl,zh)))))
    hull=convex_hull(corners)
    cross=lambda a,b,p:(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
    assert all(cross(a,b,p)>0 for a,b in zip(hull,hull[1:]+hull[:1])for p in points)
    return hull,cells

def downward_parent_pieces(poly,parent,shared_cells):
    """Same own-plane XZ enclosure; floor Y at actual packed XZ, never lift above parent."""
    a,n=source_plane(parent);result=enclose([(p[0],p[2])for p in poly],parent,shared_cells);pieces=[]
    for row in result['triangles']:
        triangle=[];residual=[]
        for px,_,pz in row['packedPieceTriplet']:
            x,z=F(px),F(pz);height=a[1]-(n[0]*(x-a[0])+n[2]*(z-a[2]))/n[1]
            y=np.float32(float(height))
            if F(float(y))>height:y=np.nextafter(y,np.float32(-np.inf))
            assert np.isfinite(y)and F(float(y))<=height
            triangle.append([px,float(y),pz]);residual.append(str(F(float(y))-height))
        pieces.append(dict(packedTriplet=triangle,exactOwnParentPlanePackingResidualM=residual,
                           packedYNotAboveOwnAuthenticatedParentPlane=True))
    return pieces

def compatible_piece(triangle,worlds):
    """Complete unchanged worlds, inclusive bounds then existing exact ordinary kernel."""
    g=np.asarray(triangle,dtype='<f8');xz=g[:,[0,2]];mask=projected_mask(g)
    if len(set(mask))<3 or sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(mask,mask[1:]+mask[:1]))==0:
        return dict(eligible=False,collapsedProjectedPiece=True,noHeightOrSupportCredit=True)
    rows=[];failed=False
    for mode,(world,lo,hi,world_sha)in worlds.items():
        ids=np.flatnonzero(np.all(hi>=xz.min(0),1)&np.all(lo<=xz.max(0),1));pairs=[]
        for i in ids:
            proof=masked_current_pair(world[i],g,mask)
            pairs.append(dict(sourceFace=int(i),proof=proof))
            failed=failed or proof.get('violatesExistingOrdinaryBound',False)
        rows.append(dict(arithmetic=mode,wholeSourceWorldSHA256=world_sha,completeSourceFaceCount=len(world),
                         closedAABBCandidateIDs=ids.tolist(),allOtherFacesStrictlyClosedAABBDisjoint=True,completeRelevantPairs=pairs))
    return dict(eligible=not failed,worlds=rows,existingOrdinaryLowerBoundM='-1/2',
                skippedNegativePiecesAreNotSourceCorruptionOrAcceptance=True,noRootOrRoleCredit=True)
