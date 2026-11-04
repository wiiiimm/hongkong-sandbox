"""ROOT-only cheap Museum actual owned replay on a fresh validated private TIN candidate."""
from pathlib import Path
import copy,gzip,json,subprocess,sys,uuid
import heritage165054_current_ordinary_physical_v1_20261014 as old
import heritage165054_two_tin_nearwater_bare_nomination_v1_20261014 as nomination
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
ROOT=old.ROOT; HERE=old.HERE; BASE=old.BASE; UID=old.UID; CURRENT=old.CURRENT; SNAPSHOT=old.SNAPSHOT; SOURCE=old.SOURCE
BATCH='government-xl-heritage165054-authentic-tin-owned-ordinary-v3-20261014'; DOC=BASE/BATCH; PROPOSAL=BASE/(BATCH+'-proposal'); LOCAL=HERE/'local'/BATCH; LEASE=LOCAL/'reservation.json'; NOMINATION=nomination.DOC
NOMINATION_JOB="988599c9728d0b779dd55a5783690de40c3ddbb83b1639675e0b3a8fec222d45"
read=old.read; ref=old.ref; check=old.check; module=old.module; save=old.save

def bind_candidate(packet,candidates,patch):
    assert packet['uid']==UID and packet['sourceGeometryChanges']==packet['sourcePoseChanges']==0 and not packet['physicalAccepted'] and not packet['installationApproved']
    c=packet['construction']; assert c['bareExistingValidatorPassed'] is True and c['candidate'] is not None and candidates==[c['candidate']]
    candidate=candidates[0]; assert candidate['uids']==[UID] and candidate['cells']==patch['coarseCells']==[528,306,532,309] and candidate['bounds']==[2492.5,-10047.5,2772.5,-9837.5]
    assert patch['meta']['targetUids']==[UID] and patch['meta']['parentTerrain']=='city/data/terrain.json' and type(patch['nativeMesh']['source']['verticalScale']) is int and patch['nativeMesh']['source']['verticalScale']==1
    assert len(patch['nativeMesh']['index'])//3==candidate['triangles'] and patch['meta']['georef']['W']==patch['w'] and patch['meta']['georef']['H']==patch['h']
    return candidate

def pending_scope_record(scope,candidate):
    assert scope['physicalAccepted'] is False and scope['installationApproved'] is False
    return {**scope,'privateCandidate':candidate,'wholeNativeBASICBeforeAfterQualificationNotExecuted':True,'oldUnchangedTerrainResultsHistoricalOnly':ref(old.DOC/'diagnostic.json.gz')}

def qualification_resources(actors):
    from run import reservations
    return reservations.normalise([('building:' if u.startswith('landsd/') else 'foreign-form:')+u for u in actors]+['terrain-patch:'+u for u in actors]+['immutable-source-proof:'+BATCH])


V2_PROPOSAL=BASE/'government-xl-heritage165054-authentic-tin-owned-ordinary-v2-20261014-proposal'

def resources(actors):
    from run import reservations
    assert actors==sorted(set(actors)) and len(actors)==45 and UID in actors and 'landsd/57455:0' in actors
    return reservations.normalise(['building:'+UID,'terrain-patch:'+UID,'immutable-source-proof:'+BATCH])

def claim_failure_record(claim):
    assert claim['ok'] is False
    return dict(claimDenied=True,error=claim.get('error'),conflicts=[dict(resource=q['resource'],batch=q.get('batch')) for q in claim.get('conflicts',[])],workerOwnedPhaseStarted=False,modelFailure=False,candidateRejected=False,takeover=False)

def inputs():
    data=old.inputs(); receipt=read(NOMINATION/'result.json'); verified=read(NOMINATION/'ROOT-VERIFIED.json'); assert receipt['jobId']==verified['jobId']==NOMINATION_JOB and receipt['stage']=='two-original-TIN-existing-nearwater-constructor-bare-validator-and18-source-context-no-warning-resolution'
    assert verified['exactNeonReadback'] and verified['allEvidenceHashesVerified'] and verified['leaseReleased'] and receipt['terrainCandidateCreated'] is True
    packet=read(NOMINATION/'diagnostic.json'); candidates=read(NOMINATION/'terrain-candidates.json'); assert len(candidates)==1 and candidates[0]['triangles']==8341 and candidates[0]['sha256']=='21216b7acafb198484957ce604fa89555df57d7f574930f7a9a28b3b7a508fc1'; patch=read(check(dict(path=candidates[0]['path'],sha256=candidates[0]['sha256']))); bind_candidate(packet,candidates,patch); assert packet['all22SourceBelowMinus05WarningsUnresolved'] is True and packet['rawStrictFoundationRemainsFalse'] is True
    scope=read(nomination.prior.north.DOC/'proposal-input.json'); assert scope['currentManifestSHA256']==CURRENT and scope['currentSnapshot']==SNAPSHOT and scope['region']==candidates[0]['bounds']
    actors=scope['scope']['allActorsForNominationLease']; assert actors==sorted(set(actors)) and UID in actors and 'landsd/57455:0' in actors and len(actors)==45
    v2pins=read(V2_PROPOSAL/'draft-pins.json'); assert v2pins['inputRefs']==distinct_refs(data[-1]+receipt['evidenceRefs']+[ref(NOMINATION/'result.json'),ref(NOMINATION/'ROOT-VERIFIED.json')]); assert read(V2_PROPOSAL/'ROOT-claim-attempt.json')['workerOwnedPhaseStarted'] is False
    refs=distinct_refs(v2pins['inputRefs']+[ref(V2_PROPOSAL/p) for p in ['draft-pins.json','actual-readonly-preparation.json','ROOT-claim-attempt.json','ROOT-reservation-overlap.json']]+[ref(HERE/'heritage165054_authentic_tin_owned_ordinary_v2_20261014.py')])
    for q in refs: check(q)
    return data,candidates,scope,receipt['jobId'],refs

