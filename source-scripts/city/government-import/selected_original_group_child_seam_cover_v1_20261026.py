"""Apply the bounded existing Float32 seam cover to a private nested child."""
import argparse
from pathlib import Path
from copy import deepcopy
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from float32_native_seam_cover_v2_20261025 import cover
from float32_coverage import approve_roundoff
from native_patch_resolution import projected_context

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','previous','expanded-parent','capture']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch;assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists()and not local.exists();refs=[Path(__file__)];pins={};receipts={}
 def take(name,path):
  if name not in pins:receipts[name],pins[name]=authenticate(base/name);refs.append(base/name/'result.json')
  assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 prior=take(a.previous,base/a.previous/'summary.json');assert prior['status']=='private-terrain-validator-passed'
 before=take(a.previous,ROOT/prior['candidate']['path']);patch=deepcopy(before)
 expanded=take(a.expanded_parent,base/a.expanded_parent/'summary.json');parent=take(a.expanded_parent,ROOT/expanded['candidateParent']['path'])
 selected=take(a.capture,base/a.capture/'selection.json.gz');rows=[r for r in selected['rows']if r['uid']in prior['uids']];assert {r['uid']for r in rows}==set(prior['uids'])==set(patch['meta']['targetUids'])
 for r in rows:
  p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p)
 helper=module('group_child_seam_validation',HERE/'resolve_pass_indexed_parent_clipping_v2.py');bounds=helper.extent(patch['coarseCells'],parent)
 proof=cover(patch,bounds)
 assert len(patch['nativeMesh']['index'])//3<=25000
 assert patch['nativeMesh']['position'][:len(before['nativeMesh']['position'])]==before['nativeMesh']['position']
 assert patch['nativeMesh']['index'][:len(before['nativeMesh']['index'])]==before['nativeMesh']['index']
 for metadata in [patch['meta']['source'],patch['nativeMesh']['source']]:metadata['derivedTerrainSeamCover']=proof
 patch['nativeMesh']['source'].pop('numericalCoverageGap',None)
 out.mkdir();local.mkdir()
 _,polygons,_,_=projected_context(patch,bounds)
 if shapely.union_all(polygons).symmetric_difference(shapely.box(*bounds)).area:save(out/'numerical-coverage.json',approve_roundoff(patch,bounds))
 overlap=module('group_child_seam_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=out;overlap.overlap_proof(patch,refs)
 helper.validate_patch(patch,parent)
 path=local/'candidate-terrain.json';save(path,patch);refs.append(path)
 save(out/'scope.json',take(a.previous,base/a.previous/'scope.json'));save(out/'seam-cover-proof.json',proof)
 result=dict(uids=prior['uids'],sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())),terrainTriangles=len(patch['nativeMesh']['index'])//3,status='private-terrain-validator-passed',seamCover=proof,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,qualification='Private additive seam repair under an authenticated5m group parent; every earlier child terrain vertex/index and original model byte retained. Existing2mm/.25m2 seam limits and all canonical validators unchanged. Reassemble exact group and rerun actual source/retained/native/basic checks.')
 save(out/'summary.json',result);refs.extend([HERE/'float32_native_seam_cover_v2_20261025.py',HERE/'resolve_pass_indexed_parent_clipping_v2.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py',HERE/'float32_coverage.py',HERE/'native_patch_resolution.py']);module('group_child_seam_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'private-nested-original-additive-seam-cover',refs,result)
 print(dict(terrainTriangles=result['terrainTriangles'],seamCover=proof),flush=True)
if __name__=='__main__':main()
