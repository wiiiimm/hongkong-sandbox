"""Unapproved explicitly configured original-plus-terrain preview; no production catalogue or terrain writes."""
import copy,os,subprocess,uuid,argparse,json,sys,math
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_supported_catalogue_scope_v1_20261024 import verify as verify_graph
BASE=ROOT/'docs/astra-city/government-import'
CONFIGPATH=(ROOT/os.environ['ORIGINAL_PREVIEW_CONFIG']).resolve()
assert CONFIGPATH.is_relative_to(BASE)
CONFIG=read(CONFIGPATH)
SOURCES=CONFIG['sources']; SUPPORTS=CONFIG['supportByUid']; BASICS=CONFIG['retainedBasicUids']
PRIMARY=CONFIG['primary']; BATCH=CONFIG['batch']; RUNTIME=CONFIG['runtime']; PATCH=CONFIG.get('patch')
assert PRIMARY in SOURCES and 0<len(SOURCES)<=40
assert BATCH.startswith('government-xl-') and '/' not in BATCH


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--owned',action='store_true');args=parser.parse_args()
    doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not(doc/'result.json').exists() and (args.owned or(not doc.exists()and not local.exists()));refs=[Path(__file__),CONFIGPATH,HERE/'original_supported_catalogue_scope_v1_20261024.py'];pins={}
    def take(batch,path):
        if batch not in pins:
            _,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(RUNTIME,BASE/RUNTIME/'selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
    assert PATCH and CONFIG.get('newTerrainMembers') is True
    terrain_result=take(PATCH,BASE/PATCH/'summary.json')
    assert terrain_result['status']=='private-three-member-chain-surface-validator-passed'
    assert terrain_result['newTerrainMembers'] is True and terrain_result['replacedNativeTerrain']==[]
    assert terrain_result['allEffectiveMembersRequired'] is True and len(terrain_result['members'])==3
    assert set(terrain_result['uids'])==set(CONFIG['terrainTargetUids'])==set(SOURCES)
    terrains=[]
    for member in terrain_result['members']:
        assert member['surfaceValidated'] is True and member['newTerrainMember'] is True and 'replaces' not in member
        candidate=ROOT/member['candidate']['path'];terrain=take(PATCH,candidate)
        assert terrain['meta']['targetUids']==CONFIG['terrainTargetUids']
        terrains.append((candidate,terrain,member['candidate']['sha256']))
    import three_member_native_boundary_v1_20261027 as chain
    validator=module('three_new_preview_validator',HERE/'validated_parent_roundoff_template_v2.py')
    rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=read(rootpath);refs.append(rootpath)
    with chain.private_validator():
        for _,terrain,_ in terrains:validator.validate_patch(terrain,root)
    chain.validate_effective_coordinated_members([t for _,t,_ in terrains])
    refs.extend([HERE/'three_member_native_boundary_v1_20261027.py',HERE/'validated_parent_roundoff_template_v2.py'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    current=[];current_locations={}
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;refs.append(path);current+=read(path)['models']
        for entry in read(path)['models']:assert entry['uid']not in current_locations;current_locations[entry['uid']]=(entry,path)
    assert len(current)==CONFIG['currentNativeActors'] and not set(SOURCES)&{m['uid']for m in current}
    retained=CONFIG.get('retainedNativeUids',[]);assert len(retained)==len(set(retained))and not set(retained)&set(SOURCES)
    retained_entries={};retained_assets={}
    if retained:
        inventory=take(CONFIG['nativeInventory'],BASE/CONFIG['nativeInventory']/'complete-bounds.json.gz')
        assert digest(manifest.read_bytes())==pins[CONFIG['nativeInventory']][str(manifest.relative_to(ROOT))]
        byuid={r['uid']:r for r in inventory['rows']};assert len(byuid)==CONFIG['currentNativeActors']
        for uid in retained:
            entry,path=current_locations[uid];asset=(path.parent/entry['asset']).resolve();assert asset.is_relative_to(ROOT)
            assert digest(asset.read_bytes())==entry['sha256']==byuid[uid]['sourceSHA256'];refs.extend([path,asset]);retained_entries[uid]=copy.deepcopy(entry);retained_assets[uid]=asset
        native_profiles=CONFIG['retainedCaptureDirectionsByViewport'];assert set(native_profiles)=={'390','1280'}
        for profile in native_profiles.values():
            assert set(profile)==set(retained)
            for xyz in profile.values():assert len(xyz)==3 and all(math.isfinite(v)for v in xyz)and sum(v*v for v in xyz)>0
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
    camera_profiles=CONFIG['captureDirectionsByViewport']
    assert set(camera_profiles)=={'390','1280'}
    assert all(set(v)==set(SOURCES) for v in camera_profiles.values())
    scope_name=CONFIG.get('terrainScope');model_scope=CONFIG['modelScope']
    obligations={f['uid']:f for f in take(scope_name,BASE/scope_name/'form-obligations.json.gz')} if scope_name else {}
    for uid in SOURCES:
        for item in take(model_scope,BASE/model_scope/(uid.split('/')[1]+'-forms.json.gz')):
            form=item['building'];u=form['uid']
            if u in obligations:assert obligations[u]==form
            obligations[u]=form
    assert set(SOURCES)|set(BASICS)|set(retained)<=set(obligations)
    if retained:
        terrain_scope=take(scope_name,BASE/scope_name/'scope.json');assert set(terrain_scope['touchingNativeUids'])==set(retained)
    resources=sorted({('building:'if u.startswith('landsd/')else'source-form:')+u for u in obligations}|{'terrain:city/data/terrain.json','server:127.0.0.1:4177'})
    leasepath=local/'reservation.json'
    if not args.owned:
        claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(leasepath,json.loads(json.dumps(lease,default=str)))
        try:subprocess.run([sys.executable,str(HERE/'bounded_reserved_runner_v2_20261022.py'),str(leasepath),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
        finally:
            if reservations.owns(lease):assert reservations.release(lease)['ok']
        return
    lease=read(leasepath);assert reservations.owns(lease)and set(resources)==set(lease['resources'])
    server=None;server_thread=None
    try:
        import functools,http.server,threading
        class Handler(http.server.SimpleHTTPRequestHandler):
            def log_message(self,*args):pass
            def copyfile(self,source,outputfile):
                try:super().copyfile(source,outputfile)
                except(BrokenPipeError,ConnectionResetError):pass
        server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')))
        server_thread=threading.Thread(target=server.serve_forever,daemon=True);server_thread.start()
        entries=[];directions={}
        for row in selection['rows']:
            uid=row['uid'];source=row['source'];tile=ROOT/'3d-viewer'/source['tile'];assert digest(tile.read_bytes())==source['tileSHA256']and next(b for b in read(tile)['buildings']if b['uid']==uid)==source['building'];refs.append(tile)
            asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[uid];refs.append(asset)
            entry=copy.deepcopy(row['candidate']['entry']);assert entry['rootTranslation']==[-834500,0,816500]and entry.get('verticalPlacementOffsetHKPD',0)==0 and not entry.get('supportDependencies')and not entry.get('retainedBasicSupportDependencies')and not entry.get('suppressesBuildingUids')
            entry.update(sourceTile=source_tiles[uid]['sourceTile'],asset='assets/'+SOURCES[uid]+'.glb.gz',priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False)
            if uid in SUPPORTS:
                parent=SUPPORTS[uid];entry['supportDependencies']=[dict(uid=parent,state='installed',buildingCSUID=sources[parent]['building']['buildingCSUID'],sha256=SOURCES[parent])]
            target=local/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(asset.read_bytes());entries.append(entry)
        directions=camera_profiles['390']
        assert verify_graph(entries,SOURCES,SUPPORTS)
        assert not(CONFIG.get('canopyExperimentReview')and CONFIG.get('canopyExperimentReviews'))
        if CONFIG.get('canopyExperimentReview'):
            review=take(CONFIG['canopyExperimentReview'],BASE/CONFIG['canopyExperimentReview']/'ROOT-PRIVATE-CANOPY-REVIEW.json')
            assert review['currentManifest']==dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes()))
            from private_canopy_preview_catalogue_v1_20261029 import apply
            entries=apply(entries,SOURCES,obligations,review);refs.append(HERE/'private_canopy_preview_catalogue_v1_20261029.py')
        elif CONFIG.get('canopyExperimentReviews'):
            reviews=[take(item['batch'],BASE/item['batch']/item['file'])for item in CONFIG['canopyExperimentReviews']]
            from private_multi_canopy_preview_catalogue_v1_20261029 import apply
            entries=apply(entries,SOURCES,obligations,reviews)
            assert all(r['currentManifest']==dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes()))for r in reviews)
            refs.extend([HERE/'private_multi_canopy_preview_catalogue_v1_20261029.py',HERE/'private_canopy_preview_catalogue_v1_20261029.py'])
        save(local/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=entries,counts=dict(packedModels=len(SOURCES))))
        save(local/'catalogue-index.json',dict(models=len(SOURCES),catalogues=['catalogue.json']));save(local/'source-forms.json',[r['building']for r in sources.values()]);save(local/'validation-forms.json',sources)
        tool=HERE/'ronsdale_three_live_browser_v19_20261028.mjs';refs.append(tool)
        configuration=dict(viewerURL=CONFIG.get('viewerURL','http://127.0.0.1:4176/city.html'),stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[dict(source=str(path.relative_to(ROOT)),destination='city/data/'+BATCH+'-terrain-'+str(i)+'.json',sha256=sha,resolution=5,area=CONFIG['label'])for i,(path,node,sha)in enumerate(terrains)],browserUids=[PRIMARY,*[u for u in SOURCES if u!=PRIMARY]],fitBox=True,captureDirectionByModel=directions,retainedBuildingUids=BASICS,additionalRetainedUids=retained,retainedNativeOwnViews=bool(retained),retainedCaptureDirectionByModel=CONFIG.get('retainedCaptureDirectionsByViewport',{}).get('390',{}),jointUids=list(SOURCES),nativeSupportUidsByModel={u:[p]for u,p in SUPPORTS.items()})
        path=local/'preflight-config.json';save(path,dict(**configuration,doc=str(doc.relative_to(ROOT))+'/'));subprocess.run(['node',str(tool),'preflight',str(path.relative_to(ROOT))],cwd=ROOT,check=True)
        for width in [1280,390]:
            configuration['captureDirectionByModel']=camera_profiles[str(width)]
            configuration['retainedCaptureDirectionByModel']=CONFIG.get('retainedCaptureDirectionsByViewport',{}).get(str(width),{})
            assert reservations.owns(lease)and reservations.heartbeat(lease)['ok']
            path=local/('browser-config-'+str(width)+'.json');save(path,dict(**configuration,viewportWidths=[width],failureTestUids=list(SOURCES)if width==390 else[],doc=str((doc/str(width)).relative_to(ROOT))+'/'))
            doc.mkdir(parents=True,exist_ok=True)
            with(doc/('browser-'+str(width)+'.log')).open('w')as log:code=subprocess.run(['node',str(tool),'staged',str(path.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1800,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'}).returncode
            save(doc/('command-'+str(width)+'.json'),dict(exitCode=code));assert code==0 and read(doc/str(width)/'staged-browser.json')['passed']
        assert digest(manifest.read_bytes())==selection['manifestSHA256']
        for uid in retained:
            entry,path=current_locations[uid];assert next(e for e in read(path)['models']if e['uid']==uid)==retained_entries[uid]and digest(retained_assets[uid].read_bytes())==entry['sha256']
        refs.extend(p for p in local.rglob('*')if p.is_file()and p.name!='reservation.json')
        result=dict(retainedNativeUids=retained,retainedNativeEntries=retained_entries,nativeMetadataChanges=0,uids=list(SOURCES),sourceSHA256ByUid=SOURCES,previewOnly=True,terrainEdits=bool(PATCH),physicalAcceptance=False,identityAccepted=False,visualAcceptance=False,installationApproved=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='Exact original runtime preview only. All four source approval flags remain false, no production writes/publication. Current physical/source-role/identity/neighbour review and all actual exports remain separate requirements.')
        module('selected_unapproved_terrain_preview_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unapproved-three-new-terrain-members-original-private-browser-preview',list(dict.fromkeys(refs)),result)
    finally:
        if server is not None:server.shutdown();server.server_close()
        if server_thread is not None:server_thread.join(timeout=5)
        assert reservations.owns(lease)


if __name__=='__main__':main()
