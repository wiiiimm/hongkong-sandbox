"""Strictly validate a bounded private child in the current retained wrapper."""
from pathlib import Path
import copy,traceback
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from native_patch_resolution import grid_surface_faces
from float32_coverage import approve_roundoff,geometry_sha
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-piers-private-wrapper-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
assert not DOC.exists();refs=[Path(__file__)];pins={}
def take(name,p):
 r,ps=authenticate(BASE/name);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/name/'result.json',p]);return read(p)
sc='government-xl-central-piers-current-scope-v1-20261021';scope=take(sc,BASE/sc/'scope.json');wp=ROOT/'3d-viewer'/scope['replacedWrapper']['url'];parent=take(sc,wp);root=take(sc,ROOT/'3d-viewer/city/data/terrain.json');domain=scope['localChildBounds'];builder=module('china_private_builder',HERE/'resolve-pass-indexed-parent-clipping.py');sampler=builder.terrain.fine.DemSampler(parent,rendered=True)
g=parent['meta']['georef'];rawcells=[(domain[0]+834500-g['bE'])/g['aE'],(816500-g['bN']-domain[1])/g['aN'],(domain[2]+834500-g['bE'])/g['aE'],(816500-g['bN']-domain[3])/g['aN']];cells=[round(v)for v in rawcells];assert np.allclose(rawcells,cells) and np.allclose(builder.extent(cells,parent),domain)
baseline=np.asarray(grid_surface_faces(sampler,shapely.box(*domain)));child=builder.make_patch(dict(uids=scope['uids'],cells=cells),parent,baseline,[],parent_url=scope['replacedWrapper']['url'],parent_sha256=scope['replacedWrapper']['sha256'],allow_native_below_clamp=True)
cn='government-xl-central-piers-combined-ground-v1-20261021';fp=HERE/'local'/cn/'bounded-terrain.json.gz';faces=np.asarray(take(cn,fp)['triangles']);child['nativeMesh']['position']=faces.reshape(-1).tolist();child['nativeMesh']['index']=list(range(len(faces)*3));policy='Private pier terrain floors with two metre collars and eight metre transitions to current rendered terrain. Government building geometry is unchanged.'
child['nativeMesh']['source']={'policy':policy,'verticalDatum':'HKPD','verticalScale':1,'evidence':dict(path=str((BASE/cn/'result.json').relative_to(ROOT)),sha256=digest((BASE/cn/'result.json').read_bytes()))};child['meta']['source']['policy']=policy;child['meta']['source']['nativeSources']=[dict(sourceFiles=[dict(path=str(fp.relative_to(ROOT)),sha256=digest(fp.read_bytes()))])]
before=geometry_sha(child);error=None
try:
 save(DOC/'numerical-coverage.json',approve_roundoff(child,domain))
 overlap=module('china_private_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=DOC;overlap.overlap_proof(child,[fp,Path(__file__)])
 builder.validate_patch(child,parent);assert geometry_sha(child)==before
except Exception as exc:
 error=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc());save(DOC/'validation-failure.json',error)
combined=copy.deepcopy(parent);replace_index=scope['proposedReplacedChildIndex'];combined['patches'][replace_index]=child;assert all(c==parent['patches'][i] for i,c in enumerate(combined['patches']) if i!=replace_index)
if error is None:
 try:builder.validate_patch(combined,root)
 except Exception as exc:
  error=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc());save(DOC/'validation-failure.json',error)
out=LOCAL/'candidate-wrapper.json';save(out,combined);refs.append(out)
descriptor=dict(path=str(out.relative_to(ROOT)),sha256=digest(out.read_bytes()),uids=scope['uids'],bounds=scope['completeParentAndPackedExtent'],triangles=len(faces),replaces=dict(url=scope['replacedWrapper']['url'],sha256=scope['replacedWrapper']['sha256'],retainedUids=scope['touchingNativeUids']))
save(DOC/'terrain-candidates.json',[descriptor]);summary=dict(uids=scope['uids'],terrainValidationPassed=error is None,error=error,childTriangles=len(faces),retainedChildren=len(parent['patches'])-1,allOtherChildrenVerbatim=True,replacedChildIndex=replace_index,geometryUnchangedDuringValidation=geometry_sha(child)==before,installationApproved=False)
save(DOC/'summary.json',summary)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
refs.extend(HERE/n for n in ['resolve-pass-indexed-parent-clipping.py','float32_coverage.py','native_patch_resolution.py','sham_shui_po_pool_shared_terrain_v2_20261016.py'])
r=module('china_wrapper_freeze2',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-current-wrapper-child-validation',refs,summary);print(dict(jobId=r['jobId'],**summary),flush=True)
