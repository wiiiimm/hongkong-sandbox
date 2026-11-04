"""Account for the exact low-edge samples without changing source or predicates."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-illumination-low-edge-context-v1-20261021';DOC=BASE/BATCH

def main():
 assert not DOC.exists();refs=[Path(__file__)]
 def take(batch,path):
  folder=BASE/batch;_,pins=authenticate(folder);p=ROOT/path;assert digest(p.read_bytes())==pins[path];refs.extend([folder/'result.json',p]);return read(p)
 sn='government-xl-illumination-actual-samples-v1-20261021';samples=take(sn,str((BASE/sn/'samples.json').relative_to(ROOT)))
 cap='government-xl-illumination-inset-runtime-v1-20261021';rt=take(cap,str((HERE/'local'/cap/'runtime-geometry.json.gz').relative_to(ROOT)));g=next(r for r in rt['rows']if r['uid']=='landsd/258737:0');assert g['sourceSHA256']==samples['sourceSHA256']
 tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];faces=sorted({r['faceIndex']for r in samples['rows']});assert faces==[1044]
 old='government-xl-illumination-original-ground-v1-20261021';terrain=np.asarray(take(old,str((HERE/'local'/old/'original-terrain.json.gz').relative_to(ROOT)))['triangles']);polys=shapely.polygons(terrain[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;terrain=terrain[valid];helper=module('illumination_original_samples',HERE/'xl-final-script-pass.py');points=np.asarray([r['position']for r in samples['rows']]);heights=helper.s.context.shared.samples(points[:,[0,2]],terrain,shapely.STRtree(polys[valid]));assert np.isfinite(heights).all()
 face=tri[1044];normal=np.cross(face[1]-face[0],face[2]-face[0]);edges=[(face[i],face[(i+1)%3])for i in range(3)];neighbours=[]
 for i,f in enumerate(tri):
  if i==1044:continue
  shared=[v.tolist()for v in f if any(np.array_equal(v,p)for p in face)]
  if len(shared)>=2:neighbours.append(dict(faceIndex=i,vertices=f.tolist(),sharedVertices=shared,normal=np.cross(f[1]-f[0],f[2]-f[0]).tolist()))
 result=dict(uids=['landsd/258737:0'],sourceSHA256=g['sourceSHA256'],faceIndex=1044,vertices=face.tolist(),normal=normal.tolist(),normalisedVertical=float(normal[1]/np.linalg.norm(normal)),edgeNeighbours=neighbours,samples=[dict(**r,originalTerrainHeight=float(h),originalTerrainGapM=float(r['position'][1]-h),renderedMinusOriginalGroundM=float(r['ground']-h))for r,h in zip(samples['rows'],heights)],installationApproved=False,physicalInterpretationAccepted=False,rawFailuresPreserved=True)
 save(DOC/'context.json',result);refs.append(HERE/'xl-final-script-pass.py');module('illumination_edge_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-low-edge-original-terrain-context',refs,result);print(dict(normalisedVertical=result['normalisedVertical'],neighbours=[r['faceIndex']for r in neighbours],originalGapRange=[float((points[:,1]-heights).min()),float((points[:,1]-heights).max())],maxRenderedDelta=float(np.abs(np.array([r['ground']for r in samples['rows']])-heights).max())),flush=True)
if __name__=='__main__':main()
