"""Root-owned atomic installation of four unchanged staged government originals.

Both complete current proofs are replayed against the same manifest before one
guarded apply. Two disjoint local terrain replacements preserve original model
bytes. Both independent live browser suites must pass before installed credit.
"""
import argparse, importlib.util, json, os, subprocess, sys, uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

NO1=module('atomic_no1',HERE/'xl-terrain-recovery-20261010-no1-garden-stage-install-v4.py')
TUNG=module('atomic_tung',HERE/'xl-tung-sing-three-original-complete-typed-stage-v1-20261010.py')
BASE=ROOT/'docs/astra-city/government-import'
NO1_NATIVE=set(read(BASE/'xl-terrain-recovery-20261010-no1-garden-complete-retained-native-v2/retained-scope.json')['retainedNativeUids'])
SPECS=[(NO1,{NO1.UID},NO1_NATIVE,'xl-terrain-recovery-20261009-multi-native-solid-browser-v4.mjs'),
       (TUNG,TUNG.UIDS,TUNG.RETAINED,'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs')]
UIDS=sorted({u for _,us,_,_ in SPECS for u in us})
BATCH='government-xl-no1-tung-four-atomic-installed-v1-20261010'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'install-reservation.json'
MANIFEST_SHA='a3a28145511e3ce6f0b0255d490e1219ad05c643030d00f3e4d9844cdf784b64'
ref=NO1.ref

def browser_verify(stage,uids,retained,filename):
    validator=module('atomic_browser_validator',HERE/'integrate.py')
    report=validator.browser_verified(stage.DOC/filename,uids)
    own=report.get('retainedNativeOwnViews',[])
    expected={(u,w,t) for u in retained for w in [1280,390] for t in ['15:00','22:00']}
    assert len(own)==len(expected) and {(v['uid'],v['width'],v['time']) for v in own}==expected
    assert all(v['active'] and v['visible'] and v['fullyFramed'] for v in own)
    config=read(stage.STAGE/'browser-config.json')
    for view in report['views']:
        if 'time' not in view:continue
        assert set(view['nativeSupports'])==set(config['nativeSupportUidsByModel'][view['uid']])
        assert all(not v['wanted'] or (v['active'] and v['visible']) for u,v in view['nativeSupports'].items() if u in retained)
        if stage is TUNG and view['uid']!=TUNG.PODIUM:
            p=view['nativeSupports'][TUNG.PODIUM]
            assert p['active'] and p['visible'] and p.get('declaredCandidateSupport')
    return report

def recheck_all(local):
    out=[]
    for i,(stage,uids,_,_) in enumerate(SPECS):
        result=stage.recheck(local/str(i))
        if stage is NO1:
            row,identity,role=result;rows=[row];identities=[identity]
        else:rows,identities,role=result
        assert {r['uid'] for r in rows}==uids and role['currentManifest']['sha256']==MANIFEST_SHA
        out.append((rows,identities,role))
    return out

