"""Fixed .1m full-facet Lippo detail association, diagnostic only."""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify
BATCH='government-xl-lippo-two-unresolved-source-detail-fixed-band-diagnostic-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
GRAPH=DOC.parent/'government-xl-lippo-three-complete-original-edge-components-and-contacts-v1-20261011'
GROUND=DOC.parent/'government-xl-lippo-three-real-facet-ordinary-ground-diagnostic-v1-20261011'
INPUT=DOC.parent/'government-xl-lippo-two-original-current-physical-inputs-v2-20261011'
LANGHAM=DOC.parent/'government-xl-lippo-langham-current-original-recovery-v1-20261011'
def main():
 assert not DOC.exists();graph=read(GRAPH/'diagnostic.json.gz');ground=read(GROUND/'diagnostic.json.gz');assert ground['unresolvedRealFacetComponents']==[11,14]
 rows=sorted(read(INPUT/'check-selection.json.gz')['rows']+read(LANGHAM/'check-selection.json.gz')['rows'],key=lambda r:r['uid']);assets=[ROOT/r['candidate']['path'] for r in rows]
 for row,path in zip(rows,assets):assert digest(path.read_bytes())==row['sourceSHA256']
 whole=np.concatenate([decode_original_world_triangles(p.read_bytes()) for p in assets]);assert digest(whole.tobytes())==ground['wholeSourceWorldSHA256']
 hosts=sorted(f for n in graph['nodes'] if n['component'] in ground['resolvedRealFacetComponents'] for f in n['globalOriginalFaces']);assert not set(hosts)&set(f for n in graph['nodes'] if n['component'] in [11,14] for f in n['globalOriginalFaces'])
 records=[]
 for k in [11,14]:
  node=graph['nodes'][k];faces=[dict(originalSourceFace=i,completeFixedBandProof=verify(whole[i],whole[hosts])) for i in node['globalOriginalFaces']]
  records.append(dict(component=k,uid=node['uid'],completeOriginalFaces=node['globalOriginalFaces'],faces=faces,wholeComponentAssociated=all(r['completeFixedBandProof'].get('wholeFacetAssociated') for r in faces),sourceRoleAccepted=False,groundRootAccepted=False))
 result=dict(completeOriginalFaces=len(whole),completeGroundReachableHostFaceIDs=hosts,rows=records,sourceGeometryChanges=0,strictBandM=.1,visualRoleAccepted=False,groundRootCredit=False,physicalAccepted=False,installationApproved=False,qualification='Complete unchanged source-only finite association to all exact ground-reachable original facets. Fixed .1m unchanged; full exact interiors and boundaries checked. Neither function nor source visual/support role follows from proximity. Actual literal/current complete ground/foreign/foundation/runtime and explicit role evidence remain separate.')
 save(DOC/'diagnostic.json.gz',result)
 refs=[Path(__file__),GRAPH/'result.json',GRAPH/'diagnostic.json.gz',GROUND/'result.json',GROUND/'diagnostic.json.gz',INPUT/'check-selection.json.gz',LANGHAM/'check-selection.json.gz',HERE/'exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py',HERE/'test_exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py',*assets]
 sp=importlib.util.spec_from_file_location('lippo_source_band_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 receipt=m.freeze(BATCH,'two-unresolved-original-detail-fixed-band-diagnostic-v1',refs,dict(uids=['landsd/231645:0'],completeOriginalFaces=len(whole),componentOutcomes=[dict(component=r['component'],wholeComponentAssociated=r['wholeComponentAssociated']) for r in records],strictBandM=.1,visualRoleAccepted=False,groundRootCredit=False,physicalAccepted=False,installationApproved=False))
 print(json.dumps(dict(jobId=receipt['jobId'],outcomes=[dict(component=r['component'],wholeAssociated=r['wholeComponentAssociated']) for r in records])),flush=True)
if __name__=='__main__':main()
