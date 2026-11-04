from pathlib import Path
import sys,json,subprocess,uuid,importlib.util
ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
from run import read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import';P=BASE/'government-xl-heritage-starmart-original91-acquisition-contact-draft-v1-20261014';DOC=BASE/'government-xl-heritage-starmart-original91-acquisition-contact-v1-20261014';CALLER=P/'heritage-starmart-original91-acquisition-contact-draft-v1.py'
assert digest(CALLER.read_bytes())=='ffb27e11ab77c8f6ba3e5e2949a5a78f9a9c45bebb8d0b2802e7781e7894288f'
c=read(P/'input-contract.json');assert not DOC.exists() and not(P/'original-source-contact-output-v1').exists()
for path,h in c['filePins'].items():assert digest((ROOT/path).read_bytes())==h,path
prep=P/'ROOT-actual-preparation-v1';prep.mkdir()
for label,cmd in [('import',[sys.executable,'-c',"import runpy; runpy.run_path("+repr(str(CALLER))+",run_name='isolated_star_preflight_import')"]),('preflight',[sys.executable,str(CALLER),'--preflight-only']),('node-syntax',['node','--check',str(P/'heritage-starmart-original91-geometry-draft-v1.mjs')])]:
 r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);(prep/(label+'.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,(label,r.stdout[-2000:],r.stderr[-2000:])
save(prep/'ROOT-PREFLIGHT.json',dict(passed=True,actualImport=True,metadataPreflight=True,nodeSyntax=True,originalMemberCount=2,sourceFaces=91,noAcquisitionYet=True))
claim=reservations.claim('star-original91-'+str(uuid.uuid4()),c['canonicalResources'],batch=P.name,ttl=3600);assert claim['ok'];lease=claim['reservation'];lf=Path('/tmp/star-original91-lease-20261014.json');save(lf,json.loads(json.dumps(lease,default=str)))
command=[sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(lf),'--ttl','3600','--',sys.executable,str(CALLER),'--acquire-original-and-compare-only','--lease-file',str(lf)]
status=None
try:
 with Path('/tmp/star-original91-worker-20261014.log').open('xb')as log:r=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 status=r.returncode
finally:
 if reservations.owns(lease):assert reservations.release(lease)['ok']
 save(P/'ROOT-supervisor-terminal.json',dict(actualWorkerExitCode=status,leaseReleased=not reservations.owns(lease),newlyInstalled=0,currentAcceptance=False))
shutil_source=Path('/tmp/star-original91-worker-20261014.log');(P/'ROOT-actual-worker.log').write_bytes(shutil_source.read_bytes())
out=P/'original-source-contact-output-v1'
if status==0:
 result=read(out/'result.json');assert result['complete']and result['sourceOriginalFaces']==91 and result['MuseumFaces']==15140
 assert not result['identityAccepted']and not result['physicalAccepted']and result['newlyInstalled']==0
 assert result['diagnosticSHA256']==digest((out/'diagnostic.json.gz').read_bytes())
 summary=dict(uids=result['uids'],contactsByFourViews=result['contactsByFourViews'],identityAccepted=False,physicalAccepted=False,currentAcceptance=False,newlyInstalled=0,originalSourceFaces=91)
 stage='authenticated-two-original-source-finite-context-only'
else:
 summary=dict(uids=['landsd/165054:0','landsd/57455:0'],actualWorkerExitCode=status,sourceCorruptionInferred=False,identityAccepted=False,physicalAccepted=False,currentAcceptance=False,newlyInstalled=0)
 stage='preserved-original-acquisition-or-capture-contract-failure-only'
DOC.mkdir();save(DOC/'ROOT-REVIEW.json',summary)
paths=[p for p in P.rglob('*')if p.is_file()and '__pycache__'not in p.parts]+[ROOT/p for p in c['filePins']]
spec=importlib.util.spec_from_file_location('star_original_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
receipt=m.freeze(DOC.name,stage,paths,summary)
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
for ref in receipt['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256'],ref['path']
save(DOC/'ROOT-VERIFIED.json',dict(jobId=receipt['jobId'],exactNeonReadback=True,allEvidenceHashesVerified=True,evidenceRefCount=len(receipt['evidenceRefs']),actualWorkerExitCode=status,leaseReleased=True,newlyInstalled=0,currentAcceptance=False))
print(json.dumps(dict(jobId=receipt['jobId'],actualWorkerExitCode=status,summary=summary)),flush=True)
