"""ROOT-only complete original four-world +23 BASIC before/after finite checks.
No strict warning relabelling, contact re-audit or source decode.
"""
from pathlib import Path
from fractions import Fraction as F
import json,sys,time,uuid,subprocess
import numpy as np
import heritage165054_parent_basic_production_capture_v1_20261014 as capture
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from upton_parent_tin_regression_bookkeeping_v1_20261012 import sha,triangles,finite_record
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
ROOT=capture.ROOT;HERE=capture.HERE;BASE=capture.BASE;UID=capture.UID;CURRENT=capture.CURRENT;SNAPSHOT=capture.SNAPSHOT
BATCH='government-xl-heritage165054-saved-full-actor-finite-v1-20261014';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
read=capture.read;ref=capture.ref;check=capture.check;save=capture.save
SOURCE=BASE/'government-xl-heritage165054-source-context-draft-v1-20261014/source-context-output-v1/complete-original-array.json.gz'
WORLDS=BASE/'government-xl-heritage165054-starmart57455-current-finite-collision-draft-v2-20261014/collision-output-v2/complete-current-star-and-museum-geometry.json.gz'
FAILED=[12130,12131,12132,12150,12191,12192,12193,12194,12195,12199,12201,12202,12203,12249,12288,12290,12292,12293]
def resources(actors):
    from run import reservations
    return reservations.normalise([r for r in capture.resources(actors)if not r.startswith('immutable-source-proof:')]+['immutable-source-proof:'+BATCH])
