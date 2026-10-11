"""Fence complete source contact and raw ground evidence, no geometry or approvals."""
import importlib.util
from run import ROOT,HERE,read,save
from popcorn_original_ancillary_replay_20261009 import verify_frozen_role_receipt
BATCH='government-xl-popcorn-source-support-roles-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
def main():
 assert not (DOC/'result.json').exists(), 'Completed checkpoint immutable'
 replay=verify_frozen_role_receipt();save(DOC/'independent-identity-receipt-replay.json',replay)
 sp=importlib.util.spec_from_file_location('immutable_checkpoint_helper',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 names=['xl-popcorn-source-support-role-graph-20261009.py','xl-popcorn-source-support-all-contacts-20261009.py','xl-popcorn-source-support-rim-roles-20261009.py','xl-popcorn-source-support-ground-inputs-20261009.py','xl-popcorn-source-support-ground-20261009.mjs','xl-popcorn-source-support-primary-architect-20261009.py','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py','popcorn_original_ancillary_replay_20261009.py','support-contact.mjs']
 paths=[HERE/n for n in names]
 for b in ['government-xl-popcorn-source-access-ownership-20261009','government-xl-popcorn-original-pair-interface-20261009','government-xl-popcorn-complete-original-source-terrain-20261009']:
  prior=ROOT/'docs/astra-city/government-import'/b/'result.json';paths.append(prior)
  paths += [ROOT/r['path'] for r in read(prior)['evidenceRefs']]
 contact=read(DOC/'every-original-station-to-mall-contact.json.gz');ground=read(DOC/'whole-original-mall-ground-contact.json.gz')['wholeOriginalLowRim'];rim=read(DOC/'every-original-unresolved-rim-face-role.json.gz')
 m.freeze(BATCH,'complete-original-contact-graph-and-ground-roles-v1',paths,{'uids':['landsd/295538:0','landsd/295539:0'],'identityReceiptReplayVerified':True,'identityAccepted':False,'supportAccepted':False,'scriptFullAcceptancePassed':False,'fullExactMallContactPairs':len(contact['contacts']),'all9OriginalUpperComponentsAttached':True,'groundSamples':ground['samples'],'groundContacts':ground['contacts'],'rawDownwardGroundRimFailures':len(ground['failed']),'rawUpperSupportFailures':rim['rawFailureReasonCounts'],'remainingReason':'whole-original-ground-burial-and-upper-envelope-role-contract-plus-detached-12-face-panel-unresolved','nextStep':'Source-specific positive same-body grounded anchor and complete original visible surface roles; keep detached panel and physical/collision/runtime/browser gates independent. No global tolerance waiver.'})
if __name__=='__main__':main()
