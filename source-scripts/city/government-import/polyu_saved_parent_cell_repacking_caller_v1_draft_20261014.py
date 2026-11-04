"""UNEXECUTED scoped saved-parent packing; no partition/source replay."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,time,uuid,subprocess,hashlib,copy
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
import polyu_five_current_parent_actual_production_capture_v2_20261014 as capture
import polyu_computed_parent_cell_enclosure_v1_draft_20261014 as packing
from polyu_five_mask_source_plane_partition_v1_20261014 import serial
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs

BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-saved-parent-cell-repacking-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
ATTR=BASE/'government-xl-polyu-saved-hole-mask-attribution-v2-20261014'
ATTR_JOB='c1e67a81c324a56e4c041f8857fc8f8d7e87ca53b831cf171a52e704c58fdcc5'
CAP_JOB='8f204d9c83bc0cc6ca45bb56da6da2fb8b70255c5af6c7dd37f346f73aceae9e'
CURRENT=capture.CURRENT;ref,check=capture.ref,capture.check

def load():
    pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
    for q in distinct_refs(pins['codeRefs']+pins['inputRefs']):check(q)
    inp=read(capture.DOC/'input.json.gz');nom=read(check(inp['newNomination']))
    receipts=[(capture.DOC,CAP_JOB),(ATTR,ATTR_JOB)]
    for folder,job in receipts:assert read(folder/'result.json')['jobId']==job
    assert nom['schema']=='private-source-plane-preserving-five-current-parent-mask-nomination-v3'
    assert len(nom['completeOldPrivateMapping'])==3214 and len(nom['completeCapturedParentMapping'])==12
    assert len(nom['candidateFaceProvenance'])==55305 and len(nom['newNativeMesh']['index'])==55305*3
    old_ids=[j for r in nom['completeOldPrivateMapping']for j in r['newCandidateFaces']]
    parent_ids=[j for r in nom['completeCapturedParentMapping']for j in r['newCandidateFaces']]
    assert old_ids==list(range(8011))and parent_ids==list(range(8011,55305))
    assert sum(len(r['completeExactMaskPartition']['inside'])for r in nom['completeCapturedParentMapping'])==24448
    assert nom['all25AffectedActors']==capture.prior.UIDS and not nom['physicalAccepted']and not nom['installationApproved']
    measured=read(ATTR/'actual-validator-rectangle-union-attribution.json.gz')
    assert measured['measuredMissingAreaM2']==.008016086737637231 and measured['measuredOutsideAreaM2']==0
    g=read(capture.DOC/'private-native-terrain-candidate.json.gz')['meta']['georef']
    patch=read(capture.DOC/'private-native-terrain-candidate.json.gz')
    domain=[g['bE']-834500,816500-g['bN'],g['bE']+(patch['w']-1)*g['aE']-834500,816500-(g['bN']+(patch['h']-1)*g['aN'])]
    assert domain==inp['fullParentDomain']==[2002.5,-2067.5,2212.5,-1927.5]
    assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
    resources=sorted(['building:'+u for u in capture.prior.UIDS]+['terrain-patch:'+u for u in capture.prior.UIDS]+['immutable-source-proof:'+BATCH]);assert len(resources)==51
    return pins,inp,nom,domain,resources,receipts

def schema_only():
    _,_,n,d,r,_=load()
    return dict(passed=True,caller=ref(Path(__file__)),currentManifestSHA256=CURRENT,oldComputedAndLiteral8011Reused=True,
        completeSavedParentInsideRegions=24448,oldPackedParentFacets=47294,complete12CurrentParents=True,fullParentDomain=d,
        saved3214MappingsAndPrefix1485Retained=True,canonicalResources=r,noPartitionPackingSourceProofDBLeaseWorker=True)

def owned():
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
    pins,inp,nom,domain,resources,receipts=load();assert lease['resources']==resources
    prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
    v=read(check(prep['helperValidationRef']));assert v['passedTests']==8 and v['failedTests']==0 and v['exitCode']==0
    assert v['executedCodeRefs']==[ref(Path(packing.__file__)),ref(HERE/'test_polyu_computed_parent_cell_enclosure_v1_draft_20261014.py')]
    refs=pins['codeRefs']+pins['inputRefs']+prep['evidenceRefs']+v['evidenceRefs']+[prep['helperValidationRef'],ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')]
    for folder,job in receipts:
        result=read(folder/'result.json')
        with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',result)
        refs+=result['evidenceRefs']+[ref(folder/'result.json')]
    refs=distinct_refs(refs);last=time.monotonic()
    def pulse():
        nonlocal last
        if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
    def fence():
        for q in refs:check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT and reservations.owns(lease)
    fence();DOC.mkdir();oldmesh=nom['newNativeMesh'];positions=list(oldmesh['position']);index=list(oldmesh['index'][:8011*3]);provenance=copy.deepcopy(nom['candidateFaceProvenance'][:8011]);parent_maps=[];shared={}
    records=read(capture.nomination.DOC/'complete-five-mask-partition-diagnostic.json.gz')['allEligibleMaskOccurrences'];assert len(records)==5553
    for original in nom['completeCapturedParentMapping']:
        i=original['capturedParentFacet'];face=original['wholeOriginalCapturedParentTriplet'];proof=original['completeExactMaskPartition'];ids=[]
        def progress(done,total):
            pulse()
            if done%128==0 or done==total:print(json.dumps(dict(stage='saved-parent-cell-repacking',parent=i,insideRegionsCompleted=done,totalInsideRegions=total)),flush=True)
        pieces,account=packing.parent_pieces(proof,face,shared,domain,progress)
        for p in pieces:
            j=len(provenance);start=len(positions)//3;positions.extend(v for xyz in p['packedPieceTriplet']for v in xyz);index.extend(range(start,start+3));ids.append(j)
            provenance.append(dict(candidateFace=j,kind='capturedCurrentParentOwnPlaneFloat32CellInsideEligibleMasks',
                ancestor=dict(capturedParentFacet=i,wholeOriginalCapturedParentTriplet=face),mask=dict(mask=p['mask'],completeMaskLineage=records[p['mask']]),
                exactOwnPlanePoints=serial(p['exactOwnPlanePoints']),exactPackedSourcePlaneResiduals=serial(p['exactPackedSourcePlaneResiduals']),
                computedInsideCellEnclosure=serial({k:p[k]for k in ['enclosureInsidePolygon','enclosureLocalTriangle','exactInsideExpansionAreaM2']}),
                partitionProofReference=dict(mapping='completeCapturedParentMapping',capturedParentFacet=i),
                packingResidualsMeasuredNotWaived=True,noOtherLayerYUsed=True,freshQualificationRequired=True))
        parent_maps.append(dict(capturedParentFacet=i,newCandidateFaces=ids,wholeOriginalCapturedParentTriplet=face,
            completeExactMaskPartition=proof,previousV3MappingVerbatim=original,completeComputedInsideEnclosureAccount=serial(account)))
        save(DOC/'parent-progress'/(str(i).zfill(2)+'.json.gz'),parent_maps[-1]);pulse()
    out=copy.deepcopy(nom);out.update(schema='private-source-plane-preserving-five-current-parent-mask-parent-cell-nomination-v4',
        previousCompleteV3Nomination=inp['newNomination'],newNativeMesh=dict(position=positions,index=index),candidateFaceProvenance=provenance,
        completeCapturedParentMapping=parent_maps,sharedComputedParentNodeCells=len(shared),all8011PreviousPackedFacetsUnchanged=True,
        all3214OldMappingsVerbatim=True,all47294PreviousParentFragmentsRetainedInSourceLineage=True,
        newlyExpandedParentRegionsOwnedFourWorldCompatibilityPending=True,actualRectangleSampler3366GuardsNative59527All25Pending=True,
        noOldGeometryBoundOverlapApprovalTransferred=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0)
    assert out['completeOldPrivateMapping']==nom['completeOldPrivateMapping']and out['candidateFaceProvenance'][:8011]==nom['candidateFaceProvenance'][:8011]
    assert positions[:len(oldmesh['position'])]==oldmesh['position']and index[:8011*3]==oldmesh['index'][:8011*3]
    assert len(index)==3*len(provenance)and [r['candidateFace']for r in provenance]==list(range(len(provenance)))
    assert sorted([j for r in out['completeOldPrivateMapping']for j in r['newCandidateFaces']]+[j for r in parent_maps for j in r['newCandidateFaces']])==list(range(len(provenance)))
    save(DOC/'private-saved-parent-cell-repacked-nomination.json.gz',out)
    save(DOC/'repacking-scope.json',dict(completeSavedInsideRegions=24448,completeOldUnchangedFacets=8011,newPackedParentFacets=len(provenance)-8011,
        completeCandidateFacets=len(provenance),completePositionVerticesIncludingUnused=len(positions)//3,ownParentPlanesBeforePacking=True,
        masksAndPartitionProofsUnchanged=True,allPrefixAndSourceOutsideAndLiteralIndicesUnchanged=True,
        noSourceBuildingOrCurrentLiveTerrainChange=True,allExpandedRegionAndActualQualificationPending=True))
    refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence()
    capture.prior.module('polyu_parent_cell_repacking_freezer',capture.prior.FREEZER).freeze(BATCH,'private-computed-parent-own-plane-cell-repacking-only',[check(q)for q in refs],dict(uids=capture.prior.UIDS,sourceOnly=True,terrainNominationNotAcceptance=True,physicalAccepted=False,newlyInstalled=0))

def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
    if '--owned'in sys.argv:return owned()
    assert '--repack-saved-current-parent-regions-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
    *_,resources,_=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
    claim=reservations.claim('polyu-saved-parent-cell-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:
        save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
