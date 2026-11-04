from pathlib import Path
import sys,json,subprocess,uuid,hashlib,re,importlib.util
ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
from run import read,save,connect,reservations,digest
BASE=ROOT/'docs/astra-city/government-import';PACKET=BASE/'government-xl-heritage165054-current-typed-identity-draft-v1-20261014';DOC=BASE/'government-xl-heritage165054-current-typed-identity-receipt-v1-20261014';CALLER=PACKET/'heritage-current-typed-identity-caller-draft-v1.py'
assert digest(CALLER.read_bytes())=='898b639f77274deff164168eee2e7a139ee2e3bdc7a9ed236b8ccf5b8a0b4213'
c=read(PACKET/'input-contract.json');assert read(PACKET/'ROOT-PREFLIGHT.json')['passed'] and not DOC.exists() and not(PACKET/'current-identity-output-v1').exists()
claim=reservations.claim('heritage-current-typed-identity-'+str(uuid.uuid4()),c['canonicalResources'],batch=PACKET.name,ttl=3600);assert claim['ok'];lease=claim['reservation'];leasefile=Path('/tmp/heritage-current-typed-identity-lease-20261014.json');save(leasefile,json.loads(json.dumps(lease,default=str)))
status=None
try:
 prep=PACKET/'ROOT-actual-preparation-v1';assert not prep.exists();prep.mkdir()
 # Actual/adverse current geometry fixtures run under the same maintained lease.
 cmd=[sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(leasefile),'--ttl','3600','--',sys.executable,'-m','unittest','discover','-s',str(PACKET),'-p','test_heritage_current_typed_identity_draft_v1.py','-v']
 r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);(prep/'tests.log').write_text(r.stdout+r.stderr);assert r.returncode==0 and re.search(r'Ran 16 tests',r.stderr) and '\nOK\n' in r.stderr,(r.stdout[-2000:],r.stderr[-2000:])
 assert reservations.owns(lease);assert reservations.heartbeat(lease,ttl=3600)['ok']
 for path,h in c['filePins'].items():assert digest((ROOT/path).read_bytes())==h,path
 v=dict(allPassed=True,exitCode=0,testCount=16,testedCodePins=c['testedCodePins'],inputContractSHA256=digest((PACKET/'input-contract.json').read_bytes()),testLog=dict(path=str((prep/'tests.log').relative_to(ROOT)),sha256=digest((prep/'tests.log').read_bytes())),command=cmd)
 validation=prep/'validation.json';save(validation,v)
 command=[sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(leasefile),'--ttl','3600','--',sys.executable,str(CALLER),'--replay-current-typed-identity-only','--test-validation',str(validation),'--test-validation-sha256',digest(validation.read_bytes()),'--lease-file',str(leasefile)]
 with Path('/tmp/heritage-current-typed-identity-worker-20261014.log').open('xb')as log:r=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 status=r.returncode
finally:
 if reservations.owns(lease):assert reservations.release(lease)['ok']
 save(PACKET/'ROOT-supervisor-terminal.json',dict(actualWorkerExitCode=status,leaseReleased=not reservations.owns(lease),newlyInstalled=0,currentAcceptance=False))
assert status==0
out=PACKET/'current-identity-output-v1';result=read(out/'result.json');assert result['complete'] and result['completeOriginalFaces']==15140 and not result['physicalAccepted']
assert result['identitySHA256']==digest((out/'typed-current-identity.json').read_bytes())
DOC.mkdir();save(DOC/'ROOT-REVIEW.json',dict(identityAccepted=result['identityAccepted'],rawReasonsRetained=result['rawReasonsRetained'],remainingIdentityReasons=result['remainingIdentityReasons'],sourceGeometryChanges=0,currentAcceptance=False,physicalAccepted=False,nextStep='Resolve the original-Star-source conflict and all current terrain, support, native/baseline physical, runtime/browser and publisher gates. No blanket canopy-role or collision exemption.'))
paths=[p for p in PACKET.rglob('*')if p.is_file()and '__pycache__'not in p.parts]+[ROOT/p for p in c['filePins']]
spec=importlib.util.spec_from_file_location('heritage_current_identity_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');freezer=importlib.util.module_from_spec(spec);spec.loader.exec_module(freezer)
receipt=freezer.freeze(DOC.name,'heritage-current-source-bound-identity-only-with-full-physical-gates-retained',paths,dict(uids=['landsd/165054:0'],identityAccepted=result['identityAccepted'],physicalAccepted=False,currentAcceptance=False,remainingIdentityReasons=result['remainingIdentityReasons'],currentHeldReason='Original-Star conflict plus full current placement/support/runtime checks unfinished',newlyInstalled=0))
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
for ref in receipt['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256'],ref['path']
save(DOC/'ROOT-VERIFIED.json',dict(jobId=receipt['jobId'],exactNeonReadback=True,allEvidenceHashesVerified=True,evidenceRefCount=len(receipt['evidenceRefs']),leaseReleased=True,identityAccepted=result['identityAccepted'],physicalAccepted=False,newlyInstalled=0))
print(json.dumps(dict(jobId=receipt['jobId'],identityAccepted=result['identityAccepted'],remainingReasons=result['remainingIdentityReasons'],newlyInstalled=0)),flush=True)
