"""Continuous upper-envelope comparison along exact projected original wall edges."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import LineString
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from source_surface_inset import plane
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-vertical-edge-terrain-v4-20261019';DOC=BASE/BATCH;SRC=BASE/'government-xl-lai-chi-kok-vertical-context-v1-20261019'
def surface(tris):
 ps=shapely.polygons(tris[:,:,[0,2]]);ok=shapely.area(ps)>1e-10;return tris[ok],ps[ok],shapely.STRtree(ps[ok])
def intervals(a,b,s):
 tris,ps,tree=s;d=b-a;dd=d@d;line=LineString([a,b]);out=[]
 for j in tree.query(line,predicate='intersects'):
  q=line.intersection(ps[j]);xy=shapely.get_coordinates(q)
  if len(xy)<2:continue
  ts=(xy-a)@d/dd;lo=max(0,float(ts.min()));hi=min(1,float(ts.max()))
  if hi<=lo:continue
  p=plane(tris[j]);out.append((lo,hi,float(d@p[:2]),float(a@p[:2]+p[2]),int(j)))
 return out
def compare(left,right):
 cuts={0.,1.}
 for rows in [left,right]:
  for a in rows:cuts.update(a[:2])
  for i,a in enumerate(rows):
   for b in rows[i+1:]:
    if a[2]==b[2]:continue
    t=(b[3]-a[3])/(a[2]-b[2])
    if max(a[0],b[0])<t<min(a[1],b[1]):cuts.add(t)
 cuts=sorted(cuts);out=[];missing=0
 for lo,hi in zip(cuts,cuts[1:]):
  if hi<=lo:continue
  mid=(lo+hi)/2;ls=[r for r in left if r[0]<=mid<=r[1]];rs=[r for r in right if r[0]<=mid<=r[1]]
  if not ls or not rs:missing+=hi-lo;out.append(dict(interval=[lo,hi],missingOriginal=not ls,missingCandidate=not rs));continue
  a=max(ls,key=lambda r:r[2]*mid+r[3]);b=max(rs,key=lambda r:r[2]*mid+r[3]);delta=[(b[2]-a[2])*t+b[3]-a[3] for t in [lo,hi]];out.append(dict(interval=[lo,hi],originalFace=a[4],candidateFace=b[4],candidateMinusOriginalAtEnds=delta))
 values=[v for r in out for v in r.get('candidateMinusOriginalAtEnds',[])];return dict(missingFraction=missing,maximumRise=max(values)if values else None,maximumLowering=-min(values)if values else None,intervals=out)
def main():
 assert compare([(0,1,0,0,0)],[(0,1,1,0,0),(0,1,-1,1,1)])['maximumRise']==1
 assert compare([(0,1,0,0,0)],[(0,.5,0,0,0)])['missingFraction']==.5
 assert not DOC.exists();receipt=read(SRC/'result.json');refs=[Path(__file__),HERE/'source_surface_inset.py',SRC/'result.json'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p);pins[p]=e['sha256']
 current=BASE/'government-xl-lai-chi-kok-full-terrain-metrics-v9-20261019';cr=read(current/'result.json');refs.append(current/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(cr['jobId'],)).fetchone()==('complete',cr)
 for e in cr['evidenceRefs']:
  p=ROOT/e['path'];assert p not in pins or pins[p]==e['sha256'];assert digest(p.read_bytes())==e['sha256'];refs.append(p);pins[p]=e['sha256']
 gp=HERE/'local/government-xl-next-five-adjoining-ground-v1-20261018/281463:0-ground.json.gz';cp=HERE/'local/government-xl-lai-chi-kok-full-terrain-metrics-v9-20261019/runtime-geometry.json.gz';assert gp in pins and cp in pins
 original=surface(np.asarray(read(gp)['completeAdjoiningTerrain']));candidate=surface(np.asarray(read(cp)['rows'][0]['drawnGroundGeometry']).reshape(-1,3,3));summary=[]
 for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
  rows=[]
  for face in read(SRC/(mode+'.json'))['faces']:
   t=np.asarray(face['vertices']);xz=t[:,[0,2]];axis=int(np.argmax(np.ptp(xz,axis=0)));a=xz[np.argmin(xz[:,axis])];b=xz[np.argmax(xz[:,axis])];length=float(np.linalg.norm(b-a));assert length>0
   r=compare(intervals(a,b,original),intervals(a,b,candidate));rows.append(dict(faceId=face['faceId'],length=length,start=a.tolist(),end=b.tolist(),**r))
  sums=dict(mode=mode,faces=len(rows),missingFaces=sum(r['missingFraction']>0 for r in rows),missingLength=sum(r['missingFraction']*r['length']for r in rows),maximumRise=max(r['maximumRise'] for r in rows if r['maximumRise']is not None),maximumLowering=max(r['maximumLowering']for r in rows if r['maximumLowering']is not None),installationApproved=False);summary.append(sums);save(DOC/(mode+'.json'),dict(summary=sums,rows=rows));print(sums,flush=True)
 save(DOC/'summary.json',dict(rows=summary,qualification='Piecewise affine upper envelopes on positive-length intervals. Isolated endpoints and off-edge visibility are not certified; missing intervals retained.',installationApproved=False))
 module('edge_terrain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-vertical-wall-continuous-edge-terrain-comparison',list(dict.fromkeys(refs)),dict(uids=['landsd/281463:0'],rows=summary,installationApproved=False))
if __name__=='__main__':main()
