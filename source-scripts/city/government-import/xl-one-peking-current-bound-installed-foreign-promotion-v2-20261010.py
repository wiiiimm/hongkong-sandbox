"""Fresh complete finite installed-foreign identity replay only; no physical approval."""
import json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from one_peking_current_bound_installed_foreign_identity_v2_20261010 import DOC as INPUT,verify_files,module
from one_peking_installed_hullett_finite_silhouette_identity_20261010 import OWN,FOREIGN
BATCH='government-xl-one-peking-current-bound-installed-foreign-promotion-v2-20261010'
DOC=INPUT.parent/BATCH;LOCAL=HERE/'local'/BATCH

def main():
 assert not DOC.exists()
 claim=reservations.claim('one-peking-current-identity-'+str(uuid.uuid4()),['building:'+OWN,'building:'+FOREIGN],batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  before=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes();assert digest(before)==read(INPUT/'current-inputs.json.gz')['manifestSHA256']
  row=read(INPUT/'selection.json.gz')['rows'][0];context=read(INPUT/'context.json.gz')['rows'][0]
  proof=verify_files(row,context,LOCAL)
  assert proof['passed'] and proof['reasons']==[] and proof['identityAccepted']
  assert not proof['physicalAccepted'] and not proof['collisionExemption'] and not proof['installationApproved']
  save(DOC/'identity.json',proof);save(DOC/'selection.json.gz',dict(rows=[row]));save(DOC/'context.json.gz',dict(rows=[context]))
  command=[sys.executable,'-m','unittest','test_one_peking_installed_hullett_finite_silhouette_identity_20261010','test_one_peking_current_bound_installed_foreign_identity_v2_20261010','-v']
  test=subprocess.run(command,cwd=HERE,text=True,capture_output=True)
  save(DOC/'actual-counterexample-tests.json',dict(command=command,exitCode=test.returncode,stdout=test.stdout,stderr=test.stderr,unmockedProductionCurrentNativeAndNeonReplay=True));assert test.returncode==0
  assert (ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before
  refs=[Path(__file__),INPUT/'result.json']+[HERE/f for f in ['one_peking_installed_hullett_finite_silhouette_identity_20261010.py','one_peking_current_bound_installed_foreign_identity_v2_20261010.py','one_peking_current_installed_foreign_inventory_20261010.py','test_one_peking_installed_hullett_finite_silhouette_identity_20261010.py','test_one_peking_current_bound_installed_foreign_identity_v2_20261010.py','routed_original_cell_identity.py','exact_original_georef_cell_identity_20261009.py','literal_production_module_dependency_closure_20261010.mjs','test_literal_production_module_dependency_closure_20261010.mjs']]
  result=module('peking_current_promotion_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-installed-foreign-finite-silhouette-identity-v2',refs,dict(uids=[OWN,FOREIGN],manifestSHA256=digest(before),identityAccepted=True,currentIdentityAccepted=True,physicalAccepted=False,installationApproved=False,foreignCollisionExemptions=0,completeOwnFaces=4114,completeInstalledForeignFaces=32635,completeCurrentForms=5,completeLiteralAndOriginalTargetCombinations=8,sourceGeometryChanges=0,sourceEvidenceInterpretationUsedAI=True,currentHeldReason='complete-original-source-support-terrain-foreign-runtime-gates-required',qualification='Exact named finite installed-original silhouette replaces only two raw footprint-proxy identity failures. Ordinary 1m2 threshold, complete current/provider identity, all other foreign actors and original/literal production geometry remain checked. No ownership, structural support, collision, terrain or installation credit.'))
  print(json.dumps(dict(jobId=result['jobId'],identityPassed=True,physicalAccepted=False,manifestSHA256=digest(before))),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
