"""Root-only publication of the two unchanged Cullinan West tower sources.

The complete current role and staged browser must already have independently
closed certificates. Retained V Walk is unchanged and receives no review credit.
No terrain, model geometry, source pose or legacy acceptance flag changes.
"""
import argparse, importlib.util, json, os, subprocess, sys, uuid
from pathlib import Path
from urllib.request import urlopen
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row

BATCH='government-xl-cullinan-west-two-unchanged-installed-v1-20261011'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH; LEASE=LOCAL/'install-reservation.json'
UIDS={'landsd/161931:0','landsd/120158:0'};NATIVE='landsd/262871:0'
MANIFEST_SHA='3a2f56f7980954ff3493aba5e8a015ca79153f81da55bb580e26bf5b2cdb2ee8'
PREVIOUS_SNAPSHOT='ee1a41d61d2de0fe'
BROWSER=HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def current_native(manifest):
    found=[m for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models'] if m['uid']==NATIVE]
    assert len(found)==1
    return found[0]
def server_ready():
    with urlopen('http://127.0.0.1:4176/city.html',timeout=10)as r:assert r.status==200 and len(r.read())>100
def browser_verify(stage,name):
    report=module('cullinan_live_browser_validation',HERE/'integrate.py').browser_verified(stage.DOC/name,UIDS)
    views=[v for v in report['views']if 'time'in v]
    assert len(views)==8 and {(v['uid'],v['width'],v['time'])for v in views}=={(u,w,t)for u in UIDS for w in [1280,390]for t in ['15:00','22:00']}
    own=report['retainedNativeOwnViews']
    assert len(own)==4 and {(v['uid'],v['width'],v['time'])for v in own}=={(NATIVE,w,t)for w in [1280,390]for t in ['15:00','22:00']}
    assert all(v['active']and v['visible']and v['fullyFramed']for v in own)
    for view in views:
        assert set(view['nativeSupports'])=={NATIVE}
        support=view['nativeSupports'][NATIVE]
        assert support['active']and support['visible']
    assert {v['uid']for v in report['views']if v.get('fallbackRetained')}==UIDS
    return report

def owned(args,stage):
    def owns():assert reservations.owns(read(LEASE))
    def call(cmd):
        subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
    owns();server_ready();manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes()
    assert digest(before)==MANIFEST_SHA
    native=current_native(read(manifest));assert native['publicationApproved']is False
    assert native['sha256']=='e98936729981df7e618478258f486ff5faaa98fcfa57937b2d3f5a11dc2277f8'
    assert native['buildingCSUID']=='3389220874P20180705'
    rows,identities,role=stage.recheck(LOCAL/'before-publication')
    assert {r['uid']for r in rows}==UIDS and role['currentManifest']['sha256']==MANIFEST_SHA
    assert role['scriptChecksPassed']and role['readyForStagedBrowser']and not role['installationApproved']
    assert role['wholeOwnedOriginalFaces']==22312 and role['nativeReacceptance']is False
    assert role['sourceGeometryChanges']==role['terrainProposalChanges']==0
    acceptance=read(stage.DOC/'acceptance.json')
    assert acceptance['passed']and acceptance['checksPassed']and acceptance['livePublicationRequired']and not acceptance['publication']
    assert set(acceptance['uids'])==UIDS and acceptance['newlyInstalled']==acceptance['modelGeometryChanges']==acceptance['scriptExternalAICalls']==0
    assert ref(stage.DOC/'staged-browser.json')==acceptance['stagedBrowser']
    for item in acceptance['evidenceRefs']:assert ref(ROOT/item['path'])==item
    browser_verify(stage,'staged-browser.json')
    models=read(stage.STAGE/'catalogue.json')['models'];assert {m['uid']for m in models}==UIDS
    dependency=dict(uid=NATIVE,csuid=native['buildingCSUID'],sha256=native['sha256'],state='installed')
    for m in models:
        assert m['sha256']==next(r['sourceSHA256']for r in rows if r['uid']==m['uid'])
        assert m['supportDependencies']==[dependency]and not m.get('suppressesBuildingUids')and m['proceduralWindows']is False
        assert ref(stage.STAGE/m['asset'])['sha256']==m['sha256']
    assert native==read(stage.DOC/'retained-native-exact-entry-before-stage.json')
    plan=read(stage.STAGE/'plan.json');assert len(plan['areas'])==1 and plan['topLevelTerrainPatches']==[]
    assert all(not(ROOT/'3d-viewer'/a['destination']).exists()for a in plan['areas'])
    current={m['uid']for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']}
    assert not(UIDS&current)
    closures=[];refs=[ref(Path(__file__)),ref(Path(stage.__file__)),ref(BROWSER)]
    for path in args.closure:
        p=ROOT/path;c=read(p);assert c['independentlyVerified']and c['verifiedReferenceVersions']>0
        closures.append(set(c['paths']));refs.append(ref(p))
    assert any({ref(stage.ROLE/p)['path']for p in ['typed-role.json.gz','result.json']}<=c for c in closures)
    required={ref(stage.DOC/p)['path']for p in ['acceptance.json','staged-browser.json']}|{ref(stage.STAGE/p)['path']for p in ['plan.json','catalogue.json','browser-config.json']}
    assert any(required<=c for c in closures)
    previous=ROOT/args.previous_count;assert read(previous)['counts']==dict(total=521,installedVerified=221,remaining=300)
    refs.extend([ref(previous),ref(stage.DOC/'acceptance.json'),ref(stage.DOC/'staged-browser.json'),ref(stage.STAGE/'browser-config.json'),ref(stage.STAGE/'catalogue.json')])
    save(DOC/'current-identities.json',identities);save(DOC/'complete-current-role.json.gz',role);save(DOC/'retained-native-before.json',native)
    plan_path=DOC/'atomic-plan.json';save(plan_path,plan)
    refs.extend(ref(DOC/p)for p in ['current-identities.json','complete-current-role.json.gz','retained-native-before.json','atomic-plan.json'])
    decision=dict(batch=BATCH,uids=sorted(UIDS),sourceSHA256s={r['uid']:r['sourceSHA256']for r in rows},checksPassed=True,passed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,terrainProposalGeometryChanged=False,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,manifestBeforeSHA256=MANIFEST_SHA,nativeReacceptance=False,legacyNativeDiagnosticsPreserved=True,legacyDependencyStateMeansCurrentNativeAvailabilityOnly=True,evidenceRefs=refs,livePublicationRequired=True)
    save(DOC/'acceptance.json',decision)
    sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
    pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);assert pointer['snapshotId']==PREVIOUS_SNAPSHOT
    inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']}
    for m in models:
        prior=parts.get(m['uid'],{})
        parts[m['uid']]=dict(uid=m['uid'],name=m['label'],landmarkIds=prior.get('landmarkIds',[]),objectId=m['objectId'],csuid=m['buildingCSUID'],candidate={'sha256':m['sha256']},sourceProgress='prepared-for-review',classification='verified-unchanged-original-complete-source-and-current-terrain-roles',knownHold=False)
    ordered=sorted(parts.values(),key=lambda p:p['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16]
    inventory_path=pointer_path.parent/('source-review-inventory-'+snapshot+'.json')
    save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Two complete unchanged Cullinan West towers; qualified exposed existing native support path only. All legacy native diagnostics and acceptance flags unchanged. No source geometry, pose or terrain edits; zero AI modelling.'})
    ledger.seed(inventory_path,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=ref(DOC/'acceptance.json')['path'])
    ledger.record_many(snapshot,LEASE,[(u,'approved-for-integration',DOC/'acceptance.json','Complete current proofs and staged browser pass; live checks pending.',commit)for u in sorted(UIDS)],effort=effort,request_id=BATCH+'-approved-'+snapshot)
    publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(plan_path)['path'],'--receipt',str(LEASE),'--phase',BATCH]
    call(publication);_,_,replayed=stage.recheck(LOCAL/'before-apply');assert replayed==role and manifest.read_bytes()==before
    for item in refs:assert ref(ROOT/item['path'])==item
    server_ready();LOCAL.mkdir(parents=True,exist_ok=True)
    (LOCAL/'manifest-before-installation.json').write_bytes(before)
    try:
        call(publication+['--apply']);call(['node',str(BROWSER),'live',ref(stage.STAGE/'browser-config.json')['path']]);browser_verify(stage,'live-browser.json')
        assert current_native(read(manifest))==native
    except BaseException:
        manifest.write_bytes(before);save(DOC/'live-failure-rollback.json',dict(manifestRestoredSHA256=digest(manifest.read_bytes()),installedCreditGranted=False));raise
    installed={**decision,'snapshotId':snapshot,'publication':True,'newlyInstalled':2,'manifest':ref(manifest),'liveBrowser':ref(stage.DOC/'live-browser.json')}
    save(DOC/'installed-acceptance.json',installed)
    ledger.record_many(snapshot,LEASE,[(u,'installed-verified',DOC/'installed-acceptance.json','Unchanged original passes complete current source/physical gates, staged/live desktop/mobile day/night, framing, picking/collision, retained-source views and failed-load retry. Zero AI modelling.',commit)for u in sorted(UIDS)],effort=effort,request_id=BATCH+'-installed-'+snapshot)
    assert read(pointer_path)==pointer
    save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inventory_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
    call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
    call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',args.previous_count,'--batch',BATCH])
    kind='two-unchanged-cullinan-originals-current-source-installed-v1';jid=jobs.enqueue(BATCH,kind,dict(acceptance=ref(DOC/'acceptance.json'),snapshot=snapshot))
    receipt=read(LEASE);job=jobs.claim(BATCH,receipt['owner'],[kind],lease_seconds=1800);assert job and job['id']==jid
    final={**installed,'installedUids':sorted(UIDS),'evidenceRefs':[ref(DOC/p)for p in ['acceptance.json','installed-acceptance.json','atomic-plan.json']]+[ref(stage.DOC/p)for p in ['staged-browser.json','live-browser.json']],'jobId':jid,'activeWorkers':0,'queuedFollowups':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json'),'fullXLCurrentCounts':read(DOC/'full-xl-current-count.json')['counts']}
    with connect()as c:
        c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,receipt)
        assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(final),jid,job['owner'],job['token'])).rowcount==1
    with connect()as c:
        c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',final)
        for r in rows:assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,r['uid'])).fetchone()==('installed-verified',r['sourceSHA256'])
    save(DOC/'result.json',final);save(DOC/'neon-sync.json',dict(jobId=jid,resultVerified=True,snapshotId=snapshot,installedUids=sorted(UIDS)))
    print(json.dumps(dict(installed=sorted(UIDS),snapshotId=snapshot,jobId=jid,neonVerified=True)),flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage-script',required=True);p.add_argument('--previous-count',required=True);p.add_argument('--closure',action='append',required=True);p.add_argument('--owned',action='store_true');args=p.parse_args()
    stage=module('cullinan_unchanged_stage',ROOT/args.stage_script);assert stage.UIDS==UIDS and stage.NATIVE==NATIVE
    if args.owned:
        from publication_lock import locked_publication
        with locked_publication(ROOT):return owned(args,stage)
    assert not DOC.exists()and len(args.closure)==2;server_ready();assert read(stage.DOC/'acceptance.json')['passed']
    keys={'building:'+u for u in UIDS|{NATIVE}}
    claim=reservations.claim('cullinan-two-unchanged-install-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'],claim
    save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
    cmd=[sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--stage-script',args.stage_script,'--previous-count',args.previous_count,'--owned']
    for c in args.closure:cmd.extend(['--closure',c])
    subprocess.run(cmd,cwd=ROOT,check=True)
if __name__=='__main__':main()
