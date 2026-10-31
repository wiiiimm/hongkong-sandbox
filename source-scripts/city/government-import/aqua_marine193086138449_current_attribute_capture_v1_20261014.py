"""ROOT-only missing two-actor arithmetic arrays; no terrain/identity replay."""
from pathlib import Path
import sys,json,subprocess,uuid,numpy as np
import aqua_marine193086_saved_source_context_diagrams_v2_20261014 as prior
from run import ROOT,HERE,read,save,connect,reservations
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
A=prior.attribution;ref,check,module=prior.ref,prior.check,prior.module
BATCH='government-xl-aqua-marine193086138449-current-attribute-capture-v1-20261014';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';RUNTIME=HERE/'aqua_marine193086138449_current_actual_attributes_v1_20261014.mjs';RECOVERY=BASE/'government-xl-aqua-marine-original-recovery-20261010/selection.json.gz'
def load():
    data,result,p,refs=prior.load();row,context,capture,saved,source,pins,*_=data;recovery=read(RECOVERY);foreign=next(r for r in recovery['rows']if r['uid']==A.prior.FOREIGN);form=next(f for f in capture['forms']if f['uid']==A.prior.FOREIGN);assert foreign['sourceSHA256']==A.prior.FOREIGN_SHA and foreign['candidate']['entry']['triangles']==116 and foreign['candidate']['entry']['buildingCSUID']==form['buildingCSUID']
    assert saved['passed']and saved['foreignCollisionExemption']is False and saved['noCommonOwnershipOrSupportClaim'];native=data[9];assert len(native)==6652 and A.prior.UID not in native
    refs=distinct_refs(refs+data[7]+[ref(RECOVERY),ref(RUNTIME),ref(Path(__file__)),p['actualRuntimeArrays']]+p['allCurrentGroundSourceInputRefs'])
    for q in refs:check(q)
    return data,result,p,foreign,form,refs

def schema_only():
    data,r,p,f,form,refs=load();return dict(passed=True,caller=ref(Path(__file__)),runtime=ref(RUNTIME),uids=[A.prior.UID,A.prior.FOREIGN],sourceFaces=[22735,116],currentCatalogue6652=True,scope=data[-1],savedGroundFaces=584,identityPassedVerbatimReused=True,missingActualArithmeticArraysOnly=True,noSourceDecodeIdentityNumericalRendererDBLeaseWorker=True)

def owned():
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__));data,result,p,foreign,form,refs=load();refs=distinct_refs(refs+prep['codeRefs']+prep['inputRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'actual-readonly-preparation.json')]);pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def fence():
        pulse(force=True)
        for q in refs:check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==A.prior.CURRENT;pulse(force=True)
    fence()
    with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior.JOB,)).fetchone()==('complete',result)
    row=data[0];manifest=read(ROOT/'3d-viewer/city/data/manifest.json');actors=[dict(uid=A.prior.UID,path=row['candidate']['path'],entry=row['candidate']['entry'],building=row['source']['building']),dict(uid=A.prior.FOREIGN,path=data[4]['originalPaths'][A.prior.FOREIGN],entry=foreign['candidate']['entry'],building=form)]
    DOC.mkdir();save(DOC/'capture-inputs.json.gz',dict(rows=actors,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/url)for url in manifest['officialModelCatalogues']],evidenceRefs=refs,sourceGeometryChanges=0,terrainGeometryChanges=0,foreignIndependent=True,identityProofVerbatim=data[3],savedCurrentGroundBinding=dict(runtime=p['actualRuntimeArrays'],completeGroundSHA256=p['completeActualGroundSHA256'],completeGroundFaces=584,inputRefs=p['allCurrentGroundSourceInputRefs']),rawStrictFoundationVerbatim=p['rawFoundationVerbatim'],all278PartialBelowFaceIDs=p['allOtherPartialBelowMinusHalfSourceFaceIDs'],minimumWholeSurfaceGapVerbatim=p['minimumWholeSurfaceGapVerbatim'],functionalApprovalClaimed=False))
    command=['node',str(RUNTIME),str((DOC/'capture-inputs.json.gz').relative_to(ROOT)),str((DOC/'complete-two-actor-actual-attributes.json.gz').relative_to(ROOT))];process=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);save(DOC/'command000.json',dict(command=command,exitCode=process.returncode,stdout=process.stdout,stderr=process.stderr));assert process.returncode==0
    captured=read(DOC/'complete-two-actor-actual-attributes.json.gz');assert captured['startEndAllInputsVerified']and captured['sourceGeometryChanges']==0 and len(captured['rows'])==2
    own,foreign=captured['rows'];assert [r['uid']for r in captured['rows']]==[A.prior.UID,A.prior.FOREIGN]and [r['sourceSHA256']for r in captured['rows']]==[A.prior.SOURCE_SHA,A.prior.FOREIGN_SHA]
    old=read(A.prior.LOCAL/'runtime-geometry.json.gz')['rows'][0];assert A.prior.encoded(own['completeLiteralWorldPosition'])==A.prior.encoded(old['position'])and own['completeOriginalIndex']==old['index']
    world=np.asarray(own['completeLiteralWorldPosition'],dtype='<f8').reshape(-1,3)[np.asarray(own['completeOriginalIndex'],dtype=np.int64).reshape(-1,3)];assert A.prior.digest(world.tobytes())==p['completeLiteralWorldSHA256']
    save(DOC/'capture-binding.json',dict(actualActorFaces=[22735,116],oldLiteralPositionAndIndexExactBytesPreserved=True,wholeUnusedVerticesCaptured=True,identityVerbatim=data[3],sourceGeometryChanges=0,terrainGeometryChanges=0,currentManifestSHA256=A.prior.CURRENT,currentSnapshot=A.prior.SNAPSHOT,completeCurrentGroundSHA256=p['completeActualGroundSHA256'],completeCurrentGroundFaces=584,rawStrictFoundationAccepted=False,all278PartialBelowRetained=True,functionalApprovalClaimed=False,ordinaryFourWorldFiniteForeignCollisionViewerAndPublicationPending=True,physicalAccepted=False,newlyInstalled=0))
    refs=distinct_refs(refs+[ref(q)for q in DOC.rglob('*')if q.is_file()]);fence();module(A.prior.FREEZER,'aqua_two_arithmetic_capture_freezer').freeze(BATCH,'two-source-actual-arithmetic-attributes-saved-current-ground-no-identity-replay',[check(q)for q in refs],dict(uids=[A.prior.UID,A.prior.FOREIGN],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))
def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only()));return
    if '--owned'in sys.argv:return owned()
    assert '--capture-two-original-arithmetic-only'in sys.argv and not DOC.exists()and not LOCAL.exists();data,*_=load();scope=data[-1];prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__));resources=['building:'+u for u in scope]+['terrain-patch:'+u for u in scope]+['immutable-source-proof:'+BATCH];claim=reservations.claim('aqua-two-source-capture-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
