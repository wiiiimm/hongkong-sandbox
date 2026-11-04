"""UNEXECUTED exact new parent-cell mesh/pointer/account binding only."""
from fractions import Fraction as F
import json
import numpy as np
from polyu_five_mask_source_plane_partition_v1_20261014 import verify_saved_packing
from polyu_face891_outside_float32_cell_enclosure_v1_draft_20261014 import source_plane

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def points(v):return [tuple(F(x)for x in p)for p in v]
def bytes3(v):return np.asarray(v,dtype='<f8').tobytes()

def validate_region(region,hit,face,ordinal,domain):
    assert type(region['insidePolygon'])is int and type(region['mask'])is int and type(hit['mask'])is int
    assert region['insidePolygon']==ordinal and region['mask']==hit['mask']
    target=points(hit['polygon']);assert points(region['originalIdealInsidePolygon'])==target
    assert region['reusedKernelOutsideFieldNamesDoNotChangeInsideSourceRole']and region['sourceParentPlaneUsedWithoutOtherLayerY']
    k=region['exactComputedParentCellKernelVerbatim'];a,n=source_plane(face)
    assert tuple(F(v)for v in k['sourcePlane']['origin'])==a and tuple(F(v)for v in k['sourcePlane']['normal'])==n
    assert [tuple(F(v)for v in p)for p in k['originalIdealOutsidePolygon']]==[(p[0],p[2])for p in target]
    assert all(sum(n[j]*(p[j]-a[j])for j in range(3))==0 for p in target)
    hull=[tuple(F(v)for v in p)for p in k['exactFloat32CellEnclosingHull']]
    assert all(F(domain[0])<=x<=F(domain[2])and F(domain[1])<=z<=F(domain[3])for x,z in hull)
    for p in hull:assert np.asarray(p,dtype='<f8').tobytes()==np.asarray(p,dtype='<f4').astype('<f8').tobytes()
    assert len(k['triangles'])==len(hull)-2
    for i,t in enumerate(k['triangles']):
        ideal=points(t['idealSourcePlanePoints']);assert [(p[0],p[2])for p in ideal]==[hull[0],hull[i+1],hull[i+2]]
        assert all(sum(n[j]*(p[j]-a[j])for j in range(3))==0 for p in ideal)
        packed=t['packedPieceTriplet'];assert verify_saved_packing(ideal,packed)
        observed=points(packed);residual=[sum(n[j]*(p[j]-a[j])for j in range(3))/n[1]for p in observed]
        assert residual==[F(v)for v in t['exactVerticalSourcePlaneResidualM']]
    return k

def validate_piece(p,row,raw,records,face_ids=None):
    pointer=p['partitionProofReference'];i=row['capturedParentFacet']
    assert type(i)is int and type(pointer['capturedParentFacet'])is int and type(p['candidateFace'])is int
    assert pointer==dict(mapping='completeCapturedParentMapping',capturedParentFacet=i)
    if face_ids is None:face_ids=frozenset(row['newCandidateFaces'])
    assert 'partitionProof'not in p and p['candidateFace']in face_ids
    assert p['kind']=='capturedCurrentParentOwnPlaneFloat32CellInsideEligibleMasks'
    assert p['ancestor']['capturedParentFacet']==i and bytes3(p['ancestor']['wholeOriginalCapturedParentTriplet'])==bytes3(row['wholeOriginalCapturedParentTriplet'])
    q=p['computedInsideCellEnclosure'];regions=row['completeComputedInsideEnclosureAccount']['completeSavedInsideRegions']
    ordinal=q['enclosureInsidePolygon'];local=q['enclosureLocalTriangle']
    assert type(ordinal)is int and 0<=ordinal<len(regions)
    r=regions[ordinal];k=r['exactComputedParentCellKernelVerbatim'];assert type(local)is int and 0<=local<len(k['triangles'])
    assert type(r['mask'])is int and 0<=r['mask']<len(records)and type(p['mask']['mask'])is int
    t=k['triangles'][local]
    assert p['mask']==dict(mask=r['mask'],completeMaskLineage=records[r['mask']])
    assert points(p['exactOwnPlanePoints'])==points(t['idealSourcePlanePoints'])and raw.tobytes()==bytes3(t['packedPieceTriplet'])
    assert F(q['exactInsideExpansionAreaM2'])==F(k['exactHullExpansionAreaM2'])
    normal=[F(v)for v in k['sourcePlane']['normal']]
    assert [F(v)for v in p['exactPackedSourcePlaneResiduals']]==[F(v)*normal[1]for v in t['exactVerticalSourcePlaneResidualM']]
    assert p['noOtherLayerYUsed']and p['packingResidualsMeasuredNotWaived']and p['freshQualificationRequired']
    return ordinal,local

