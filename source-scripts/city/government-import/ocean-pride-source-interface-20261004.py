"""Stage Ocean Pride's untouched source after exact installed-podium interface checks."""
import importlib.util
import os
import shutil
import subprocess
import sys
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest
spec=importlib.util.spec_from_file_location('resolution',HERE/'sol-hold-resolution-20261004.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
c=r.c;UID='landsd/273839:0';SUPPORT='landsd/175935:0'
BATCH='government-xl-ocean-pride-interface-20261004'
DOC=c.DOC/'ocean-pride';STAGE=HERE/'accepted'/BATCH


def call(args):
    subprocess.run(args,cwd=ROOT,check=True,env={**os.environ,
        'CHROME_PATH':'/home/williamli/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'})


def stage():
    c.owns()
    contacts=read(c.DOC/'contact-faces.json.gz')
    proof=next(row for row in contacts['rows'] if row['uid']==UID)
    assert proof['interfaceProof']['passed'] and proof['supportUid']==SUPPORT
    for path,sha in contacts['inputHashes'].items():
        assert digest((ROOT/path).read_bytes())==sha, 'Contact input changed: '+path
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
    installed={e['uid']:e for url in manifest['officialModelCatalogues'] for e in read(ROOT/'3d-viewer'/url)['models']}
    assert UID not in installed and installed[SUPPORT]['sha256']==proof['supportSHA256']
    frozen=next(row for row in read(c.BASE/'sol-pilot-20261002/packet.json')['rows'] if row['uid']==UID)
    identity=frozen['identity']
    assert identity['exactObjectAndCSUID'] and identity['unrelatedIntersectingForms']==0
    assert identity['targetCoveredBySourceProjection']>=.95 and identity['sourceExcessFraction']<=.05
    row=next(row for row in read(r.PREVIOUS/'ocean-pride/selection.json.gz')['rows'] if row['uid']==UID)
    entry=dict(row['candidate']['entry']);assert entry['sha256']==proof['sourceSHA256']==frozen['sourceSHA256']
    asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(row['candidate']['path'],asset);assert digest(asset.read_bytes())==entry['sha256']
    entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,identityReviewApproved=True,
        placementReviewed=True,publicationApproved=True,suppressesBuildingUids=[],
        supportDependencies=[{'uid':SUPPORT,'state':'installed','csuid':installed[SUPPORT]['buildingCSUID']}],
        placementReview='Unchanged exact source, full current terrain foundation and native podium contact. Two vertical wall edges intersect the exact installed podium within the ordinary 0.5m source-clearance allowance; no geometry edits.')
    catalogue=read(HERE/'accepted/government-xxl-20260911/catalogue.json')
    catalogue.update(area='Ocean Pride Tower 2 original government source',models=[entry],counts={'packedModels':1})
    save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']})
    save(STAGE/'source-forms.json',[row['source']['building']]);save(DOC/'source-forms.json',{UID:row['source']})
    save(DOC/'selection.json.gz',{'rows':[row],'manifestSHA256':digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())})
    destination='city/data/official-models/'+BATCH+'/catalogue.json'
    save(STAGE/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':c.ref(STAGE/'catalogue.json')['path'],'destination':destination}]})
    save(STAGE/'browser-config.json',{'stage':str(STAGE.relative_to(ROOT))+'/',
        'doc':str(DOC.relative_to(ROOT))+'/','catalogueURL':destination,'terrain':[],
        'fitBox':True,'browserUids':[UID],'failureTestUids':[UID],
        'nativeSupportUidsByModel':{UID:[SUPPORT]}})
    call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),
        '--candidates',str(STAGE.relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),
        '--geometry-out',str((c.LOCAL/'ocean-runtime-geometry.json.gz').relative_to(ROOT))])
    call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',str(STAGE.relative_to(ROOT)),
        '--source-forms',str((DOC/'source-forms.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))])
    metric=read(DOC/'metrics.json');m=metric['rows'][0]
    policy=c.module('ocean_ordinary_policy','acceptance-policy.py')
    failures=set(policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':entry['sha256']},m,metric['profiles']['mobile']))
    assert failures=={'ground-contact-unresolved'},failures
    v=read(DOC/'validation.json')['results'][0]
    assert v['outcome']!='validation-exception' and set(v.get('concerns',[]))<= {'sampled-ground-gap-below-model-bottom'}
    runtime=read(c.LOCAL/'ocean-runtime-geometry.json.gz')['rows'][0]
    model=np.asarray(runtime['position']).reshape(-1,3)[np.asarray(runtime['index']).reshape(-1,3)]
    terrain=np.asarray(runtime['drawnGroundGeometry']).reshape(-1,3,3)
    final=c.module('ocean_full_foundation','xl-final-script-pass.py')
    b=row['source']['building'];foundation=final.foundation_context(model,terrain,Polygon(b['rings'][0],b['rings'][1:]))
    assert foundation['completeTerrainTriangles']==foundation['triangles'] and not foundation['fullyBuriedUpwardTriangles'] and foundation['fullyBuriedAreaFraction']==0
    save(DOC/'foundation.json',{'uid':UID,'sourceSHA256':entry['sha256'],'strictFoundationAccepted':True,'foundation':foundation,'modelGeometryChanges':0})
    save(DOC/'identity.json',{'uid':UID,'sourceSHA256':entry['sha256'],'identity':identity})
    save(DOC/'support-interface.json',proof)
    save(DOC/'stage.json',{'batch':BATCH,'uids':[UID],'sourceSHA256':entry['sha256'],
        'catalogue':c.ref(STAGE/'catalogue.json'),'plan':c.ref(STAGE/'plan.json'),
        'supportSHA256':proof['supportSHA256'],'sourceChecksPassed':True,'publication':False,
        'scriptExternalAICalls':0,'modelGeometryChanges':0})
    print({'staged':UID,'foundationTriangles':foundation['triangles'],'supportInterfaces':proof['interfaceProof']['samples']},flush=True)


def accept():
    c.owns()
    direct=c.module('ocean_browser_gates','integrate.py')
    browser=direct.browser_verified(DOC/'staged-browser.json',{UID})
    assert all(v['nativeSupports'][SUPPORT]['active'] and v['nativeSupports'][SUPPORT]['visible']
               for v in browser['views'] if 'time' in v)
    stage=read(DOC/'stage.json')
    assert stage['sourceChecksPassed'] and stage['uids']==[UID]
    for key in ('catalogue','plan'):
        assert digest((ROOT/stage[key]['path']).read_bytes())==stage[key]['sha256']
    proof=read(DOC/'support-interface.json');assert proof['interfaceProof']['passed']
    assert read(DOC/'foundation.json')['strictFoundationAccepted']
    evidence={name:c.ref(DOC/(name+'.json')) for name in
              ('stage','metrics','validation','foundation','identity','support-interface','staged-browser')}
    evidence['interfacePolicy']=c.ref(HERE/'support-interface.mjs')
    evidence['ordinaryPolicy']=c.ref(HERE/'acceptance-policy.py')
    save(DOC/'acceptance.json',{'batch':BATCH,'uids':[UID],'passed':True,'failures':[],
        'sourceSHA256':stage['sourceSHA256'],'supportSHA256':stage['supportSHA256'],
        'evidence':evidence,'scriptExternalAICalls':0,'modelGeometryChanges':0,
        'foundation':read(DOC/'foundation.json')['foundation'],'publication':False})
    print({'accepted':UID,'browserViews':4},flush=True)


def install():
    c.owns()
    sys.path.insert(0,str(HERE.parent/'model-review-ledger'))
    import ledger
    direct=c.module('ocean_install_browser','integrate.py')
    acceptance=read(DOC/'acceptance.json');assert acceptance['passed'] and not acceptance['failures']
    for evidence in acceptance['evidence'].values():
        assert digest((ROOT/evidence['path']).read_bytes())==evidence['sha256']
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes())==read(c.DOC/'checkpoint.json')['viewerManifest']['sha256']
    installed={e['uid']:e for url in read(manifest)['officialModelCatalogues'] for e in read(ROOT/'3d-viewer'/url)['models']}
    assert UID not in installed and installed[SUPPORT]['sha256']==acceptance['supportSHA256']
    model=read(STAGE/'catalogue.json')['models'][0]
    assert model['sha256']==acceptance['sourceSHA256']==digest((STAGE/model['asset']).read_bytes())
    assert model['supportDependencies']==[{'uid':SUPPORT,'state':'installed','csuid':installed[SUPPORT]['buildingCSUID']}]
    pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
    pointer=read(pointer_path);inventory=read(ROOT/pointer['inventory'])
    parts={p['uid']:p for p in inventory['parts']};old=parts.get(UID,{})
    parts[UID]={'uid':UID,'name':model['label'],'landmarkIds':old.get('landmarkIds',[]),
        'objectId':model['objectId'],'csuid':model['buildingCSUID'],
        'candidate':{'sha256':model['sha256']},'sourceProgress':'prepared-for-review',
        'classification':'script-verified-original-government-native-interface','knownHold':False}
    ordered=sorted(parts.values(),key=lambda p:p['uid'])
    snapshot=digest(c.jobs.encode([ordered,acceptance]).encode())[:16]
    inventory_path=pointer_path.parent/f'source-review-inventory-{snapshot}.json'
    save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],
        'parts':ordered,'qualification':'Ocean Pride Tower 2 unchanged source passes exact identity, full terrain foundation, original vertical wall/podium interface and browser gates. No architecture generation.'})
    ledger.seed(inventory_path,inherit=pointer['snapshotId'])
    effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203',
            'job_id':read(c.LOCAL/'job.json')['id'],'output_ref':str((DOC/'acceptance.json').relative_to(ROOT))}
    observation='Original Ocean Pride Tower 2 installed on exact existing native podium 175935. Two original vertical wall edges intersect the podium; native coordinates and geometry unchanged. Full foundation, runtime, desktop/mobile day/night, picking, collision, fallback/retry and support visibility pass.'
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    ledger.record_many(snapshot,c.LEASE,[(UID,'approved-for-integration',DOC/'acceptance.json',observation,commit)],
                       effort=effort,request_id=BATCH+'-approved-'+snapshot)
    publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),
                 str((STAGE/'plan.json').relative_to(ROOT)),'--receipt',str(c.LEASE),'--phase',BATCH]
    call(publication)
    before=manifest.read_bytes();save(c.LOCAL/'manifest-before.json',read(manifest))
    call(publication+['--apply'])
    try:
        call(['node',str(HERE/'resolution-browser.mjs'),'live',str((STAGE/'browser-config.json').relative_to(ROOT))])
        browser=direct.browser_verified(DOC/'live-browser.json',{UID})
        assert all(v['nativeSupports'][SUPPORT]['active'] and v['nativeSupports'][SUPPORT]['visible']
                   for v in browser['views'] if 'time' in v)
    except BaseException:
        manifest.write_bytes(before)
        raise
    save(DOC/'installed-acceptance.json',{**acceptance,'snapshotId':snapshot,'publication':True,
        'liveBrowser':c.ref(DOC/'live-browser.json'),'manifest':c.ref(manifest)})
    ledger.record_many(snapshot,c.LEASE,[(UID,'installed-verified',DOC/'installed-acceptance.json',observation,commit)],
                       effort=effort,request_id=BATCH+'-installed-'+snapshot)
    assert read(pointer_path)==pointer
    save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':str(inventory_path.relative_to(ROOT)),
        'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
    call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh'])
    call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
    with c.connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,UID)).fetchone()[0]=='installed-verified'
    save(DOC/'installed-summary.json',{'uid':UID,'snapshotId':snapshot,'neonVerified':True,
        'progress':read(ROOT/'3d-viewer/city/data/building-progress.json'),
        'scriptExternalAICalls':0,'modelGeometryChanges':0})
    print({'installed':UID,'snapshotId':snapshot},flush=True)


if __name__=='__main__':
    if sys.argv[1] in ('stage','accept','install'):
        {'stage':stage,'accept':accept,'install':install}[sys.argv[1]]()
    else:
        call(['node',str(HERE/'resolution-browser.mjs'),sys.argv[1],str((STAGE/'browser-config.json').relative_to(ROOT))])
