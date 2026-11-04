"""Validate saved private geometry without requesting an inapplicable roundoff allowance."""
from pathlib import Path
import traceback
import shapely,numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from native_patch_resolution import projected_context
from float32_coverage import approve_roundoff,geometry_sha
BASE=ROOT/'docs/astra-city/government-import';OLD='government-xl-harbourfront-tower-private-wrapper-v1-20261021';BATCH='government-xl-harbourfront-tower-private-wrapper-v2-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
assert not DOC.exists();receipt,pins=authenticate(BASE/OLD);p=HERE/'local'/OLD/'candidate-wrapper.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];parent=read(p);child=parent['patches'][0];domain=read(BASE/OLD/'summary.json')['childBounds'];rootp=ROOT/'3d-viewer/city/data/terrain.json';assert digest(rootp.read_bytes())==pins[str(rootp.relative_to(ROOT))];root=read(rootp);before=geometry_sha(child);refs=[Path(__file__),BASE/OLD/'result.json',p,rootp];error=None
for name,h in pins.items():
 if name.startswith('3d-viewer/'):
  assert digest((ROOT/name).read_bytes())==h,name
  refs.append(ROOT/name)
_,polygons,missing,_=projected_context(child,domain);union=shapely.union_all(polygons);difference=float(union.symmetric_difference(shapely.box(*domain)).area)
save(DOC/'coverage-measurement.json',dict(float32SymmetricDifferenceAreaM2=difference,missingAreaM2=float(missing.area),roundoffAllowanceNeeded=difference>0,geometrySHA256=before))
try:
 if difference>0:save(DOC/'numerical-coverage.json',approve_roundoff(child,domain))
 overlap=module('harbourfront_wrapper_overlap_v2',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=DOC;overlap.overlap_proof(child,[p,Path(__file__)])
 builder=module('harbourfront_wrapper_validator_v2',HERE/'resolve-pass-indexed-parent-clipping.py');builder.validate_patch(parent,root);assert geometry_sha(child)==before
except Exception as exc:error=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc());save(DOC/'validation-failure.json',error)
out=LOCAL/'candidate-wrapper.json';save(out,parent);refs.append(out);descriptor=read(BASE/OLD/'terrain-candidates.json');descriptor[0].update(path=str(out.relative_to(ROOT)),sha256=digest(out.read_bytes()));save(DOC/'terrain-candidates.json',descriptor)
summary=dict(uids=['landsd/118230:0'],terrainValidationPassed=error is None,error=error,childTriangles=len(child['nativeMesh']['index'])//3,geometryUnchanged=True,sourceGeometryChanges=0,float32SymmetricDifferenceAreaM2=difference,installationApproved=False,qualification='V1 failed because roundoff metadata requires a positive residue, whereas this mesh has zero residue. No threshold changed. Actual native-mesh and grid validators run unchanged. Physical/runtime/neighbour/browser acceptance remains required.')
save(DOC/'summary.json',summary);refs.extend([HERE/'float32_coverage.py',HERE/'native_patch_resolution.py',HERE/'resolve-pass-indexed-parent-clipping.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py']);r=module('harbourfront_wrapper_v2_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'saved-private-whampoa-wrapper-validation',list(dict.fromkeys(refs)),summary);print(dict(jobId=r['jobId'],**summary),flush=True)
