"""Construct a private station TIN nested inside the unchanged current regional parent."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ets-nested-runtime-candidate-v1-20261015';DOC=BASE/BATCH
PARENT='city/data/terrain-government-xl-caine-road-original-pair-installed-v2-20261010.json';UID='landsd/323703:0'
def main():
 assert not DOC.exists();prior=BASE/'government-xl-ets-residual-source-floor-v2-20261015';receipt=read(prior/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 refs=[Path(__file__),prior/'result.json']
 for q in receipt['evidenceRefs']:
  p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p)
 source=next(r for r in read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows']if r['modelId']=='B360171738601063C0');asset=ROOT/source['asset']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());lo,hi=tri.min((0,1)),tri.max((0,1))
 parentpath=ROOT/'3d-viewer'/PARENT;manifestpath=ROOT/'3d-viewer/city/data/manifest.json';parent=read(parentpath);manifest=read(manifestpath);assert any(x['url']==PARENT for x in manifest['terrainPatches']);pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in [parentpath,manifestpath]};refs.extend([parentpath,manifestpath])
 build=module('ets_nested_builder',HERE/'resolve-pass-indexed-parent-clipping.py');refs.append(HERE/'resolve-pass-indexed-parent-clipping.py');cells=build.rectangle_for([lo,hi],parent);assert 0<=cells[0]<cells[2]<parent['w']and 0<=cells[1]<cells[3]<parent['h'];assert not any(build.terrain.overlap(cells,p['coarseCells'])for p in parent.get('patches',[]));bounds=build.extent(cells,parent)
 native=np.asarray(read(prior/'private-terrain.json.gz')['allCandidateTerrainTriplets']);native=native[(native[:,:,0].max(1)>=bounds[0])&(native[:,:,0].min(1)<=bounds[2])&(native[:,:,2].max(1)>=bounds[1])&(native[:,:,2].min(1)<=bounds[3])];assert len(native)
 DOC.mkdir();plan={'uid':UID,'sourceSHA256':source['sourceSHA256'],'nestedCells':cells,'nestedBounds':bounds,'currentPins':pins,'parentURL':PARENT,'retainedNestedPatches':[{'id':p.get('id'),'logicalSHA256':digest(__import__('json').dumps(p,sort_keys=True,separators=(',',':')).encode())}for p in parent.get('patches',[])],'sourceGeometryChanges':0,'publication':False};save(DOC/'plan.json',plan)
 original_validator=build.validate_patch
 def capture_then_validate(p,parent):
  save(DOC/'private-patch.json.gz',p)
  return original_validator(p,parent)
 build.validate_patch=capture_then_validate
 try:
  candidate=build.make_patch({'uids':[UID],'cells':cells},parent,native,[{'sourceCandidate':str((prior/'private-terrain.json.gz').relative_to(ROOT)),'sha256':digest((prior/'private-terrain.json.gz').read_bytes()),'privateSourceBoundedTerrainRepair':True}],native_core=[lo[0]-1,lo[2]-1,hi[0]+1,hi[2]+1],parent_url=PARENT,parent_sha256=pins[str(parentpath.relative_to(ROOT))],terrain_triangle_budget=100000)
  summary={'patchValidationPassed':True,'triangles':len(candidate['nativeMesh']['index'])//3}
 except (AssertionError,ValueError)as e:summary={'patchValidationPassed':False,'error':str(e)}
 finally:build.validate_patch=original_validator
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 summary.update(nestedCells=cells,nestedBounds=bounds,retainedNestedPatchCount=len(parent.get('patches',[])),regionalNativeTriangles=len(native),publication=False,fullAcceptance=False);save(DOC/'summary.json',summary)
 module('freeze_ets_nested',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-station-nested-runtime-candidate-v1',refs,{'uids':[UID],'summary':summary,'fullAcceptance':False});print(summary,flush=True)
if __name__=='__main__':main()
