"""Real fresh complete current identity replay only; no physical/publication credit."""
from pathlib import Path
import json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations
from lippo_current_bound_six_roof_identity_v2_20261010 import DOC as INPUT,verify_files,module,EXPECTED_RAW_REASONS
from lippo_three_original_current_inventory_20261010 import EXPECTED,catalogue_inventory
BATCH='government-xl-lippo-current-bound-six-roof-promotion-v2-20261010';DOC=INPUT.parent/BATCH;LOCAL=HERE/'local'/BATCH
def main():
 assert not DOC.exists()
 claim=reservations.claim('lippo-current-identity-'+str(uuid.uuid4()),['building:'+u for u in EXPECTED],batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  manifest=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes();capture=read(INPUT/'current-inputs.json.gz');assert digest(manifest)==capture['manifestSHA256']
  inventory=catalogue_inventory(manifest);assert inventory==capture['catalogueInventory']
  row=next(r for r in read(INPUT/'selection.json.gz')['rows'] if r['uid']=='landsd/231645:0');context=read(INPUT/'context.json.gz')['rows'][0]
  proof=verify_files(row,context,LOCAL)
  assert proof['passed'] and proof['identityAccepted'] and proof['reasons']==[]
  assert proof['rawNativeIdentityReasons']==proof['rawFullCellIdentity']['reasons']==EXPECTED_RAW_REASONS
  assert not proof['physicalAccepted'] and not proof['installationApproved']
  assert proof['currentBinding']['completeActualRenderAttributeFloat32StreamsVerified']
  save(DOC/'identity.json',proof);save(DOC/'selection.json.gz',dict(rows=[row]));save(DOC/'context.json.gz',dict(rows=[context]))
  command=[sys.executable,'-m','unittest','test_lippo_current_bound_six_roof_identity_v2_20261010','test_lippo_actual_render_float32_diagnostic_20261010','-v']
  test=subprocess.run(command,cwd=HERE,text=True,capture_output=True)
  save(DOC/'actual-counterexample-tests.json',dict(command=command,exitCode=test.returncode,stdout=test.stdout,stderr=test.stderr,separateProductionReplayBeforeTests=True,hermeticActualSourceCounterexamples=True));assert test.returncode==0
  assert (ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==manifest and catalogue_inventory(manifest)==inventory
  refs=[Path(__file__),INPUT/'result.json',DOC.parent/'government-xl-lippo-actual-render-attributes-and-float32-world-diagnostic-v1-20261010/result.json',DOC.parent/'government-xl-lippo-current-binding-hermetic-fixtures-v2-20261010/manifest-and-catalogue-bytes.json.gz']
  refs += [HERE/p for p in ['lippo_current_bound_six_roof_identity_v2_20261010.py','test_lippo_current_bound_six_roof_identity_v2_20261010.py','lippo_actual_render_float32_diagnostic_20261010.py','test_lippo_actual_render_float32_diagnostic_20261010.py','lippo_original_six_roof_current_scope_proposal_v2_20261010.py','lippo_three_original_current_inventory_20261010.py','xl-lippo-current-bound-six-roof-inputs-v2-20261010.py','xl-lippo-original-actual-render-attribute-geometry-v1-20261010.mjs','exact_original_georef_cell_identity_20261009.py','routed_original_cell_identity.py','exact_original_finite_triangle_contacts_20261010.py','literal_production_module_dependency_closure_20261010.mjs']]
  result=module('lippo_current_promotion_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-three-source-six-roof-finite-identity-and-f32-replay-v2',refs,dict(uids=sorted(EXPECTED),manifestSHA256=digest(manifest),identityAccepted=True,currentIdentityAccepted=True,physicalAccepted=False,installationApproved=False,foreignCollisionExemptions=0,completeOwnFaces=13725,completeAllSourceFaces=29580,completeCurrentForms=12,completeFloat32Representations=2,rawIdentityFailuresPreserved=EXPECTED_RAW_REASONS,testsPassed=49,sourceGeometryChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,currentHeldReason='complete-original-and-rendered-support-terrain-all-current-foreign-runtime-gates-required',qualification='Only two exact named raw2D foreign identity reasons are reconsidered using six complete source roof-face roles, exact source/literal/F32 finite associations and all ordinary spatial/source/provider/current/native guards. Silvercord remains full current basic physical foreign actor. No common ownership, support, collision, terrain or installation credit; camera/GPU arithmetic remains qualified separately.'))
  print(json.dumps(dict(jobId=result['jobId'],identityPassed=True,physicalAccepted=False,manifestSHA256=digest(manifest))),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
