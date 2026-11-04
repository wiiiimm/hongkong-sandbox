"""Supervised complete original four-stream typed replay; no installation."""
import json,uuid,subprocess,sys,importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,reservations,digest
from evangel_college_whole_current_role_bound_20261011 import verify_files,DOCS,UID,pin_path
BATCH='government-xl-evangel-college-91306-whole-current-role-acceptance-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
VALIDATION=ROOT/'docs/astra-city/government-import/government-xl-evangel-college-91306-whole-role-code-validation-v1-20261011'
CODE_NAMES=['xl-evangel-college-91306-whole-current-role-acceptance-v1-20261011.py','evangel_college_whole_current_role_bound_20261011.py','evangel_college_whole_current_role_policy_20261011.py','test_evangel_college_whole_current_role_policy_20261011.py','evangel_college_named_lower_source_skin_v3_20261011.py','evangel_college_named_lower_source_skin_v2_20261011.py','evangel_college_named_two_upper_strips_v2_20261011.py','evangel_college_named_standing_grade_skin_20261011.py','test_evangel_college_named_remaining_source_roles_v3_20261011.py','test_evangel_college_named_standing_grade_skin_v2_20261011.py','evangel_college_post_elements_current_bound_wing_extension_identity_v3_20261011.py','evangel_college_original_wing_extension_identity_20261011.py','exact_cell_replay_with_original_routed_callable_20261011.py','exact_original_shared_edge_component_census_v2_20261011.py','xl-evangel-college-91306-remaining-original-lower-skin-and-two-strip-proposal-v3-20261011.py']
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();test=read(VALIDATION/'validation.json');assert test['passed']is True and test['tests']==36 and test['hermeticActualSourceCounterexamples']is True and test['productionCurrentNativeAndNeonReplayPerformedByTests']is False
 assert set(test['codeHashes'])=={str((HERE/n).relative_to(ROOT))for n in CODE_NAMES}
 assert digest((VALIDATION/'actual-adverse-tests.log').read_bytes())==test['testLogSHA256']
 for p,h in test['codeHashes'].items():assert digest((ROOT/p).read_bytes())==h
 role,entry=verify_files(LOCAL);assert reservations.owns(lease);save(DOC/'acceptance.json',role);save(DOC/'staged-original-entry.json',entry)
 refs=[Path(__file__),DOC/'acceptance.json',DOC/'staged-original-entry.json',VALIDATION/'validation.json',VALIDATION/'actual-adverse-tests.log']
 refs.extend(HERE/n for n in CODE_NAMES)
 for label,folder in DOCS.items():
  receipt=read(folder/'result.json');refs.append(folder/'result.json');refs.extend(pin_path(label,p)for p in receipt['evidenceRefs'])
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 assert reservations.owns(lease)
 spec=importlib.util.spec_from_file_location('evangel_typed_role_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);r=m.freeze(BATCH,'evangel-complete13960-226-four-stream-current-typed-role-acceptance',refs,dict(uids=[UID],completeOriginalFaces=13960,completeRealComponents=226,currentTypedPhysicalAccepted=True,acceptanceReadyForStaging=True,installationApproved=False,newlyInstalled=0));print(json.dumps(dict(jobId=r['jobId'])),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('evangel-whole-role-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
