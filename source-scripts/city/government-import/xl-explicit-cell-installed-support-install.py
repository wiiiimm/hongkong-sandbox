"""Install an unchanged supported tower with fresh full physical/browser gates."""
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row,NATIVE_RUN
from dependency_preflight import from_catalogues
from installed_support_acceptance import verify_resolution

parser=argparse.ArgumentParser(description=__doc__)
for name in ('uid','batch','source','base'):parser.add_argument('--'+name,required=True)
parser.add_argument('--prepare-only',action='store_true')
parser.add_argument('--retry-of',help='Explicit interrupted approval directory; fresh acceptance still required')
parser.add_argument('--owned',action='store_true',help=argparse.SUPPRESS)
args=parser.parse_args()
assert Path(args.batch).name==args.batch and args.batch.startswith('government-xl-')
UID=args.uid;BATCH=args.batch
SOURCE=(ROOT/args.source).resolve();BASE=(ROOT/args.base).resolve()
assert SOURCE.is_relative_to(ROOT) and BASE.is_relative_to(ROOT)
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/SOURCE.name
STAGE=HERE/'accepted'/BATCH
LEASE=HERE/'local'/BATCH/'install-reservation.json'
CHROME='/home/williamli/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'


def module(name,filename):
    spec=importlib.util.spec_from_file_location(name,HERE/filename)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def ref(path):return {'path':str(Path(path).relative_to(ROOT)),'sha256':digest(Path(path).read_bytes())}


def owns():assert reservations.owns(read(LEASE)),'Live source reservation required'


