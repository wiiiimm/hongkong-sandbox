"""UNEXECUTED computed current-parent terrain packing, no building edits.

Reuse immediate Float32 cells and each untouched current parent's own plane.
No mask/domain enlargement by buffer; no acceptance or old approval transfer.
"""
from fractions import Fraction as F
import polyu_face891_outside_float32_cell_enclosure_v1_draft_20261014 as cells


def inside_piece(hit,face,shared_cells,domain):
    assert len(domain)==4 and domain[0]<domain[2]and domain[1]<domain[3]
    domain=tuple(F(v)for v in domain)
    assert all(cells.cell(v)==(v,v)for v in domain),'Parent rectangle boundaries must be exact Float32'
    points=cells.prior.rational_points(hit['polygon']);poly=cells.prior.projected(points)
    origin,normal=cells.source_plane(face)
    assert all(sum(normal[k]*(p[k]-origin[k])for k in range(3))==0 for p in points),'Saved region must belong to this exact current parent plane'
    assert cells.prior.coverage.signed_area(poly)!=0,'Only saved positive-area inside regions; no fabricated degenerate infill'
    assert all(domain[0]<=x<=domain[2]and domain[1]<=z<=domain[3]for x,z in poly)
    result=cells.enclose(poly,face,shared_cells)
    assert all(domain[0]<=x<=domain[2]and domain[1]<=z<=domain[3]for x,z in result['exactFloat32CellEnclosingHull']),'No out-of-parent clipping or silent modification'
    # The legacy reused helper names its target "outside". Preserve its full
    # result while explicitly binding the target to this saved inside polygon.
    return dict(mask=hit['mask'],originalIdealInsidePolygon=points,
        exactComputedParentCellKernelVerbatim=result,
        reusedKernelOutsideFieldNamesDoNotChangeInsideSourceRole=True,
        sourceParentPlaneUsedWithoutOtherLayerY=True,
        completeRegionTargetNotPointSample=True,
        onlyXZImmediateCellsNoArbitraryBuffer=True,
        originalGovernmentBuildingGeometryPoseEdited=False,
        freshExpandedRegionOrdinaryAndAllActorRuntimePending=True,
        geometricCoverageObservationsNotPhysicalAcceptance=True)


def parent_pieces(proof,face,shared_cells,domain,progress):
    assert proof['completeOwnPlanePartition']and not proof.get('projectedVerticalOrZeroPreservedWhole')
    pieces=[];regions=[]
    for ordinal,hit in enumerate(proof['inside']):
        account=inside_piece(hit,face,shared_cells,domain)
        result=account['exactComputedParentCellKernelVerbatim'];normal=result['sourcePlane']['normal']
        for local,t in enumerate(result['triangles']):
            pieces.append(dict(mask=hit['mask'],enclosureInsidePolygon=ordinal,enclosureLocalTriangle=local,
                exactOwnPlanePoints=t['idealSourcePlanePoints'],packedPieceTriplet=t['packedPieceTriplet'],
                exactPackedSourcePlaneResiduals=[v*normal[1]for v in t['exactVerticalSourcePlaneResidualM']],
                exactInsideExpansionAreaM2=result['exactHullExpansionAreaM2'],
                noOtherLayerYUsed=True,packingResidualsMeasuredNotWaived=True))
        regions.append(dict(insidePolygon=ordinal,**account));progress(ordinal+1,len(proof['inside']))
    return pieces,dict(completeSavedInsideRegions=regions,
        completeInsideFirstOwnershipOrderPreserved=True,
        allOutsideAndLiteralPrefixFragmentsRemainUntouched=True,
        differentPackedGeometryFreshQualificationRequired=True,
        heightAdmissionAndDrawObservationsAreDiagnosticOnly=True)
