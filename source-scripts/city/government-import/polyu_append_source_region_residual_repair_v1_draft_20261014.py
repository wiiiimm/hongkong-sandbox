"""UNEXECUTED append-only own-plane terrain nominee from saved source regions."""
from fractions import Fraction as F
import numpy as np
import exact_original_projection_coverage_v2_20261010 as clipping
import polyu_face891_outside_float32_cell_enclosure_v1_draft_20261014 as cells

LEGACY={'previousPrivateOwnPlaneOutsideEligibleMasks','unchangedPreviousPrivateDraw'}

def select_targets(attribution,nom):
    selected={};contradictions=[];not_selected=[]
    old=nom['completeOldPrivateMapping'];prov=nom['candidateFaceProvenance']
    for region in attribution['regions']:
        if region['kind']!='missing':continue
        if region['GEOSRepresentativeDiagnosticPoint']['nativeClosedMembership']['closedMembers']:
            contradictions.append(region['region']);continue
        families=set()
        for q in region['completeClosedBBoxNominations']:
            j=q['candidateFace'];assert type(j)is int and 0<=j<len(prov)and prov[j]['candidateFace']==j
            p=prov[j]
            if p['kind']not in LEGACY:continue
            i=p.get('oldPrivateFace',p.get('ancestor',{}).get('oldPrivateFace'))
            assert type(i)is int and 0<=i<len(old)and old[i]['oldPrivateFace']==i
            assert j in old[i]['newCandidateFaces']
            # Already-enclosed families get no identical enclosure replay.
            if old[i].get('computedOutsideEnclosureAccount'):continue
            families.add(i)
        bounds=[F(v)for v in region['absoluteXZBounds']];found=0
        for i in sorted(families):
            row=old[i];proof=row['completeExactMaskPartition']
            if proof.get('projectedVerticalOrZeroPreservedWhole'):
                not_selected.append(dict(region=region['region'],oldPrivateFace=i,reason='saved zero/vertical has no new ground-height credit'));continue
            assert proof['completeOwnPlanePartition']
            for ordinal,poly in enumerate(proof['outside']):
                pts=cells.prior.rational_points(poly);xz=cells.prior.projected(pts)
                lower=(min(p[0]for p in xz),min(p[1]for p in xz));upper=(max(p[0]for p in xz),max(p[1]for p in xz))
                if upper[0]<bounds[0]or upper[1]<bounds[1]or lower[0]>bounds[2]or lower[1]>bounds[3]:continue
                key=(i,ordinal);found+=1
                if key not in selected:selected[key]=dict(oldPrivateFace=i,outsidePolygon=ordinal,
                    completeIdealOutsidePolygon=poly,ownProposedPlane=row['previousLineageVerbatim']['exactProposedPoints'],
                    previousLineageVerbatim=row['previousLineageVerbatim'],locatorRegions=[],
                    sourcePointer=dict(mapping='completeOldPrivateMapping',oldPrivateFace=i,field='completeExactMaskPartition.outside',outsidePolygon=ordinal),
                    completeSourceRegionNotGEOSGapVertices=True)
                selected[key]['locatorRegions'].append(region['region'])
        if not found:not_selected.append(dict(region=region['region'],reason='no legacy exact-region closed-bound nomination; no invented repair'))
    return [selected[k]for k in sorted(selected)],dict(contradictoryCoveredRepresentativeRegions=contradictions,
        unresolvedOrUncreditedLocators=not_selected,alreadyCellEnclosedParentAndOutsideNotRepacked=True,
        noPointFitNearestPlaneBufferOrAcceptance=True)

def enclose_target(target,domain,shared):
    domain=tuple(F(v)for v in domain);assert all(cells.cell(v)==(v,v)for v in domain)
    source=cells.prior.rational_points(target['completeIdealOutsidePolygon']);face=target['ownProposedPlane'];a,n=cells.source_plane(face)
    assert all(sum(n[k]*(p[k]-a[k])for k in range(3))==0 for p in source)
    xz=cells.prior.projected(source);original=xz
    x0,z0,x1,z1=domain;rectangle=[(x0,z0),(x1,z0),(x1,z1),(x0,z1)]
    for p,q in zip(rectangle,rectangle[1:]+rectangle[:1]):xz=clipping.clip(xz,p,q,True)
    if not clipping.signed_area(xz):return dict(target=target,noPositiveRestrictedSourceRegion=True,noInfillOrAcceptance=True)
    result=cells.enclose(xz,face,shared)
    assert all(x0<=x<=x1 and z0<=z<=z1 for x,z in result['exactFloat32CellEnclosingHull'])
    return dict(target=target,completeOriginalSourceProjection=original,exactSourceRegionRestrictedToParentRectangle=xz,
        exactOwnPlaneCellEnclosure=result,noGEOSCoordinateUsedForConstruction=True,
        planeIsRecordedProposedComputePlaneNotRelabelledUntouchedGovernmentY=True,
        noOtherLayerHeightUsed=True,freshGeometryQualificationPending=True)

def append_pieces(mesh,accounts):
    positions=list(mesh['position']);index=list(mesh['index']);old_raw=np.asarray(positions,dtype='<f8').reshape(-1,3)[np.asarray(index,dtype=np.int64).reshape(-1,3)]
    existing={t.tobytes()for t in old_raw};appended=[];representation=[]
    for account in accounts:
        if account.get('noPositiveRestrictedSourceRegion'):continue
        result=account['exactOwnPlaneCellEnclosure']
        for local,t in enumerate(result['triangles']):
            raw=np.asarray(t['packedPieceTriplet'],dtype='<f8');key=raw.tobytes()
            if key in existing:
                representation.append(dict(sourcePointer=account['target']['sourcePointer'],localTriangle=local,exactXYZAlreadyPresent=True,noNewAcceptanceCredit=True));continue
            j=len(index)//3;start=len(positions)//3;positions.extend(v for p in t['packedPieceTriplet']for v in p);index.extend(range(start,start+3));existing.add(key)
            appended.append(dict(candidateFace=j,kind='appendedLegacyExactSourceRegionOwnPlaneCellEnclosure',sourcePointer=account['target']['sourcePointer'],
                localTriangle=local,completeIdealSourcePlanePoints=t['idealSourcePlanePoints'],packedTriplet=t['packedPieceTriplet'],
                exactVerticalSourcePlaneResidualM=t['exactVerticalSourcePlaneResidualM'],locatorRegions=account['target']['locatorRegions'],
                originalBuildingGeometryPoseUnchanged=True,physicalAccepted=False))
    assert np.asarray(positions[:len(mesh['position'])],dtype='<f8').tobytes()==np.asarray(mesh['position'],dtype='<f8').tobytes()
    assert index[:len(mesh['index'])]==mesh['index']
    return dict(position=positions,index=index),dict(appendedFaces=appended,exactExistingRepresentations=representation,
        allOldPositionsIncludingUnusedAndIndicesUnchanged=True,previousFullMappingRemainsAtBoundReference=True,
        noOriginalLayerDeletionOrApprovalTransfer=True,allExpandedRegionAndActualQualificationPending=True)
