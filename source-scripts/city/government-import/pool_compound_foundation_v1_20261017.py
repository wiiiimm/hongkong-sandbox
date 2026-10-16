"""Whole original pool/tower foundation diagnostic against unchanged source support."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-sham-shui-po-pool-compound-foundation-v1-20261017'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-sham-shui-po-pool-original-group-v1-20261016'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256'];refs.append(ROOT/q['path'])
 path=HERE/'local'/PRIOR.name/'runtime-geometry.json.gz';geometries=read(path)['rows'];selection=read(PRIOR/'selection.json.gz')['rows']
 triangles={g['uid']:np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)] for g in geometries}
 ground=np.concatenate([np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3) for g in geometries]);f=module('pool_foundation',HERE/'xl-final-script-pass.py');rows=[];DOC.mkdir()
 for row in selection:
  uid=row['uid'];support=ground if uid=='landsd/265480:0' else np.concatenate([ground,triangles['landsd/265480:0']]);b=row['source']['building'];proof=f.foundation_context(triangles[uid],support,Polygon(b['rings'][0],b['rings'][1:]))
  rows.append(dict(uid=uid,foundation=proof,strictFoundationAccepted=proof['completeTerrainTriangles']==len(triangles[uid]) and not proof['fullyBuriedUpwardTriangles'] and proof['fullyBuriedAreaFraction']==0))
 save(DOC/'summary.json',dict(rows=rows,mode='saved-loader-world-only',fullAcceptance=False))
 refs += [path,HERE/'xl-final-script-pass.py']
 out=module('pool_foundation_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-pool-compound-foundation-diagnostic-v1',list(dict.fromkeys(refs)),dict(uids=[r['uid'] for r in rows],rows=rows,fullAcceptance=False,newlyInstalled=0))
 print(dict(jobId=out['jobId'],rows=rows),flush=True)
if __name__=='__main__':main()
