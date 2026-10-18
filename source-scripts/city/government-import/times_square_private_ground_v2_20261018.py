"""Bounded private source-terrain candidate for Times Square; no publication."""
import json,sys,uuid,subprocess,traceback
from pathlib import Path
import numpy as np,shapely
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from shapely.geometry import box
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-times-square-private-ground-v2-20261018';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SRC=BASE/'government-xl-next-five-adjoining-ground-v1-20261018';CAP=BASE/'government-xl-next-five-current-terrain-v1-20261018';UID='landsd/233901:0'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [SRC,CAP]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=next(r for r in read(CAP/'selection.json.gz')['rows']if r['uid']==UID);manifestpath=ROOT/'3d-viewer/city/data/manifest.json';parentpath=ROOT/'3d-viewer/city/data/terrain.json';manifest=read(manifestpath);parent=read(parentpath);builder=module('times_ground_constructor',HERE/'resolve-pass-indexed-parent-clipping.py');cells=builder.rectangle_for(row['candidate']['entry']['worldBounds'],parent);bounds=builder.extent(cells,parent)
 for e in manifest['terrainPatches']:
  p=read(ROOT/'3d-viewer'/e['url']);g=p['meta']['georef'];extent=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(p['w']-1)*g['aE'],816500-g['bN']-(p['h']-1)*g['aN']]
  assert box(*bounds).intersection(box(*extent)).area<=1e-8,('existing terrain overlap',e['url'])
 groundpath=HERE/'local'/SRC.name/'233901:0-ground.json.gz';ground=read(groundpath);native=np.asarray(ground['completeAdjoiningTerrain']);native=native[(native[:,:,0].max(1)>=bounds[0])&(native[:,:,0].min(1)<=bounds[2])&(native[:,:,2].max(1)>=bounds[1])&(native[:,:,2].min(1)<=bounds[3])]
 lo,hi=row['candidate']['entry']['worldBounds'];core=[lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2];sources=[r for r in read(SRC/'acquisitions.json')if r['sheet']in ground['sheets']];DOC.mkdir();save(DOC/'scope.json',dict(uid=UID,coarseCells=cells,changedParentExtent=bounds,originalCore=core,sourceTerrainFaces=len(native),existingTerrainOverlaps=[],allActorNominationPending=True,identityApprovalPending=True))
 error=None
 try:
  validator=builder.validate_patch
  builder.validate_patch=lambda *_:None
  try:patch=builder.make_patch(dict(uids=[UID],cells=cells),parent,native,sources,native_core=core,terrain_triangle_budget=1000000)
  finally:builder.validate_patch=validator
  # Private intermediate only: restore exact existing parent planes outside the
  # complete source projection before subjecting the finished patch to all guards.
  repair=module('times_parent_preservation',HERE/'native_patch_resolution.py')
  tri=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());xz=tri[:,:,[0,2]]
  projection=shapely.union_all([shapely.union_all(shapely.polygons(xz)),shapely.union_all(shapely.linestrings(np.concatenate([xz,xz[:,:1]],axis=1))),shapely.union_all(shapely.points(xz.reshape(-1,2)))])
  protected=projection.buffer(1,join_style='mitre');region=box(*bounds).difference(protected);assert region.intersection(projection).area<1e-8
  sampler=builder.terrain.fine.DemSampler(parent,rendered=True)
  preservation=repair.preserve_parent_under_projection(patch,bounds,region,sampler);save(DOC/'parent-preservation.json',preservation)
  gap=repair.projected_context(patch,bounds)[2].intersection(projection)
  fill=repair.fill_narrow_source_seam(patch,bounds,projection,sampler,tolerance=.02)if gap.area>1e-6 else repair.fill_parent_only_holes(patch,parent,bounds,projection,sampler)
  save(DOC/'hole-fill.json',fill);remaining=repair.projected_context(patch,bounds)[2].area;maximum=max(.25,(bounds[2]-bounds[0])*(bounds[3]-bounds[1])*1e-3);assert remaining<=maximum
  if remaining>1e-8:patch['nativeMesh']['source']['numericalCoverageGap']=dict(policy='parent-grid-fallback',measuredAreaM2=float(remaining),maximumAreaM2=maximum,maximumFraction=1e-3)
  patch['nativeMesh']['source']['finalBoundarySnap']=repair.snap_boundary_to_parent(patch,bounds,sampler)
  path=LOCAL/'terrain-times-square.json';save(path,patch)
  if repair.projected_context(patch,bounds)[3]>1e-8:
   files=[]
   for source in sources:
    for name in source['terrainPaths']:
     gltf=ROOT/name;files.append(dict(path=name,sha256=digest(gltf.read_bytes())))
     for buffer in read(gltf)['buffers']:
      q=gltf.parent/buffer['uri'];files.append(dict(path=str(q.relative_to(ROOT)),sha256=digest(q.read_bytes())))
   repair.approve_original_overlap(patch,path,DOC/'native-overlap.json',files);repair.finalize_overlap_evidence(patch,DOC/'native-overlap.json')
  assert len(patch['nativeMesh']['index'])//3<=100000
  validator(patch,parent)
  refs.append(HERE/'native_patch_resolution.py')
  path=LOCAL/'terrain-times-square.json';save(path,patch);save(DOC/'terrain-candidates.json',[dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uids=[UID],coarseCells=cells)])
  asset=LOCAL/row['candidate']['entry']['asset'];asset.parent.mkdir(parents=True,exist_ok=True);raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];asset.write_bytes(raw);row['candidate']['path']=str(asset.relative_to(ROOT));save(DOC/'selection.json.gz',dict(rows=[row],manifestSHA256=digest(manifestpath.read_bytes())))
  command=['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
  with(DOC/'worker.log').open('w')as log:subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
  m=read(DOC/'metrics.json');assert len(m['rows'])==1 and not m['rows'][0].get('error');print(m['rows'][0],flush=True)
  for p,h in m['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 except Exception as exc:
  error=str(exc);save(DOC/'guard-failure.json',dict(error=error,traceback=traceback.format_exc(),installationApproved=False));print('Candidate guard:',error,flush=True)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 assert reservations.owns(lease);refs.extend(ROOT/p for p in pins);refs.extend([groundpath,parentpath,manifestpath,HERE/'resolve-pass-indexed-parent-clipping.py']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 module('times_private_ground_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'times-square-private-original-terrain-candidate',list(dict.fromkeys(refs)),dict(uids=[UID],guardFailure=error,installationApproved=False,identityApprovalPending=True,neighbourNominationPending=True))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+UID,'terrain-patch:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
