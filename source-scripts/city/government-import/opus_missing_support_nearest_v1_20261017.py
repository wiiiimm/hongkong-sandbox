"""Measure unresolved Opus points against original surfaces; no geometry edits."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from fu_tor_loy_nearest_interfaces_v1_20261017 import nearest
from require_remaining_xl import require_remaining
BASE=ROOT/'docs/astra-city/government-import'
PRIOR=BASE/'government-xl-opus-exact-wall-interfaces-v1-20261017'
BATCH='government-xl-opus-missing-support-nearest-v1-20261017'
DOC=BASE/BATCH

def main():
 assert not (DOC/'result.json').exists()
 count=BASE/'government-xl-sham-shui-po-pool-original-installed-v1-20261017/full-xl-current-count.json'
 require_remaining(count,'landsd/322573:0','e3c4ad4fff2acda8844233c83b6885dbbd73c1da9acb0a0efc7ec9778f57d764')
 r=read(PRIOR/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for ref in r['evidenceRefs']: assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
 inp=read(PRIOR/'input.json')
 geo=read(ROOT/inp['geometryPath'])['rows']
 surfaces={g['uid']:np.array(g['position']).reshape(-1,3)[np.array(g['index']).reshape(-1,3)] for g in geo}
 output=[]
 for row in read(PRIOR/'interfaces.json.gz')['rows']:
  for f in row['unresolved']:
   if f.get('gap') is not None: continue
   p=np.array(f['position']); measurements=[]
   for uid,tri in surfaces.items():
    i,q,d=nearest(p,tri)
    incident=np.array([face['vertices'] for face in f['sourceFaces']])
    incident_distance=nearest(q,incident)[2] if len(incident) else None
    measurements.append(dict(supportUid=uid,faceIndex=i,nearestPoint=q.tolist(),distanceM=d,incidentSourceDistanceM=incident_distance,withinHalfMetre=d<=.5))
   output.append(dict(uid=row['uid'],position=f['position'],surfaces=measurements))
 assert len(output)==4
 DOC.mkdir(exist_ok=True)
 save(DOC/'measurements.json',dict(rows=output,fullAcceptance=False,newlyInstalled=0,qualification='Nearest-surface diagnostic only; distance alone is not support acceptance. Source geometry is unchanged.'))
 refs=[Path(__file__),HERE/'fu_tor_loy_nearest_interfaces_v1_20261017.py',HERE/'require_remaining_xl.py',count,PRIOR/'result.json']
 refs += [ROOT/x['path'] for x in r['evidenceRefs']]
 out=module('opus_missing_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-missing-support-nearest-v1',refs,dict(uids=['landsd/248432:0','landsd/319559:0','landsd/322573:0'],fullAcceptance=False,newlyInstalled=0))
 print(dict(jobId=out['jobId'],rows=output),flush=True)
if __name__=='__main__': main()
