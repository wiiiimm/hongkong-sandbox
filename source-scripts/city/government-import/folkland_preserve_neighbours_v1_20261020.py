"""Preserve existing terrain beneath four neighbours outside the original Folkland pair."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from rendered_patch_sampler import RenderedPatchSampler
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import native_patch_resolution as repair
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-folkland-preserve-neighbours-v1-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-folkland-neighbours-v1-20261020';CAP=BASE/'government-xl-folkland-pair-candidate-foundations-v1-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [SRC,CAP]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 def consume(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 descriptor=consume(CAP/'terrain-candidates.json')[0];patch=consume(ROOT/descriptor['path']);inputs=consume(SRC/'neighbour-inputs.json.gz');checks=consume(SRC/'neighbour-checks.json');selection=consume(CAP/'selection.json.gz');byuid={r['building']['uid']:r['building']for r in inputs['rows']};flagged=[r['uid']for r in checks['rows']if r['reasons']and not r['existingNative']and r['uid']not in ['landsd/264677:0','landsd/225387:0']];assert set(flagged)=={'landsd/264680:0','landsd/264681:0','landsd/20270:0','landsd/274231:0'}
 faces=[]
 for r in selection['rows']:
  p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p);faces.extend(decode_original_world_triangles(p.read_bytes()))
 tri=np.asarray(faces);projection=shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in tri]);protected=shapely.union_all([Polygon(byuid[u]['rings'][0],byuid[u]['rings'][1:]).buffer(.01,join_style='mitre')for u in flagged]).difference(projection.buffer(.01,join_style='mitre'))
 assert protected.area>0 and protected.intersection(projection).area==0
 builder=module('folkland_preservation_builder',HERE/'resolve-pass-indexed-parent-clipping.py');rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=read(rootpath);refs.append(rootpath);parentpath=ROOT/'3d-viewer'/descriptor['replaces']['url'];parent=consume(parentpath);grid=builder.terrain.fine.DemSampler(root,rendered=True);parentgrid=builder.terrain.fine.DemSampler(parent,rendered=True);sampler=RenderedPatchSampler(parent,grid,parentgrid)
 bounds=consume(SRC/'actor-scope.json')['changedParentExtent'];DOC.mkdir();patch['nativeMesh'].pop('sourceOverlap',None)
 proof=repair.preserve_parent_under_projection(patch,bounds,protected,sampler,edge_sampler=grid);save(DOC/'preservation.json',dict(proof=proof,neighbours=flagged,sourceProjectionIntersectionM2=0,sourceFaces=len(tri)))
 raw=DOC/'unapproved-terrain.json';save(raw,patch);sources=[parentpath,ROOT/descriptor['path'],DOC/'preservation.json'];audit=repair.approve_original_overlap(patch,raw,DOC/'native-overlap.json',[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in sources]);repair.finalize_overlap_evidence(patch,DOC/'native-overlap.json');builder.validate_patch(patch,root);count=len(patch['nativeMesh']['index'])//3;assert count<=100000
 target=DOC/'candidate-terrain.json';save(target,patch);descriptor.update(path=str(target.relative_to(ROOT)),sha256=digest(target.read_bytes()));save(DOC/'terrain-candidates.json',[descriptor]);save(DOC/'summary.json',dict(uids=['landsd/264677:0','landsd/225387:0'],preservedNeighbours=flagged,terrainFaces=count,terrainValidatorPassed=True,sourceGeometryChanges=0,installationApproved=False,nextStep='Repeat complete foundation and neighbour checks against these exact bytes.'))
 refs.extend([raw,target,HERE/'native_patch_resolution.py',HERE/'rendered_patch_sampler.py',HERE/'resolve-pass-indexed-parent-clipping.py',HERE/'exact_packed_world_geometry_20261009.py']);module('folkland_preserved_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-disjoint-neighbour-terrain-preservation',refs,read(DOC/'summary.json'));print(read(DOC/'summary.json'),flush=True)
if __name__=='__main__':main()
