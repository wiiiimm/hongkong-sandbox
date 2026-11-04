"""Private single original with an exact retained-terrain replacement preview.

No source approvals, production writes, geometry edits or installation credit.
"""
import argparse,copy,os,subprocess,uuid,sys,functools,http.server,threading
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','scope','inventory','uid','patch','terrain-scope','resource-plan','replacement-binding','neighbours']:p.add_argument('--'+k,required=True)
    p.add_argument('--direction',type=float,nargs=3,default=[-1,1.8,-1]);p.add_argument('--owned',action='store_true');a=p.parse_args()
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch
    assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:
            _,pins[batch]=authenticate(base/batch);refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(a.runtime,base/a.runtime/'selection.json.gz');row=next(r for r in selection['rows']if r['uid']==a.uid)
    scope=take(a.scope,base/a.scope/'summary.json');scoped=next(r for r in scope['rows']if r['uid']==a.uid)
    inventory=take(a.inventory,base/a.inventory/'complete-bounds.json.gz');manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes())==selection['manifestSHA256']==scope['currentManifestSHA256']==pins[a.inventory][str(manifest.relative_to(ROOT))];refs.append(manifest)
    installed={}
    for url in read(manifest)['officialModelCatalogues']:
        cat=ROOT/'3d-viewer'/url;assert digest(cat.read_bytes())==pins[a.inventory][str(cat.relative_to(ROOT))];refs.append(cat)
        for e in read(cat)['models']:assert e['uid']not in installed;installed[e['uid']]=e
    assert len(installed)==len(inventory['rows'])==scoped['currentNativeActorsChecked']and a.uid not in installed
    terrain_scope=take(a.terrain_scope,base/a.terrain_scope/'scope.json')
    forms=take(a.terrain_scope,base/a.terrain_scope/'form-obligations.json.gz')
    replacement=take(a.replacement_binding,base/a.replacement_binding/'summary.json')
    checks=take(a.neighbours,base/a.neighbours/'summary.json')
    assert replacement['newSourceUids']==[a.uid]
    assert set(terrain_scope['uids'])==set(replacement['uids'])==set(checks['uids'])
    assert terrain_scope['positiveAreaTerrainOverlaps']==1
    assert checks['forms']==len(forms) and not checks['basicFlags']
    assert set(checks['requiredNativeUids'])==set(terrain_scope['touchingNativeUids'])
    assert set(checks['nativeResolved'])==set(checks['requiredNativeUids'])
    assert len(checks['nativeRows'])==len(checks['requiredNativeUids'])
    assert all(r['passed'] is True for r in checks['nativeRows'])
    assert terrain_scope['currentNativeActors']==len(installed)
    retained=sorted({r['uid']for r in scoped['nearbyNativeActors']}|set(terrain_scope['touchingNativeUids']))
    assert len(retained)==len(set(retained)) and set(retained)<=set(installed)
    patch_summary=take(a.patch,base/a.patch/'summary.json')
    assert patch_summary['status']=='private-terrain-validator-passed' and patch_summary['uids']==[a.uid]
    assert patch_summary['sourceSHA256ByUid']=={a.uid:row['sourceSHA256']}
    candidate=patch_summary['candidate'];patchpath=ROOT/candidate['path']
    assert digest(patchpath.read_bytes())==candidate['sha256'];refs.append(patchpath)
    assert replacement['candidate']['path']==candidate['path'] and replacement['candidate']['sha256']==candidate['sha256']
    replacements=replacement['replacedNativeTerrain'];assert len(replacements)==1
    old=replacements[0];oldpath=ROOT/old['path']
    assert oldpath==ROOT/'3d-viewer'/old['url'] and digest(oldpath.read_bytes())==old['sha256']
    refs.append(oldpath);oldterrain=read(oldpath);patch=read(patchpath)
    assert oldterrain['meta']['targetUids']==old['targetUids']
    assert patch['coarseCells']==oldterrain['coarseCells']==terrain_scope['regionalCoarseCells']
    assert set(patch['meta']['targetUids'])==set(old['targetUids'])|{a.uid}==set(terrain_scope['uids'])
    assert patch['meta']['parentTerrain']==oldterrain['meta']['parentTerrain'] and patch['meta']['parentSha256']==oldterrain['meta']['parentSha256']
    assert replacement['candidate']['replaces']==dict(url=old['url'],sha256=old['sha256'],retainedUids=old['targetUids'])
    positive=[r for r in terrain_scope['terrainContacts']if r['coarseOverlapAreaM2']>0 or any(c['overlapAreaM2']>0 for c in r['packedContacts'])]
    assert len(positive)==1 and positive[0]['url']==old['url']
    terrain=[dict(source=candidate['path'],destination='city/data/'+a.batch+'-terrain.json',sha256=candidate['sha256'],resolution=patch['cell'],area='Private exact retained-terrain replacement preview',replacesMany=replacements)]
    for form in forms:
        matches=[b for entry in read(manifest)['tiles'] if entry['id']==form['tile'] for b in read(ROOT/'3d-viewer'/entry['url'])['buildings'] if b['uid']==form['uid']]
        assert matches==[form]

    for r in scoped['nearbyNativeActors']:assert installed[r['uid']]['sha256']==r['sourceSHA256']
    tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256']and next(f for f in read(tile)['buildings']if f['uid']==a.uid)==row['source']['building'];refs.append(tile)
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
    entry=copy.deepcopy(row['candidate']['entry']);assert entry['sha256']==row['sourceSHA256']and entry['rootTranslation']==[-834500,0,816500]and entry.get('verticalPlacementOffsetHKPD',0)==0
    assert not any(entry.get(k)for k in ['supportDependencies','retainedBasicSupportDependencies','suppressesBuildingUids','sourceWorldBounds','partialSource','embeddedModel','embeddedModels'])
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');native=row['native'];records=db.execute('SELECT i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s',(native['cacheKey'],)).fetchall()
        assert len(records)==1 and records[0][1]==native['resultSha'];sheet=records[0][0]
    if 'sourceTile'in entry:assert entry['sourceTile']==sheet
    planpath=ROOT/a.resource_plan;assert planpath.is_relative_to(base);plan=read(planpath);refs.append(planpath)
    resources=sorted(set(plan['resources'])|{'server:127.0.0.1:4177','terrain:city/data/terrain.json'}|{'building:'+u for u in [a.uid,*retained]}|{('building:'if b['uid'].startswith('landsd/')else'source-form:')+b['uid']for b in forms})
    lp=local/'reservation.json'
    if not a.owned:
        assert not local.exists();claim=reservations.claim(a.batch+'-'+str(uuid.uuid4()),resources,batch=a.batch,ttl=3600);assert claim['ok']
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    manifest_before=manifest.read_bytes();server=None;thread=None
    try:
        entry.update(asset='assets/'+row['sourceSHA256']+'.glb.gz',sourceTile=sheet,priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False)
        target=local/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(asset.read_bytes())
        save(local/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=[entry],counts=dict(packedModels=1)))
        save(local/'source-tile-provenance.json',dict(uid=a.uid,sourceSHA256=row['sourceSHA256'],sourceTile=sheet,cacheKey=native['cacheKey'],nativeResultSHA256=native['resultSha']))
        save(local/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(local/'source-forms.json',[row['source']['building']]);save(local/'validation-forms.json',{a.uid:row['source']})
        configuration=dict(viewerURL='http://127.0.0.1:4177/city.html',diagnosticOnly=True,publication=False,stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+a.batch+'/catalogue.json',terrain=terrain,browserUids=[a.uid],fitBox=True,captureDirectionByModel={a.uid:a.direction},retainedCaptureDirectionByModel={u:[1,3,-1]for u in retained},retainedBuildingUids=[b['uid']for b in forms if b['uid']not in [a.uid,*retained]],additionalRetainedUids=retained,jointUids=[a.uid],nativeSupportUidsByModel={})
        tool=HERE/'ronsdale_three_live_browser_v15_20261026.mjs';refs.append(tool)
        closure=HERE/'private_viewer_runtime_closure_v1_20261028.mjs';refs.append(closure);out.mkdir(parents=True,exist_ok=True)
        closurepath=out/'runtime-input-closure.json';subprocess.run(['node',str(closure),'capture',str(closurepath.relative_to(ROOT))],cwd=ROOT,check=True)
        class Handler(http.server.SimpleHTTPRequestHandler):
            def log_message(self,*args):pass
            def copyfile(self,source,outputfile):
                try:super().copyfile(source,outputfile)
                except(BrokenPipeError,ConnectionResetError):pass
        server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        preflight=local/'preflight-config.json';save(preflight,dict(**configuration,doc=str(out.relative_to(ROOT))+'/'))
        subprocess.run(['node',str(tool),'preflight',str(preflight.relative_to(ROOT))],cwd=ROOT,check=True)
        for width in [1280,390]:
            assert reservations.owns(lease)and reservations.heartbeat(lease)['ok'];cfg=local/('browser-config-'+str(width)+'.json');save(cfg,dict(**configuration,viewportWidths=[width],failureTestUids=[a.uid]if width==390 else[],doc=str((out/str(width)).relative_to(ROOT))+'/'));out.mkdir(parents=True,exist_ok=True)
            with(out/('browser-'+str(width)+'.log')).open('w')as log:code=subprocess.run(['node',str(tool),'staged',str(cfg.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1800,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'}).returncode
            save(out/('command-'+str(width)+'.json'),dict(exitCode=code));assert code==0
            report=read(out/str(width)/'staged-browser.json');assert report['passed']and not report['errors']
            assert len([v for v in report['views']if'time'in v])==2
            old=report.get('retainedNativeOwnViews',[]);assert len(old)==2*len(retained)and{v['uid']for v in old}==set(retained)
        assert digest(manifest.read_bytes())==selection['manifestSHA256'];assert manifest.read_bytes()==manifest_before
        subprocess.run(['node',str(closure),'verify',str(closurepath.relative_to(ROOT))],cwd=ROOT,check=True);refs.append(closurepath)
        refs.extend(ROOT/p for p in read(closurepath)['inputHashes'])
        refs.extend(p for p in local.rglob('*')if p.is_file()and p.name!='reservation.json')
        result=dict(uids=[a.uid],sourceSHA256ByUid={a.uid:row['sourceSHA256']},retainedNativeUids=retained,currentNativeActors=len(installed),previewOnly=True,physicalAcceptance=False,identityAccepted=False,visualAcceptance=False,installationApproved=False,sourceGeometryChanges=0,sourcePoseChanges=0,privateTerrainSHA256=candidate['sha256'],exactReplacement=replacements,fullAffectedBaseForms=len(forms),leaseResources=resources,terrainEdits=False,qualification='Unapproved original with exact private terrain only; no public terrain/model writes. Complete affected base forms and scoped retained natives are loaded from their real catalogues and each requires own desktop/mobile day/night views. Source approval flags stay false; no source/support metadata or production writes. Actual ROOT visual, identity, physical and neighbour review remains separate.')
        module('single_unapproved_original_preview_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'unapproved-single-original-and-complete-scoped-retained-native-preview',list(dict.fromkeys(refs)),result)
    finally:
        if server is not None:server.shutdown();server.server_close()
        if thread is not None:thread.join(timeout=5)

if __name__=='__main__':main()
