"""ROOT-only ordinary staged/live acceptance and atomic two-original installation.
No geometry calculation; raw strict failures/source applicability remain exact.
"""
from pathlib import Path
import argparse,json,os,subprocess,sys,time,uuid
from urllib.request import urlopen
from run import ROOT,HERE,read,save,connect,reservations,jobs,Jsonb,dict_row,digest
import upton_joint_original_dimension_private_stage_v2_20261014 as stage
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from upton_preserve_replacement_slot_v1_20261014 import preserve_slot
physical=stage.physical;ref,check=stage.ref,stage.check
BASE=ROOT/'docs/astra-city/government-import';STAGED_BATCH='government-xl-upton-joint-original-dimension-staged-browser-v2-20261014';INSTALL_BATCH='government-xl-upton-joint-original-functional-installed-v1-20261014';STAGED=BASE/STAGED_BATCH;INSTALLED=BASE/INSTALL_BATCH;PUB=HERE/'upton_slot_preserving_guarded_publish_v2_20261014.py'

def verified(folder,job):
    r=read(folder/'result.json');v=read(folder/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==job and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased']
    for q in distinct_refs(r['evidenceRefs']):check(q)
    return r

def browser_report(doc,name):
    report=physical.module(HERE/'integrate.py','upton_unchanged_browser_verifier').browser_verified(doc/name,set(stage.OWNED));views=[v for v in report['views']if 'time'in v]
    assert len(views)==8 and all(v['fullyFramed']and v['selectionClosed']and v['fallbackFaces']==0 and v['solidAppearance']and all(o==1 for o in v['materialOpacities'])for v in views)
    own=report['retainedNativeOwnViews'];assert len(own)==4 and {(v['uid'],v['width'],v['time'])for v in own}=={(physical.RETAINED,w,t)for w in [1280,390]for t in ['15:00','22:00']}
    assert all(v['active']and v['visible']and v['fullyFramed']and v['fallbackFaces']==0 for v in own)
    for v in views:
        if v['uid']==stage.OWNED[1]:assert v['nativeSupports'][stage.OWNED[0]]['active']and v['nativeSupports'][stage.OWNED[0]]['visible']and v['nativeSupports'][stage.OWNED[0]]['declaredCandidateSupport']
    return report

def owned(args):
    batch=STAGED_BATCH if args.staged_browser_only else INSTALL_BATCH;doc=BASE/batch;local=HERE/'local'/batch;lease=local/'reservation.json';last=time.monotonic()
    def owns():assert reservations.owns(read(lease))
    def call(cmd):
        log=doc/('command-'+str(len(list(doc.glob('command-*.json')))).zfill(3)+'.json');p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,env={**os.environ,'CHROME_PATH':os.environ.get('CHROME_PATH','/opt/google/chrome/chrome')});save(log,dict(command=cmd,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));owns();assert p.returncode==0,log
    owns();assert not doc.exists();
    with urlopen('http://127.0.0.1:4176/city.html',timeout=10)as r:assert r.status==200
    source=verified(stage.DOC,args.stage_job);p,adapted,rows,c,patch=stage.load_completed();assert adapted['scriptChecksPassed']and not adapted['remainingActualPhysicalReasons']and not adapted['strictInterfacePassed']
    with connect()as con:con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(args.stage_job,)).fetchone()==('complete',source)
    source_refs=distinct_refs(source['evidenceRefs']+[ref(stage.DOC/'result.json'),ref(stage.DOC/'ROOT-VERIFIED.json'),ref(Path(__file__)),ref(PUB),ref(HERE/'upton_preserve_replacement_slot_v1_20261014.py')]);manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==physical.CURRENT
    for q in source_refs:check(q)
    doc.mkdir(parents=True);plan=read(stage.STAGE/'plan.json');models=read(stage.STAGE/'catalogue.json')['models'];assert [m['uid']for m in models]==stage.OWNED
    if args.staged_browser_only:
        config={**read(stage.STAGE/'browser-config.json'),'doc':str(doc.relative_to(ROOT))+'/'};save(local/'browser-config.json',config)
        publication=[sys.executable,str(PUB),str((stage.STAGE/'plan.json').relative_to(ROOT)),'--receipt',str(lease),'--phase',batch];call(publication)
        call(['node',str(stage.BROWSER),'staged',str((local/'browser-config.json').relative_to(ROOT))]);report=browser_report(doc,'staged-browser.json')
        save(doc/'acceptance.json',dict(batch=batch,uids=stage.OWNED,sourceSHA256s={m['uid']:m['sha256']for m in models},passed=True,checksPassed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,strictInterfacePassed=False,sourceApplicabilityVerbatim=adapted,sourceStage=ref(stage.DOC/'result.json'),stagedBrowser=ref(doc/'staged-browser.json'),browserConfig=ref(local/'browser-config.json'),plan=ref(stage.STAGE/'plan.json'),livePublicationRequired=True))
        assert manifest.read_bytes()==before
        refs=distinct_refs(source_refs+[ref(f)for f in doc.rglob('*')if f.is_file()]+[ref(local/'browser-config.json')])
        for q in refs:check(q)
        physical.module(physical.FREEZER,'upton_joint_staged_freezer').freeze(batch,'original-functional-assembly-ordinary-solid-staged-browser-no-install',[check(q)for q in refs],dict(uids=stage.OWNED,currentManifestSHA256=physical.CURRENT,sourceOnly=True,sourceGeometryChanges=0,publication=False,newlyInstalled=0));return
    raise AssertionError('This isolated caller is staged browser only; live publication is separate')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--staged-browser-only',action='store_true',required=True);parser.add_argument('--stage-job',required=True);parser.add_argument('--owned',action='store_true');args=parser.parse_args();batch=STAGED_BATCH;doc=BASE/batch;local=HERE/'local'/batch;lease=local/'reservation.json'
    if args.owned:
        from publication_lock import locked_publication
        with locked_publication(ROOT):return owned(args)
    assert not doc.exists()and not local.exists();verified(stage.DOC,args.stage_job);stage.load_completed();uids=stage.old.functional.review.scope_uids();resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+batch];claim=reservations.claim('upton-publication-'+str(uuid.uuid4()),resources,batch=batch,ttl=3600);assert claim['ok'];reservation=claim['reservation']
    try:save(lease,json.loads(json.dumps(reservation,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(lease),'--ttl','3600','--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(reservation):assert reservations.release(reservation)['ok']
if __name__=='__main__':main()
