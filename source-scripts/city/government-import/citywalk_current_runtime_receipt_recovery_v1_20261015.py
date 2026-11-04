"""Recover completed runtime results using each producer's actual hash schema."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citywalk-current-runtime-checks-v1-20261015';DOC=BASE/BATCH
m=read(DOC/'metrics.json');v=read(DOC/'validation.json');assert len(m['rows'])==1 and v['models']==v['loaderAccepted']==v['checksPassed']==1 and v['exceptions']==0
paths=[Path(__file__),HERE/'citywalk_current_runtime_checks_v1_20261015.py',HERE/'acceptance-metrics.mjs',HERE.parent/'building-batch/validate_candidates.mjs']
for hashes in [m['inputHashes'],v['hashes']]:
 for p,h in hashes.items():assert digest((ROOT/p).read_bytes())==h,p;paths.append(ROOT/p)
policy=module('citywalk_current_policy',HERE/'acceptance-policy.py');identity=read(BASE/'government-xl-remaining-20260923/sol-hold-resolution-20261004/citywalk-contact-rescue/identity-resolution.json')['rows'][0];assert identity['identityAccepted'] and identity['exactObjectAndCSUID']
reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=m['rows'][0]['sourceSHA256'],identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True)),m['rows'][0],m['profiles']['mobile']);assert not reasons,reasons
paths.extend([HERE/'acceptance-policy.py',BASE/'government-xl-remaining-20260923/sol-hold-resolution-20261004/citywalk-contact-rescue/identity-resolution.json'])
(DOC/'receipt-schema-failure.log').write_bytes(Path('/tmp/citywalk-current-runtime-checks-v1-20261015.log').read_bytes())
save(DOC/'policy.json',dict(remainingReasons=reasons,loaderConcerns=v['results'][0]['concerns'],qualification='Global maximum terrain above global source minimum remains contextual; full four-mode foundation and all local metrics are separate evidence. Source-junction and neighbours not approved here.',numericReplay=False))
module('citywalk_runtime_recovery_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-original-runtime-metrics-and-loader-v1',paths,dict(uids=['landsd/134332:0'],fullAcceptance=False,ordinaryPolicyReasons=reasons,loaderAccepted=1,exceptions=0,receiptOnlyRecovery=True,originalSourceAndFormUnchanged=True))
