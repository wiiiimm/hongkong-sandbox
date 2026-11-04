"""Validate private conforming source terrain; no physical/publication acceptance."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from float32_coverage import approve_roundoff
from native_patch_resolution import projected_context
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-yoho-eight-noded-core-candidate-v2-20261022'
PREVIOUS='government-xl-yoho-eight-core-margin-020-v1-20261022'
TRIAL='government-xl-yoho-eight-noded-core-feasibility-v2-20261022'
def main():
 doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists()
 refs=[Path(__file__)];pins={}
 for name in [PREVIOUS,TRIAL]:
  _,p=authenticate(BASE/name);pins.update(p);refs.append(BASE/name/'result.json')
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 previous=take(BASE/PREVIOUS/'result.json');trial=take(BASE/TRIAL/'summary.json');assert trial['allTestedFacesCovered']
 path=HERE/'local'/TRIAL/'unapproved-candidate-terrain.json';candidate=take(path)
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=take(parentpath)
 builder=module('noded_core_builder',HERE/'validated_parent_roundoff_template_v2.py');bounds=builder.extent(candidate['coarseCells'],parent)
 save(doc/'scope.json',dict(uids=['landsd/146396:0'],cells=candidate['coarseCells'],bounds=list(bounds),qualification='Exact unchanged coarse-cell domain derived from candidate and pinned parent; no historical manifest approval.'))
 _,polygons,_,_=projected_context(candidate,bounds)
 # Recompute changed numeric coverage/overlap evidence; old approval never transfers.
 candidate['nativeMesh']['source'].pop('numericalCoverageGap',None)
 if shapely.union_all(polygons).symmetric_difference(shapely.box(*bounds)).area:
  save(doc/'numerical-coverage.json',approve_roundoff(candidate,bounds))
 overlap=module('noded_core_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=doc
 overlap.overlap_proof(candidate,[path,Path(__file__)])
 save(doc/'proposal-with-overlap-evidence.json',candidate);builder.validate_patch(candidate,parent)
 faces=len(candidate['nativeMesh']['index'])//3;assert faces<=25000
 destination=local/'candidate-terrain.json';save(destination,candidate);refs.append(destination)
 result=dict(uids=['landsd/146396:0'],status='private-terrain-validator-passed',candidate=dict(path=str(destination.relative_to(ROOT)),sha256=digest(destination.read_bytes()),replaces=previous['candidate']['replaces']),terrainTriangles=faces,sourceGeometryChanges=0,installationApproved=False,qualification='Noded private source-terrain triangulation with fresh unchanged native validators/overlap/coverage proof. Current full source, four-world foundation/rims, identity, all neighbours and browser remain required.')
 save(doc/'summary.json',result)
 refs.extend(p for p in doc.rglob('*')if p.is_file());refs.extend([HERE/'validated_parent_roundoff_template_v2.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py',HERE/'float32_coverage.py',HERE/'native_patch_resolution.py'])
 module('noded_candidate_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-noded-original-terrain-candidate',refs,result)
 print(dict(terrainTriangles=faces,status=result['status']),flush=True)
if __name__=='__main__':main()
