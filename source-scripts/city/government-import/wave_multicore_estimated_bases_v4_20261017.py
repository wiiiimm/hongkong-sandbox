"""Measure complete rendered terrain under three unsurveyed BASIC forms; private proposals only."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-wave-verdant-multicore-ground-capture-v4-20261017';BATCH='government-xl-wave-multicore-estimated-bases-v4-20261017';DOC=BASE/BATCH
UIDS=['landsd/207423:0','landsd/207682:0','landsd/268957:0']
def polygons(g):
 if g.geom_type=='Polygon':yield g
 elif hasattr(g,'geoms'):
  for part in g.geoms:yield from polygons(part)
def measure(tri,poly):
 x0,z0,x1,z1=poly.bounds;ids=np.flatnonzero((tri[:,:,0].max(1)>=x0)&(tri[:,:,0].min(1)<=x1)&(tri[:,:,2].max(1)>=z0)&(tri[:,:,2].min(1)<=z1));records=[];heights=[];pieces=[];zeros=[]
 for i in ids:
  t=tri[i];a,b,c=t;u=b-a;v=c-a;det=u[0]*v[2]-u[2]*v[0]
  if abs(det)<1e-12:zeros.append(int(i));continue
  clipped=Polygon(t[:,[0,2]]).intersection(poly)
  for part in polygons(clipped):
   if part.area==0:continue
   coords=np.array([q for ring in [part.exterior,*part.interiors]for q in ring.coords]);d=coords-a[[0,2]];s=(d[:,0]*v[2]-d[:,1]*v[0])/det;k=(u[0]*d[:,1]-u[2]*d[:,0])/det;h=a[1]+s*u[1]+k*v[1];heights.extend(h.tolist());pieces.append(part);records.append(dict(face=int(i),areaM2=part.area,clippedXZ=coords.tolist(),heights=h.tolist()))
 assert heights
 union=unary_union(pieces);return dict(minimum=min(heights),maximum=max(heights),footprintAreaM2=poly.area,uncoveredAreaM2=poly.difference(union).area,overlapAreaM2=sum(p.area for p in pieces)-union.area,records=records,verticalOrDegenerateBroadphaseFaces=zeros)
def main():
 assert not DOC.exists();r=read(CAP/'result.json');refs=[Path(__file__),CAP/'result.json'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';forms={};live=set()
 for url in read(manifest)['officialModelCatalogues']:live.update(m['uid']for m in read(ROOT/'3d-viewer'/url)['models'])
 assert not set(UIDS)&live
 for tile in read(manifest)['tiles']:
  path=ROOT/'3d-viewer'/tile['url']
  for b in read(path)['buildings']:
   if b['uid']in UIDS:forms[b['uid']]=b;refs.append(path)
 assert set(forms)==set(UIDS)
 grounds={mode:np.array(read(CAP/(mode+'-ground.json.gz'))['completeRelevantDrawnTriplets']).reshape(-1,3,3)for mode in ['before','after']};rows=[]
 for uid,b in forms.items():
  assert b['baseHeightHKPD']is None and b['topHeightHKPD']is None and b['baseSource']=='terrain-estimated'and b['heightSource']=='estimated'and not b.get('modelGeometry')
  poly=Polygon(b['rings'][0],b['rings'][1:]);measurements={mode:measure(t,poly)for mode,t in grounds.items()};after=measurements['after'];relief=after['maximum']-after['minimum'];proposal=dict(uid=uid,sourceBefore=b,previousBase=b['base'],proposedBase=after['minimum'],height=b['height'],terrainReliefM=relief,roofClearanceAboveMaximumTerrainM=b['height']-relief,uniformBaseCandidate=after['uncoveredAreaM2']<1e-8 and abs(after['overlapAreaM2'])<1e-8 and relief<b['height']-1.8,officialFieldsChanged=False,originalGovernmentGeometryChanged=False,publication=False);rows.append(proposal);save(DOC/(uid.split('/')[1]+'-terrain.json'),measurements);print({k:v for k,v in proposal.items()if k!='sourceBefore'},flush=True)
 save(DOC/'proposals.json',dict(rows=rows,fullAcceptance=False,qualification='Deterministic footprint clipping against actual drawn terrain; uniform base update nominated only when full coverage, no overlapping projected terrain and at least 1.8m clearance remain. No live files changed. Rendered BASIC geometry and neighbour checks remain mandatory.'))
 out=module('wave_base_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unsurveyed-basic-private-base-estimate-proposals-v1',list(set(refs)),dict(uids=UIDS,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
