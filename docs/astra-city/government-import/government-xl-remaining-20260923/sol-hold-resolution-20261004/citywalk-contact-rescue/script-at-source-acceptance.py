"""Install unchanged Citywalk using reviewed source TIN and retained native checks."""
import importlib.util
import os
import shutil
import subprocess
import sys
import uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations

spec=importlib.util.spec_from_file_location('resolution',HERE/'sol-hold-resolution-20261004.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);c=r.c
UID='landsd/134332:0';BATCH='government-xl-citywalk-source-20261004'
DOC=c.DOC/'citywalk-contact-rescue';STAGE=HERE/'accepted'/BATCH


def call(args):
    subprocess.run(args,cwd=ROOT,check=True,env={**os.environ,
        'CHROME_PATH':'/home/williamli/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'})


def gates():
    metrics=read(DOC/'metrics.json');m=metrics['rows'][0]
    identity=read(DOC/'identity-resolution.json')['rows'][0]
    assert identity['identityAccepted'] and identity['exactObjectAndCSUID']
    policy=c.module('citywalk_policy','acceptance-policy.py')
    reasons=policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':m['sourceSHA256'],
        'identityProof':{'exactObjectId':True,'exactBuildingCSUID':True,'uniqueViewerMatch':True,
                         'identityAccepted':identity['identityAccepted']}},m,metrics['profiles']['mobile'])
    assert not reasons,reasons
    validation=read(DOC/'validation.json')['results'][0]
    assert validation['outcome']!='validation-exception' and set(validation.get('concerns',[]))<={'sampled-terrain-above-model-bottom'},validation
    foundation=read(DOC/'foundation.json')['foundation']
    assert foundation['completeTerrainTriangles']==foundation['triangles'] and foundation['fullyBuriedAreaFraction']==0 and not foundation['fullyBuriedUpwardTriangles']
    neighbours=read(DOC/'neighbour-checks.json');native=read(DOC/'native-neighbour-checks.json')
    assert not (set(u for row in neighbours['patches'] for u in row['blockedBy'])-set(native['resolved'])-{UID})
    assert not (set(native['blocked'])-set(native['resolved']))
    assert {'landsd/305615:0','landsd/273839:0'}<=set(native['resolved'])


