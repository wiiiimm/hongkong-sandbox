"""ROOT-only cached6653 source/entry/whole-unused-bound reconciliation; no re-decode."""
from pathlib import Path
import json,subprocess,sys,uuid
import heritage165054_exact18_saved_source_views_v1_20261014 as source
from heritage_saved_native_bounds_binding_v1_20261014 import bind_record,closed_disjoint,encoded
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
ROOT=source.ROOT;HERE=source.HERE;BASE=source.BASE;UID=source.UID;CURRENT=source.CURRENT
BATCH='government-xl-heritage165054-saved-current-native-bounds-reconciliation-v1-20261014';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
read=source.read;ref=source.ref;check=source.check;save=source.save
REVIEW=BASE/'government-xl-heritage165054-exact18-lower-closure-applicability-review-v1-20261014/ROOT-existing-warning-applicability.json'
PACKETS=[('government-xl-complete-current-native-actual-position-matrix-bounds-v4-20261012','8614ecb76819b66f4dc97e0a840fc17532f25896d54e971d3c060332d644085e','inventory.json.gz','rows'),('government-xl-complete-native-actual-position-post-nam-delta-v1-20261013','2202e62655e42b58e4e277e10dc2018be4e69ac99c4ef0b487cf5c98db8d239c','inventory.json.gz','rows'),('government-xl-polyu-whole-actor-current-ground-delta3-v1-20261014','0d3f5c3eb6569ab431cdc719057068ef4883c71ea3a5279f47677451637eaa24','actual-delta3-native-position-bounds.json.gz','deltaRows')]
def resources():
    from run import reservations
    return reservations.normalise(['building:'+UID,'terrain-patch:'+UID,'immutable-source-proof:'+BATCH])
