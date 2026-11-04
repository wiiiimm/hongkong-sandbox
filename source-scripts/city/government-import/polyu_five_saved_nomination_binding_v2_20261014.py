"""V3 saved mesh/provenance binding; no source/ground clearance or approval."""
from fractions import Fraction as F
import numpy as np
from polyu_five_mask_source_plane_partition_v1_20261014 import verify_saved_packing


def resolve_partition(nom,p):
    pointer=p.get('partitionProofReference')
    if pointer is None:
        assert 'partitionProof'in p
        return p['partitionProof']
    assert 'partitionProof'not in p and isinstance(pointer,dict)
    if pointer['mapping']=='completeOldPrivateMapping':
        assert set(pointer)=={'mapping','oldPrivateFace'}
        i=pointer['oldPrivateFace'];assert type(i)is int and 0<=i<len(nom['completeOldPrivateMapping'])
        row=nom['completeOldPrivateMapping'][i]
        assert row['oldPrivateFace']==i and p['ancestor']['oldPrivateFace']==i
    else:
        assert pointer['mapping']=='completeCapturedParentMapping'and set(pointer)=={'mapping','capturedParentFacet'}
        i=pointer['capturedParentFacet'];assert type(i)is int and 0<=i<len(nom['completeCapturedParentMapping'])
        row=nom['completeCapturedParentMapping'][i]
        assert row['capturedParentFacet']==i and p['ancestor']['capturedParentFacet']==i
    assert p['candidateFace']in row['newCandidateFaces']
    return row['completeExactMaskPartition']


def points(values):return [tuple(F(v)for v in p)for p in values]


def validate_binding(nom,patch,lineage,parents):
    assert nom['schema']=='private-source-plane-preserving-five-current-parent-mask-nomination-v3'
    old_pos=patch['nativeMesh']['position'];old_idx=patch['nativeMesh']['index'];mesh=nom['newNativeMesh']
    assert mesh['position'][:len(old_pos)]==old_pos and nom['oldPositionBufferRetainedIncludingUnusedVertices']
    pos=np.asarray(mesh['position'],dtype='<f8');idx=np.asarray(mesh['index'],dtype=np.int64)
    assert pos.ndim==1 and len(pos)%3==0 and idx.ndim==1 and len(idx)%3==0 and np.isfinite(pos).all()
    assert all(type(i)is int for i in mesh['index'])and idx.min()>=0 and idx.max()<len(pos)//3
    raw=pos.reshape(-1,3)[idx.reshape(-1,3)];assert raw.tobytes()==raw.astype('<f4').astype('<f8').tobytes()
    old_raw=np.asarray(old_pos,dtype='<f8').reshape(-1,3)[np.asarray(old_idx,dtype=np.int64).reshape(-1,3)]
    provenance=nom['candidateFaceProvenance'];assert len(provenance)==len(raw)and [r['candidateFace']for r in provenance]==list(range(len(raw)))
    oldmap=nom['completeOldPrivateMapping'];parentmap=nom['completeCapturedParentMapping'];assert len(oldmap)==len(old_raw)==len(lineage)
    assert [r['oldPrivateFace']for r in oldmap]==list(range(len(old_raw)))and [r['capturedParentFacet']for r in parentmap]==list(range(len(parents)))
    assigned=[]
    for r in oldmap:
        i=r['oldPrivateFace'];assert np.asarray(r['wholeOldRawTriplet'],dtype='<f8').tobytes()==old_raw[i].tobytes()and r['previousLineageVerbatim']==lineage[i]
        assert r['removedFragmentsRemainInSourceInventory']and r['completeExactMaskPartition']['completeOwnPlanePartition']
        for j in r['newCandidateFaces']:
            assert type(j)is int and 0<=j<len(raw);assigned.append(j);p=provenance[j]
            if p['kind']=='unchangedPreviousPrivateDraw':
                assert 'partitionProofReference'not in p
                assert p['oldPrivateFace']==i and p['previousLineageVerbatim']==lineage[i]
                assert mesh['index'][3*j:3*j+3]==old_idx[3*i:3*i+3]and raw[j].tobytes()==old_raw[i].tobytes()
            else:
                assert p['kind']in ['previousPrivateOwnPlaneOutsideEligibleMasks','previousPrivateOwnPlaneFloat32CellOutsideEligibleMasks']
                assert p['ancestor']['oldPrivateFace']==i and p['ancestor']['previousLineageVerbatim']==lineage[i]
                assert resolve_partition(nom,p)==r['completeExactMaskPartition']
                assert p['noOtherLayerYUsed']and p['packingResidualsMeasuredNotWaived'];verify_saved_packing(p['exactOwnPlanePoints'],raw[j])
                if p['kind']=='previousPrivateOwnPlaneFloat32CellOutsideEligibleMasks':
                    assert 'partitionProofReference'in p
                    q=p['computedOutsideCellEnclosure'];a=r['computedOutsideEnclosureAccount']['completeComputedOutsidePolygonAccounting']
                    k=q['enclosureOutsidePolygon'];t=q['enclosureLocalTriangle']
                    assert type(k)is int and 0<=k<len(a)and a[k]['outsidePolygon']==k
                    triangles=a[k]['triangles'];assert type(t)is int and 0<=t<len(triangles)
                    expected=triangles[t]
                    assert points(p['exactOwnPlanePoints'])==points(expected['idealSourcePlanePoints'])
                    assert np.asarray(expected['packedPieceTriplet'],dtype='<f8').tobytes()==raw[j].tobytes()
                    assert F(q['exactOutsideExpansionAreaM2'])==F(a[k]['exactHullExpansionAreaM2'])
                    assert q['packedGeometryChangedFreshQualificationRequired']
    for r in parentmap:
        i=r['capturedParentFacet'];assert np.asarray(r['wholeOriginalCapturedParentTriplet'],dtype='<f8').tobytes()==np.asarray(parents[i],dtype='<f8').tobytes()
        assert r['completeExactMaskPartition']['completeOwnPlanePartition']
        for j in r['newCandidateFaces']:
            assert type(j)is int and 0<=j<len(raw);assigned.append(j);p=provenance[j]
            assert p['kind']=='capturedCurrentParentInsideEligibleMasks'and p['ancestor']['capturedParentFacet']==i
            assert 'partitionProofReference'in p and resolve_partition(nom,p)==r['completeExactMaskPartition']
            assert np.asarray(p['ancestor']['wholeOriginalCapturedParentTriplet'],dtype='<f8').tobytes()==np.asarray(parents[i],dtype='<f8').tobytes()
            assert p['noOtherLayerYUsed']and p['packingResidualsMeasuredNotWaived'];verify_saved_packing(p['exactOwnPlanePoints'],raw[j])
    assert sorted(assigned)==list(range(len(raw))),'all new facets exactly once, including restored parents'
    return raw
