"""Exact source-plane mask partitions; unchanged split/fan primitives only.

This is private computed terrain nomination, never building geometry or
acceptance. Outside pieces inherit their own input triangle's affine plane.
Current-parent pieces inherit that parent's plane, never another layer's Y.
"""
from fractions import Fraction as F
import numpy as np
from southside_saved_local_core_parent_adapter_v3_20261012 import points,normal,bb,tri_planes,split,old


def serial(v):
    if isinstance(v,F):return str(v)
    if isinstance(v,dict):return {k:serial(q)for k,q in v.items()}
    if isinstance(v,(tuple,list)):return [serial(q)for q in v]
    return v


def masks_from_records(records):
    out=[]
    for r in records:
        t=[(F(p[0]),F(0),F(p[1]))for p in r['exactClosedProjection']]
        assert len(t)==3 and normal(t)[1]!=0
        out.append(dict(lineage=r,triangle=t,bounds=bb(t),planes=tri_planes(t)))
    return out


def verify_saved_packing(ideal, raw):
    exact=points(ideal)
    assert len(exact)==3 and all(len(p)==3 for p in exact)
    saved=np.asarray(raw,dtype='<f8');assert saved.shape==(3,3)and np.isfinite(saved).all()
    packed=np.asarray([[float(v)for v in p]for p in exact],dtype='<f4').astype('<f8')
    assert packed.tobytes()==saved.tobytes(),'exact rational source does not reproduce saved packed facet'
    return True


def protected_literal_declaration(account,facet_count):
    if 'protectedLiteralOutputFacetIDs'not in account:
        return [],dict(declarationPresent=False,authenticatedPriorAccountHasNoProtectedLiteralDeclaration=True,
                       noPriorLiteralProtectionCredit=True,allGovernmentBuildingGeometryImmutable=True,
                       fullSourceAndPhysicalObligationsPending=True)
    ids=account['protectedLiteralOutputFacetIDs']
    assert isinstance(ids,list)and ids==sorted(set(ids))and all(type(i)is int and 0<=i<facet_count for i in ids)
    return ids,dict(declarationPresent=True,declaredProtectedLiteralIDs=ids,
                    onlyExplicitPriorDeclarationUsed=True,noNewAcceptanceCredit=True)


def partition(ideal, masks, *, protected_literal=False):
    face=points(ideal);n=normal(face)
    if n[1]==0:
        return dict(inside=[],outside=[face],projectedVerticalOrZeroPreservedWhole=True,
                    noAffineHeightOrCoverageCredit=True,completeOwnPlanePartition=True)
    axis=max(range(3),key=lambda k:abs(n[k]));required=old.intrinsic_area(face,axis)
    pending=[face];inside=[];relevant=[];bound=bb(face)
    for mi,m in enumerate(masks):
        mb=m['bounds']
        if bound[2]<mb[0]or mb[2]<bound[0]or bound[3]<mb[1]or mb[3]<bound[1]:continue
        relevant.append(mi)
    for mi in relevant:
        m=masks[mi];following=[]
        for poly in pending:
            hit,rest=split(poly,m['planes'],axis);following.extend(rest)
            if old.intrinsic_area(hit,axis):inside.append(dict(mask=mi,polygon=hit))
        pending=following
        if not pending:break
    inside_area=sum((old.intrinsic_area(r['polygon'],axis)for r in inside),F(0))
    outside_area=sum((old.intrinsic_area(p,axis)for p in pending),F(0))
    assert inside_area+outside_area==required
    if protected_literal:assert inside_area==0,'protected literal intersects proposed restoration: unresolved'
    for p in pending+[r['polygon']for r in inside]:
        assert all(sum(n[k]*(v[k]-face[0][k])for k in range(3))==0 for v in p)
    return dict(inside=inside,outside=pending,exactWholeIntrinsicArea=required,
                exactInsideMaskUnionIntrinsicArea=inside_area,exactOutsideMaskUnionIntrinsicArea=outside_area,
                completeRelevantClosedAABBMasks=relevant,allOtherMasksStrictlyClosedAABBDisjoint=True,
                maskFirstOwnershipPreventsDuplicateArea=True,completeOwnPlanePartition=True,
                closedBoundariesRetained=True,noGEOSToleranceOrBuffer=True)


def packed_pieces(polygons, ideal):
    face=points(ideal);n=normal(face);out=[]
    for poly in polygons:
        for triangle in old.fan(poly):
            assert all(sum(n[k]*(v[k]-face[0][k])for k in range(3))==0 for v in triangle)
            packed=np.asarray([[float(v)for v in p]for p in triangle],dtype='<f4').astype('<f8')
            assert np.isfinite(packed).all()
            residual=[sum(n[k]*(F(float(p[k]))-face[0][k])for k in range(3))for p in packed]
            out.append(dict(exactOwnPlanePoints=triangle,packedPieceTriplet=packed.tolist(),
                            exactPackedSourcePlaneResiduals=residual,
                            packingResidualsMeasuredNotWaived=True,noOtherLayerYUsed=True))
    return out
