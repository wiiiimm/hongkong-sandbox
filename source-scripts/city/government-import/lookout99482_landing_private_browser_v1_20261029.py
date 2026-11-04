"""Run existing real-viewer assertions on an isolated unchanged Lookout fixture."""
import argparse,copy,functools,http.server,os,subprocess,sys,threading,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from lookout99482_landing_source_role_account_v1_20261029 import P,UID,SOURCE,TERRAIN
BATCH=P+'landing-private-browser-v1-20261029';BASE=ROOT/'docs/astra-city/government-import'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json';assert not out.exists()
    names=dict(runtime=P+'landing-runtime-v1-20261029',patch=P+'landing-inset-v1-20261029',review=P+'landing-physical-review-v1-20261029',scope=P+'landing-scope-v1-20261029')
    pins={};refs=[Path(__file__)]
    def take(key,path):
        name=names[key]
        if name not in pins:pins[name]=authenticate(BASE/name)[1];refs.append(BASE/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take('runtime',BASE/names['runtime']/'selection.json.gz');assert len(selection['rows'])==1;row=selection['rows'][0]
    review=take('review',BASE/names['review']/'ROOT-PHYSICAL-REVIEW.json');assert review['sourceSpecificPhysicalInterpretationAccepted']and review['sourceSHA256ByUid']=={UID:SOURCE}
    forms=take('scope',BASE/names['scope']/'form-obligations.json.gz');resources=sorted({'building:'+r['uid']for r in forms}|{'building:'+UID,'terrain:city/data/terrain.json'})
    assert len(forms)==3
    if not a.owned:
        assert not local.exists();claim=reservations.claim('lookout-original-browser-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(resources)<=set(lease['resources'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    tile=ROOT/'3d-viewer'/row['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==UID)==row['source']['building'];refs.append(tile)
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');native=db.execute('SELECT i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s',(row['native']['cacheKey'],)).fetchone()
    assert native and native[1]==row['native']['resultSha']
    entry=copy.deepcopy(row['candidate']['entry']);assert entry['uid']==UID and entry['sha256']==SOURCE and not entry.get('supportDependencies')and not entry.get('suppressesBuildingUids')
    entry.update(sourceTile=native[0],priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False,asset='assets/'+SOURCE+'.glb.gz')
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SOURCE;refs.append(asset);dest=local/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(asset.read_bytes())
    save(local/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=[entry],counts=dict(packedModels=1)))
    save(local/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(local/'source-forms.json',[row['source']['building']]);save(local/'validation-forms.json',{UID:row['source']})
    patch=take('patch',BASE/names['patch']/'summary.json');candidate=ROOT/patch['candidate']['path'];assert digest(candidate.read_bytes())==patch['candidate']['sha256']==TERRAIN;refs.append(candidate)
    config=dict(diagnosticOnly=True,publication=False,stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[dict(source=str(candidate.relative_to(ROOT)),destination='city/data/'+BATCH+'-terrain.json',sha256=TERRAIN,resolution=read(candidate)['cell'],area='Private original Lookout landing terrain')],viewerURL='http://127.0.0.1:4177/city.html',browserUids=[UID],retainedBuildingUids=sorted(r['uid']for r in forms if r['uid']!=UID),additionalRetainedUids=[],jointUids=[UID],fitBox=True,fitJointCamera=True,fitJointCameraMobile=True,failureTestUids=[UID],captureDirectionByModel={UID:[-1,.8,1]})
    tool=HERE/'ronsdale_three_live_browser_v19_20261028.mjs';refs.append(tool);out.mkdir();log=(out/'private-server.log').open('w')
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,fmt,*args):log.write((fmt%args)+'\n');log.flush()
    server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();commands=[]
    try:
        preflight=local/'preflight-config.json';save(preflight,dict(config,doc=str(out.relative_to(ROOT))+'/'))
        subprocess.run(['node',str(tool),'preflight',str(preflight.relative_to(ROOT))],cwd=ROOT,check=True)
        for width in [1280,390]:
            assert reservations.owns(lease);cfg=local/('browser-config-'+str(width)+'.json');save(cfg,dict(config,viewportWidths=[width],doc=str((out/str(width)).relative_to(ROOT))+'/'))
            print(dict(width=width,phase='private-browser-start'),flush=True)
            with(out/('browser-'+str(width)+'.log')).open('w')as stdout:
                proc=subprocess.run(['node',str(tool),'staged',str(cfg.relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=stdout,stderr=subprocess.STDOUT,timeout=1800)
            path=out/str(width)/'staged-browser.json';report=read(path)if path.exists()else{}
            record=dict(width=width,exitCode=proc.returncode,reportPresent=path.exists(),passed=proc.returncode==0 and report.get('passed')is True);commands.append(record);save(out/('command-'+str(width)+'.json'),record);print(record,flush=True)
            if proc.returncode:break
        assert reservations.owns(lease)
        for path in refs:
            key=str(path.relative_to(ROOT))
            for bound in pins.values():
                if key in bound:assert digest(path.read_bytes())==bound[key]
        refs.extend(p for p in local.rglob('*')if p.is_file()and p.name!='reservation.json')
        result=dict(uids=[UID],commands=commands,allBrowserDiagnosticsPassed=len(commands)==2 and all(r['passed']for r in commands),sourceGeometryChanges=0,sourcePoseChanges=0,productionFilesWritten=0,privateLoopbackPort=4177,shared4176Untouched=True,sourceSHA256ByUid={UID:SOURCE},terrainCandidateSHA256=TERRAIN,visualAcceptance=False,installationApproved=False,publication=False,qualification='Existing V19 desktop/mobile assertions, whole current viewer, exact immutable original and validated terrain overlay. No production module, catalogue or terrain writes. ROOT must inspect actual exports; browser diagnostics alone grant no visual or installation approval.')
        save(out/'summary.json',result);module('lookout_private_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-exact-lookout-desktop-mobile-real-viewer',list(dict.fromkeys(refs)),result)
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5);log.close()

if __name__=='__main__':main()
