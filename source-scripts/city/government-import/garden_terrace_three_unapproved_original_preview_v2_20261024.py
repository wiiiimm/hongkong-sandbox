"""Private exact Garden Terrace site preview; no identity, physical or publication approval."""
import copy,os,subprocess,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_supported_catalogue_scope_v1_20261024 import verify as verify_graph
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-next-repairs-garden-terrace2-three-unapproved-preview-v2-20261024'
RUNTIME='government-xl-next-repairs-garden-terrace2-three-current-runtime-v1-20261024'
SOURCES={'landsd/109491:0': 'd6f60c07b429bd89b7c45b09f3a3077960ecbd96898c833684a564d1a4fb9f2e', 'landsd/162285:0': '331e11c7d4e5834397430c9b10d10e753f550e080f398c75d8b390741ebc1cbd', 'landsd/21894:0': 'ea3b2a1531c7cce1f1d3915bc3014bc5eab2f0cef807fe3f581bf9f1320f4e5f'}
PARENT='landsd/162285:0';SUPPORTS={u:PARENT for u in ['landsd/109491:0','landsd/21894:0']};RETAINED=['landsd/304714:0']

def main():
    doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(RUNTIME,BASE/RUNTIME/'selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    current=[]
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;refs.append(path);current+=read(path)['models']
    assert len(current)==6881 and not set(SOURCES)&{m['uid']for m in current}
    assert set(RETAINED)<={m['uid']for m in current}
    for uid in SUPPORTS:
        name='government-xl-next-repairs-garden-terrace2-'+uid.split('/')[1].split(':')[0]+'-original-podium-paths-v1-20261024';proof=take(name,BASE/name/'summary.json');assert proof['allUnresolvedHaveFinitePaths']and proof['uids']==[uid,PARENT]
    resources=['building:'+uid for uid in sorted(set(SOURCES)|set(RETAINED))];claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation']
    try:
        entries=[];forms={}
        for row in selection['rows']:
            uid=row['uid'];source=row['source'];tile=ROOT/'3d-viewer'/source['tile'];assert digest(tile.read_bytes())==source['tileSHA256']and next(b for b in read(tile)['buildings']if b['uid']==uid)==source['building'];refs.append(tile)
            asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[uid];refs.append(asset);entry=copy.deepcopy(row['candidate']['entry']);assert entry['rootTranslation']==[-834500,0,816500]and entry.get('verticalPlacementOffsetHKPD',0)==0 and not entry.get('supportDependencies')and not entry.get('suppressesBuildingUids')and not entry.get('retainedBasicSupportDependencies')
            entry.update(asset='assets/'+SOURCES[uid]+'.glb.gz',priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False)
            if uid in SUPPORTS:entry['supportDependencies']=[dict(uid=PARENT,state='installed',buildingCSUID='3395615206P20060312',sha256=SOURCES[PARENT])]
            target=local/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(asset.read_bytes());entries.append(entry);forms[uid]=source
        assert verify_graph(entries,SOURCES,SUPPORTS)
        save(local/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=entries,counts=dict(packedModels=3)));save(local/'catalogue-index.json',dict(models=3,catalogues=['catalogue.json']));save(local/'source-forms.json',[r['building']for r in forms.values()]);save(local/'validation-forms.json',forms)
        tool=HERE/'ronsdale_three_live_browser_v9_20261024.mjs';refs.extend([tool,HERE/'original_supported_catalogue_scope_v1_20261024.py'])
        configuration=dict(stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[],browserUids=[PARENT,*[u for u in SOURCES if u!=PARENT]],fitBox=True,captureDirectionByModel={u:([1,3,1]if u==PARENT else[0,1.8,-1]if u=='landsd/109491:0'else[-.5,.9,1])for u in SOURCES},retainedBuildingUids=[],additionalRetainedUids=RETAINED,jointUids=list(SOURCES),nativeSupportUidsByModel={u:[PARENT]for u in SUPPORTS})
        path=local/'preflight-config.json';save(path,dict(**configuration,doc=str(doc.relative_to(ROOT))+'/'));subprocess.run(['node',str(tool),'preflight',str(path.relative_to(ROOT))],cwd=ROOT,check=True)
        for width in [1280,390]:
            assert reservations.owns(lease)and reservations.heartbeat(lease)['ok'];path=local/('browser-config-'+str(width)+'.json');save(path,dict(**configuration,viewportWidths=[width],failureTestUids=list(SOURCES)if width==390 else[],doc=str((doc/str(width)).relative_to(ROOT))+'/'));doc.mkdir(parents=True,exist_ok=True)
            with(doc/('browser-'+str(width)+'.log')).open('w')as log:code=subprocess.run(['node',str(tool),'staged',str(path.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1500,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'}).returncode
            save(doc/('command-'+str(width)+'.json'),dict(exitCode=code));assert code==0 and read(doc/str(width)/'staged-browser.json')['passed']
        assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.extend(p for p in local.rglob('*')if p.is_file())
        result=dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,previewOnly=True,physicalAcceptance=False,identityAccepted=False,visualAcceptance=False,installationApproved=False,sourceGeometryChanges=0,qualification='Unapproved original-source runtime preview, unchanged terrain and retained-native/failure checks only. All source approvals false; no production writes or publication plan. Source roles, every current neighbour and actual exported images require separate review.')
        module('yoho_preview_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unapproved-three-original-shared-site-private-browser-preview',list(dict.fromkeys(refs)),result)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']

if __name__=='__main__':main()