def call(args):
    subprocess.run(args,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':CHROME})
    owns()


def start():
    assert not DOC.exists(), 'Fresh acceptance batch required; completed evidence is immutable'
    scope={r['building']['uid'] for r in read(SOURCE/'neighbour-inputs.json.gz')['rows']}|{UID,read(SOURCE/'installed-support-proof.json')['supportUid']}
    claim=reservations.claim('codex-xl-explicit-install-'+str(uuid.uuid4()),
        [('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope)]+['terrain-patch:'+UID],batch=BATCH)
    assert claim['ok'],claim
    save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run',
        '--lease-file',str(LEASE),'--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)


def stage():
    owns()
    selection=read(SOURCE/'selection.json.gz');assert len(selection['rows'])==1
    row=selection['rows'][0];assert row['uid']==UID
    assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==selection['manifestSHA256']
    for path,pinned in read(SOURCE/'neighbour-inputs.json.gz')['inputHashes'].items():assert ref(ROOT/path)['sha256']==pinned
    source=read(BASE/'context.json.gz')
    context=next(r for r in source['rows'] if r['uid']==UID)
    assert context['sourceSHA256']==row['sourceSHA256']
    for path,pinned in context['neighbourTileHashes'].items():assert ref(ROOT/'3d-viewer'/path)['sha256']==pinned
    identity_record=read(SOURCE/'identity-proof.json')
    if identity_record.get('method') == 'original-government-full-georef-cell-identity-v1':
        from government_georef_cell_identity import verify_files, POLICY
        positive=verify_files(row,context,HERE/'local'/BATCH/'identity-publication-recheck')
        assert positive['policy']==POLICY and positive['passed'], positive['reasons']
        assert positive==read(SOURCE/'owned-source-identity.json')
        assert positive==read(SOURCE/'owned-source-identity-contact.json')
        assert identity_record['ownedSourceProofSHA256']==ref(SOURCE/'owned-source-identity.json')['sha256']
        assert identity_record['proof']==positive['proof']
        save(DOC/'positive-identity-publication-recheck.json',positive)
    else:
        assert not identity_record.get('method'), 'Unknown identity route'
        assert module('west_kowloon_identity','xl-remaining-direct.py').identity_clear(context['identity'])
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        actual=con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r '
            'JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',
            (NATIVE_RUN,row['native']['cacheKey'])).fetchone()
        assert actual and actual[0]==row['native']['resultSha']
        review=con.execute('SELECT snapshot_id,review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE uid=%s ORDER BY updated_at DESC LIMIT 1',(UID,)).fetchone()
        if args.retry_of:
            from interrupted_acceptance import verify_retry
            prior=(ROOT/args.retry_of).resolve();assert prior.is_relative_to(ROOT/'docs/astra-city/government-import')
            acceptance=ref(prior/'acceptance.json');decision=read(prior/'acceptance.json')
            assert decision['stagedBrowser']==ref(prior/'staged-browser.json'),'Interrupted browser evidence changed'
            oldlease=read(HERE/'local'/prior.name/'install-reservation.json')
            released=con.execute('SELECT released_at IS NOT NULL FROM astra_modelling.reservation_groups WHERE token=%s',(oldlease['token'],)).fetchone()
            pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
            current=con.execute('SELECT review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(pointer['snapshotId'],UID)).fetchone()
            assert review
            retry=verify_retry(dict(zip(('snapshot_id','review_state','source_sha256','result'),review)),uid=UID,source_sha=row['sourceSHA256'],
                prior_path=acceptance['path'],prior_sha=acceptance['sha256'],prior_decision=decision,
                browser_passed=read(prior/'staged-browser.json')['passed'],prior_installed=(prior/'installed-acceptance.json').exists() or (prior/'result.json').exists(),
                current_review=current,prior_released=bool(released and released[0]))
            retry.update(helper=ref(HERE/'interrupted_acceptance.py'),priorStagedBrowser=ref(prior/'staged-browser.json'),
                         priorReservationToken=oldlease['token'],priorReservationReleased=True)
            save(DOC/'retry-evidence.json',retry)
        else:assert review is None,'Review changed since current frozen inputs'
    result=read(SOURCE/'result.json');assert result['uid']==UID and result['scriptChecksPassed'] and not result['reasons']
    sync=read(SOURCE/'neon-sync.json');assert sync['resultVerified'] and sync['jobId']==result['jobId']
    for evidence in result['evidenceRefs']:assert ref(ROOT/evidence['path'])['sha256']==evidence['sha256']
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
    proof=read(SOURCE/'identity-proof.json');assert proof['uid']==UID and proof['sourceSHA256']==row['sourceSHA256']
    metrics=read(SOURCE/'metrics.json');metric=metrics['rows'][0]
    policy=module('west_kowloon_numeric','acceptance-policy.py')
    support_proof=verify_resolution(SOURCE,policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':row['sourceSHA256'],'identityProof':proof['proof']},metric,metrics['profiles']['mobile']))
    assert support_proof['uid']==UID and support_proof['sourceSHA256']==row['sourceSHA256']
    for path,pinned in metrics['inputHashes'].items():assert ref(ROOT/path)['sha256']==pinned
    validation=read(SOURCE/'validation.json')
    assert validation['checksPassed']==validation['loaderAccepted']==1 and validation['exceptions']==0
    if validation['results'][0].get('concerns'):
        proof_resolution=module('explicit_install_diagnostics','terrain_diagnostic_resolution.py').resolve_global_bottom_warning(
            validation['results'][0],metric,read(SOURCE/'foundation.json')['rows'][0])
        assert proof_resolution==read(SOURCE/'diagnostic-resolution.json')
        assert not read(SOURCE/'support-ground-resolution.json')['remainingDiagnosticReasons']
    foundation=read(SOURCE/'foundation.json')['rows'][0]
    assert foundation['strictFoundationAccepted'] and foundation['sourceSHA256']==row['sourceSHA256']
    resolved=set(read(SOURCE/'native-neighbour-checks.json')['resolved'])
    assert not any(r['reasons'] for r in read(SOURCE/'neighbour-checks.json')['rows'] if r['uid'] not in resolved)
    native=read(SOURCE/'native-neighbour-checks.json');assert not set(native.get('blocked',[]))-set(native.get('resolved',[]))
    catalogue=read(LOCAL/'catalogue.json');entry=dict(catalogue['models'][0])
    assert entry['uid']==UID and entry['sha256']==row['sourceSHA256']
    entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,
        identityReviewApproved=True,placementReviewed=True,publicationApproved=True,suppressesBuildingUids=[],
        placementReview='Exact original UID/ObjectID/CSUID/SHA, native HKPD transforms and bounded projection proof. Full source contact, foundation, basic/native neighbours and runtime gates pass against pinned current terrain. No AI modelling, geometry edits, height shifts or suppression.')
    if identity_record.get('method'):
        entry['placementReview']='Exact original government mesh ownership, unique UID/ObjectID/CSUID/SHA, native HKPD pose and whole GeoRef coordinate-cell proof. Fresh full-source coverage/extent/unrelated-form limits and whole official geographic coordinate cell pass; cached centroid/overlap proxies remain raw diagnostics. This explicit identity route replaces cached centroid/overlap and roof-area shape proxies with positive unique original-source identity; full terrain/contact/foundation/neighbour/runtime gates and staged/live browser verification remain required. No geometry edits, height shifts or suppression.'
    entry['supportDependencies']=[{'uid':support_proof['supportUid'],'state':'installed','csuid':support_proof['supportCSUID'],'sha256':support_proof['supportSHA256']}]
    entry['placementReview']='Exact unchanged original tower with complete strict original interface contacts on exact current installed government support; full compound foundation, source identity, terrain, neighbours and runtime checks. Original terrain-only gap diagnostics retained. No geometry edits or model AI.'
    asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/row['candidate']['path'],asset);assert ref(asset)['sha256']==entry['sha256']
    catalogue.update(area=entry['label']+' original government source',models=[entry],counts={'packedModels':1})
    save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']})
    save(STAGE/'source-forms.json',[row['source']['building']])
    candidate=read(SOURCE/'terrain-candidates.json')[0]
    assert ref(ROOT/candidate['path'])['sha256']==candidate['sha256']
    original=read(ROOT/candidate['path']);assert candidate.get('replaces') and original.get('nativeMesh') and not original.get('patches')
    assert original['meta']['parentTerrain']=='city/data/terrain.json' and original['meta']['parentSha256']==ref(ROOT/'3d-viewer/city/data/terrain.json')['sha256']
    patch=STAGE/Path(candidate['path']).name;shutil.copyfile(ROOT/candidate['path'],patch)
    terrain={'source':ref(patch)['path'],'sha256':ref(patch)['sha256'],
        'destination':'city/data/'+patch.name,'resolution':read(patch)['cell'],
        'area':entry['label']+' unchanged indexed government terrain'}
    assert identity_record.get('method') == 'original-government-full-georef-cell-identity-v1'
    replacement=candidate['replaces']
    assert ref(ROOT/'3d-viewer'/replacement['url'])['sha256']==replacement['sha256']
    assert replacement['url'] in {p['url'] for p in read(ROOT/'3d-viewer/city/data/manifest.json')['terrainPatches']}
    assert set(replacement['retainedUids']) <= set(original['meta']['targetUids'])
    assert set(replacement['retainedUids']) <= {r['uid'] for r in native['rows']}, 'Every retained native source must be fully checked'
    replacement_review={'status':'approved-for-integration','supersededURL':replacement['url'],
        'supersededSHA256':replacement['sha256'],'replacementSHA256':terrain['sha256'],
        'sourceGeometryChanged':False,'aiCalls':0,'modelGeometryChanges':0,
        'retainedUids':replacement['retainedUids'],'replacementTargetUids':original['meta']['targetUids'],
        'fullMeshCheck':ref(SOURCE/'native-neighbour-checks.json')}
    save(DOC/'native-replacement-review.json',replacement_review)
    terrain.update(replaces=replacement,nativeReview=ref(DOC/'native-replacement-review.json'))
    destination='city/data/official-models/'+BATCH+'/catalogue.json'
    save(STAGE/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':ref(STAGE/'catalogue.json')['path'],
        'destination':destination}],'topLevelTerrainPatches':[terrain]})
    retained=[]
    preservation=[]
    if (SOURCE/'parent-preservation.json').exists():preservation.append(SOURCE/'parent-preservation.json')
    if (SOURCE/'recheck-inputs.json').exists():
        for prior in read(SOURCE/'recheck-inputs.json')['previousEvidenceRefs']:
            if Path(prior['path']).name=='parent-preservation.json':
                assert ref(ROOT/prior['path'])['sha256']==prior['sha256'];preservation.append(ROOT/prior['path'])
    for prior in preservation:retained.extend(read(prior)['proof'].get('protectedUids',[]))
    native_uids={m['uid'] for url in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    retained=sorted(set(retained)-native_uids)
    bounds=[list(entry['worldBounds'][0]),list(entry['worldBounds'][1])]
    support=next(m for u in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/u)['models'] if m['uid']==support_proof['supportUid'])
    for axis in range(3):
        bounds[0][axis]=min(bounds[0][axis],support['worldBounds'][0][axis])
        bounds[1][axis]=max(bounds[1][axis],support['worldBounds'][1][axis])
    save(STAGE/'browser-config.json',{'viewBoundsByModel':{UID:bounds},'nativeSupportUidsByModel':{UID:sorted(set(replacement['retainedUids'])|{support_proof['supportUid']})},'stage':str(STAGE.relative_to(ROOT))+'/',
        'doc':str(DOC.relative_to(ROOT))+'/','catalogueURL':destination,'terrain':[terrain],
        'fitBox':True,'browserUids':[UID],'failureTestUids':[UID],
        'retainedBuildingUidsByModel':{UID:retained},'nativeSupportUidsByModel':{UID:[]}})
    dependencies=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json'])
    assert not any(r['blockers'] for r in dependencies['rows']);save(DOC/'dependencies.json',dependencies)
    save(DOC/'identity.json',context)
    evidence={name:ref(SOURCE/(name+'.json')) for name in
        ('metrics','validation','foundation','neighbour-checks',
         'native-neighbour-checks','identity-proof','result','neon-sync')}
    for i,prior in enumerate(preservation):evidence['parent-preservation-'+str(i)]=ref(prior)
    recovery_name='source-recovery' if (SOURCE/'source-recovery.json').exists() else 'recheck-inputs'
    evidence[recovery_name]=ref(SOURCE/(recovery_name+'.json'))
    if args.retry_of:evidence['retry-evidence']=ref(DOC/'retry-evidence.json')
    if (SOURCE/'diagnostic-resolution.json').exists():
        evidence['diagnostic-resolution']=ref(SOURCE/'diagnostic-resolution.json')
        evidence['diagnostic-resolver']=ref(HERE/'terrain_diagnostic_resolution.py')
    for name in ['installed-support-proof','support-ground-resolution','support-inputs']:
        evidence[name]=ref(SOURCE/(name+'.json'))
    evidence['support-checks']=ref(SOURCE/'support-checks.json.gz')
    evidence['support-policy']=ref(HERE/'installed_support_acceptance.py')
    evidence['native-replacement-review']=ref(DOC/'native-replacement-review.json')
    evidence['assembly-runtime-script']=ref(HERE/'resolution-assembly-browser.mjs')
    evidence['assembly-runtime-config']=ref(STAGE/'browser-config.json')
    evidence.update(identity=ref(DOC/'identity.json'),dependencies=ref(DOC/'dependencies.json'),
        selection=ref(SOURCE/'selection.json.gz'),policy=ref(HERE/'acceptance-policy.py'),
        catalogue=ref(STAGE/'catalogue.json'),plan=ref(STAGE/'plan.json'))
    if identity_record.get('method'):
        for name in ['owned-source-identity','owned-source-identity-contact','indexed-preflight']:
            evidence[name]=ref(SOURCE/(name+'.json'))
        evidence['positive-identity-publication-recheck']=ref(DOC/'positive-identity-publication-recheck.json')
        for name in ['government_georef_cell_identity.py','original_source_ownership.py','xl-second-pass.py']:
            evidence[name]=ref(HERE/name)
    save(DOC/'stage.json',{'batch':BATCH,'uids':[UID],'sourceSHA256':entry['sha256'],
        'terrain':ref(patch),'evidence':evidence,'checksPassed':True,'publication':False,
        'scriptExternalAICalls':0,'modelGeometryChanges':0})


