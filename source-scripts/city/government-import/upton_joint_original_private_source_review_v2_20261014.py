"""ROOT-only V2 display: close selected outline and frame entire indexed sources.
V1 completed arrays/interpretation proofs reused under exact bindings; no kernels.
"""
from pathlib import Path
import sys,json,time,uuid,subprocess
from run import ROOT,HERE,read,save,connect,reservations
import upton_joint_original_private_source_review_v1_20261014 as previous
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
physical=previous.physical;ref,check=physical.ref,physical.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-joint-original-private-source-review-v2-20261014';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';RUNTIME=HERE/'upton_joint_original_private_source_preview_v2_20261014.mjs';JOB='b3694f4081686c35bcb8716282d699890a5fac25af20f4e5891df02cbea66611'
def load():
    p=read(PROPOSAL/'draft-pins.json');assert p['caller']==ref(Path(__file__))
    for q in p['codeRefs']+p['inputRefs']:check(q)
    r=read(previous.DOC/'result.json');v=read(previous.DOC/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==JOB and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased']
    old=read(previous.DOC/'preview-input.json');proof=read(previous.DOC/'actual-private-source-preview.json');assert proof['actualGround']['faces']==11645 and proof['actualGround']['sha256']==previous.GROUND and not proof['errors']
    assert len(old['points'])==41 and len(old['incidentSourceFaces'])==36 and len(old['mainContactPrimitives'])==197
    assert old['currentManifest']['sha256']==physical.CURRENT and ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==physical.CURRENT
    return p,old,proof
def schema_only():
    p,i,r=load();return dict(passed=True,caller=ref(Path(__file__)),sourcePreviewOnly=True,completeSourceLiteralBindingsVerbatim=r['actualSourceBindings'],groundVerbatim=r['actualGround'],noSourceArraysArithmeticRendererDBLeaseWorker=True)
def owned():
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
    def pulse(force=False):
        nonlocal last
        if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
    p,old,proof=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
    refs=distinct_refs(p['codeRefs']+p['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs'])
    def fence():
        for q in distinct_refs(refs):check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==physical.CURRENT;pulse(True)
    result=read(previous.DOC/'result.json')
    with connect()as con:con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',result)
    fence();DOC.mkdir(parents=True);views=[]
    for v in old['views']:
        if v['id']in ['assembly','foot-plan']:views.append(dict(id=v['id'],title=v['title']+' — complete indexed source box',fitIndexedSource=True,direction=[-1,.6,1]if v['id']=='assembly'else[0,1,.08]))
        else:views.append(v)
    data={**old,'batch':BATCH,'views':views,'executionRefs':refs};save(DOC/'preview-input.json',data)
    save(DOC/'exact-V1-source-ground-proof-reuse.json',dict(completedV1=ref(previous.DOC/'result.json'),actualFullSourceAndGroundBindingsVerbatim=proof,numbered41And36And197Verbatim=ref(previous.DOC/'numbered41-faces-source-contact-key.json.gz'),savedArrayDiagramVerbatim=ref(previous.DOC/'saved-array-diagram.json'),mainExposureVerbatim=ref(previous.DOC/'main-contact-ground-exposure-summary.json'),noFiniteContactOrGroundProofRelabelling=True,strictInterfacePassed=False,physicalAccepted=False))
    command=['node',str(RUNTIME),str(DOC.relative_to(ROOT))+'/'];r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);save(DOC/'actual-private-preview-log.json',dict(command=command,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0;pulse(True)
    out=read(DOC/'actual-private-source-preview.json');assert out['actualGround']==proof['actualGround']and not out['errors']and len(out['views'])==6
    assert out['actualSourceBindings']==proof['actualSourceBindings']
    for v in out['views']:assert v['selectionClosed'];assert v['id']not in ['assembly','foot-plan']or v['indexedSourceFraming']
    refs +=[ref(p)for p in DOC.rglob('*')if p.is_file()];fence();physical.module(physical.FREEZER,'upton_fullframe_display_freezer').freeze(BATCH,'private-display-only-selection-closed-full-indexed-source-framing',[check(q)for q in distinct_refs(refs)],dict(uids=physical.OWNED,currentManifestSHA256=physical.CURRENT,sourceOnly=True,sourceGeometryChanges=0,physicalAccepted=False,newlyInstalled=0))
def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
    if '--owned'in sys.argv:return owned()
    assert '--capture-private-source-review-only'in sys.argv and not DOC.exists()and not LOCAL.exists();load();uids=previous.scope_uids();resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-fullframe-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
