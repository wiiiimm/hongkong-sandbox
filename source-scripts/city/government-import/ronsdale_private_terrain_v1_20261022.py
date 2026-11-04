"""Stage an original-government terrain patch for the unchanged Ronsdale podium."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-private-terrain-v1-20261022';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
GROUND=BASE/'government-xl-ronsdale-podium-original-ground-v1-20261022';SCOPE=BASE/'government-xl-ronsdale-terrain-scope-v2-20261022'
def main():
 assert not DOC.exists();_,gp=authenticate(GROUND);_,sp=authenticate(SCOPE);refs=[Path(__file__),GROUND/'result.json',SCOPE/'result.json']
 adjacent=BASE/'government-xl-ronsdale-adjacent-ground-v1-20261022';_,ap=authenticate(adjacent);refs.append(adjacent/'result.json')
 for name,h in ap.items():
  assert name not in gp or gp[name]==h;gp[name]=h
 def take(p,pins):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 scope=take(SCOPE/'scope.json',sp);assert not scope['overlappingTerrain'];parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=take(parentpath,sp);manifest=ROOT/'3d-viewer/city/data/manifest.json';take(manifest,sp)
 decoder=module('ronsdale_private_decode',HERE/'xl-second-pass.py');decoder.LOCAL=LOCAL;source=[];tri=[]
 for name,sha in gp.items():
  if '/terrain/'not in name or not name.endswith('.gltf'):continue
  p=ROOT/name;assert digest(p.read_bytes())==sha;refs.append(p)
  for uri in read(p).get('buffers',[]):
   q=p.parent/uri['uri'];assert digest(q.read_bytes())==gp[str(q.relative_to(ROOT))];refs.append(q)
  tri.append(decoder.terrain_triangles(p));source.append(dict(path=name,sha256=sha))
 assert tri
 native=np.concatenate(tri);bb=scope['baseReplacementExtent'];native=native[(native[:,:,0].max(1)>=bb[0])&(native[:,:,0].min(1)<=bb[2])&(native[:,:,2].max(1)>=bb[1])&(native[:,:,2].min(1)<=bb[3])]
 builder=module('ronsdale_private_builder',HERE/'resolve-pass-indexed-parent-clipping.py')
 original_validate=builder.validate_patch
 def capture_and_validate(p,parent):
  import shapely
  save(DOC/'failed-or-proposed-terrain.json',p)
  faces=np.asarray(p['nativeMesh']['position']).reshape(-1,3,3);polys=shapely.polygons(faces[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;union=shapely.union_all(polys[valid]);domain=shapely.box(*bb)
  save(DOC/'overlap-diagnostic.json',dict(triangles=len(faces),projectedExcessM2=float(shapely.area(polys[valid]).sum()-union.area),coverageDifferenceM2=float(union.symmetric_difference(domain).area),validationUnchanged=True,installationApproved=False))
  original_validate(p,parent)
 builder.validate_patch=capture_and_validate
 patch=builder.make_patch(dict(cells=scope['baseReplacementCells'],uids=scope['uids']),parent,native,source,parent_sha256=digest(parentpath.read_bytes()));path=LOCAL/'candidate-terrain.json';save(path,patch)
 save(DOC/'terrain-candidates.json',[dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uids=scope['uids'],bounds=bb,triangles=len(patch['nativeMesh']['index'])//3)])
 refs.extend([path,HERE/'resolve-pass-indexed-parent-clipping.py',HERE/'xl-second-pass.py']);module('ronsdale_private_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-original-terrain-candidate',refs,dict(uids=scope['uids'],terrainTriangles=len(patch['nativeMesh']['index'])//3,installationApproved=False,sourceGeometryChanges=0));print(len(patch['nativeMesh']['index'])//3,flush=True)
if __name__=='__main__':main()
