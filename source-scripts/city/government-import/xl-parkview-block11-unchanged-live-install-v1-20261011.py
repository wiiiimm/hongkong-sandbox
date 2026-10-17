"""Root-only publication of unchanged Parkview Block 11 with reviewed terrain replacement.

The complete current role and staged browser must already have independently
closed certificates. All four retained native entries remain unchanged and receive no whole-source review credit.
Only the independently checked terrain replacement changes. Original model bytes, source pose and legacy native acceptance flags remain unchanged.
"""
import argparse, importlib.util, json, os, subprocess, sys, uuid
from pathlib import Path
from urllib.request import urlopen
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row

BATCH='government-xl-parkview-block11-unchanged-installed-v1-20261011'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH; LEASE=LOCAL/'install-reservation.json'
UIDS={'landsd/255647:0'};NATIVE='landsd/254491:0'
RETAINED={'landsd/254491:0','landsd/255439:0','landsd/256112:0','landsd/256114:0'}
MANIFEST_SHA='aba0edb60daac0497b98c78d21507461b13b20a4ddcc177ca0526fabeaa86eef'
PREVIOUS_SNAPSHOT='49a5adaa2155315c'
BROWSER=HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def current_native(manifest):
    found=[m for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models'] if m['uid']in RETAINED]
    assert len(found)==len(RETAINED) and {m['uid']for m in found}==RETAINED
    return {m['uid']:m for m in found}
def server_ready():
    with urlopen('http://127.0.0.1:4176/city.html',timeout=10)as r:assert r.status==200 and len(r.read())>100
def browser_verify(stage,name):
    report=module('parkview_live_browser_validation',HERE/'integrate.py').browser_verified(stage.DOC/name,UIDS)
    views=[v for v in report['views']if 'time'in v]
    assert len(views)==4 and {(v['uid'],v['width'],v['time'])for v in views}=={(u,w,t)for u in UIDS for w in [1280,390]for t in ['15:00','22:00']}
    own=report['retainedNativeOwnViews']
    assert len(own)==16 and {(v['uid'],v['width'],v['time'])for v in own}=={(u,w,t)for u in RETAINED for w in [1280,390]for t in ['15:00','22:00']}
    assert all(v['active']and v['visible']and v['fullyFramed']for v in own)
    for view in views:
        assert set(view['nativeSupports'])==RETAINED
        assert view['nativeSupports'][NATIVE]['active']and view['nativeSupports'][NATIVE]['visible']
        assert all(not p['wanted']or(p['active']and p['visible'])for p in view['nativeSupports'].values())
    assert {v['uid']for v in report['views']if v.get('fallbackRetained')}==UIDS
    return report

def owned(args,stage):
    def owns():assert reservations.owns(read(LEASE))
    def call(cmd):
        subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
    owns();server_ready();manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes()
    assert digest(before)==MANIFEST_SHA
    native=current_native(read(manifest))
    assert native[NATIVE]['sha256']=='8d1de7a507bedd3b321786220569d5ff4ee279496220bd1e5c93580411c7ad77'
    rows,identities,role=stage.recheck(LOCAL/'before-publication')
    assert {r['uid']for r in rows}==UIDS and role['currentManifest']['sha256']==MANIFEST_SHA
    assert role['scriptChecksPassed']and role['readyForStagedBrowser']and not role['installationApproved']
    assert role['completeOriginalFaces']==10679 and role['completeOriginalComponents']==81 and role['nativeReacceptance']is False
    assert role['independentlySupportedStructuralOwnedComponents']==80 and role['visualOnlyOwnedComponents']==[324]
    assert role['sourceGeometryChanges']==0 and role['terrainProposalGeometryChanged']is True
    assert role['currentTypedPhysicalAccepted']is True and not role['reasons'] and role['namedRoofUnitRootOrBridgeCredit']is False
    assert role['completeCurrentInstalledNativeEntriesPreserved']==native and set(role['retainedNativeUIDs'])==RETAINED
    acceptance=read(stage.DOC/'acceptance.json')
    assert acceptance['passed']and acceptance['checksPassed']and acceptance['livePublicationRequired']and not acceptance['publication']
    assert set(acceptance['uids'])==UIDS and acceptance['newlyInstalled']==acceptance['modelGeometryChanges']==acceptance['scriptExternalAICalls']==0
    assert ref(stage.DOC/'staged-browser.json')==acceptance['stagedBrowser']
    for item in acceptance['evidenceRefs']:assert ref(ROOT/item['path'])==item
    browser_verify(stage,'staged-browser.json')
    models=read(stage.STAGE/'catalogue.json')['models'];assert {m['uid']for m in models}==UIDS
    dependency=dict(uid=NATIVE,csuid=native[NATIVE]['buildingCSUID'],sha256=native[NATIVE]['sha256'],state='installed')
    for m in models:
        assert m['sha256']==next(r['sourceSHA256']for r in rows if r['uid']==m['uid'])
        assert m['supportDependencies']==[dependency]and not m.get('suppressesBuildingUids')and m['proceduralWindows']is False
        assert ref(stage.STAGE/m['asset'])['sha256']==m['sha256']
    assert native==read(stage.DOC/'retained-native-exact-entries-before-stage.json')
    plan=read(stage.STAGE/'plan.json');assert len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1
    terrain=plan['topLevelTerrainPatches'][0];replacement=terrain['replaces']
    assert not terrain.get('replacesMany') and replacement==dict(url='city/data/government-native-255439-0.json',sha256='6b4a065b4e5cb3e62c82434ad03b47206c17765498b9b6e65a8f2ad9355097b5',retainedUids=['landsd/255439:0'])
    oldterrain=ROOT/'3d-viewer'/replacement['url'];oldbytes=oldterrain.read_bytes();assert digest(oldbytes)==replacement['sha256']
    assert terrain['destination']!=replacement['url'] and not(ROOT/'3d-viewer'/terrain['destination']).exists()
    assert ref(ROOT/terrain['source'])['sha256']==terrain['sha256']=='12816eebe4f6600fd13a41a897bfd9c044e2a7ac5edf0dde0d7d76647642f1d6'
    patch=read(ROOT/terrain['source']);assert len(patch['nativeMesh']['index'])//3==94794 and patch['meta']['targetUids']==['landsd/255439:0','landsd/255647:0']
    assert ref(ROOT/terrain['nativeReview']['path'])==terrain['nativeReview']
    review=read(ROOT/terrain['nativeReview']['path']);assert review['status']=='approved-for-integration' and review['replacementSHA256']==terrain['sha256'] and review['sourceGeometryChanged']is False
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
    previous=ROOT/args.previous_count;assert read(previous)['counts']==dict(total=521,installedVerified=223,remaining=298)
    refs.extend([ref(previous),ref(stage.DOC/'acceptance.json'),ref(stage.DOC/'staged-browser.json'),ref(stage.STAGE/'browser-config.json'),ref(stage.STAGE/'catalogue.json')])
    save(DOC/'current-identities.json',identities);save(DOC/'complete-current-role.json.gz',role);save(DOC/'retained-native-before.json',native)
    plan_path=DOC/'atomic-plan.json';save(plan_path,plan)
    refs.extend(ref(DOC/p)for p in ['current-identities.json','complete-current-role.json.gz','retained-native-before.json','atomic-plan.json'])
    decision=dict(batch=BATCH,uids=sorted(UIDS),sourceSHA256s={r['uid']:r['sourceSHA256']for r in rows},checksPassed=True,passed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,terrainProposalGeometryChanged=True,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,manifestBeforeSHA256=MANIFEST_SHA,nativeReacceptance=False,legacyNativeDiagnosticsPreserved=True,legacyDependencyStateMeansCurrentNativeAvailabilityOnly=True,evidenceRefs=refs,livePublicationRequired=True)
    save(DOC/'acceptance.json',decision)
    sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
    pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);assert pointer['snapshotId']==PREVIOUS_SNAPSHOT
    inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']}
    for m in models:
        prior=parts.get(m['uid'],{})
        parts[m['uid']]=dict(uid=m['uid'],name=m['label'],landmarkIds=prior.get('landmarkIds',[]),objectId=m['objectId'],csuid=m['buildingCSUID'],candidate={'sha256':m['sha256']},sourceProgress='prepared-for-review',classification='verified-unchanged-original-complete-source-and-current-terrain-roles',knownHold=False)
    ordered=sorted(parts.values(),key=lambda p:p['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16]
    inventory_path=pointer_path.parent/('source-review-inventory-'+snapshot+'.json')
    save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Complete unchanged Parkview Block 11; bounded exposed original native grade-wall and roof contact, 80 independently supported original parts and one narrowly mounted original roof appendage. Authenticated terrain replacement preserves all 26 forms and four current native sources. No source geometry or pose edits, no whole native reacceptance; zero AI modelling.'})
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
        assert current_native(read(manifest))==native and oldterrain.read_bytes()==oldbytes
    except BaseException:
        manifest.write_bytes(before);save(DOC/'live-failure-rollback.json',dict(manifestRestoredSHA256=digest(manifest.read_bytes()),installedCreditGranted=False));raise
    installed={**decision,'snapshotId':snapshot,'publication':True,'newlyInstalled':1,'manifest':ref(manifest),'liveBrowser':ref(stage.DOC/'live-browser.json')}
    save(DOC/'installed-acceptance.json',installed)
    ledger.record_many(snapshot,LEASE,[(u,'installed-verified',DOC/'installed-acceptance.json','Unchanged original passes complete current source/physical gates, staged/live desktop/mobile day/night, framing, picking/collision, retained-source views and failed-load retry. Zero AI modelling.',commit)for u in sorted(UIDS)],effort=effort,request_id=BATCH+'-installed-'+snapshot)
    assert read(pointer_path)==pointer
    save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inventory_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
    call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
    call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',args.previous_count,'--batch',BATCH])
    kind='unchanged-parkview-block11-bounded-current-source-installed-v1';jid=jobs.enqueue(BATCH,kind,dict(acceptance=ref(DOC/'acceptance.json'),snapshot=snapshot))
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
    stage=module('parkview_unchanged_stage',ROOT/args.stage_script);assert stage.UIDS==UIDS and stage.NATIVE==NATIVE and set(stage.RETAINED)==RETAINED
    if args.owned:
        from publication_lock import locked_publication
        with locked_publication(ROOT):return owned(args,stage)
    assert not DOC.exists()and len(args.closure)==2;server_ready();assert read(stage.DOC/'acceptance.json')['passed']
    forms=read(stage.PHYSICAL/'neighbour-inputs.json.gz')['rows']
    keys={(('building:'if r['building']['uid'].startswith('landsd/')else'foreign-form:')+r['building']['uid'])for r in forms}
    keys.update('building:'+u for u in UIDS|RETAINED)
    keys.update({'terrain-patch:landsd/255647:0','terrain-surface:city/data/government-native-255439-0.json','terrain-surface:city/data/terrain-government-xl-parkview-block11-authentic-installed-v1-20261011.json'})
    claim=reservations.claim('parkview-unchanged-install-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'],claim
    save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
    cmd=[sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--stage-script',args.stage_script,'--previous-count',args.previous_count,'--owned']
    for c in args.closure:cmd.extend(['--closure',c])
    subprocess.run(cmd,cwd=ROOT,check=True)
if __name__=='__main__':main()
