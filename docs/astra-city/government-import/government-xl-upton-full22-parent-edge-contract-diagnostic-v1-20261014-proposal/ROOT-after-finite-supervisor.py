from pathlib import Path
import sys,json,time,subprocess
sys.path.insert(0,'source-scripts/city/government-import')
from run import ROOT,HERE,read,save,digest,connect,reservations
import upton_full22_parent_edge_contract_diagnostic_v1_20261014 as edge
import upton_full22_saved_actual_union_delta_v1_20261014 as finite
import upton_full22_saved_area_pair_ancestor_v1_20261014 as area
assert digest(Path(edge.__file__).read_bytes())=='8e4b2ddfe38b4054df47e62da9f303eb597a72cf33014ccf82ef5030fc2904e3'
pins=read(edge.PROPOSAL/'draft-pins.json');prep=read(edge.PROPOSAL/'actual-readonly-preparation.json')
assert prep['passed'] and prep['literalValidatorSampleASTExactlyUnchanged']
for ref in pins['codeRefs']+pins['inputRefs']+prep['evidenceRefs']:edge.check(ref)
command=[sys.executable,'-m','unittest','-v',edge.TEST]
r=subprocess.run(command,cwd=HERE,capture_output=True,text=True)
assert r.returncode==0,(r.stdout,r.stderr)
log=edge.PROPOSAL/'ROOT-independent-tests.log';assert not log.exists();log.write_text(r.stdout+r.stderr)
schema=edge.schema_only();assert schema['passed']
save(edge.PROPOSAL/'ROOT-validation.json',dict(passed=True,independentTestCount=5,exactSamplerASTMatched=True,schema=schema,noDBLeaseOrProductionSampler=True))
print('Independent Upton edge preflight passed; waiting for existing finite and area workers.',flush=True)
while not all((module.DOC/'ROOT-VERIFIED.json').is_file()for module in [finite,area]):time.sleep(20)
for module in [finite,area]:
 result=read(module.DOC/'result.json');v=read(module.DOC/'ROOT-VERIFIED.json')
 assert v['jobId']==result['jobId'] and v['exactNeonReadback'] and v['allEvidenceHashesVerified'] and v['leaseReleased']
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for ref in result['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256'],ref['path']
 assert not reservations.owns(read(module.LEASE))
assert not edge.DOC.exists() and not edge.LOCAL.exists()
with Path('/tmp/upton-full22-parent-edge-contract-worker-20261014.log').open('xb') as f:
 r=subprocess.run([sys.executable,edge.__file__,'--check-saved860-parent-edge-contract-only'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
assert r.returncode==0
result=read(edge.DOC/'result.json')
with connect() as db:
 db.execute('SET TRANSACTION READ ONLY')
 assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
for ref in result['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256'],ref['path']
assert not reservations.owns(read(edge.LEASE))
proof=read(edge.DOC/'complete860-canonical-parent-edge-vertex-guard.json.gz')
save(edge.DOC/'ROOT-VERIFIED.json',dict(jobId=result['jobId'],exactNeonReadback=True,allEvidenceHashesVerified=True,evidenceRefCount=len(result['evidenceRefs']),leaseReleased=True,actualWorkerExitCode=0,canonicalParentEdgeAll860Passed=proof['allPassed'],canonicalMaximumGap=proof['maximumGap'],newlyInstalled=0,currentAcceptance=False))
print(json.dumps(dict(jobId=result['jobId'],canonicalParentAll860Passed=proof['allPassed'],maximumGap=proof['maximumGap'],newlyInstalled=0)),flush=True)
