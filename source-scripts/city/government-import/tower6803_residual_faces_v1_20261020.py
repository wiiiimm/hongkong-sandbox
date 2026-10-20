from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tower6803-residual-faces-v1-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-tower6803-original-wall-paths-v1-20261020';LOCAL=HERE/'local'/SRC.name
assert not DOC.exists();r=read(SRC/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};inputs=[LOCAL/'original.json.gz',SRC/'original-verified.json.gz'];refs=[Path(__file__),SRC/'result.json']
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
for p in inputs:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
tool=HERE/'tower6803_residual_faces_v1_20261020.mjs';DOC.mkdir();subprocess.run(['node',str(tool),*[str(p)for p in inputs],str(DOC/'faces.json.gz')],cwd=ROOT,check=True);rows=read(DOC/'faces.json.gz')['rows'];s=dict(uid='landsd/6803:0',residual=len(rows),directFiniteContacts=sum(bool(x['directFiniteSupportFaces'])for x in rows),noDirectContact=sum(not x['directFiniteSupportFaces']for x in rows),originalSourceOnly=True,installationApproved=False);save(DOC/'summary.json',s)
refs.extend([tool,HERE/'source-face-query.mjs',HERE/'triangle-point-index.mjs',ROOT/'3d-viewer/vendor/three.module.js'])
module('tower_residual_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-residual-source-face-contacts',refs,dict(uids=['landsd/6803:0'],summary=s,installationApproved=False))
