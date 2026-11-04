"""Guarded dry run and actual private browser with five migrated dependencies."""
from pathlib import Path
import subprocess,json,uuid,sys
from run import ROOT,HERE,read,save,digest,reservations,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citywalk-reviewed-stage-checks-v1-20261015';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
STAGE=HERE/'accepted/government-xl-citywalk-reviewed-private-stage-v1-20261015';PREP=BASE/STAGE.name
PUB=HERE/'citywalk_slot_preserving_guarded_publish_v1_20261015.py';BROWSER=HERE/'citywalk_joint_resolution_browser_v1_20261015.mjs'
def main():
 if '--owned'not in sys.argv:
  assert not DOC.exists()and not LOCAL.exists();scope=read(BASE/'government-xl-citywalk-complete-current-scope-v1-20261015/scope.json.gz');uids=['landsd/134332:0']+[r['uid']for r in scope['nominatedNativeActors']];claim=reservations.claim('citywalk-stage-checks-'+str(uuid.uuid4()),['building:'+u for u in uids]+['terrain-patch:'+u for u in uids],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'lease.json',json.loads(json.dumps(lease,default=str)))
  try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'lease.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
  finally:
   if reservations.owns(lease):assert reservations.release(lease)['ok']
  return
 receipt=read(PREP/'result.json');paths=[Path(__file__),PUB,BROWSER,PREP/'result.json'];pins={r['path']:r['sha256']for r in receipt['evidenceRefs']}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;paths.append(ROOT/p)
 DOC.mkdir();manifest=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes();config=read(STAGE/'browser-config.json');config['doc']=str(DOC.relative_to(ROOT))+'/';save(LOCAL/'browser-config.json',config)
 commands=[[sys.executable,str(PUB),str((STAGE/'plan.json').relative_to(ROOT)),'--receipt',str(LOCAL/'lease.json'),'--phase',BATCH],['node',str(BROWSER),'staged',str((LOCAL/'browser-config.json').relative_to(ROOT))]]
 for i,cmd in enumerate(commands):
  with(DOC/f'command-{i}.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1800)
  assert p.returncode==0,(i,p.returncode)
 assert (ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==manifest
 report=module('citywalk_standard_browser_acceptance',HERE/'integrate.py').browser_verified(DOC/'staged-browser.json',{'landsd/134332:0'});views=[v for v in report['views']if 'time'in v];assert len(views)==4 and len(report['retainedNativeOwnViews'])==36
 assert all(v['selectionClosed']and v['fullyFramed']and v['fallbackFaces']==0 and all(o==1 for o in v['materialOpacities'])for v in views)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 paths.extend([LOCAL/'browser-config.json',HERE/'integrate.py']);paths.extend(p for p in (ROOT/'docs/astra-city/model-integration-20260909'/BATCH).rglob('*')if p.is_file())
 save(DOC/'acceptance.json',dict(passed=True,uids=['landsd/134332:0'],publication=False,sourceGeometryChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,raw294StrictFailuresPreserved=True,dependencyChanges=5,currentManifestSHA256=digest(manifest),plan=dict(path=str((STAGE/'plan.json').relative_to(ROOT)),sha256=digest((STAGE/'plan.json').read_bytes())),livePublicationRequired=True))
 module('citywalk_stage_checks_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'guarded-dry-run-and-reviewed-dependency-staged-browser-v1',paths,dict(uids=['landsd/134332:0'],stagedAccepted=True,fullAcceptance=False,newlyInstalled=0))
 print('Guarded staged checks passed',flush=True)
if __name__=='__main__':main()
