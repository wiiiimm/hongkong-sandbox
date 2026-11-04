from pathlib import Path
import hashlib,json,os,subprocess,sys,time

ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city')
HERE=ROOT/'source-scripts/city/government-import'
BASE=ROOT/'docs/astra-city/government-import'
FINITE='government-xl-upton-three-own-layer-saved-actual-union-delta-v1-20261013'
PAIRS='government-xl-upton-three-own-layer-changed-area-pair-ancestor-v1-20261013'
SCRIPT=HERE/'upton_three_own_layer_changed_area_pair_ancestor_draft_v1_20261013.py'
EXPECTED='43c096e39b78c5c338688c7da69f55d6d604a9c1f38a0b4403183adb610477c0'
sys.path.insert(0,str(HERE))
from run import read,save,connect,reservations

def live_finite():
    needle=b'upton_three_own_layer_saved_actual_union_delta_draft_v1_20261013.py'
    for p in Path('/proc').iterdir():
        if not p.name.isdigit() or int(p.name)==os.getpid():continue
        try:
            args=(p/'cmdline').read_bytes().split(b'\0')
            if any(a.endswith(needle) for a in args):return True
        except (FileNotFoundError,PermissionError,ProcessLookupError):pass
    return False

missing=0
while not (BASE/FINITE/'result.json').exists():
    missing=0 if live_finite() else missing+1
    if missing>=3:raise RuntimeError('Finite worker absent without completed receipt; dependent work not started')
    time.sleep(10)
while live_finite():time.sleep(5)
receipt=read(BASE/FINITE/'result.json')
lease=read(HERE/'local'/FINITE/'reservation.json')
assert not reservations.owns(lease)
with connect() as db:
    db.execute('SET TRANSACTION READ ONLY')
    assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
for pin in receipt['evidenceRefs']:
    assert hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256'],pin['path']
save(BASE/FINITE/'ROOT-SERIAL-VERIFIED.json',dict(jobId=receipt['jobId'],exactNeonReadback=True,allEvidenceRefsVerified=len(receipt['evidenceRefs']),leaseReleased=True,actualWorkerAbsent=True,dependentScope=PAIRS,sourceOnly=True,newlyInstalled=0))
print(json.dumps(dict(finiteCompletedAndVerified=receipt['jobId'],refs=len(receipt['evidenceRefs']),next=PAIRS)),flush=True)
assert hashlib.sha256(SCRIPT.read_bytes()).hexdigest()==EXPECTED
proposal=BASE/(PAIRS+'-proposal')
assert read(proposal/'ROOT-REVIEW.json')['rootReviewed']
assert not (BASE/PAIRS).exists() and not (HERE/'local'/PAIRS).exists()
subprocess.run([sys.executable,str(SCRIPT),'--classify-saved-three-own-layer-sixteen-area-pairs-only'],cwd=ROOT,check=True)
receipt=read(BASE/PAIRS/'result.json')
with connect() as db:
    db.execute('SET TRANSACTION READ ONLY')
    assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
for pin in receipt['evidenceRefs']:
    assert hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256'],pin['path']
assert not reservations.owns(read(HERE/'local'/PAIRS/'reservation.json'))
save(BASE/PAIRS/'ROOT-SERIAL-VERIFIED.json',dict(jobId=receipt['jobId'],exactNeonReadback=True,allEvidenceRefsVerified=len(receipt['evidenceRefs']),leaseReleased=True,sourceOnly=True,newlyInstalled=0))
print(json.dumps(dict(pairsCompletedAndVerified=receipt['jobId'],refs=len(receipt['evidenceRefs']))),flush=True)
