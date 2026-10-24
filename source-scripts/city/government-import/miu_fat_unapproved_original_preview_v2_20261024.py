"""Private Miu Fat original assembly preview; never approve, install or publish.

Exact three source hashes, existing canonical support and gateway coverage bind
this diagnostic. All catalogue approval flags remain false. No publication plan.
"""
import copy,json,os,subprocess,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import policy
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-next-repairs-miu-fat-unapproved-original-preview-v2-20261024'
RUNTIME='government-xl-next-repairs-miu-fat-three-current-runtime-v1-20261024'
COVERAGE='government-xl-next-repairs-miu-fat-gateway-coverage-review-v1-20261024'
SUPPORT='government-xl-next-repairs-miu-fat-lin-wah-original-support-v1-20261024'
SOURCES={'landsd/165889:0':'5c2a3560515f4ad2f80e6f2d5b634988ae4d655a9268c137bd55c5952e00b862','landsd/233638:0':'0bd1fc65477e3b4f84805586f62cb2c0e8aca133532de79822eb413e88dcdf91','landsd/241215:0':'901fd6a0098ede2e783deeb9b308f9594fe31dc0ca44ef2c6e1790adb169ba7a'}
PRIMARY='landsd/165889:0';HALL='landsd/241215:0';GATE='landsd/197385:0';HOME='landsd/6393:0'

def main():
    doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(RUNTIME,BASE/RUNTIME/'selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
    coverage=take(COVERAGE,BASE/COVERAGE/'gateway-coverage-review.json');assert coverage['coverageApprovedForStagedValidation']and not coverage['installationApproved']and coverage['sourceSHA256']==SOURCES[PRIMARY]and coverage['secondaryUid']==GATE
    support=take(SUPPORT,BASE/SUPPORT/'summary.json');assert support['allFourModesPassed']and support['supportedUid']==HALL and support['supportUid']==PRIMARY
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==coverage['currentManifest']['sha256'];refs.append(manifest)
    current=[]
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;refs.append(path);current+=read(path)['models']
    assert len(current)==6873 and not(set(SOURCES)|{GATE})&{m['uid']for m in current}
    assert not any(GATE in {uid for uid,_ in policy.dependency_rows(m)}for m in current)
    resources=['building:'+uid for uid in sorted(set(SOURCES)|{GATE,HOME})];claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation']
    try:
        entries=[];forms={}
        for row in selection['rows']:
            uid=row['uid'];source=row['source'];tile=ROOT/'3d-viewer'/source['tile'];assert digest(tile.read_bytes())==source['tileSHA256']and next(b for b in read(tile)['buildings']if b['uid']==uid)==source['building'];refs.append(tile)
            asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[uid];refs.append(asset);entry=copy.deepcopy(row['candidate']['entry']);entry.update(asset='assets/'+SOURCES[uid]+'.glb.gz',priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False)
            assert not entry.get('supportDependencies')and not entry.get('suppressesBuildingUids')and not entry.get('retainedBasicSupportDependencies')
            if uid==PRIMARY:entry['suppressesBuildingUids']=[GATE]
            if uid==HALL:entry['supportDependencies']=[dict(uid=PRIMARY,state='installed',buildingCSUID='1641631155P20060508',sha256=SOURCES[PRIMARY])]
            target=local/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(asset.read_bytes());entries.append(entry);forms[uid]=source
        save(local/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=entries,counts=dict(packedModels=3)))
        save(local/'catalogue-index.json',dict(models=3,catalogues=['catalogue.json']));save(local/'source-forms.json',[r['building']for r in forms.values()]);save(local/'validation-forms.json',forms)
        tool=HERE/'ronsdale_three_live_browser_v9_20261024.mjs';refs.append(tool)
        config=dict(stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[],browserUids=list(SOURCES),fitBox=True,captureDirectionByModel={PRIMARY:[-.7,1,1],'landsd/233638:0':[.1,1.5,1],HALL:[.7,.8,1]},retainedBuildingUids=[],retainedBuildingUidsByModel={'landsd/233638:0':[HOME]},jointUids=list(SOURCES),nativeSupportUidsByModel={HALL:[PRIMARY]})
        pre=local/'preflight-config.json';save(pre,dict(**config,doc=str(doc.relative_to(ROOT))+'/'));subprocess.run(['node',str(tool),'preflight',str(pre.relative_to(ROOT))],cwd=ROOT,check=True)
        for width in [1280,390]:
            assert reservations.owns(lease);assert reservations.heartbeat(lease)['ok'];path=local/('browser-config-'+str(width)+'.json');save(path,dict(**config,viewportWidths=[width],failureTestUids=list(SOURCES)if width==390 else[],doc=str((doc/str(width)).relative_to(ROOT))+'/'));doc.mkdir(parents=True,exist_ok=True)
            with(doc/('browser-'+str(width)+'.log')).open('w')as log:code=subprocess.run(['node',str(tool),'staged',str(path.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1200,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'}).returncode
            save(doc/('command-'+str(width)+'.json'),dict(exitCode=code));assert code==0 and read(doc/str(width)/'staged-browser.json')['passed']
        assert digest(manifest.read_bytes())==selection['manifestSHA256']
        refs.extend(p for p in local.rglob('*')if p.is_file());result=dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,previewOnly=True,physicalAcceptance=False,identityAccepted=False,visualAcceptance=False,installationApproved=False,sourceGeometryChanges=0,qualification='Private unchanged-original preview and scripted runtime/fallback measurements only. All model approvals false; no publication plan and no production writes. Actual exported images still need inspection. Current source-role, retained-home interface and exact source acceptance are unresolved; no browser or diagnostic success automatically approves them.')
        module('miu_unapproved_preview_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unapproved-exact-original-assembly-private-browser-preview',list(dict.fromkeys(refs)),result)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']

if __name__=='__main__':main()
