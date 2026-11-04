"""Inspect all authentic ground layers at buried source witnesses; no terrain edits."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mount-sterling-ground-layers-v1-20261020';DOC=BASE/BATCH
GROUND=BASE/'government-xl-mount-sterling-adjoining-ground-v1-20261020';SRC=BASE/'government-xl-mount-sterling-compound-foundations-v1-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [GROUND,SRC]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins.update({e['path']:e['sha256']for e in r['evidenceRefs']})
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 g=np.asarray(take(HERE/'local'/GROUND.name/'289787:0-ground.json.gz')['completeAdjoiningTerrain'])
 source=take(SRC/'289787:0-original.json.gz');faces=source['buriedFaces'];ps=shapely.polygons(g[:,:,[0,2]]);valid=shapely.area(ps)>1e-10;ids=np.flatnonzero(valid);g=g[valid];ps=ps[valid];tree=shapely.STRtree(ps)
 normals=np.cross(g[:,1]-g[:,0],g[:,2]-g[:,0]);d=np.einsum('ij,ij->i',normals,g[:,0]);records=[]
 for face in faces:
  tri=np.asarray(face['vertices']);samples=[]
  for p in [*tri,tri.mean(0)]:
   point=shapely.Point(p[[0,2]]);hit=tree.query(point,predicate='intersects');heights=(d[hit]-normals[hit,0]*p[0]-normals[hit,2]*p[2])/normals[hit,1]
   layers=[dict(terrainFace=int(ids[i]),height=float(h))for i,h in zip(hit,heights)]
   samples.append(dict(position=p.tolist(),layers=layers,minimumGap=float(p[1]-max(heights))if len(heights)else None,maximumGap=float(p[1]-min(heights))if len(heights)else None,spread=float(np.ptp(heights))if len(heights)else None))
  records.append(dict(faceId=face['faceId'],samples=samples))
 summary=dict(uids=['landsd/289787:0'],faces=len(records),samples=sum(len(r['samples'])for r in records),multipleHeightSamples=sum(s['spread'] is not None and s['spread']>.01 for r in records for s in r['samples']),missingSamples=sum(s['spread']is None for r in records for s in r['samples']),facesBuriedEvenAtLowestAuthenticSurface=sum(all(s['maximumGap']is not None and s['maximumGap']<-.5 for s in r['samples'])for r in records),installationApproved=False,sourceGeometryChanges=0,terrainChanges=0)
 save(DOC/'layers.json.gz',dict(rows=records));save(DOC/'summary.json',summary)
 module('mount_ground_layers_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'all-authentic-ground-layers-at-buried-witnesses',refs,summary)
 print(summary,flush=True)
if __name__=='__main__':main()
