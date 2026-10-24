"""Restore only byte-pinned outputs after a terminal original installer interruption."""
import argparse,os,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from publication_lock import locked_publication
from primrose_compound_foundation_v2_20261015 import module

def expected_states(root,history,plan,catalogue,destination):
 before={r['originalPath']:r for r in history['mutableCurrentByteSnapshots']};after=dict(plan['after'])
 for m in catalogue['models']:after[str((Path('3d-viewer')/destination).parent/m['asset'])]=m['sha256']
 saved={};observed={}
 for rel in history['allMutableDestinations']:
  p=root/rel;actual=digest(p.read_bytes())if p.exists()else None;q=before.get(rel);raw=None
  if q:
   raw=(root/q['savedHistoricalBytes']['path']).read_bytes();assert digest(raw)==q['originalSHA256']==q['savedHistoricalBytes']['sha256']
  expected=digest(raw)if raw is not None else None
  assert actual in {expected,after.get(rel,expected)},'Unexpected current destination: '+rel
  saved[rel]=raw;observed[rel]=actual
 return saved,observed

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','install','qualified']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args();assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.install,a.qualified])
 base=ROOT/'docs/astra-city/government-import';old=base/a.install;doc=base/a.batch;assert not doc.exists()and not(old/'result.json').exists()and not(old/'installed-acceptance.json').exists()
 # A lock file is insufficient. Inspect actual Python/Node command lines first.
 for p in Path('/proc').iterdir():
  if not p.name.isdigit()or int(p.name)==os.getpid():continue
  try:argv=[x.decode(errors='replace')for x in(p/'cmdline').read_bytes().split(b'\0')if x]
  except(OSError,PermissionError):continue
  if not argv or not any(x in Path(argv[0]).name for x in ['python','node']):continue
  assert not(any('selected_original_live_install_v2.py'in x for x in argv)and'--owned'in argv),'Original installer still live'
  assert not any('selected_original_guarded_publish_v2.py'in x for x in argv),'Original publisher still live'
  assert not('node'in Path(argv[0]).name and any(a.install in x for x in argv)),'Original live browser still running'
 leasefile=HERE/'local'/a.install/'reservation.json';oldlease=read(leasefile)
 if reservations.owns(oldlease):assert reservations.release(oldlease)['ok']
 keys=read(base/a.qualified/'qualification.json')['leaseResources'];claim=reservations.claim(a.batch+'-'+uuid.uuid4().hex,keys,batch=a.batch,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  with locked_publication(ROOT):
   assert reservations.owns(lease)
   initialRecovery=read(old/'failure-recovery.json');save(doc/'initial-failure-recovery.json',initialRecovery)
   history=read(old/'historical-input-context.json');stage=HERE/'accepted'/a.qualified;qualifiedplan=read(stage/'plan.json');assert len(qualifiedplan['areas'])==1
   pub=ROOT/'docs/astra-city/model-integration-20260909'/a.install/'publication-plan.json';plan=read(pub);assert plan['published']is False
   applied=read(old/'command-001.json');assert applied['exitCode']==0 and'--apply'in applied['command']
   saved,before=expected_states(ROOT,history,plan,read(stage/'catalogue.json'),qualifiedplan['areas'][0]['destination'])
   pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer)['snapshotId']==history['preInstallSnapshot']
   for rel,raw in sorted(saved.items(),key=lambda x:x[0]=='3d-viewer/city/data/manifest.json'):
    assert reservations.owns(lease);p=ROOT/rel
    if raw is None:p.unlink(missing_ok=True)
    elif digest(p.read_bytes())!=digest(raw):
     tmp=p.with_name(p.name+'.restore-'+uuid.uuid4().hex);tmp.write_bytes(raw);os.replace(tmp,p)
   rows=[]
   for rel,raw in saved.items():
    p=ROOT/rel;sha=digest(p.read_bytes())if p.exists()else None;assert sha==(digest(raw)if raw is not None else None);rows.append(dict(path=rel,observedInterruptedSHA256=before[rel],restoredSHA256=sha))
   result=dict(error='Terminal original installer failure; exact outputs independently verified/restored under fresh ownership.',initialFailure=initialRecovery,allPublicDestinationsRestored=True,currentPointerRestoredNotDerivedCredit=True,derivedInstalledReviewHistoryRetained=False,rollbackErrors=[],verifiedExpectedStatesAndRestoration=rows,newlyInstalled=0)
   save(old/'failure-recovery.json',result);save(doc/'recovery.json',result)
  refs=[Path(__file__),old/'historical-input-context.json',old/'acceptance.json',old/'command-001.json',old/'failure-recovery.json',pub,stage/'plan.json',stage/'catalogue.json',doc/'recovery.json',doc/'initial-failure-recovery.json']
  module('original_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-interrupted-original-publication-recovery',refs,dict(uids=[m['uid']for m in read(stage/'catalogue.json')['models']],restored=True,installationApproved=False,sourceCorruption=False,newlyInstalled=0))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
