"""Unexecuted root-only guarded publication of the complete Mount Verdant pair.

Two independently verified source/stage closures and all live browser checks
are mandatory. Original building bytes/pose are unchanged; the explicit
authentic-TIN terrain proposal replaces coarse terrain without native reapproval.
"""
import argparse, copy, importlib.util, json, os, shutil, subprocess, sys, uuid
from pathlib import Path
from urllib.request import urlopen
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row

BATCH='government-xl-mount-verdant-two-unchanged-installed-v1-20261011'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH; LEASE=LOCAL/'install-reservation.json'
UIDS={'landsd/261717:0','landsd/75782:0'};PODIUM='landsd/75782:0'
MANIFEST_SHA='b61c0bc2d706793c7d436ef3334ccb41e93675d3d50c29818a2dca3b56f8830e'
PREVIOUS_SNAPSHOT='8d35b6f1d6f6bcdc'
SOURCE_CERT='docs/astra-city/government-import/government-xl-mount-verdant-source-root-closure-v1-20261011/root-closed-scope.json'
STAGE_CERT='docs/astra-city/government-import/government-xl-mount-verdant-stage-root-closure-v1-20261011/root-closed-scope.json'
STAGE_SCRIPT='source-scripts/city/government-import/xl-terrain-recovery-20261011-mount-verdant-two-stage-install-v1.py'
INVENTORY=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261011-complete-current-native-position-inventory-v9/inventory.json.gz'
BROWSER=HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def server_ready():
    with urlopen('http://127.0.0.1:4176/city.html',timeout=10)as r:assert r.status==200 and len(r.read())>100
def browser_verify(stage,name):
    report=module('mount_verdant_live_browser_validation',HERE/'integrate.py').browser_verified(stage.DOC/name,UIDS)
    views=[v for v in report['views']if 'time'in v]
    assert len(views)==8 and {(v['uid'],v['width'],v['time'])for v in views}=={(u,w,t)for u in UIDS for w in [1280,390]for t in ['15:00','22:00']}
    assert not report.get('retainedNativeOwnViews')
    config=read(stage.STAGE/'browser-config.json')
    assert config['nativeSupportUidsByModel']=={PODIUM:[],'landsd/261717:0':[PODIUM]}
    for view in views:
        expected=set(config['nativeSupportUidsByModel'][view['uid']])
        assert set(view['nativeSupports'])==expected
        assert all(v['active']and v['visible']and v.get('declaredCandidateSupport')for v in view['nativeSupports'].values())
    assert {v['uid']for v in report['views']if v.get('fallbackRetained')}==UIDS
    return report

