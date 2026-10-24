"""Private independent-original preview with complete scoped retained-native views.

No source approvals, production writes, model geometry edits or installation credit; the explicit private terrain candidate is routed only in the test browser.
"""
import argparse,copy,os,subprocess,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','scope','inventory','uid','patch','terrain-scope']:p.add_argument('--'+k,required=True)
    p.add_argument('--retained-basic',action='append',default=[]);p.add_argument('--direction',type=float,nargs=3,default=[.5,1.8,-1]);a=p.parse_args()
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch
    assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists()and not local.exists()
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
    retained=sorted(r['uid']for r in scoped['nearbyNativeActors']);assert len(retained)==len(set(retained))
    for r in scoped['nearbyNativeActors']:assert installed[r['uid']]['sha256']==r['sourceSHA256']
    scoped_forms=take(a.scope,base/a.scope/(a.uid.split('/')[1]+'-forms.json.gz'))
    scoped_uids={r['building']['uid']for r in scoped_forms}
    basic=set(a.retained_basic)
    assert len(basic)==len(a.retained_basic)and basic<=scoped_uids and not basic&set(installed)and a.uid not in basic
    terrain_summary=take(a.patch,base/a.patch/'summary.json')
    assert terrain_summary['status']=='private-terrain-validator-passed'and terrain_summary['uids']==[a.uid]
    terrain_candidate=terrain_summary['candidate'];terrain_path=ROOT/terrain_candidate['path']
    assert digest(terrain_path.read_bytes())==terrain_candidate['sha256']
    terrain_node=take(a.patch,terrain_path)
    terrain_scope=take(a.terrain_scope,base/a.terrain_scope/'scope.json')
    assert terrain_scope['uids']==[a.uid]and terrain_scope['currentNativeActors']==len(installed)
    assert terrain_scope['positiveAreaTerrainOverlaps']==0 and not terrain_scope['touchingNativeUids']
    terrain_forms=take(a.terrain_scope,base/a.terrain_scope/'form-obligations.json.gz')
    terrain_uids={f['uid']for f in terrain_forms}
    assert len(terrain_forms)==len(terrain_uids)==terrain_scope['intersectingForms']
    terrain_config=[dict(source=str(terrain_path.relative_to(ROOT)),destination='city/data/'+a.batch+'-terrain.json',sha256=terrain_candidate['sha256'],resolution=5,area='Private exact original-TIN local grade candidate')]
    tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256']and next(f for f in read(tile)['buildings']if f['uid']==a.uid)==row['source']['building'];refs.append(tile)
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
    entry=copy.deepcopy(row['candidate']['entry']);assert entry['sha256']==row['sourceSHA256']and entry['rootTranslation']==[-834500,0,816500]and entry.get('verticalPlacementOffsetHKPD',0)==0
    assert not any(entry.get(k)for k in ['supportDependencies','retainedBasicSupportDependencies','suppressesBuildingUids','sourceWorldBounds','partialSource','embeddedModel','embeddedModels'])
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');native=row['native'];records=db.execute('SELECT i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s',(native['cacheKey'],)).fetchall()
        assert len(records)==1 and records[0][1]==native['resultSha'];sheet=records[0][0]
    if 'sourceTile'in entry:assert entry['sourceTile']==sheet
    resources=sorted({'building:'+u for u in [a.uid,*retained,*sorted(basic),*sorted(terrain_uids)]});claim=reservations.claim(a.batch+'-'+str(uuid.uuid4()),resources,batch=a.batch,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:
        entry.update(asset='assets/'+row['sourceSHA256']+'.glb.gz',sourceTile=sheet,priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False)
        target=local/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(asset.read_bytes())
        save(local/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=[entry],counts=dict(packedModels=1)))
        save(local/'source-tile-provenance.json',dict(uid=a.uid,sourceSHA256=row['sourceSHA256'],sourceTile=sheet,cacheKey=native['cacheKey'],nativeResultSHA256=native['resultSha']))
        save(local/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(local/'source-forms.json',[row['source']['building']]);save(local/'validation-forms.json',{a.uid:row['source']})
        configuration=dict(stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+a.batch+'/catalogue.json',terrain=terrain_config,browserUids=[a.uid],fitBox=True,captureDirectionByModel={a.uid:a.direction},retainedCaptureDirectionByModel={u:[1,3,-1]for u in retained},retainedBuildingUids=sorted(basic),additionalRetainedUids=retained,jointUids=[a.uid],nativeSupportUidsByModel={})
        tool=HERE/'ronsdale_three_live_browser_v9_20261024.mjs';refs.append(tool);preflight=local/'preflight-config.json';save(preflight,dict(**configuration,doc=str(out.relative_to(ROOT))+'/'))
        subprocess.run(['node',str(tool),'preflight',str(preflight.relative_to(ROOT))],cwd=ROOT,check=True)
        for width in [1280,390]:
            assert reservations.owns(lease)and reservations.heartbeat(lease)['ok'];cfg=local/('browser-config-'+str(width)+'.json');save(cfg,dict(**configuration,viewportWidths=[width],failureTestUids=[a.uid]if width==390 else[],doc=str((out/str(width)).relative_to(ROOT))+'/'));out.mkdir(parents=True,exist_ok=True)
            with(out/('browser-'+str(width)+'.log')).open('w')as log:code=subprocess.run(['node',str(tool),'staged',str(cfg.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1800,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'}).returncode
            save(out/('command-'+str(width)+'.json'),dict(exitCode=code));assert code==0
            report=read(out/str(width)/'staged-browser.json');assert report['passed']and not report['errors']
            assert len([v for v in report['views']if'time'in v])==2
            old=report.get('retainedNativeOwnViews',[]);assert len(old)==2*len(retained)and{v['uid']for v in old}==set(retained)
        assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.extend(p for p in local.rglob('*')if p.is_file())
        result=dict(uids=[a.uid],sourceSHA256ByUid={a.uid:row['sourceSHA256']},retainedNativeUids=retained,retainedBasicUids=sorted(basic),currentNativeActors=len(installed),previewOnly=True,physicalAcceptance=False,identityAccepted=False,visualAcceptance=False,installationApproved=False,sourceGeometryChanges=0,sourcePoseChanges=0,terrainEdits=True,productionTerrainEdits=False,terrainCandidate=terrain_candidate,qualification='Unapproved independent original only. Explicit current basic neighbours must remain loaded, basic and visible. Complete scoped retained natives are loaded from their real catalogues and each requires own desktop/mobile day/night views. Source approval flags stay false; no source/support metadata or production writes. Explicit authenticated private terrain is test-routed only. Actual ROOT visual, identity, physical and neighbour review remains separate.')
        module('single_unapproved_original_preview_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'unapproved-single-original-and-complete-scoped-retained-native-preview',list(dict.fromkeys(refs)),result)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']

if __name__=='__main__':main()
