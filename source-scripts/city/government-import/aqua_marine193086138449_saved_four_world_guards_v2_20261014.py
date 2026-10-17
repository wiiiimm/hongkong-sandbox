"""ROOT-only complete four-world source/ground and independent foreign contacts.
Raw finite negatives are retained; no new root/structural/watertight admission.
"""
from pathlib import Path
import sys,json,subprocess,uuid,time,numpy as np
import aqua_marine193086138449_current_attribute_capture_v2_20261014 as capture
from aqua_exact_existing_warning_review_v1_20261014 import bind_review
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
from exact_original_paired_finite_clearance_20261010 import verify as paired
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from run import ROOT,HERE,read,save,connect,reservations
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
A=capture.A;ref,check,module=capture.ref,capture.check,capture.module
BATCH='government-xl-aqua-marine193086138449-saved-four-world-guards-v2-20261014';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';REVIEW=BASE/'government-xl-aqua-marine193086-facade-bottom-functional-proposal-v1-20261014/ROOT-FUNCTIONAL-SOURCE-REVIEW.json';CSUID='3333921515P20060311'
def load(job):
    data,old,p,foreign,form,refs=capture.load();r=read(capture.DOC/'result.json');v=read(capture.DOC/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==job and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased'];binding=read(capture.DOC/'capture-binding.json');assert binding['oldLiteralPositionAndIndexExactBytesPreserved']and binding['sourceGeometryChanges']==binding['terrainGeometryChanges']==0 and binding['completeCurrentGroundSHA256']==p['completeActualGroundSHA256']and binding['completeCurrentGroundFaces']==584
    review=read(REVIEW);disposition=bind_review(review,p,uid=A.prior.UID,csuid=CSUID,source_sha=A.prior.SOURCE_SHA,current_manifest=A.prior.CURRENT,current_snapshot=A.prior.SNAPSHOT)
    proof=read(ROOT/review['verifiedJobProof']['path']);assert proof['jobId']==review['completedJob']and proof['exactNeonReadback']and proof['allEvidenceHashesVerified']and proof['leaseReleased']
    refs=distinct_refs(refs+r['evidenceRefs']+[ref(capture.DOC/'result.json'),ref(capture.DOC/'ROOT-VERIFIED.json'),ref(REVIEW),ref(Path(__file__))]+[review[k]for k in ['actualExportInspected','exactContext','proposedContext','verifiedJobProof']])
    for q in refs:check(q)
    return data,r,p,disposition,refs

def schema_only(job):
    data,r,p,d,refs=load(job);arrays=read(capture.DOC/'complete-two-actor-actual-attributes.json.gz');assert len(arrays['rows'])==2 and arrays['startEndAllInputsVerified'];return dict(passed=True,caller=ref(Path(__file__)),captureJob=job,ROOTFunctionalReview=ref(REVIEW),actualSourceFaces=[22735,116],fourRepresentations=['providerOriginal','actualLiteral','explicitLeftAssociatedF32','explicitBalancedF32'],scope=data[-1],fullSavedGroundFaces=584,rawStrictFoundationPassed=False,onlyExistingThreeFaceWarningDisposition=True,noSourceArraysMathFiniteCollisionDBLeaseWorker=True)

def worlds(data,packet):
    captured=read(capture.DOC/'complete-two-actor-actual-attributes.json.gz');result={};assert captured['startEndAllInputsVerified']
    for row in captured['rows']:
        uid=row['uid'];idx=np.asarray(row['completeOriginalIndex'],dtype=np.int64).reshape(-1,3);n=22735 if uid==A.prior.UID else 116;assert len(idx)==n
        streams={name:np.asarray(row[key],dtype='<f8').reshape(-1,3)[idx]for name,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]}
        if uid==A.prior.UID:
            original=np.empty((n,3,3),dtype='<f8');seen=set()
            for part in read(A.PARTS)['rows'][0]['parts']:
                tri=np.asarray(part['position'],dtype='<f8').reshape(-1,3)[np.asarray(part['index'],dtype=np.int64).reshape(-1,3)]
                for i,t in zip(part['originalFaceIds'],tri):assert i not in seen;seen.add(i);original[i]=t
            assert seen==set(range(n))and A.prior.digest(original.tobytes())==packet['completeSavedOriginalWorldSHA256']and A.prior.digest(streams['actualLiteral'].tobytes())==packet['completeLiteralWorldSHA256']
        else:
            # Missing provider-original foreign coordinates only. Existing decoder,
            # byte-bound exact source; no source identity/role census recalculation.
            original=decode_original_world_triangles((ROOT/data[4]['originalPaths'][uid]).read_bytes());assert A.prior.digest(np.asarray(original,dtype='<f8').tobytes())==data[5]['foreign']['completeWorldSHA256']
        streams={'providerOriginal':np.asarray(original,dtype='<f8'),**streams}
        for t in streams.values():assert t.shape==(n,3,3)and np.isfinite(t).all()
        result[uid]=streams
    assert set(result)=={A.prior.UID,A.prior.FOREIGN};return result

