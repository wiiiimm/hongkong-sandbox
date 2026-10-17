"""Freeze a nonaccepting exact source/current-join proposal and adversarial tests.
Historical current capture stays historical; no fresh-current acceptance here.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys
from run import ROOT,HERE,read,save,digest,connect
from lippo_tower_current_basic_mainbody_join_actual_fixture_v1_20261011 import fixture,INPUT,SUPPORT,PARTITION,FOREIGN
from lippo_tower_current_basic_mainbody_join_role_v1_20261011 import verify
BATCH='government-xl-lippo-mainbody-current-basic-join-source-proposal-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
CONTEXT=DOC.parent/'government-xl-lippo-bounded-lower-mainbody-source-role-context-v2-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__)];receipts=[]
 for folder in [INPUT,SUPPORT,PARTITION,FOREIGN,CONTEXT]:
  receipt=read(folder/'result.json')
  with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  receipts.append(dict(folder=str(folder.relative_to(ROOT)),jobId=receipt['jobId'],receipt=ref(folder/'result.json')));refs.append(folder/'result.json')
 data=fixture();result=verify(data);assert result['physicalAccepted'] is False and result['installationApproved'] is False
 save(DOC/'diagnostic.json.gz',result)
 test=HERE/'test_lippo_tower_current_basic_mainbody_join_role_v1_20261011.py';proc=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(HERE),'-p',test.name,'-v'],cwd=ROOT,capture_output=True,text=True)
 save(DOC/'tests.json',dict(exitCode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr,hermeticActualSourceCounterexamples=True,separateUnmockedProductionCurrentNativeAndNeonReplay=False,historicalImmutableSourceAndCurrentFixture=True));assert proc.returncode==0,proc.stderr
 methods=['lippo_tower_current_basic_mainbody_join_role_v1_20261011.py','lippo_tower_current_basic_mainbody_join_actual_fixture_v1_20261011.py',test.name,'xl-lippo-tower-current-basic-complete-lower-interface-partition-v2-20261011.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','exact_original_finite_triangle_contacts_20261010.py','exact_closed_two_level_mesh_vertical_ray_20261010.py']
 refs += [HERE/n for n in methods]
 inputs=[INPUT/'input.json.gz',INPUT/'complete-current-geometry.json.gz',SUPPORT/'diagnostic.json.gz',SUPPORT/'complete-actual-basic-finite-facets.json.gz',SUPPORT/'bounded-basic-grade-roof-paths.json.gz',PARTITION/'diagnostic.json.gz',FOREIGN/'diagnostic.json.gz',CONTEXT/'diagnostic.json.gz',CONTEXT/'complete-original-and-current-basic-2400x1500.png',CONTEXT/'lower-interface-original-detail-2400x1500.png']
 inputs += sorted(SUPPORT.glob('complete-tower-finite-*.json.gz'));refs += inputs
 row=read(INPUT/'input.json.gz')['rows'][0];refs.append(ROOT/row['candidate']['path'])
 save(DOC/'source-context.json',dict(sourceGeometryChanges=0,terrainGeometryChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,historicalCapturedManifest=read(INPUT/'input.json.gz')['currentManifest'],sourceAndExactCurrentJoinProposalOnly=True,freshCurrentFinalIdentityNativePhysicsAndBrowserRequired=True,receipts=receipts,sourceRoleAccepted=False,physicalAccepted=False,installationApproved=False))
 refs += [DOC/'diagnostic.json.gz',DOC/'tests.json',DOC/'source-context.json']
 snapshot=[ref(p) for p in refs]
 for r in snapshot:assert ref(ROOT/r['path'])==r
 s=importlib.util.spec_from_file_location('lippo_mainbody_join_proposal_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 receipt=m.freeze(BATCH,'lippo-unchanged-lower-mainbody-current-basic-exact-four-stream-join-proposal-only',refs,dict(uids=['landsd/239465:0','landsd/231645:0'],sourceGeometryChanges=0,terrainGeometryChanges=0,sourceRoleAccepted=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0,completeOriginalFaces=3597,completeCurrentBasicFaces=284,uncreditedSourceZeroAreaFaces=[13,25,2091,2744],currentFinalRebindRequired=True))
 print(json.dumps(dict(jobId=receipt['jobId'],sourceProposalOnly=True)),flush=True)
if __name__=='__main__':main()
