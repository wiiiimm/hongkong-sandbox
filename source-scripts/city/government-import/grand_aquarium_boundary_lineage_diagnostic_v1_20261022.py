"""Trace newly exposed boundary samples to immutable installed terrain facets."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from china_ferry_current_foundations_v1_20261020 import authenticate
from ronsdale_local_inset_v2_20261022 import plane
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-grand-aquarium-boundary-lineage-diagnostic-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists()
 previous=BASE/'government-xl-grand-aquarium-retained-followthrough-v1-20261022-candidate'
 _,pins=authenticate(previous)
 summary=read(previous/'summary.json');candidatepath=ROOT/summary['candidate']['path'];oldpath=ROOT/'3d-viewer'/summary['candidate']['replaces']['url']
 refs=[Path(__file__),previous/'result.json',previous/'summary.json',candidatepath,oldpath]
 for p in refs[2:]:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 capturepath=HERE/'local/government-xl-grand-aquarium-retained-boundary-inset-v6-20261022/parent.json'
 _,cpins=authenticate(BASE/'government-xl-grand-aquarium-retained-boundary-inset-v6-20261022')
 assert digest(capturepath.read_bytes())==cpins[str(capturepath.relative_to(ROOT))]
 rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=read(rootpath)
 builder=module('boundary_lineage_builder',HERE/'resolve_pass_indexed_parent_clipping_v2.py')
 sampler=builder.terrain.fine.DemSampler(root,rendered=True)
 old=read(oldpath);candidate=read(candidatepath);g=old['meta']['georef'];bounds=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(old['w']-1)*g['aE'],816500-g['bN']-(old['h']-1)*g['aN']]
 def edges(p):
  a=np.asarray(p['nativeMesh']['position'],dtype=np.float32).reshape(-1,3).astype(float)
  return a[np.minimum.reduce([abs(a[:,0]-bounds[0]),abs(a[:,0]-bounds[2]),abs(a[:,2]-bounds[1]),abs(a[:,2]-bounds[3])])<.002]
 def worst(p):
  a=edges(p);errors=np.array([abs(y-sampler.ground(x,z))for x,y,z in a]);i=int(errors.argmax());return dict(point=a[i].tolist(),rootHeight=float(sampler.ground(a[i,0],a[i,2])),errorM=float(errors[i]))
 before,after=worst(old),worst(candidate);x,y,z=after['point'];capture=read(capturepath);matches=[]
 oldfaces=np.asarray(old['nativeMesh']['position'],dtype=np.float32).reshape(-1,3)[np.asarray(old['nativeMesh']['index']).reshape(-1,3)]
 maxfit=0.
 for i,f in enumerate(capture['triangles']):
  a=np.asarray(f)
  try:q=plane(a)
  except ValueError:continue
  maxfit=max(maxfit,float(np.max(abs(a[:,[0,2]]@q[:2]+q[2]-a[:,1]))))
  if any(abs(v[0]-x)<.002 and abs(v[2]-z)<.002 and abs(v[1]-y)<.002 for v in f):
   original=np.asarray(capture['lineage'][i]['originalFace']);indices=np.flatnonzero(np.all(oldfaces==original,axis=(1,2)));assert len(indices)
   matches.append(dict(captureFace=i,installedFaceIndices=indices.tolist(),originalFace=original.tolist(),interpolatedHeight=float(np.array([x,z])@plane(original)[:2]+plane(original)[2])))
 assert before['errorM']<.01 and after['errorM']>1 and matches and maxfit<1e-6
 result=dict(uids=['landsd/93424:0'],status='boundary-lineage-confirmed',installedVertexCheck=before,newBoundarySample=after,parentPlaneMaxReconstructionErrorM=maxfit,matchingInstalledFacets=matches,conclusion='Clipping exposes an interpolated point on an existing long boundary facet. Its original vertices pass the root-height guard, but interpolation between them differs from the piecewise root DEM. Plane fitting is not the cause. A source-backed boundary transition must be constructed and all retained actors rechecked; no guard waiver.',sourceGeometryChanges=0,newlyInstalled=0,installationApproved=False,scriptExternalAICalls=0)
 save(doc/'summary.json',result)
 refs.extend([capturepath,rootpath,HERE/'ronsdale_local_inset_v2_20261022.py',HERE/'china_merchants_finite_inset_v4_20261021.py',HERE/'resolve_pass_indexed_parent_clipping_v2.py'])
 module('boundary_lineage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-terrain-boundary-lineage',refs,result)
 print(dict(status=result['status'],originalVertexError=before['errorM'],newSampleError=after['errorM'],matches=len(matches)))
if __name__=='__main__':main()
