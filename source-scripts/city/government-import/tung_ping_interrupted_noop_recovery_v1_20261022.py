"""Prove the interrupted Tung Ping attempt left every public byte unchanged."""
from pathlib import Path
import uuid
from run import ROOT,HERE,read,save,digest,reservations
from publication_lock import locked_publication
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-tung-ping-interrupted-noop-recovery-v1-20261022'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
OLD=BASE/'government-xl-tung-ping-retained-original-installed-v4-20261022'
assert not DOC.exists() and not (OLD/'result.json').exists() and not (OLD/'installed-acceptance.json').exists()
history=read(OLD/'historical-input-context.json')
qualification=BASE/'government-xl-tung-ping-retained-qualified-stage-v1-20261022/qualification.json'
claim=reservations.claim(BATCH+'-'+uuid.uuid4().hex,read(qualification)['leaseResources'],batch=BATCH,ttl=3600)
assert claim['ok'];lease=claim['reservation']
try:
 with locked_publication(ROOT):
  assert reservations.owns(lease)
  saved={r['originalPath']:r for r in history['mutableCurrentByteSnapshots']};rows=[]
  for rel in history['allMutableDestinations']:
   p=ROOT/rel;actual=digest(p.read_bytes()) if p.exists() else None
   q=saved.get(rel);expected=q['originalSHA256'] if q else None
   if q:assert digest((ROOT/q['savedHistoricalBytes']['path']).read_bytes())==q['savedHistoricalBytes']['sha256']==expected
   assert actual==expected,rel
   rows.append(dict(path=rel,restoredSHA256=actual,changed=False))
  assert read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')['snapshotId']==history['preInstallSnapshot']
  proof=dict(error='Supervisor lease renewal observation failed; child is terminal. All destinations remained exactly pre-install; no restoration writes needed.',allPublicDestinationsRestored=True,currentPointerRestoredNotDerivedCredit=True,derivedInstalledReviewHistoryRetained=False,rollbackErrors=[],verifiedExpectedStatesAndRestoration=rows,newlyInstalled=0)
  save(OLD/'failure-recovery.json',proof);save(DOC/'recovery.json',proof)
 module('tung_ping_noop_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'interrupted-original-publication-unchanged',[Path(__file__),OLD/'historical-input-context.json',OLD/'acceptance.json',OLD/'failure-recovery.json',qualification,DOC/'recovery.json'],dict(uids=['landsd/97301:0'],restored=True,sourceCorruption=False,installationApproved=False,newlyInstalled=0))
finally:
 if reservations.owns(lease):assert reservations.release(lease)['ok']