def owned(args,stage):
    def owns():assert reservations.owns(read(LEASE))
    def call(cmd):
        subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
    owns();server_ready();manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes()
    assert digest(before)==MANIFEST_SHA
    old_manifest=read(manifest);inv=read(INVENTORY)
    assert inv['currentManifest']['sha256']==MANIFEST_SHA and inv['completeNativeActors']==6640
    before_catalogue_urls=old_manifest['officialModelCatalogues'];before_terrain=old_manifest['terrainPatches']
    before_entries={m['uid']:m for url in before_catalogue_urls for m in read(ROOT/'3d-viewer'/url)['models']}
    assert len(before_entries)==6640 and len(inv['rows'])==6640 and{r['uid']for r in inv['rows']}==set(before_entries)
    preserved_pins={}
    for item in inv['rows']:
        assert item['rawCurrentEntry']==before_entries[item['uid']]
        for pin in [item['catalogue'],item['source']]:
            assert ref(ROOT/pin['path'])==pin;preserved_pins[pin['path']]=pin
    for path in [ROOT/'3d-viewer/city/data/terrain.json']+[ROOT/'3d-viewer'/t['url']for t in before_terrain]:
        pin=ref(path);preserved_pins[pin['path']]=pin
    assert len({item['uid']for item in inv['rows']})==6640
    rows,identities,role=stage.recheck(LOCAL/'before-publication')
    assert {r['uid']for r in rows}==UIDS and role['currentManifest']['sha256']==MANIFEST_SHA
    assert role['currentTypedPhysicalAccepted']and role['readyForStagedBrowser']and not role['installationApproved']and not role['reasons']
    assert role['completeOriginalFaces']==15579 and role['completeOriginalNonzeroBodies']==973 and role['completeCurrentForeignForms']==13
    assert role['nativeReacceptance']is False and role['sourceGeometryChanges']==0
    unchanged_role_pins=[pin for pin in read(stage.ROLE/'result.json')['evidenceRefs']if pin['path']!='3d-viewer/city/data/manifest.json']
    for pin in unchanged_role_pins:assert ref(ROOT/pin['path'])==pin
    save(DOC/'prepublication-preserved-current-inputs.json',dict(currentNativeInventory=ref(INVENTORY),complete6640RawEntries=before_entries,completeCatalogueTerrainSourcePins=list(preserved_pins.values()),currentFormSourceModulePins=unchanged_role_pins))
    assert all(p['all973NonzeroBodiesAccounted']for p in role['completeFourStreamComposition'])
    acceptance=read(stage.DOC/'acceptance.json')
    assert acceptance['passed']and acceptance['checksPassed']and acceptance['livePublicationRequired']and not acceptance['publication']
    assert set(acceptance['uids'])==UIDS and acceptance['newlyInstalled']==acceptance['modelGeometryChanges']==acceptance['scriptExternalAICalls']==0
    assert ref(stage.DOC/'staged-browser.json')==acceptance['stagedBrowser']
    for item in acceptance['evidenceRefs']:assert ref(ROOT/item['path'])==item
    browser_verify(stage,'staged-browser.json')
    models=read(stage.STAGE/'catalogue.json')['models'];assert {m['uid']for m in models}==UIDS
    podium=next(m for m in models if m['uid']==PODIUM)
    dependency=dict(uid=PODIUM,csuid=podium['buildingCSUID'],sha256=podium['sha256'],state='candidate')
    for m in models:
        assert m['sha256']==next(r['sourceSHA256']for r in rows if r['uid']==m['uid'])
        assert m['supportDependencies']==([]if m['uid']==PODIUM else[dependency])and not m.get('suppressesBuildingUids')and not m.get('footprintScope')and m['proceduralWindows']is False
        assert ref(stage.STAGE/m['asset'])['sha256']==m['sha256']
    assert models[0]['uid']==PODIUM
    plan=read(stage.STAGE/'plan.json');assert len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1
    assert all(not(ROOT/'3d-viewer'/a['destination']).exists()for a in plan['areas'])
    terrain=plan['topLevelTerrainPatches'][0]
    assert not terrain.get('replaces')and not terrain.get('replacesMany')
    assert terrain['destination']=='city/data/terrain-government-xl-mount-verdant-original-pair-installed-v1-20261011.json'
    assert not(ROOT/'3d-viewer'/terrain['destination']).exists()
    assert ref(ROOT/terrain['source'])['sha256']==terrain['sha256']=='00afbe63bb404dc325923596687ccb398f8c4600703b465cbfcb94dbad13468b'
    patch=read(ROOT/terrain['source']);assert patch.get('nativeMesh')and not patch.get('patches')and len(patch['nativeMesh']['index'])//3==14449
    original=read(stage.PHYSICAL/'terrain-candidates.json');assert len(original)==1 and set(original[0]['uids'])==UIDS and original[0]['sha256']==terrain['sha256']
    assert patch['meta']['parentTerrain']=='city/data/terrain.json'and patch['meta']['parentSha256']==ref(ROOT/'3d-viewer/city/data/terrain.json')['sha256']
    current={m['uid']for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']}
    assert not(UIDS&current)
    closures=[];refs=[ref(Path(__file__)),ref(Path(stage.__file__)),ref(BROWSER),ref(DOC/'prepublication-preserved-current-inputs.json'),ref(INVENTORY)]
    for path in args.closure:
        p=ROOT/path;c=read(p);assert c['independentlyVerified']and c['verifiedReferenceVersions']>0
        closures.append(set(c['paths']));refs.append(ref(p))
    assert any({ref(stage.ROLE/p)['path']for p in ['typed-role.json.gz','result.json']}<=c for c in closures)
    required={ref(stage.DOC/p)['path']for p in ['acceptance.json','staged-browser.json']}|{ref(stage.STAGE/p)['path']for p in ['plan.json','catalogue.json','browser-config.json']}|{SOURCE_CERT,'docs/astra-city/government-import/xl-terrain-recovery-20261011-mount-langham-hoi-source-checkpoint-scope-v2/declared-scope.json'}
    assert any(required<=c for c in closures)
    previous=ROOT/args.previous_count;assert read(previous)['counts']==dict(total=521,installedVerified=226,remaining=295)and read(previous)['manifestSHA256']==MANIFEST_SHA and read(previous)['snapshotId']==PREVIOUS_SNAPSHOT
    refs.extend([ref(previous),ref(stage.DOC/'acceptance.json'),ref(stage.DOC/'staged-browser.json'),ref(stage.STAGE/'browser-config.json'),ref(stage.STAGE/'catalogue.json')])
    save(DOC/'current-identities.json',identities);save(DOC/'complete-current-role.json.gz',role)
    publication_dir=LOCAL/'publication-catalogue';publication_dir.mkdir(parents=True)
    publication_catalogue=copy.deepcopy(read(stage.STAGE/'catalogue.json'))
    for m in publication_catalogue['models']:
        if m['uid']!=PODIUM:m['supportDependencies']=[{**dependency,'state':'installed'}]
        asset=publication_dir/m['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(stage.STAGE/m['asset'],asset)
        assert ref(asset)['sha256']==m['sha256'];refs.append(ref(asset))
    normalized=copy.deepcopy(publication_catalogue)
    for m in normalized['models']:
        if m['uid']!=PODIUM:m['supportDependencies']=[dependency]
    assert normalized==read(stage.STAGE/'catalogue.json')
    save(publication_dir/'catalogue.json',publication_catalogue)
    save(DOC/'candidate-to-installed-dependency-publication.json',dict(original=ref(stage.STAGE/'catalogue.json'),published=ref(publication_dir/'catalogue.json'),onlyChangedPath='/models/1/supportDependencies/0/state',before='candidate',after='installed',exactUid=dependency['uid'],exactCSUID=dependency['csuid'],exactSourceSHA256=dependency['sha256'],allOtherFieldsEqual=True,modelGeometryChanges=0))
    publication_plan=copy.deepcopy(plan);publication_plan['areas'][0]['catalogue']=ref(publication_dir/'catalogue.json')['path']
    plan_path=DOC/'atomic-plan.json';save(plan_path,publication_plan)
    refs.extend([ref(publication_dir/'catalogue.json'),ref(DOC/'candidate-to-installed-dependency-publication.json')])
    refs.extend(ref(DOC/p)for p in ['current-identities.json','complete-current-role.json.gz','atomic-plan.json'])
    decision=dict(batch=BATCH,uids=sorted(UIDS),sourceSHA256s={r['uid']:r['sourceSHA256']for r in rows},checksPassed=True,passed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,terrainProposalGeometryChanged=True,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,manifestBeforeSHA256=MANIFEST_SHA,nativeReacceptance=False,nativeAvailabilityUnchanged=True,evidenceRefs=refs,livePublicationRequired=True)
    save(DOC/'acceptance.json',decision)
    sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
    pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);assert pointer['snapshotId']==PREVIOUS_SNAPSHOT
    inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']}
    for m in models:
        prior=parts.get(m['uid'],{})
        parts[m['uid']]=dict(uid=m['uid'],name=m['label'],landmarkIds=prior.get('landmarkIds',[]),objectId=m['objectId'],csuid=m['buildingCSUID'],candidate={'sha256':m['sha256']},sourceProgress='prepared-for-review',classification='verified-unchanged-original-complete-source-and-current-terrain-roles',knownHold=False)
    ordered=sorted(parts.values(),key=lambda p:p['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16]
    inventory_path=pointer_path.parent/('source-review-inventory-'+snapshot+'.json')
    save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':stage.PLACEMENT})
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
        after=read(manifest)
        assert after['officialModelCatalogues']==before_catalogue_urls+[publication_plan['areas'][0]['destination']]
        assert after['terrainPatches'][:-1]==before_terrain and len(after['terrainPatches'])==len(before_terrain)+1
        assert after['terrainPatches'][-1]['url']==terrain['destination']and after['terrainPatches'][-1]['sha256']==terrain['sha256']
        for pin in list(preserved_pins.values())+unchanged_role_pins:assert ref(ROOT/pin['path'])==pin
        all_after=[m for url in after['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']]
        assert len(all_after)==6642 and len({m['uid']for m in all_after})==6642
        assert {m['uid']:m for m in all_after if m['uid']not in UIDS}==before_entries
        assert read(ROOT/'3d-viewer'/publication_plan['areas'][0]['destination'])==publication_catalogue
        published=[m for m in all_after if m['uid']in UIDS]
        assert len(published)==2 and {m['uid']for m in published}==UIDS
        for m in published:
            assert m['sha256']==next(r['sourceSHA256']for r in rows if r['uid']==m['uid'])
            assert ref(ROOT/'3d-viewer'/Path(publication_plan['areas'][0]['destination']).parent/m['asset'])['sha256']==m['sha256']
            assert m['supportDependencies']==([]if m['uid']==PODIUM else[{**dependency,'state':'installed'}])
        assert ref(ROOT/'3d-viewer'/terrain['destination'])['sha256']==terrain['sha256']
    except BaseException:
        manifest.write_bytes(before);save(DOC/'live-failure-rollback.json',dict(manifestRestoredSHA256=digest(manifest.read_bytes()),installedCreditGranted=False));raise
    installed={**decision,'snapshotId':snapshot,'publication':True,'newlyInstalled':2,'manifest':ref(manifest),'liveBrowser':ref(stage.DOC/'live-browser.json')}
    save(DOC/'installed-acceptance.json',installed)
    ledger.record_many(snapshot,LEASE,[(u,'installed-verified',DOC/'installed-acceptance.json','Unchanged original passes complete current source/physical gates, staged/live desktop/mobile day/night, framing, picking/collision, candidate podium support and failed-load retry. Zero AI modelling.',commit)for u in sorted(UIDS)],effort=effort,request_id=BATCH+'-installed-'+snapshot)
    assert read(pointer_path)==pointer
    save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inventory_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
    call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
    call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',args.previous_count,'--batch',BATCH])
    assert read(DOC/'full-xl-current-count.json')['counts']==dict(total=521,installedVerified=227,remaining=294)
    kind='two-unchanged-mount-verdant-originals-current-source-installed-v1';jid=jobs.enqueue(BATCH,kind,dict(acceptance=ref(DOC/'acceptance.json'),snapshot=snapshot))
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
    assert args.stage_script==STAGE_SCRIPT
    stage=module('mount_verdant_unchanged_stage',ROOT/args.stage_script);assert stage.UIDS==UIDS
    if args.owned:
        from publication_lock import locked_publication
        with locked_publication(ROOT):return owned(args,stage)
    assert not DOC.exists()and len(args.closure)==2 and set(args.closure)=={SOURCE_CERT,STAGE_CERT};server_ready();assert read(stage.DOC/'acceptance.json')['passed']
    forms=read(stage.PHYSICAL/'neighbour-inputs.json.gz')['rows']
    keys={('building:'if r['building']['uid'].startswith('landsd/')else'foreign-form:')+r['building']['uid']for r in forms}|{'terrain-patch:'+u for u in UIDS}
    assert {'building:'+u for u in UIDS}<=keys
    claim=reservations.claim('mount-verdant-two-unchanged-install-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'],claim
    save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
    cmd=[sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--stage-script',args.stage_script,'--previous-count',args.previous_count,'--owned']
    for c in args.closure:cmd.extend(['--closure',c])
    subprocess.run(cmd,cwd=ROOT,check=True)
if __name__=='__main__':main()
