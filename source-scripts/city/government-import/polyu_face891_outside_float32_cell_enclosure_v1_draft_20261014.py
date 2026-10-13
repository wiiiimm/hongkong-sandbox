"""UNEXECUTED bounded source-plane terrain nomination; not model geometry.

Exact enclosing Float32 cells replace nearest-node undercoverage for saved
outside polygons only. New overlaps/packing need fresh candidate qualification.
"""
from fractions import Fraction as F
import numpy as np
import polyu_face891_saved_packed_closed_coverage_v1_draft_20261014 as prior


def cell(value):
    value=F(value);nearest=np.float32(float(value));assert np.isfinite(nearest)
    observed=F(float(nearest))
    if observed==value:lower=upper=nearest
    elif observed<value:lower=nearest;upper=np.nextafter(nearest,np.float32(np.inf))
    else:lower=np.nextafter(nearest,np.float32(-np.inf));upper=nearest
    assert np.isfinite(lower)and np.isfinite(upper)
    lo,hi=F(float(lower)),F(float(upper));assert lo<=value<=hi
    if lo!=hi:assert np.nextafter(lower,np.float32(np.inf))==upper
    return lo,hi


def convex_hull(points):
    points=sorted(set(points));assert len(points)>=3
    def half(values):
        result=[]
        for p in values:
            while len(result)>=2 and prior.coverage.cross(result[-2],result[-1],p)<=0:result.pop()
            result.append(p)
        return result
    hull=half(points)[:-1]+half(list(reversed(points)))[:-1]
    assert len(hull)>=3 and prior.coverage.signed_area(hull)>0
    return hull


def source_plane(face):
    a,b,c=prior.rational_points(face)
    u=[b[k]-a[k]for k in range(3)];v=[c[k]-a[k]for k in range(3)]
    n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
    assert n[1]!=0,'Vertical/zero source has no affine height; no infill nomination'
    return a,n


def enclose(poly,face,shared_cells):
    a,n=source_plane(face);corners=[];cell_rows=[]
    for x,z in poly:
        key=(x,z)
        if key not in shared_cells:shared_cells[key]=(cell(x),cell(z))
        (xl,xh),(zl,zh)=shared_cells[key]
        corners.extend([(xl,zl),(xl,zh),(xh,zl),(xh,zh)])
        cell_rows.append(dict(originalXZ=key,xCell=(xl,xh),zCell=(zl,zh)))
    hull=convex_hull(corners)
    assert all(prior.coverage.cross(p,q,v)>=0 for p,q in zip(hull,hull[1:]+hull[:1])for v in poly)
    lifted=[(x,a[1]-(n[0]*(x-a[0])+n[2]*(z-a[2]))/n[1],z)for x,z in hull]
    assert all(sum(n[k]*(p[k]-a[k])for k in range(3))==0 for p in lifted)
    triangles=[];rows=[];residuals=[]
    for i in range(1,len(lifted)-1):
        ideal=[lifted[0],lifted[i],lifted[i+1]]
        packed=np.asarray([[float(v)for v in p]for p in ideal],dtype='<f4').astype('<f8')
        assert np.isfinite(packed).all()
        exact=prior.rational_points(packed.tolist());xz=prior.projected(exact)
        # XZ hull corners are already Float32: only Y is newly rounded here.
        assert xz==[hull[0],hull[i],hull[i+1]]
        residual=[sum(n[k]*(p[k]-a[k])for k in range(3))/n[1]for p in exact]
        triangles.append(dict(idealSourcePlanePoints=ideal,packedPieceTriplet=packed.tolist(),
                              exactVerticalSourcePlaneResidualM=residual))
        determinant=prior.production_determinant(packed.tolist())
        rows.append(dict(id=i-1,points=xz,bound=prior.bounds(xz),
            collapsed=prior.exact_zero_3d(exact),projectedPositive=bool(prior.coverage.signed_area(xz)),
            productionDeterminant=determinant,heightAdmitted=abs(determinant)>=1e-10))
        residuals.extend(residual)
    drawn=prior.closed_coverage(poly,rows)
    admitted=prior.closed_coverage(poly,[r for r in rows if r['heightAdmitted']])
    return dict(originalIdealOutsidePolygon=poly,exactFloat32CellEnclosingHull=hull,
        sharedNodeCells=cell_rows,sourcePlane= dict(origin=a,normal=n),triangles=triangles,
        completePackedFacetDescriptors=rows,
        exactHullExpansionAreaM2=abs(prior.coverage.signed_area(hull))-abs(prior.coverage.signed_area(poly)),
        exactDrawnOutsideProjection=drawn,exactHeightAdmittedOutsideProjection=admitted,
        maxAbsVerticalPackingResidualM=max(map(abs,residuals),default=F(0)),
        packedGeometryChanged=True,expandedCurrentProtectedRegionCompatibilityPending=True,
        originalBuildingGeometryPoseEdited=False,noArbitraryBuffer=True,noAcceptance=True)


def nominate(packet,outside_findings,progress):
    assert len(outside_findings)==143
    assert [r['id']for r in outside_findings]==list(range(143))
    face=packet['sourceFaceLineageVerbatim']['exactProposedPoints']
    shared={};results=[]
    for i,(polygon,old)in enumerate(zip(packet['exactIdealPartition']['outside'],outside_findings)):
        poly=prior.projected(prior.rational_points(polygon))
        assert poly==[tuple(F(v)for v in p)for p in old['points']]
        result=dict(region=i,priorPackedPieceIDs=old['packedPieceIDs'],
                    priorCompleteOutsideFinding=old,**enclose(poly,face,shared))
        results.append(result);progress(dict(outsideRegionsCompleted=len(results),totalOutsideRegions=143),result)
    return dict(complete=True,scope='ONE face891,143 source-outside Float32-cell nominations only',
        regions=results,sharedIdealVertexCellCount=len(shared),
        allOutsideDrawnClosedProjectionCovered=all(r['exactDrawnOutsideProjection']['completeClosedXZCovered']for r in results),
        allOutsideHeightAdmittedClosedProjectionCovered=all(r['exactHeightAdmittedOutsideProjection']['completeClosedXZCovered']for r in results),
        sourcePlaneBeforeStoragePreserved=True,sourceLayersMerged=False,
        newProtectedOverlapOrdinaryHeightMAXRuntimeAndFullCandidateCoveragePending=True,
        insideSourceShadowsNotContinued=True,fullCandidateConstructed=False,
        physicalAccepted=False,installationApproved=False,sourceGeometryPoseEdited=False)
