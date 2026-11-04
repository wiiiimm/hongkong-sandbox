"""Stage an original-government terrain patch for the unchanged Illumination pair."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-illumination-private-terrain-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
GROUND=BASE/'government-xl-illumination-original-ground-v1-20261021';SCOPE=BASE/'government-xl-illumination-terrain-scope-v1-20261021'
def main():
 assert not DOC.exists();_,gp=authenticate(GROUND);_,sp=authenticate(SCOPE);refs=[Path(__file__),GROUND/'result.json',SCOPE/'result.json']
 def take(p,pins):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 scope=take(SCOPE/'scope.json',sp);assert not scope['overlappingTerrain'];parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=take(parentpath,sp);manifest=ROOT/'3d-viewer/city/data/manifest.json';take(manifest,sp)
 decoder=module('illumination_private_decode',HERE/'xl-second-pass.py');decoder.LOCAL=LOCAL;source=[];tri=[]
 for name,sha in gp.items():
  if '/terrain/'not in name or not name.endswith('.gltf'):continue
  p=ROOT/name;assert digest(p.read_bytes())==sha;refs.append(p)
  for uri in read(p).get('buffers',[]):
   q=p.parent/uri['uri'];assert digest(q.read_bytes())==gp[str(q.relative_to(ROOT))];refs.append(q)
  tri.append(decoder.terrain_triangles(p));source.append(dict(path=name,sha256=sha))
 assert tri
 native=np.concatenate(tri);bb=scope['baseReplacementExtent'];native=native[(native[:,:,0].max(1)>=bb[0])&(native[:,:,0].min(1)<=bb[2])&(native[:,:,2].max(1)>=bb[1])&(native[:,:,2].min(1)<=bb[3])]
 builder=module('illumination_private_builder',HERE/'resolve-pass-indexed-parent-clipping.py');patch=builder.make_patch(dict(cells=scope['baseReplacementCells'],uids=scope['uids']),parent,native,source,parent_sha256=digest(parentpath.read_bytes()));path=LOCAL/'candidate-terrain.json';save(path,patch)
 save(DOC/'terrain-candidates.json',[dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uids=scope['uids'],bounds=bb,triangles=len(patch['nativeMesh']['index'])//3)])
 refs.extend([path,HERE/'resolve-pass-indexed-parent-clipping.py',HERE/'xl-second-pass.py']);module('illumination_private_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-original-terrain-candidate',refs,dict(uids=scope['uids'],terrainTriangles=len(patch['nativeMesh']['index'])//3,installationApproved=False,sourceGeometryChanges=0));print(len(patch['nativeMesh']['index'])//3,flush=True)
if __name__=='__main__':main()
