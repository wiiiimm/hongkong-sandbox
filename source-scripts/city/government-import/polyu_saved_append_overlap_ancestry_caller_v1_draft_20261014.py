"""UNEXECUTED saved complete candidate overlap/ancestry; no scene acceptance."""
from pathlib import Path
import json,sys,time,uuid,subprocess,collections
import numpy as np
import shapely
from run import ROOT,HERE,read,save,connect,reservations
import polyu_append_source_region_historical_production_caller_v1_draft_20261014 as prior
import polyu_saved_append_overlap_ancestry_v1_draft_20261014 as helper
from polyu_compact_runtime_mesh_projection_v1_draft_20261014 import mesh_binding
from upton_actual_candidate_clearance_audit_v1_20261012 import verify_drawn_multiset
from polyu_five_mask_source_plane_partition_v1_20261014 import serial
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-saved-append-overlap-ancestry-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
JOB='62d0bea3f201479354bd87fff2ef10b7a1aa14757019f1f4439e6a7d28cf8a37'
ref,check=prior.ref,prior.check
def load():
    pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
    for q in distinct_refs(pins['codeRefs']+pins['inputRefs']):check(q)
    receipt=read(prior.DOC/'result.json');cert=read(prior.DOC/'ROOT-VERIFIED.json');assert receipt['jobId']==cert['jobId']==JOB and cert['exactNeonReadback']and cert['allEvidenceHashesVerified']and cert['leaseReleased']
    inp=read(prior.DOC/'input.json.gz');replay=read(prior.DOC/'actual-production-replay.json.gz');candidate=read(prior.DOC/'private-native-terrain-candidate.json.gz')
    assert inp['historicalReplay']and not inp['currentAcceptance']and replay['historicalCapturedManifestSHA256']==prior.binding.HISTORICAL and replay['startEndAllInputsVerified']and replay['currentExteriorXYZOrderedHashMatched']
    failure=read(prior.DOC/'real-validator-outcome.json');assert failure['actualFailure']['message']=='Native terrain contains overlapping height surfaces'and not failure['passed']
    mesh={k:candidate['nativeMesh'][k]for k in ['position','index']};assert mesh_binding(mesh)==inp['completeMeshBinding']==pins['completeMeshBinding']
    assert inp['completeNewNativeFacets']==148459 and inp['completeNewPositionVertices']==587502
    nom=read(check(inp['newNomination']));old=read(check(inp['previousFullNomination']));assert nom['previousFullNomination']==inp['previousFullNomination']
    assert len(old['candidateFaceProvenance'])==147096 and len(nom['appendAccount']['appendedFaces'])==1363 and len(old['completeOldPrivateMapping'])==3214 and len(old['completeCapturedParentMapping'])==12
    assert prior.binding.grid_domain(candidate)==inp['fullParentDomain']==[2002.5,-2067.5,2212.5,-1927.5]
    assert len(replay['before']['closedDomainDrawnTriplets'])==40 and len(replay['after']['closedDomainDrawnTriplets'])==148487 and len(replay['allCandidateGridSamples'])==1247
    guards=read(prior.DOC/'all25-original-production-guard-site-replay.json.gz');assert len(guards['rows'])==25 and not guards['allSamplerErrors']and not any(q['error']for q in replay['allCandidateGridSamples'])
    parent_ref=dict(path='3d-viewer/city/data/terrain.json',sha256=replay['inputHashes']['3d-viewer/city/data/terrain.json']);parent=read(check(parent_ref))
    return pins,receipt,inp,replay,candidate,nom,old,guards,parent,parent_ref
def schema_only():
    pins,_,inp,_,_,nom,old,guards,_,parent_ref=load()
    assert [q['candidateFace']for q in old['candidateFaceProvenance']]==list(range(147096))and [q['candidateFace']for q in nom['appendAccount']['appendedFaces']]==list(range(147096,148459))
    return dict(passed=True,caller=ref(Path(__file__)),completeMeshBinding=pins['completeMeshBinding'],candidateFaces=148459,completePositionsIncludingUnused=587502,oldProvenance=147096,appendedProvenance=1363,
        completeOriginalSourceSlots=3214,completeCapturedParentSlots=12,actualBaseParent=parent_ref,historicalReplay=True,currentAcceptance=False,noUnionPairPlaneFiniteDBLeaseWorker=True)
