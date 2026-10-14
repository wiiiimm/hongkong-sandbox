"""ROOT-only saved V3 diagnostic/checkpoint finalization; no model check rerun."""
from pathlib import Path
import hashlib,json,struct,subprocess,sys,uuid
import heritage165054_authentic_tin_owned_ordinary_v3_20261014 as prior
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
ROOT=prior.ROOT;HERE=prior.HERE;BASE=prior.BASE;UID=prior.UID;SOURCE=prior.SOURCE;CURRENT=prior.CURRENT;SNAPSHOT=prior.SNAPSHOT
BATCH='government-xl-heritage165054-owned-saved-output-finalization-v1-20261014';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
TERMINAL=prior.PROPOSAL/'ROOT-TERMINAL.json'
read=prior.read;ref=prior.ref;check=prior.check;save=prior.save

def resources():
    from run import reservations
    return reservations.normalise(['building:'+UID,'terrain-patch:'+UID,'immutable-source-proof:'+BATCH])

def diagnostic_refs():
    # CONTEXT belongs to the nomination module, not nomination.prior.
    return dict(rawHistoricalCurrentTerrainIntersectionAndStrictFalseRetained=ref(prior.old.DOC/'diagnostic.json.gz'),all22PriorSourceBelowMinus05WarningsRetained=ref(prior.nomination.CONTEXT),exact18FourWorldDescriptorsRetained=ref(prior.NOMINATION/'exact18-four-world-source-context.json.gz'),savedCompletedV3Commands=[ref(prior.DOC/('command-'+str(i).zfill(3)+'.json')) for i in range(2)],savedFullFoundation=ref(prior.DOC/'foundation.json'),savedMetrics=ref(prior.DOC/'metrics.json'),savedValidation=ref(prior.DOC/'validation.json'),savedActualGeometry=ref(prior.LOCAL/'runtime-geometry.json.gz'),failedV3Terminal=ref(TERMINAL))

def referenced_files():
    d=diagnostic_refs()
    return d['savedCompletedV3Commands']+[v for k,v in d.items() if k!='savedCompletedV3Commands']

def bind_terminal(t):
    assert t['session']==1885 and t['observedExitCode']==1 and t['supervisorReportedReleased'] is True and t['leaseStillOwned'] is False
    assert t['caller']==ref(Path(prior.__file__)) and t['geometryChecksCompleted'] is True and t['finalCheckpointWritten'] is False and t['modelRejected'] is False
    assert t['failure']=='AttributeError: nomination.prior.CONTEXT missing during diagnostic report construction'
    assert t['completedCommands']==[dict(file='command-000.json',exitCode=0),dict(file='command-001.json',exitCode=0)]

def bind_completed_commands(commands):
    rel=lambda p:str(p.relative_to(ROOT))
    expected=[['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(prior.DOC/'selection.json.gz'),'--candidates',rel(prior.LOCAL),'--terrain-candidates',rel(prior.DOC/'terrain-candidates.json'),'--out',rel(prior.DOC/'metrics.json'),'--geometry-out',rel(prior.LOCAL/'runtime-geometry.json.gz')],['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(prior.LOCAL),'--source-forms',rel(prior.LOCAL/'source-forms.json'),'--terrain-candidates',rel(prior.DOC/'terrain-candidates.json'),'--out',rel(prior.DOC/'validation.json')]]
    assert len(commands)==2
    for c,e in zip(commands,expected):assert c['command']==e and c['exitCode']==0 and c['stderr']==''

def assess_saved():
    metrics=read(prior.DOC/'metrics.json');validation=read(prior.DOC/'validation.json');foundation=read(prior.DOC/'foundation.json')
    assert len(metrics['rows'])==len(foundation['rows'])==1 and metrics['rows'][0]['uid']==foundation['rows'][0]['uid']==UID
    f=foundation['rows'][0];assert f['sourceSHA256']==metrics['rows'][0]['sourceSHA256']==SOURCE and foundation['sourceGeometryChanges']==0
    assert f['foundation']['triangles']==f['foundation']['completeTerrainTriangles']==15140
    strict=f['strictFoundationAccepted'];assert strict==(not f['foundation']['fullyBuriedUpwardTriangles'] and f['foundation']['fullyBuriedAreaFraction']==0)
    runtime=validation['results'];assert len(runtime)==1 and runtime[0]['uid']==UID and runtime[0]['triangles']==15140 and runtime[0]['outcome']=='runtime-accepted-placement-unreviewed'
    clear=not runtime[0]['concerns'] and validation['loaderAccepted']==validation['checksPassed']==1 and validation['exceptions']==0
    identity=read(prior.DOC/'identity.json');policy=prior.module(HERE/'acceptance-policy.py','heritage_saved_finalization_policy')
    reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCE,identityProof=identity['proof']),metrics['rows'][0],metrics['profiles']['mobile'])
    return metrics,validation,strict,clear,reasons

