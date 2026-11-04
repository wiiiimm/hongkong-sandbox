"""ROOT-only parent/BASIC production capture and ordinary neighbour delta; no owned replay."""
from pathlib import Path
import json,subprocess,sys,uuid
import heritage165054_saved_current_native_bounds_reconciliation_v1_20261014 as bounds
from heritage_parent_capture_scope_binding_v1_20261014 import bind_scope,bind_current_forms
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
ROOT=bounds.ROOT;HERE=bounds.HERE;BASE=bounds.BASE;UID=bounds.UID;CURRENT=bounds.CURRENT;SNAPSHOT=bounds.source.SNAPSHOT
BATCH='government-xl-heritage165054-parent-basic-production-capture-v1-20261014';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
RUNTIME=HERE/'heritage165054_parent_basic_production_capture_runtime_v1_20261014.mjs';JOB='7f76fac77c7fcb2319026e7f1eb580c7f8b26322164daf04c99135f4fa579df2'
read=bounds.read;ref=bounds.ref;check=bounds.check;save=bounds.save

def resources(actors):
    from run import reservations
    assert len(actors)==len(set(actors))==23 and UID in actors
    return reservations.normalise([('building:'if u.startswith('landsd/')else'foreign-form:')+u for u in actors]+['terrain-patch:'+u for u in actors]+['immutable-source-proof:'+BATCH])

