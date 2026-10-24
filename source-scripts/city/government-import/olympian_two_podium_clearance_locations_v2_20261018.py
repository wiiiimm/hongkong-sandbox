"""Locate remaining podium samples against rendered and unchanged original TIN."""
from pathlib import Path
import numpy as np,shapely
from fractions import Fraction as F
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_point_triangle_distance_20261018 import squared_distance
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-olympian-two-three-podium-terrain-v2-20261018';BATCH='government-xl-olympian-two-podium-clearance-locations-v2-20261018';DOC=BASE/BATCH
RECOVERY=BASE/'government-xl-olympian-two-current-retained-terrain-v1-20261018/source-recovery.json'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};refs=[Path(__file__),PRIOR/'result.json',RECOVERY]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 assert str(RECOVERY.relative_to(ROOT))in pins
 second=module('olympian_clearance_second',HERE/'xl-second-pass.py');second.LOCAL=HERE/'local'/BATCH;parts=[]
 for s in read(RECOVERY)['sheets']:
  folder=ROOT/s['cache'];proof=read(folder/'original/download.json');assert proof['directorySHA256']==s['directorySHA256'];refs.append(folder/'original/download.json')
  for e in s['terrainFiles']:
   p=folder/'terrain'/e['name'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
   if p.suffix=='.gltf':parts.append(second.terrain_triangles(p))
 original=np.concatenate(parts)
 def samples(mesh,points):
  lo=points[:,[0,2]].min(0)-1;hi=points[:,[0,2]].max(0)+1;mesh=mesh[(mesh[:,:,0].max(1)>=lo[0])&(mesh[:,:,0].min(1)<=hi[0])&(mesh[:,:,2].max(1)>=lo[1])&(mesh[:,:,2].min(1)<=hi[1])];polys=shapely.polygons(mesh[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;return second.context.shared.samples(points[:,[0,2]],mesh[valid],shapely.STRtree(polys[valid]))
 metrics={x['uid']:x for x in read(PRIOR/'metrics.json')['rows']};rt=HERE/'local'/PRIOR.name/'runtime-geometry.json.gz';assert str(rt.relative_to(ROOT))in pins;rows=[]
 for g in read(rt)['rows']:
  uid=g['uid'];v=np.asarray(g['position']).reshape(-1,3);idx=np.asarray(g['index']).reshape(-1,3);t=v[idx];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);points,bottom=second.resolution.sample_points(g);h=samples(ground,points);gap=points[:,1]-h;assert np.isfinite(gap).all();assert abs(float(gap.min())-metrics[uid]['minSurfaceGap'])<1e-6
  low=points[:,1]<=bottom+.35;mask=(gap<-.5)|(low&(gap>1));
  if gap[low].min()>.1:mask|=low
  bad=np.flatnonzero(mask);oh=samples(original,points[bad]);assert np.isfinite(oh).all();lo=t.min(1);hi=t.max(1);details=[];used=set(idx.reshape(-1).tolist())
  for k,i in enumerate(bad):
   p=points[i];candidate=np.flatnonzero(np.all((lo-.001<=p)&(hi+.001>=p),axis=1));incident=[int(j)for j in candidate if squared_distance(p,t[j])<=F(.001)**2];details.append(dict(sampleIndex=int(i),kind='vertex'if i<len(v)else'triangle-centroid'if i<len(v)+len(t)else'low-edge-interior',unusedPackedVertex=bool(i<len(v)and int(i)not in used),position=p.tolist(),candidateGapM=float(gap[i]),originalTerrainGapM=float(p[1]-oh[k]),candidateMinusOriginalTerrainM=float(h[i]-oh[k]),incidentIndexedFaces=incident))
  summary=dict(uid=uid,sourceSHA256=g['sourceSHA256'],checks=len(points),flagged=len(details),belowGrade=sum(x['candidateGapM']<-.5 for x in details),unusedPackedVertexFlags=sum(x['unusedPackedVertex']for x in details),incidentOriginalFaces=sorted({i for x in details for i in x['incidentIndexedFaces']}),minimumCandidateGap=float(gap.min()),maxCandidateOriginalDifference=max(abs(x['candidateMinusOriginalTerrainM'])for x in details));save(DOC/(uid.split('/')[1]+'-locations.json.gz'),dict(**summary,rows=details));rows.append(summary);print({k:v for k,v in summary.items()if k!='incidentOriginalFaces'},flush=True)
 save(DOC/'summary.json',dict(rows=rows,fullAcceptance=False,newlyInstalled=0));refs.extend(ROOT/p for p in pins);refs.extend([rt,HERE/'xl-second-pass.py',HERE/'resolve-pass.py',HERE/'exact_point_triangle_distance_20261018.py'])
 out=module('olympian_clearance_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-three-podium-original-candidate-clearance-location-v1',list(set(refs)),dict(uids=[x['uid']for x in rows],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
