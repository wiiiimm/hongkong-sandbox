"""Run private source-driven floor candidates through unchanged patch construction."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-unmapped-floor-patch-probe-v1-20261015';DOC=BASE/BATCH

def main():
 assert not DOC.exists();DOC.mkdir();prev=BASE/'government-xl-unmapped-source-floor-candidate-v1-20261015';r=read(prev/'result.json');paths=[Path(__file__),prev/'result.json']
 for q in r['evidenceRefs']:
  p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];paths.append(p)
 resolution=module('unmapped_patch_probe',HERE/'resolve-pass.py');paths.append(HERE/'resolve-pass.py');parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);paths.extend([parentpath,manifestpath]);bindingpath=BASE/'government-xl-unmapped-two-primary-evidence-v1-20261015/viewer-bindings.json';bindings=read(bindingpath)['rows'];paths.append(bindingpath);out=[]
 recovery=read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows']
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 for row in r['rows']:
  model=row['modelId'];binding=next(b for b in bindings if b['modelId']==model);uids=[b['viewerUID']for b in binding['bindings']];source=next(s for s in recovery if s['modelId']==model);asset=ROOT/source['asset']['path'];paths.append(asset);tri=decode_original_world_triangles(asset.read_bytes());lo,hi=tri.min((0,1)),tri.max((0,1));cells=resolution.rectangle_for([lo,hi],parent);bounds=resolution.extent(cells,parent);overlaps=[]
  for entry in manifest['terrainPatches']:
   p=ROOT/'3d-viewer'/entry['url'];patch=read(p);paths.append(p)
   if resolution.terrain.overlap(cells,patch['coarseCells']):overlaps.append(entry['url'])
  data=read(prev/(model+'-private-terrain.json.gz'));native=np.asarray(data['allCandidateTerrainTriplets']);mask=(native[:,:,0].max(1)>=bounds[0])&(native[:,:,0].min(1)<=bounds[2])&(native[:,:,2].max(1)>=bounds[1])&(native[:,:,2].min(1)<=bounds[3]);native=native[mask]
  result={'modelId':model,'uids':uids,'cells':cells,'bounds':bounds,'overlappingInstalledPatches':overlaps,'regionalNativeTriangles':len(native),'sourceGeometryChanges':0,'installationApproved':False}
  try:
   assert not overlaps,'Existing patch overlap requires a coordinated replacement, not an additional overlapping patch'
   candidate=resolution.make_patch({'uids':uids,'cells':cells},parent,native,[{'sourceCandidate':str((prev/(model+'-private-terrain.json.gz')).relative_to(ROOT)),'sha256':digest((prev/(model+'-private-terrain.json.gz')).read_bytes()),'privateFloorRepair':True}],native_core=[lo[0]-1,lo[2]-1,hi[0]+1,hi[2]+1],terrain_triangle_budget=100000)
   save(DOC/(model+'-patch.json.gz'),candidate);result['patchValidationPassed']=True
  except (AssertionError,ValueError)as e:result.update(patchValidationPassed=False,error=str(e))
  out.append(result);print(result,flush=True)
 save(DOC/'probe.json',{'rows':out,'publication':False})
 module('freeze_floor_patch_probe',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-native-patch-construction-probe-v1',paths,{'uids':sorted({u for row in out for u in row['uids']}),'rows':out,'liveTerrainChanged':False,'fullAcceptance':False})
if __name__=='__main__':main()
