"""Finite original-terrain checks; each concrete phase holds its own canonical lease."""
import sys,subprocess
from run import ROOT,HERE,read,save
from china_ferry_current_foundations_v1_20261020 import authenticate
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-silvercord-lippo-complete-floor-checks-sequence-v1-20261103'
STEPS=[('scope','silvercord_lippo_full_parent_scope_v3_20261103.py','government-xl-silvercord-lippo-full-current-parent-scope-v3-20261103'),('runtime','silvercord_lippo_complete_floor_runtime_v2_20261103.py','government-xl-silvercord-lippo-complete-floor-runtime-v2-20261103'),('forms','silvercord_lippo_complete_floor_form_regression_v4_20261103.py','government-xl-silvercord-lippo-complete-floor-full-form-regression-v4-20261103')]
def main():
 graph,_=authenticate(BASE/'government-xl-silvercord-lippo-graph-surface-diagnostic-v4-20261103');assert graph['allFiniteSeamsPassed'] and graph['allMemberSurfaceChecksPassed'] and not graph['installationApproved']
 local=HERE/'local'/BATCH;assert not local.exists();completed=[]
 for name,script,batch in STEPS:
  save(local/'progress.json',dict(currentPhase=name,completed=completed,installationApproved=False))
  print(dict(starting=name,script=script),flush=True)
  subprocess.run([sys.executable,str(HERE/script)],cwd=ROOT,check=True)
  result,_=authenticate(BASE/batch)
  if name=='runtime':assert result['exactWholeRenderedFaceMultisetMatchesPrivateTrial'] and all(r['fullyBuriedUpwardTriangles']==0 for r in result['rows'])
  completed.append(dict(phase=name,batch=batch,jobId=result['jobId']))
 save(local/'progress.json',dict(complete=True,completed=completed,installationApproved=False))
 print(dict(complete=True,phases=completed,installationApproved=False),flush=True)
if __name__=='__main__':main()