def stage():
    c.owns()
    terrain=read(DOC/'terrain-candidates.json')[0]
    assert digest((ROOT/terrain['path']).read_bytes())==terrain['sha256']
    row=read(DOC/'selection.json.gz')['rows'][0];entry=dict(row['candidate']['entry'])
    target=STAGE/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(row['candidate']['path'],target);assert digest(target.read_bytes())==entry['sha256']
    entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,identityReviewApproved=True,
        placementReviewed=True,publicationApproved=True,suppressesBuildingUids=[],
        placementReview='Exact original source with source-backed terrain clipping, complete foundation and retained Citywalk 2 / Ocean Pride full-mesh neighbour checks; no geometry edits.')
    catalogue=read(HERE/'accepted/government-xxl-20260911/catalogue.json')
    catalogue.update(area='Citywalk original government source',models=[entry],counts={'packedModels':1})
    save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']})
    save(STAGE/'source-forms.json',[row['source']['building']]);save(DOC/'source-forms.json',{UID:row['source']})
    patch=STAGE/'government-native-citywalk-source-20261004.json';shutil.copyfile(ROOT/terrain['path'],patch)
    replacement={ 'source':str(patch.relative_to(ROOT)),'sha256':digest(patch.read_bytes()),
        'destination':'city/data/'+patch.name,'resolution':read(patch)['cell'],
        'area':'Citywalk original terrain with retained Citywalk 2 and neighbour surfaces','replaces':terrain['replaces']}
    save(DOC/'native-replacement-review.json',{'status':'approved-for-integration',
        'supersededURL':terrain['replaces']['url'],'supersededSHA256':terrain['replaces']['sha256'],
        'replacementSHA256':replacement['sha256'],'sourceGeometryChanged':False,
        'retainedUids':terrain['replaces']['retainedUids'],'replacementTargetUids':read(patch)['meta']['targetUids'],
        'fullMeshCheck':c.ref(DOC/'native-neighbour-checks.json'),'aiCalls':0,'modelGeometryChanges':0})
    replacement['nativeReview']=c.ref(DOC/'native-replacement-review.json')
    destination='city/data/official-models/'+BATCH+'/catalogue.json'
    save(STAGE/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':str((STAGE/'catalogue.json').relative_to(ROOT)),
        'destination':destination}],'topLevelTerrainPatches':[replacement]})
    save(STAGE/'browser-config.json',{'stage':str(STAGE.relative_to(ROOT))+'/', 'doc':str(DOC.relative_to(ROOT))+'/',
        'catalogueURL':destination,'terrain':[replacement],'fitBox':True,'browserUids':[UID],'failureTestUids':[UID]})
    # Retained sources are checked under the replacement terrain using their
    # existing catalogues; they are neither republished nor made dependencies.
    for name,uid,batch in (('citywalk2','landsd/305615:0','government-xl-citywalk2-mask-20260929'),
                           ('ocean-pride','landsd/273839:0','government-xl-ocean-pride-interface-20261004')):
        config={'stage':str((HERE/'accepted'/batch).relative_to(ROOT))+'/',
            'doc':str((DOC/('retained-'+name)).relative_to(ROOT))+'/',
            'catalogueURL':'city/data/official-models/'+batch+'/catalogue.json',
            'terrain':[replacement],'fitBox':True,'browserUids':[uid],'failureTestUids':[uid]}
        if name=='ocean-pride':config['nativeSupportUidsByModel']={uid:['landsd/175935:0']}
        save(STAGE/('retained-'+name+'-browser-config.json'),config)
    call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),
        '--candidates',str(STAGE.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),
        '--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((c.LOCAL/'citywalk-runtime-geometry.json.gz').relative_to(ROOT))])
    call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',str(STAGE.relative_to(ROOT)),
        '--source-forms',str((DOC/'source-forms.json').relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),
        '--out',str((DOC/'validation.json').relative_to(ROOT))])
    runtime=read(c.LOCAL/'citywalk-runtime-geometry.json.gz')['rows'][0]
    model=np.asarray(runtime['position']).reshape(-1,3)[np.asarray(runtime['index']).reshape(-1,3)]
    final=c.module('citywalk_full_foundation','xl-final-script-pass.py');b=row['source']['building']
    foundation=final.foundation_context(model,np.asarray(runtime['drawnGroundGeometry']).reshape(-1,3,3),Polygon(b['rings'][0],b['rings'][1:]))
    save(DOC/'foundation.json',{'uid':UID,'foundation':foundation,'sourceSHA256':entry['sha256'],'modelGeometryChanges':0})
    gates()
    save(DOC/'runtime-resolution.json',{'uid':UID,'concerns':read(DOC/'validation.json')['results'][0].get('concerns',[]),
        'resolvedBy':[c.ref(DOC/'metrics.json'),c.ref(DOC/'foundation.json')],
        'policy':'Global terrain maximum above global model minimum is contextual: every actual source contact is checked against its local drawn terrain, with ordinary 0.5m maximum penetration and zero fully buried faces. No runtime exception or unrelated diagnostic is accepted.',
        'modelGeometryChanges':0,'scriptExternalAICalls':0})
    save(DOC/'stage.json',{'batch':BATCH,'uids':[UID],'sourceSHA256':entry['sha256'],
        'catalogue':c.ref(STAGE/'catalogue.json'),'plan':c.ref(STAGE/'plan.json'),
        'manifest':c.ref(ROOT/'3d-viewer/city/data/manifest.json'),'publication':False})
    print({'staged':UID,'foundationFaces':foundation['triangles']},flush=True)


def accept():
    c.owns();gates();direct=c.module('citywalk_browser_gates','integrate.py')
    stage=read(DOC/'stage.json')
    for key in ('catalogue','plan','manifest'):assert digest((ROOT/stage[key]['path']).read_bytes())==stage[key]['sha256']
    entry=read(STAGE/'catalogue.json')['models'][0]
    assert entry['sha256']==stage['sourceSHA256']==digest((STAGE/entry['asset']).read_bytes())
    patch=read(STAGE/'plan.json')['topLevelTerrainPatches'][0]
    assert digest((ROOT/patch['source']).read_bytes())==patch['sha256']
    direct.browser_verified(DOC/'staged-browser.json',{UID})
    for name,uid in (('citywalk2','landsd/305615:0'),('ocean-pride','landsd/273839:0')):
        direct.browser_verified(DOC/('retained-'+name)/'staged-browser.json',{uid})
    evidence={name:c.ref(DOC/(name+'.json')) for name in ('stage','metrics','validation','foundation','runtime-resolution','identity-resolution',
        'neighbour-checks','native-neighbour-checks','native-replacement-review','staged-browser')}
    for name in ('citywalk2','ocean-pride'):
        evidence['retained-'+name]=c.ref(DOC/('retained-'+name)/'staged-browser.json')
    for name in ('acceptance-policy.py','check-native-neighbours.mjs','rendered_patch_sampler.py',
                 'citywalk-source-install-20261004.py'):
        evidence[name]=c.ref(HERE/name)
    save(DOC/'acceptance.json',{'batch':BATCH,'uids':[UID],'passed':True,'failures':[],
        'sourceSHA256':read(DOC/'stage.json')['sourceSHA256'],'evidence':evidence,
        'scriptExternalAICalls':0,'modelGeometryChanges':0,'publication':False})


