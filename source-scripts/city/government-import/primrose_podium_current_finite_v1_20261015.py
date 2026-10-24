"""Reconcile exact buried source indices and check every original podium face."""
from pathlib import Path
import uuid
import numpy as np
import shapely
from primrose_compound_foundation_v1_20261015 import module,BASE,CAPTURE,SOURCE,GROUND,PODIUM
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_paired_finite_clearance_v3_20261011 import verify
BATCH='government-xl-primrose-podium-current-finite-v1-20261015';DOC=BASE/BATCH

def main():
 assert not DOC.exists();refs={}
 for folder in [CAPTURE,GROUND,BASE/'government-xl-primrose-compound-foundation-v1-20261015',BASE/'government-xl-primrose-podium-source-role-review-v1-20261015']:
  receipt=read(folder/'result.json')
  with connect() as db:
   db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for q in receipt['evidenceRefs']:
   assert q['path'] not in refs or refs[q['path']]==q['sha256'];refs[q['path']]=q['sha256']
  refs[str((folder/'result.json').relative_to(ROOT))]=digest((folder/'result.json').read_bytes())
 for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h,p
 row=next(r for r in read(SOURCE/'selection.json.gz')['rows']if r['uid']==PODIUM)
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
 original=decode_original_world_triangles(asset.read_bytes())
 c=next(r for r in read(CAPTURE/'attributes.json.gz')['rows']if r['uid']==PODIUM)
 ix=np.asarray(c['completeOriginalIndex']).reshape(-1,3)
 worlds={'original':original}
 for mode,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(c[key],float).reshape(-1,3)[ix]
 context=read(BASE/'government-xl-primrose-podium-buried-face-context-v1-20261015/context.json')
 assert context['sourceSHA256']==row['sourceSHA256'];assert context['sourceFace']==999
 assert np.array_equal(original[999],np.asarray(context['vertices']))
 ground=np.asarray(read(GROUND/'after-ground.json.gz')['completeRelevantDrawnTriplets'],float).reshape(-1,3,3)
 f=module('existing_foundation',HERE/'xl-final-script-pass.py')
 polygons=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10
 native=ground[valid];tree=shapely.STRtree(polygons[valid])
 claim=reservations.claim('primrose-podium-finite-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 summaries=[];cache={}
 try:
  DOC.mkdir()
  for mode,tri in worlds.items():
   assert len(tri)==2508
   points=np.concatenate([tri,tri.mean(axis=1)[:,None,:]],axis=1)
   heights=f.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),native,tree).reshape(-1,4)
   gaps=points[:,:,1]-heights;buried=np.flatnonzero(np.isfinite(heights).all(axis=1)&(gaps<-.5).all(axis=1)).tolist()
   matched=buried==[999]
   save(DOC/(mode+'-source-role.json'),dict(mode=mode,buriedSourceFaces=buried,matchesReviewedOriginalUnderside=matched,sourceFace999=tri[999].tolist(),sourceSHA256=row['sourceSHA256'],sourceGeometryChanges=0,fullAcceptance=False))
   print(mode,'buried faces',buried,'matches prior underside',matched,flush=True)
   worldsha=digest(tri.tobytes())
   if worldsha in cache:
    source,faces=cache[worldsha];reused=source
   else:
    faces=[];reused=None
    for i,face in enumerate(tri):
     faces.append(dict(sourceFace=i,proof=verify(face,ground)))
     if i%50==0:
      assert reservations.heartbeat(lease)['ok'];print(mode,i,len(tri),flush=True)
    cache[worldsha]=(mode,faces)
   save(DOC/(mode+'.json.gz'),dict(worldSHA256=worldsha,groundSHA256=digest(ground.tobytes()),reusedByteIdenticalWorld=reused,faces=faces,fullAcceptance=False))
   summaries.append(dict(mode=mode,buriedSourceFaces=buried,matchesReviewedOriginalUnderside=matched,faces=len(faces),uncovered=[r['sourceFace']for r in faces if not r['proof']['groundProjectionCovered']],unproved=[r['sourceFace']for r in faces if not r['proof']['existingOrdinaryClearanceBoundProved']]))
  for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h,p
  save(DOC/'summary.json',dict(rows=summaries,fullAcceptance=False))
  paths=[ROOT/p for p in refs]+[Path(__file__),asset,SOURCE/'selection.json.gz']+[HERE/n for n in ['primrose_compound_foundation_v1_20261015.py','xl-final-script-pass.py','exact_original_paired_finite_clearance_v3_20261011.py','exact_original_paired_finite_clearance_v2_20261010.py','exact_original_triangle_pair_column_gap_20261010.py','exact_original_projection_coverage_v2_20261010.py']]
  module('freeze_podium',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-podium-finite-and-exact-underside-reconciliation-v1',paths,dict(uids=[PODIUM],rows=summaries,fullAcceptance=False))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