def inputs():
    p,refs=source.load();review=read(REVIEW);assert ref(REVIEW)['sha256']=='b6ce3cb1a68720ece7b0e5e96c8d92918cde4cbcab6ed7747e02419e2c64bb22' and review['rootFunctionalReviewAccepted'] and not review['physicalAccepted'] and not review['installationApproved']
    current=read(ROOT/'3d-viewer/city/data/manifest.json');assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
    entries={};refs=refs+[ref(REVIEW)];roots=[]
    for url in current['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;cat=read(path);assert cat['rootTranslation']==[-834500,0,816500]
        refs.append(ref(path));roots.append(cat['rootTranslation'])
        for e in cat['models']:assert e['uid']not in entries;entries[e['uid']]=e
    assert len(entries)==6653
    declared={};bounds={};origin={};receipts=[];expectedCounts=[6649,1,3]
    for packetIndex,(folder,job,file,key) in enumerate(PACKETS):
        d=BASE/folder;r=read(d/'result.json');assert r['jobId']==job
        inp=read(d/'input.json.gz');inv=read(d/file);assert len(inp[key])==len(inv['rows'])==expectedCounts[packetIndex];receipts.append((d,job,r));packetRefs=dict(input=ref(d/'input.json.gz'),inventory=ref(d/file),receipt=ref(d/'result.json'),jobId=job)
        for packetKey in ['input','inventory']:
            q=packetRefs[packetKey];assert q in r['evidenceRefs'];refs.append(q)
        refs.append(packetRefs['receipt'])
        refs +=[q for q in r['evidenceRefs'] if q['path'].endswith(('.mjs','.js','.wasm')) or '/exact_packed_world_'in q['path']]
        for a in inp[key]:assert a['uid']not in declared;declared[a['uid']]=a;refs.append(a['source'])
        for a in inv['rows']:assert a['uid']not in bounds;bounds[a['uid']]=a;origin[a['uid']]=packetRefs
    assert set(declared)==set(bounds)==set(entries) and len(bounds)==6653
    for uid in entries:
        # Exact identity/schema only here; geographic arithmetic is ROOT owned-phase.
        bind_record(entries[uid],declared[uid],bounds[uid])
    scope=read(source.completed.prior.nomination.prior.north.DOC/'proposal-input.json');assert scope['region']==[2492.5,-10047.5,2772.5,-9837.5]
    refs=distinct_refs(refs+[ref(source.completed.prior.nomination.prior.north.DOC/'proposal-input.json')])
    for q in refs:check(q)
    return entries,declared,bounds,origin,scope,receipts,refs
def load():
    p=read(PROPOSAL/'draft-pins.json');assert p['caller']==ref(Path(__file__)) and p['canonicalResources']==resources()
    for q in p['codeRefs']+p['inputRefs']:check(q)
    d=inputs();assert d[-1]==p['inputRefs'];return p,d
def owned():
    from run import reservations,connect
    p,d=load();entries,declared,bounds,origin,scope,receipts,refs=d;prep=read(PROPOSAL/'actual-readonly-preparation.json');lease=read(LEASE);assert prep['passed']and reservations.owns(lease)and lease['resources']==resources()and not DOC.exists()
    refs=distinct_refs(refs+p['codeRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')]);pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def fence():
        pulse(force=True)
        for q in refs:check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(force=True)
    fence()
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder,job,result in receipts:assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',result)
    domain=scope['region'];rows=[]
    for uid in sorted(entries):
        boxes=bind_record(entries[uid],declared[uid],bounds[uid]);disjoint=closed_disjoint(boxes,domain)
        rows.append(dict(uid=uid,sourceSHA256=entries[uid]['sha256'],currentRawEntry=entries[uid],completeCurrentEntryByteIdenticalToSavedDeclaration=True,completePositionVertices=bounds[uid]['completePositionVertices'],completeFaces=bounds[uid]['completeFaces'],completeFourUnusedWorldBoundsVerbatim=boxes,strictAllFourClosedDomainDisjoint=disjoint,wholeCurrentActorBeforeAfterRequired=not disjoint,cachedActualBoundsProvenance=origin[uid],nativeInstallationApprovalTransferred=False));pulse()
    touching=[r['uid']for r in rows if not r['strictAllFourClosedDomainDisjoint']];actors=scope['scope']['allActorsForNominationLease'];unknown={r['uid']for r in scope['scope']['missingOrChangedWholeBoundsActorsRetained']}
    DOC.mkdir();save(DOC/'complete6653-current-native-bounds-reconciliation.json.gz',dict(rows=rows,completeCurrentNativeActors=6653,fullParentClosedDomain=domain,currentManifestSHA256=CURRENT,currentSnapshot=source.SNAPSHOT,wholeCurrentNativeTouchingUIDs=touching,touchingNativeOutsideNominationScope=sorted(set(touching)-set(actors)),all22PriorUnknownUIDsRetained=sorted(unknown),priorUnknownUIDsProvedOutside=[u for u in sorted(unknown)if u not in touching],all45NominationActorsRetained=actors,all91FuturePhysicalResourcesRetained=source.completed.prior.read(source.completed.prior.PROPOSAL/'draft-pins.json')['futurePhysicalQualificationResources'],exact18ConditionalSourceFeatureReview=ref(REVIEW),ordinarySampledNumericFailureRemains=True,beforeAfterExteriorRendererAndFullBASICFiniteStillRequired=True,noSourceDecodeOrModelLoaderRerun=True,noIdentityFoundationRoleOrFiniteRerun=True,noOtherSourceApprovalTransferred=True,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
    refs=distinct_refs(refs+[ref(p)for p in DOC.iterdir()if p.is_file()]);fence();source.completed.prior.module(source.completed.prior.old.FREEZER,'heritage_cached_bounds_freezer').freeze(BATCH,'exact-current-entry-cached-whole-unused-native-bounds-parent-domain-reconciliation-no-model-rerun',[check(q)for q in refs],dict(uids=[UID],sourceOnly=True,completeNativeActors=6653,physicalAccepted=False,newlyInstalled=0))
def main():
    if '--schema-only'in sys.argv:
        p,d=load();print(json.dumps(dict(passed=True,caller=ref(Path(__file__)),currentNativeActors=len(d[0]),allCurrentEntryDeclarationsExactlyBound=True,canonicalResources=resources(),noSourceDecodeBoundsArithmeticDBLeaseWorker=True)));return
    if '--owned'in sys.argv:return owned()
    assert sys.argv[1:]==['--reconcile-saved-current-bounds-only']and not DOC.exists()and not LOCAL.exists();p,d=load();assert read(PROPOSAL/'actual-readonly-preparation.json')['passed']
    from run import reservations
    c=reservations.claim('heritage-cached-bounds-'+str(uuid.uuid4()),resources(),batch=BATCH,ttl=3600)
    if not c['ok']:print(json.dumps(source.completed.prior.claim_failure_record(c)));raise RuntimeError('Cached bounds reservation denied')
    lease=c['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
