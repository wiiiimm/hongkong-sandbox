"""Post-supervisor recovery survives a killed child; exact-byte checks prevent overwrites."""
import os,uuid
from run import read,save,digest,reservations
from publication_lock import locked_publication

def recover(root,here,doc,prep,resources):
 claim=reservations.claim('publication-recovery-'+uuid.uuid4().hex,resources,batch=doc.name+'-recovery',ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  with locked_publication(root):
   assert reservations.owns(lease)
   if (doc/'result.json').exists():return
   history=read(doc/'historical-input-context.json');plan=read(prep/'publication-plan.json');saved={r['originalPath']:r for r in history['mutableCurrentByteSnapshots']};edits={r['destination']:r for r in plan['edits']+plan['assets']}
   # Never overwrite another publication or an unexpected progress/snapshot change.
   for p,r in saved.items():
    assert digest((root/r['savedHistoricalBytes']['path']).read_bytes())==r['originalSHA256']
    assert digest((root/p).read_bytes()) in {r['originalSHA256'],edits.get(p,{}).get('source',{}).get('sha256')},p
   for p,r in edits.items():
    if p not in saved:assert not (root/p).exists()or digest((root/p).read_bytes())==r['source']['sha256'],p
   for p,r in saved.items():
    dest=root/p
    if digest(dest.read_bytes())==r['originalSHA256']:continue
    tmp=dest.with_name(dest.name+'.restore-'+uuid.uuid4().hex);tmp.write_bytes((root/r['savedHistoricalBytes']['path']).read_bytes());os.replace(tmp,dest)
   for p,r in edits.items():
    if p not in saved:(root/p).unlink(missing_ok=True)
   for p,r in saved.items():assert digest((root/p).read_bytes())==r['originalSHA256']
   save(doc/'supervisor-recovery.json',dict(allPublicDestinationsRestored=True,currentSnapshot=history['preInstallSnapshot'],newlyInstalled=0,qualification='Parent cleanup after supervisor termination; exact-byte fenced recovery. No model rejection.'))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