def source_map(old,nom):
    descriptors=[];sources={}
    def source(key,kind,points,pointer,identity):
        if key in sources:assert sources[key]['completeOwnPlanePoints']==points;return
        sources[key]=dict(kind=kind,completeOwnPlanePoints=points,exactOwnPlane=helper.rational_plane(points),fullSourcePointer=pointer,sourceIdentityVerbatim=identity,
            authenticatedRecordedTerrainPlaneNotArchitectureOrApproval=True)
    def legacy(i):
        r=old['completeOldPrivateMapping'][i];assert r['oldPrivateFace']==i;lineage=r['previousLineageVerbatim'];key='legacy:'+str(i)
        source(key,'legacy-recorded-proposed-terrain-plane',lineage['exactProposedPoints'],dict(mapping='completeOldPrivateMapping',oldPrivateFace=i,field='previousLineageVerbatim.exactProposedPoints'),lineage);return key
    for i,p in enumerate(old['candidateFaceProvenance']):
        assert p['candidateFace']==i
        if i<8011:
            j=p.get('oldPrivateFace',p.get('ancestor',{}).get('oldPrivateFace'));assert type(j)is int and 0<=j<3214;key=legacy(j)
        else:
            j=p['ancestor']['capturedParentFacet'];r=old['completeCapturedParentMapping'][j];assert r['capturedParentFacet']==j;key='parent:'+str(j)
            source(key,'captured-current-parent-plane',r['wholeOriginalCapturedParentTriplet'],dict(mapping='completeCapturedParentMapping',capturedParentFacet=j,field='wholeOriginalCapturedParentTriplet'),dict(capturedParentFacet=j))
        descriptors.append(dict(candidateFace=i,kind=p['kind'],sourcePlaneKey=key,fullProvenancePointer=dict(field='candidateFaceProvenance',candidateFace=i)))
    for p in nom['appendAccount']['appendedFaces']:
        i=p['candidateFace'];assert i==len(descriptors);j=p['sourcePointer']['oldPrivateFace'];key=legacy(j)
        descriptors.append(dict(candidateFace=i,kind=p['kind'],sourcePlaneKey=key,fullProvenancePointer=dict(field='appendAccount.appendedFaces',appendedOrdinal=i-147096),sourceRegionPointer=p['sourcePointer']))
    assert len(descriptors)==148459;return descriptors,sources
