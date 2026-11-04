"""Source-only complete finite-edge convex facet associations for two podium details.

All original22 facets and two whole lower loops tested against all576 main-body
facets. Failed upward-roof loop findings remain verbatim. The main body has
source-only grade/cap evidence, never current acceptance; no role/root credit.
"""
from pathlib import Path
import importlib.util,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_facet_piecewise_finite_host_edge_band_diagnostic_v1_20261011 import verify as facet_verify
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as edge_verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-mount-verdant-two-details-piecewise-finite-host-edge-facets-v1';DOC=BASE/BATCH
PRIOR=BASE/'xl-terrain-recovery-20261011-mount-verdant-podium-grade-cap-lower-loops-v2'
OLDNEG=BASE/'xl-terrain-recovery-20261011-mount-verdant-two-details-finite-host-edge-facets-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 assert ref(PRIOR/'diagnostic.json.gz')in receipt['evidenceRefs'];d=read(PRIOR/'diagnostic.json.gz')
 old=read(OLDNEG/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(old['jobId'],)).fetchone()==('complete',old)
 assert ref(OLDNEG/'diagnostic.json.gz')in old['evidenceRefs']
 source=next(ROOT/r['path']for r in d['evidenceRefs']if r['path'].endswith('4d3d6e5e5b08c6f33b1ce710161edc3554998f7afc7ee15ce29577f9e4c2f781.glb.gz'));assert digest(source.read_bytes())==d['sourceSHA256'];tri=decode_original_world_triangles(source.read_bytes());assert tri.shape==(641,3,3) and digest(tri.tobytes())==d['completeOriginalWorldSHA256']
 hosts=d['completeMainBody576OriginalFaces'];assert len(hosts)==576
 names=['exact_packed_world_geometry_20261009.py','exact_original_facet_piecewise_finite_host_edge_band_diagnostic_v1_20261011.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_surface_coordinate_band_20261010.py','exact_original_projection_coverage_20261009.py','test_exact_original_facet_piecewise_finite_host_edge_band_diagnostic_v1_20261011.py','exact_original_edge_finite_facade_distance_band_v2_20261010.py','exact_original_edge_finite_facade_distance_band_20261010.py','xl-popcorn-source-investigations-checkpoints-20261009.py']
 refs=[ref(p)for p in [Path(__file__),source,PRIOR/'diagnostic.json.gz',PRIOR/'result.json',OLDNEG/'diagnostic.json.gz',OLDNEG/'result.json',*[HERE/n for n in names]]]
 claim=reservations.claim('mount-complete-detail-hosts-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];rows=[]
 try:
  for detail in d['completeTwoDetachedDetailLowerLoopDiagnoses']:
   ids=detail['completeOriginalSourceFaces'];facets=[];edges=[]
   for i in ids:
    p=facet_verify(tri[i],tri[hosts]);facets.append(dict(sourceFace=i,wholeFiniteHostProof=p));assert reservations.heartbeat(lease)['ok']
   for e in detail['completeOriginalLowerEdges']:
    p=edge_verify(e,tri[hosts]);edges.append(dict(wholeOriginalLowerEdge=e,completeFiniteHostProof=p));assert reservations.heartbeat(lease)['ok']
   r=dict(originalPodiumComponent=detail['originalPodiumComponent'],completeOriginalSourceFaces=ids,completeWholeFacetProofs=facets,completeLowerLoopFiniteHostProofs=edges,priorUpwardRoofLoopFailureVerbatim=detail,completeHostOriginalFaceIds=hosts,wholeComponentAssociated=all(p['wholeFiniteHostProof']['wholeFacetFiniteEdgeUnionAssociated']for p in facets),wholeLowerLoopAssociated=detail['wholeLowerPerimeterDegreeTwo']and all(p['completeFiniteHostProof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for p in edges),strictBandM=.1,conditionalHostCurrentGroundingNotAccepted=True,sourceOnly=True,authoredRoleAccepted=False,structuralRootOrBridgeCredit=False);rows.append(r)
   print(dict(component=r['originalPodiumComponent'],wholeFacets=sum(p['wholeFiniteHostProof']['wholeFacetFiniteEdgeUnionAssociated']for p in facets),total=len(ids),wholeLowerLoop=r['wholeLowerLoopAssociated']),flush=True)
  assert all(ref(ROOT/r['path'])==r for r in refs);out=dict(uids=['landsd/75782:0'],sourceSHA256=d['sourceSHA256'],completeOriginalWorldSHA256=d['completeOriginalWorldSHA256'],completeOriginalGroundSHA256=d['completeOriginalGroundSHA256'],completeMainBodyHostFaces=hosts,all22OriginalDetailFacesRetained=True,rows=rows,uninstalledTowerNeverUsed=True,currentAcceptance=False,sourceOnly=True,authoredRoleAccepted=False,structuralRootCredit=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze',HERE/names[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'mount-complete22-original-detail-piecewise-convex-finite-host-edge-facet-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=out['uids'],sourceOnly=True,currentAcceptance=False,all22OriginalDetailFacesRetained=True,detailResults=[dict(component=r['originalPodiumComponent'],wholeComponentAssociated=r['wholeComponentAssociated'],wholeLowerLoopAssociated=r['wholeLowerLoopAssociated'])for r in rows],newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
