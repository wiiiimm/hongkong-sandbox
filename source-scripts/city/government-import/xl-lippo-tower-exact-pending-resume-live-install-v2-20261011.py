"""DRAFT ONLY: exact own-pending Lippo preapply resume; no terrain changes or review reset.

The complete current role and staged browser must already have independently
closed certificates. The retained native entry remain unchanged and receive no whole-source review credit.
All terrain entries/bytes, all existing native catalogues/assets and current BASIC source forms remain unchanged.
Postapply checks use exact publication deltas; prepublication identity is never replayed against an installed Tower.
"""
import argparse, importlib.util, json, os, subprocess, sys, uuid
from pathlib import Path
from urllib.request import urlopen
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row

BATCH='government-xl-lippo-tower-exact-pending-resume-installed-v2-20261011'
ORIGINAL=ROOT/'docs/astra-city/government-import/government-xl-lippo-tower-current-basic-unchanged-installed-v1-20261011'
PENDING_SNAPSHOT='8d35b6f1d6f6bcdc'
ORIGINAL_ACCEPTANCE_SHA256='f191d93907f340180e7dfd6eb87122620c6f15325fad9d8a8362c62ef2280ff1'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH; LEASE=LOCAL/'install-reservation.json'
UIDS={'landsd/239465:0'};NATIVE='landsd/21915:0';CARRIER='landsd/231645:0'
RETAINED={'landsd/21915:0'}
MANIFEST_SHA='4a6756a928b11a781d5eca86a22278994441985f532dba40a973f46df2902285'
PREVIOUS_SNAPSHOT='0063f9701137947c'
BROWSER=HERE/'xl-lippo-current-basic-solid-browser-v1-20261011.mjs'
STAGE_SCRIPT=HERE/'xl-lippo-tower-exact-pending-resume-recheck-v1-20261011.py'

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def current_native(manifest):
    found=[m for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models'] if m['uid']in RETAINED]
    assert len(found)==len(RETAINED) and {m['uid']for m in found}==RETAINED
    return {m['uid']:m for m in found}
def terrain_snapshot(manifest):
    entries=manifest.get('terrainPatches',[])
    return dict(entries=entries,base=ref(ROOT/'3d-viewer/city/data/terrain.json'),patches={e['url']:ref(ROOT/'3d-viewer'/e['url'])for e in entries})
def native_asset_snapshot(manifest):
    rows={}
    for url in manifest['officialModelCatalogues']:
        cat=ROOT/'3d-viewer'/url
        for e in read(cat)['models']:
            if e['uid']in RETAINED:
                assert e['uid']not in rows;asset=cat.parent/e['asset'];assert digest(asset.read_bytes())==e['sha256'];rows[e['uid']]=dict(entry=e,asset=ref(asset),catalogue=ref(cat))
    assert set(rows)==RETAINED
    return rows

def server_ready():
    with urlopen('http://127.0.0.1:4176/city.html',timeout=10)as r:assert r.status==200 and len(r.read())>100
def browser_verify(stage,name):
    report=module('lippo_live_browser_validation',HERE/'integrate.py').browser_verified(stage.DOC/name,UIDS)
    views=[v for v in report['views']if 'time'in v]
    assert len(views)==4 and {(v['uid'],v['width'],v['time'])for v in views}=={(u,w,t)for u in UIDS for w in [1280,390]for t in ['15:00','22:00']}
    own=report['retainedNativeOwnViews']
    assert len(own)==4 and {(v['uid'],v['width'],v['time'])for v in own}=={(u,w,t)for u in RETAINED for w in [1280,390]for t in ['15:00','22:00']}
    assert all(v['active']and v['visible']and v['fullyFramed']for v in own)
    for view in views:
        assert set(view['nativeSupports'])==RETAINED
        assert view['nativeSupports'][NATIVE]['active']and view['nativeSupports'][NATIVE]['visible']
        basic=view['actualBasicCarrier'];assert basic['completeDrawnFaces']==284 and basic['exactCurrentBasicGeometryVisible'] and basic['productionSupportAvailable'] and basic['wholeBasicReaccepted'] is False
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
    role,entry=stage.recheck(LOCAL/'before-publication')
    assert role['currentManifest']['sha256']==MANIFEST_SHA and role['scriptChecksPassed']
    assert role['acceptanceReadyForStaging'] and not role['installationApproved'] and role['reasons']==[]
    assert role['physicalAccepted'] and not role['wholeBasicReaccepted'] and not role['originalGovernmentPodiumUsedAsRuntimeSupport']
    assert entry['uid'] in UIDS and entry['triangles']==3597
    inp=read(stage.bound.INPUT/'input.json.gz');rows=inp['rows'];identities=[read(stage.bound.IDENTITY/'identity.json')]
    assert {r['uid']for r in rows}==UIDS and entry==read(stage.ROLE/'staged-entry.json')
    assert read(stage.ROLE/'result.json')['modelGeometryChanges']==0
    assert all(r['sourceSHA256']==entry['sha256']for r in rows)
    all_catalogues_before={r['path']:ref(ROOT/r['path'])for r in inp['currentCatalogueRefs']}
    module_form_pins={**inp['currentTileHashes'],**read(stage.bound.INPUT/'complete-current-geometry.json.gz')['inputHashes']}
    source_inventory=read(stage.bound.BASE/'xl-terrain-recovery-20261011-complete-current-native-position-inventory-v8'/'inventory.json.gz')
    assert source_inventory['completeNativeActors']==6639 and all(r['uid']not in UIDS for r in source_inventory['rows'])
    all_current_source_pins={r['source']['path']:r['source']['sha256']for r in source_inventory['rows']}
    acceptance=read(stage.DOC/'acceptance.json')
    assert acceptance['passed']and not acceptance['failures']and acceptance['livePublicationRequired']and not acceptance['publication']
    assert set(acceptance['uids'])==UIDS and acceptance['newlyInstalled']==acceptance['sourceGeometryChanges']==acceptance['terrainGeometryChanges']==0
    assert ref(stage.DOC/'staged-browser.json')==acceptance['stagedBrowser']
    for item in acceptance['evidenceRefs']:assert ref(ROOT/item['path'])==item
    browser_verify(stage,'staged-browser.json')
    models=read(stage.STAGE/'catalogue.json')['models'];assert {m['uid']for m in models}==UIDS
    dependency=dict(uid=CARRIER,csuid='3551417531P20050812',state='surveyed-footprint-fallback')
    for m in models:
        assert m['sha256']==next(r['sourceSHA256']for r in rows if r['uid']==m['uid'])
        assert m['supportDependencies']==[dependency]and not m.get('suppressesBuildingUids')and m['proceduralWindows']is False
        assert ref(stage.STAGE/m['asset'])['sha256']==m['sha256']
    assert stage.retained_snapshot()==read(stage.DOC/'retained-native-before-stage.json')
    plan=read(stage.STAGE/'plan.json');assert len(plan['areas'])==1 and plan['topLevelTerrainPatches']==[]
    terrain_before=terrain_snapshot(read(manifest));native_assets_before=native_asset_snapshot(read(manifest))
    assert native_assets_before==read(stage.DOC/'retained-native-before-stage.json')
    assert all(not(ROOT/'3d-viewer'/a['destination']).exists()for a in plan['areas'])
    current={m['uid']for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']}
    assert not(UIDS&current)
    closures=[];refs=[ref(Path(__file__)),ref(Path(stage.__file__)),ref(BROWSER)]
    for path in args.closure:
        p=ROOT/path;c=read(p);assert c['independentlyVerified']and c['verifiedReferenceVersions']>0
        closures.append(set(c['paths']));refs.append(ref(p))
    assert any({ref(stage.ROLE/p)['path']for p in ['acceptance.json','result.json']}<=c for c in closures)
    required={ref(stage.DOC/p)['path']for p in ['acceptance.json','staged-browser.json']}|{ref(stage.STAGE/p)['path']for p in ['plan.json','catalogue.json','browser-config.json']}
    assert any(required<=c for c in closures)
    resume_required={str((HERE/p).relative_to(ROOT)) for p in [
        'lippo_exact_own_pending_preapply_phase_guard_v1_20261011.py',
        'test_lippo_exact_own_pending_preapply_phase_guard_v1_20261011.py',
        'lippo_tower_current_basic_complete_role_current_bound_v4_20261011.py',
        'test_lippo_tower_current_basic_complete_role_current_bound_v4_20261011.py',
        'xl-lippo-tower-exact-pending-resume-recheck-v1-20261011.py',
        'xl-lippo-tower-exact-pending-resume-live-install-v2-20261011.py',
        'xl-lippo-exact-pending-current-full-replay-diagnostic-v1-20261011.py']}
    replay_doc=stage.bound.BASE/'government-xl-lippo-exact-pending-current-full-replay-diagnostic-v1-20261011'
    replay=read(replay_doc/'result.json');stage.bound.receipt_pins(replay)
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(replay['jobId'],)).fetchone()==('complete',replay)
    proof=read(replay_doc/'diagnostic.json.gz')
    assert proof['completeCurrentMathematicalRoleExactlyMatchesOriginalV3'] and proof['stagedEntryExactlyMatchesOriginalV3']
    assert proof['pendingSnapshotId']==PENDING_SNAPSHOT and proof['publication'] is False and proof['newlyInstalled']==0
    assert proof['currentRole']==role and proof['stagedEntry']==entry
    resume_required.update(str((replay_doc/p).relative_to(ROOT)) for p in ['result.json','diagnostic.json.gz'])
    resume_required.add(str(stage.bound.PENDING_CONTEXT.relative_to(ROOT)))
    resume_required.add(str((ORIGINAL/'acceptance.json').relative_to(ROOT)))
    assert any(resume_required<=c for c in closures), 'new pending phase, replay and resume must be independently closed'
    refs.extend([ref(replay_doc/'result.json'),ref(replay_doc/'diagnostic.json.gz'),ref(stage.bound.PENDING_CONTEXT)])
    previous=ROOT/args.previous_count;assert read(previous)['counts']==dict(total=521,installedVerified=226,remaining=295)
    refs.extend([ref(previous),ref(stage.DOC/'acceptance.json'),ref(stage.DOC/'staged-browser.json'),ref(stage.STAGE/'browser-config.json'),ref(stage.STAGE/'catalogue.json')])
    save(DOC/'retained-terrain-before.json',terrain_before);save(DOC/'retained-native-exact-assets-before.json',native_assets_before);save(DOC/'current-identities.json',identities);save(DOC/'complete-current-role.json.gz',role);save(DOC/'retained-native-before.json',native)
    plan_path=DOC/'atomic-plan.json';save(plan_path,plan)
    refs.extend(ref(DOC/p)for p in ['current-identities.json','complete-current-role.json.gz','retained-native-before.json','retained-terrain-before.json','retained-native-exact-assets-before.json','atomic-plan.json'])
    original_acceptance=ORIGINAL/'acceptance.json'
    assert digest(original_acceptance.read_bytes())==ORIGINAL_ACCEPTANCE_SHA256
    decision=read(original_acceptance)
    assert decision['uids']==sorted(UIDS) and decision['checksPassed'] and not decision['publication'] and decision['newlyInstalled']==0
    assert decision['manifestBeforeSHA256']==MANIFEST_SHA and decision['sourceSHA256s']=={entry['uid']:entry['sha256']}
    for pin in decision['evidenceRefs']:assert ref(ROOT/pin['path'])==pin
    pending_context=read(stage.bound.PENDING_CONTEXT)
    snapshot=PENDING_SNAPSHOT
    assert pending_context['snapshotId']==snapshot
    sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
    pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);assert pointer['snapshotId']==PREVIOUS_SNAPSHOT
    inventory_path=ROOT/pending_context['exactLiveFiles']['pendingInventory']['path']
    assert ref(inventory_path)==pending_context['exactLiveFiles']['pendingInventory']
    assert read(inventory_path)['snapshotId']==snapshot and read(inventory_path)['derivedFrom']==PREVIOUS_SNAPSHOT
    # Original pending inventory and approval event are retained, never reseeded,
    # deleted, regenerated from new code refs or re-recorded under another request.
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=str((DOC/'acceptance.json').relative_to(ROOT)))
    resume=dict(batch=BATCH,snapshotId=snapshot,originalApprovedAcceptance=ref(original_acceptance),
        pendingAttemptContext=ref(stage.bound.PENDING_CONTEXT),sourceSHA256s=decision['sourceSHA256s'],
        exactCurrentRoleReplay=ref(DOC/'complete-current-role.json.gz'),evidenceRefs=refs,
        publication=False,newlyInstalled=0,sourceGeometryChanges=0,terrainGeometryChanges=0,
        originalPendingApprovalAndInventoryRetained=True,historicalReviewDeletion=False,
        newPendingApprovalCreated=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False)
    save(DOC/'acceptance.json',resume)
    publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(plan_path)['path'],'--receipt',str(LEASE),'--phase',BATCH]
    call(publication);replayed,replayed_entry=stage.recheck(LOCAL/'before-apply');assert replayed==role and replayed_entry==entry and manifest.read_bytes()==before
    for item in refs:assert ref(ROOT/item['path'])==item
    server_ready();LOCAL.mkdir(parents=True,exist_ok=True)
    (LOCAL/'manifest-before-installation.json').write_bytes(before)
    try:
        call(publication+['--apply']);call(['node',str(BROWSER),'live',ref(stage.STAGE/'browser-config.json')['path']]);browser_verify(stage,'live-browser.json')
        after=read(manifest);before_obj=json.loads(before);new_url=plan['areas'][0]['destination']
        assert after['officialModelCatalogues']==before_obj['officialModelCatalogues']+[new_url]
        assert {k:v for k,v in after.items()if k!='officialModelCatalogues'}=={k:v for k,v in before_obj.items()if k!='officialModelCatalogues'}
        assert read(ROOT/'3d-viewer'/new_url)==read(stage.STAGE/'catalogue.json')
        assert current_native(after)==native and native_asset_snapshot(after)==native_assets_before and terrain_snapshot(after)==terrain_before
        for path,pin in all_catalogues_before.items():assert ref(ROOT/path)==pin
        for path,sha in all_current_source_pins.items():assert digest((ROOT/path).read_bytes())==sha
        for path,sha in module_form_pins.items():
            if path=='3d-viewer/city/data/manifest.json':assert sha==MANIFEST_SHA;continue
            assert digest((ROOT/path).read_bytes())==sha
        assert len({m['uid']for u in after['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/u)['models']})==6640
        installed_cat=ROOT/'3d-viewer'/new_url;installed_entry=read(installed_cat)['models'][0]
        assert installed_entry==entry and digest((installed_cat.parent/entry['asset']).read_bytes())==entry['sha256']

    except BaseException:
        manifest.write_bytes(before);save(DOC/'live-failure-rollback.json',dict(manifestRestoredSHA256=digest(manifest.read_bytes()),installedCreditGranted=False));raise
    installed={**decision,'batch':BATCH,'resumeAttempt':ref(DOC/'acceptance.json'),'resumedOriginalApprovalWithoutHistoryEdits':True,'snapshotId':snapshot,'publication':True,'newlyInstalled':1,'manifest':ref(manifest),'liveBrowser':ref(stage.DOC/'live-browser.json')}
    save(DOC/'installed-acceptance.json',installed)
    ledger.record_many(snapshot,LEASE,[(u,'installed-verified',DOC/'installed-acceptance.json','Unchanged original passes complete current source/physical gates, staged/live desktop/mobile day/night, framing, picking/collision, retained-source views and failed-load retry. Zero AI modelling.',commit)for u in sorted(UIDS)],effort=effort,request_id=BATCH+'-installed-'+snapshot)
    assert read(pointer_path)==pointer
    save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inventory_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
    call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
    call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',args.previous_count,'--batch',BATCH])
    counts=read(DOC/'full-xl-current-count.json')['counts'];assert counts['total']==521 and counts['installedVerified']+counts['remaining']==521
    assert counts==dict(total=521,installedVerified=226,remaining=295), 'Lippo Tower is auxiliary outside immutable521; BASIC podium source remains held'
    save(DOC/'conditional-fixed-xl-count-delta.json',dict(previousFixedXLInstalled=226,currentFixedXLInstalled=counts['installedVerified'],actualFixedXLDelta=counts['installedVerified']-226,newOriginalInstallations=1,auxiliaryImportDoesNotAutomaticallyIncreaseFixedXL=True,governmentPodium231645Installed=False))
    kind='unchanged-lippo-tower-exact-current-basic-carrier-installed-v2';jid=jobs.enqueue(BATCH,kind,dict(acceptance=ref(DOC/'acceptance.json'),snapshot=snapshot))
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
    assert (ROOT/args.stage_script).resolve()==STAGE_SCRIPT.resolve()
    stage=module('lippo_unchanged_stage',ROOT/args.stage_script);assert {stage.UID}==UIDS and stage.CARRIER==CARRIER and set(stage.RETAINED)==RETAINED
    if args.owned:
        from publication_lock import locked_publication
        with locked_publication(ROOT):return owned(args,stage)
    assert not DOC.exists()and len(args.closure)==2;server_ready();assert read(stage.DOC/'acceptance.json')['passed']
    forms=read(stage.bound.INPUT/'input.json.gz')['completeCurrentForms']
    keys={(('building:'if r['building']['uid'].startswith('landsd/')else'foreign-form:')+r['building']['uid'])for r in forms}
    keys.update('building:'+u for u in UIDS|RETAINED|{CARRIER})
    claim=reservations.claim('lippo-unchanged-install-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'],claim
    save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
    cmd=[sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--stage-script',args.stage_script,'--previous-count',args.previous_count,'--owned']
    for c in args.closure:cmd.extend(['--closure',c])
    subprocess.run(cmd,cwd=ROOT,check=True)
if __name__=='__main__':main()
