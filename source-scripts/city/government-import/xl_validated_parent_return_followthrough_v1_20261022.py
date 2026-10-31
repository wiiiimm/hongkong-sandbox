"""After the exact current cohort finishes, test the corrected validated parent return."""
import subprocess,sys,time
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
OLD='government-xl-six-parent-coverage-followthrough-v1-20261022'
RUNNER=BASE/'government-xl-six-parent-coverage-detached-runner-v1-20261022'
BATCH='government-xl-validated-parent-return-followthrough-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();doc.mkdir()
 runner=read(RUNNER/'runner.json');refs=[Path(__file__),RUNNER/'runner.json']
 save(doc/'waiting-for.json',dict(runner=runner,qualification='Wait for exact existing cohort; no model worker duplicated.'))
 terminal=RUNNER/'terminal.json'
 while not terminal.exists():
  p=Path('/proc')/str(runner['pid'])
  if not p.exists():raise RuntimeError('Exact worker missing without terminal receipt; inspect, do not restart')
  assert (p/'stat').read_text().split()[21]==runner['startTicks'],'Worker PID reused; no automatic continuation'
  assert '--owned' in (p/'cmdline').read_bytes().decode().replace('\0',' ')
  time.sleep(20)
 assert read(terminal)['exitCode']==0,'Earlier cohort failed; inspect before continuation'
 old,pins=authenticate(BASE/OLD);cohort,cp=authenticate(BASE/(OLD+'-candidates'))
 refs.extend([terminal,BASE/OLD/'result.json',BASE/(OLD+'-candidates')/'result.json'])
 selected=[r for r in cohort['rows'] if r['status']=='terrain-investigation' and r.get('reasons')==['Native terrain boundary does not join parent heights']]
 assert selected,'No applicable parent-boundary failure; no unrelated retries'
 candidate_pairs=[]
 for r in selected:
  f=BASE/r['batches']['terrain'];result,rp=authenticate(f);trace=read(f/'failure.json')['traceback']
  assert 'builder.validate_patch(template, parent)' in trace,'Only final inset failure is covered by this construction fix'
  p=f/'terrain-source-context.json';assert digest(p.read_bytes())==rp[str(p.relative_to(ROOT))]
  # The exact original terrain binding is retained in the authenticated prior candidate selection.
  selection=BASE/(OLD+'-candidates')/'selection.json';assert digest(selection.read_bytes())==cp[str(selection.relative_to(ROOT))]
  ground=next(v for u,v in read(selection)['candidates'] if u==r['uid'])
  candidate_pairs.append((r['uid'],ground));refs.extend([f/'result.json',f/'failure.json',selection])
 name=BATCH+'-candidates';tool=HERE/'selected_original_bounded_candidate_batch_v5.py'
 save(doc/'selection.json',dict(candidates=candidate_pairs,capture=OLD+'-capture',installationApproved=False))
 command=[sys.executable,str(tool),'--batch',name,'--capture',OLD+'-capture','--inventory','government-xl-after-kam-fat-current-inventory-v1-20261022','--workers','2',*[v for uid,g in candidate_pairs for v in ['--candidate',uid+','+g]]]
 with(doc/'candidates.log').open('w')as log:code=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT).returncode
 assert code==0,'Corrected candidate run failed; retain logs, inspect exact stage'
 result,_=authenticate(BASE/name);refs.extend([tool,BASE/name/'result.json'])
 summary=dict(uids=[p[0] for p in candidate_pairs],candidateJobId=result['jobId'],rows=result['rows'],newlyInstalled=0,installationApproved=False,publication=False,sourceGeometryChanges=0,scriptExternalAICalls=0,qualification='Preserve the validated parent-edge return; every source/terrain/current-neighbour/browser gate remains separate. No blanket failure waiver or source geometry edits.')
 save(doc/'summary.json',summary)
 module('parent_return_followthrough_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'validated-parent-return-current-followthrough',refs,summary)
if __name__=='__main__':main()
