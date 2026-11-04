from pathlib import Path
import hashlib,json,subprocess,sys,uuid
ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city')
HERE=ROOT/'source-scripts/city/government-import'
PACKET=ROOT/'docs/astra-city/government-import/government-xl-hkust309822-232155-target-provenance-draft-v1-20261014'
LOCAL=HERE/'local/government-xl-hkust-two-original-context-v1-20261014'
ARRAY_SHA='4d6896acaabb53db6f20aa05f82087543656f82c2101c426cab11c14b87c808b'
sys.path.insert(0,str(HERE))
from run import read,save,reservations
c=read(PACKET/'input-contract.json')
t=read(PACKET/'ROOT-CACHED-ARRAYS-TERMINAL.json')
assert t['exitCode']==0 and t['leaseReleased'] and t['arrayReceiptSHA256']==ARRAY_SHA
assert hashlib.sha256((PACKET/'cached-complete-original-arrays-v1/array-receipt.json').read_bytes()).hexdigest()==ARRAY_SHA
for r in t['rows']:assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
log=Path('/tmp/hkust-lower-edge-root-tests-with-kernel-path-20261014.log').read_text()
assert 'Ran 8 tests' in log and '\nOK\n' in log
assert not LOCAL.exists() and not(PACKET/'two-original-scope-interface-output-v1').exists()
claim=reservations.claim('hkust-two-original-context-'+str(uuid.uuid4()),c['canonicalResources'],batch='government-xl-hkust-two-original-context-v1-20261014',ttl=3600)
assert claim['ok'],'Canonical HKUST two-original resources unavailable'
lease=claim['reservation'];leasefile=LOCAL/'reservation.json'
try:
    save(leasefile,json.loads(json.dumps(lease,default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(leasefile),'--ttl','3600','--',sys.executable,str(PACKET/'two-original-target-interface-draft-v1.py'),'--calculate-two-original-context-only','--array-receipt-sha256',ARRAY_SHA,'--lease-file',str(leasefile)],cwd=ROOT,check=True)
finally:
    if reservations.owns(lease):assert reservations.release(lease)['ok']
assert not reservations.owns(lease)
terminal=read(PACKET/'two-original-scope-interface-output-v1/terminal.json')
assert terminal['complete'] and terminal['allInputHashesUnchanged'] and not terminal['currentAcceptance']
save(PACKET/'ROOT-TWO-ORIGINAL-CONTEXT-TERMINAL.json',dict(exitCode=0,leaseReleased=True,exactObservedArrayReceiptSHA256=ARRAY_SHA,resultSHA256=terminal['resultSHA256'],sourceGeometryChanges=0,currentAcceptance=False))
print(json.dumps(read(PACKET/'ROOT-TWO-ORIGINAL-CONTEXT-TERMINAL.json')),flush=True)
