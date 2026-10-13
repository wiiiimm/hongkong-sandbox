from pathlib import Path
import sys,json,subprocess,ast
sys.path.insert(0,'source-scripts/city/government-import')
from run import ROOT,HERE,read,save,digest,connect,reservations
import upton_full22_saved_actual_union_delta_v1_20261014 as finite
import upton_full22_saved_area_pair_ancestor_v1_20261014 as area

def find_assess(p):
 return next(n for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,ast.FunctionDef) and n.name=='assess')
assert ast.dump(find_assess(Path(finite.__file__)),include_attributes=False)==ast.dump(find_assess(Path(finite.previous_delta.__file__)),include_attributes=False)
assert digest(Path(finite.__file__).read_bytes())=='7f6e739f5d926e1b93ba4ce3dcb40713fef0b1a0ae4f492f76b8141c10b73b82'
assert digest(Path(area.__file__).read_bytes())=='66ac3fbf6e22c82590dab4a90dcdaaab70357be517fce0766aaba864c7de95d1'
for module in [finite,area]:
 prep=read(module.PROPOSAL/'actual-readonly-preparation.json');pins=read(module.PROPOSAL/'draft-pins.json')
 assert prep['passed'] and prep['caller']==module.ref(Path(module.__file__))
 for ref in prep['evidenceRefs']+pins['codeRefs']+pins['inputRefs']:module.check(ref)
 command=[sys.executable,module.__file__,'--schema-only']
 r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
 assert r.returncode==0,(module.BATCH,r.stdout,r.stderr)
 schema=json.loads(r.stdout)
 assert schema['passed']
 save(module.PROPOSAL/'ROOT-schema-validation.json',dict(command=command,schema=schema,independentRootBindingCheck=True,unchangedFullFiniteAssessAST=True,noWorkerDBLease=True))
for module,flag in [(finite,'--check-saved-full22-actual-union-delta-only'),(area,'--classify-saved-full22-area-pairs-only')]:
 assert not module.DOC.exists() and not module.LOCAL.exists()
 log=Path('/tmp')/(module.BATCH+'-ROOT-worker.log')
 with log.open('xb') as f:
  result=subprocess.run([sys.executable,module.__file__,flag],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
 assert result.returncode==0,(module.BATCH,result.returncode,str(log))
 receipt=read(module.DOC/'result.json')
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for ref in receipt['evidenceRefs']:
  assert digest((ROOT/ref['path']).read_bytes())==ref['sha256'],ref['path']
 assert not reservations.owns(read(module.LEASE))
 save(module.DOC/'ROOT-VERIFIED.json',dict(jobId=receipt['jobId'],exactNeonReadback=True,allEvidenceHashesVerified=True,evidenceRefCount=len(receipt['evidenceRefs']),leaseReleased=True,actualWorkerExitCode=0,newlyInstalled=0,currentAcceptance=False))
 print(json.dumps(dict(batch=module.BATCH,jobId=receipt['jobId'],verified=True,newlyInstalled=0)),flush=True)