def install():
    c.owns();acceptance=read(DOC/'acceptance.json');assert acceptance['passed'] and not acceptance['failures']
    for evidence in acceptance['evidence'].values():assert digest((ROOT/evidence['path']).read_bytes())==evidence['sha256']
    stage=read(DOC/'stage.json')
    for name in ('catalogue','plan','manifest'):assert digest((ROOT/stage[name]['path']).read_bytes())==stage[name]['sha256']
    pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes()
    assert all(UID!=m['uid'] for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models'])
    claim=reservations.claim('codex-citywalk-terrain-'+str(uuid.uuid4()),['terrain-patch:'+UID],batch=BATCH);assert claim['ok'],claim
    terrain_receipt=c.LOCAL/'citywalk-terrain-reservation.json';save(terrain_receipt,c.json.loads(c.json.dumps(claim['reservation'],default=str)))
    try:
        sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
        inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']};model=read(STAGE/'catalogue.json')['models'][0]
        parts[UID]={'uid':UID,'name':model['label'],'landmarkIds':parts.get(UID,{}).get('landmarkIds',[]),
            'objectId':model['objectId'],'csuid':model['buildingCSUID'],'candidate':{'sha256':model['sha256']},
            'sourceProgress':'prepared-for-review','classification':'script-verified-original-government-native-terrain','knownHold':False}
        ordered=sorted(parts.values(),key=lambda p:p['uid']);snapshot=digest(c.jobs.encode([ordered,acceptance]).encode())[:16]
        inventory_path=pointer_path.parent/f'source-review-inventory-{snapshot}.json'
        save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,
            'qualification':'Citywalk unchanged source accepted with full foundation, source TIN, retained native models and staged/live browser gates.'})
        ledger.seed(inventory_path,inherit=pointer['snapshotId'])
        effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203',
            'job_id':read(c.LOCAL/'job.json')['id'],'output_ref':str((DOC/'acceptance.json').relative_to(ROOT))}
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        observation='Original Citywalk source installed unchanged; source-backed local terrain contact restored, exact installed neighbour facets preserved and duplicate coplanar terrain clipped. Full foundation, retained Citywalk 2 / Ocean Pride meshes, runtime and staged/live browser pass; no AI modelling.'
        ledger.record_many(snapshot,c.LEASE,[(UID,'approved-for-integration',DOC/'acceptance.json',observation,commit)],effort=effort,request_id=BATCH+'-approve-'+snapshot)
        publish=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),str((STAGE/'plan.json').relative_to(ROOT)),
            '--receipt',str(c.LEASE),'--receipt',str(terrain_receipt),'--phase',BATCH]
        call(publish);call(publish+['--apply'])
        try:
            call(['node',str(HERE/'resolution-browser.mjs'),'live',str((STAGE/'browser-config.json').relative_to(ROOT))])
            c.module('citywalk_live_gates','integrate.py').browser_verified(DOC/'live-browser.json',{UID})
            for name,uid in (('citywalk2','landsd/305615:0'),('ocean-pride','landsd/273839:0')):
                call(['node',str(HERE/'resolution-browser.mjs'),'live',str((STAGE/('retained-'+name+'-browser-config.json')).relative_to(ROOT))])
                c.module('citywalk_retained_live_gates','integrate.py').browser_verified(DOC/('retained-'+name)/'live-browser.json',{uid})
        except BaseException:
            manifest.write_bytes(before)
            raise
        save(DOC/'installed-acceptance.json',{**acceptance,'snapshotId':snapshot,'publication':True,
            'manifest':c.ref(manifest),'liveBrowser':c.ref(DOC/'live-browser.json'),
            'retainedLiveBrowsers':{name:c.ref(DOC/('retained-'+name)/'live-browser.json') for name in ('citywalk2','ocean-pride')}})
        ledger.record_many(snapshot,c.LEASE,[(UID,'installed-verified',DOC/'installed-acceptance.json',observation,commit)],effort=effort,request_id=BATCH+'-installed-'+snapshot)
        assert read(pointer_path)==pointer
        save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':str(inventory_path.relative_to(ROOT)),
            'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
        call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
        with c.connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,UID)).fetchone()[0]=='installed-verified'
        save(DOC/'installed-summary.json',{'uid':UID,'snapshotId':snapshot,'neonVerified':True,
            'progress':read(ROOT/'3d-viewer/city/data/building-progress.json'),'modelGeometryChanges':0,'scriptExternalAICalls':0})
        print({'installed':UID,'snapshot':snapshot},flush=True)
    finally:
        assert reservations.release(read(terrain_receipt))['ok']


if __name__=='__main__':
    if sys.argv[1] in ('stage','accept','install'):{'stage':stage,'accept':accept,'install':install}[sys.argv[1]]()
    elif sys.argv[1]=='retained':
        for name in ('citywalk2','ocean-pride'):
            c.owns();call(['node',str(HERE/'resolution-browser.mjs'),'staged',str((STAGE/('retained-'+name+'-browser-config.json')).relative_to(ROOT))])
    else:call(['node',str(HERE/'resolution-browser.mjs'),sys.argv[1],str((STAGE/'browser-config.json').relative_to(ROOT))])
