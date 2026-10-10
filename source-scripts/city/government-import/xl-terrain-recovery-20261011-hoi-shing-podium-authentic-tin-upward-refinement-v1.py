"""Exact paired finite refinement of twenty upward Hoi Shing podium warnings.

Priority causal check only. Complete5533-face coarse receipt stays mandatory,
all660 other conservative negatives retained; no ground/source/root acceptance.
"""
from pathlib import Path
import importlib.util,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_paired_finite_clearance_v2_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-hoi-shing-podium-authentic-tin-upward-refinement-v1';DOC=BASE/BATCH
TIN=BASE/'xl-terrain-recovery-20261011-hoi-shing-two-original-authentic-tin-finite-v1'
PROBE=BASE/'government-xl-terrain-recovery-hoi-shing-two-original-current-probe-v1-20261011'
UID='landsd/318830:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipt=read(TIN/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 row=next(r for r in read(PROBE/'selection.json.gz')['rows']if r['uid']==UID)
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']=='cb52942f086f38d8d95a346e83538003c90f9aaa772811ac13d3485e1ae27b7f'
 world=decode_original_world_triangles(asset.read_bytes());assert world.shape==(5533,3,3)
 groundfile=HERE/'local'/TIN.name/'complete-authentic-source-tin-ground.json.gz';g=read(groundfile);ground=np.asarray(g['completeSelectedFacets']);assert digest(ground.tobytes())==g['completeSelectedFacetSHA256']
 coarse=next(r for r in read(TIN/'diagnostic.json.gz')['rows']if r['uid']==UID)
 assert coarse['completeOriginalWorldSHA256']==digest(world.tobytes())and len(coarse['allFaces'])==5533
 normals=np.cross(world[:,1]-world[:,0],world[:,2]-world[:,0]);length=np.linalg.norm(normals,axis=1)
 ny=np.divide(normals[:,1],length,out=np.zeros(len(world)),where=length!=0)
 faces=[i for i in coarse['unprovedOriginalFaces']if ny[i]>.5];assert faces==[1446,2361,2365,3257,3259,3260,3261,3262,3263,3264,3265,3266,3267,3272,3273,3274,3275,3288,3289,3290]
 refs=[ref(p)for p in [Path(__file__),TIN/'result.json',TIN/'diagnostic.json.gz',groundfile,PROBE/'selection.json.gz',asset,
  HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_paired_finite_clearance_v2_20261010.py',
  HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py',
  HERE/'exact_original_projection_coverage_v2_20261010.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py']]
 claim=reservations.claim('hoi-shing-authentic-tin-upward-refinement-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];records=[]
 try:
  for i in faces:
   prior=coarse['allFaces'][i]['proof'];assert prior['sourceFaceSHA256']==digest(world[i].tobytes())and prior['completeCurrentGroundSHA256']==digest(ground.tobytes())
   proof=verify(world[i],ground);records.append(dict(sourceFace=i,completeOriginalVertices=world[i].tolist(),rawCoarseProofVerbatim=prior,independentExactPairedFiniteProof=proof))
   assert reservations.heartbeat(lease)['ok'];print(dict(sourceFace=i,exactBound=proof['exactCertifiedLowerClearanceM'],strictOrdinaryProved=proof['existingOrdinaryClearanceBoundProved']),flush=True)
  assert all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uids=[UID],sourceSHA256=row['sourceSHA256'],completeOriginalWorldSHA256=digest(world.tobytes()),completeOriginalTINSelectedGroundSHA256=digest(ground.tobytes()),
   allTwentyUpwardRefinements=records,complete5533FacetCoarseInventoryPreserved=ref(TIN/'diagnostic.json.gz'),
   allOther660RawConservativeWarningsRetained=[i for i in coarse['unprovedOriginalFaces']if i not in faces],
   remainingTrueUpwardClearanceFailures=[r['sourceFace']for r in records if not r['independentExactPairedFiniteProof']['existingOrdinaryClearanceBoundProved']],
   currentRendererGround=False,sourceOnly=True,currentAcceptance=False,terrainProposalCreated=False,structuralRootCredit=False,newlyInstalled=0,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',out);spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.freeze(BATCH,'complete-twenty-hoi-shing-original-podium-upward-authentic-tin-exact-paired-refinement-v1',
   [ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],upwardFaces=20,
    remainingTrueUpwardFaces=out['remainingTrueUpwardClearanceFailures'],sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
