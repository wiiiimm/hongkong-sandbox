"""Finish receipt after completed compute; parent lease collided with freezer lease."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-citywalk-current-foundation-v2-20261015';DOC=ROOT/'docs/astra-city/government-import'/BATCH
lease=read(HERE/'local'/BATCH/'lease.json');assert not reservations.owns(lease)
ground=read(DOC/'ground.json.gz');f=read(DOC/'foundation.json');assert len(f['rows'])==4 and all(r['foundation']['triangles']==41277 for r in f['rows'])
for p,h in ground['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p
plan=read(DOC/'plan.json');assert digest((ROOT/plan['sourceInput']['path']).read_bytes())==plan['sourceInput']['sha256']
log=Path('/tmp/citywalk-current-foundation-v2-20261015.log');assert log.read_text().count("'mode':")==4 and '"released": true' in log.read_text()
(DOC/'completed-compute-receipt-failure.log').write_bytes(log.read_bytes())
save(DOC/'recovery.json',dict(computeCompleted=True,priorSupervisorTerminal=1,priorLeaseReleased=True,failure='Freezer requested source-context resource already owned by its supervisor. No numeric failure; receipt resumed after verified release.',numericalReplay=False,installationApproved=False))
paths=[Path(__file__),HERE/'citywalk_current_foundation_v2_20261015.py',HERE/'xl-final-script-pass.py',HERE/'accepted/government-xl-citywalk-source-20261004/source-forms.json']+[ROOT/p for p in ground['inputHashes']]
module('citywalk_recovered_foundation_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-current-original-foundation-v1',paths,dict(uids=['landsd/134332:0'],fullAcceptance=False,sourceOnly=True,computeCompleted=True,receiptOnlyRecovery=True,nextStep='Current ground retains 35 buried faces and 6–7 incomplete sampled coverage faces. Attribute these against source-backed candidate terrain; do not install by resolving tower junction alone.'))
