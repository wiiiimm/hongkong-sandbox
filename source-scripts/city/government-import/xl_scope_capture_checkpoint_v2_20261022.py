"""Read back completed XL diagnostics, separating historical inputs from current evidence."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-scoped-feature-current-checkpoint-v2-20261022'
NAMES=[
 'government-xl-rest-recovered-current-supervisor-v1-20261022',
 'government-xl-rest-recovered-current-supervisor-v1-20261022-chunk-01-candidates',
 'government-xl-runtime-fit-99482-scoped-current-selection-v1-20261022',
 'government-xl-runtime-fit-99482-scoped-current-capture-v3-20261022',
 'government-xl-runtime-fit-99482-scoped-local-terrain-v6-20261022',
]
def main():
 doc=BASE/BATCH
 assert not doc.exists()
 refs=[Path(__file__)];out=[];cache={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   path=BASE/name/'result.json';r=read(path)
   assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   changed=[];matched=0
   for e in r['evidenceRefs']:
    p=ROOT/e['path'];key=(e['path'],e['sha256'])
    if key not in cache: cache[key]=p.exists() and digest(p.read_bytes())==e['sha256']
    if cache[key]:matched+=1
    else:changed.append(e['path'])
   out.append(dict(batch=name,jobId=r['jobId'],exactNeonReadback=True,currentMatchingReferences=matched,changedOrMissingReferences=changed,currentInputSetVerified=not changed))
   refs.append(path)
 # Source capture and selection must remain current; older finished cohort is historical after resolver integration.
 assert all(r['currentInputSetVerified'] for r in out[2:])
 rows=read(BASE/NAMES[1]/'summary.json')['rows']
 from collections import Counter
 result=dict(uids=sorted({u for n in NAMES for u in read(BASE/n/"result.json")["uids"]}),rows=out,cohortCounts=dict(Counter(r['status'] for r in rows)),cohortProcessed=len(rows),newlyInstalled=0,installationApproved=False,publication=False,aiGeometryModelling=False,scriptExternalAICalls=0,qualification='Exact completed Neon receipts read back. Historical dependency changes are explicit, never reused as fresh physical approval. Production Lookout capture succeeds; private terrain stops at unchanged near-water clamp.')
 save(doc/'summary.json',result)
 module('scope_capture_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'xl-current-source-capture-checkpoint',refs,result)
 print(dict(cohortProcessed=len(rows),counts=result['cohortCounts'],jobsVerified=len(out),currentCapturesVerified=True),flush=True)
if __name__=='__main__':main()
