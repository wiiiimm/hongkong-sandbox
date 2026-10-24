"""Strict canonical support on actual rendered terrain and unchanged assembly."""
import subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-runtime-support-v2-20261018';DOC=BASE/BATCH
CAP=BASE/'government-xl-west-wing-group-four-world-v1-20261018';GROUND=BASE/'government-xl-west-wing-exterior-capture-v2-20261018'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,GROUND]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 ground=read(GROUND/'after-ground.json.gz')['completeRelevantDrawnTriplets'];terrain=[[t[:3],t[3:6],t[6:]]for t in ground]
 save(DOC/'input.json.gz',dict(worlds=read(CAP/'worlds.json.gz'),terrain=terrain))
 tool=HERE/'west_wing_runtime_support_v1_20261018.mjs'
 with(DOC/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(DOC)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 rows=read(DOC/'checks.json.gz')['rows'];summary=[dict(uid=r['uid'],mode=r['mode'],passed=r['interface']['passed'],samples=r['interface']['samples'],unresolved=len(r['unresolved']),reasons=r['reasons'])for r in rows];save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins);refs.extend([tool,*[HERE/n for n in ['support-interface.mjs','source-face-query.mjs','support-contact.mjs','triangle-point-index.mjs']]])
 out=module('west_runtime_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'west-wing-all-four-world-runtime-canonical-support-v1',list(dict.fromkeys(refs)),dict(uids=sorted({r['uid']for r in rows}),summary=summary,fullAcceptance=False,publication=False));print(out['jobId'],flush=True)
if __name__=='__main__':main()
