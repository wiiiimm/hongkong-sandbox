"""Complete original Hoi Shing pair versus authenticated original source TIN.

Different ground from the frozen current renderer; no proposal/installation,
source geometry edits, current clearance, group ownership or root credit.
Every source triangle and covering original finite TIN facet remains bound.
"""
from pathlib import Path
import importlib.util,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_face_conservative_clearance_v5_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-hoi-shing-two-original-authentic-tin-finite-v1';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PROBE=BASE/'government-xl-terrain-recovery-hoi-shing-two-original-current-probe-v1-20261011'
PRIOR=BASE/'xl-terrain-recovery-20261011-hoi-shing-two-original-current-finite-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [PROBE,PRIOR]:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.extend(ref(folder/p)for p in ['result.json','diagnostic.json.gz']if(folder/p).exists())
 selection=read(PROBE/'selection.json.gz');assert {r['uid']for r in selection['rows']}=={'landsd/318801:0','landsd/318830:0'}
 sources=[]
 for row in selection['rows']:
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
  world=decode_original_world_triangles(asset.read_bytes());assert len(world)=={'landsd/318801:0':13841,'landsd/318830:0':5533}[row['uid']]
  sources.append((row,world));refs.append(ref(asset))
 terrain=module('hoi_shing_authentic_terrain','xl-owned-indexed-terrain-continuation.py')
 folder,terrain_receipt=terrain.terrain_sheet('11-NW-13A',LOCAL)
 decoder=module('hoi_shing_tin_decoder','xl-second-pass.py')
 whole=np.concatenate([decoder.terrain_triangles(folder/'terrain'/r['name'])for r in terrain_receipt['terrainFiles']if r['name'].endswith('.gltf')])
 allworld=np.concatenate([w for _,w in sources]);lo=allworld.min((0,1));hi=allworld.max((0,1))
 keep=(whole[:,:,0].max(1)>=lo[0])&(whole[:,:,0].min(1)<=hi[0])&(whole[:,:,2].max(1)>=lo[2])&(whole[:,:,2].min(1)<=hi[2]);ground=whole[keep]
 assert len(ground)>0 and np.isfinite(ground).all()
 groundfile=LOCAL/'complete-authentic-source-tin-ground.json.gz'
 save(groundfile,dict(sourceTerrainReceipt=terrain_receipt,completeOriginalSheetFacets=len(whole),
  completeOriginalSheetFacetSHA256=digest(whole.tobytes()),sourceCoveringWholeFacetIds=np.flatnonzero(keep).tolist(),
  completeSelectedFacets=ground.tolist(),completeSelectedFacetSHA256=digest(ground.tobytes()),
  wholeOriginalSourceBounds=[lo.tolist(),hi.tolist()],currentRendererGround=False,
  finiteSelection='Every whole original terrain facet whose closed AABB intersects whole source projection bounds; no clipping, filtering by slope, resampling or height edit.'))
 refs.extend(ref(p)for p in [groundfile,folder/'original/download.json',folder/'directory/result.json',
  *[folder/'terrain'/r['name']for r in terrain_receipt['terrainFiles']],
  PROBE/'selection.json.gz',PROBE/'historical-current-manifest.json',
  HERE/'xl-owned-indexed-terrain-continuation.py',HERE/'xl-second-pass.py',HERE/'exact_packed_world_geometry_20261009.py',
  HERE/'exact_original_face_conservative_clearance_v5_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py',
  HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'])
 claim=reservations.claim('hoi-shing-original-tin-finite-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600)
 assert claim['ok'];lease=claim['reservation'];rows=[];last=time.monotonic()
 try:
  for row,world in sources:
   binding=dict(producer=ref(Path(__file__)),sourceSHA256=row['sourceSHA256'],completeWorldSHA256=digest(world.tobytes()),completeGroundSHA256=digest(ground.tobytes()),ground=ref(groundfile))
   checkpoint=LOCAL/(row['uid'].replace('/','-').replace(':','-')+'-partial.json.gz')
   partial=read(checkpoint)if checkpoint.exists()else None;assert partial is None or partial['binding']==binding
   faces=[]if partial is None else partial['allFaces'];assert [r['sourceFace']for r in faces]==list(range(len(faces)))
   assert reservations.heartbeat(lease)['ok']
   for i in range(len(faces),len(world)):
    faces.append(dict(sourceFace=i,proof=verify(world[i],ground)))
    if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];save(checkpoint,dict(binding=binding,allFaces=faces));print(dict(uid=row['uid'],faces=len(faces),total=len(world)),flush=True);last=time.monotonic()
   save(checkpoint,dict(binding=binding,allFaces=faces,complete=True));rows.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],completeOriginalWorldSHA256=digest(world.tobytes()),completeOriginalFaces=len(world),allFaces=faces,
    unprovedOriginalFaces=[r['sourceFace']for r in faces if not r['proof']['existingOrdinaryClearanceBoundProved']]))
  assert reservations.heartbeat(lease)['ok'];assert all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uids=[r['uid']for r in rows],rows=rows,sourceTerrainReceipt=terrain_receipt,
   wholeOriginalTerrainSheetFacets=len(whole),completeRelevantOriginalTerrainFacets=len(ground),
   allOriginalSourceFacesAccounted=True,currentRendererGround=False,sourceOnly=True,
   rawCurrentTerrainFailuresPreserved=True,terrainProposalCreated=False,currentAcceptance=False,
   structuralRootCredit=False,identityGroupingProved=False,newlyInstalled=0,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',out);m=module('freeze_hoi_shing_tin','xl-popcorn-source-investigations-checkpoints-20261009.py')
  m.freeze(BATCH,'complete-hoi-shing-two-original-source-finite-authentic-tin-diagnostic-v1',
   [ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=out['uids'],
    completeOriginalFaces=19374,sourceOnly=True,originalTINFacets=len(ground),
    unprovedFacesByUID={r['uid']:len(r['unprovedOriginalFaces'])for r in rows},currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
