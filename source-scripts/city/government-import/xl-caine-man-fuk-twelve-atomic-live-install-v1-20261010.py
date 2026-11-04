"""Root-owned atomic installation of twelve unchanged staged government originals.

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

CAINE=module('atomic_caine',HERE/'xl-terrain-recovery-20261010-caine-road-two-stage-install-v2.py')
MAN=module('atomic_man_fuk',HERE/'xl-man-fuk-ten-complete-typed-stage-v2-20261010.py')
SUPPLEMENT=module('caine_podium_extra',HERE/'xl-terrain-recovery-20261010-caine-road-podium-solid-followup-v2.py')
MAN_EXTRA=module('man_fuk_podium_extra',HERE/'xl-man-fuk-podium-solid-followup-v1-20261010.py')
BASE=ROOT/'docs/astra-city/government-import'
CAINE_NATIVE=set(read(CAINE.ROLE/'typed-role.json.gz')['completeCurrentRetainedNativeScope']['retainedNativeUids'])
assert len(CAINE_NATIVE)==10
SPECS=[(CAINE,CAINE.UIDS,CAINE_NATIVE,'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'),
       (MAN,MAN.UIDS,MAN.RETAINED,'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs')]
PODIA={CAINE:'landsd/101781:0',MAN:MAN.PODIUM}
UIDS=sorted({u for _,us,_,_ in SPECS for u in us})
BATCH='government-xl-caine-man-fuk-twelve-atomic-installed-v1-20261010'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'install-reservation.json'
MANIFEST_SHA='44c9e80ec3999285616bb12a3fdfbe142a15855db7aa7c3216bffab3500f991a'
ref=CAINE.ref

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
        if view['uid']!=PODIA[stage]:
            p=view['nativeSupports'][PODIA[stage]]
            assert p['active'] and p['visible'] and p.get('declaredCandidateSupport')
    return report

def recheck_all(local):
    out=[]
    for i,(stage,uids,_,_) in enumerate(SPECS):
        rows,identities,role=stage.recheck(local/str(i))
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
        if stage in PODIA:
            p=next(m for m in entries if m['uid']==PODIA[stage])
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
    # Only Caine's appended local child differs from its existing broad wrapper.
    # The two locally changed terrain regions and all cross-assembly bodies
    # must be strictly disjoint; the original broad wrapper grid stays exact.
    a=read(CAINE.PHYSICAL/'terrain-candidates.json')[0]
    b=read(MAN.PHYSICAL/'terrain-candidates.json')[0]
    def disjoint(a,b):
        return a[3]<b[1] or b[3]<a[1] or a[2]<b[0] or b[2]<a[0]
    assert disjoint(a['bounds'],b['bounds'])
    caine_entries=read(CAINE.STAGE/'catalogue.json')['models']
    man_entries=read(MAN.STAGE/'catalogue.json')['models']
    def xz(entry):
        lo,hi=entry['worldBounds'];assert all(lo[i]<=hi[i] for i in range(3))
        return [lo[0],lo[2],hi[0],hi[2]]
    assert all(disjoint(xz(c),xz(m)) for c in caine_entries for m in man_entries)
    assert all(disjoint(a['bounds'],xz(m)) for m in man_entries)
    assert all(disjoint(b['bounds'],xz(c)) for c in caine_entries)
    new=read(ROOT/terrains[0]['source']);old=read(ROOT/'3d-viewer'/terrains[0]['replaces']['url'])
    assert len(new['patches'])==10 and len(old['patches'])==9
    assert new['patches'][:9]==old['patches']
    for k in ['w','h','cell','coarseCells','elev','renderedElev','vegetation','hydro']:
        assert new.get(k)==old.get(k)
    assert new['meta']['georef']==old['meta']['georef']
    assert set(terrains[0]['replaces']['retainedUids'])==CAINE_NATIVE
    assert set(terrains[1]['replaces']['retainedUids'])==MAN.RETAINED
    assert terrains[1]['replaces']['url']=='city/data/government-native-75697-0.json'
    man_patch=read(ROOT/terrains[1]['source'])
    assert man_patch.get('nativeMesh') and len(man_patch['nativeMesh']['index'])//3==10495
    audited=MAN.audited_terrain(b)
    assert ref(ROOT/terrains[1]['source'])['sha256']==audited['sha256']
    for terrain in terrains:
        review=read(ROOT/terrain['nativeReview']['path'])
        assert ref(ROOT/terrain['nativeReview']['path'])==terrain['nativeReview']
        assert review['sourceGeometryChanged'] is False
        assert review['replacementSHA256']==terrain['sha256']
        assert review['supersededSHA256']==terrain['replaces']['sha256']
    supplemental=read(SUPPLEMENT.DOC/'acceptance.json')
    assert supplemental['passed'] and supplemental['allTenNativeOwnViewsRemainBoundToBaseStage']
    assert supplemental['noNativeOrSupportProofOmitted'] and supplemental['extraVisualWitnessUid']==PODIA[CAINE]
    SUPPLEMENT.recheck()
    for item in supplemental['evidenceRefs']:assert ref(ROOT/item['path'])==item
    extra_validator=module('supplement_validator',HERE/'integrate.py')
    extra=extra_validator.browser_verified(SUPPLEMENT.DOC/'staged-browser.json',{PODIA[CAINE]})
    assert len([v for v in extra['views'] if 'time' in v])==4
    refs.extend(supplemental['evidenceRefs']+[ref(SUPPLEMENT.DOC/'acceptance.json')])
    man_extra=read(MAN_EXTRA.DOC/'acceptance.json')
    assert man_extra['passed'] and man_extra['allRetainedNativeOwnViewsRemainBoundToBaseStage']
    assert man_extra['noNativeOrSupportProofOmitted'] and man_extra['extraVisualWitnessUid']==PODIA[MAN]
    MAN_EXTRA.recheck()
    for item in man_extra['evidenceRefs']:assert ref(ROOT/item['path'])==item
    extra=extra_validator.browser_verified(MAN_EXTRA.DOC/'staged-browser.json',{PODIA[MAN]})
    assert len([v for v in extra['views'] if 'time' in v])==4
    refs.extend(man_extra['evidenceRefs']+[ref(MAN_EXTRA.DOC/'acceptance.json')])
    assert len({t['replaces']['url'] for t in terrains})==2 and len({t['destination'] for t in terrains})==2
    assert sorted(m['uid'] for m in models)==UIDS
    current={m['uid'] for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    assert not(set(UIDS)&current) and manifest.read_bytes()==before
    for path in args.closure:
        closure=ROOT/path;closed=read(closure);assert closed['independentlyVerified'] is True and closed['paths'] and closed['verifiedReferenceVersions']>0;refs.append(ref(closure))
    prior=ROOT/args.previous_count;count=read(prior)['counts'];assert count['total']==521 and count['installedVerified']==217 and count['remaining']==304
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
    save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Twelve unchanged government originals: Caine Road pair and Man Fuk ten-source assembly. Both complete original/literal proofs and current-neighbour contexts pass; all11 retained originals receive own live views. Two strictly disjoint terrain proposals change terrain only. Zero AI building geometry.'})
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
        call(['node',str(HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'),'live',ref(SUPPLEMENT.DOC/'browser-config.json')['path']])
        extra=extra_validator.browser_verified(SUPPLEMENT.DOC/'live-browser.json',{PODIA[CAINE]})
        assert len([v for v in extra['views'] if 'time' in v])==4
        call(['node',str(HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'),'live',ref(MAN_EXTRA.DOC/'browser-config.json')['path']])
        extra=extra_validator.browser_verified(MAN_EXTRA.DOC/'live-browser.json',{PODIA[MAN]})
        assert len([v for v in extra['views'] if 'time' in v])==4
    except BaseException:
        manifest.write_bytes(before);save(DOC/'live-failure-rollback.json',dict(manifestRestoredSHA256=digest(manifest.read_bytes()),installedCreditGranted=False));raise
    installed={**decision,'snapshotId':snapshot,'publication':True,'newlyInstalled':12,'manifest':ref(manifest),'liveBrowsers':[ref(s.DOC/'live-browser.json') for s,_,_,_ in SPECS]+[ref(SUPPLEMENT.DOC/'live-browser.json'),ref(MAN_EXTRA.DOC/'live-browser.json')]}
    save(DOC/'installed-acceptance.json',installed)
    ledger.record_many(snapshot,LEASE,[(u,'installed-verified',DOC/'installed-acceptance.json','Unchanged original passes all complete current source/physical gates and staged/live desktop/mobile day/night, framing, picking/collision, retained-source views and failed-load retry. Zero AI geometry modelling.',commit) for u in UIDS],effort=effort,request_id=BATCH+'-installed-'+snapshot)
    assert read(pointer_path)==pointer
    save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inventory_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
    call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
    call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',args.previous_count,'--batch',BATCH])
    stage='atomic-twelve-unchanged-caine-man-fuk-current-source-installed-v1';jid=jobs.enqueue(BATCH,stage,dict(acceptance=ref(DOC/'acceptance.json'),snapshot=snapshot))
    receipt=read(LEASE);job=jobs.claim(BATCH,receipt['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
    final={**installed,'installedUids':UIDS,'evidenceRefs':[ref(DOC/p) for p in ['acceptance.json','installed-acceptance.json','atomic-plan.json']]+[ref(s.DOC/name) for s,_,_,_ in SPECS for name in ['staged-browser.json','live-browser.json']]+[ref(SUPPLEMENT.DOC/'live-browser.json')],'jobId':jid,'newlyInstalled':12,'activeWorkers':0,'queuedFollowups':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json'),'fullXLCurrentCounts':read(DOC/'full-xl-current-count.json')['counts']}
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
    claim=reservations.claim('xl-caine-man-fuk-twelve-atomic-'+str(uuid.uuid4()),[('building:' if u.startswith('landsd/') else 'foreign-form:')+u for u in sorted(scope)]+sorted(resources),batch=BATCH,ttl=3600);assert claim['ok'],claim
    save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
    cmd=[sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--previous-count',args.previous_count,'--owned']
    for c in args.closure:cmd.extend(['--closure',c])
    subprocess.run(cmd,cwd=ROOT,check=True)

if __name__=='__main__':main()
