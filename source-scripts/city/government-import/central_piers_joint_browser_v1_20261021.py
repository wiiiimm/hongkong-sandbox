"""Joint staged pier originals with desktop/mobile and failed-download recovery."""
from pathlib import Path
import os,subprocess,json,sys,uuid,copy
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-piers-joint-browser-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;UIDS=['landsd/213352:0','landsd/285475:0'];NODE='/home/williamli/.nvm/versions/node/v24.18.0/bin/node'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)];pins={}
 def take(n,p):
  _,ps=authenticate(BASE/n);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/n/'result.json',p]);return read(p)
 assert take('government-xl-central-piers-native-delta-v1-20261021',BASE/'government-xl-central-piers-native-delta-v1-20261021/summary.json')['neighbourRegressionPassed']
 policy=take('government-xl-central-piers-original-policy-v1-20261021',BASE/'government-xl-central-piers-original-policy-v1-20261021/summary.json');assert all(r['originalPolicyPassed']for r in policy['rows'])
 catalogues=[];forms=[]
 for label,n in [('pier8','government-xl-central-pier8-staged-browser-v1-20261021'),('pier7','government-xl-central-pier7-staged-browser-v3-20261021')]:
  old=HERE/'local'/n;cat=take(n,old/'catalogue.json');catalogues.append(cat);forms.extend(take(n,old/'source-forms.json'))
  for m in cat['models']:
   raw=(old/m['asset']).read_bytes();assert digest(raw)==m['sha256'];refs.append(old/m['asset']);p=LOCAL/m['asset'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 cat=copy.deepcopy(catalogues[0]);cat['models']=[m for c in catalogues for m in c['models']];cat['counts']['packedModels']=2;assert {m['uid']for m in cat['models']}==set(UIDS)
 save(LOCAL/'catalogue.json',cat);save(LOCAL/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',forms)
 n='government-xl-central-piers-private-wrapper-v2-20261021';candidate=take(n,BASE/n/'terrain-candidates.json')[0];p=ROOT/candidate['path'];assert digest(p.read_bytes())==candidate['sha256'];refs.append(p)
 terrain=[dict(source=candidate['path'],destination='city/data/government-native-central-piers-private-browser-v1-20261021.json',sha256=candidate['sha256'],resolution=read(p)['cell'],area='Central piers unchanged original pair',replaces=candidate['replaces'])]
 tool=HERE/'tko_grandiose_synchronised_browser_v2_20261021.mjs';refs.append(tool)
 cfg=dict(stage=str(LOCAL.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=terrain,browserUids=UIDS,failureTestUids=UIDS,fitBox=True,captureDirectionByModel={u:[-.3,.5,-1]for u in UIDS},localJointViews=[dict(id='both-pier-originals',uids=UIDS,target=[185,9,75],camera=[130,100,-130])])
 for width in [1280,390]:
  assert reservations.owns(lease);config={**cfg,'viewportWidths':[width],'doc':str((DOC/str(width)).relative_to(ROOT))+'/'};p=LOCAL/f'browser-config-{width}.json';save(p,config);DOC.mkdir(parents=True,exist_ok=True)
  with(DOC/f'browser-{width}.log').open('w')as log:proc=subprocess.run([NODE,str(tool),'staged',str(p.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1200)
  save(DOC/f'command-{width}.json',dict(exitCode=proc.returncode));assert proc.returncode==0;report=read(DOC/str(width)/'staged-browser.json');assert report['passed']and not report['errors']
  if width==390:assert {r['uid']for r in report['views']if r.get('phase')=='failed-download'and r['fallbackRetained']}==set(UIDS)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');r=module('piers_joint_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'joint-original-desktop-mobile-recovery-browser',list(dict.fromkeys(refs)),dict(uids=UIDS,installationApproved=False,visualAcceptance=False,sourceGeometryChanges=0));print(r['jobId'],flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();c=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert c['ok'],c;lease=c['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
