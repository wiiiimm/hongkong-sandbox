"""ROOT-only two saved-source orthographic visuals; no geometry/sampling rerun."""
from pathlib import Path
import json,subprocess,sys,uuid
import heritage165054_owned_saved_output_finalization_v1_20261014 as completed
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
from heritage18_saved_orthographic_visuals_v1_20261014 import bind_groups,render_saved
ROOT=completed.ROOT;HERE=completed.HERE;BASE=completed.BASE;UID=completed.UID;SOURCE=completed.SOURCE;CURRENT=completed.CURRENT;SNAPSHOT=completed.SNAPSHOT
BATCH='government-xl-heritage165054-exact18-saved-source-views-v1-20261014';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';JOB='3308047352b9f55b2deac74a0b90600120e7524b3d63cf8f5b95c83c167351a0'
read=completed.read;ref=completed.ref;check=completed.check;save=completed.save

def resources():
    from run import reservations
    return reservations.normalise(['building:'+UID,'terrain-patch:'+UID,'immutable-source-proof:'+BATCH])

def inputs():
    pins,data=completed.load();r=read(completed.DOC/'result.json');v=read(completed.DOC/'ROOT-VERIFIED.json')
    assert r['jobId']==v['jobId']==JOB and v['exactNeonReadback'] and v['allEvidenceHashesVerified'] and v['leaseReleased']
    raw=read(completed.DOC/'diagnostic.json.gz');assert raw['uid']==UID and raw['strictFoundationAccepted'] is True and raw['ordinaryNumericReasons']==['terrain-intersects-source-over-0.5m'] and raw['noMetricsLoaderFoundationRerun'] is True
    packet=read(completed.prior.NOMINATION/'exact18-four-world-source-context.json.gz');bind_groups(packet)
    assert packet['uid']==UID and packet['sourceSHA256']==SOURCE and packet['CSUID']=='3712526467T20050430'
    refs=distinct_refs(data[1]+pins['codeRefs']+r['evidenceRefs']+[ref(completed.DOC/p)for p in ['result.json','ROOT-VERIFIED.json','diagnostic.json.gz']])
    for q in refs:check(q)
    return refs

def load():
    p=read(PROPOSAL/'draft-pins.json');assert p['caller']==ref(Path(__file__)) and p['canonicalResources']==resources()
    for q in p['codeRefs']+p['inputRefs']:check(q)
    r=inputs();assert r==p['inputRefs'];return p,r

def owned():
    from run import reservations
    p,refs=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');lease=read(LEASE);assert prep['passed'] and reservations.owns(lease) and lease['resources']==resources() and not DOC.exists()
    refs=distinct_refs(refs+p['codeRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')]);pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def fence():
        pulse(force=True)
        for q in refs:check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(force=True)
    fence();packet=read(completed.prior.NOMINATION/'exact18-four-world-source-context.json.gz');rows=read(completed.prior.LOCAL/'runtime-geometry.json.gz')['rows'];assert len(rows)==1 and rows[0]['uid']==UID and rows[0]['sourceSHA256']==SOURCE
    DOC.mkdir();images,panels=render_saved(packet,rows[0],DOC);assert len(images)==2
    save(DOC/'saved-source-interpretation-context.json',dict(uid=UID,CSUID=packet['CSUID'],sourceSHA256=SOURCE,currentManifestSHA256=CURRENT,currentSnapshot=SNAPSHOT,completedOrdinaryFinalizationJob=JOB,completedOrdinaryDiagnostic=ref(completed.DOC/'diagnostic.json.gz'),savedLiteralWorldAndGround=ref(completed.prior.LOCAL/'runtime-geometry.json.gz'),exact18FourWorldDescriptors=ref(completed.prior.NOMINATION/'exact18-four-world-source-context.json.gz'),images=[ref(p)for p in images],panels=panels,all22WitnessesRetainedVerbatim=packet['all22SavedBelowMinus05WitnessesVerbatim'],sourceRoleAssigned=False,warningResolved=False,ordinaryNumericReasonRetained='terrain-intersects-source-over-0.5m',rawStrictFoundationOnOldCurrentTerrainFalseRetained=True,actualPrivateTINStrictFoundationTrue=True,globalBottomResolutionNotApplicable=True,noTinyAreaNormalAdjacencyWaiver=True,displayOnlyOrthographicProjectionsNotSections=True,projectedVisibilityNotLiveVisibility=True,GPUFloat32RecastUsed=False,originalSourcePoseChanges=0,sourceGeometryChanges=0,newTerrainConstruction=False,noMetricsLoaderFoundationSamplerRerun=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
    refs=distinct_refs(refs+[ref(p)for p in DOC.iterdir()if p.is_file()]);fence()
    completed.prior.module(completed.prior.old.FREEZER,'heritage18_source_views_freezer').freeze(BATCH,'two-saved-literal-source-ground-orthographic-context-views-no-functional-or-installation-decision',[check(q)for q in refs],dict(uids=[UID],sourceOnly=True,sourceRoleAssigned=False,warningResolved=False,physicalAccepted=False,newlyInstalled=0))

def main():
    if '--schema-only'in sys.argv:
        p,r=load();print(json.dumps(dict(passed=True,caller=ref(Path(__file__)),canonicalResources=resources(),savedFinalizationJob=JOB,imagesPlanned=2,noModelChecksRendererDBLeaseWorker=True)));return
    if '--owned'in sys.argv:return owned()
    assert sys.argv[1:]==['--render-two-saved-source-views-only'] and not DOC.exists() and not LOCAL.exists();p,r=load();assert read(PROPOSAL/'actual-readonly-preparation.json')['passed']
    from run import reservations
    c=reservations.claim('heritage18-source-views-'+str(uuid.uuid4()),resources(),batch=BATCH,ttl=3600)
    if not c['ok']:print(json.dumps(completed.prior.claim_failure_record(c)));raise RuntimeError('Saved source view reservation denied')
    lease=c['reservation']
    try:
        save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
