"""Measure exact finite source-face offsets; do not change support tolerances."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-nearest-source-faces-v1-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-parkview-three-four-world-contacts-v2-20261020'
assert not DOC.exists();receipt=read(SRC/'result.json')
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
pins={e['path']:e['sha256']for e in receipt['evidenceRefs']}
for n in ['input.json.gz','contacts.json.gz']:
 p=SRC/n;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
DOC.mkdir();tool=HERE/'parkview-nearest-source-faces-v1-20261020.mjs';subprocess.run(['node',str(tool),str(SRC.relative_to(ROOT)),str((DOC/'nearest.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
r=read(DOC/'nearest.json.gz');refs=[Path(__file__),SRC/'result.json']
for p,h in r['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
rows=[{k:v for k,v in x.items()if k!='points'}for x in r['rows']]
module('parkview_nearest_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-finite-original-face-distances',refs,dict(uids=[r['uid']for r in rows],rows=rows,installationApproved=False,geometryChanges=0))
