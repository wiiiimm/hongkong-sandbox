from pathlib import Path
import hashlib,json,subprocess,sys,uuid
ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city')
HERE=ROOT/'source-scripts/city/government-import'
PACKET=ROOT/'docs/astra-city/government-import/government-xl-hkust309822-232155-target-provenance-draft-v1-20261014'
LOCAL=HERE/'local/government-xl-hkust-cached-original-arrays-v1-20261014'
sys.path.insert(0,str(HERE))
from run import read,save,reservations
c=read(PACKET/'input-contract.json')
t=read(PACKET/'ROOT-TARGET-AUDIT-TERMINAL.json')
assert t['exitCode']==0 and t['leaseReleased'] and all(r['matched']for r in t['literalRingMatches'])
assert not LOCAL.exists() and not(PACKET/'cached-complete-original-arrays-v1').exists()
claim=reservations.claim('hkust-cached-original-arrays-'+str(uuid.uuid4()),c['canonicalResources'],batch='government-xl-hkust-cached-original-arrays-v1-20261014',ttl=3600)
assert claim['ok'],'Canonical HKUST original-array resources unavailable'
lease=claim['reservation'];leasefile=LOCAL/'reservation.json'
try:
    save(leasefile,json.loads(json.dumps(lease,default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(leasefile),'--ttl','3600','--',sys.executable,str(PACKET/'two-original-target-interface-draft-v1.py'),'--prepare-cached-original-arrays-only','--lease-file',str(leasefile)],cwd=ROOT,check=True)
finally:
    if reservations.owns(lease):assert reservations.release(lease)['ok']
assert not reservations.owns(lease)
receipt=PACKET/'cached-complete-original-arrays-v1/array-receipt.json';r=read(receipt)
assert r['allInputHashesUnchanged'] and r['originalPoseChanges']==r['sourceGeometryChanges']==0
for row in r['rows']:assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
out={'exitCode':0,'leaseReleased':True,'arrayReceiptSHA256':hashlib.sha256(receipt.read_bytes()).hexdigest(),'rows':r['rows'],'sourceGeometryChanges':0,'currentAcceptance':False}
save(PACKET/'ROOT-CACHED-ARRAYS-TERMINAL.json',out)
print(json.dumps(out),flush=True)
