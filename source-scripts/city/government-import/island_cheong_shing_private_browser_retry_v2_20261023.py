"""Retry a terminal private browser observation with exact-source scripted cameras."""
from pathlib import Path
import os,subprocess,sys
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-cheong-shing-private-browser-retry-v2-20261023';out=base/batch;assert not out.exists();refs=[Path(__file__)]
    failed='government-xl-island-cheong-shing-repaired-acceptance-chain-v1-20261023';r,_=authenticate(base/failed);refs.append(base/failed/'result.json');assert r['status']=='source-or-script-review-required'and r['stoppedAt']=='browser'
    physical='government-xl-island-cheong-shing-physical-review-v1-20261023';_,pins=authenticate(base/physical);refs.append(base/physical/'result.json');p=base/physical/'ROOT-PHYSICAL-REVIEW.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);review=read(p);assert review['sourceSpecificPhysicalInterpretationAccepted'];sources=review['sourceSHA256ByUid']
    for uid in ['20270','159422']:
        n='government-xl-island-'+uid+'-four-source-camera-v1-20261023';_,pins=authenticate(base/n);refs.append(base/n/'result.json');p=base/n/'summary.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);camera=read(p);assert camera['sourceSHA256']==sources['landsd/'+uid+':0']and camera['cameraDirection']==[1.,1.2,0.]
    retained=sorted({u for r in review['exactTerrainReplacements']for u in r['retainedUids']});assert len(retained)==32
    child='government-xl-island-cheong-shing-four-original-private-browser-v2-20261023';assert not(base/child).exists();script=HERE/'selected_original_coordinated_staged_browser_v2_20261023.py';refs.append(script)
    command=[sys.executable,str(script),'--batch',child,'--runtime','government-xl-island-cheong-shing-four-original-runtime-v4-20261023','--patch','government-xl-island-industrial-paired-surface-binding-v6-20261023','--review',physical,'--support','landsd/20270:0,landsd/159422:0','--support','landsd/274231:0,landsd/269430:0','--capture-direction','1','1.2','0',*[x for u in retained for x in ['--retain-native',u]]]
    out.mkdir();log=out/'browser.log';env=dict(os.environ);env['PATH']='/home/williamli/.nvm/versions/node/v24.18.0/bin:'+env.get('PATH','');env['OPENBLAS_NUM_THREADS']='1';env['PYTHONDONTWRITEBYTECODE']='1'
    save(out/'command.json',dict(command=command,observationTimeoutSecondsPerViewport=2400,perActorChecksUnchanged=True,installationApproved=False))
    with log.open('w')as f:proc=subprocess.run(command,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
    refs.append(log);result=dict(uids=sorted(sources),exitCode=proc.returncode,sourceGeometryChanges=0,visualAcceptance=False,installationApproved=False)
    if not proc.returncode:r,_=authenticate(base/child);refs.append(base/child/'result.json');result.update(status='private-device-evidence-awaiting-root-image-review',browserJobId=r['jobId'])
    else:result['status']='private-device-observation-or-script-investigation'
    save(out/'summary.json',result);module('browser_retry_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-original-private-browser-terminal-observation-retry',refs,result)

if __name__=='__main__':main()
