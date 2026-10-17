"""Exact paired refinement of all75 Mount Verdant podium TIN warnings.

Full641-face coarse inventory remains pinned. Original terrain/source geometry
and all failures preserved; no current/source/root/terrain acceptance.
"""
from pathlib import Path
import importlib.util,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_paired_finite_clearance_v2_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-mount-verdant-podium-authentic-tin-paired-refinement-v1';DOC=BASE/BATCH
TIN=BASE/'xl-terrain-recovery-20261011-mount-verdant-podium-authentic-tin-finite-v1'
PROBE=BASE/'government-xl-full-cell-aqua-mount-support-recovered-20261006'
UID='landsd/75782:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipt=read(TIN/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 bound={r['path']:r for r in receipt['evidenceRefs']}
 assert bound[str((TIN/'diagnostic.json.gz').relative_to(ROOT))]==ref(TIN/'diagnostic.json.gz')
 row=next(r for r in read(PROBE/'selection.json.gz')['rows']if r['uid']==UID)
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']=='4d3d6e5e5b08c6f33b1ce710161edc3554998f7afc7ee15ce29577f9e4c2f781'
 world=decode_original_world_triangles(asset.read_bytes());assert world.shape==(641,3,3)
 groundfile=HERE/'local'/TIN.name/'complete-authentic-source-tin-ground.json.gz';g=read(groundfile);ground=np.asarray(g['completeSelectedFacets']);assert digest(ground.tobytes())==g['completeSelectedFacetSHA256']
 coarse=next(r for r in read(TIN/'diagnostic.json.gz')['rows']if r['uid']==UID)
 assert coarse['completeOriginalWorldSHA256']==digest(world.tobytes())and len(coarse['allFaces'])==641
 normals=np.cross(world[:,1]-world[:,0],world[:,2]-world[:,0]);length=np.linalg.norm(normals,axis=1)
 ny=np.divide(normals[:,1],length,out=np.zeros(len(world)),where=length!=0)
 faces=list(coarse['unprovedOriginalFaces']);assert len(faces)==75 and faces==sorted(set(faces))
 assert bound[str(groundfile.relative_to(ROOT))]==ref(groundfile)
 refs=[ref(p)for p in [Path(__file__),TIN/'result.json',TIN/'diagnostic.json.gz',groundfile,PROBE/'selection.json.gz',asset,
  HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_paired_finite_clearance_v2_20261010.py',
  HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py',
  HERE/'exact_original_projection_coverage_v2_20261010.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py']]
 claim=reservations.claim('mount-verdant-authentic-tin-paired-refinement-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];records=[]
 try:
  for i in faces:
   prior=coarse['allFaces'][i]['proof'];assert prior['sourceFaceSHA256']==digest(world[i].tobytes())and prior['completeCurrentGroundSHA256']==digest(ground.tobytes())
   proof=verify(world[i],ground);records.append(dict(sourceFace=i,completeOriginalVertices=world[i].tolist(),originalNormalY=float(ny[i]),rawCoarseProofVerbatim=prior,independentExactPairedFiniteProof=proof))
   assert reservations.heartbeat(lease)['ok'];print(dict(sourceFace=i,exactBound=proof['exactCertifiedLowerClearanceM'],strictOrdinaryProved=proof['existingOrdinaryClearanceBoundProved']),flush=True)
  assert all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uids=[UID],sourceSHA256=row['sourceSHA256'],completeOriginalWorldSHA256=digest(world.tobytes()),completeOriginalTINSelectedGroundSHA256=digest(ground.tobytes()),
   allSeventyFiveCompletePairedRefinements=records,complete641FacetCoarseInventoryPreserved=ref(TIN/'diagnostic.json.gz'),
   allOtherRawConservativeWarningsRetained=[i for i in coarse['unprovedOriginalFaces']if i not in faces],
   remainingExactPairedClearanceFailures=[r['sourceFace']for r in records if not r['independentExactPairedFiniteProof']['existingOrdinaryClearanceBoundProved']],
   allOriginalFacetProofsAccounted=len(coarse['allFaces'])==641,upwardFailures=[r['sourceFace']for r in records if r['originalNormalY']>.5 and not r['independentExactPairedFiniteProof']['existingOrdinaryClearanceBoundProved']],currentRendererGround=False,sourceOnly=True,currentAcceptance=False,terrainProposalCreated=False,structuralRootCredit=False,newlyInstalled=0,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',out);spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.freeze(BATCH,'complete-mount-verdant-original-podium-all75-authentic-tin-exact-paired-refinement-v1',
   [ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],refinedFaces=75,
    remainingExactPairedFaces=out['remainingExactPairedClearanceFailures'],sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
