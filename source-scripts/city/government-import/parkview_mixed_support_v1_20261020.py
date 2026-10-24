"""Check archived literal complete ground plus podium; fresh placement still required."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-mixed-support-v1-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-star-parkview-support-v1-20261020'
assert not DOC.exists();receipt=read(SRC/'result.json')
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
p=HERE/'local'/SRC.name/'runtime-geometry.json.gz';pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
DOC.mkdir();tool=HERE/'parkview-mixed-support-v1-20261020.mjs';subprocess.run(['node',str(tool),str(p.relative_to(ROOT)),str((DOC/'contacts.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
r=read(DOC/'contacts.json.gz');refs=[Path(__file__),SRC/'result.json']
for p,h in r['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
rows=[{k:v for k,v in x.items()if k not in ['mapped','rawInterface']}for x in r['rows']]
module('parkview_mixed_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'archived-literal-mixed-terrain-podium-diagnostic',refs,dict(uids=[r['uid']for r in rows],rows=rows,scope='Historical exact runtime capture; no fresh current-map placement approval.',installationApproved=False))
