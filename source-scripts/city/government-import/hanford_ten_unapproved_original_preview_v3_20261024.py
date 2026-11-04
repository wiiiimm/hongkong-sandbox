"""Unapproved ten-original Hanford preview; no production catalogue or terrain writes."""
import copy,os,subprocess,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from hanford_ten_original_catalogue_scope_v1_20261024 import SOURCES,SUPPORTS,PRIMARY,SECONDARY,verify_metadata
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-next-repairs-hanford-ten-original-'
BATCH=P+'unapproved-preview-v3-20261024';RUNTIME=P+'two-podium-runtime-v1-20261024';PATCH=P+'two-podium-terrain-v1-20261024'


def main():
    doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists();refs=[Path(__file__),HERE/'hanford_ten_original_catalogue_scope_v1_20261024.py'];pins={}
    def take(batch,path):
        if batch not in pins:
            _,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(RUNTIME,BASE/RUNTIME/'selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
    terrain_result=take(PATCH,BASE/PATCH/'summary.json');assert terrain_result['status']=='private-terrain-validator-passed'and terrain_result['allSubFloorRegionsNonregressing']
    candidate=ROOT/terrain_result['candidate']['path'];terrain=take(PATCH,candidate);assert terrain['meta']['targetUids']==sorted([PRIMARY,SECONDARY])
    low=take(PATCH,BASE/PATCH/'low-base-preservation.json');assert low['sameCompleteFloat32Multiset']and low['allSubFloorRegionsNonregressing']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==terrain_result['currentManifestSHA256'];refs.append(manifest)
    current=[]
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;refs.append(path);current+=read(path)['models']
    assert len(current)==6884 and not set(SOURCES)&{m['uid']for m in current}
    old=P+'current-attributes-v1-20261024';new=P+'two-podium-attributes-v1-20261024'
    before={r['uid']:r for r in take(old,BASE/old/'attributes.json.gz')['rows']};after={r['uid']:r for r in take(new,BASE/new/'attributes.json.gz')['rows']}
    for uid,sha in SOURCES.items():
        assert before[uid]['sourceSHA256']==after[uid]['sourceSHA256']==sha
        for field in ['completeOriginalIndex','completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:assert np.array_equal(before[uid][field],after[uid][field])
    follow=P+'support-followthrough-v1-20261024';support=take(follow,BASE/follow/'summary.json')
    for uid,parent in SUPPORTS.items():
        row=next(r for r in support['rows']if r['uid']==uid and r['supportUid']==parent)
        name=row['pathsBatch'];proof=take(name,BASE/name/'summary.json');assert proof['allUnresolvedHaveFinitePaths']and proof['uids']==[uid,parent]
    sources={r['uid']:r['source']for r in selection['rows']}
    # Two older prepared entries omitted required sourceTile metadata. Bind it
    # to their exact pinned native input/result, without editing source bytes.
    source_tiles={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for row in selection['rows']:
            uid=row['uid'];native=row['native']
            values=db.execute('SELECT i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s',(native['cacheKey'],)).fetchall()
            assert len(values)==1 and values[0][1]==native['resultSha']
            sheet=values[0][0];assert isinstance(sheet,str)and sheet
            if 'sourceTile'in row['candidate']['entry']:assert row['candidate']['entry']['sourceTile']==sheet
            source_tiles[uid]=dict(sourceTile=sheet,cacheKey=native['cacheKey'],resultSHA256=native['resultSha'],sourceSHA256=SOURCES[uid])
    save(doc/'source-tile-provenance.json',source_tiles);refs.append(doc/'source-tile-provenance.json')
    resources=['building:'+uid for uid in sorted(SOURCES)]+['terrain:city/data/terrain.json']
    claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation']
    try:
        entries=[];directions={}
        centers={r['uid']:np.mean(np.asarray(r['candidate']['entry']['worldBounds']),axis=0)for r in selection['rows']}
        center=np.mean([c for u,c in centers.items()if u in SUPPORTS],axis=0)
        for row in selection['rows']:
            uid=row['uid'];source=row['source'];tile=ROOT/'3d-viewer'/source['tile'];assert digest(tile.read_bytes())==source['tileSHA256']and next(b for b in read(tile)['buildings']if b['uid']==uid)==source['building'];refs.append(tile)
            asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[uid];refs.append(asset)
            entry=copy.deepcopy(row['candidate']['entry']);assert entry['rootTranslation']==[-834500,0,816500]and entry.get('verticalPlacementOffsetHKPD',0)==0 and not entry.get('supportDependencies')and not entry.get('retainedBasicSupportDependencies')and not entry.get('suppressesBuildingUids')
            entry.update(sourceTile=source_tiles[uid]['sourceTile'],asset='assets/'+SOURCES[uid]+'.glb.gz',priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False)
            if uid in SUPPORTS:
                parent=SUPPORTS[uid];entry['supportDependencies']=[dict(uid=parent,state='installed',buildingCSUID=sources[parent]['building']['buildingCSUID'],sha256=SOURCES[parent])]
            target=local/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(asset.read_bytes());entries.append(entry)
            v=centers[uid]-center;length=np.linalg.norm(v[[0,2]]);assert length>0
            directions[uid]=[float(v[0]/length),1.6,float(v[2]/length)]
        directions[PRIMARY]=[.5,3,1];directions[SECONDARY]=[1,1.6,-.5];directions['landsd/195682:0']=[-.4,.8,1]
        assert verify_metadata(entries)
        save(local/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=entries,counts=dict(packedModels=10)))
        save(local/'catalogue-index.json',dict(models=10,catalogues=['catalogue.json']));save(local/'source-forms.json',[r['building']for r in sources.values()]);save(local/'validation-forms.json',sources)
        tool=HERE/'ronsdale_three_live_browser_v9_20261024.mjs';refs.append(tool)
        configuration=dict(stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[dict(source=str(candidate.relative_to(ROOT)),destination='city/data/'+BATCH+'-terrain.json',sha256=terrain_result['candidate']['sha256'],resolution=5,area='Private original Hanford two-podium terrain')],browserUids=[PRIMARY,SECONDARY,*[u for u in SOURCES if u not in [PRIMARY,SECONDARY]]],fitBox=True,captureDirectionByModel=directions,retainedBuildingUids=[],additionalRetainedUids=[],jointUids=list(SOURCES),nativeSupportUidsByModel={u:[p]for u,p in SUPPORTS.items()})
        # The authored-yaw tower needs a wider camera fit than its nominal
        # source bounds. Expand the camera box only; complete framing remains
        # mandatory and no source/world bounds or asset metadata is changed.
        yaw=next(m for m in entries if m['uid']=='landsd/194725:0')['worldBounds']
        configuration['captureBoundsByModel']={'landsd/194725:0':[[v-20 for v in yaw[0]],[v+20 for v in yaw[1]]]}
        path=local/'preflight-config.json';save(path,dict(**configuration,doc=str(doc.relative_to(ROOT))+'/'));subprocess.run(['node',str(tool),'preflight',str(path.relative_to(ROOT))],cwd=ROOT,check=True)
        for width in [1280,390]:
            assert reservations.owns(lease)and reservations.heartbeat(lease)['ok']
            path=local/('browser-config-'+str(width)+'.json');save(path,dict(**configuration,viewportWidths=[width],failureTestUids=list(SOURCES)if width==390 else[],doc=str((doc/str(width)).relative_to(ROOT))+'/'))
            doc.mkdir(parents=True,exist_ok=True)
            with(doc/('browser-'+str(width)+'.log')).open('w')as log:code=subprocess.run(['node',str(tool),'staged',str(path.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1800,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'}).returncode
            save(doc/('command-'+str(width)+'.json'),dict(exitCode=code));assert code==0 and read(doc/str(width)/'staged-browser.json')['passed']
        assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.extend(p for p in local.rglob('*')if p.is_file())
        result=dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,previewOnly=True,physicalAcceptance=False,identityAccepted=False,visualAcceptance=False,installationApproved=False,sourceGeometryChanges=0,sourcePoseChanges=0,sourceCoordinateStreamsIdenticalToOriginalSupportProofs=True,qualification='Exact original runtime preview only. All ten source approval flags remain false, no production writes/publication. Current physical/source-role/identity/neighbour review and all actual exports remain separate requirements.')
        module('hanford_unapproved_preview_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unapproved-ten-original-hanford-assembly-private-browser-preview',list(dict.fromkeys(refs)),result)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']


if __name__=='__main__':main()
