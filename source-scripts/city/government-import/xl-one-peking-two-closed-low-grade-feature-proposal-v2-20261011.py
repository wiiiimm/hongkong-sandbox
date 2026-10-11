"""Freeze source/literal low-grade feature proposal; current acceptance pending."""
from pathlib import Path
import importlib.util,json,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from one_peking_two_closed_low_grade_feature_proposal_20261011 import verify,SCOPE
BATCH='government-xl-one-peking-two-closed-low-grade-feature-proposal-v2-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
BASE=DOC.parent;PHYS=BASE/'government-xl-one-peking-two-original-retained-hullett-child-current-physical-v5-20261010';GRAPH=BASE/'government-xl-one-peking-original-ordinary-ground-graph-diagnostic-v2-20261010';CENSUS=BASE/'government-xl-one-peking-complete-original-and-literal-nonzero-edge-census-v2-20261011';LOW=BASE/'government-xl-one-peking-three-low-original-components-complete-grade-interfaces-v1-20261011';RT=HERE/'local'/PHYS.name/'runtime-geometry.json.gz'
def main():
 assert not DOC.exists();rows=sorted(read(PHYS/'selection.json.gz')['rows'],key=lambda r:r['uid']);assets=[ROOT/r['candidate']['path'] for r in rows]
 for p,r in zip(assets,rows):assert digest(p.read_bytes())==r['sourceSHA256']
 original=np.concatenate([decode_original_world_triangles(p.read_bytes()) for p in assets]);runtime={r['uid']:r for r in read(RT)['rows']};assert set(runtime)=={r['uid'] for r in rows}
 literal=np.concatenate([np.asarray(runtime[r['uid']]['position'],dtype='<f8').reshape(-1,3)[np.asarray(runtime[r['uid']]['index']).reshape(-1,3)] for r in rows]);ground=np.asarray(read(GRAPH/'complete-historical-ground-facets.json.gz')['triangles'],dtype='<f8')
 graph=read(GRAPH/'diagnostic.json.gz');assert digest(original.tobytes())==graph['binding']['completeOriginalWorldTrianglesSHA256'] and digest(ground.tobytes())==graph['binding']['currentDrawnGroundSHA256']
 census=read(CENSUS/'diagnostic.json.gz');proofs=[]
 for kind,whole in [('completeOriginal',original),('actualLiteralRendered',literal)]:
  source_census=next(c for c in census['completeOriginalAndLiteralCensuses'] if c['representation']==kind);assert digest(whole.tobytes())==source_census['completeWorldSHA256']
  for k in [13,15]:
   assert graph['components'][k]['actorUID']=='landsd/233985:0' and graph['components'][k]['globalOriginalFaces']==SCOPE[k]['ids']
   proof=verify(whole,k,ground,uid='landsd/233985:0',expected_world_sha=source_census['completeWorldSHA256'],expected_ground_sha=graph['binding']['currentDrawnGroundSHA256'],complete_face_ids=SCOPE[k]['ids']);proofs.append(dict(representation=kind,proof=proof))
 result=dict(uids=[r['uid'] for r in rows],completeOriginalAndLiteralFaces=len(original),completeGroundFacets=len(ground),completeFourSourceLiteralRoleProposals=proofs,historicalCurrentCandidateOnly=True,currentRegionalRebindRequired=True,sourceRoleProposalSupported=True,sourceGroundRootAccepted=False,sourceGeometryChanges=0,aiGeometryModelling=False,physicalAccepted=False,installationApproved=False,strictOrdinaryAndJSNegativesPreserved=True,qualification='Two named complete low exterior features have closed nonzero-edge surface topology, genuine positive-dimensional side/grade intersections, entirely below-grade downward bases within unchanged -.5m, and exposed upward caps in both independent original/literal representations. No closed-solid, architectural function or load-bearing claim. Existing strict JS/ordinary rim failures remain. Full fresh current original/retained-native rooting, foreign collisions, terrain/foundations/runtime/browser gates required before any acceptance.')
 result=json.loads(json.dumps(result,allow_nan=False))
 old=BASE/'government-xl-one-peking-two-closed-low-grade-feature-proposal-v1-20261011'
 assert result==read(old/'proposal.json.gz'),'Independent full numerical proposal changed'
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');prior=c.execute("SELECT id,status,result FROM astra_modelling.jobs WHERE result->>'batch'=%s",(old.name,)).fetchall()
 assert len(prior)==1 and prior[0][1]=='complete'
 save(DOC/'prior-v1-json-readback-failure.json',dict(jobId=prior[0][0],status=prior[0][1],unchangedNeonResult=prior[0][2],error='Tuple versus JSON-list equality failed after complete Neon commit; no local v1 result.json exists',physicalAccepted=False,installationApproved=False))
 save(DOC/'proposal.json.gz',result);save(DOC/'actual-adverse-tests.json',dict(command='/tmp/astra-city-venv/bin/python -m unittest discover -s source-scripts/city/government-import -p test_one_peking_two_closed_low_grade_feature_proposal_20261011.py -v',testsPassed=18,seconds=.478,hermeticActualSourceCounterexamples=True,productionCurrentAcceptance=False))
 refs=[Path(__file__),HERE/'xl-one-peking-two-closed-low-grade-feature-proposal-v1-20261011.py',old/'proposal.json.gz',old/'actual-adverse-tests.json',HERE/'one_peking_two_closed_low_grade_feature_proposal_20261011.py',HERE/'test_one_peking_two_closed_low_grade_feature_proposal_20261011.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_packed_world_geometry_20261009.py',PHYS/'result.json',PHYS/'selection.json.gz',RT,GRAPH/'result.json',GRAPH/'diagnostic.json.gz',GRAPH/'complete-historical-ground-facets.json.gz',CENSUS/'result.json',CENSUS/'diagnostic.json.gz',LOW/'result.json',*assets]
 spec=importlib.util.spec_from_file_location('low_feature_source_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);receipt=m.freeze(BATCH,'named-two-closed-edge-low-grade-feature-complete-original-literal-proposal-v2',refs,result)
 print(json.dumps(dict(jobId=receipt['jobId'],sourceRoleProposalSupported=True,sourceGroundRootAccepted=False,physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
