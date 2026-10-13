"""ROOT-only reviewed proposal: maintained tests lease, then fresh replay lease."""
from pathlib import Path
import sys,json,subprocess,uuid,re
PACKET=Path(__file__).resolve().parent;ROOT=PACKET.parents[3];HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
from run import read,save,reservations,digest
CALLER=PACKET/'heritage-current-typed-identity-caller-draft-v2.py';c=read(PACKET/'input-contract.json')
assert digest(CALLER.read_bytes())==c['callerSHA256']and read(PACKET/'ROOT-PREFLIGHT.json')['passed']
assert not(PACKET/'current-identity-output-v2').exists()
prep=PACKET/'ROOT-actual-preparation-v2';assert not prep.exists();prep.mkdir()
def fence():
 for p,h in c['filePins'].items():assert digest((ROOT/p).read_bytes())==h,p
 assert digest(CALLER.read_bytes())==c['callerSHA256']
def claim(stage):
 q=reservations.claim('heritage-identity-v2-'+stage+'-'+str(uuid.uuid4()),c['canonicalResources'],batch=PACKET.name,ttl=3600);assert q['ok'];lease=q['reservation']
 p=Path('/tmp')/('heritage-current-identity-v2-'+stage+'-'+str(uuid.uuid4())+'-lease.json');save(p,json.loads(json.dumps(lease,default=str)));return lease,p
runner=HERE.parent/'shared-modelling/reservations.py'
fence();testlease,testfile=claim('tests');testStatus=None
try:
 cmd=[sys.executable,str(runner),'run','--lease-file',str(testfile),'--ttl','3600','--',sys.executable,'-m','unittest','discover','-s',str(PACKET),'-p','test_heritage_current_typed_identity_draft_v2.py','-v']
 q=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);testStatus=q.returncode
 with (prep/'tests.log').open('x')as f:f.write(q.stdout+q.stderr)
finally:
 # run_reserved waits/reaps its subprocess/group before returning/releasing.
 if reservations.owns(testlease):assert reservations.release(testlease)['ok']
 save(prep/'test-supervisor-terminal.json',dict(exitCode=testStatus,leaseReleased=not reservations.owns(testlease),leaseFile=str(testfile)))
assert testStatus==0 and re.search(r'Ran 16 tests',q.stderr)and '\nOK\n'in q.stderr
assert not reservations.owns(testlease);fence()
validation=prep/'validation.json';save(validation,dict(allPassed=True,exitCode=0,testCount=16,testedCodePins=c['testedCodePins'],inputContractSHA256=digest((PACKET/'input-contract.json').read_bytes()),testLog=dict(path=str((prep/'tests.log').relative_to(ROOT)),sha256=digest((prep/'tests.log').read_bytes())),command=cmd))
# Do not repeat tests or assume the runner retained its old lease.
fence();replaylease,replayfile=claim('replay');replayStatus=None
try:
 command=[sys.executable,str(runner),'run','--lease-file',str(replayfile),'--ttl','3600','--',sys.executable,str(CALLER),'--replay-current-typed-identity-only','--test-validation',str(validation),'--test-validation-sha256',digest(validation.read_bytes()),'--lease-file',str(replayfile)]
 with (Path('/tmp')/('heritage-current-identity-v2-replay-'+str(uuid.uuid4())+'.log')).open('xb')as log:q=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 replayStatus=q.returncode
finally:
 if reservations.owns(replaylease):assert reservations.release(replaylease)['ok']
 save(prep/'replay-supervisor-terminal.json',dict(exitCode=replayStatus,leaseReleased=not reservations.owns(replaylease),leaseFile=str(replayfile)))
assert replayStatus==0;fence()
# ROOT reviews/finally freezes output separately; no historical job/review/event mutation.
print(json.dumps(dict(complete=True,tests=16,testLeaseReleased=True,replayLeaseReleased=not reservations.owns(replaylease),result=read(PACKET/'current-identity-output-v2/result.json'))),flush=True)