def inputs(job):
    pins,data,actors,refs=capture.load();r=read(capture.DOC/'result.json');v=read(capture.DOC/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==job and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased']
    report=read(capture.DOC/'actual-production-capture-report.json.gz');assert report['startEndAllInputsVerified']and report['strictOutsideParentAndActorROIDrawUnchanged']and report['completeCurrentBASICActors']==23
    basic=read(capture.DOC/'complete23-current-basic-constructor-streams.json.gz');assert len(basic['rows'])==23 and {r['uid']for r in basic['rows']}==set(actors)and basic['completeActorROI']==report['completeActorROI']
    original=read(SOURCE);worlds=read(WORLDS);assert original['uid']==worlds['uid']==UID and original['sourceSHA256']==worlds['sourceSHA256']==capture.bounds.source.SOURCE and original['completeOriginalFaceCount']==worlds['completeOriginalFaceCount']==15140 and len(original['completeOrderedOriginalTriangles'])==15140 and len(worlds['completeOriginalIndex'])==45420 and worlds['startAndEndInputsVerified']
    review=read(capture.bounds.REVIEW);assert ref(capture.bounds.REVIEW)['sha256']=='b6ce3cb1a68720ece7b0e5e96c8d92918cde4cbcab6ed7747e02419e2c64bb22'and review['exactFailedSampleSourceFaceIDs']==FAILED and review['rootFunctionalReviewAccepted']and not review['rawOrdinaryReasonResolved']and not review['physicalAccepted']and not review['installationApproved']
    refs=distinct_refs(refs+pins['codeRefs']+r['evidenceRefs']+[ref(capture.DOC/p)for p in ['result.json','ROOT-VERIFIED.json','actual-production-capture-report.json.gz','complete23-current-basic-constructor-streams.json.gz','complete-before-ground.json.gz','complete-candidate-ground.json.gz','neighbour-checks.json']]+[ref(SOURCE),ref(WORLDS),ref(capture.bounds.REVIEW)])
    for q in refs:check(q)
    return data,actors,r,report,basic,review,refs

def load(job):
    p=read(PROPOSAL/'draft-pins.json');assert p['caller']==ref(Path(__file__))and p['captureJob']==job
    for q in p['codeRefs']+p['inputRefs']:check(q)
    d=inputs(job);assert p['inputRefs']==d[-1]and p['canonicalResources']==resources(d[1]);return p,d

def worlds(basic):
    original=read(SOURCE);saved=read(WORLDS);idx=np.asarray(saved['completeOriginalIndex'],dtype=np.int64).reshape(-1,3)
    own={'providerOriginal':triangles(original['completeOrderedOriginalTriangles'])}
    for mode,key in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeLeftFloat32WorldPosition'),('explicitBalancedF32','completeBalancedFloat32WorldPosition')]:own[mode]=triangles(np.asarray(saved[key],dtype='<f8').reshape(-1,3)[idx])
    assert sha(own['providerOriginal'])==original['worldTrianglesSHA256']=='258ac5cbe505d4f78f8cd334e1b6bbd3e3a56bcd6ef4e1854865f1dade75e8c7'and sha(own['literal'])=='0f1f5703f6fbd6c200a5f11ea5b2b617e7018dcfdd99436f9e0340c22633684f'
    result=[dict(uid=UID,role='complete-owned-original',worlds=own)]
    for row in basic['rows']:
        modes={}
        for mode in ['constructorFloat32World','leftFloat32World','balancedFloat32World']:
            parts=[]
            for mesh in row['meshes']:
                positions=np.asarray(mesh['streams'][mode],dtype='<f8').reshape(-1,3);ix=np.asarray(mesh['index'],dtype=np.int64).reshape(-1,3);assert len(positions)==mesh['completePositionVerticesIncludingUnused']and len(ix)==mesh['completeIndexedFaces'];parts.append(positions[ix])
            modes[mode]=triangles(np.concatenate(parts));assert len(modes[mode])==row['completeFaces']
        result.append(dict(uid=row['uid'],role='owned-current-BASIC-context'if row['uid']==UID else'current-BASIC-neighbour',worlds=modes))
    assert len(result)==24 and len(result[0]['worlds'])==4;return result

def calculate(data,report,basic,review,pulse):
    before=triangles(np.asarray(read(capture.DOC/'complete-before-ground.json.gz')['completeRelevantDrawnTriplets'],dtype='<f8').reshape(-1,3,3));after=triangles(np.asarray(read(capture.DOC/'complete-candidate-ground.json.gz')['completeRelevantDrawnTriplets'],dtype='<f8').reshape(-1,3,3))
    old=CompleteGround(before);new=CompleteGround(after);roi=np.asarray(report['completeActorROI']);actors=worlds(basic);cache={};mode_cache={};results=[];clock=time.monotonic()
    for actor_index,actor in enumerate(actors):
        modes=[]
        for mode,world in actor['worlds'].items():
            assert np.all(world[:,:,[0,2]]>=roi[:2])and np.all(world[:,:,[0,2]]<=roi[2:]);wsha=sha(world);key=(wsha,old.ground_sha,new.ground_sha);reused=key in mode_cache
            if not reused:
                chunks=[];pending=[];current_failed=[];candidate_failed=[];introduced=[];missing=[]
                def flush():
                    nonlocal pending
                    if not pending:return
                    path=DOC/'chunks'/str(actor_index).zfill(2)/mode/(str(len(chunks)).zfill(5)+'.json.gz');assert not path.exists();save(path,dict(uid=actor['uid'],role=actor['role'],mode=mode,completeWorldSHA256=wsha,beforeGroundSHA256=old.ground_sha,afterGroundSHA256=new.ground_sha,rows=pending));chunks.append(ref(path));pending=[];pulse(force=True)
                for i,face in enumerate(world):
                    exact=[[F(float(x))for x in q]for q in face.tolist()];oid,ob=old.select(exact);nid,nb=new.select(exact);findings=[]
                    for ground,ids in [(before,oid),(after,nid)]:
                        k=(sha(face),sha(ground[ids]))
                        if k not in cache:cache[k]=finite_record(face,ground[ids])
                        findings.append(cache[k])
                    current,candidate=findings
                    pending.append(dict(sourceFace=i,sourceFaceSHA256=sha(face),currentCompleteSelectedGround=ob,candidateCompleteSelectedGround=nb,current=current,candidate=candidate,exactCompleteRelevantTupleReuse=current is candidate,noKernelHashOrNegativeContextRelabelling=True,noSourceRoleOrAcceptanceCredit=True))
                    if not current['ordinaryBoundProved']:current_failed.append(i)
                    if not candidate['ordinaryBoundProved']:candidate_failed.append(i)
                    if current['ordinaryBoundProved']and not candidate['ordinaryBoundProved']:introduced.append(i)
                    if not candidate['projectionCovered']:missing.append(i)
                    if len(pending)==64:flush()
                    pulse()
                    if time.monotonic()-clock>=20:print(json.dumps(dict(uid=actor['uid'],mode=mode,faces=i+1,total=len(world))),flush=True);clock=time.monotonic()
                flush();mode_cache[key]=dict(chunks=chunks,completeFaces=len(world),currentOrdinaryUnproved=current_failed,candidateOrdinaryUnproved=candidate_failed,currentClearCandidateUnproved=introduced,candidateUncovered=missing)
            findings=mode_cache[key];modes.append(dict(mode=mode,wholeWorldSHA256=wsha,completeFaces=len(world),findings=findings,exactCompleteWorldAndBothGroundModeReuse=reused,ownedCandidateUnprovedOutsideConditional18=sorted(set(findings['candidateOrdinaryUnproved'])-set(FAILED))if actor['role']=='complete-owned-original'else None,existingConditional18ReviewNotAutomaticallyFiniteApproval=True));pulse(force=True)
        results.append(dict(uid=actor['uid'],role=actor['role'],worlds=modes,allSourceFacesAccounted=True))
    old.verify_binding();new.verify_binding()
    save(DOC/'complete-current-candidate-full-actor-finite.json.gz',dict(rows=results,completeOwnedOriginalFaces=15140,completeOwnedFourWorlds=True,currentBASICActorsIncludingOwnedContext=23,otherBASICActors=22,beforeGroundSHA256=old.ground_sha,afterGroundSHA256=new.ground_sha,completeActorROI=report['completeActorROI'],allRawNegativesZerosAndUncoveredRetained=True,rawMuseumMetricAnd22SamplesRetained=ref(capture.bounds.source.completed.DOC/'diagnostic.json.gz'),conditionalExact18Review=ref(capture.bounds.REVIEW),conditionalReviewDoesNotExtendToNewFiniteNegativeFeatures=True,oldNativeOutside6653CertificateRetained=ref(capture.bounds.DOC/'complete6653-current-native-bounds-reconciliation.json.gz'),ordinaryNeighbourChecks=ref(capture.DOC/'neighbour-checks.json'),StarFootprintRejectionAndRaw14Current8OriginalContactsRetained=True,noContactExemption=True,noCollisionLoaderFoundationSourceDecodeOrViewsReplayed=True,noNewEngineeringRootOrWatertightnessGate=True,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0))

def owned(job):
    from run import reservations,connect
    p,d=load(job);data,actors,receipt,report,basic,review,refs=d;lease=read(LEASE);prep=read(PROPOSAL/'actual-readonly-preparation.json');assert reservations.owns(lease)and lease['resources']==resources(actors)and prep['passed']and not DOC.exists()
    refs=distinct_refs(refs+p['codeRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')]);pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def fence():
        pulse(force=True)
        for q in refs:check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(force=True)
    fence()
    with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',receipt)
    DOC.mkdir();calculate(data,report,basic,review,pulse);refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence();capture.bounds.source.completed.prior.module(capture.bounds.source.completed.prior.old.FREEZER,'heritage_full_finite_freezer').freeze(BATCH,'complete-owned15140-four-world-and23-current-BASIC-current-candidate-full-finite-raw-negatives-retained',[check(q)for q in refs],dict(uids=[UID],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))

def main():
    job=sys.argv[sys.argv.index('--capture-job')+1]
    if '--schema-only'in sys.argv:
        p,d=load(job);print(json.dumps(dict(passed=True,captureJob=job,canonicalResources=resources(d[1]),ownedSourceFaces=15140,ownedWorlds=4,currentBASICActorsIncludingOwnedContext=23,noSourceWorldFiniteDBLeaseWorker=True)));return
    if '--owned'in sys.argv:return owned(job)
    assert '--complete-saved-full-actor-finite-only'in sys.argv and not DOC.exists()and not LOCAL.exists();p,d=load(job);assert read(PROPOSAL/'actual-readonly-preparation.json')['passed']
    from run import reservations
    c=reservations.claim('heritage-full-finite-'+str(uuid.uuid4()),resources(d[1]),batch=BATCH,ttl=3600)
    if not c['ok']:print(json.dumps(capture.bounds.source.completed.prior.claim_failure_record(c)));raise RuntimeError('Full finite reservation denied')
    lease=c['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--capture-job',job,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
