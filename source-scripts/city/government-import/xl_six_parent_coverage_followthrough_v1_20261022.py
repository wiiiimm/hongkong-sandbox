"""Follow the six exact saved-parent coverage positives through fresh current checks."""
import os,subprocess,sys
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-six-parent-coverage-followthrough-v1-20261022'
TRIAGE=BASE/'government-xl-recovered-parent-coverage-triage-v1-20261022'
PREVIOUS='government-xl-rest-recovered-current-supervisor-v1-20261022-chunk-01'
INVENTORY='government-xl-after-kam-fat-current-inventory-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists()
 tr,pins=authenticate(TRIAGE)
 path=TRIAGE/'summary.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
 eligible=[r for r in read(path)['rows'] if r['status']=='eligible-for-v6-terrain-followthrough']
 assert len(eligible)==6 and all(r['currentParentInputsVerified'] and r['parentMinimumHeight']>=1.2 for r in eligible)
 previous=BASE/PREVIOUS/'selected-source-checkpoints.json'
 _,pp=authenticate(BASE/PREVIOUS);assert digest(previous.read_bytes())==pp[str(previous.relative_to(ROOT))]
 recovered={r['uid']:r for r in read(previous)['rows']}
 uids=sorted(r['uid'] for r in eligible);names={s:BATCH+'-'+s for s in ['selection','capture','candidates']}
 refs=[Path(__file__),TRIAGE/'result.json',path,BASE/PREVIOUS/'result.json',previous]
 doc.mkdir();save(doc/'inputs.json',dict(uids=uids,names=names,inventory=INVENTORY,sourceGeometryChanges=0,publication=False))
 stages=[('selection','selected_original_refresh_selection_v1.py',['--capture',PREVIOUS+'-selection',*[x for u in uids for x in ['--uid',u]]]),('capture','selected_original_current_capture_v3.py',['--capture',names['selection'],*[x for u in uids for x in ['--uid',u]]]),('candidates','selected_original_bounded_candidate_batch_v4.py',['--capture',names['capture'],'--inventory',INVENTORY,'--workers','2',*[x for u in uids for x in ['--candidate',u+','+recovered[u]['batch']]]])]
 completed=[];failure=None
 for stage,script,tail in stages:
  tool=HERE/script;refs.append(tool)
  with (doc/(stage+'.log')).open('w') as log:
   p=subprocess.run([sys.executable,str(tool),'--batch',names[stage],*tail],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  if p.returncode:
   failure=dict(stage=stage,exitCode=p.returncode);break
  r,_=authenticate(BASE/names[stage]);refs.append(BASE/names[stage]/'result.json')
  completed.append(dict(stage=stage,batch=names[stage],jobId=r['jobId']))
  save(doc/'progress.json',dict(completed=completed,uids=uids));print(completed[-1],flush=True)
 result=dict(uids=uids,completed=completed,failure=failure,status='script-investigation'if failure else'current-candidate-checks-complete',newlyInstalled=0,installationApproved=False,sourceGeometryChanges=0,publication=False,scriptExternalAICalls=0)
 save(doc/'summary.json',result)
 module('six_coverage_followthrough_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'six-original-parent-coverage-current-followthrough',refs,result)
if __name__=='__main__':main()
