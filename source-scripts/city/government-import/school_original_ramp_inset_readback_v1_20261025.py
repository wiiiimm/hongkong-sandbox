"""Independent original-plane/unchanged-terrain readback of the private ramp cut."""
from pathlib import Path
from copy import deepcopy
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from source_surface_inset import plane
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-quality-music-school-ramp-inset-readback-v1-20261025'
OLD='government-xl-quality-music-school-three-original-inset-v1-20261025'
NEW='government-xl-quality-music-school-original-ramp-inset-v4-20261025'
RAMPS='government-xl-quality-music-school-podium-eight-ramp-context-v1-20261025'

def main():
 out=BASE/BATCH;assert not out.exists();pins={};receipts={};refs=[Path(__file__)]
 def take(n,path):
  if n not in pins:receipts[n],pins[n]=authenticate(BASE/n);refs.append(BASE/n/'result.json')
  assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 oldmeta=take(OLD,BASE/OLD/'terrain-source-context.json');a=take(OLD,ROOT/receipts[OLD]['candidate']['path'])
 proof=take(NEW,BASE/NEW/'inset-proof.json.gz');b=take(NEW,ROOT/receipts[NEW]['candidate']['path']);r=take(RAMPS,BASE/RAMPS/'summary.json')
 def faces(p):return np.asarray(p['nativeMesh']['position']).reshape(-1,3)[np.asarray(p['nativeMesh']['index']).reshape(-1,3)]
 old,new=faces(a),faces(b);ramps=np.asarray([x['vertices']for x in r['rows']]);footprint=shapely.union_all(shapely.polygons(ramps[:,:,[0,2]]))
 assert {k:v for k,v in a['meta'].items()if k!='source'}=={k:v for k,v in b['meta'].items()if k!='source'}
 assert {k:v for k,v in a['nativeMesh'].items()if k not in ['position','index','source','sourceOverlap']}=={k:v for k,v in b['nativeMesh'].items()if k not in ['position','index','source','sourceOverlap']}
 for oldsource,newsource in [(a['meta']['source'],b['meta']['source']),(a['nativeMesh']['source'],b['nativeMesh']['source'])]:assert {k:v for k,v in oldsource.items()if k!='numericalCoverageGap'}=={k:v for k,v in newsource.items()if k not in ['authoredRampInset','numericalCoverageGap']}
 parent=take(OLD,ROOT/'3d-viewer/city/data/terrain.json');helper=module('ramp_readback_domain',HERE/'resolve_pass_indexed_parent_clipping_v2.py');bounds=helper.extent(b['coarseCells'],parent)
 from float32_coverage import approve_roundoff
 replay=deepcopy(b);approve_roundoff(replay,bounds);assert replay['nativeMesh']['source']['numericalCoverageGap']==b['nativeMesh']['source']['numericalCoverageGap']
 for key in ['maximumAreaM2','maximumRoundoffDistanceM','policy']:assert a['nativeMesh']['source']['numericalCoverageGap'][key]==b['nativeMesh']['source']['numericalCoverageGap'][key]
 assert {k:v for k,v in a['nativeMesh']['sourceOverlap'].items()if k not in ['evidencePath','evidenceSHA256']}=={k:v for k,v in b['nativeMesh']['sourceOverlap'].items()if k not in ['evidencePath','evidenceSHA256']}
 overlap=b['nativeMesh']['sourceOverlap'];overlap_path=ROOT/overlap['evidencePath'];take(NEW,overlap_path);assert digest(overlap_path.read_bytes())==overlap['evidenceSHA256']
 assert a['coarseCells']==b['coarseCells']and a['meta']['targetUids']==b['meta']['targetUids']and len(proof['lineage'])==len(new)
 assert {k:v for k,v in a.items()if k not in ['meta','nativeMesh']}=={k:v for k,v in b.items()if k not in ['meta','nativeMesh']}
 counts={};max_plane_error=0.;steps=[];inserted=removed=0.
 for t,l in zip(new,proof['lineage']):
  kind=l['kind'];counts[kind]=counts.get(kind,0)+1;p=shapely.Polygon(t[:,[0,2]])
  if kind=='unchanged-terrain':assert np.array_equal(t,old[l['face']]);continue
  source=old[l['face']]if kind=='terrain-plane-fragment'else ramps[l['face']]
  q=plane(source);error=float(abs(t[:,1]-(t[:,[0,2]]@q[:2]+q[2])).max());max_plane_error=max(max_plane_error,error);assert error<1e-9
  assert p.difference(shapely.Polygon(source[:,[0,2]])).area<1e-8
  if kind=='inset-source-plane-fragment':
   assert p.difference(footprint).area<1e-8;parent=old[l['terrainFace']];q=plane(parent);height=t[:,[0,2]]@q[:2]+q[2];assert np.all(t[:,1]<=height+1e-9)
   assert p.difference(shapely.Polygon(parent[:,[0,2]])).area<1e-8
   inserted+=p.area
   for v,y in zip(t,height):
    if shapely.Point(v[[0,2]]).distance(footprint.boundary)<1e-8:steps.append(float(y-v[1]))
  else:assert kind=='terrain-plane-fragment'
 for i in proof['changedTerrainFaceIndices']:
  p=shapely.Polygon(old[i][:,[0,2]]);kept=[shapely.Polygon(t[:,[0,2]])for t,l in zip(new,proof['lineage'])if l['kind']=='terrain-plane-fragment'and l['face']==i]
  removed+=p.difference(shapely.union_all(kept)).area
 assert abs(removed-inserted)<1e-6 and abs(inserted-proof['insertedProjectedAreaM2'])<1e-6
 result=dict(uids=receipts[NEW]['uids'],passed=True,oldTerrainFaces=len(old),newTerrainFaces=len(new),outputLineageCounts=counts,exactUnchangedTerrainFaces=counts['unchanged-terrain'],maximumPlaneResidualM=max_plane_error,removedProjectedAreaM2=removed,insertedProjectedAreaM2=inserted,maximumInternalBoundaryHeightStepM=max(steps,default=0),continuousReturnClaimed=False,originalSourceBytesChanged=0,sourceGeometryChanges=0,installationApproved=False,qualification='Every unchanged face equals old bytes; other old fragments stay on their original terrain plane. Every lowered fragment stays on one exact original ramp plane and inside that ramp and its original terrain face, with conserved projected area. Internal height steps are recorded, not claimed smooth or visually accepted. No building vertices or ground-clearance limits changed; fresh runtime/neighbours/browser remain mandatory.')
 save(out/'summary.json',result);refs.extend([HERE/'source_surface_inset.py',HERE/'float32_coverage.py',HERE/'resolve_pass_indexed_parent_clipping_v2.py']);module('school_ramp_readback_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'independent-exact-original-plane-ramp-terrain-cut-readback',refs,result);print(result,flush=True)
if __name__=='__main__':main()
