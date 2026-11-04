"""Whole-source foundation diagnosis on the forty captured current terrains."""
import numpy as np
from pathlib import Path
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
CAP=BASE/'government-xl-ronsdale-inset-runtime-v1-20261022'
BATCH='government-xl-ronsdale-inset-foundations-v1-20261022'
DOC=BASE/BATCH

def main():
 assert not DOC.exists()
 receipt=read(CAP/'result.json');pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 runtime=read(HERE/'local'/CAP.name/'runtime-geometry.json.gz')['rows'];selection=read(CAP/'selection.json.gz')['rows'];lookup={r['uid']:r for r in runtime};errors={r['uid']:r['error'] for r in read(CAP/'metrics.json')['rows'] if r.get('error')};assert not(set(lookup)&set(errors));assert set(lookup)|set(errors)=={r['uid']for r in selection}
 final=module('next_five_foundation',HERE/'xl-final-script-pass.py');summary=[]
 for row in selection:
  uid=row['uid']
  if uid in errors:
   result=dict(uid=uid,status='runtime-blocked',reason=errors[uid],foundationChecked=False,installationApproved=False);summary.append(result);save(DOC/(uid.split('/')[1]+'.json'),result);print(result,flush=True);continue
  g=lookup[uid];assert g['sourceSHA256']==row['sourceSHA256'];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);assert len(tri)==row['triangles'];b=row['source']['building']
  foundation=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));save(DOC/(uid.split('/')[1]+'.json'),dict(uid=uid,sourceSHA256=row['sourceSHA256'],foundation=foundation,installationApproved=False))
  result=dict(uid=uid,**{k:v for k,v in foundation.items()if k!='components'});summary.append(result);print(result,flush=True)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 save(DOC/'summary.json',dict(rows=summary,installationApproved=False))
 module('next_five_foundation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'forty-current-terrain-complete-foundation-diagnostics',[Path(__file__),CAP/'result.json',HERE/'xl-final-script-pass.py',*[ROOT/p for p in pins]],dict(uids=[r['uid']for r in selection],rows=summary,installationApproved=False))
if __name__=='__main__':main()
