from pathlib import Path
import sys,json,hashlib,subprocess,uuid
ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city')
HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
from run import read,save,reservations
PACKET=ROOT/'docs/astra-city/government-import/government-xl-heritage165054-source-context-draft-v1-20261014'
CALLER=PACKET/'heritage-original-source-context-draft-v1.py'
assert hashlib.sha256(CALLER.read_bytes()).hexdigest()=='08e90fa02f8c1da1a34678233c0c65d473505ef0a40c4addbd9667d09686ade6'
contract=read(PACKET/'input-contract.json');assert not(PACKET/'source-context-output-v1').exists()
claim=reservations.claim('heritage-original-source-context-'+str(uuid.uuid4()),contract['canonicalResources'],batch=PACKET.name,ttl=3600);assert claim['ok'];lease=claim['reservation']
lease_file=Path('/tmp/heritage165054-source-context-lease-20261014.json');save(lease_file,json.loads(json.dumps(lease,default=str)))
result=None
try:
 command=[sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(lease_file),'--ttl','3600','--',sys.executable,str(CALLER),'--export-original-source-context-only','--lease-file',str(lease_file)]
 result=subprocess.run(command,cwd=ROOT)
finally:
 if reservations.owns(lease):assert reservations.release(lease)['ok']
 save(PACKET/'ROOT-supervisor-terminal.json',{'actualWorkerExitCode':result.returncode if result else None,'leaseReleased':not reservations.owns(lease),'newlyInstalled':0,'currentAcceptance':False})
assert result.returncode==0
output=PACKET/'source-context-output-v1';terminal=read(output/'terminal.json');receipt=read(output/'result.json')
assert terminal['complete']and terminal['allInputHashesUnchanged']and terminal['resultSHA256']==hashlib.sha256((output/'result.json').read_bytes()).hexdigest()
assert receipt['completeOriginalFaces']==15140 and receipt['farFaces']==462 and receipt['independentOverlapCounts']==[1106,2]
for ref in [receipt['completeArrayRef'],receipt['contextRef']]+receipt['actualExports']:assert hashlib.sha256((ROOT/ref['path']).read_bytes()).hexdigest()==ref['sha256']
print(json.dumps({'complete':True,'leaseReleased':True,'contextSHA256':receipt['contextRef']['sha256'],'newlyInstalled':0}),flush=True)
