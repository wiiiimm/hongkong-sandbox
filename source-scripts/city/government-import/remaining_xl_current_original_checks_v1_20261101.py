"""Reusable leased current-scene checks for exact unfinished fixed-XL originals.

Reuses cached source bytes, actual renderer and existing identity checks. No
geometry edits, publication, optimisation or automatic terminal classification.
"""
import argparse,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations
from require_remaining_xl import require_remaining
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['batch','capture','installed']:p.add_argument('--'+key,required=True)
 p.add_argument('--uid',action='append',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert a.batch.startswith('government-xl-')and '/'not in a.batch
 assert 0<len(a.uid)==len(set(a.uid))<=40
 local=HERE/'local'/a.batch;lease=local/'reservation.json'
 # Authenticate exact cached selection and current installation count before CPU work.
 for folder in [BASE/a.capture,BASE/a.installed]:
  _,pins=authenticate(folder)
  file=folder/('selection.json.gz'if folder==BASE/a.capture else'full-xl-current-count.json')
  assert digest(file.read_bytes())==pins[str(file.relative_to(ROOT))]
 sources={r['uid']:r for r in read(BASE/a.capture/'selection.json.gz')['rows']}
 for uid in a.uid:require_remaining(BASE/a.installed/'full-xl-current-count.json',uid,sources[uid]['sourceSHA256'])
 if not a.owned:
  assert not local.exists()
  c=reservations.claim('remaining-xl-current-original-'+str(uuid.uuid4()),['building:'+u for u in sorted(a.uid)]+['immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert c['ok'],c
  execute_reserved(c['reservation'],lease,[sys.executable,__file__,*sys.argv[1:],'--owned']);return
 assert reservations.owns(read(lease))
 jobs=[]
 steps=[('selection','selected_original_refresh_selection_v1.py',['--capture',a.capture,*[v for u in a.uid for v in ['--uid',u]]]),('runtime','selected_original_current_capture_v3.py',['--capture',a.batch+'-selection',*[v for u in a.uid for v in ['--uid',u]]]),('identity','selected_original_identity_v3.py',['--capture',a.batch+'-runtime'])]
 for step,tool,args in steps:
  assert reservations.owns(read(lease))
  with (local/(step+'.log')).open('w')as log:
   subprocess.run([sys.executable,str(HERE/tool),'--batch',a.batch+'-'+step,*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=10800)
  r=read(BASE/(a.batch+'-'+step)/'result.json');jobs.append(dict(phase=step,batch=a.batch+'-'+step,jobId=r['jobId']));print(step+' complete',flush=True)
 save(local/'completed.json',dict(uids=sorted(a.uid),jobs=jobs,sourceGeometryChanges=0,installationApproved=False,publication=False))
if __name__=='__main__':main()
