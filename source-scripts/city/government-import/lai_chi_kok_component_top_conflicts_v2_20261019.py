"""Locate terrain/platform occlusion of original upper component surfaces; diagnostic."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from source_surface_inset import plane,lower_region
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-component-top-conflicts-v2-20261019';DOC=BASE/BATCH;SRC=BASE/'government-xl-lai-chi-kok-original-component-checks-v1-20261019';ATTR=BASE/'government-xl-lai-chi-kok-all-contact-ground-attribution-v2-20261019'
def index(tri):
 ps=shapely.polygons(tri[:,:,[0,2]]);ok=shapely.area(ps)>1e-10;ts=tri[ok];ps=ps[ok];return ps,[plane(t)for t in ts],shapely.STRtree(ps),np.flatnonzero(ok)
def higher(p,coeff,s,clearance):
 ps,planes,tree,ids=s;cuts=[]
 for j in tree.query(p,predicate='intersects'):
  q=p.intersection(ps[j])
  if q.area<=1e-10:continue
  assert q.geom_type=='Polygon'
  d=planes[j]-coeff;d=d.copy();d[2]-=clearance
  h=lower_region(q,d)
  if h.area>1e-10:cuts.append(h)
 return shapely.union_all(cuts)
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'source_surface_inset.py'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [SRC,ATTR]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 cap=HERE/'local/government-xl-lai-chi-kok-full-terrain-metrics-v3-20261019/runtime-geometry.json.gz';gp=HERE/'local/government-xl-next-five-adjoining-ground-v1-20261018/281463:0-ground.json.gz';assert str(cap.relative_to(ROOT))in pins and str(gp.relative_to(ROOT))in pins
 g=read(cap)['rows'][0];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);pod=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];surfaces=dict(candidate=index(ground),original=index(np.asarray(read(gp)['completeAdjoiningTerrain'])),platform=index(pod));summaries=[]
 for row in read(SRC/'input.json.gz')['rows']:
  tri=np.asarray(row['position']).reshape(-1,3)[np.asarray(row['index']).reshape(-1,3)];own=index(tri);norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);wanted=np.flatnonzero(norm[:,1]>.25*np.linalg.norm(norm,axis=1));tops=[];regions={k:[]for k in surfaces};details=[]
  for i in wanted:
   p=shapely.Polygon(tri[i][:,[0,2]]);coeff=plane(tri[i]);exposed=p.difference(higher(p,coeff,own,1e-8));tops.append(exposed);areas={}
   for key,s in surfaces.items():
    above=higher(p,coeff,s,.5);conflict=shapely.Polygon() if exposed.is_empty or above.is_empty else exposed.intersection(above);regions[key].append(conflict);areas[key]=conflict.area
   if any(v>1e-10 for v in areas.values()):details.append(dict(faceId=int(i),exposedArea=exposed.area,occludedArea=areas))
  masks={k:shapely.union_all(v)for k,v in regions.items()};total=shapely.union_all(tops);new=masks['candidate'].difference(masks['original']);summary=dict(uid=row['uid'],upwardFaces=len(wanted),exposedUpwardProjectionArea=total.area,occludedProjectionAreas={k:v.area for k,v in masks.items()},candidateNewOcclusionArea=new.area,installationApproved=False);summaries.append(summary);save(DOC/(row['uid'].split('/')[1]+'.json'),dict(summary=summary,faces=details,conflictRegions={k:v.__geo_interface__ for k,v in masks.items()},newTerrainOcclusion=new.__geo_interface__));print(summary,flush=True)
 save(DOC/'summary.json',dict(rows=summaries,installationApproved=False,qualification='Projected upper-surface areas; own coplanar tie clearance1e-8m and existing0.5m burial diagnostic. Does not approve wall support, identity or installation.'))
 module('tops_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-component-upper-surface-terrain-platform-attribution',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in summaries],rows=summaries,installationApproved=False))
if __name__=='__main__':main()
