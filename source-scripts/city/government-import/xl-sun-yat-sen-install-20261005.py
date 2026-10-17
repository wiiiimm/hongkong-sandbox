"""Install the unchanged Sun Yat Sen Memorial Park Sports source after all actual continuation gates."""
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

UID='landsd/239367:0'
BATCH='government-xl-sun-yat-sen-20261005-v2'
SOURCE=ROOT/'docs/astra-city/government-import/government-xl-sun-yat-sen-contact-20261005'
DOC=SOURCE/'installation-v2'
LOCAL=HERE/'local/government-xl-sun-yat-sen-contact-20261005'
STAGE=HERE/'accepted'/BATCH
LEASE=LOCAL/'install-reservation.json'
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
    scope={r['building']['uid'] for r in read(SOURCE/'neighbour-inputs.json.gz')['rows']}|{UID}
    parent=read(ROOT/'3d-viewer/city/data/terrain-central-with-hullett.json')
    scope.update(u for c in parent.get('patches',[]) for u in c['meta'].get('targetUids',[]))
    claim=reservations.claim('codex-xl-sun-install-'+str(uuid.uuid4()),
        [('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope)]+['terrain-patch:'+UID,'terrain-surface:city/data/terrain-central-with-hullett.json'],batch=BATCH)
    assert claim['ok'],claim
    save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run',
        '--lease-file',str(LEASE),'--',sys.executable,__file__,'owned'],cwd=ROOT,check=True)


def stage():
    owns()
    selection=read(SOURCE/'selection.json.gz');assert len(selection['rows'])==1
    row=selection['rows'][0];assert row['uid']==UID
    assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==selection['manifestSHA256']
    for path,pinned in read(SOURCE/'neighbour-inputs.json.gz')['inputHashes'].items():assert ref(ROOT/path)['sha256']==pinned
    source=read(ROOT/'docs/astra-city/government-import/government-xl-next-100-20261005/context.json.gz')
    context=next(r for r in source['rows'] if r['uid']==UID)
    assert context['sourceSHA256']==row['sourceSHA256']
    for path,pinned in context['neighbourTileHashes'].items():assert ref(ROOT/'3d-viewer'/path)['sha256']==pinned
    assert module('sun_identity','xl-remaining-direct.py').identity_clear(context['identity'])
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        actual=con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r '
            'JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',
            (NATIVE_RUN,row['native']['cacheKey'])).fetchone()
        assert actual and actual[0]==row['native']['resultSha']
        review=con.execute('SELECT snapshot_id,review_state,source_sha256 FROM astra_modelling.model_reviews WHERE uid=%s ORDER BY updated_at DESC LIMIT 1',(UID,)).fetchone()
        assert review==('e4ce769b8bde5057','approved-for-integration',row['sourceSHA256']), 'Unexpected source/review change since the preserved first publication attempt'
        for evidence in read(SOURCE/'first-publication-attempt/receipt.json')['evidence']:
            assert ref(ROOT/evidence['retainedPath'])['sha256']==evidence['original']['sha256']
    metrics=read(SOURCE/'metrics.json');metric=metrics['rows'][0]
    policy=module('sun_numeric','acceptance-policy.py')
    assert not policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':row['sourceSHA256']},metric,metrics['profiles']['mobile'])
    for path,pinned in metrics['inputHashes'].items():assert ref(ROOT/path)['sha256']==pinned
    validation=read(SOURCE/'validation.json')
    assert validation['checksPassed']==validation['loaderAccepted']==1 and validation['exceptions']==0
    assert not validation['results'][0].get('concerns',[])
    foundation=read(SOURCE/'foundation.json')['rows'][0]
    assert foundation['strictFoundationAccepted'] and foundation['sourceSHA256']==row['sourceSHA256']
    assert not any(r['reasons'] for r in read(SOURCE/'neighbour-checks.json')['rows'])
    native=read(SOURCE/'native-neighbour-checks.json');assert not set(native.get('blocked',[]))-set(native.get('resolved',[]))
    catalogue=read(LOCAL/'catalogue.json');entry=dict(catalogue['models'][0])
    assert entry['uid']==UID and entry['sha256']==row['sourceSHA256']
    entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,
        identityReviewApproved=True,placementReviewed=True,publicationApproved=True,suppressesBuildingUids=[],
        placementReview='Exact original source UID/CSUID/SHA and native HKPD transforms. Full source TIN contact and foundation pass; six existing Central terrain children retained unchanged. Neighbour and runtime gates pass. No AI modelling or geometry edits.')
    asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/row['candidate']['path'],asset);assert ref(asset)['sha256']==entry['sha256']
    catalogue.update(area='Sun Yat Sen Memorial Park Sports Centre original government source',models=[entry],counts={'packedModels':1})
    save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']})
    save(STAGE/'source-forms.json',[row['source']['building']])
    candidate=read(SOURCE/'terrain-candidates.json')[0]
    assert ref(ROOT/candidate['path'])['sha256']==candidate['sha256']
    parent=read(ROOT/'3d-viewer'/candidate['replaces']['url'])
    assert ref(ROOT/'3d-viewer'/candidate['replaces']['url'])['sha256']==candidate['replaces']['sha256']
    wrapper=read(ROOT/candidate['path'])
    module('sun_terrain_validator','xl-second-pass.py').resolution.validate_patch(wrapper,read(ROOT/'3d-viewer/city/data/terrain.json'))
    assert wrapper['elev']==parent['elev'] and wrapper.get('renderedElev')==parent.get('renderedElev')
    assert len(wrapper['patches'])==len(parent['patches'])+1
    for original,retained in zip(parent['patches'],wrapper['patches']):
        assert original['id']==retained['id'] and original['meta']['georef']==retained['meta']['georef']
        assert original.get('elev')==retained.get('elev') and original.get('renderedElev')==retained.get('renderedElev')
        for key in ('position','index'):assert original.get('nativeMesh',{}).get(key)==retained.get('nativeMesh',{}).get(key)
    patch=STAGE/Path(candidate['path']).name;shutil.copyfile(ROOT/candidate['path'],patch)
    terrain={'source':ref(patch)['path'],'sha256':ref(patch)['sha256'],
        'destination':'city/data/'+patch.name,'resolution':read(patch)['cell'],
        'area':'Sun Yat Sen Memorial Park Sports Centre original government terrain with unchanged Central grid and six retained nested patches',
        'replaces':candidate['replaces']}
    destination='city/data/official-models/'+BATCH+'/catalogue.json'
    save(STAGE/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':ref(STAGE/'catalogue.json')['path'],
        'destination':destination}],'topLevelTerrainPatches':[terrain]})
    save(STAGE/'browser-config.json',{'stage':str(STAGE.relative_to(ROOT))+'/',
        'doc':str(DOC.relative_to(ROOT))+'/','catalogueURL':destination,'terrain':[terrain],
        'fitBox':True,'browserUids':[UID],'failureTestUids':[UID],
        'retainedBuildingUidsByModel':{UID:['landsd/260992:0','landsd/321198:0']}})
    dependencies=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json'])
    assert not any(r['blockers'] for r in dependencies['rows']);save(DOC/'dependencies.json',dependencies)
    save(DOC/'identity.json',context)
    evidence={name:ref(SOURCE/(name+'.json')) for name in
        ('metrics','validation','foundation','neighbour-checks',
         'native-neighbour-checks','retained-parent-proof')}
    evidence.update(identity=ref(DOC/'identity.json'),dependencies=ref(DOC/'dependencies.json'),
        selection=ref(SOURCE/'selection.json.gz'),policy=ref(HERE/'acceptance-policy.py'),
        catalogue=ref(STAGE/'catalogue.json'),plan=ref(STAGE/'plan.json'))
    save(DOC/'stage.json',{'batch':BATCH,'uids':[UID],'sourceSHA256':entry['sha256'],
        'terrain':ref(patch),'evidence':evidence,'checksPassed':True,'publication':False,
        'scriptExternalAICalls':0,'modelGeometryChanges':0})


