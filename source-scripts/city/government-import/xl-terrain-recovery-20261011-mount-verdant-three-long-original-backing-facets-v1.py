"""Complete original30-facet diagnosis of three long source strips.

Failed open-loop associations retained; every authored face is tested against
the same complete source-only host. Positive complete backing patches get
independent whole-boundary tests. No association/role/root waiver or function.
"""
from pathlib import Path
import importlib.util,json,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify as facet_band
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as edge_band
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-mount-verdant-three-long-original-backing-facets-v1';DOC=BASE/BATCH
PRIOR=BASE/'xl-terrain-recovery-20261011-mount-verdant-207-original-complete-back-associations-v1';SOURCE=BASE/'government-xl-full-cell-aqua-mount-support-recovered-20261006'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 assert ref(PRIOR/'diagnostic.json.gz')in receipt['evidenceRefs'];d=read(PRIOR/'diagnostic.json.gz');selected=read(SOURCE/'selection.json.gz');parts=[];assets=[]
 for uid,count in [('landsd/261717:0',14938),('landsd/75782:0',641)]:
  row=next(r for r in selected['rows']if r['uid']==uid);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];world=decode_original_world_triangles(asset.read_bytes());assert world.shape==(count,3,3);parts.append(world);assets.append(asset)
 tri=np.concatenate(parts);assert digest(tri.tobytes())==d['complete15579PairWorldSHA256'];hosts=d['completeHostGlobalFaceIDs'];host=tri[hosts];bodies=[r for r in d['all207Bodies2682Faces']if r['originalBody']in[311,312,313]];assert len(bodies)==3 and all(len(r['completeOriginalGlobalFaceIDs'])==10 and not r['completeBoundaryWithinFixedBand']for r in bodies)
 context=HERE/'xl-terrain-recovery-20261011-mount-verdant-34-complete-backing-patches-context-v1.py';spec=importlib.util.spec_from_file_location('patch',context);patch=importlib.util.module_from_spec(spec);spec.loader.exec_module(patch)
 names=['exact_packed_world_geometry_20261009.py','exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py','exact_original_surface_coordinate_band_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_edge_finite_facade_distance_band_v2_20261010.py','exact_original_edge_finite_facade_distance_band_20261010.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs=[ref(p)for p in [Path(__file__),context,PRIOR/'result.json',PRIOR/'diagnostic.json.gz',SOURCE/'selection.json.gz',*assets,*[HERE/n for n in names]]];claim=reservations.claim('mount-three-long-facets-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();rows=[]
 try:
  for body in bodies:
   proofs=[]
   for fi in body['completeOriginalGlobalFaceIDs']:
    proof=facet_band(tri[fi],host);proofs.append(dict(originalGlobalFace=fi,wholeFacetFiniteHostProof=proof))
    if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic()
   positive=[r['originalGlobalFace']for r in proofs if r['wholeFacetFiniteHostProof']['wholeFacetAssociated']];inventory=patch.patch_inventory(tri,positive)if positive else None;edges=[]if inventory is None else[dict(completeOriginalBackingBoundaryEdge=e,proof=edge_band(np.asarray(e),host))for e in inventory['completeBackingBoundaryEdges']]
   rows.append(dict(originalBody=body['originalBody'],all10CompleteOriginalFaces=body['completeOriginalGlobalFaceIDs'],completeAll10FacetProofs=proofs,completePositiveFacetPatch=inventory,completePatchBoundaryProofs=edges,conditionalCompleteBackingPatchPositive=bool(inventory)and inventory['everyBackingFaceSharedEdgeConnected']and inventory['completeBoundaryDegreeTwo']and not inventory['backingWindingConflicts']and not inventory['backingNonmanifoldEdges']and all(r['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for r in edges),oldOpenBoundaryLoopFailureVerbatim=body,allUnassociatedOriginalFacesRemain=True));print(json.dumps(dict(body=body['originalBody'],positiveFaces=positive)),flush=True)
  assert reservations.heartbeat(lease)['ok']and all(ref(ROOT/r['path'])==r for r in refs);out=dict(uid='landsd/261717:0',complete15579WorldSHA256=digest(tri.tobytes()),all30OriginalLongStripFaces=rows,completeSourceOnlyHostGlobalFaces=hosts,unqualifiedHostGroundingStillRequired=True,sourceOnly=True,functionInferred=False,visualRoleAccepted=False,rootOrBridgeCredit=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze',HERE/names[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'mount-three-long-source-strips-all30-facets-backing-patch-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[out['uid']],sourceOnly=True,currentAcceptance=False,completeBackingPatchPositiveBodies=[r['originalBody']for r in rows if r['conditionalCompleteBackingPatchPositive']],newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
