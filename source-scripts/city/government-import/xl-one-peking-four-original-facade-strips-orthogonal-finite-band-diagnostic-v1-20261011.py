"""New complete orthogonal finite .1m host association diagnostic for four original strips.

Association is not an accepted visual role or grounded structural support. Every
source face is retained, including zero-area primitive records; existing roof
plate43/44 failure is not rerun or silently reconsidered.
"""
from pathlib import Path
import json,importlib.util
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify as orthogonal_band
BATCH='government-xl-one-peking-four-original-facade-strips-orthogonal-finite-band-diagnostic-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
GRAPH=DOC.parent/'government-xl-one-peking-original-ordinary-ground-graph-diagnostic-v2-20261010'
PHYS=DOC.parent/'government-xl-one-peking-two-original-retained-hullett-child-current-physical-v5-20261010'
def main():
 assert not DOC.exists();g=read(GRAPH/'diagnostic.json.gz');rows=sorted(read(PHYS/'selection.json.gz')['rows'],key=lambda r:r['uid']);assets=[ROOT/r['candidate']['path'] for r in rows]
 for p,r in zip(assets,rows):assert digest(p.read_bytes())==r['sourceSHA256']
 a=np.concatenate([decode_original_world_triangles(p.read_bytes()) for p in assets]);assert digest(a.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256']
 targets=[27,34,46,49];assert not set(targets)&set(g['resolvedOriginalComponents'])
 hosts=sorted(f for k in g['resolvedOriginalComponents'] for f in g['components'][k]['globalOriginalFaces'] if g['components'][k]['actorUID']=='landsd/240487:0');complete_host=a[hosts];results=[]
 for k in targets:
  component=g['components'][k];assert component['actorUID']=='landsd/240487:0'
  faces=[]
  for f in component['globalOriginalFaces']:
   proof=orthogonal_band(a[f],complete_host)
   faces.append(dict(globalOriginalFace=f,completeOriginalTriangle=a[f].tolist(),finiteAssociation=proof))
  results.append(dict(component=k,completeOriginalFaceIDs=component['globalOriginalFaces'],completeWorldBounds=[a[component['globalOriginalFaces']].min((0,1)).tolist(),a[component['globalOriginalFaces']].max((0,1)).tolist()],completeFaceProofs=faces,allFacesAssociated=all(v['finiteAssociation']['wholeFacetAssociated'] for v in faces),nondegenerateAssociatedFaceCount=sum(v['finiteAssociation']['wholeFacetAssociated'] for v in faces),visualRoleAccepted=False,supportAccepted=False))
  print(json.dumps(dict(component=k,faces=len(faces),associated=results[-1]['nondegenerateAssociatedFaceCount'])),flush=True)
 out=dict(completeOriginalWorldSHA256=digest(a.tobytes()),groundedHostComponentIds=[k for k in g['resolvedOriginalComponents'] if g['components'][k]['actorUID']=='landsd/240487:0'],completeGroundedHostOriginalFaceIDs=hosts,completeHostWorldSHA256=digest(complete_host.tobytes()),strictEuclideanBandM=.1,priorAxisBandFailurePreserved=True,uids=[r['uid'] for r in rows],completeFourComponentProofs=results,historicalCandidateGroundOnly=True,sourceGeometryChanges=0,visualRoleAccepted=False,supportAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Exact complete finite .1m orthogonal Euclidean foot association only. Exact inward rational plane-distance bands cannot increase the limit. Prior coordinate-axis failure remains preserved. Every source face and historical ordinary-ground-reached same-original host face retained; current root acceptance still separate. No named function, load-bearing role, structural root or installation credit. Degenerate source primitive records remain unresolved if this area-facet diagnostic cannot classify them; no omission or threshold change.')
 save(DOC/'diagnostic.json.gz',out)
 refs=[Path(__file__),GRAPH/'result.json',GRAPH/'diagnostic.json.gz',PHYS/'result.json',PHYS/'selection.json.gz',HERE/'exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py',HERE/'test_exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py',HERE/'exact_original_surface_coordinate_band_20261010.py',DOC.parent/'government-xl-one-peking-four-facade-band-negative-preservation-v1-20261011/result.json',HERE/'exact_original_slab_projection_coverage_20261010.py',HERE/'exact_original_projection_coverage_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',*assets]
 sp=importlib.util.spec_from_file_location('peking_strips_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);r=m.freeze(BATCH,'complete-four-original-facade-strip-orthogonal-finite-host-fixed-band-source-only-diagnostic-v1',refs,out)
 print(json.dumps(dict(jobId=r['jobId'],sourceOnly=True,physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
