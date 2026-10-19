"""Stage original-source terrain against current parent; never publish or waive checks."""
import json, sys, uuid, subprocess
import numpy as np, shapely
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-sheung-shui-candidate-terrain-v5-20261020'
BASE=ROOT/'docs/astra-city/government-import'; DOC=BASE/BATCH; LOCAL=HERE/'local'/BATCH
SCOPE=BASE/'government-xl-next-twenty-current-scope-v1-20261020'
GROUND=BASE/'government-xl-sheung-shui-full-domain-ground-v1-20261020'
def owned():
 lease=read(LOCAL/'reservation.json'); assert reservations.owns(lease)
 pins={};refs=[HERE/'sheung_shui_candidate_terrain_v5_20261020.py']
 for folder in [SCOPE,GROUND,BASE/'government-xl-sheung-shui-candidate-terrain-v1-20261020',BASE/'government-xl-sheung-shui-neighbours-v1-20261020']:
  r=read(folder/'result.json')
  with connect() as db:
   db.execute('SET TRANSACTION READ ONLY')
   assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256']
   pins[e['path']]=e['sha256']
 for p,h in pins.items(): assert digest((ROOT/p).read_bytes())==h,p
 uid='landsd/56054:0';scope=next(r for r in read(SCOPE/'scope.json')['rows']if r['uid']==uid)
 assert not scope['touchingBaseDomainNativeUids'] and not scope['overlappingInstalledTerrain']
 selection=BASE/'government-xl-next-twenty-current-terrain-v2-20261020/selection.json.gz'
 row=next(r for r in read(selection)['rows']if r['uid']==uid);refs.append(selection)
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath)
 builder=module('sheung_candidate_builder',HERE/'resolve-pass-indexed-parent-clipping.py');refs.append(HERE/'resolve-pass-indexed-parent-clipping.py')
 cells=builder.rectangle_for(row['candidate']['entry']['worldBounds'],parent);assert cells==scope['baseReplacementCells']
 groundpath=HERE/'local'/GROUND.name/'56054:0-ground.json.gz';native=np.asarray(read(groundpath)['completeAdjoiningTerrain']);refs.append(groundpath)
 bb=builder.extent(cells,parent);lo=native[:,:,[0,2]].min(axis=1);hi=native[:,:,[0,2]].max(axis=1)
 native=native[(hi[:,0]>=bb[0])&(lo[:,0]<=bb[2])&(hi[:,1]>=bb[1])&(lo[:,1]<=bb[3])]
 print('nominated terrain triangles',len(native),flush=True)
 sources=read(GROUND/'acquisitions.json');result=dict(uids=[uid],installationApproved=False,sourceGeometryModified=False,scopeReceipt=read(SCOPE/'result.json')['jobId'],nominatedTerrainTriangles=len(native),touchingInstalledActors=0)
 low=native[:,:,1].min(axis=1)<1.2
 save(DOC/'native-elevation-context.json',dict(minimumSourceHeight=float(native[:,:,1].min()),sourceFacesBelowDisplayClamp=int(low.sum()),policy='Preserve original native elevations; parent water mask and full native validation remain mandatory.'))
 validate=builder.validate_patch
 def capture_then_validate(p,parent):
  save(LOCAL/'pre-validation-terrain.json',p)
  repair=module('sheung_bounded_repair',HERE/'native_patch_resolution.py');refs.append(HERE/'native_patch_resolution.py')
  original=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());xz=original[:,:,[0,2]]
  projection=shapely.union_all([shapely.union_all(shapely.polygons(xz)),shapely.union_all(shapely.linestrings(np.concatenate([xz,xz[:,:1]],axis=1))),shapely.union_all(shapely.points(xz.reshape(-1,2)))])
  sampler=builder.terrain.fine.DemSampler(parent,rendered=True)
  protected=projection.buffer(1,join_style='mitre');region=shapely.box(*bb).difference(protected);assert region.intersection(projection).area<1e-8
  preservation=repair.preserve_parent_under_projection(p,bb,region,sampler);save(DOC/'parent-preservation.json',preservation)
  gap=repair.projected_context(p,bb)[2].intersection(projection)
  fill=repair.fill_narrow_source_seam(p,bb,projection,sampler,tolerance=.02)if gap.area>1e-6 else repair.fill_parent_only_holes(p,parent,bb,projection,sampler)
  save(DOC/'hole-fill.json',fill)
  remaining=repair.projected_context(p,bb)[2].area
  assert remaining<=.25,'residual-gap-exceeds-quarter-square-metre'
  if remaining>1e-8:p['nativeMesh']['source']['numericalCoverageGap']=dict(policy='parent-grid-fallback',measuredAreaM2=float(remaining),maximumAreaM2=.25)
  p['nativeMesh']['source']['finalBoundarySnap']=repair.snap_boundary_to_parent(p,bb,sampler)
  path=LOCAL/'repaired-before-validation.json';save(path,p);refs.append(path)
  if repair.projected_context(p,bb)[3]>1e-8:
   files=[]
   for source in sources:
    for name in source['terrainPaths']:
     gltf=ROOT/name;files.append(dict(path=name,sha256=digest(gltf.read_bytes())))
     for buf in read(gltf)['buffers']:
      q=gltf.parent/buf['uri'];files.append(dict(path=str(q.relative_to(ROOT)),sha256=digest(q.read_bytes())))
   repair.approve_original_overlap(p,path,DOC/'native-overlap.json',files);repair.finalize_overlap_evidence(p,DOC/'native-overlap.json')
  save(LOCAL/'repaired-final.json',p);refs.append(LOCAL/'repaired-final.json')
  return validate(p,parent)
 builder.validate_patch=capture_then_validate
 try:
  patch=builder.make_patch(dict(uids=[uid],cells=cells),parent,native,sources,allow_native_below_clamp=bool(low.any()))
  save(LOCAL/'candidate-terrain.json',patch);refs.append(LOCAL/'candidate-terrain.json')
  result.update(candidateBuilt=True,terrainTriangles=len(patch['nativeMesh']['index'])//3,nextStep='Complete rendered-surface, boundary, owned-model and basic-neighbour acceptance before publication')
 except AssertionError as e:
  result.update(candidateBuilt=False,failedGuard=str(e),nextStep='Resolve the specific terrain constructor guard without changing government building geometry or acceptance thresholds')
 if (LOCAL/'pre-validation-terrain.json').exists():refs.append(LOCAL/'pre-validation-terrain.json')
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 assert reservations.owns(lease);refs.extend(ROOT/p for p in pins)
 save(DOC/'summary.json',result)
 module('sheung_candidate_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'sheung-shui-current-parent-terrain-candidate',list(dict.fromkeys(refs)),result)
 print(result,flush=True)
def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists()
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
