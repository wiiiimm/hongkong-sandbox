"""Certify two original hidden wall faces under finite actual terrain in four streams."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_subgrade_face_coverage_v1 import prove
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grand-aquarium-exact-subgrade-faces-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();refs=[Path(__file__)]
 def take(batch,name,local=False):
  folder=BASE/batch;_,pins=authenticate(folder);p=(HERE/'local'/batch if local else folder)/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([folder/'result.json',p]);return read(p)
 runtime='government-xl-grand-aquarium-crack-repaired-runtime-v1-20261022';g=take(runtime,'runtime-geometry.json.gz',True)['rows'][0];selection=take(runtime,'selection.json.gz')['rows'][0];asset=ROOT/selection['candidate']['path'];assert digest(asset.read_bytes())==g['sourceSHA256'];refs.append(asset);original=decode_original_world_triangles(asset.read_bytes());attrs=take('government-xl-grand-aquarium-original-attributes-v1-20261022','attributes.json.gz')['rows'][0];index=np.asarray(attrs['completeOriginalIndex']).reshape(-1,3);streams=dict(original=original)
 for mode,key in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:streams[mode]=np.asarray(attrs[key]).reshape(-1,3)[index]
 actual=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert np.array_equal(actual,streams['literal']);ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);paths=take('government-xl-grand-aquarium-original-wall-paths-v1-20261022','paths.json.gz');rows=[]
 for mode,tri in streams.items():
  assert len(tri)==10571
  for i in [9336,9337]:
   path=next(p for p in paths['faces']if p['sourceFace']==i);assert path['reasons']==['no-exposed-wall-witness'];proof=prove(tri[i],ground);row=dict(mode=mode,sourceFace=i,sourceFaceSHA256=digest(tri[i].tobytes()),drawnGroundSHA256=digest(ground.tobytes()),sourceSHA256=g['sourceSHA256'],originalWallToClearRoofPath=path['wallToRoofPath'],sourceGeometryChanges=0,**proof);save(doc/(mode+'-'+str(i)+'.json.gz'),row);rows.append(dict(mode=mode,sourceFace=i,wholeOriginalFaceAtOrBelowFiniteTerrain=proof['wholeOriginalFaceAtOrBelowFiniteTerrain'],exactUncoveredSourceUVArea=proof['exactUncoveredSourceUVArea']));print(rows[-1],flush=True)
 result=dict(uids=['landsd/93424:0'],sourceSHA256=g['sourceSHA256'],rows=rows,allEightFaceStreamCasesProven=all(r['wholeOriginalFaceAtOrBelowFiniteTerrain']for r in rows),qualifiedAsExposedWall=False,rawNoExposedWitnessFlagsRetained=True,sourceGeometryChanges=0,newlyInstalled=0,installationApproved=False,qualification='Exact full 3D authored face lies at/below at least one finite actual terrain facet everywhere, in original/literal/two explicit Float32 source streams. No hidden-face removal or geometry edit; no exposed-wall guard waiver. Source-specific below-grade retention evidence only; all foreign scope, other physical and publication gates remain independent.');save(doc/'summary.json',result);refs.extend(HERE/n for n in ['exact_subgrade_face_coverage_v1.py','exact_original_projection_coverage_v2_20261010.py','exact_packed_world_geometry_20261009.py']);module('aquarium_exact_subgrade_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-whole-subgrade-source-face-four-stream-certificate',refs,result)
if __name__=='__main__':main()
