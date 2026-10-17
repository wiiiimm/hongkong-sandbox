"""DRAFT separate reviewed high-camera reports; no scene or geometry mutations."""
import os,subprocess,importlib.util
import numpy as np
from run import ROOT,HERE,read,save,digest
P='landsd/184285:0';T='landsd/184286:0'
HELPER=HERE/'xl-heya-aqua-retained-podium-high-camera-browser-v1-20261011.mjs'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def supplementary(stage,mode):
 source=read(stage.DOCS['actual']/'complete-current-actual-source-and-ground-184285-0.json.gz');support=read(stage.DOCS['identity']/'installed-support-entry.json')['entry'];entry=read(stage.STAGE/'catalogue.json')['models'][0]
 assert source['entry']==support and source['sourceSHA256']==support['sha256']
 b=np.asarray(source['completeWholeUnusedVertexBounds']);assert b.shape==(3,2,3)and np.isfinite(b).all()
 bounds=[b[:,0,:].min(0).tolist(),b[:,1,:].max(0).tolist()]
 config=read(stage.STAGE/'browser-config.json');config.update(doc=str((stage.DOC/'supplementary').relative_to(ROOT))+'/',retainedCaptureBoundsByModel={P:bounds},retainedCaptureDirectionByModel={P:[.05,1,.05]},retainedCandidateWitnessUids=[T])
 path=stage.DOC/'supplementary-camera-config.json'
 if path.exists():assert read(path)==config
 else:save(path,config)
 subprocess.run(['node',str(HELPER),mode,str(path.relative_to(ROOT))],cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'})
 report=read(stage.DOC/'supplementary'/(mode+'-browser.json'));assert report['passed']and report['errors']==[]
 views=report['retainedNativeOwnViews'];assert {(v['uid'],v['width'],v['time'])for v in views}=={(P,w,t)for w in [1280,390]for t in ['15:00','22:00']}and len(views)==4
 for v in views:
  assert v['sourceSHA256']==support['sha256']and v['originalTriangles']==3844 and v['active']and v['visible']and v['fullyFramed']and v['fallbackFaces']==0
  t=v['candidateSourceWitnesses'][T];assert t['sourceSHA256']==entry['sha256']and t['originalTriangles']==17910 and t['active']and t['visible']and t['fallbackFaces']==0 and all(t['meshVisibility'])
 return report
