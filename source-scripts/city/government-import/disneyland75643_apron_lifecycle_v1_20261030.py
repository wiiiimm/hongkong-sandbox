"""Private exact-original apron-graphic lifecycle; no installation/geometry writes."""
from pathlib import Path
import functools
import http.server
import json
import os
import subprocess
import threading
import uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-disneyland-eastern75643-apron-current-lifecycle-v1-20261030'
PREVIEW='government-xl-disneyland-eastern75643-apron-current-native-preview-v1-20261030'
UID='landsd/75643:0'
SHA='4c8e577256875f9ecc67fe5728e262113d852748ac743798b804f9b090f0dbc2'


def main():
    out=BASE/BATCH;local=HERE/'local'/BATCH
    assert not out.exists()and not local.exists()
    receipt,pins=authenticate(BASE/PREVIEW)
    stage=HERE/'local'/PREVIEW
    refs=[Path(__file__),BASE/PREVIEW/'result.json']
    for name in ['catalogue.json','source-forms.json','browser-config-390.json']:
        p=stage/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
    catalogue=read(stage/'catalogue.json');assert len(catalogue['models'])==1
    source=catalogue['models'][0];assert source['uid']==UID and source['sha256']==SHA
    fixturepath=ROOT/'3d-viewer/city/tests/fixtures/disneyland-reviewed-osm-apron.json';fixture=read(fixturepath);refs.append(fixturepath)
    assert source['reviewedOsmApronGraphic']==fixture['catalogue']['models'][0]['reviewedOsmApronGraphic']
    assert source['suppressesBuildingUids']==['way/334029318:0'] and not source.get('supportDependencies')
    asset=stage/source['asset'];assert digest(asset.read_bytes())==SHA;refs.append(asset)
    original_manifest=ROOT/'3d-viewer/city/data/manifest.json';before=original_manifest.read_bytes();refs.append(original_manifest)
    cfg=read(stage/'browser-config-390.json');assert not cfg['terrain']
    cfg.update(diagnosticOnly=True,publication=False,expectedOwnerUid=UID,expectedSourceSHA256=SHA,expectedCanopyUid='way/334029318:0')
    tool=HERE/'model_single_canopy_lifecycle_browser_v1_20261029.mjs';refs.append(tool)
    claim=reservations.claim('pier-apron-lifecycle-'+str(uuid.uuid4()),['building:'+UID,'source-form:way/334029318:0','terrain:city/data/terrain.json','server:127.0.0.1:4177'],batch=BATCH,ttl=3600)
    assert claim['ok'];lease=claim['reservation'];server=None;thread=None
    try:
        out.mkdir();save(local/'reservation.json',json.loads(json.dumps(lease,default=str)));save(local/'browser-config.json',cfg)
        class Handler(http.server.SimpleHTTPRequestHandler):
            def log_message(self,*args):pass
        server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        with (out/'browser.log').open('w')as log:
            command=['node',str(tool),str((local/'browser-config.json').relative_to(ROOT)),str(out.relative_to(ROOT))]
            result=subprocess.run(command,cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=log,stderr=subprocess.STDOUT,timeout=3300)
        save(out/'command.json',dict(command=command,exitCode=result.returncode))
        assert reservations.owns(lease)and original_manifest.read_bytes()==before
        report=read(out/'report.json')
        passed=result.returncode==0 and report.get('passed')is True and not report['pageErrors']
        if passed:
            assert len(report['cases'])==2
            for case in report['cases']:
                assert case['completeGroupEvicted']and case['baseOnlyRestoredCompleteGroup']and not case['audit']['violations']
                phases={r['phase']:r for r in case['canopyLifecycle']}
                assert {'original-active','base-only','auto-restored','evicted-return-base-only'}<=set(phases)
                if case['failedUid']:assert case['failureKeptAllBasics']and 'failed-download'in phases
        summary=dict(uids=[UID],sourceSHA256=SHA,passed=passed,privateLoopbackPort=4177,shared4176Untouched=True,
                     geometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,
                     qualification='Single immutable original source; exact reviewed BASIC apron graphic visibility must follow source availability through failure/retry, Base-only, Auto and eviction/return. No source identity or architectural approval granted.')
        server.shutdown();server.server_close();thread.join(timeout=5);server=None
        save(out/'summary.json',summary);refs.append(local/'browser-config.json')
        module('single_canopy_lifecycle_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-original-pier-apron-graphic-full-lifecycle',refs,summary)
        assert passed,'Lifecycle failed; complete report retained'
    finally:
        if server is not None:server.shutdown();server.server_close()
        if thread is not None:thread.join(timeout=5)
        assert reservations.release(lease)['ok']


if __name__=='__main__':main()