def owned():
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
    def pulse():
        nonlocal last
        if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
    pins,receipt,inp,replay,candidate,nom,old,guards,parent,parent_ref=load();assert lease['resources']==['immutable-source-proof:'+BATCH]
    prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
    validation=read(check(prep['helperValidationRef']));assert validation['passedTests']==5 and validation['failedTests']==0 and validation['exitCode']==0
    assert validation['executedCodeRefs']==[ref(Path(helper.__file__)),ref(HERE/'test_polyu_saved_append_overlap_ancestry_v1_draft_20261014.py')]
    refs=distinct_refs(pins['codeRefs']+pins['inputRefs']+prep['evidenceRefs']+validation['evidenceRefs']+[prep['helperValidationRef'],ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')])
    def fence():
        for q in distinct_refs(refs):check(q);pulse()
        assert reservations.owns(lease)
    with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
    fence();DOC.mkdir();mesh=candidate['nativeMesh'];raw=np.asarray(mesh['position'],dtype=np.float32).astype('<f8').reshape(-1,3)[np.asarray(mesh['index'],dtype=np.int64).reshape(-1,3)]
    multiset=verify_drawn_multiset(raw,np.asarray(replay['after']['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3));descriptors,sources=source_map(old,nom);pulse()
    save(DOC/'complete-source-plane-and-face-map.json.gz',serial(dict(descriptors=descriptors,sources=sources,oldFullNomination=inp['previousFullNomination'],appendNomination=inp['newNomination'])))
    polygons,ids,measurement=helper.measurement(raw,inp['fullParentDomain']);save(DOC/'actual-rectangle-and-overlap-measurement.json',dict(**measurement,actualDrawMultiset=multiset,rawValidatorFailureVerbatim=read(prior.DOC/'real-validator-outcome.json')));pulse()
    edges=helper.parent_edge_rows(candidate,parent,inp['fullParentDomain']);save(DOC/'complete-actual-base-parent-edge-inventory.json.gz',dict(**edges,actualBaseParent=parent_ref,validatorStoppedBeforeEdgeGate=True));pulse()
    eligible=[polygons[i]for i in ids];tree=shapely.STRtree(eligible);counts=collections.Counter();area_by_group=collections.defaultdict(float);positive=0;packed_plane_cache={}
    for start in range(0,len(ids),128):
        left,right=tree.query(eligible[start:start+128],predicate='intersects');pairs=sorted((int(a)+start,int(b))for a,b in zip(left,right)if int(a)+start<int(b));rows=[]
        for a,b in pairs:
            i,j=ids[a],ids[b];region=polygons[i].intersection(polygons[j]);dimension='area'if region.area>0 else'line'if region.length>0 else'empty'if region.is_empty else'point';counts[dimension]+=1
            if dimension=='area':
                row=helper.pair_record(i,j,region,raw,descriptors,sources,packed_plane_cache);positive+=1;counts['sameIdealPlane'if row['sameAuthenticatedIdealPlane']else'differentOrNonAffineIdealPlane']+=1;area_by_group[row['group']]+=region.area
            else:row=dict(leftFace=i,rightFace=j,projectedDimension=dimension,measuredLengthM=region.length,noPositiveAreaOrApprovalCredit=True)
            rows.append(row);pulse()
        save(DOC/'complete-pair-chunks'/(str(start).zfill(6)+'.json.gz'),dict(eligibleStart=start,eligibleEnd=min(start+128,len(ids)),completeDeterministicIntersectingPairs=rows,pairwiseAreaNotUnionExcess=True));pulse()
        print(json.dumps(dict(completeEligibleFacesVisited=min(start+128,len(ids)),totalEligibleFaces=len(ids),positiveAreaPairs=positive)),flush=True)
    save(DOC/'complete-overlap-summary.json',dict(measurement=measurement,counts=dict(counts),summedPairwiseAreaByGroup=dict(area_by_group),pairwiseAreaIsNotUnionExcess=True,
        completeCandidateFacets=148459,positiveAreaPairs=positive,sourcePlaneCount=len(sources),all25GuardScalarRows=[{k:q[k]for k in ['uid','checks','beforeGap','afterGap','maxGroundChange','reasons']}for q in guards['rows']],
        completeBaseParentEdges=ref(DOC/'complete-actual-base-parent-edge-inventory.json.gz'),noPackingCaptureNativeDecodeWholeActorFiniteMAXRayOrApproval=True,currentAcceptance=False,physicalAccepted=False))
    refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence()
    result=prior.capture.prior.module('saved_append_overlap_freezer',prior.capture.prior.FREEZER).freeze(BATCH,'historical-saved-candidate-complete-measured-overlap-source-plane-ancestry-only',[check(q)for q in refs],dict(uids=prior.capture.prior.UIDS,sourceOnly=True,
        historicalCapturedManifestSHA256=prior.binding.HISTORICAL,currentAcceptance=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0,completeCandidateFacets=148459,positiveAreaPairs=positive))
    fence();print(json.dumps(dict(jobId=result['jobId'],result=ref(DOC/'result.json'),positiveAreaPairs=positive)),flush=True)
def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only()));return
    if '--owned'in sys.argv:return owned()
    assert '--measure-saved-whole-overlap-ancestry-only'in sys.argv and not DOC.exists()and not LOCAL.exists();load()
    prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
    claim=reservations.claim('polyu-saved-overlap-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:
        save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
