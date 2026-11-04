"""ROOT-reviewed guarded atomic Park Haven pair plus HKDI Block B.

Requires independently closed source/stage receipts and a reachable dev server.
One reviewed Park terrain replacement; HKDI terrain and legacy native unchanged.
Both complete fresh role replays and all twenty live views/three retries precede
installed credit. Original source bytes, strict limits and raw native holds stay.
"""
import argparse, importlib.util, json, os, subprocess, sys, uuid
from pathlib import Path
from urllib.request import urlopen
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

PARK=module('atomic_park',HERE/'xl-terrain-recovery-20261010-park-haven-two-stage-install-v5.py')
HKDI=module('atomic_hkdi',HERE/'xl-terrain-recovery-20261010-hkdi-block-b-stage-v1.py')
BASE=ROOT/'docs/astra-city/government-import'
SPECS=[(PARK,PARK.UIDS,{'landsd/246270:0'},'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'),
       (HKDI,HKDI.UIDS,{HKDI.NATIVE},'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs')]
PODIA={PARK:'landsd/246467:0'}
UIDS=sorted({u for _,us,_,_ in SPECS for u in us})
BATCH='government-xl-park-haven-hkdi-three-atomic-installed-v4-20261010'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'install-reservation.json'
MANIFEST_SHA='afe71ffa851d82ab2d1350834b5a6cd1484f28e481bd6bf866ca7a6f73e05d0b'
PREVIOUS_SNAPSHOT='af8dc86b47d2b0aa'
TERRAIN_DESTINATION='city/data/terrain-government-xl-park-haven-original-pair-installed-v3-20261010.json'
ref=PARK.ref

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
        if stage in PODIA and view['uid']!=PODIA[stage]:
            p=view['nativeSupports'][PODIA[stage]]
            assert p['active'] and p['visible'] and p.get('declaredCandidateSupport')
    assert len([v for v in report['views'] if 'time' in v])==4*len(uids)
    assert {v['uid'] for v in report['views'] if v.get('fallbackRetained')}==uids
    return report

def recheck_all(local):
    out=[]
    for i,(stage,uids,_,_) in enumerate(SPECS):
        rows,identities,role=stage.recheck(local/str(i))
        assert {r['uid'] for r in rows}==uids and role['currentManifest']['sha256']==MANIFEST_SHA
        out.append((rows,identities,role))
    return out

def server_ready():
    with urlopen('http://127.0.0.1:4176/city.html',timeout=10) as response:
        assert response.status==200 and len(response.read())>100

