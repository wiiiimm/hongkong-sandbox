"""Capture one obstructed retained actor after the installation worker finishes.

Read-only actual HTTP viewer checks under a separate lease/publication lock.
The installed ledger and all original source/terrain bytes remain unchanged.
"""
import argparse,json,os,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from publication_lock import locked_publication
BASE=ROOT/'docs/astra-city/government-import'
INSTALLED=BASE/'government-xl-ocean-coordinated-original-original-installed-v1-20261027'
BATCH='government-xl-ocean-live-retained-visibility-camera-v1-20261027'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
UIDS=['landsd/232907:0']

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    receipt,pins=authenticate(INSTALLED);assert receipt['publication'] and receipt['newlyInstalled']==2
    manifest=ROOT/'3d-viewer/city/data/manifest.json';expected=receipt['manifest']['sha256'];assert digest(manifest.read_bytes())==expected
    if not a.owned:
        assert not DOC.exists() and not LOCAL.exists()
        resources=['building:'+u for u in UIDS]+['terrain:city/data/terrain.json','immutable-source-proof:'+BATCH]
        claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];save(LEASE,json.loads(json.dumps(lease,default=str)))
        try:subprocess.run([sys.executable,str(HERE/'bounded_reserved_runner_v2_20261022.py'),str(LEASE),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
        finally:
            if reservations.owns(lease):assert reservations.release(lease)['ok']
        return
    lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists()
    with locked_publication(ROOT):
        assert digest(manifest.read_bytes())==expected
        refs=[Path(__file__),INSTALLED/'result.json',manifest];models={}
        for url in read(manifest)['officialModelCatalogues']:
            path=ROOT/'3d-viewer'/url
            for model in read(path)['models']:
                if model['uid'] not in UIDS:continue
                assert model['uid'] not in models;models[model['uid']]=model;refs.append(path)
                asset=path.parent/model['asset'];assert digest(asset.read_bytes())==model['sha256'];refs.append(asset)
        assert set(models)==set(UIDS)
        for name in ['app.js','official-models.js','streaming.js','model-group-lifecycle.js','model-activation-groups.js','model-support.js']:
            path=ROOT/'3d-viewer/city'/name;assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path)
        refs.append(ROOT/'3d-viewer/city/model-spatial-index.js')
        cfg=LOCAL/'config.json';save(cfg,dict(doc=str(DOC.relative_to(ROOT))+'/',viewerURL='http://127.0.0.1:4177/city.html',publication=False,geometryEdits=0,uids=UIDS,sourceSHA256ByUid={u:m['sha256'] for u,m in models.items()}))
        tool=HERE/'retained_live_visibility_camera_v1_20261027.mjs';refs.extend([cfg,tool]);before={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in refs}
        DOC.mkdir();command=['node',str(tool),str(cfg.relative_to(ROOT))]
        with (DOC/'browser.log').open('w') as log:p=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1800)
        save(DOC/'command.json',dict(command=command,exitCode=p.returncode));assert p.returncode==0
        report=read(DOC/'report.json');assert report['passed'] and not report['errors'] and report['manifestSHA256']==expected
        assert len(report['views'])==4 and {(v['uid'],v['width'],v['time']) for v in report['views']}=={(u,w,t) for u in UIDS for w in [390,1280] for t in ['15:00','22:00']}
        for v in report['views']:
            assert v['active'] and v['visible'] and v['fullyFramed'] and v['sourceSHA256']==models[v['uid']]['sha256']
            assert v['cameraChoice']['choice']['unobstructed']>=4
        assert reservations.owns(lease)
        for path,sha in before.items():assert digest((ROOT/path).read_bytes())==sha,path
        save(DOC/'summary.json',dict(uids=UIDS,browserPassed=True,sourceSHA256ByUid={u:m['sha256'] for u,m in models.items()},rawObstructedExportsPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,installedMetadataChanges=0,visualAcceptance=False,publication=False,performanceAcceptance=False))
        module('ocean_live_camera_followup_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'installed-retained-target-visibility-camera-only-proof-v1',refs,read(DOC/'summary.json'))

if __name__=='__main__':main()
