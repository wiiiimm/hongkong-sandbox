"""UNEXECUTED hard-bounded face891 fixture; never a full constructor or worker.

Only the first1..16 relevant exact-unique masks may be compared. All539 unique /
2415 occurrence masks remain an explicit full-context obligation. No source
bytes are decoded, no candidate file is written, no DB/lease is used.
"""
from pathlib import Path
from fractions import Fraction as F
import gzip,hashlib,json,sys,time
import numpy as np
import polyu_five_mask_source_plane_partition_fast_v1_20261014 as v2
import polyu_five_mask_positive_hit_partition_v3_draft_20261014 as v3
from test_polyu_five_mask_positive_hit_partition_v3_draft_20261014 import difference_area,closed_segment_covered

ROOT=Path(__file__).resolve().parents[3]
PROPOSAL=ROOT/'docs/astra-city/government-import/government-xl-polyu-positive-hit-partition-v3-code-proposal-20261014'

def read(path):
    raw=path.read_bytes();return json.loads(gzip.decompress(raw)if path.suffix=='.gz'else raw)

def check(ref):
    path=ROOT/ref['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==ref['sha256'];return path

def packing_diagnostics(result,ideal):
    polygons=result['outside']+[q['polygon']for q in result['inside']]
    pieces=v2.oracle.packed_pieces(polygons,ideal);digest=hashlib.sha256();excluded=0;collapsed=0
    n=v2.oracle.normal(v2.oracle.points(ideal));residuals=[]
    for piece in pieces:
        triangle=piece['packedPieceTriplet'];digest.update(np.asarray(triangle,dtype='<f8').tobytes())
        (ax,_,az),(bx,_,bz),(cx,_,cz)=triangle
        determinant=(bz-cz)*(ax-cx)+(cx-bx)*(az-cz) # Same binary64 operation association as native-terrain.js.
        excluded+=abs(determinant)<1e-10
        collapsed+=not any(v2.oracle.normal(v2.oracle.points(triangle)))
        residuals.extend(abs(q/n[1])for q in piece['exactPackedSourcePlaneResiduals'])
    return dict(packedFacets=len(pieces),orderedPackedSHA256=digest.hexdigest(),
                rendererExcludedProjectedFacetsAtExistingAbsDetLessThan1eMinus10=excluded,
                exact3DAreaZeroPackedFacets=collapsed,
                maxExactOwnPlaneVerticalPackingResidualM=str(max(residuals,default=F(0))),
                productionHeightCoverageMAXOrdinaryOrRuntimeProved=False)

def compare(limit):
    assert type(limit)is int and 1<=limit<=16
    pins=read(PROPOSAL/'bounded891-input-pins.json')
    for ref in pins['evidenceRefs']:check(ref)
    source=read(check(pins['sourceAccountRef']));feasibility=read(check(pins['feasibilityRef']))
    assert source['candidateSHA256']=='b033b8f2e451d7ce73a6c409d0b855686a7a1b604454a04a8b6a56db118ed647'
    records=[]
    for row in feasibility['rows']:
        if row['eligibleCurrentParentMaskNominationOnly']:
            mask=read(check(row['completeMask']))
            records.extend({**mask['rows'][i],'uid':row['uid'],'maskEvidence':row['completeMask']}
                           for i in mask['positiveMaskIDs'])
    context=v2.PreparedMasks(records)
    assert len(context.masks)==5553 and len(context.first_ids)==1234
    lineage=source['account']['completeOutputFacetLineage'];assert len(lineage)==3214
    ideal=lineage[891]['exactProposedPoints'];face=v2.oracle.points(ideal)
    first,relevant=context.relevant(v2.oracle.bb(face));assert len(first)==539 and len(relevant)==2415
    chosen=first[:limit];subset=v2.PreparedMasks([records[i]for i in chosen])
    started=time.perf_counter();old=v2.partition(ideal,subset);old_time=time.perf_counter()-started
    started=time.perf_counter();new=v3.partition(ideal,subset);new_time=time.perf_counter()-started
    axis=max(range(3),key=lambda k:abs(v2.oracle.normal(face)[k]))
    for key in ['exactWholeIntrinsicArea','exactInsideMaskUnionIntrinsicArea','exactOutsideMaskUnionIntrinsicArea']:assert old[key]==new[key]
    for name in ['inside','outside']:
        a=old[name]if name=='outside'else [q['polygon']for q in old[name]]
        b=new[name]if name=='outside'else [q['polygon']for q in new[name]]
        assert difference_area(a,b,axis)==difference_area(b,a,axis)==0
    for mi in subset.first_ids:
        a=[q['polygon']for q in old['inside']if q['mask']==mi];b=[q['polygon']for q in new['inside']if q['mask']==mi]
        assert difference_area(a,b,axis)==difference_area(b,a,axis)==0
    polygons=new['outside']+[q['polygon']for q in new['inside']]
    assert all(closed_segment_covered(a,b,polygons)for a,b in zip(face,face[1:]+face[:1]))
    result=dict(face=891,onlySelectedUniqueMasks=limit,selectedOriginalGlobalMaskIDs=chosen,
                subsetOwnerIDsAreLocalAndMappedBySelectedOriginalGlobalMaskIDs=True,
                fullContextUniqueRelevantMasks=539,fullContextOccurrenceMasks=2415,
                full539MaskPartitionNotComputed=True,sourceFaceLineageVerbatim=lineage[891],
                oldSeconds=old_time,newSeconds=new_time,oldOutsidePolygons=len(old['outside']),
                newOutsidePolygons=len(new['outside']),oldInsidePolygons=len(old['inside']),
                newInsidePolygons=len(new['inside']),exactSubsetIdealSurfaceAndFirstOwnershipEqual=True,
                fullOriginalBoundarySegmentsCoveredByExactSubsetPartition=True,
                oldPacking=packing_diagnostics(old,ideal),newPacking=packing_diagnostics(new,ideal),
                actualProductionCaptureOrPhysicalQualification=False,geometryApprovalTransferred=False)
    for ref in pins['evidenceRefs']:check(ref)
    return result

if __name__=='__main__':
    assert len(sys.argv)==3 and sys.argv[1]=='--compare-first-unique-masks'
    print(json.dumps(compare(int(sys.argv[2])),sort_keys=True))