def inputs():
    r=read(bounds.DOC/'result.json');v=read(bounds.DOC/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==JOB and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased']
    scope=read(bounds.source.completed.prior.nomination.prior.north.DOC/'proposal-input.json');certificate=read(bounds.DOC/'complete6653-current-native-bounds-reconciliation.json.gz');forms,actors=bind_scope(scope,certificate,UID)
    tiles={};refs=[]
    for f in forms:
        q=f['tileRef'];check(q)
        if f['tile']not in tiles:tiles[f['tile']]=read(ROOT/'3d-viewer'/f['tile']);refs.append(q)
    bind_current_forms(forms,tiles)
    candidate=read(bounds.source.completed.prior.NOMINATION/'terrain-candidates.json');assert len(candidate)==1 and candidate[0]['uids']==[UID]and candidate[0]['triangles']==8341 and candidate[0]['sha256']=='21216b7acafb198484957ce604fa89555df57d7f574930f7a9a28b3b7a508fc1'
    current=read(ROOT/'3d-viewer/city/data/manifest.json');assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
    refs += r['evidenceRefs']+[ref(bounds.DOC/p)for p in ['result.json','ROOT-VERIFIED.json','complete6653-current-native-bounds-reconciliation.json.gz']]
    refs +=[ref(bounds.REVIEW),ref(bounds.source.completed.DOC/'diagnostic.json.gz'),ref(bounds.source.completed.prior.LOCAL/'runtime-geometry.json.gz'),ref(bounds.source.completed.prior.NOMINATION/'terrain-candidates.json'),dict(path=candidate[0]['path'],sha256=candidate[0]['sha256']),ref(ROOT/'3d-viewer/city/data/manifest.json'),ref(ROOT/'3d-viewer/city/data/terrain.json')]
    refs +=[ref(ROOT/'3d-viewer'/p['url'])for p in current['terrainPatches']]
    refs=distinct_refs(refs)
    for q in refs:check(q)
    return dict(schema='heritage-parent-basic-production-capture-v1',ownedUID=UID,currentManifestSHA256=CURRENT,currentSnapshot=SNAPSHOT,parentDomain=scope['region'],ownedFourWorldUnusedBounds=scope['completeFourWorldUnusedMuseumBounds'],currentForms=forms,candidate=candidate[0],allInputRefs=refs,verifiedNativeBoundsJob=JOB,all6653NativeOutsideCertificate=ref(bounds.DOC/'complete6653-current-native-bounds-reconciliation.json.gz'),all45HistoricalNominationActorsRetained=scope['scope']['allActorsForNominationLease'],ownMuseumIsOneOf23CurrentBASICForms=True,otherCurrentBASICUIDs=[u for u in actors if u!=UID],sourceGeometryChanges=0,physicalAccepted=False),actors,refs

def load():
    p=read(PROPOSAL/'draft-pins.json');assert p['caller']==ref(Path(__file__))
    for q in p['codeRefs']+p['inputRefs']:check(q)
    data,actors,refs=inputs();assert refs==p['inputRefs']and resources(actors)==p['canonicalResources'];return p,data,actors,refs

def owned():
    from run import reservations,connect
    p,data,actors,refs=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');lease=read(LEASE);assert prep['passed']and reservations.owns(lease)and lease['resources']==resources(actors)and not DOC.exists()
    refs=distinct_refs(refs+p['codeRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')]);pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def fence():
        pulse(force=True)
        for q in refs:check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(force=True)
    fence()
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',read(bounds.DOC/'result.json'))
    DOC.mkdir();save(DOC/'input.json.gz',data)
    save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=f['building'],patchIndexes=[0],existingNative=False)for f in data['currentForms']],inputHashes={f['tileRef']['path']:f['tileRef']['sha256']for f in data['currentForms']},candidateIds=[UID],patches=[data['candidate']]))
    def call(command):
        fence();r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);path=DOC/('command-'+str(len(list(DOC.glob('command-*.json')))).zfill(3)+'.json');save(path,dict(command=command,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr));fence();assert r.returncode==0,path
    rel=str(DOC.relative_to(ROOT));call(['node',str(RUNTIME),rel]);call(['node',str(HERE/'check-neighbours.mjs'),rel+'/'])
    capture=read(DOC/'actual-production-capture-report.json.gz');neighbours=read(DOC/'neighbour-checks.json');assert capture['strictOutsideParentAndActorROIDrawUnchanged']and capture['completeCurrentBASICActors']==23 and {r['uid']for r in neighbours['rows']}==set(actors)
    save(DOC/'diagnostic.json.gz',dict(uid=UID,currentManifestSHA256=CURRENT,currentSnapshot=SNAPSHOT,verifiedWholeNativeBoundsJob=JOB,completeNativeActorsOutsideFullParentDomain=6653,priorUnknown22OutsideCertificatesRetained=True,currentBASICActorsIncludingOwnedMuseum=23,otherBASICActors=22,exactCurrentActorUIDs=actors,completeOwnOriginalSourceFaces=15140,rawOwnedMetricAnd22SamplesRetained=ref(bounds.source.completed.DOC/'diagnostic.json.gz'),exact18ConditionalApplicabilityOnly=ref(bounds.REVIEW),ordinaryNeighbourRowsVerbatim=neighbours['rows'],ordinaryNeighbourRegressions=[r for r in neighbours['rows']if r['reasons']],actualProductionCaptureVerbatim=capture,completeOwnFourWorldAndBASICFinitePending=True,noNativeAcceptanceTransferred=True,noOwnedMetricsLoaderFoundationIdentityOrSourceViewRerun=True,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
    refs=distinct_refs(refs+[ref(p)for p in DOC.iterdir()if p.is_file()]);fence();bounds.source.completed.prior.module(bounds.source.completed.prior.old.FREEZER,'heritage_parent_capture_freezer').freeze(BATCH,'complete-parent-exterior-draw-and23-current-basic-production-capture-with-ordinary-neighbour-delta-no-owned-rerun',[check(q)for q in refs],dict(uids=[UID],sourceOnly=True,currentBASICActors=23,physicalAccepted=False,newlyInstalled=0))

def main():
    if '--schema-only'in sys.argv:
        p,d,a,r=load();print(json.dumps(dict(passed=True,caller=ref(Path(__file__)),currentBASICActorsIncludingMuseum=len(a),otherBASICActors=22,actorUIDs=a,canonicalResources=resources(a),noSourceGeometryRendererDBLeaseWorker=True)));return
    if '--owned'in sys.argv:return owned()
    assert sys.argv[1:]==['--capture-parent-and-basic-neighbours-only']and not DOC.exists()and not LOCAL.exists();p,d,a,r=load();assert read(PROPOSAL/'actual-readonly-preparation.json')['passed']
    from run import reservations
    c=reservations.claim('heritage-parent-capture-'+str(uuid.uuid4()),resources(a),batch=BATCH,ttl=3600)
    if not c['ok']:print(json.dumps(bounds.source.completed.prior.claim_failure_record(c)));raise RuntimeError('Parent capture reservation denied')
    lease=c['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
