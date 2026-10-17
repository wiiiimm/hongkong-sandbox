"""ROOT-only bounded exact source context; raw viewer failures remain unresolved."""
from pathlib import Path
import sys,json,subprocess,uuid,numpy as np
import aqua_marine193086_saved_source_context_diagrams_v2_20261014 as prior
from aqua_facade_bottom_context_v1_20261014 import descriptor,shared_edges,draw_2d
from run import ROOT,HERE,read,save,connect,reservations
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
A=prior.attribution;ref,check,module=prior.ref,prior.check,prior.module
BATCH='government-xl-aqua-marine193086-facade-bottom-functional-proposal-v1-20261014';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';JOB='802e52e3ae5ef64bceffff5802b11b7f015d17519ab6837143bef06fcd63dc9b';CSUID='3333921515P20060311';FAILED=[7525,7526,7527];CONTINUATION=[13595,13596,15455,15456,15457,16548,16549,16550]
def load():
    data,attribution_result,p,refs=prior.load();r=read(prior.DOC/'result.json');v=read(prior.DOC/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==JOB and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased'];views=read(prior.DOC/'saved-source-diagrams.json');assert len(views['views'])==7 and not views['roleAssigned']and not views['strictFoundationAccepted']and not views['ordinaryWarningResolved']
    assert sorted({i for row in views['exactLiteralCoordinateContext']for i in row['exactXYZSharedVertexFaceIDs']})==sorted(FAILED+CONTINUATION)
    assert data[0]['candidate']['entry']['buildingCSUID']==CSUID
    refs=distinct_refs(refs+r['evidenceRefs']+[ref(prior.DOC/'result.json'),ref(prior.DOC/'ROOT-VERIFIED.json'),ref(Path(__file__))])
    for q in refs:check(q)
    return data,r,p,views,refs

def schema_only():
    data,r,p,v,refs=load();return dict(passed=True,caller=ref(Path(__file__)),diagramJob=JOB,actualAttributionJob=prior.JOB,scope=data[-1],failedFaceIDs=FAILED,completeContinuationFaceIDs=CONTINUATION,allPartialBelowFaces=278,rawStrictFoundationPassed=False,warningResolved=False,noSourceGeometryCalculationRenderDecodeNumericalDBLeaseWorker=True)

def compute(packet,views):
    a=read(A.prior.LOCAL/'runtime-geometry.json.gz')['rows'][0];pos=np.asarray(a['position'],dtype='<f8').reshape(-1,3);index=np.asarray(a['index'],dtype=np.int64).reshape(-1,3);tri=pos[index];assert len(tri)==22735 and A.prior.digest(tri.tobytes())==packet['completeLiteralWorldSHA256']
    selected=sorted(FAILED+CONTINUATION);original={};census={}
    for part in read(A.PARTS)['rows'][0]['parts']:
        needed=set(selected)&set(part['originalFaceIds'])
        if not needed:continue
        pos=np.asarray(part['position'],dtype='<f8').reshape(-1,3);ix=np.asarray(part['index'],dtype=np.int64).reshape(-1,3)
        for local,face in enumerate(part['originalFaceIds']):
            if face in needed:assert face not in original;original[face]=pos[ix[local]];census[face]=part['component']
    assert sorted(original)==selected
    rows=[dict(originalFaceID=i,sourceVertexIndices=index[i].tolist(),actualLiteralXYZ=tri[i].tolist(),savedOriginalXYZ=original[i].tolist(),literalDescriptor=descriptor(i,tri[i]),originalDescriptor=descriptor(i,original[i]),savedCensusComponentContext=census[i],componentIsNotTopologyOrStructuralCredit=True,architecturalRoleAssigned=None)for i in selected]
    shared=shared_edges(tri[7527],tri[16549]);original_shared=shared_edges(original[7527],original[16549]);assert len(shared)==len(original_shared)==1
    raw=packet['rawFoundationVerbatim'];assert not raw['strictFoundationAccepted'];partial=packet['allOtherPartialBelowMinusHalfSourceFaceIDs'];assert len(partial)==278
    save(DOC/'exact-source-facade-bottom-context.json.gz',dict(rows=rows,exactFailedToTallContinuationWholeEdge=dict(failedFaceID=7527,continuationFaceID=16549,exactLiteralXYZ=shared[0],exactSavedOriginalXYZ=original_shared[0],representationsHaveIndependentExactCoordinates=True,sourceRoleNotInferredFromEdgeAlone=True),all278PartialBelowFaceDescriptors=[descriptor(i,tri[i])for i in partial],all278PartialBelowFaceIDs=partial,all281BelowSampleRecordsVerbatim=packet['allBelowMinusHalfSampleSites'],rawFoundationVerbatim=raw,minimumWholeSurfaceGapVerbatim=packet['minimumWholeSurfaceGapVerbatim'],rawOrdinaryReasonsVerbatim=packet['rawOrdinaryReasonsVerbatim'],exactSourceIndexBindingVerbatim=packet['exactSourceIndexBinding'],sourceWorldGroundBindings=dict(UID=A.prior.UID,CSUID=CSUID,sourceSHA256=A.prior.SOURCE_SHA,currentManifestSHA256=A.prior.CURRENT,currentSnapshot=A.prior.SNAPSHOT,completeLiteralWorldSHA256=packet['completeLiteralWorldSHA256'],completeSavedOriginalWorldSHA256=packet['completeSavedOriginalWorldSHA256'],completeActualGroundSHA256=packet['completeActualGroundSHA256'],allCurrentGroundSourceInputRefs=packet['allCurrentGroundSourceInputRefs'],actualRuntimeArrays=packet['actualRuntimeArrays'],savedOriginalCensus=packet['savedFullOriginalSourceCensus']),wholeSourceFaces=22735,actualGroundFaces=584,sourceGeometryChanges=0,strictFoundationAccepted=False,warningResolved=False,physicalAccepted=False,installationApproved=False))
    # Only the original failure's exact twelve sample sites justify the local Y=6 locator.
    assert all(w['height']==6. for row in packet['rows']for w in row['fourUnchangedFoundationSampleWitnesses'])
    fig=draw_2d(tri,FAILED,partial,CONTINUATION)
    import matplotlib.pyplot as plt
    try:fig.savefig(DOC/'full-source-and-facade-context-1800x1200.png',dpi=100)
    finally:plt.close(fig)
    save(DOC/'proposed-existing-warning-applicability.json',dict(proposedOnly=True,rootFunctionalReviewAccepted=False,acceptedReasons=[],candidateExistingReasonScope=['terrain-intersects-source-over-0.5m'],proposedSourceInterpretation='The three upward buried authored triangles form a lower closure strip at a full-height facade continuation rather than an independently identified exposed floor. Exact edge7527/16549 and all eleven original/literal descriptors support review of that specific source context; neither small area nor adjacency alone resolves the warning.',exactFailedFaceIDs=FAILED,completeContinuationFaceIDs=CONTINUATION,all278PartialBelowRetained=True,partialFaceRolesRemainUnassigned=True,rawStrictFoundationPassed=False,rawOrdinaryReasonResolved=False,wholeMinimumGapPreserved=True,noAreaDistanceNormalThresholdWaiver=True,noPerComponentRootEngineeringWatertightnessGate=True,noIndependentFootSupportClaim=True,noSourcePoseScaleOrGeometryChange=True,requiredNextReview='ROOT inspect exact eleven source descriptors and the single saved-source 2D projection export; determine applicability of the existing burial warning to this exact authored context, preserving every partial and raw strict result.',ordinaryFourWorldFiniteForeignSourceCollisionAndCurrentViewerChecksStillPending=True,sourceContext=ref(DOC/'exact-source-facade-bottom-context.json.gz'),contextImage=ref(DOC/'full-source-and-facade-context-1800x1200.png'),priorActualOrdinaryResult=ref(A.prior.DOC/'result.json'),priorActualAttribution=ref(A.DOC/'exact-three-source-face-attribution.json.gz'),priorActualDiagrams=ref(prior.DOC/'saved-source-diagrams.json'),physicalAccepted=False,newlyInstalled=0,installationApproved=False))

def owned():
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__));data,r,p,views,refs=load();refs=distinct_refs(refs+prep['codeRefs']+prep['inputRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'actual-readonly-preparation.json')]);pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def fence():
        pulse(force=True)
        for q in refs:check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==A.prior.CURRENT;pulse(force=True)
    fence()
    with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',r)
    DOC.mkdir();compute(p,views);refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence();module(A.prior.FREEZER,'aqua_facade_context_freezer').freeze(BATCH,'exact-authored-facade-bottom-context-proposed-only-raw-failures-retained',[check(q)for q in refs],dict(uids=[A.prior.UID],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))
def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only()));return
    if '--owned'in sys.argv:return owned()
    assert '--prepare-exact-facade-bottom-review-only'in sys.argv and not DOC.exists()and not LOCAL.exists();data,*_=load();scope=data[-1];prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__));resources=['building:'+u for u in scope]+['terrain-patch:'+u for u in scope]+['immutable-source-proof:'+BATCH];claim=reservations.claim('aqua-facade-context-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
