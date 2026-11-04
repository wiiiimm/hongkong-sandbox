"""Private terrain candidate preserving current ground under separate Oi Yuk House."""
import json,subprocess,uuid
from pathlib import Path
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-oi-sin-podium-terrain-v1-20261017'
BATCH='government-xl-oi-sin-preserve-oi-yuk-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PODIUM='landsd/91128:0';NEIGHBOUR='landsd/256824:0'
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+PODIUM,'terrain-patch:'+PODIUM,'building:'+NEIGHBOUR],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  selection=read(PRIOR/'selection.json.gz');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];row=selection['rows'][0];assert row['uid']==PODIUM
  old=read(PRIOR/'terrain.json');original=old['patch'];asset=ROOT/original['path'];assert digest(asset.read_bytes())==original['sha256'];patch=read(asset);bounds=original['bounds'];parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath)
  inputs=read(PRIOR/'neighbour-inputs.json.gz');b=next(r['building']for r in inputs['rows']if r['building']['uid']==NEIGHBOUR)
  from exact_packed_world_geometry_20261009 import decode_original_world_triangles
  raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));protected=Polygon(b['rings'][0],b['rings'][1:]).buffer(1,join_style='mitre');assert protected.intersection(projection).area==0
  second=module('oi_yuk_terrain',HERE/'xl-second-pass.py');patches=module('oi_yuk_patch',HERE/'native_patch_resolution.py');sampler=second.resolution.terrain.fine.DemSampler(parent,rendered=True)
  proof=patches.preserve_parent_under_projection(patch,bounds,protected,sampler);patches.fill_parent_only_holes(patch,parent,bounds,projection,sampler);patch['nativeMesh']['source']['finalBoundarySnap']=patches.snap_boundary_to_parent(patch,bounds,sampler)
  target=LOCAL/'oi-sin-oi-yuk-preserved.json';save(target,patch)
  if patches.projected_context(patch,bounds)[3]>1e-8:
   patches.approve_original_overlap(patch,target,DOC/'overlap.json',old['sourceFiles']);patches.finalize_overlap_evidence(patch,DOC/'overlap.json')
  else:patch['nativeMesh'].pop('sourceOverlap',None)
  second.resolution.validate_patch(patch,parent);save(target,patch)
  revised=dict(original,path=str(target.relative_to(ROOT)),sha256=digest(target.read_bytes()),triangles=len(patch['nativeMesh']['index'])//3)
  save(DOC/'terrain-candidates.json',[revised]);inputs['patches']=[revised];save(DOC/'neighbour-inputs.json.gz',inputs);save(DOC/'selection.json.gz',selection);save(DOC/'preservation.json',dict(uid=NEIGHBOUR,proof=proof,distanceFromOriginalPodiumM=protected.distance(projection),sourceProjectionIntersectionM2=0,originalPatch=original,revisedPatch=revised,publication=False))
  subprocess.run(['node',str(HERE/'check-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
  assert reservations.owns(lease)and digest(manifest.read_bytes())==selection['manifestSHA256']
  checks=read(DOC/'neighbour-checks.json');remaining=[r for r in checks['rows']if r['reasons']];refs=[Path(__file__),PRIOR/'result.json',PRIOR/'terrain.json',PRIOR/'selection.json.gz',PRIOR/'neighbour-inputs.json.gz',asset,target,parentpath,manifest,ROOT/row['candidate']['path'],HERE/'native_patch_resolution.py',HERE/'check-neighbours.mjs']
  for p,h in checks['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  out=module('oi_yuk_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-separate-oi-yuk-current-ground-preserved-v1',refs,dict(uids=[PODIUM,NEIGHBOUR],remainingNeighbourFailures=remaining,fullAcceptance=False,nextStep='Validate the revised podium foundation/loader and resolve three same-building raised parts. Complete all-current native scope and browser checks before any publication.'))
  print(dict(jobId=out['jobId'],remaining=[r['uid']for r in remaining]),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
