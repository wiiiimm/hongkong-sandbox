"""Independent readback of all V3 transaction destinations after terminal rollback."""
import json, subprocess, sys, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
OLD=BASE/'government-xl-june-garden-original-installed-v3-20261103'
BATCH='government-xl-june-garden-v3-rollback-readback-v1-20261103'
LOCAL=HERE/'local'/BATCH

def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 assert subprocess.run(['ps','-p','1284489,1293832,1293876,1355364'],capture_output=True).returncode==1
 failure=read(OLD/'failure-recovery.json');assert failure['allPublicDestinationsRestored'] and not failure['rollbackErrors'] and not failure['derivedInstalledReviewHistoryRetained']
 history=read(OLD/'historical-input-context.json');saved={r['originalPath']:r for r in history['mutableCurrentByteSnapshots']};rows=[];refs=[Path(__file__),OLD/'failure-recovery.json',OLD/'historical-input-context.json']
 for rel in history['allMutableDestinations']:
  path=ROOT/rel
  if rel in saved:
   item=saved[rel];backup=ROOT/item['savedHistoricalBytes']['path'];assert digest(backup.read_bytes())==item['savedHistoricalBytes']['sha256']==item['originalSHA256'];assert path.read_bytes()==backup.read_bytes();refs.extend([path,backup]);rows.append(dict(path=rel,restoredSHA256=digest(path.read_bytes()),exists=True))
  else:
   assert not path.exists(),rel;rows.append(dict(path=rel,exists=False))
 assert len(rows)==16
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer)['snapshotId']==history['preInstallSnapshot']
 out=BASE/BATCH;log=out/'failed-worker.log';log.parent.mkdir(parents=True);log.write_bytes(Path('/tmp/astra-june-garden-original-install-v3-20261103.log').read_bytes());refs.append(log)
 result=dict(uids=read(OLD/'acceptance.json')['uids'],all16DestinationsIndependentlyRestored=True,rows=rows,preInstallSnapshot=history['preInstallSnapshot'],installedCredit=0,publication=False,workerTerminal=True,validatedDesktopCaptures=read(OLD/'viewport-1280/validated-browser-checkpoint.json')['validatedCaptureCount'],failureReason='Fail-closed V3 lease action returned an unclassified failure; exact subprocess cause was not recorded. No source corruption inferred.')
 save(out/'summary.json',result);assert reservations.owns(lease)
 module('june_v3_rollback_readback_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'independent-complete-transaction-rollback-readback',refs,result)
 print(dict(rollbackVerified=True,destinations=len(rows),installedCredit=0),flush=True)

if __name__=='__main__':
 if '--owned' in sys.argv:owned()
 else:
  assert not LOCAL.exists() and not(BASE/BATCH).exists()
  keys=read(HERE/'local'/OLD.name/'reservation.json')['resources'];claim=reservations.claim('june-v3-rollback-'+str(uuid.uuid4()),sorted(set(keys)|{'immutable-source-proof:'+BATCH}),batch=BATCH,ttl=3600);assert claim['ok']
  execute_reserved(claim['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
