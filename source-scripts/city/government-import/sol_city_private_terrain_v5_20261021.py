"""Construct and strictly validate a private regional terrain replacement."""
from pathlib import Path
import json,subprocess,sys,uuid,traceback
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from native_patch_resolution import grid_surface_faces,fill_parent_only_holes,fill_narrow_source_seam
from float32_coverage import approve_roundoff,geometry_sha
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-private-terrain-v5-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SOURCE=BASE/'government-xl-sol-city-shaped-ground-v2-20261021';SCOPE=BASE/'government-xl-sol-city-regional-scope-v1-20261021'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in [SOURCE,SCOPE]:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 scope=read(SCOPE/'scope.json');domain=scope['regionalParentExtent'];parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath)
 builder=module('yoho_private_metadata',HERE/'resolve-pass-indexed-parent-clipping.py');sampler=builder.terrain.fine.DemSampler(parent,rendered=True)
 baseline=np.asarray(grid_surface_faces(sampler,shapely.box(*domain)),dtype='float64')
 # Build valid standard metadata using unchanged parent planes first, then run
 # the same strict validator again on the exact proposed surface geometry.
 candidate=builder.make_patch(dict(uids=scope['uids'],cells=scope['regionalCoarseCells']),parent,baseline,[],allow_native_below_clamp=True)
 surfacespath=HERE/'local'/SOURCE.name/'diagnostic-height-surfaces.json.gz';faces=np.asarray(read(surfacespath)['triangles'],dtype='float64')
 candidate['nativeMesh']['position']=faces.reshape(-1).tolist();candidate['nativeMesh']['index']=list(range(len(faces)*3));candidate['nativeMesh']['source']={'policy':'Immutable original source core, eight metre transition to retained current terrain, unchanged current surfaces outside transition. Private proposal.','verticalDatum':'HKPD','verticalScale':1,'evidence':dict(path=str((SOURCE/'result.json').relative_to(ROOT)),sha256=digest((SOURCE/'result.json').read_bytes()))}
 candidate['meta']['source']['policy']=candidate['nativeMesh']['source']['policy'];candidate['meta']['source']['nativeSources']=[dict(sourceFiles=[dict(path=str(surfacespath.relative_to(ROOT)),sha256=digest(surfacespath.read_bytes()))])]
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 selectionPath=BASE/'government-xl-sol-city-assembly-capture-v2-20261021/selection.json.gz';assert digest(selectionPath.read_bytes())==pins[str(selectionPath.relative_to(ROOT))]
 row=next(r for r in read(selectionPath)['rows']if r['uid']=='landsd/273271:0');asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
 model=decode_original_world_triangles(asset.read_bytes());core=shapely.union_all(shapely.polygons(model[:,:,[0,2]])).buffer(.5,join_style='mitre')
 refs.extend([selectionPath,asset,HERE/'exact_packed_world_geometry_20261009.py'])
 # Existing 2cm nearest-source-edge policy bridges the authenticated 3.125cm sheet seam; every protected point is at most 1.5625cm from a source edge.
 fill=fill_narrow_source_seam(candidate,domain,core,sampler)
 save(DOC/'source-seam-fill.json',fill)
 before=geometry_sha(candidate);error=None
 try:
  save(DOC/'numerical-coverage.json',approve_roundoff(candidate,domain))
  overlap=module('yoho_private_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=DOC;overlap.overlap_proof(candidate,[surfacespath,Path(__file__)])
  builder.validate_patch(candidate,parent);assert len(faces)<=25000;assert geometry_sha(candidate)==before
 except Exception as exc:
  error=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc());save(DOC/'validation-failure.json',error)
 out=LOCAL/'candidate-terrain.json';save(out,candidate)
 descriptor=dict(path=str(out.relative_to(ROOT)),sha256=digest(out.read_bytes()),uids=scope['uids'],bounds=domain,triangles=len(candidate['nativeMesh']['index'])//3,replacesMany=[dict(url=r['url'],sha256=r['sha256'],retainedUids=scope['touchingNativeUids']) for r in scope['retainedPatches']])
 assert not scope['retainedPatches'],'This constructor is pinned to a new patch with no replaced native parents'
 descriptor.pop('replacesMany')
 save(DOC/'terrain-candidates.json',[descriptor]);summary=dict(uids=scope['uids'],terrainValidationPassed=error is None,error=error,triangles=len(candidate['nativeMesh']['index'])//3,geometryUnchanged=geometry_sha(candidate)==before,installationApproved=False,productionChanges=0)
 save(DOC/'summary.json',summary)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 assert reservations.owns(lease);refs.extend([out,HERE/'resolve-pass-indexed-parent-clipping.py',HERE/'float32_coverage.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py',HERE/'native_patch_resolution.py'])
 r=module('yoho_private_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-original-regional-terrain-validation',list(dict.fromkeys(refs)),summary);print(json.dumps(dict(jobId=r['jobId'],**summary)),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/273271:0'],batch=BATCH,ttl=3600);assert claim['ok'],claim
 lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