def owned(args):
    def owns():assert reservations.owns(read(LEASE))
    def call(cmd):
        subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
    owns();manifest=ROOT/'3d-viewer/city/data/manifest.json'
    before=manifest.read_bytes();assert digest(before)==MANIFEST_SHA
    refs=[ref(Path(__file__))];models=[];rows=[];areas=[];terrains=[]
    verified=recheck_all(LOCAL/'current-proof-replay')
    for i,((stage,uids,retained,browser),(stage_rows,identities,role)) in enumerate(zip(SPECS,verified)):
        acceptance=read(stage.DOC/'acceptance.json')
        assert acceptance['passed'] and acceptance['checksPassed'] and acceptance['publication'] is False and acceptance['livePublicationRequired']
        assert set(acceptance['uids'])==uids and acceptance['newlyInstalled']==acceptance['modelGeometryChanges']==acceptance['scriptExternalAICalls']==0
        for item in acceptance['evidenceRefs']:assert ref(ROOT/item['path'])==item
        assert ref(stage.DOC/'staged-browser.json')==acceptance['stagedBrowser']
        browser_verify(stage,uids,retained,'staged-browser.json')
        save(DOC/('current-identities-'+str(i)+'.json'),identities)
        save(DOC/('complete-current-role-'+str(i)+'.json.gz'),role)
        entries=read(stage.STAGE/'catalogue.json')['models'];assert {m['uid'] for m in entries}==uids
        for m in entries:
            assert m['sha256']==next(r['sourceSHA256'] for r in stage_rows if r['uid']==m['uid'])
            assert not m.get('suppressesBuildingUids') and m['proceduralWindows'] is False
        if stage is TUNG:
            p=next(m for m in entries if m['uid']==TUNG.PODIUM)
            dependency=dict(uid=p['uid'],csuid=p['buildingCSUID'],sha256=p['sha256'],state='candidate')
            for m in entries:assert m['supportDependencies']==([] if m['uid']==p['uid'] else [dependency])
        else:assert all(not m.get('supportDependencies') for m in entries)
        plan=read(stage.STAGE/'plan.json');assert len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1
        for t in plan['topLevelTerrainPatches']:
            assert t.get('replaces') and not t.get('replacesMany')
            assert set(t['replaces']['retainedUids'])<=retained
            assert ref(ROOT/'3d-viewer'/t['replaces']['url'])['sha256']==t['replaces']['sha256']
            assert ref(ROOT/t['source'])['sha256']==t['sha256']
        models.extend(entries);rows.extend(stage_rows);areas.extend(plan['areas']);terrains.extend(plan['topLevelTerrainPatches'])
        refs.extend(ref(p) for p in [stage.DOC/'acceptance.json',stage.DOC/'staged-browser.json',stage.STAGE/'plan.json',stage.STAGE/'browser-config.json',Path(stage.__file__),HERE/browser,DOC/('current-identities-'+str(i)+'.json'),DOC/('complete-current-role-'+str(i)+'.json.gz')])
    # The only change to No1's existing wrapper is its ninth local child; the
    # prior eight children and broad grid are unchanged. The ninth child and
    # Tung's whole local replacement are disjoint in the viewer's X/Z plane.
    a=read(NO1.PHYSICAL/'terrain-candidates.json')[0];b=read(TUNG.PHYSICAL/'terrain-candidates.json')[0]
    assert a['bounds'][3]<b['bounds'][1] or b['bounds'][3]<a['bounds'][1] or a['bounds'][2]<b['bounds'][0] or b['bounds'][2]<a['bounds'][0]
    no1=read(ROOT/terrains[0]['source']);old=read(ROOT/'3d-viewer'/terrains[0]['replaces']['url'])
    assert len(no1['patches'])==9 and no1['patches'][:8]==old['patches'] and no1['patches'][8]['meta']['targetUids']==[NO1.UID]
    for k in ['w','h','cell','coarseCells','elev','renderedElev','vegetation','hydro']:assert no1.get(k)==old.get(k)
    assert no1['meta']['georef']==old['meta']['georef']
    assert len({t['replaces']['url'] for t in terrains})==2 and len({t['destination'] for t in terrains})==2
    assert sorted(m['uid'] for m in models)==UIDS
    current={m['uid'] for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    assert not(set(UIDS)&current) and manifest.read_bytes()==before
    for path in args.closure:
        closure=ROOT/path;closed=read(closure);assert closed['independentlyVerified'] is True and closed['paths'] and closed['verifiedReferenceVersions']>0;refs.append(ref(closure))
    prior=ROOT/args.previous_count;count=read(prior)['counts'];assert count['total']==521 and count['installedVerified']==215 and count['remaining']==306
    refs.extend([ref(prior),ref(HERE.parent/'model-integration-20260909/publish.py')])
    plan_path=DOC/'atomic-plan.json';save(plan_path,dict(areas=areas,topLevelTerrainPatches=terrains))
    decision=dict(batch=BATCH,uids=UIDS,sourceSHA256s={r['uid']:r['sourceSHA256'] for r in rows},checksPassed=True,passed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,manifestBeforeSHA256=MANIFEST_SHA,stagedAcceptances=[ref(s.DOC/'acceptance.json') for s,_,_,_ in SPECS],atomicPlan=ref(plan_path),localTerrainReplacementsDisjoint=True,evidenceRefs=refs,livePublicationRequired=True)
    save(DOC/'acceptance.json',decision)
    sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
    pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path)
    inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']}
    for m in models:
        previous=parts.get(m['uid'],{})
        parts[m['uid']]=dict(uid=m['uid'],name=m['label'],landmarkIds=previous.get('landmarkIds',[]),objectId=m['objectId'],csuid=m['buildingCSUID'],candidate={'sha256':m['sha256']},sourceProgress='prepared-for-review',classification='verified-unchanged-original-complete-source-and-current-terrain-roles',knownHold=False)
    ordered=sorted(parts.values(),key=lambda p:p['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16]
    inventory_path=pointer_path.parent/('source-review-inventory-'+snapshot+'.json')
    save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Four unchanged government originals: No.1 Garden and mandatory Tung Sing/Lei Tung assembly. Both independent complete original/rendered source proofs and current-neighbour contexts pass; all 16 retained/current originals receive their own live views. Two disjoint local terrain proposals change terrain only. Zero AI building geometry.'})
    ledger.seed(inventory_path,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=ref(DOC/'acceptance.json')['path'])
    ledger.record_many(snapshot,LEASE,[(u,'approved-for-integration',DOC/'acceptance.json','Both full current source-role proofs and staged browsers pass; live checks pending.',commit) for u in UIDS],effort=effort,request_id=BATCH+'-approved-'+snapshot)
    publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(plan_path)['path'],'--receipt',str(LEASE),'--phase',BATCH]
    call(publication);recheck_all(LOCAL/'before-apply-proof-replay');assert manifest.read_bytes()==before
    for item in refs:assert ref(ROOT/item['path'])==item
    (LOCAL/'manifest-before-installation.json').write_bytes(before)
    try:
        call(publication+['--apply'])
        for stage,uids,retained,browser in SPECS:
            call(['node',str(HERE/browser),'live',ref(stage.STAGE/'browser-config.json')['path']])
            browser_verify(stage,uids,retained,'live-browser.json')
    except BaseException:
        manifest.write_bytes(before);save(DOC/'live-failure-rollback.json',dict(manifestRestoredSHA256=digest(manifest.read_bytes()),installedCreditGranted=False));raise
    installed={**decision,'snapshotId':snapshot,'publication':True,'newlyInstalled':4,'manifest':ref(manifest),'liveBrowsers':[ref(s.DOC/'live-browser.json') for s,_,_,_ in SPECS]}
    save(DOC/'installed-acceptance.json',installed)
    ledger.record_many(snapshot,LEASE,[(u,'installed-verified',DOC/'installed-acceptance.json','Unchanged original passes all complete current source/physical gates and staged/live desktop/mobile day/night, framing, picking/collision, retained-source views and failed-load retry. Zero AI geometry modelling.',commit) for u in UIDS],effort=effort,request_id=BATCH+'-installed-'+snapshot)
    assert read(pointer_path)==pointer
    save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inventory_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
    call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
    call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',args.previous_count,'--batch',BATCH])
    stage='atomic-four-unchanged-no1-tung-current-source-installed-v1';jid=jobs.enqueue(BATCH,stage,dict(acceptance=ref(DOC/'acceptance.json'),snapshot=snapshot))
    receipt=read(LEASE);job=jobs.claim(BATCH,receipt['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
    final={**installed,'installedUids':UIDS,'evidenceRefs':[ref(DOC/p) for p in ['acceptance.json','installed-acceptance.json','atomic-plan.json']]+[ref(s.DOC/name) for s,_,_,_ in SPECS for name in ['staged-browser.json','live-browser.json']],'jobId':jid,'newlyInstalled':4,'activeWorkers':0,'queuedFollowups':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json'),'fullXLCurrentCounts':read(DOC/'full-xl-current-count.json')['counts']}
    with connect() as con:
        con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,receipt)
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(final),jid,job['owner'],job['token'])).rowcount==1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',final)
        for r in rows:assert con.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,r['uid'])).fetchone()==('installed-verified',r['sourceSHA256'])
    save(DOC/'result.json',final);save(DOC/'neon-sync.json',dict(jobId=jid,resultVerified=True,snapshotId=snapshot,installedUids=UIDS))
    print(json.dumps(dict(installed=UIDS,snapshotId=snapshot,jobId=jid,neonVerified=True)),flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--owned',action='store_true');p.add_argument('--previous-count',required=True);p.add_argument('--closure',action='append',required=True);args=p.parse_args()
    if args.owned:
        from publication_lock import locked_publication
        with locked_publication(ROOT):return owned(args)
    assert not DOC.exists() and len(args.closure)==2
    assert all(read(s.DOC/'acceptance.json')['passed'] for s,_,_,_ in SPECS)
    scope=set(UIDS);resources=set()
    for s,us,retained,_ in SPECS:
        scope.update(r['building']['uid'] for r in read(s.PHYSICAL/'neighbour-inputs.json.gz')['rows']);scope.update(retained)
        resources.update('terrain-patch:'+u for u in us)
        resources.update('terrain-surface:'+t['replaces']['url'] for t in read(s.STAGE/'plan.json')['topLevelTerrainPatches'])
    claim=reservations.claim('xl-no1-tung-four-atomic-'+str(uuid.uuid4()),[('building:' if u.startswith('landsd/') else 'foreign-form:')+u for u in sorted(scope)]+sorted(resources),batch=BATCH,ttl=3600);assert claim['ok'],claim
    save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
    cmd=[sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--previous-count',args.previous_count,'--owned']
    for c in args.closure:cmd.extend(['--closure',c])
    subprocess.run(cmd,cwd=ROOT,check=True)

if __name__=='__main__':main()
