"""Restore only exact interrupted Harbourfront publication bytes under a fresh lease."""
from pathlib import Path
import os,uuid
from run import ROOT,HERE,read,save,digest,reservations
from publication_lock import locked_publication
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-harbourfront-tower-original-installed-v1-20261021';BATCH='government-xl-harbourfront-install-recovery-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists() and not (OLD/'result.json').exists()
log=Path('/tmp/harbourfront-live-install-v1-20261021.log').read_text();assert 'lease-lost-or-renewal-failed' in log and '"released": true' in log
oldlease=read(HERE/'local'/OLD.name/'reservation.json');assert not reservations.owns(oldlease)
claim=reservations.claim(BATCH+'-'+uuid.uuid4().hex,oldlease['resources'],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
try:
 with locked_publication(ROOT):
  assert reservations.owns(lease)
  plan=read(BASE/'government-xl-harbourfront-tower-qualified-publication-plan-v1-20261021/publication-plan.json');history=read(OLD/'historical-input-context.json');saved={r['originalPath']:r for r in history['mutableCurrentByteSnapshots']};edits={r['destination']:r for r in plan['edits']+plan['assets']}
  for p,r in saved.items():
   original=ROOT/r['savedHistoricalBytes']['path'];assert digest(original.read_bytes())==r['originalSHA256']
   current=digest((ROOT/p).read_bytes());assert current in {r['originalSHA256'],edits.get(p,{}).get('source',{}).get('sha256')},p
  for p,r in edits.items():
   if p not in saved:assert not (ROOT/p).exists() or digest((ROOT/p).read_bytes())==r['source']['sha256'],p
  pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer)['snapshotId']==history['preInstallSnapshot']
  DOC.mkdir();(DOC/'terminal-worker.log').write_text(log)
  restored=[]
  for p,r in saved.items():
   dest=ROOT/p
   if digest(dest.read_bytes())==r['originalSHA256']:continue
   raw=(ROOT/r['savedHistoricalBytes']['path']).read_bytes();tmp=dest.with_name(dest.name+'.recovery-'+uuid.uuid4().hex);tmp.write_bytes(raw);os.replace(tmp,dest);restored.append(p)
  removed=[]
  for p,r in edits.items():
   if p not in saved and (ROOT/p).exists():
    assert digest((ROOT/p).read_bytes())==r['source']['sha256'];(ROOT/p).unlink();removed.append(p)
  for p,r in saved.items():assert digest((ROOT/p).read_bytes())==r['originalSHA256']
  summary=dict(failure='lease-renewal-supervisor-terminated-before-live-verification',restored=restored,removedExactNewDestinations=removed,currentSnapshot=history['preInstallSnapshot'],allPublicDestinationsRestored=True,newlyInstalled=0,modelCorruption=False,installationApproved=False,qualification='Interrupted publication recovered using exact saved pre-install bytes. Derived approved-for-integration history retained; no installed credit.')
  save(DOC/'summary.json',summary)
finally:
 if reservations.owns(lease):assert reservations.release(lease)['ok']
refs=[Path(__file__),OLD/'historical-input-context.json',OLD/'acceptance.json',BASE/'government-xl-harbourfront-tower-qualified-publication-plan-v1-20261021/publication-plan.json']
module('recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'interrupted-publication-exact-recovery',refs,summary)
