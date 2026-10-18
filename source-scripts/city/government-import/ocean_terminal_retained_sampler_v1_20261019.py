"""Authenticate exact structural evidence and run actual publisher-order sampler checks."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ocean-terminal-retained-sampler-v1-20261019';DOC=BASE/BATCH
SRC=BASE/'government-xl-ocean-terminal-retained-parent-equivalence-v1-20261019'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json'];pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 tool=HERE/'ocean_terminal_retained_sampler_v1_20261019.mjs';refs.extend([tool,HERE.parent/'island-detail-integration/publish.py']);pins.update({str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs})
 save(DOC/'input.json',dict(inputHashes=pins,plan='docs/astra-city/government-import/government-xl-ocean-terminal-private-ground-v2-20261018/terrain-candidates.json',inventory='docs/astra-city/government-import/government-xl-ocean-terminal-current-scope-v1-20261019/complete-bounds.json.gz'))
 subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);out=read(DOC/'sampler.json')
 for p,h in {**pins,**out['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('ocean_sampler_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'ocean-terminal-retained-publisher-order-sampler',list(dict.fromkeys(refs)),dict(uids=['landsd/205767:0'],samplerCorroborationPassed=out['passed'],points=out['uniqueProbePoints'],errors=len(out['errors']),differences=len(out['differences']),installationApproved=False))
if __name__=='__main__':main()
