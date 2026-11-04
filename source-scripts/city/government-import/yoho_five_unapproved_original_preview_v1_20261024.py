"""Private exact Yoho site preview; no identity, physical or publication approval."""
import copy,os,subprocess,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_supported_catalogue_scope_v1_20261024 import verify as verify_graph
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-next-repairs-yoho-five-unapproved-preview-v1-20261024'
RUNTIME='government-xl-next-repairs-yoho-five-inset-runtime-v1-20261024';PATCH='government-xl-next-repairs-yoho-local-inset-current-validation-v1-20261024'
SOURCES={'landsd/61738:0': '40cf48f2e506dc4aba5b8a28816b99078ae7f7d1b91252c9bae75c03a3ab0928', 'landsd/231756:0': 'd716e1d0d761cbd1268798db53d5367b630c837a72fa94ec64fddfaabcf30167', 'landsd/122702:0': '0c2d1237e415884793e62fe74685a07ae936d877d535bf89ff5eb0273ff7398b', 'landsd/56771:0': 'f96ce65998446a8de280c071a9e367bfbe58bbc17969857c4fa7dd4acae19a45', 'landsd/60281:0': '5af938ed04770f6b4826c796d88d9e259e82e0f1a9152cbfe0e6063790478542'}
PARENT='landsd/231756:0';SUPPORTS={u:PARENT for u in ['landsd/122702:0','landsd/60281:0','landsd/56771:0']};RETAINED=['landsd/58849:0','landsd/121143:0','landsd/146396:0']

def main():
    doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(RUNTIME,BASE/RUNTIME/'selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
    patch=take(PATCH,BASE/PATCH/'summary.json');assert patch['status']=='private-terrain-validator-passed'and patch['actualCurrentParentIdentical']and patch['targetSetUnchanged']and patch['uids']==[PARENT]
    candidate=ROOT/patch['candidate']['path'];terrain=take(PATCH,candidate);assert terrain['meta']['targetUids']==[PARENT]
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==patch['currentManifestSHA256'];refs.append(manifest)
    current=[]
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;refs.append(path);current+=read(path)['models']
    assert len(current)==6876 and not set(SOURCES)&{m['uid']for m in current}
    assert set(RETAINED)<={m['uid']for m in current}
    for uid in SUPPORTS:
        name='government-xl-next-repairs-yoho-'+uid.split('/')[1].split(':')[0]+'-original-podium-paths-v1-20261024';proof=take(name,BASE/name/'summary.json');assert proof['allUnresolvedHaveFinitePaths']and proof['uids']==[uid,PARENT]
    resources=['building:'+uid for uid in sorted(set(SOURCES)|set(RETAINED))];claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation']
    try:
        entries=[];forms={}
        for row in selection['rows']:
            uid=row['uid'];source=row['source'];tile=ROOT/'3d-viewer'/source['tile'];assert digest(tile.read_bytes())==source['tileSHA256']and next(b for b in read(tile)['buildings']if b['uid']==uid)==source['building'];refs.append(tile)
            asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[uid];refs.append(asset);entry=copy.deepcopy(row['candidate']['entry']);assert entry['rootTranslation']==[-834500,0,816500]and entry.get('verticalPlacementOffsetHKPD',0)==0 and not entry.get('supportDependencies')and not entry.get('suppressesBuildingUids')and not entry.get('retainedBasicSupportDependencies')
            entry.update(asset='assets/'+SOURCES[uid]+'.glb.gz',priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False)
            if uid in SUPPORTS:entry['supportDependencies']=[dict(uid=PARENT,state='installed',buildingCSUID='2187833636P20050609',sha256=SOURCES[PARENT])]
            target=local/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(asset.read_bytes());entries.append(entry);forms[uid]=source
        assert verify_graph(entries,SOURCES,SUPPORTS)
        save(local/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=entries,counts=dict(packedModels=5)));save(local/'catalogue-index.json',dict(models=5,catalogues=['catalogue.json']));save(local/'source-forms.json',[r['building']for r in forms.values()]);save(local/'validation-forms.json',forms)
        tool=HERE/'ronsdale_three_live_browser_v9_20261024.mjs';refs.extend([tool,HERE/'original_supported_catalogue_scope_v1_20261024.py'])
        configuration=dict(stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[dict(source=str(candidate.relative_to(ROOT)),destination='city/data/'+BATCH+'-terrain.json',sha256=patch['candidate']['sha256'],resolution=5,area='Private unapproved original-TIN ramp inset')],browserUids=[PARENT,*[u for u in SOURCES if u!=PARENT]],fitBox=True,captureDirectionByModel={u:([.1,4,.1]if u==PARENT else[-.5,.9,1])for u in SOURCES},retainedBuildingUids=[],additionalRetainedUids=RETAINED,jointUids=list(SOURCES),nativeSupportUidsByModel={u:[PARENT]for u in SUPPORTS})
        path=local/'preflight-config.json';save(path,dict(**configuration,doc=str(doc.relative_to(ROOT))+'/'));subprocess.run(['node',str(tool),'preflight',str(path.relative_to(ROOT))],cwd=ROOT,check=True)
        for width in [1280,390]:
            assert reservations.owns(lease)and reservations.heartbeat(lease)['ok'];path=local/('browser-config-'+str(width)+'.json');save(path,dict(**configuration,viewportWidths=[width],failureTestUids=list(SOURCES)if width==390 else[],doc=str((doc/str(width)).relative_to(ROOT))+'/'));doc.mkdir(parents=True,exist_ok=True)
            with(doc/('browser-'+str(width)+'.log')).open('w')as log:code=subprocess.run(['node',str(tool),'staged',str(path.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1500,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'}).returncode
            save(doc/('command-'+str(width)+'.json'),dict(exitCode=code));assert code==0 and read(doc/str(width)/'staged-browser.json')['passed']
        assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.extend(p for p in local.rglob('*')if p.is_file())
        result=dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,previewOnly=True,physicalAcceptance=False,identityAccepted=False,visualAcceptance=False,installationApproved=False,sourceGeometryChanges=0,qualification='Unapproved original-source runtime preview, exact private-inset activation and retained-native/failure checks only. All source approvals false; no production writes or publication plan. Source roles, every current neighbour and actual exported images require separate review.')
        module('yoho_preview_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unapproved-five-original-shared-site-private-browser-preview',list(dict.fromkeys(refs)),result)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']

if __name__=='__main__':main()
