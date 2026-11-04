"""Strict geometry validation of the private joint original-installation terrain.
The construction helper default is reported; runtime acceptance remains pending.
"""
from pathlib import Path
import json,traceback
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from native_patch_resolution import grid_surface_faces
from float32_coverage import approve_roundoff,geometry_sha
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-grandiose-joint-validation-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SOURCE=BASE/'government-xl-tko-grandiose-joint-surface-v3-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__)];hashes={}
 def take(folder,path):
  receipt,pins=authenticate(folder);key=str(path.relative_to(ROOT));assert digest(path.read_bytes())==pins[key];refs.extend([folder/'result.json',path]);hashes[key]=pins[key];return read(path)
 summary=take(SOURCE,SOURCE/'summary.json');path=HERE/'local'/SOURCE.name/'joint-terrain-faces.json.gz';faces=np.asarray(take(SOURCE,path)['triangles'])
 scopes=[]
 for name in ['government-xl-grandiose-regional-scope-v1-20261021','government-xl-tko-podium-regional-scope-v2-20261021']:
  folder=BASE/name;scopes.append(take(folder,folder/'scope.json'))
 cells=[min(s['regionalCoarseCells'][0]for s in scopes),min(s['regionalCoarseCells'][1]for s in scopes),max(s['regionalCoarseCells'][2]for s in scopes),max(s['regionalCoarseCells'][3]for s in scopes)]
 uids=sorted(set(u for s in scopes for u in s['uids']));retained=sorted(set(u for s in scopes for u in s['touchingNativeUids']))
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);refs.append(parentpath);hashes[str(parentpath.relative_to(ROOT))]=digest(parentpath.read_bytes())
 for scope in scopes:
  for entry in scope['retainedPatches']:
   p=ROOT/'3d-viewer'/entry['url'];assert digest(p.read_bytes())==entry['sha256'];refs.append(p);hashes[str(p.relative_to(ROOT))]=entry['sha256']
 builder=module('joint_validation_builder',HERE/'resolve-pass-indexed-parent-clipping.py');domain=builder.extent(cells,parent);assert list(domain)==summary['bounds']
 baseline=np.asarray(grid_surface_faces(builder.terrain.fine.DemSampler(parent,rendered=True),shapely.box(*domain)))
 candidate=builder.make_patch(dict(uids=uids,cells=cells),parent,baseline,[],allow_native_below_clamp=True)
 candidate['nativeMesh']['position']=faces.reshape(-1).tolist();candidate['nativeMesh']['index']=list(range(len(faces)*3))
 candidate['nativeMesh']['source']={'policy':'Joint source-ground planes preserved beneath original buildings; scripted transition between protected projections. Private, runtime approval pending.','verticalDatum':'HKPD','verticalScale':1}
 candidate['meta']['source']['policy']=candidate['nativeMesh']['source']['policy'];candidate['meta']['source']['nativeSources']=[dict(sourceFiles=[dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))])]
 before=geometry_sha(candidate);failure=None
 try:
  save(DOC/'numerical-coverage.json',approve_roundoff(candidate,domain))
  overlap=module('joint_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=DOC;overlap.overlap_proof(candidate,[path,Path(__file__)])
  builder.validate_patch(candidate,parent);assert geometry_sha(candidate)==before
 except Exception as exc:
  failure=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc());save(DOC/'validation-failure.json',failure)
 out=LOCAL/'candidate-terrain.json';save(out,candidate);refs.append(out)
 replacements={r['url']:r for s in scopes for r in s['retainedPatches']}
 save(DOC/'terrain-candidates.json',[dict(path=str(out.relative_to(ROOT)),sha256=digest(out.read_bytes()),uids=uids,bounds=domain,triangles=len(faces),replacesMany=[dict(url=r['url'],sha256=r['sha256'],retainedUids=retained)for r in replacements.values()])])
 result=dict(uids=uids,triangles=len(faces),terrainGeometryValidationPassed=failure is None,failure=failure,constructionDefaultTriangles=25000,exceedsConstructionDefault=len(faces)>25000,runtimeBudgetApproved=False,installationApproved=False,productionChanges=0,sourceGeometryChanges=0)
 save(DOC/'summary.json',result)
 for p,h in hashes.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend([HERE/'resolve-pass-indexed-parent-clipping.py',HERE/'float32_coverage.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py',HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/native_terrain_validation.py'])
 receipt=module('joint_validation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'strict-private-joint-terrain-validation',list(dict.fromkeys(refs)),result);print(json.dumps(dict(jobId=receipt['jobId'],**result)),flush=True)
if __name__=='__main__':main()