def inputs():
    pins,data=prior.load();bind_terminal(read(TERMINAL));assert read(prior.PROPOSAL/'actual-readonly-preparation.json')['passed']
    commands=[read(prior.DOC/('command-'+str(i).zfill(3)+'.json')) for i in range(2)];bind_completed_commands(commands)
    assert len(list(prior.DOC.glob('command-*.json')))==2 and not (prior.DOC/'diagnostic.json.gz').exists()
    metrics,validation,strict,clear,reasons=assess_saved();refs=data[-1]+pins['codeRefs']+[ref(prior.PROPOSAL/p) for p in ['draft-pins.json','actual-readonly-preparation.json']]+referenced_files()
    for out in [metrics,validation]:refs +=[dict(path=p,sha256=h) for p,h in (out.get('inputHashes') or out.get('hashes')).items()]
    refs +=[ref(p) for folder in [prior.DOC,prior.LOCAL] for p in folder.rglob('*') if p.is_file() and p.name!='reservation.json']
    refs=distinct_refs(refs)
    for q in refs:check(q)
    return data,refs

def load():
    pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__)) and pins['canonicalResources']==resources()
    for q in pins['codeRefs']+pins['inputRefs']:check(q)
    data=inputs();assert data[1]==pins['inputRefs'];return pins,data

def owned():
    from run import reservations
    pins,(data,refs)=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');lease=read(LEASE)
    assert prep['passed'] and reservations.owns(lease) and lease['resources']==resources() and not DOC.exists()
    refs=distinct_refs(refs+pins['codeRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')]);pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def fence():
        pulse(force=True)
        for q in refs:check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(force=True)
    fence()
    geometry=read(prior.LOCAL/'runtime-geometry.json.gz')['rows'];assert len(geometry)==1 and geometry[0]['uid']==UID and geometry[0]['sourceSHA256']==SOURCE
    g=geometry[0];pos=g['position'];idx=g['index'];assert len(pos)==43248*3 and len(idx)==15140*3 and len(g['drawnGroundGeometry'])%9==0
    h=hashlib.sha256()
    for i in idx:assert type(i)is int and 0<=i<43248;h.update(struct.pack('<ddd',*pos[i*3:i*3+3]))
    literal=h.hexdigest();assert literal=='0f1f5703f6fbd6c200a5f11ea5b2b617e7018dcfdd99436f9e0340c22633684f'
    assert ref(prior.LOCAL/data[0][0]['candidate']['entry']['asset'])['sha256']==SOURCE
    metrics,validation,strict,clear,reasons=assess_saved();candidate=data[1][0];DOC.mkdir()
    diagnostic=dict(uid=UID,candidate=candidate,currentManifestSHA256=CURRENT,currentSnapshot=SNAPSHOT,nominationJob=data[3],ordinaryNumericReasons=reasons,rawRuntimeRows=validation['results'],loaderAccepted=validation['loaderAccepted'],runtimeChecksPassed=validation['checksPassed'],runtimeExceptions=validation['exceptions'],strictFoundationAccepted=strict,ownCheapOrdinaryTerrainGatePassed=not reasons and strict and clear,completeOriginalFaces=15140,completeActualDrawnGroundFaces=len(g['drawnGroundGeometry'])//9,actualLiteralWorldSHA256=literal,**diagnostic_refs(),wholeCurrentParentDomainBeforeAfterNativeBASICDeltaStillRequired=True,noFunctionalApplicabilityApprovalTransferred=True,originalStarFootprintRejectionAndRawJunctionCrossingsRetained=True,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0,finalizationOnly=True,noMetricsLoaderFoundationRerun=True)
    save(DOC/'diagnostic.json.gz',diagnostic);refs=distinct_refs(refs+[ref(DOC/'diagnostic.json.gz')]);fence()
    prior.module(prior.old.FREEZER,'heritage_saved_finalization_freezer').freeze(BATCH,'saved-completed-owned-original-checks-finalization-only-no-model-rerun-no-neighbour-install-credit',[check(q) for q in refs],dict(uids=[UID],sourceOnly=True,ownCheapOrdinaryTerrainGatePassed=not reasons and strict and clear,strictFoundationAccepted=strict,wholeCurrentDeltaStillRequired=True,physicalAccepted=False,newlyInstalled=0))

def main():
    if '--schema-only' in sys.argv:
        p,d=load();print(json.dumps(dict(passed=True,caller=ref(Path(__file__)),canonicalResources=resources(),noModelChecksRerun=True,diagnosticRefs=diagnostic_refs())));return
    if '--owned' in sys.argv:return owned()
    assert sys.argv[1:]==['--finalize-saved-owned-outputs-only'] and not DOC.exists() and not LOCAL.exists();p,d=load();assert read(PROPOSAL/'actual-readonly-preparation.json')['passed']
    from run import reservations
    claim=reservations.claim('heritage-saved-finalization-'+str(uuid.uuid4()),resources(),batch=BATCH,ttl=3600)
    if not claim['ok']:print(json.dumps(prior.claim_failure_record(claim)));raise RuntimeError('Saved-output finalization reservation denied')
    lease=claim['reservation']
    try:
        save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