def owned():
    stage();direct=module('sun_browser','integrate.py')
    call(['node',str(HERE/'resolution-browser.mjs'),'staged',str((STAGE/'browser-config.json').relative_to(ROOT))])
    browser=direct.browser_verified(DOC/'staged-browser.json',{UID})
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
        'qualification':'Sun Yat Sen Memorial Park Sports Centre untouched original source passes native terrain, complete foundation, unchanged Central child terrain and staged/live runtime gates. No architectural AI.'})
    ledger.seed(inventory_path,inherit=pointer['snapshotId'])
    effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203',
        'run_id':snapshot,'output_ref':ref(DOC/'acceptance.json')['path']}
    observation='Unchanged original Sun Yat Sen Memorial Park Sports Centre installed at native coordinates with exact government TIN. Full contact, foundation, source identity, neighbour preservation, desktop/mobile day/night, picking, collision and download fallback/retry pass.'
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    ledger.record_many(snapshot,LEASE,[(UID,'approved-for-integration',DOC/'acceptance.json',observation,commit)],
        effort=effort,request_id=BATCH+'-approved-'+snapshot)
    publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),
        ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH]
    call(publication);manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes()
    (LOCAL/'manifest-before-installation.json').write_bytes(before);call(publication+['--apply'])
    try:
        call(['node',str(HERE/'resolution-browser.mjs'),'live',str((STAGE/'browser-config.json').relative_to(ROOT))])
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
        'jobId':jobid,'widerXLCheckpoint':{'models':352,'installed':41,'held':311},
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
    save(DOC/'neon-sync.json',{'jobId':jobid,'resultVerified':True,'snapshotId':snapshot,'installedUids':[UID]})
    print(json.dumps({'installed':UID,'snapshotId':snapshot,'jobId':jobid,'neonVerified':True}),flush=True)


if __name__=='__main__':owned() if 'owned' in sys.argv else start()
