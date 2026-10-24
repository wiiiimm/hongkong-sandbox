"""ROOT serial handoff: completed finite receipt before the separately reviewed pair diagnostic."""
from pathlib import Path
import sys,time,json,subprocess
ROOT=Path(__file__).resolve().parents[4]
HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
from run import read,save,connect,reservations,digest
BATCH='government-xl-upton-current-ring12-saved-actual-union-delta-v1-20261013'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LEASE=HERE/'local'/BATCH/'reservation.json'
NEXT=HERE/'upton_current_ring12_changed_area_pair_ancestor_draft_v1_20261013.py'
EXPECTED='03ca799d25327ed9be73f73c4366c0daf0ace000ea6a5f3a2e6d624171170f16'
DEADLINE=time.monotonic()+3700
while not (DOC/'result.json').exists():
    assert time.monotonic()<DEADLINE,'Finite receipt did not arrive; no pair diagnostic started.'
    assert LEASE.exists() and reservations.owns(read(LEASE)),'Finite lease ended without a receipt; no pair diagnostic started.'
    time.sleep(15)
while reservations.owns(read(LEASE)):
    assert time.monotonic()<DEADLINE,'Finite lease still active; no pair diagnostic started.'
    time.sleep(5)
r=read(DOC/'result.json')
with connect() as c:
    c.execute('SET TRANSACTION READ ONLY')
    assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
for q in r['evidenceRefs']:
    assert digest((ROOT/q['path']).read_bytes())==q['sha256'],q['path']
assert not r['installationApproved'] and r['newlyInstalled']==0
assert digest(NEXT.read_bytes())==EXPECTED
proof=dict(jobId=r['jobId'],exactNeonReadback=True,allEvidenceHashesVerified=True,evidenceRefs=len(r['evidenceRefs']),leaseReleased=True,sourceOnly=True,installationCredit=False)
save(DOC/'ROOT-SERIAL-VERIFIED.json',proof)
print(json.dumps(proof),flush=True)
subprocess.run([sys.executable,str(NEXT),'--classify-saved-current-ring12-five-area-pairs-only'],cwd=ROOT,check=True)
