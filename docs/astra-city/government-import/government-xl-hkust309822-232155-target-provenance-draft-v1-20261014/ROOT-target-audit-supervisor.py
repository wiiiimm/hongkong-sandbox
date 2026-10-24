from pathlib import Path
import hashlib,json,subprocess,sys,uuid
ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city')
HERE=ROOT/'source-scripts/city/government-import'
BASE=ROOT/'docs/astra-city/government-import'
PACKET=BASE/'government-xl-hkust309822-232155-target-provenance-draft-v1-20261014'
LOCAL=HERE/'local/government-xl-hkust-provider-target-audit-v1-20261014'
sys.path.insert(0,str(HERE))
from run import read,save,reservations
c=read(PACKET/'input-contract.json')
assert read(PACKET/'ROOT-TARGET-AUDIT-REVIEW.json')['rootReviewed']
assert not LOCAL.exists()
claim=reservations.claim('hkust-provider-target-audit-'+str(uuid.uuid4()),c['canonicalResources'],batch='government-xl-hkust-provider-target-audit-v1-20261014',ttl=3600)
assert claim['ok'],'Canonical HKUST target-audit resources unavailable'
lease=claim['reservation']
leasefile=LOCAL/'reservation.json'
try:
    save(leasefile,json.loads(json.dumps(lease,default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(leasefile),'--ttl','3600','--',sys.executable,str(PACKET/'two-original-target-interface-draft-v1.py'),'--audit-provider-target-only','--lease-file',str(leasefile)],cwd=ROOT,check=True)
finally:
    if reservations.owns(lease):assert reservations.release(lease)['ok']
assert not reservations.owns(lease)
out=PACKET/'exact-provider-target-audit-output-v1/target-audit.json'
r=read(out)
assert r['allInputHashesUnchanged'] and r['noModelDecode'] and not r['currentAcceptance']
save(PACKET/'ROOT-TARGET-AUDIT-TERMINAL.json',{'exitCode':0,'leaseReleased':True,'auditSHA256':hashlib.sha256(out.read_bytes()).hexdigest(),'literalRingMatches':[{'uid':a['uid'],'matched':a['literalPackedRingsEqualCurrent']}for a in r['records']],'sourceGeometryChanges':0,'currentAcceptance':False})
print(json.dumps(read(PACKET/'ROOT-TARGET-AUDIT-TERMINAL.json')),flush=True)