def owned():
    stage();direct=module('west_kowloon_browser','integrate.py')
    # Catch publisher overlap/identity/dependency guards before browser work or ledger approval.
    call([sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),
        ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH])
    call(['node',str(HERE/'resolution-assembly-browser.mjs'),'staged',str((STAGE/'browser-config.json').relative_to(ROOT))])
    browser=direct.browser_verified(DOC/'staged-browser.json',{UID})
    if args.prepare_only:
        save(DOC/'prepared.json',{'uid':UID,'batch':BATCH,'stagedBrowser':ref(DOC/'staged-browser.json'),'publication':False,'newlyInstalled':0})
        print(json.dumps({'prepared':UID,'publication':False}),flush=True);return
    decision=read(DOC/'stage.json');assert decision['checksPassed']
    for evidence in decision['evidence'].values():assert ref(ROOT/evidence['path'])['sha256']==evidence['sha256']
    decision.update(stagedBrowser=ref(DOC/'staged-browser.json'),passed=True,failures=[])
    save(DOC/'acceptance.json',decision)
    sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
    pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
    pointer=read(pointer_path);inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']}
    model=read(STAGE/'catalogue.json')['models'][0];previous=parts.get(UID,{})
    parts[UID]={'uid':UID,'name':model['label'],'landmarkIds':previous.get('landmarkIds',[]),
        'objectId':model['objectId'],'csuid':model['buildingCSUID'],'candidate':{'sha256':model['sha256']},
        'sourceProgress':'prepared-for-review','classification':'script-verified-original-government-native-terrain','knownHold':False}
    ordered=sorted(parts.values(),key=lambda p:p['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16]
    inventory_path=pointer_path.parent/f'source-review-inventory-{snapshot}.json'
    save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,
        'qualification':'Untouched original source passes exact identity, native terrain, complete foundation, clear neighbour checks and staged/live runtime gates. No architectural AI.'})
    ledger.seed(inventory_path,inherit=pointer['snapshotId'])
    effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203',
        'run_id':snapshot,'output_ref':ref(DOC/'acceptance.json')['path']}
    observation='Unchanged original '+model['label']+' installed at native coordinates with exact government TIN. Full contact, foundation, source identity, neighbour checks, desktop/mobile day/night, picking, collision and download fallback/retry pass.'
    approval_observation='Unchanged original '+model['label']+' passes source identity, contact, foundation, neighbour and staged desktop/mobile day/night runtime, picking, collision and fallback/retry checks. Guarded publication and live verification remain pending.'
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    ledger.record_many(snapshot,LEASE,[(UID,'approved-for-integration',DOC/'acceptance.json',approval_observation,commit)],
        effort=effort,request_id=BATCH+'-approved-'+snapshot)
    publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),
        ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH]
    call(publication);manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes()
    (LEASE.parent/'manifest-before-installation.json').write_bytes(before);call(publication+['--apply'])
    try:
        call(['node',str(HERE/'resolution-assembly-browser.mjs'),'live',str((STAGE/'browser-config.json').relative_to(ROOT))])
        direct.browser_verified(DOC/'live-browser.json',{UID})
    except BaseException:
        manifest.write_bytes(before)
        raise
    installed={**decision,'snapshotId':snapshot,'publication':True,'liveBrowser':ref(DOC/'live-browser.json'),
        'manifest':ref(manifest)};save(DOC/'installed-acceptance.json',installed)
    ledger.record_many(snapshot,LEASE,[(UID,'installed-verified',DOC/'installed-acceptance.json',observation,commit)],
        effort=effort,request_id=BATCH+'-installed-'+snapshot)
    assert read(pointer_path)==pointer
    save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inventory_path)['path'],
        'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
    call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh'])
    call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
    receipt=read(LEASE);payload={'acceptance':ref(DOC/'acceptance.json'),'snapshot':snapshot}
    jobid=jobs.enqueue(BATCH,'original-government-terrain-install-v1',payload)
    job=jobs.claim(BATCH,receipt['owner'],['original-government-terrain-install-v1'],lease_seconds=1800)
    assert job and job['id']==jobid
    result={**installed,'installedUids':[UID],'evidenceRefs':[ref(DOC/n) for n in
        ('acceptance.json','installed-acceptance.json','staged-browser.json','live-browser.json')],
        'jobId':jobid,'newlyInstalled':1,'activeWorkers':0,'queuedFollowups':0,
        'progress':read(ROOT/'3d-viewer/city/data/building-progress.json')}
    with connect() as con:
        con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
        assert reservations._current(con,receipt)
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
            (Jsonb(result),jobid,job['owner'],job['token'])).rowcount==1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()[0]==result
        assert con.execute('SELECT review_state FROM astra_modelling.model_reviews WHERE uid=%s AND snapshot_id=%s',(UID,snapshot)).fetchone()[0]=='installed-verified'
    save(DOC/'result.json',result)
    save(DOC/'neon-sync.json',{'jobId':jobid,'resultVerified':True,'snapshotId':snapshot,'installedUids':[UID]})
    print(json.dumps({'installed':UID,'snapshotId':snapshot,'jobId':jobid,'neonVerified':True}),flush=True)


if __name__=='__main__':
    if args.owned:
        from publication_lock import locked_publication
        with locked_publication(ROOT):owned()
    else:start()
