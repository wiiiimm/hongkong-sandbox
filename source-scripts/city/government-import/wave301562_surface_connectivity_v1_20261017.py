"""Record exact source topology for the non-XL companion preventing Wave terrain acceptance."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave-four-world-paths-v1-20261017';BATCH='government-xl-wave301562-surface-connectivity-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={};refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 worlds=read(PRIOR/'worlds.json.gz');save(DOC/'input.json.gz',dict(worlds={m:{u:t for u,t in w.items()if u in ['landsd/301562:0','landsd/301560:0']}for m,w in worlds.items()}));tool=HERE/'wave301562_surface_connectivity_v1_20261017.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);out=read(DOC/'connectivity.json.gz')
 for p,h in out['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 refs.append(tool);result=module('wave_companion_connectivity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-companion-to-existing-contact-topology-v1',list(set(refs)),dict(uids=['landsd/301562:0','landsd/301560:0'],fullAcceptance=False,newlyInstalled=0));print(result['jobId'],flush=True)
if __name__=='__main__':main()
