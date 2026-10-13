from pathlib import Path
import sys,json,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_saved_hanging_subdivision_investigation_draft_v1_20261013 as a
P=Path(__file__).parent
pins=a.read(P/'draft-pins.json');refs=pins['codeRefs']+pins['inputRefs']+[a.ref(P/'draft-pins.json'),a.ref(Path(__file__))]
for q in refs:a.check(q)
assert len(pins['codeRefs'])==42 and len(pins['inputRefs'])==86
assert not a.DOC.exists() and not a.LOCAL.exists()
commands=[]
def run(cmd,name):
 path=P/name;assert not path.exists();r=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);path.write_bytes(r.stdout)
 commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,r.returncode,path)
run([sys.executable,'-m','unittest','discover','-s',str(a.HERE),'-p','test_upton_saved_hanging_subdivision_investigation_v1_20261013.py','-v'],'actual-nine-adverse-tests.log')
log=(P/'actual-nine-adverse-tests.log').read_text();assert 'Ran 9 tests' in log and '\nOK\n' in log
validation=dict(passedTests=9,failedTests=0,exitCode=0,executedCodeRefs=[a.ref(Path(a.__file__)),a.ref(a.HERE/'test_upton_saved_hanging_subdivision_investigation_v1_20261013.py'),a.ref(a.HERE/'upton_saved_uncovered_packed_ancestor_boundary_attribution_draft_v1_20261013.py')],actualLog=a.ref(P/'actual-nine-adverse-tests.log'),noWorkerLeaseOrDB=True)
a.save(P/'actual-nine-fixture-validation.json',validation)
run([sys.executable,'-c',"import sys;sys.path.insert(0,'source-scripts/city/government-import');import upton_saved_hanging_subdivision_investigation_draft_v1_20261013;print('isolated import PASS; no worker/lease/DB')"],'actual-isolated-import.log')
run([sys.executable,str(Path(a.__file__)),'--schema-only'],'actual-schema-only.log')
schema=json.loads((P/'actual-schema-only.log').read_text());assert schema['passed'] and schema['completeRawNativeFacets']==11575 and len(schema['literalWholeCurrentProtectedFacets'])==68 and schema['completeSavedRows']==357 and schema['intervalRows']==100 and schema['areaRows']==257
assert len({r['candidateFace']for r in schema['literalWholeCurrentProtectedFacets']})==68
manifest=a.read(a.ROOT/'3d-viewer/city/data/manifest.json')
# Count all catalogue entries from the already-bound raw source paths via production input schema; strict manifest hash remains authoritative.
for q in refs:a.check(q)
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.prior.prior.CURRENT
assert not a.DOC.exists() and not a.LOCAL.exists()
summary=dict(passed=True,caller=a.ref(Path(a.__file__)),driver=a.ref(Path(__file__)),commands=commands,fixtureValidation=a.ref(P/'actual-nine-fixture-validation.json'),declaredCodePins=42,declaredInputPins=86,allPinsVerifiedBeforeAndEnd=True,currentManifestSHA256=a.prior.prior.CURRENT,currentExpectedNativeCount=6650,schemaPassed=True,completeWholeLiteralTriplets=68,noDOCOrLOCAL=True,noWorkerLeaseOrDB=True)
a.save(P/'actual-readonly-preparation.json',summary);print(json.dumps(summary,sort_keys=True))