def calculate(data,packet,disposition,pulse):
    streams=worlds(data,packet);ground=np.asarray(read(A.prior.LOCAL/'runtime-geometry.json.gz')['rows'][0]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);assert len(ground)==584 and A.prior.digest(ground.tobytes())==packet['completeActualGroundSHA256'];gsha=packet['completeActualGroundSHA256'];cache={};summaries=[];clock=time.monotonic()
    historical=set(packet['allOtherPartialBelowMinusHalfSourceFaceIDs'])|{7525,7526,7527}
    for uid,modes in streams.items():
        for mode,tri in modes.items():
            wsha=A.prior.digest(tri.tobytes());rows=[]
            for i,face in enumerate(tri):
                key=(A.prior.digest(face.tobytes()),gsha)
                if key in cache:
                    previous,proof=cache[key];row=dict(originalFaceID=i,exactIdenticalSourceFaceAndCompleteGroundTupleReuse=previous,proofVerbatim=proof)
                else:
                    first=coarse(face,ground);second=None if first['existingOrdinaryClearanceBoundProved']else paired(face,ground);proof=dict(coarse=first,paired=second,rawOrdinaryBoundProved=first['existingOrdinaryClearanceBoundProved']or bool(second and second['existingOrdinaryClearanceBoundProved']),rawProjectionCovered=first['groundProjectionCovered']and(second is None or second['groundProjectionCovered']));cache[key]=(dict(uid=uid,arithmetic=mode,originalFaceID=i,sourceFaceSHA256=key[0],completeGroundSHA256=gsha),proof);row=dict(originalFaceID=i,freshExactKernel=True,proofVerbatim=proof)
                rows.append(row);pulse()
                if time.monotonic()-clock>=20:print(json.dumps(dict(uid=uid,mode=mode,faces=i+1,total=len(tri))),flush=True);clock=time.monotonic()
            bad=[r['originalFaceID']for r in rows if not r['proofVerbatim']['rawOrdinaryBoundProved']];missing=[r['originalFaceID']for r in rows if not r['proofVerbatim']['rawProjectionCovered']];file=DOC/(uid.replace('/','-').replace(':','-')+'-'+mode+'-finite.json.gz');save(file,dict(uid=uid,arithmetic=mode,completeSourceWorldSHA256=wsha,completeGroundSHA256=gsha,allOriginalFaces=rows,rawOrdinaryUnprovedFaceIDs=bad,rawProjectionUncoveredFaceIDs=missing,noSourceFacesOmitted=True,rawStrictFoundationUnchanged=True,applicabilityNotAutomaticallyExtendedToFiniteRows=True,physicalAccepted=False));summaries.append(dict(uid=uid,arithmetic=mode,completeSourceWorldSHA256=wsha,completeFaces=len(tri),finite=ref(file),rawOrdinaryUnprovedFaceIDs=bad,rawProjectionUncoveredFaceIDs=missing,ownedRawBelowGradeIDsOutsideSaved281=sorted(set(bad)-historical)if uid==A.prior.UID else[],foreignOriginalIsNotInstalledOrExempt=True))
    contacts=[]
    # The four named arithmetic interpretations are checked coherently for both
    # source actors. Explicit arithmetic is not universal GPU acceptance.
    for mode in streams[A.prior.UID]:
        own=streams[A.prior.UID][mode];foreign=streams[A.prior.FOREIGN][mode];proof=exact_finite_contacts(own,list(range(len(own))),foreign,list(range(len(foreign))));assert proof['allPairsExamined']and proof['sourceFacesOmitted']==0;file=DOC/(mode+'-complete-independent-foreign-contacts.json.gz');save(file,dict(arithmetic=mode,wholeOwnedWorldSHA256=A.prior.digest(own.tobytes()),wholeForeignWorldSHA256=A.prior.digest(foreign.tobytes()),allContactsVerbatim=proof,foreignCollisionExemption=False,identityDoesNotApproveAnyContact=True,physicalAccepted=False));contacts.append(dict(arithmetic=mode,completeOwnedFaces=len(own),completeForeignFaces=len(foreign),exactContacts=ref(file),contactCount=len(proof['contacts']),sourceCollisionDispositionPending=bool(proof['contacts'])));pulse(force=True)
    save(DOC/'complete-four-world-guard-result.json',dict(rows=summaries,foreignCollisionRows=contacts,completeEightWorldFaceStreams=True,completeFourCoherentForeignCollisionStreams=True,allRawKernelNegativesRetained=True,rawFoundationVerbatim=packet['rawFoundationVerbatim'],all278PartialBelowFaceIDs=packet['allOtherPartialBelowMinusHalfSourceFaceIDs'],wholeMinimumGapVerbatim=packet['minimumWholeSurfaceGapVerbatim'],existingThreeFaceWarningDisposition=disposition,ROOTFunctionalReview=ref(REVIEW),savedOrdinaryDiagnostics=ref(A.prior.DOC/'diagnostic.json.gz'),existingLoaderRuntimeNativeBASICReasonsReusedOnlyForUnchangedSourceWorldGroundCurrentInputTuple=True,currentViewerPickingMobileCollisionAndPublicationStillRequired=True,rawStrictFoundationPassed=False,noNewStructuralRootWatertightnessGate=True,allFiniteNegativeFacesAreNotAutomaticallyExempt=True,sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0))

