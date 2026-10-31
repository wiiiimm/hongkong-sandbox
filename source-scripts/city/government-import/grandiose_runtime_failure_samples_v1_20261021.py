from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-grandiose-private-runtime-v1-20261021';BATCH='government-xl-grandiose-runtime-failure-samples-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
for e in r['evidenceRefs']:
 p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
DOC.mkdir();tool=HERE/'grandiose_runtime_failure_samples_v1_20261021.mjs';subprocess.run(['node',str(tool),str((DOC/'samples.json').relative_to(ROOT))],cwd=ROOT,check=True)
data=read(DOC/'samples.json');summary=dict(uids=[x['uid']for x in data['rows']],rows=[dict(uid=x['uid'],checks=x['checks'],minSurfaceGap=x['minSurfaceGap'],failureCounts={k:sum(f['kind']==k for f in x['failures'])for k in ['vertex','centroid','edge']})for x in data['rows']],installationApproved=False);save(DOC/'summary.json',summary);refs.extend([tool,ROOT/'3d-viewer/city/native-terrain.js']);module('runtime_sample_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-production-runtime-failure-sample-attribution',refs,summary);print(summary)