def load():
    pins=read(PROPOSAL/'draft-pins.json'); assert pins['caller']==ref(Path(__file__))
    for q in pins['codeRefs']+pins['inputRefs']: check(q)
    data=inputs(); assert data[-1]==pins['inputRefs'] and data[3]==pins['nominationJob']; assert pins['canonicalResources']==resources(data[2]['scope']['allActorsForNominationLease']) and pins['futurePhysicalQualificationResources']==qualification_resources(data[2]['scope']['allActorsForNominationLease']) and len(pins['futurePhysicalQualificationResources'])==91; return pins,data

def owned():
    from run import reservations,connect,NATIVE_RUN
    import numpy as np
    from shapely.geometry import Polygon
    pins,data=load(); saved,candidates,scope,job,refs=data; row,identity,context,forms,tiles,native,_=saved
    prep=read(PROPOSAL/'actual-readonly-preparation.json'); assert prep['passed'] and prep['caller']==ref(Path(__file__))
    lease=read(LEASE); assert reservations.owns(lease) and lease['resources']==pins['canonicalResources'] and not DOC.exists()
    refs=distinct_refs(refs+pins['codeRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')]); pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def fence():
        pulse(force=True)
        for q in refs: check(q); pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT; pulse(force=True)
    fence()
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder,j in [(NOMINATION,job),(old.DOC,'09423e020fcce2205b300ecf4ecc60ca69f5ca23274bad3957490738d4d7cd1f')]: assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(j,)).fetchone()==('complete',read(folder/'result.json'))
    DOC.mkdir(); old.bind_saved_identity(row,identity,context,forms,tiles)
    original=(ROOT/row['candidate']['path']).read_bytes(); asset=LOCAL/row['candidate']['entry']['asset']; asset.parent.mkdir(parents=True,exist_ok=True)
    with asset.open('xb') as f: f.write(original)
    assert ref(asset)['sha256']==SOURCE
    current_row=copy.deepcopy(row); current_row['candidate']['path']=str(asset.relative_to(ROOT)); cat=read(HERE/'accepted/government-xxl-20260911/catalogue.json'); cat.update(area=BATCH,models=[row['candidate']['entry']],counts=dict(packedModels=1))
    save(LOCAL/'catalogue.json',cat); save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json'])); save(LOCAL/'source-forms.json',{UID:row['source']}); save(DOC/'identity.json',identity)
    save(DOC/'selection.json.gz',dict(rows=[current_row],batch=BATCH,manifestSHA256=CURRENT,nativeRun=NATIVE_RUN)); save(DOC/'terrain-candidates.json',candidates)
    save(DOC/'whole-parent-domain-pending-current-qualification.json',{**pending_scope_record(scope,candidates[0]),'ownedOnlyReplayResources':pins['canonicalResources'],'futurePhysicalQualificationResources':pins['futurePhysicalQualificationResources'],'historicalV2QualificationResources':read(V2_PROPOSAL/'draft-pins.json')['canonicalResources'],'all45ActorsRetainedForFutureQualification':True})
    def call(command,allowed=(0,)):
        fence(); p=DOC/('command-'+str(len(list(DOC.glob('command-*.json')))).zfill(3)+'.json'); r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True); save(p,dict(command=command,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr)); fence(); assert r.returncode in allowed,p
    rel=lambda p:str(p.relative_to(ROOT))
    call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
    call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],(0,1))
    rows=read(LOCAL/'runtime-geometry.json.gz')['rows']; assert len(rows)==1 and rows[0]['uid']==UID and rows[0]['sourceSHA256']==SOURCE; a=rows[0]
    tri=np.asarray(a['position'],dtype='<f8').reshape(-1,3)[np.asarray(a['index'],dtype=np.int64).reshape(-1,3)]; ground=np.asarray(a['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
    assert tri.shape==(15140,3,3) and np.isfinite(tri).all() and np.isfinite(ground).all() and old.hashlib.sha256(tri.tobytes()).hexdigest()=='0f1f5703f6fbd6c200a5f11ea5b2b617e7018dcfdd99436f9e0340c22633684f'
    final=module(HERE/'xl-final-script-pass.py','heritage_candidate_owned_foundation'); b=row['source']['building']; foundation=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:])); strict=foundation['completeTerrainTriangles']==foundation['triangles'] and not foundation['fullyBuriedUpwardTriangles'] and foundation['fullyBuriedAreaFraction']==0
    save(DOC/'foundation.json',dict(rows=[dict(uid=UID,sourceSHA256=SOURCE,foundation=foundation,strictFoundationAccepted=strict)],sourceGeometryChanges=0))
    metrics=read(DOC/'metrics.json'); validation=read(DOC/'validation.json'); assert len(metrics['rows'])==1 and metrics['rows'][0]['uid']==UID
    policy=module(HERE/'acceptance-policy.py','heritage_candidate_owned_policy'); reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCE,identityProof=identity['proof']),metrics['rows'][0],metrics['profiles']['mobile'])
    runtime=validation['results']; runtime_clear=len(runtime)==1 and runtime[0]['uid']==UID and not runtime[0]['concerns'] and validation['loaderAccepted']==validation['checksPassed']==1 and validation['exceptions']==0
    save(DOC/'diagnostic.json.gz',dict(uid=UID,candidate=candidates[0],currentManifestSHA256=CURRENT,currentSnapshot=SNAPSHOT,nominationJob=job,ordinaryNumericReasons=reasons,rawRuntimeRows=runtime,loaderAccepted=validation['loaderAccepted'],runtimeChecksPassed=validation['checksPassed'],runtimeExceptions=validation['exceptions'],strictFoundationAccepted=strict,ownCheapOrdinaryTerrainGatePassed=not reasons and strict and runtime_clear,completeOriginalFaces=15140,completeActualDrawnGroundFaces=len(ground),actualLiteralWorldSHA256=old.hashlib.sha256(tri.tobytes()).hexdigest(),rawHistoricalCurrentTerrainIntersectionAndStrictFalseRetained=ref(old.DOC/'diagnostic.json.gz'),wholeCurrentParentDomainBeforeAfterNativeBASICDeltaStillRequired=True,all22PriorSourceBelowMinus05WarningsRetained=ref(nomination.prior.CONTEXT),exact18FourWorldDescriptorsRetained=ref(NOMINATION/'exact18-four-world-source-context.json.gz'),noFunctionalApplicabilityApprovalTransferred=True,originalStarFootprintRejectionAndRawJunctionCrossingsRetained=True,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
    for out in [metrics,validation]: refs=distinct_refs(refs+[dict(path=p,sha256=h) for p,h in (out.get('inputHashes') or out.get('hashes') or {}).items()])
    refs=distinct_refs(refs+[ref(p) for folder in [DOC,LOCAL] for p in folder.rglob('*') if p.is_file() and p.name!='reservation.json']); fence()
    module(old.FREEZER,'heritage_candidate_owned_freezer').freeze(BATCH,'cheap-owned-actual-original-candidate-terrain-ordinary-foundation-no-neighbour-or-install-credit',[check(q) for q in refs],dict(uids=[UID],sourceOnly=True,ownCheapOrdinaryTerrainGatePassed=not reasons and strict and runtime_clear,wholeCurrentDeltaStillRequired=True,physicalAccepted=False,newlyInstalled=0))

def main():
    if '--schema-only' in sys.argv:
        p,d=load(); print(json.dumps(dict(passed=True,caller=ref(Path(__file__)),nominationJob=d[3],candidate=d[1][0],canonicalContextActors=45,ownedLeaseActors=1,futurePhysicalQualificationResources=len(p['futurePhysicalQualificationResources']),canonicalResources=len(p['canonicalResources']),noSourceDecodeGeometryRendererDBLeaseWorker=True))); return
    if '--owned' in sys.argv: return owned()
    assert sys.argv[1:]==['--check-owned-on-private-authentic-tin-only'] and not DOC.exists() and not LOCAL.exists(); p,d=load(); assert read(PROPOSAL/'actual-readonly-preparation.json')['passed']
    from run import reservations
    claim=reservations.claim('heritage-owned-candidate-'+str(uuid.uuid4()),p['canonicalResources'],batch=BATCH,ttl=3600)
    if not claim['ok']:
        failure=claim_failure_record(claim)
        with (PROPOSAL/'claim-denied-attempt.json').open('x') as f: json.dump(failure,f,sort_keys=True,indent=2); f.write('\n')
        print(json.dumps(failure,sort_keys=True)); raise RuntimeError('Owned-only reservation denied; exact resource/batch diagnostics preserved')
    lease=claim['reservation']
    try:
        save(LEASE,json.loads(json.dumps(lease,default=str))); subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease): assert reservations.release(lease)['ok']
if __name__=='__main__': main()
