"""Bounded complete-owned source-only paired refinement; full native negatives stay.

Every10679 owned original/literal facet is accounted; unrelated retained native
full63133 inventory remains explicitly referenced and unapproved. No acceptance.
"""
import importlib.util,json,time,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_paired_finite_clearance_20261010 import verify
from original_paired_finite_chunk_accounting_20261010 import verify_chunk
BASE=ROOT/'docs/astra-city/government-import'
PHYS=BASE/'government-xl-terrain-recovery-parkview-block11-complete-original-current-probe-v1-20261010'
OLD=BASE/'xl-terrain-recovery-20261010-parkview-block11-complete-original-and-literal-finite-v1'
BATCH='government-xl-terrain-recovery-parkview-block11-complete-owned-paired-finite-v1-20261010';DOC=BASE/BATCH
UID='landsd/255647:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipt=read(OLD/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for f in receipt['evidenceRefs']:assert ref(ROOT/f['path'])==f
 prior=read(OLD/'diagnostic.json.gz');cached=next(r for r in prior['rows']if r['uid']==UID);selection=read(PHYS/'selection.json.gz');row=next(r for r in selection['rows']if r['uid']==UID);asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==cached['sourceSHA256'];tri=decode_original_world_triangles(raw);rtpath=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';rt=next(r for r in read(rtpath)['rows']if r['uid']==UID);world=np.asarray(rt['position'],float).reshape(-1,3)[np.asarray(rt['index']).reshape(-1,3)];ground=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3)
 assert len(tri)==len(cached['allFaces'])==10679 and digest(tri.tobytes())==cached['completeOriginalWorldSHA256'] and digest(world.tobytes())==cached['completeActualRenderedWorldSHA256']and digest(ground.tobytes())==cached['completeGroundSHA256']
 refs=[ref(p)for p in [Path(__file__),OLD/'result.json',OLD/'diagnostic.json.gz',PHYS/'selection.json.gz',rtpath,asset,HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'original_paired_finite_chunk_accounting_20261010.py',HERE/'test_original_paired_finite_chunk_accounting_20261010.py']]
 claim=reservations.claim('parkview-bounded-owned-paired-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];clock=time.monotonic();faces=[]
 try:
  for i,c in enumerate(cached['allFaces']):
   assert c['sourceFace']==i;first=None if c['completeOriginal']['existingOrdinaryClearanceBoundProved']else verify(tri[i],ground)
   second=None if c['actualRendered']['existingOrdinaryClearanceBoundProved']else first if first is not None and np.array_equal(tri[i],world[i])else verify(world[i],ground)
   faces.append(dict(sourceFace=i,priorCoarseBoundProofVerbatim=c,pairedExactOriginalFiniteBound=first,pairedExactActualRenderedFiniteBound=second,completeOriginalBoundProved=c['completeOriginal']['existingOrdinaryClearanceBoundProved']or bool(first and first['existingOrdinaryClearanceBoundProved']),completeActualRenderedBoundProved=c['actualRendered']['existingOrdinaryClearanceBoundProved']or bool(second and second['existingOrdinaryClearanceBoundProved'])))
   if time.monotonic()-clock>=20:assert reservations.heartbeat(lease)['ok'];clock=time.monotonic();print(json.dumps(dict(uid=UID,completeOwnedFaces=i,total=10679)),flush=True)
  binding=dict(source=ref(asset),coarseReceipt=ref(OLD/'result.json'),sourceWorldSHA256=digest(tri.tobytes()),actualWorldSHA256=digest(world.tobytes()),completeGroundSHA256=digest(ground.tobytes()),baselineManifestSHA256=selection['manifestSHA256']);chunk=dict(binding=binding,first=0,endExclusive=10679,faces=faces,fullAcceptance=False,installationApproved=False);verify_chunk(chunk,binding,tri,world,ground,cached['allFaces'],0,10679)
  for r in refs:assert ref(ROOT/r['path'])==r
  owned=dict(uid=UID,sourceSHA256=row['sourceSHA256'],completeOriginalFaces=10679,completeOriginalWorldSHA256=digest(tri.tobytes()),completeActualRenderedWorldSHA256=digest(world.tobytes()),completeGroundSHA256=digest(ground.tobytes()),allFaces=faces,unprovedOriginalFaces=[r['sourceFace']for r in faces if not r['completeOriginalBoundProved']],unprovedActualRenderedFaces=[r['sourceFace']for r in faces if not r['completeActualRenderedBoundProved']])
  result=dict(rows=[owned],wholeRetainedNativeInventoryNotOmitted=ref(OLD/'diagnostic.json.gz'),wholeNativeLegacyNegativesPreservedCount=len(next(r['unprovedOriginalFaceBounds']for r in prior['rows']if r['uid']=='landsd/254491:0')),frozenCapturedBaselineManifestSHA256=selection['manifestSHA256'],freshCurrentAcceptance=False,nativeReacceptance=False,allWholeOriginalAndRenderedBoundsProved=not owned['unprovedOriginalFaces']and not owned['unprovedActualRenderedFaces'],sourceGeometryChanges=0,fullAcceptance=False,installationApproved=False,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',result);s=importlib.util.spec_from_file_location('parkview_owned_finite_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'bounded-complete-owned-original-literal-finite-refinement-v1',[ROOT/f['path']for f in refs],dict(uids=[UID],completeOwnedFaces=10679,unprovedOriginalCount=len(owned['unprovedOriginalFaces']),unprovedLiteralCount=len(owned['unprovedActualRenderedFaces']),nativeReacceptance=False,freshCurrentAcceptance=False,fullAcceptance=False));print(json.dumps(dict(ownedOriginalUnproved=len(owned['unprovedOriginalFaces']),ownedLiteralUnproved=len(owned['unprovedActualRenderedFaces']),nativeReacceptance=False)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