def owned(args):
    def owns():assert reservations.owns(read(LEASE))
    def call(cmd):
        subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
    owns();manifest=ROOT/'3d-viewer/city/data/manifest.json'
    before=manifest.read_bytes();assert digest(before)==MANIFEST_SHA
    refs=[ref(Path(__file__)),ref(BASE/'government-xl-park-haven-hkdi-three-atomic-installed-v1-20261010/live-failure-rollback.json'),ref(BASE/'government-xl-park-haven-hkdi-three-atomic-installed-v1-20261010/dev-server-live-failure.log'),ref(BASE/'government-xl-park-haven-hkdi-three-atomic-installed-v2-20261010/terrain-destination-guard-failure.log'),ref(BASE/'government-xl-park-haven-hkdi-three-atomic-installed-v1-20261010/failed-live-browser-park.json'),ref(BASE/'government-xl-park-haven-hkdi-three-atomic-installed-v3-20261010/catalogue-destination-guard-failure.log'),ref(BASE/'government-xl-park-haven-hkdi-three-atomic-installed-v1-20261010/rolled-back-viewer-assets/archive-proof.json')];models=[];rows=[];areas=[];terrains=[]
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
        else:
            native=role['completeCurrentInstalledNativeEntryPreserved']
            dependency=dict(uid=HKDI.NATIVE,csuid=native['buildingCSUID'],sha256=native['sha256'],state='installed')
            assert all(m['supportDependencies']==[dependency] for m in entries)
            assert role['nativeReacceptance'] is False and role['currentNativeReacceptance'] is False
            assert role['terrainProposal']==[] and role['terrainProposalGeometryChanged'] is False
            assert native==read(HKDI.DOC/'retained-native-exact-entry-before-stage.json')
        assert all(ref(stage.STAGE/m['asset'])['sha256']==m['sha256'] for m in entries)
        plan=read(stage.STAGE/'plan.json');assert len(plan['areas'])==1
        assert len(plan['topLevelTerrainPatches'])==(1 if stage is PARK else 0)
        for t in plan['topLevelTerrainPatches']:
            t['destination']=TERRAIN_DESTINATION
            assert t.get('replaces') and not t.get('replacesMany')
            assert set(t['replaces']['retainedUids'])<=retained
            assert ref(ROOT/'3d-viewer'/t['replaces']['url'])['sha256']==t['replaces']['sha256']
            assert ref(ROOT/t['source'])['sha256']==t['sha256']
        models.extend(entries);rows.extend(stage_rows);areas.extend(plan['areas']);terrains.extend(plan['topLevelTerrainPatches'])
        refs.extend(ref(p) for p in [stage.DOC/'acceptance.json',stage.DOC/'staged-browser.json',stage.STAGE/'plan.json',stage.STAGE/'browser-config.json',Path(stage.__file__),HERE/browser,DOC/('current-identities-'+str(i)+'.json'),DOC/('complete-current-role-'+str(i)+'.json.gz')])
    # Protected regions include complete original POSITION, runtime/literal/F32,
    # retained actors, all current foreign rings and Park's whole terrain proposal.
    def disjoint(a,b):
        assert len(a)==len(b)==4 and a[0]<=a[2] and a[1]<=a[3] and b[0]<=b[2] and b[1]<=b[3]
        return a[3]<b[1] or b[3]<a[1] or a[2]<b[0] or b[2]<a[0]
    regions=[v[2]['completeCurrentRegionalManifestRebind']['completeFrozenRegionWorldXZBounds'] for v in verified]
    assert disjoint(*regions)
    assert len(terrains)==1 and len(areas)==2
    terrain=terrains[0];assert terrain['replaces']['url']=='city/data/government-native-246270-0.json'
    assert set(terrain['replaces']['retainedUids'])=={'landsd/246270:0'}
    c=read(PARK.PHYSICAL/'terrain-candidates.json')[0]
    assert c['bounds'][0]>=regions[0][0] and c['bounds'][1]>=regions[0][1] and c['bounds'][2]<=regions[0][2] and c['bounds'][3]<=regions[0][3]
    assert disjoint(c['bounds'],regions[1])
    review=read(ROOT/terrain['nativeReview']['path'])
    assert ref(ROOT/terrain['nativeReview']['path'])==terrain['nativeReview']
    assert review['sourceGeometryChanged'] is False and review['terrainProposalChanged'] is True
    assert review['disjointClaim'] is False and review['explicitMeasuredOwnedNativeOverlap'] is True
    assert review['replacementSHA256']==terrain['sha256'] and review['supersededSHA256']==terrain['replaces']['sha256']
    assert review['completeOriginalNativeAndOwnedSourceFoundationsPassed'] is True
    assert set(review['retainedUids'])=={'landsd/246270:0'}
    retained_before={u:next(m for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models'] if m['uid']==u) for _,_,us,_ in SPECS for u in us}
    assert retained_before[HKDI.NATIVE]==verified[1][2]['completeCurrentInstalledNativeEntryPreserved']
    assert sorted(m['uid'] for m in models)==UIDS
    current={m['uid'] for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    assert not(set(UIDS)&current) and manifest.read_bytes()==before
    # Root certificates must cover the actual completed source AND both stages.
    assert len(args.closure)==2
    closures=[]
    for path in args.closure:
        closure=ROOT/path;closed=read(closure)
        assert closed['independentlyVerified'] is True and closed['paths'] and closed['verifiedReferenceVersions']>0
        closures.append(set(closed['paths']));refs.append(ref(closure))
    source_required={ref(s.ROLE/p)['path'] for s,_,_,_ in SPECS for p in ['typed-role.json.gz','result.json']}
    stage_required={ref(s.DOC/p)['path'] for s,_,_,_ in SPECS for p in ['acceptance.json','staged-browser.json']}|{ref(s.STAGE/p)['path'] for s,_,_,_ in SPECS for p in ['plan.json','catalogue.json','browser-config.json']}
    assert any(source_required<=c for c in closures) and any(stage_required<=c for c in closures)
    prior=ROOT/args.previous_count;count=read(prior)['counts']
    assert count['total']==521 and count['installedVerified']==219 and count['remaining']==302
    refs.extend([ref(prior),ref(HERE.parent/'model-integration-20260909/publish.py')])
    plan_path=DOC/'atomic-plan.json';save(plan_path,dict(areas=areas,topLevelTerrainPatches=terrains))
    decision=dict(batch=BATCH,uids=UIDS,sourceSHA256s={r['uid']:r['sourceSHA256'] for r in rows},checksPassed=True,passed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,manifestBeforeSHA256=MANIFEST_SHA,stagedAcceptances=[ref(s.DOC/'acceptance.json') for s,_,_,_ in SPECS],atomicPlan=ref(plan_path),completeAssemblyRegionsStrictlyDisjoint=True,terrainProposalGeometryChanged=True,nativeReacceptance=False,currentNativeReacceptance=False,legacyNativeDiagnosticsPreserved=True,evidenceRefs=refs,livePublicationRequired=True)
    save(DOC/'acceptance.json',decision)
    sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
    pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);assert pointer['snapshotId']==PREVIOUS_SNAPSHOT
    inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']}
    for m in models:
        previous=parts.get(m['uid'],{})
        parts[m['uid']]=dict(uid=m['uid'],name=m['label'],landmarkIds=previous.get('landmarkIds',[]),objectId=m['objectId'],csuid=m['buildingCSUID'],candidate={'sha256':m['sha256']},sourceProgress='prepared-for-review',classification='verified-unchanged-original-complete-source-and-current-terrain-roles',knownHold=False)
    ordered=sorted(parts.values(),key=lambda p:p['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16]
    inventory_path=pointer_path.parent/('source-review-inventory-'+snapshot+'.json')
    save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Three unchanged government originals: Park Haven pair and HKDI Block B. Both complete source/literal/current roles pass in strictly disjoint protected regions. Park terrain-only replacement preserves its retained native; HKDI current terrain/native remain unchanged and raw legacy native negatives retained without native reacceptance. Both retained originals receive own views. Zero AI building geometry; XL count independently audited.'})
    ledger.seed(inventory_path,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=ref(DOC/'acceptance.json')['path'])
    ledger.record_many(snapshot,LEASE,[(u,'approved-for-integration',DOC/'acceptance.json','Both full current source-role proofs and staged browsers pass; live checks pending.',commit) for u in UIDS],effort=effort,request_id=BATCH+'-approved-'+snapshot)
    publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(plan_path)['path'],'--receipt',str(LEASE),'--phase',BATCH]
    call(publication);recheck_all(LOCAL/'before-apply-proof-replay');assert manifest.read_bytes()==before
    server_ready()
    for item in refs:assert ref(ROOT/item['path'])==item
    (LOCAL/'manifest-before-installation.json').write_bytes(before)
    try:
        call(publication+['--apply'])
        for stage,uids,retained,browser in SPECS:
            call(['node',str(HERE/browser),'live',ref(stage.STAGE/'browser-config.json')['path']])
            browser_verify(stage,uids,retained,'live-browser.json')
        current_retained={u:next(m for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models'] if m['uid']==u) for u in retained_before}
        assert current_retained==retained_before
        assert sum(len([v for v in read(s.DOC/'live-browser.json')['views'] if 'time' in v])+len(read(s.DOC/'live-browser.json')['retainedNativeOwnViews']) for s,_,_,_ in SPECS)==20
    except BaseException:
        manifest.write_bytes(before);save(DOC/'live-failure-rollback.json',dict(manifestRestoredSHA256=digest(manifest.read_bytes()),installedCreditGranted=False));raise
    installed={**decision,'snapshotId':snapshot,'publication':True,'newlyInstalled':3,'manifest':ref(manifest),'liveBrowsers':[ref(s.DOC/'live-browser.json') for s,_,_,_ in SPECS]}
    save(DOC/'installed-acceptance.json',installed)
    ledger.record_many(snapshot,LEASE,[(u,'installed-verified',DOC/'installed-acceptance.json','Unchanged original passes all complete current source/physical gates and staged/live desktop/mobile day/night, framing, picking/collision, retained-source views and failed-load retry. Zero AI geometry modelling.',commit) for u in UIDS],effort=effort,request_id=BATCH+'-installed-'+snapshot)
    assert read(pointer_path)==pointer
    save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inventory_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
    call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
    call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',args.previous_count,'--batch',BATCH])
    stage='atomic-three-unchanged-park-haven-hkdi-current-source-installed-v4';jid=jobs.enqueue(BATCH,stage,dict(acceptance=ref(DOC/'acceptance.json'),snapshot=snapshot))
    receipt=read(LEASE);job=jobs.claim(BATCH,receipt['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
    final={**installed,'installedUids':UIDS,'evidenceRefs':[ref(DOC/p) for p in ['acceptance.json','installed-acceptance.json','atomic-plan.json']]+[ref(s.DOC/name) for s,_,_,_ in SPECS for name in ['staged-browser.json','live-browser.json']],'jobId':jid,'newlyInstalled':3,'activeWorkers':0,'queuedFollowups':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json'),'fullXLCurrentCounts':read(DOC/'full-xl-current-count.json')['counts']}
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
    assert not (ROOT/'3d-viewer'/TERRAIN_DESTINATION).exists()
    server_ready()
    for s,_,_,_ in SPECS:
        for area in read(s.STAGE/'plan.json')['areas']:assert not (ROOT/'3d-viewer'/area['destination']).exists()
    assert all(read(s.DOC/'acceptance.json')['passed'] for s,_,_,_ in SPECS)
    scope=set(UIDS);resources=set()
    for s,us,retained,_ in SPECS:
        scope.update(r['building']['uid'] for r in read(s.PHYSICAL/'neighbour-inputs.json.gz')['rows']);scope.update(retained)
        resources.update('terrain-patch:'+u for u in us)
        resources.update('terrain-surface:'+t['replaces']['url'] for t in read(s.STAGE/'plan.json')['topLevelTerrainPatches'])
    claim=reservations.claim('xl-park-haven-hkdi-three-atomic-'+str(uuid.uuid4()),[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope)]+sorted(resources),batch=BATCH,ttl=3600);assert claim['ok'],claim
    save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
    cmd=[sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--previous-count',args.previous_count,'--owned']
    for c in args.closure:cmd.extend(['--closure',c])
    subprocess.run(cmd,cwd=ROOT,check=True)

if __name__=='__main__':main()