def owned(job):
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['captureJob']==job;data,r,p,d,refs=load(job);refs=distinct_refs(refs+prep['codeRefs']+prep['inputRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'actual-readonly-preparation.json')]);pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def fence():
        pulse(force=True)
        for q in refs:check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==A.prior.CURRENT;pulse(force=True)
    fence()
    with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',r)
    DOC.mkdir();calculate(data,p,d,pulse);refs=distinct_refs(refs+[ref(q)for q in DOC.rglob('*')if q.is_file()]);fence();module(A.prior.FREEZER,'aqua_four_source_guard_freezer').freeze(BATCH,'complete-current-four-world-finite-independent-foreign-contacts-raw-failures-retained',[check(q)for q in refs],dict(uids=[A.prior.UID,A.prior.FOREIGN],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))
def main():
    job=sys.argv[sys.argv.index('--capture-job')+1]
    if '--schema-only'in sys.argv:print(json.dumps(schema_only(job)));return
    if '--owned'in sys.argv:return owned(job)
    assert '--complete-four-world-source-guards-only'in sys.argv and not DOC.exists()and not LOCAL.exists();data,*_=load(job);scope=data[-1];prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['captureJob']==job;resources=['building:'+u for u in scope]+['terrain-patch:'+u for u in scope]+['immutable-source-proof:'+BATCH];claim=reservations.claim('aqua-four-source-guards-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--capture-job',job,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
