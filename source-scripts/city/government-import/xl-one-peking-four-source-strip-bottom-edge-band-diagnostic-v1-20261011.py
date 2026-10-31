"""Complete exact nonzero bottom-edge association, no structural/mount credit.

The failed whole-facet band is preserved. This different source-only query asks
whether the full finite lower edges of four original thin strips are near the
original podium. All original faces, zero-area records and open edges remain.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,json,collections
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify
BATCH='government-xl-one-peking-four-source-strip-bottom-edge-band-diagnostic-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
PHYS=DOC.parent/'government-xl-one-peking-two-original-retained-hullett-child-current-physical-v5-20261010'
GRAPH=DOC.parent/'government-xl-one-peking-original-ordinary-ground-graph-diagnostic-v2-20261010'
CENSUS=DOC.parent/'government-xl-one-peking-complete-original-and-literal-nonzero-edge-census-v2-20261011'
FAILED=DOC.parent/'government-xl-one-peking-four-facade-band-negative-preservation-v1-20261011'
COMPONENTS=(27,34,46,49)
def main():
 assert not DOC.exists()
 rows=sorted(read(PHYS/'selection.json.gz')['rows'],key=lambda r:r['uid']);assert [r['uid'] for r in rows]==['landsd/233985:0','landsd/240487:0']
 parts=[];assets=[]
 for r in rows:
  p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];assets.append(p);parts.append(decode_original_world_triangles(raw))
 whole=np.concatenate(parts);assert len(parts[0])==4114 and len(whole)==15784
 graph=read(GRAPH/'diagnostic.json.gz');assert digest(whole.tobytes())==graph['binding']['completeOriginalWorldTrianglesSHA256']
 hosts=parts[0];results=[]
 for k in COMPONENTS:
  c=graph['components'][k];ids=c['globalOriginalFaces'];proof=census(whole,ids);assert len(proof['sharedEdgeConnectedComponents'])==1
  positive=proof['completeRenderableFaceIds'];low=float(whole[positive,:,1].min());edges=collections.defaultdict(list)
  for face in positive:
   verts=[tuple(p) for p in whole[face]]
   for a,b in zip(verts,verts[1:]+verts[:1]):
    if a!=b and a[1]==b[1]==low:edges[tuple(sorted([a,b]))].append(face)
  records=[]
  for edge,faces in sorted(edges.items()):
   segment=np.asarray(edge);lo=np.nextafter(segment.min(0)-.1,-np.inf);hi=np.nextafter(segment.max(0)+.1,np.inf)
   # Conservative outward broad phase only; final interval arithmetic exact.
   selected=np.flatnonzero(((hosts.max(1)>=lo)&(hosts.min(1)<=hi)).all(1))
   finite=[int(i) for i in selected if not census(hosts,[int(i)])['exactNonrenderingOriginalFaces']]
   assert finite,'No finite original podium host near complete lower edge'
   band=verify(segment,hosts[finite]);band['completeSourceHostFaceIDs']=finite
   records.append(dict(edgeVertices=segment.tolist(),completeLowerEdgeOwnerFaceIDs=faces,completeFiniteHostBand=band))
  result=dict(component=k,actorUID=c['actorUID'],completeOriginalFaceIDs=ids,completeNonzeroAreaEdgeCensus=proof,originalComponentBottomHKPD=low,completeBottomNonzeroEdgeCount=len(records),completeBottomEdgeRecords=records,allCompleteBottomEdgesWithinFixedBand=bool(records) and all(r['completeFiniteHostBand']['verifiedCompleteOriginalEdgeFiniteFacadeBand'] for r in records),visualRoleAccepted=False,structuralRootCredit=False,installationApproved=False)
  results.append(result);save(DOC/'diagnostic-progress.json.gz',dict(rows=results));print(json.dumps(dict(component=k,bottomEdges=len(records),finiteBottomBandPassed=result['allCompleteBottomEdgesWithinFixedBand'])),flush=True)
 result=dict(rows=results,completeOriginalPairFaces=len(whole),sourceGeometryChanges=0,unchangedFiniteBandM=.1,priorWholeFacetBandRemainsFailed=True,identityAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Complete finite original lower-edge proximity only. No point-only root, load-bearing/function interpretation, authored mounting role, grounded-host acceptance or current terrain/foreign/runtime credit. All complete original and nonrendering source records retained. Different query from the preserved failed whole-facet band.')
 save(DOC/'diagnostic.json.gz',result)
 refs=[Path(__file__),PHYS/'selection.json.gz',PHYS/'result.json',GRAPH/'result.json',GRAPH/'diagnostic.json.gz',CENSUS/'result.json',FAILED/'result.json',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_edge_finite_facade_distance_band_v2_20261010.py',HERE/'exact_original_edge_finite_facade_distance_band_20261010.py',*assets]
 spec=importlib.util.spec_from_file_location('one_bottom_edge_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 receipt=m.freeze(BATCH,'complete-four-original-strip-lower-edge-fixed-band-diagnostic-v1',refs,dict(uids=sorted(r['uid'] for r in rows),completeOriginalFaces=len(whole),components=list(COMPONENTS),allFourCompleteBottomEdgesInFixedBand=all(r['allCompleteBottomEdgesWithinFixedBand'] for r in results),sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False,installationApproved=False,currentHeldReason='source-owned-visual-role-and-independent-rooted-host-current-complete-physics-unresolved'))
 print(json.dumps(dict(jobId=receipt['jobId'],physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
