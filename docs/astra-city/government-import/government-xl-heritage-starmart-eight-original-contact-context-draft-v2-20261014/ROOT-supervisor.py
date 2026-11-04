from pathlib import Path
import sys,json,subprocess,uuid,importlib.util
ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
from run import read,save,digest,reservations,connect
BASE=ROOT/'docs/astra-city/government-import';P=BASE/'government-xl-heritage-starmart-eight-original-contact-context-draft-v2-20261014';DOC=BASE/'government-xl-heritage-starmart-eight-original-contact-context-v2-20261014';CALLER=P/'heritage-starmart-eight-original-contact-context-draft-v2.py'
assert digest(CALLER.read_bytes())=='de57fdb411fa22d482d072ebd2c19618268c13e681a6da8e10c88d32e10fdb77'
c=read(P/'input-contract.json');assert not DOC.exists();prep=P/'ROOT-actual-preparation-v1';prep.mkdir()
for label,cmd in [('import',[sys.executable,'-c',"import runpy;runpy.run_path("+repr(str(CALLER))+",run_name='isolated_source_context_import')"]),('preflight',[sys.executable,str(CALLER),'--preflight-only'])]:
 r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);(prep/(label+'.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,(r.stdout[-2000:],r.stderr[-2000:])
for path,h in c['filePins'].items():assert digest((ROOT/path).read_bytes())==h,path
claim=reservations.claim('heritage-star-context-'+str(uuid.uuid4()),c['canonicalResources'],batch=P.name,ttl=3600);assert claim['ok'];lease=claim['reservation'];lf=Path('/tmp/heritage-star-8-source-context-v2-lease-20261014.json');save(lf,json.loads(json.dumps(lease,default=str)))
status=None
try:
 cmd=[sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(lf),'--ttl','3600','--',sys.executable,str(CALLER),'--export-saved-source-context-only','--lease-file',str(lf)]
 with Path('/tmp/heritage-star-8-source-context-v2-worker-20261014.log').open('xb')as log:r=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 status=r.returncode
finally:
 if reservations.owns(lease):assert reservations.release(lease)['ok']
 save(P/'ROOT-supervisor-terminal.json',dict(exitCode=status,leaseReleased=not reservations.owns(lease),newlyInstalled=0))
assert status==0
(P/'ROOT-actual-worker.log').write_bytes(Path('/tmp/heritage-star-8-source-context-v2-worker-20261014.log').read_bytes())
out=P/'source-coordinate-context-output-v2';result=read(out/'result.json');assert result['complete']and len(result['actualExports'])==3 and not result['physicalAccepted']
assert result['contextSHA256']==digest((out/'context.json.gz').read_bytes())
for ref in result['actualExports']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']and ref['width']==3000 and ref['height']==1800
DOC.mkdir();paths=[p for p in P.rglob('*')if p.is_file()and '__pycache__'not in p.parts]+[ROOT/p for p in c['filePins']]
s=importlib.util.spec_from_file_location('heritage_star_context_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
receipt=m.freeze(DOC.name,'saved-two-original-eight-contact-source-coordinate-context-only',paths,dict(uids=result['uids'],physicalAccepted=False,currentAcceptance=False,newlyInstalled=0,actualExports=result['actualExports']))
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
for ref in receipt['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256'],ref['path']
save(DOC/'ROOT-VERIFIED.json',dict(jobId=receipt['jobId'],exactNeonReadback=True,allEvidenceHashesVerified=True,evidenceRefCount=len(receipt['evidenceRefs']),leaseReleased=True,newlyInstalled=0,sourceRoleAccepted=False,physicalAccepted=False));print(json.dumps({'jobId':receipt['jobId'],'exports':result['actualExports'],'newlyInstalled':0}))
