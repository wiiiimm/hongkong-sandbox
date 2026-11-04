import sys
sys.path.insert(0,'source-scripts/city/government-import')
from run import read,ROOT,HERE
import numpy as np,shapely
from source_surface_inset import plane
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from native_patch_resolution import _faces
base=ROOT/'docs/astra-city/government-import'
row=read(base/'government-xl-lai-chi-kok-full-terrain-metrics-v7-20261019/selection.json.gz')['rows'][0]
s=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());p=shapely.polygons(s[:,:,[0,2]]);cross=np.cross(s[:,1]-s[:,0],s[:,2]-s[:,0]);valid=cross[:,1]>2e-10;ids=np.flatnonzero(valid);tree=shapely.STRtree(p[valid])
g=_faces(read(base/'government-xl-lai-chi-kok-full-terrain-metrics-v5-20261019/private-terrain.json'));gp=shapely.polygons(g[:,:,[0,2]]);gt=shapely.STRtree(gp)

from pathlib import Path
from run import save,digest
from primrose_compound_foundation_v2_20261015 import module
batch='government-xl-lai-chi-kok-wall-gap-attribution-v1-20261019';doc=base/batch
assert not doc.exists()
edge=base/'government-xl-lai-chi-kok-vertical-edge-terrain-v3-20261019/original.json'
rows=[];candidates=set()
for r in read(edge)['rows']:
 for interval in r['intervals']:
  if not interval.get('missingCandidate') or interval.get('missingOriginal'):continue
  a=np.asarray(r['start']);b=np.asarray(r['end']);lo,hi=interval['interval'];mid=a+(b-a)*((lo+hi)/2);pt=shapely.Point(mid);old=[]
  for j in gt.query(pt,predicate='intersects'):
   if gp[j].area<=1e-10:continue
   candidates.add(int(j));old.append(int(j))
  rows.append(dict(faceId=r['faceId'],interval=[lo,hi],midpoint=mid.tolist(),previousTerrainFaceIds=old))
checks=[]
for j in sorted(candidates):
 fp=plane(g[j]);hits=[]
 for k in tree.query(gp[j],predicate='intersects'):
  i=int(ids[k]);q=gp[j].intersection(p[i])
  if q.area<=1e-10:continue
  xy=shapely.get_coordinates(q);diff=fp-plane(s[i]);v=xy@diff[:2]+diff[2]
  if v.max()>.005:hits.append(dict(sourceFaceId=i,maximumRise=float(v.max()),overlapArea=float(q.area)))
 checks.append(dict(previousTerrainFaceId=j,area=float(gp[j].area),overtoppedSourceFaces=hits))
save(doc/'attribution.json',dict(rows=rows,candidates=checks,installationApproved=False,diagnosticOnly=True))
refs=[Path(__file__),edge,base/'government-xl-lai-chi-kok-full-terrain-metrics-v5-20261019/private-terrain.json',ROOT/row['candidate']['path'],HERE/'native_patch_resolution.py',HERE/'source_surface_inset.py',HERE/'exact_packed_world_geometry_20261009.py']
module('gap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'original-wall-gap-source-attribution',refs,dict(uids=['landsd/281463:0'],installationApproved=False,diagnosticOnly=True))
print(dict(intervals=len(rows),candidates=checks),flush=True)
