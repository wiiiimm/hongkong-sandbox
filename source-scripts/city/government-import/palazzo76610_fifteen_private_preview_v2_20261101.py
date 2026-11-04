"""Private15-original source/runtime diagnostics; no approval or publication.

Uses existing unchanged desktop/mobile and atomic browser adapters, plus the
current installed304700native through its existing native-own-view guards.
V1 incorrectly routed it through BOTH basic-visible and native-active guards;
V2 separates existing native/basic obligations without changing either guard.
No BASIC overlays, geometry or terrain edits.
"""
import argparse,copy,functools,http.server,os,shutil,subprocess,sys,threading,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-palazzo76610-after-prosperous-'
BATCH=P+'fifteen-private-preview-v2-20261101'
RUNTIME=P+'fifteen-authentic-tin-runtime-v1-20261101'
PATCH=P+'fourteen-authentic-tin-v1-20261101'
SCOPE=P+'fourteen-authentic-tin-scope-v1-20261101'
OWNER='landsd/76610:0'

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json'
    assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:
            pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(RUNTIME,'selection.json.gz');rows=selection['rows'];uids=sorted(r['uid']for r in rows)
    assert len(uids)==len(set(uids))==15 and OWNER in uids
    forms=take(SCOPE,'form-obligations.json.gz');scope=take(SCOPE,'scope.json')
    assert len(forms)==103 and scope['touchingNativeUids']==['landsd/304700:0'] and scope['positiveAreaTerrainOverlaps']==0
    resources=sorted({('building:'if b['uid'].startswith('landsd/')else'source-form:')+b['uid']for b in forms}|{'building:'+u for u in uids}|{'server:127.0.0.1:4177','terrain:city/data/terrain.json'})
    if not a.owned:
        assert not local.exists();claim=reservations.claim('prosperous-private-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    preflight=take(P+'fifteen-dependency-preflight-v1-20261101','summary.json')
    assert preflight['candidateCount']==15 and preflight['requiresAssemblyInvestigation']==0
    assert preflight['sourceSHA256ByUid']=={r['uid']:r['sourceSHA256']for r in rows}
    support_by_uid=preflight['proposedSupportByUid']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_before=manifest.read_bytes()
    assert digest(manifest_before)==selection['manifestSHA256'];refs.append(manifest)
    models=[];owner=next(r for r in rows if r['uid']==OWNER)
    for row in rows:
        tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256']
        assert next(b for b in read(tile)['buildings']if b['uid']==row['uid'])==row['source']['building'];refs.append(tile)
        entry=copy.deepcopy(row['candidate']['entry']);assert entry['sha256']==row['sourceSHA256']
        assert not entry.get('suppressesBuildingUids') and not entry.get('supportDependencies')
        entry.update(priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False)
        if row['uid']in support_by_uid:
            parent=next(r for r in rows if r['uid']==support_by_uid[row['uid']])
            entry['supportDependencies']=[dict(uid=parent['uid'],state='installed',buildingCSUID=parent['source']['building']['buildingCSUID'],sha256=parent['sourceSHA256'])]
        asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
        entry['asset']='assets/'+row['sourceSHA256']+'.glb.gz';target=local/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset,target);models.append(entry)
    save(local/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=models,counts=dict(packedModels=15)))
    save(local/'catalogue-index.json',dict(models=15,catalogues=['catalogue.json']))
    save(local/'source-forms.json',[r['source']['building']for r in rows]);save(local/'validation-forms.json',{r['uid']:r['source']for r in rows})
    patch=take(PATCH,'summary.json')['candidate'];path=ROOT/patch['path'];assert digest(path.read_bytes())==patch['sha256'];refs.append(path)
    terrain=[dict(source=patch['path'],destination='city/data/'+BATCH+'-terrain.json',sha256=patch['sha256'],resolution=read(path)['cell'],area='Private fifteen-original diagnostic')]
    cfg=dict(viewerURL='http://127.0.0.1:4177/city.html',stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=terrain,browserUids=uids,fitBox=True,captureDirectionByModel={u:[-1,1.6,1]for u in uids},retainedBuildingUids=[b['uid']for b in forms if b['uid']not in set(uids)|set(scope['touchingNativeUids'])],jointUids=uids,nativeSupportUidsByModel={u:[v]for u,v in support_by_uid.items()},additionalRetainedUids=scope['touchingNativeUids'],privateSourceBoundTileOverlays=[],diagnosticOnly=True,publication=False)
    assert not set(cfg['retainedBuildingUids'])&set(cfg['additionalRetainedUids'])
    assert set(cfg['retainedBuildingUids'])|set(cfg['additionalRetainedUids'])=={b['uid']for b in forms if b['uid']not in uids}
    tool=HERE/'ronsdale_three_live_browser_v13_20261025.mjs';closure=HERE/'private_viewer_runtime_closure_v1_20261028.mjs';refs.extend([tool,closure]);out.mkdir()
    closurepath=out/'runtime-input-closure.json';subprocess.run(['node',str(closure),'capture',str(closurepath.relative_to(ROOT))],cwd=ROOT,check=True)
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
        def copyfile(self,source,outputfile):
            try:super().copyfile(source,outputfile)
            except(BrokenPipeError,ConnectionResetError):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        for width in [1280,390]:
            assert reservations.owns(lease)
            configpath=local/('browser-config-'+str(width)+'.json');save(configpath,dict(cfg,viewportWidths=[width],failureTestUids=uids if width==390 else [],doc=str((out/str(width)).relative_to(ROOT))+'/'))
            with(out/('browser-'+str(width)+'.log')).open('w')as log:
                result=subprocess.run(['node',str(tool),'staged',str(configpath.relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=log,stderr=subprocess.STDOUT,timeout=1800)
            save(out/('command-'+str(width)+'.json'),dict(exitCode=result.returncode))
            assert result.returncode==0 and read(out/str(width)/'staged-browser.json')['passed']
        # Atomic tests use the same exact six assets, without conferring approval.
        for m in models:m['activationGroup']=uids
        atomic=local/'atomic';atomic.mkdir();save(atomic/'catalogue.json',dict(read(local/'catalogue.json'),models=models));save(atomic/'source-forms.json',[r['source']['building']for r in rows])
        for m in models:
            target=atomic/m['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(local/m['asset'],target)
        atomiccfg=dict(cfg,stage=str(atomic.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'-atomic/catalogue.json');save(local/'atomic-config.json',atomiccfg)
        tool=HERE/'model_atomic_lifecycle_browser_v2_20261027.mjs';refs.append(tool)
        with(out/'atomic-browser.log').open('w')as log:
            result=subprocess.run(['node',str(tool),str((local/'atomic-config.json').relative_to(ROOT)),str((out/'atomic-browser').relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=log,stderr=subprocess.STDOUT,timeout=3300)
        report=read(out/'atomic-browser/report.json');assert result.returncode==0 and report['passed']and not report['pageErrors']and len(report['cases'])==16
        assert {(r['width'],r['failedUid'])for r in report['cases']}=={(1280,None)}|{(390,u)for u in uids}
        for case in report['cases']:
            assert case['completeGroupEvicted']and case['baseOnlyRestoredCompleteGroup']and not case['audit']['violations']
            assert {m['uid']:m['sha256']for m in case['sources']}=={r['uid']:r['sourceSHA256']for r in rows}
            if case['failedUid']:assert case['failureKeptAllBasics']
        assert manifest.read_bytes()==manifest_before and reservations.owns(lease)
        subprocess.run(['node',str(closure),'verify',str(closurepath.relative_to(ROOT))],cwd=ROOT,check=True);refs.append(closurepath)
        refs.extend(ROOT/p for p in read(closurepath)['inputHashes'])
        for p,h in {p:h for values in pins.values()for p,h in values.items()if ROOT/p in refs}.items():assert digest((ROOT/p).read_bytes())==h
        refs.extend(p for p in local.rglob('*')if p.is_file()and p.name!='reservation.json')
        summary=dict(uids=uids,sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},leaseResources=resources,desktopMobileBrowserPassed=True,atomicCases=16,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,qualification='Exact fifteen original source browser diagnostics only. Full approval and publisher guards remain separate. Private support metadata is a proposed graph; its installed state names the final required parent rather than granting installation credit.')
        save(out/'summary.json',summary);module('palazzo_fifteen_private_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-fifteen-original-rendering-picking-collision-and-atomic-fallback-diagnostic',list(dict.fromkeys(refs)),summary)
    finally:server.shutdown();server.server_close();thread.join(timeout=5)
if __name__=='__main__':main()