def validate_binding(nom,previous,records,domain):
    assert nom['schema']=='private-source-plane-preserving-five-current-parent-mask-parent-cell-nomination-v4'
    assert previous['schema']=='private-source-plane-preserving-five-current-parent-mask-nomination-v3'
    assert len(records)==5553 and len(previous['candidateFaceProvenance'])==55305
    assert len(nom['completeOldPrivateMapping'])==3214 and len(nom['completeCapturedParentMapping'])==12
    assert canonical(nom['completeOldPrivateMapping'])==canonical(previous['completeOldPrivateMapping'])
    assert canonical(nom['candidateFaceProvenance'][:8011])==canonical(previous['candidateFaceProvenance'][:8011])
    mesh=nom['newNativeMesh'];oldmesh=previous['newNativeMesh'];position=np.asarray(mesh['position'],dtype='<f8');index=np.asarray(mesh['index'],dtype=np.int64)
    assert position.ndim==index.ndim==1 and len(position)%3==len(index)%3==0 and np.isfinite(position).all()
    assert all(type(i)is int for i in mesh['index'])and index.min()>=0 and index.max()<len(position)//3
    assert position.tobytes()==position.astype('<f4').astype('<f8').tobytes()
    assert position[:len(oldmesh['position'])].tobytes()==bytes3(oldmesh['position'])
    assert mesh['index'][:8011*3]==oldmesh['index'][:8011*3]
    raw=position.reshape(-1,3)[index.reshape(-1,3)];oldraw=np.asarray(oldmesh['position'],dtype='<f8').reshape(-1,3)[np.asarray(oldmesh['index'],dtype=np.int64).reshape(-1,3)]
    assert raw[:8011].tobytes()==oldraw[:8011].tobytes()
    assert len(raw)==len(nom['candidateFaceProvenance'])and [p['candidateFace']for p in nom['candidateFaceProvenance']]==list(range(len(raw)))
    assigned=[j for r in nom['completeOldPrivateMapping']for j in r['newCandidateFaces']];assert assigned==list(range(8011))
    for i,row in enumerate(nom['completeCapturedParentMapping']):
        old=previous['completeCapturedParentMapping'][i];assert row['capturedParentFacet']==old['capturedParentFacet']==i
        assert type(row['capturedParentFacet'])is int and type(old['capturedParentFacet'])is int
        assert canonical(row['previousV3MappingVerbatim'])==canonical(old)
        assert bytes3(row['wholeOriginalCapturedParentTriplet'])==bytes3(old['wholeOriginalCapturedParentTriplet'])
        assert canonical(row['completeExactMaskPartition'])==canonical(old['completeExactMaskPartition'])
        proof=row['completeExactMaskPartition'];regions=row['completeComputedInsideEnclosureAccount']['completeSavedInsideRegions']
        assert len(regions)==len(proof['inside'])
        expected=[]
        for ordinal,(r,hit)in enumerate(zip(regions,proof['inside'])):
            k=validate_region(r,hit,row['wholeOriginalCapturedParentTriplet'],ordinal,domain)
            expected.extend((ordinal,j)for j in range(len(k['triangles'])))
        actual=[];face_ids=frozenset(row['newCandidateFaces'])
        for j in row['newCandidateFaces']:
            assert type(j)is int and 8011<=j<len(raw);assigned.append(j)
            actual.append(validate_piece(nom['candidateFaceProvenance'][j],row,raw[j],records,face_ids))
        assert actual==expected,'complete ordered inside pieces, no subset, duplicate or swapped ancestor'
    assert assigned==list(range(len(raw)))
    assert sum(len(r['completeExactMaskPartition']['inside'])for r in nom['completeCapturedParentMapping'])==24448
    assert nom['all8011PreviousPackedFacetsUnchanged']and nom['all3214OldMappingsVerbatim']and not nom['physicalAccepted']and not nom['installationApproved']
    assert 'sourceOverlap'not in mesh and len(mesh)==2
    return raw
