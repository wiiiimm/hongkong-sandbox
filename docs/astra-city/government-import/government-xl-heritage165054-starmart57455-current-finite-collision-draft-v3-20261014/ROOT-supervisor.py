from pathlib import Path
import sys,json,hashlib,subprocess,uuid,importlib.util
ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city')
HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
from run import read,save,reservations,connect,digest
BASE=ROOT/'docs/astra-city/government-import'
PACKET=BASE/'government-xl-heritage165054-starmart57455-current-finite-collision-draft-v3-20261014'
DOC=BASE/'government-xl-heritage165054-starmart57455-current-finite-collision-receipt-v3-20261014'
CALLER=PACKET/'heritage-starmart-current-finite-draft-v3.py'
assert digest(CALLER.read_bytes())=='4ea2a2cecfbf692a93f6a799de9beeb362a391486719b6fc73420b2e11d58406'
validation=PACKET/'ROOT-actual-preparation-v1/validation-v2.json'
contract=read(PACKET/'input-contract.json');assert read(PACKET/'ROOT-PREFLIGHT.json')['passed']
assert not DOC.exists() and not(PACKET/'collision-output-v3').exists()
claim=reservations.claim('heritage-starmart-current-collision-'+str(uuid.uuid4()),contract['canonicalResources'],batch=PACKET.name,ttl=3600);assert claim['ok'];lease=claim['reservation']
lease_file=Path('/tmp/heritage165054-starmart-collision-lease-v3-20261014.json');save(lease_file,json.loads(json.dumps(lease,default=str)))
result=None
try:
 command=[sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(lease_file),'--ttl','3600','--',sys.executable,str(CALLER),'--calculate-current-full-collision-only','--lease-file',str(lease_file),'--test-validation',str(validation),'--test-validation-sha256',digest(validation.read_bytes())]
 with Path('/tmp/heritage165054-starmart-collision-worker-v3-20261014.log').open('xb') as log:result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
finally:
 if reservations.owns(lease):assert reservations.release(lease)['ok']
 save(PACKET/'ROOT-supervisor-terminal.json',dict(actualWorkerExitCode=result.returncode if result else None,leaseReleased=not reservations.owns(lease),newlyInstalled=0,currentAcceptance=False))
assert result.returncode==0
out=PACKET/'collision-output-v3';completed=read(out/'result.json');diagnostic=read(out/'diagnostic.json.gz')
assert completed['complete'] and completed['sourceFaces']==15140 and len(completed['contactCounts'])==4
assert completed['diagnosticSHA256']==digest((out/'diagnostic.json.gz').read_bytes())
assert len(diagnostic['fourViews'])==4 and diagnostic['noChosenFaceShortcut'] and not diagnostic['physicalAccepted']
for path,h in contract['filePins'].items():assert digest((ROOT/path).read_bytes())==h,path
DOC.mkdir();save(DOC/'ROOT-REVIEW.json',dict(completeOriginalSourceFaces=15140,completeBASICFaces=completed['BASICFaces'],contactsByFourViews=completed['contactCounts'],noChosenFaceShortcut=True,sourceGeometryChanges=0,wholePhysicalAcceptance=False,containmentOrVolumetricClearanceCertified=False,nextStep='Review complete contact classifications, independently verify identity, then finish full current placement, support, runtime/browser and guarded publication.'))
paths=[p for p in PACKET.rglob('*') if p.is_file() and '__pycache__' not in p.parts]+[ROOT/p for p in contract['filePins']]
spec=importlib.util.spec_from_file_location('heritage_collision_source_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
receipt=module.freeze(DOC.name,'heritage-whole-original-starmart-full-finite-collision-only',paths,dict(uids=['landsd/165054:0'],sourceSHA256=contract['sourceSHA256'],sourceOnly=True,completeOriginalSourceFaces=15140,completeBASICFaces=completed['BASICFaces'],contactsByFourViews=completed['contactCounts'],currentHeldReason='whole identity/current placement/support and remaining physical/runtime checks unfinished',physicalAccepted=False,identityAccepted=False,newlyInstalled=0))
with connect() as db:
 db.execute('SET TRANSACTION READ ONLY')
 assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
for ref in receipt['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256'],ref['path']
save(DOC/'ROOT-VERIFIED.json',dict(jobId=receipt['jobId'],exactNeonReadback=True,allEvidenceHashesVerified=True,evidenceRefCount=len(receipt['evidenceRefs']),leaseReleased=True,actualWorkerExitCode=0,contactsByFourViews=completed['contactCounts'],newlyInstalled=0,currentAcceptance=False))
print(json.dumps(dict(jobId=receipt['jobId'],complete=True,contactsByFourViews=completed['contactCounts'],neonVerified=True,newlyInstalled=0)),flush=True)
