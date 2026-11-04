"""Diagnose saved parent-capture overlay failures; no geometry edits or approvals."""
from pathlib import Path
from collections import Counter
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from inherited_parent_coverage_v1 import qualify
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
COHORT=BASE/'government-xl-rest-recovered-current-supervisor-v1-20261022-chunk-01-candidates'
BATCH='government-xl-recovered-parent-coverage-triage-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists()
 refs=[Path(__file__),HERE/'inherited_parent_coverage_v1.py',HERE/'float32_coverage.py',COHORT/'result.json'];out=[]
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  receipt=read(COHORT/'result.json')
  assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for row in receipt['rows']:
   if row['status']!='terrain-investigation' or row.get('reasons')!=['']:continue
   name=row['batches']['terrain'];folder=BASE/name;r=read(folder/'result.json')
   assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   pins={e['path']:e['sha256'] for e in r['evidenceRefs']};p=HERE/'local'/name/'parent.json';sp=folder/'scope.json'
   for f in [p,sp]:assert digest(f.read_bytes())==pins[str(f.relative_to(ROOT))];refs.append(f)
   refs.append(folder/'result.json');cap=read(p)
   changed=[path for path,sha in cap['inputHashes'].items() if digest((ROOT/path).read_bytes())!=sha]
   record=dict(uid=row['uid'],terrainBatch=name,changedParentCaptureInputs=changed,currentParentInputsVerified=not changed,installationApproved=False)
   assert not changed, 'Refresh parent capture rather than reuse changed inputs'
   tri=np.asarray(cap['triangles']);record['parentMinimumHeight']=float(tri[:,:,1].min())
   try:
    record['coverage']=qualify(tri,read(sp)['bounds'])
    record['status']='existing-parent-below-clamp' if record['parentMinimumHeight']<1.2 else 'eligible-for-v6-terrain-followthrough'
   except AssertionError as exc:
    record.update(status='material-parent-coverage-investigation',reason=str(exc))
   save(doc/(row['uid'].split('/')[1]+'.json'),record);out.append(record)
   print(dict(uid=record['uid'],status=record['status'],minimumHeight=record['parentMinimumHeight']),flush=True)
 result=dict(uids=[r['uid'] for r in out],rows=out,counts=dict(Counter(r['status'] for r in out)),newlyInstalled=0,installationApproved=False,publication=False,sourceGeometryChanges=0,scriptExternalAICalls=0,qualification='Saved exact parent captures retain unchanged current input bindings. Existing coverage/clamp policies only; no waiver, geometry edit, installation or permanent rejection.')
 save(doc/'summary.json',result)
 module('parent_coverage_triage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'saved-current-parent-coverage-triage',refs,result)
if __name__=='__main__':main()
