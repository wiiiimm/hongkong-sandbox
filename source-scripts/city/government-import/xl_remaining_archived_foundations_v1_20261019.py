"""Inspect complete foundations from authenticated archived original captures.
Historical diagnostic only: this does not approve current placement or publication.
"""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
CAP=BASE/'government-xl-next-twenty-current-terrain-v1-20261018'
BATCH='government-xl-remaining-archived-foundations-v1-20261019'
DOC=BASE/BATCH
UIDS=['landsd/233227:0','landsd/64856:0','landsd/232240:0']
def main():
 assert not DOC.exists()
 receipt=read(CAP/'result.json')
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 geometry=HERE/'local'/CAP.name/'runtime-geometry.json.gz'
 selection=CAP/'selection.json.gz'
 refs=[Path(__file__),CAP/'result.json',geometry,selection,HERE/'xl-final-script-pass.py']
 pins={r['path']:r['sha256']for r in receipt['evidenceRefs']}
 for p in [geometry,selection,HERE/'xl-final-script-pass.py']:
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 gs={x['uid']:x for x in read(geometry)['rows']};ss={x['uid']:x for x in read(selection)['rows']}
 checker=module('archived_foundation_checker',HERE/'xl-final-script-pass.py');summaries=[]
 for uid in UIDS:
  g=gs[uid];r=ss[uid];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=r['source']['building']
  result=checker.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));save(DOC/(uid.replace('/','-').replace(':','-')+'.json'),result)
  summaries.append(dict(uid=uid,foundation={k:v for k,v in result.items()if k!='components'}));print(uid,summaries[-1],flush=True)
 save(DOC/'summary.json',dict(rows=summaries,historicalTerrainOnly=True,currentPlacementApproved=False,installationApproved=False,sourceGeometryChanges=0))
 frozen=module('archived_foundation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'remaining-original-archived-foundations',refs,dict(uids=UIDS,rows=summaries,historicalTerrainOnly=True,installationApproved=False))
 print(frozen['jobId'],flush=True)
if __name__=='__main__':main()
