"""Private source-terrain triangulation feasibility, never publication or acceptance."""
import copy
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from ronsdale_local_inset_v2_20261022 import plane,lift
from exact_original_projection_coverage_v2_20261010 import exact_coverage
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-yoho-eight-noded-core-feasibility-v2-20261022'
PATCH='government-xl-yoho-eight-core-margin-020-v1-20261022'
RESIDUAL='government-xl-yoho-eight-core-020-residual-preflight-v1-20261022'
RUNTIME='government-xl-after-fu-loy-three-current-capture-v1-20261022'
def main():
 out=BASE/BATCH;local=HERE/'local'/BATCH;assert not out.exists()and not local.exists()
 refs=[Path(__file__),HERE/'ronsdale_local_inset_v2_20261022.py',HERE/'exact_original_projection_coverage_v2_20261010.py'];pins={}
 for name in [PATCH,RESIDUAL,RUNTIME]:
  _,p=authenticate(BASE/name);pins.update(p);refs.append(BASE/name/'result.json')
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 patch=take(BASE/PATCH/'result.json');n=take(ROOT/patch['candidate']['path']);lineage=take(BASE/PATCH/'lineage.json.gz')
 residual=take(BASE/RESIDUAL/'summary.json');runtime=take(HERE/'local'/RUNTIME/'runtime-geometry.json.gz')
 geometry=next(r for r in runtime['rows']if r['uid']=='landsd/146396:0')
 source=np.asarray(geometry['position']).reshape(-1,3)[np.asarray(geometry['index']).reshape(-1,3)]
 t=np.asarray(n['nativeMesh']['position']).reshape(-1,3)[np.asarray(n['nativeMesh']['index']).reshape(-1,3)]
 mask=np.asarray([r['kind']=='complete-authentic-original-tin-core'for r in lineage['outputLineage']]);normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);mask &= np.abs(normal[:,1])>1e-10;core=t[mask] # retain all non-plane/degenerate original terrain facets verbatim
 polys=shapely.polygons(core[:,:,[0,2]]);tree=shapely.STRtree(polys);planes=[plane(f)for f in core]
 # Node every shared edge before triangulation so both incident facets use
 # the same intermediate vertices when packed as Float32.
 lines=shapely.union_all(shapely.boundary(polys));cells=list(shapely.get_parts(shapely.polygonize(shapely.get_parts(lines))))
 faces=[];cellproof=[]
 for cell in cells:
  point=cell.representative_point();ids=tree.query(point,predicate='intersects')
  if not len(ids):continue
  assert all(cell.difference(polys[i]).area<1e-7 for i in ids)
  x,z=point.x,point.y;i=max(ids,key=lambda i:np.dot([x,z,1],planes[i]))
  fragments=lift(cell,planes[i]);faces.extend(fragments);cellproof.append(dict(sourceCoreFace=int(i),triangles=len(fragments),areaM2=float(cell.area)))
 faces=np.asarray(faces);oldunion=shapely.union_all(polys);newunion=shapely.union_all(shapely.polygons(faces[:,:,[0,2]]))
 area=float(oldunion.symmetric_difference(newunion).area);assert area<1e-7
 output=np.concatenate([t[~mask],faces]);candidate=copy.deepcopy(n);candidate['nativeMesh']['position']=output.reshape(-1).tolist();candidate['nativeMesh']['index']=list(range(output.size//3))
 save(local/'unapproved-candidate-terrain.json',candidate);refs.append(local/'unapproved-candidate-terrain.json')
 ground=output.astype('float32').astype('float64');proofs=[]
 for face in residual['stillUncovered']:proofs.append(dict(sourceFace=face,**exact_coverage(source[face],ground)))
 report=dict(uids=['landsd/146396:0'],sourceSHA256=geometry['sourceSHA256'],previousCandidateSHA256=patch['candidate']['sha256'],testedFaces=residual['stillUncovered'],proofs=proofs,allTestedFacesCovered=all(r['exactProjectionCovered']for r in proofs),originalCoreFaces=len(core),nodedCoreFaces=len(faces),oldVsNewCoreProjectionSymmetricDifferenceM2=area,cells=cellproof,installationApproved=False,qualification='Only two previously failed source faces tested against a private terrain triangulation. Whole-source clearance, native validators, current-scene binding, neighbours, identity and browser remain unapproved. Original building bytes unchanged.')
 save(out/'summary.json',report)
 module('noded_core_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-source-terrain-noded-core-feasibility',refs,report)
 print(dict(allTestedFacesCovered=report['allTestedFacesCovered'],originalCoreFaces=len(core),nodedCoreFaces=len(faces)),flush=True)
if __name__=='__main__':main()
