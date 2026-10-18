"""Bind unchanged original interface diagnostics to completed source checks."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';SRC=BASE/'government-xl-kai-tak-cruise-original-component-checks-v2-20261019';BATCH='government-xl-kai-tak-cruise-support-layers-v1-20261019';DOC=BASE/BATCH
def main():
 assert not DOC.exists();r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json'];pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 subprocess.run(['node',str(HERE/'kai_tak_cruise_support_layers_v1_20261019.mjs'),str(SRC.relative_to(ROOT)),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True)
 x=read(DOC/'layers.json.gz')
 for p,h in x['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 summary=[dict(uid=r['uid'],counts=r['counts'],rawFailed=len(r['failures']))for r in x['rows']]
 module('kai_layer_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kai-tak-cruise-complete-original-contact-layer-diagnostics',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in x['rows']],rows=summary,installationApproved=False))
if __name__=='__main__':main()
