"""Exact bounded source-only strongest backing interfaces; no visual role credit.

Part1 one entire original long lower backing edge; part6 complete original
2facet backing side and its4edge perimeter. Every other face/free/open boundary
and failed whole-lower-loop/whole-facet test remains preserved. No root/bridge.
"""
from pathlib import Path
from collections import Counter
import importlib.util,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify as facet_verify
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as edge_verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-mount-verdant-specific-back-attachments-v1';DOC=BASE/BATCH
PRIOR=BASE/'xl-terrain-recovery-20261011-mount-verdant-two-details-complete-finite-hosts-v1'
GRADE=BASE/'xl-terrain-recovery-20261011-mount-verdant-podium-grade-cap-lower-loops-v2'
UNION=BASE/'xl-terrain-recovery-20261011-mount-verdant-two-details-piecewise-finite-host-edge-facets-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in (PRIOR,GRADE,UNION):
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  assert ref(folder/'diagnostic.json.gz')in r['evidenceRefs'];refs.extend([ref(folder/'diagnostic.json.gz'),ref(folder/'result.json')])
 d=read(PRIOR/'diagnostic.json.gz');grade=read(GRADE/'diagnostic.json.gz');source=next(ROOT/r['path']for r in grade['evidenceRefs']if r['path'].endswith('4d3d6e5e5b08c6f33b1ce710161edc3554998f7afc7ee15ce29577f9e4c2f781.glb.gz'));assert digest(source.read_bytes())==d['sourceSHA256'];tri=decode_original_world_triangles(source.read_bytes());assert tri.shape==(641,3,3)and digest(tri.tobytes())==d['completeOriginalWorldSHA256'];hostids=d['completeMainBodyHostFaces'];assert len(hostids)==576;hosts=tri[hostids]
 names=['exact_packed_world_geometry_20261009.py','exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py','exact_original_surface_coordinate_band_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_edge_finite_facade_distance_band_v2_20261010.py','exact_original_edge_finite_facade_distance_band_20261010.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs.extend(ref(p)for p in [source,*[HERE/n for n in names]])
 claim=reservations.claim('mount-specific-back-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  part1=next(r for r in d['rows']if r['originalPodiumComponent']==1);passed=[e for e in part1['completeLowerLoopFiniteHostProofs']if e['completeFiniteHostProof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']];assert len(passed)==1;edge=passed[0]['wholeOriginalLowerEdge'];p=edge_verify(edge,hosts);assert p==passed[0]['completeFiniteHostProof']and p['verifiedCompleteOriginalEdgeFiniteFacadeBand'];length=float(np.linalg.norm(np.asarray(edge)[1]-np.asarray(edge)[0]));assert length>9;assert reservations.heartbeat(lease)['ok']
  part6=next(r for r in d['rows']if r['originalPodiumComponent']==6);back=[r['sourceFace']for r in part6['completeWholeFacetProofs']if r['wholeFiniteHostProof']['wholeFacetAssociated']];assert back==[456,457];facets=[]
  for i in back:
   p=facet_verify(tri[i],hosts);assert p==next(r['wholeFiniteHostProof']for r in part6['completeWholeFacetProofs']if r['sourceFace']==i)and p['wholeFacetAssociated'];facets.append(dict(sourceFace=i,wholeOriginalBackFacet=tri[i].tolist(),proof=p));assert reservations.heartbeat(lease)['ok']
  inventory=Counter(tuple(sorted((tuple(a),tuple(b))))for i in back for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)));loop=sorted(e for e,n in inventory.items()if n==1);assert len(loop)==4 and sorted(inventory.values())==[1,1,1,1,2];assert all(n==2 for n in Counter(v for e in loop for v in e).values());bands=[]
  for e in loop:
   p=edge_verify(e,hosts);bands.append(dict(wholeOriginalBackingPerimeterEdge=[list(v)for v in e],proof=p));assert reservations.heartbeat(lease)['ok']
  assert all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uids=['landsd/75782:0'],sourceSHA256=d['sourceSHA256'],completeOriginalWorldSHA256=d['completeOriginalWorldSHA256'],completeOriginalConditionalHostFaces=hostids,part1=dict(completeOriginalSourceFaces=part1['completeOriginalSourceFaces'],wholeOriginalLongLowerBackingEdge=edge,wholeExactFiniteEdgeBand=p if False else passed[0]['completeFiniteHostProof'],edgeLengthM=length,twoDistinctOriginalEndpoints=True,priorWholeFacetAndLowerLoopFailuresVerbatim=part1,proposedVisualOnlyRoleNotAccepted=True),part6=dict(completeOriginalSourceFaces=part6['completeOriginalSourceFaces'],completeOriginalBackingSideFaces=back,wholeOriginalBackFacetProofs=facets,completeOriginalBackingSidePerimeter=bands,allFourOriginalBackingEdgesWithinFixedBand=all(r['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for r in bands),priorWholeLowerLoopFailureVerbatim=part6,proposedVisualOnlyRoleNotAccepted=True),sourceOnly=True,all22SourceFacesPreserved=True,conditionalHostCurrentRootNotAccepted=True,uninstalledTowerNeverUsed=True,authoredRoleAccepted=False,structuralRootOrBridgeCredit=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze',HERE/names[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'two-complete-original-mount-podium-specific-back-mount-associations-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=out['uids'],part1CompleteBackingEdgeWithinFixedBand=True,part6CompleteBackingSideWithinFixedBand=True,part6AllFourBackingEdgesWithinFixedBand=out['part6']['allFourOriginalBackingEdgesWithinFixedBand'],sourceOnly=True,currentAcceptance=False,authoredRoleAccepted=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
