"""Run the existing original wall-contact rule on exact saved Opus sources."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from require_remaining_xl import require_remaining
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-exact-wall-interfaces-v1-20261017';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-opus-assembly-layers-v1-20261016'
def main():
 assert not DOC.exists();count=BASE/'government-xl-sham-shui-po-pool-original-installed-v1-20261017/full-xl-current-count.json';require_remaining(count,'landsd/322573:0','e3c4ad4fff2acda8844233c83b6885dbbd73c1da9acb0a0efc7ec9778f57d764')
 r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={q['path']:q['sha256']for q in r['evidenceRefs']};inp=read(PRIOR/'input.json');paths=[PRIOR/'input.json',ROOT/inp['geometryPath'],ROOT/inp['actorsPath']]
 for p in paths:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 DOC.mkdir();save(DOC/'input.json',inp);tool=HERE/'opus_exact_wall_interfaces_v1_20261017.mjs'
 with(DOC/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 out=read(DOC/'interfaces.json.gz')
 for p,h in out['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;paths.append(ROOT/p)
 result=module('opus_interface_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'existing-exact-original-wall-rule-source-diagnostic-v1',[Path(__file__),tool,PRIOR/'result.json',count,HERE/'require_remaining_xl.py',*paths],dict(uids=['landsd/322573:0','landsd/319559:0','landsd/248432:0'],fullAcceptance=False,newlyInstalled=0));print(dict(jobId=result['jobId'],summary=read(DOC/'summary.json')),flush=True)
if __name__=='__main__':main()
