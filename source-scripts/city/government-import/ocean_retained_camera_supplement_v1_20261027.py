"""Supplement obstructed retained views; preserve all original full-run evidence.

Only camera directions and the supplemental retained observation set change.
The exact original catalogue, terrain, runtime and five atomic lifecycle cases
remain bound to the completed full run. This script grants no visual approval.
"""
import argparse,json,os,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BATCH='government-xl-ocean-retained-camera-supplement-v1-20261027'
PREVIOUS='government-xl-ocean-coordinated-full-browser-v2-20261027'
PHYSICAL='government-xl-ocean-four-original-physical-review-v2-20261027'
UIDS=sorted('landsd/'+s+':0' for s in ['213822','101781','319534','232907','263590','239465'])
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'

def supplement(config):
    import copy
    result=copy.deepcopy(config)
    result['additionalRetainedUids']=UIDS[:]
    result['retainedCaptureDirectionByModel']={u:[0,1,.01] for u in UIDS}
    result.pop('doc',None);result.pop('viewportWidths',None)
    # No new failure-test credit. The mandatory completed five-case atomic
    # run is authenticated separately, on the exact unchanged stage/runtime.
    assert result['failureTestUids']==[]
    assert result['catalogueReplacements']==[]
    allowed={'additionalRetainedUids','retainedCaptureDirectionByModel','doc','viewportWidths'}
    assert {k:v for k,v in result.items() if k not in allowed}=={k:v for k,v in config.items() if k not in allowed}
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    receipt,pins=authenticate(BASE/PREVIOUS)
    assert receipt['allBrowserDiagnosticsPassed'] and receipt['atomicFailureCases']==5
    assert not receipt['visualAcceptance'] and not receipt['installationApproved']
    for rel,sha in pins.items():assert digest((ROOT/rel).read_bytes())==sha,rel
    physical,physical_pins=authenticate(BASE/PHYSICAL)
    review_path=BASE/PHYSICAL/'ROOT-PHYSICAL-REVIEW.json'
    assert digest(review_path.read_bytes())==physical_pins[str(review_path.relative_to(ROOT))]
    review=read(review_path);assert set(UIDS)<=set(receipt['retainedNativeUids'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes())==review['currentManifestSHA256']
    if not a.owned:
        assert not DOC.exists() and not LOCAL.exists()
        claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),review['leaseResources'],batch=BATCH,ttl=3600)
        assert claim['ok'];lease=claim['reservation'];save(LEASE,json.loads(json.dumps(lease,default=str)))
        try:subprocess.run([sys.executable,str(HERE/'bounded_reserved_runner_v2_20261022.py'),str(LEASE),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
        finally:
            if reservations.owns(lease):assert reservations.release(lease)['ok']
        return
    lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists();DOC.mkdir()
    prior=HERE/'local'/PREVIOUS
    config_path=prior/'browser-config-1280.json'
    assert digest(config_path.read_bytes())==pins[str(config_path.relative_to(ROOT))]
    config=supplement(read(config_path));tool=HERE/'ronsdale_three_live_browser_v15_20261026.mjs'
    assert digest(tool.read_bytes())==pins[str(tool.relative_to(ROOT))]
    reports=[]
    for width in [1280,390]:
        cfg=LOCAL/('browser-config-'+str(width)+'.json')
        save(cfg,dict(**config,viewportWidths=[width],doc=str((DOC/str(width)).relative_to(ROOT))+'/'))
        assert reservations.owns(lease);print('supplement',width,'starting',flush=True)
        command=['node',str(tool),'staged',str(cfg.relative_to(ROOT))]
        with (DOC/('browser-'+str(width)+'.log')).open('w') as log:
            p=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1800)
        save(DOC/('browser-'+str(width)+'-command.json'),dict(command=command,exitCode=p.returncode));assert p.returncode==0
        report=read(DOC/str(width)/'staged-browser.json');assert report['passed'] and not report['errors']
        views=report['retainedNativeOwnViews']
        assert {(r['uid'],r['time']) for r in views}=={(u,t) for u in UIDS for t in ['15:00','22:00']} and len(views)==12
        assert all(r['active'] and r['visible'] and r['fullyFramed'] and r['fallbackFaces']==0 for r in views)
        reports.append(dict(width=width,retainedViews=len(views)));assert reservations.owns(lease)
        print('supplement',width,'passed',flush=True)
    for rel,sha in pins.items():assert digest((ROOT/rel).read_bytes())==sha,rel
    assert digest(manifest.read_bytes())==review['currentManifestSHA256']
    refs=[Path(__file__),BASE/PREVIOUS/'result.json',BASE/PHYSICAL/'result.json',review_path,tool,manifest]
    refs.extend(ROOT/rel for rel in pins)
    refs.extend(p for p in LOCAL.rglob('*') if p.is_file() and p.name!='reservation.json')
    result=dict(uids=receipt['uids'],supplementRetainedUids=UIDS,reports=reports,allBrowserDiagnosticsPassed=True,fullBrowserReceipt=PREVIOUS,mandatoryAtomicCasesBoundToFullRun=5,visualAcceptance=False,installationApproved=False,publication=False,performanceAcceptance=False,sourceGeometryChanges=0,existingCatalogueChanges=0,qualification='Additional camera-only observations. Original obstructed captures remain intact; no automatic visual approval.')
    save(DOC/'summary.json',result)
    module('ocean_camera_supplement_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-retained-camera-only-supplement-v1',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
