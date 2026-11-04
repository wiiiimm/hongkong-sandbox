"""Compare the entire original Opus pair against unblended official terrain."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-pair-original-ground-v1-20261016';DOC=BASE/BATCH
PAIR=BASE/'government-xl-opus-pair-foundation-v1-20261016';TERRAIN=BASE/'government-xl-opus-two-sheet-terrain-v1-20261016'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 for folder in [PAIR,TERRAIN]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json')
  for ref in r['evidenceRefs']:
   p,h=ref['path'],ref['sha256'];assert p not in pins or pins[p]==h;pins[p]=h
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 f=module('opus_pair_original',HERE/'xl-final-script-pass.py');ground=np.concatenate([f.s.context.triangles(ROOT/p)for p in read(TERRAIN/'summary.json')['terrainPaths']]);geometry=HERE/'local'/PAIR.name/'runtime-geometry.json.gz';models=read(geometry)['rows'];selection=read(PAIR/'selection.json.gz')['rows'];forms={r['uid']:r['source']['building']for r in selection};rows=[];alltri=[]
 for g in models:
  t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];alltri.append(t);b=forms[g['uid']];foundation=f.foundation_context(t,ground,Polygon(b['rings'][0],b['rings'][1:]));rows.append(dict(uid=g['uid'],foundation=foundation))
 polygon=shapely.union_all([Polygon(b['rings'][0],b['rings'][1:])for b in forms.values()]);foundation=f.foundation_context(np.concatenate(alltri),ground,polygon);summary=dict(rows=rows,compoundFoundation=foundation,originalTerrainFaces=len(ground),fullAcceptance=False)
 DOC.mkdir();save(DOC/'summary.json',summary);refs += [geometry,PAIR/'selection.json.gz',TERRAIN/'summary.json',HERE/'xl-final-script-pass.py',Path(f.s.context.__file__),Path(f.s.context.shared.__file__)]
 result=module('opus_pair_original_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'opus-complete-pair-unblended-original-ground-v1',list(dict.fromkeys(refs)),dict(uids=sorted(forms),summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=result['jobId'],foundation=foundation),flush=True)
if __name__=='__main__':main()
