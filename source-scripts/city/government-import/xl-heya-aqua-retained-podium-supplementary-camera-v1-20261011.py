"""Unexecuted supplementary PRIVATE camera-only views; original stage immutable.
No BASIC hidden, geometry/source/terrain transformed, bounds clipped, or residency
forced. Reuses exact original private scene and normal user visits/production loader.
"""
import importlib.util,json,os,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-heya-aqua-retained-podium-supplementary-camera-v1-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
HELPER=HERE/'xl-heya-aqua-retained-podium-high-camera-browser-v1-20261011.mjs'
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def pin(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
 stage=module('heya_original_private_stage_camera_context',HERE/'xl-heya-aqua-184286-unchanged-private-stage-v1-20261011.py')
 old=read(stage.DOC/'acceptance.json');assert old['passed']and not old['publication']
 role,entry,_=stage.recheck(LOCAL/'initial-current-recheck')
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes()
 files=[Path(__file__),HELPER,Path(stage.__file__),stage.SOURCE_CERT,stage.ROLE/'result.json',stage.DOC/'acceptance.json',stage.DOC/'staged-browser.json',stage.STAGE/'browser-config.json',stage.STAGE/'catalogue.json',stage.STAGE/'plan.json']
 files += [stage.DOC/v['file']for v in read(stage.DOC/'staged-browser.json')['views']if 'time'in v]
 files += [stage.DOC/v['file']for v in read(stage.DOC/'staged-browser.json')['retainedNativeOwnViews']]
 source=read(stage.DOCS['actual']/'complete-current-actual-source-and-ground-184285-0.json.gz')
 files.append(stage.DOCS['actual']/'complete-current-actual-source-and-ground-184285-0.json.gz')
 bounds=np.asarray(source['completeWholeUnusedVertexBounds'],dtype='<f8');assert bounds.shape==(3,2,3)and np.isfinite(bounds).all()
 support=read(stage.DOCS['identity']/'installed-support-entry.json');assert source['entry']==support['entry']and source['sourceSHA256']==support['entry']['sha256']
 complete=[bounds[:,0,:].min(0).tolist(),bounds[:,1,:].max(0).tolist()]
 expected=np.asarray(support['entry']['worldBounds']);assert np.all(np.asarray(complete)[0]<=expected[0])and np.all(np.asarray(complete)[1]>=expected[1])
 pins=[pin(p)for p in files]
 config=read(stage.STAGE/'browser-config.json')
 config.update(doc=str(DOC.relative_to(ROOT))+'/',retainedCaptureBoundsByModel={stage.P:complete},retainedCaptureDirectionByModel={stage.P:[.05,1,.05]},retainedCandidateWitnessUids=[stage.UID])
 save(LOCAL/'browser-config.json',config);pins.append(pin(LOCAL/'browser-config.json'))
 subprocess.run(['node',str(HELPER),'staged',pin(LOCAL/'browser-config.json')['path']],cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'})
 report=module('heya_supplementary_camera_report',HERE/'integrate.py').browser_verified(DOC/'staged-browser.json',{stage.UID})
 own=[v for v in report['views']if 'time'in v];retained=report['retainedNativeOwnViews'];assert len(own)==len(retained)==4
 assert {(v['uid'],v['width'],v['time'])for v in retained}=={(stage.P,w,t)for w in [1280,390]for t in ['15:00','22:00']}
 for v in retained:
  assert v['active']and v['visible']and v['fullyFramed']and v['originalTriangles']==3844 and v['sourceSHA256']==support['entry']['sha256']and v['fallbackFaces']==0
  t=v['candidateSourceWitnesses'][stage.UID];assert t['active']and t['visible']and t['sourceSHA256']==entry['sha256']and t['originalTriangles']==17910 and t['fallbackFaces']==0 and all(t['meshVisibility'])
 final,finalentry,_=stage.recheck(LOCAL/'final-current-recheck');assert final==role and finalentry==entry
 assert manifest.read_bytes()==before and reservations.owns(lease)
 for p in pins:assert pin(ROOT/p['path'])==p
 save(DOC/'supplementary-camera-result.json',dict(cameraOnly=True,passed=True,publication=False,newlyInstalled=0,sourceGeometryChanges=0,terrainGeometryChanges=0,basicActorsHidden=False,sourceTransformsChanged=False,forcedResidency=False,boundsClipped=False,originalStagePreserved=True,originalStageAcceptance=pin(stage.DOC/'acceptance.json'),completePodiumCaptureBounds=complete,retainedCaptureDirection=[.05,1,.05],browser=pin(DOC/'staged-browser.json'),exports=[pin(DOC/v['file'])for v in own+retained],evidenceRefs=pins))
 print(json.dumps(dict(supplementaryCameraPassed=True,publication=False)),flush=True)
def main():
 if '--owned'in sys.argv:
  from publication_lock import locked_publication
  with locked_publication(ROOT):return owned()
 assert not DOC.exists()and not LOCAL.exists()
 forms=read(BASE/'government-xl-heya-aqua-184286-184285-current-actual-ground-capture-v1-20261011/capture-inputs.json.gz')['completeCurrentForms']
 claim=reservations.claim('heya-supplementary-camera-'+str(uuid.uuid4()),['building:'+f['uid']for f in forms],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
