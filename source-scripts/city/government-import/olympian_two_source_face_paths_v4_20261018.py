"""Authenticate inputs and record exact original source-face connection diagnostics."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-olympian-two-exact-start-faces-v1-20261018';INPUT=BASE/'government-xl-olympian-two-canonical-contacts-v1-20261018';BATCH='government-xl-olympian-two-source-face-paths-v4-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 DOC.mkdir();tool=HERE/'olympian-two-source-face-paths-v4-20261018.mjs';subprocess.run(['node',str(tool),str(INPUT),str(DOC/'paths.json.gz'),str(PRIOR/'exact-start-faces.json.gz')],cwd=ROOT,check=True)
 rows=read(DOC/'paths.json.gz')['rows'];save(DOC/'summary.json',dict(rows=[{k:v for k,v in row.items()if k!='details'}for row in rows],fullAcceptance=False))
 refs=[Path(__file__),tool,PRIOR/'result.json',HERE/'support-contact.mjs',*[ROOT/p for p in pins]]
 out=module('olympian_face_paths_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-exact-original-lower-region-shared-edge-contact-context-v4',list(set(refs)),dict(uids=[r['uid']for r in rows],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
