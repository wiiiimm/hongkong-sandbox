"""Measure actual neighbour projections against both unchanged museum sources."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-science-history-neighbour-projection-v1-20261016'
DOC=BASE/BATCH
names=['government-xl-science-history-basic-ground-capture-v1-20261016','government-xl-science-history-highest-surface-v2-20261016','government-xl-science-history-private-neighbours-v1-20261016']
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in names:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for q in r['evidenceRefs']:
    assert q['path'] not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 geometry=HERE/'local'/names[1]/'runtime-geometry.json.gz';refs.append(geometry);pieces=[];faces=0
 for r in read(geometry)['rows']:
  t=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];faces+=len(t);pieces.extend(shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in t)
 projection=shapely.union_all(pieces);excluded=projection.buffer(.01,join_style='mitre')
 actors=BASE/names[0]/'basic-actors.json.gz';flagfile=BASE/names[2]/'summary.json';refs.extend([actors,flagfile]);flagged={r['uid'] for r in read(flagfile)['flagged']};rows=[]
 for r in read(actors)['rows']:
  if r['uid'] not in flagged:continue
  t=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];p=shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in t]);safe=p.buffer(.01,join_style='mitre').difference(excluded);b=r['building']
  rows.append(dict(uid=r['uid'],kind=b.get('kind'),actualFaces=len(t),actualProjectionM2=p.area,overlapMuseumsM2=p.intersection(projection).area,sourceDisjointPreservableM2=safe.area,sourceDisjointGeoJSON=shapely.to_geojson(safe),estimatedOpenSided=b.get('kind')=='roof' and b.get('baseSource')=='terrain-estimated',qualification='Projection scope only; no foundation, placement or installation approval.'))
 assert {r['uid'] for r in rows}==flagged
 DOC.mkdir();summary=dict(rows=rows,completeMuseumFaces=faces,fullAcceptance=False,newlyInstalled=0,liveChanges=False);save(DOC/'summary.json',summary)
 result=module('projection_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'actual-neighbour-and-two-original-source-projection-scope-v1',list(dict.fromkeys(refs)),dict(uids=sorted(flagged),fullAcceptance=False,newlyInstalled=0))
 print(dict(jobId=result['jobId'],rows=[{k:v for k,v in r.items() if k!='sourceDisjointGeoJSON'} for r in rows]),flush=True)
if __name__=='__main__':main()
