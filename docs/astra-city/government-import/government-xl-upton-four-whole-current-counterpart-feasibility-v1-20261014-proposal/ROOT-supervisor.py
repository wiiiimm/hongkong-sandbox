from pathlib import Path
import sys,json,subprocess,re
sys.path.insert(0,'source-scripts/city/government-import')
from run import ROOT,HERE,read,save,digest,connect,reservations
import upton_four_whole_current_counterpart_feasibility_v1_20261014 as a
assert digest(Path(a.__file__).read_bytes())=='6aeac017819de5ad8758c92c8ac02bd32f65e23d7cbd935a7480439d65b2fc37'
pins=read(a.PROPOSAL/'draft-pins.json');prep=read(a.PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']
for ref in pins['codeRefs']+pins['inputRefs']+prep['evidenceRefs']:a.check(ref)
cmd=[sys.executable,'-m','unittest','-v',*a.TESTS];r=subprocess.run(cmd,cwd=HERE,capture_output=True,text=True);log=a.PROPOSAL/'ROOT-independent-tests.log';assert not log.exists();log.write_text(r.stdout+r.stderr)
assert r.returncode==0 and re.search(r'Ran 22 tests',r.stderr) and r.stderr.rstrip().endswith('OK')
schema=a.schema_only();assert schema['passed'];save(a.PROPOSAL/'ROOT-validation.json',dict(passed=True,independentTests=22,schema=schema,noDBLeaseOrSourceCalculation=True))
assert not a.DOC.exists() and not a.LOCAL.exists()
with Path('/tmp/upton-four-whole-current-worker-20261014.log').open('xb') as f:r=subprocess.run([sys.executable,a.__file__,'--test-four-whole-current-counterparts-only'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
assert r.returncode==0
receipt=read(a.DOC/'result.json')
with connect() as db:
 db.execute('SET TRANSACTION READ ONLY')
 assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
for ref in receipt['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256'],ref['path']
assert not reservations.owns(read(a.LEASE))
proof=read(a.DOC/'complete-four-whole-current-compatibility-and-packed-target-coverage.json.gz')
save(a.DOC/'ROOT-VERIFIED.json',dict(jobId=receipt['jobId'],exactNeonReadback=True,allEvidenceHashesVerified=True,evidenceRefCount=len(receipt['evidenceRefs']),actualWorkerExitCode=0,leaseReleased=True,wholeCurrentOrdinaryCompatibleWithoutUncredited=proof['wholeCurrentOrdinaryCompatibleWithoutUncredited'],allTwelvePackedTargetCoverageAndOrdinaryPassed=proof['allTwelvePackedTargetCoverageAndOrdinaryPassed'],privateNominationExists=(a.DOC/'private-four-whole-current-counterpart-nomination.json.gz').exists(),newlyInstalled=0,currentAcceptance=False))
print(json.dumps(read(a.DOC/'ROOT-VERIFIED.json')),flush=True)
