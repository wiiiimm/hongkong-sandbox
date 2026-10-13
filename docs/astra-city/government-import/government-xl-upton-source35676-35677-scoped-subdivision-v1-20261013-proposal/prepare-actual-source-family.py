from pathlib import Path
import sys,json,subprocess
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_saved_source35676_35677_scoped_subdivision_draft_v1_20261013 as a
P=Path(__file__).parent;pins=a.read(P/'draft-pins.json');refs=pins['codeRefs']+pins['inputRefs']+[a.ref(P/'draft-pins.json'),a.ref(Path(__file__))]
assert len(pins['codeRefs'])==46 and len(pins['inputRefs'])==110
for q in refs:a.check(q)
assert not a.DOC.exists()and not a.LOCAL.exists()
commands=[]
def run(cmd,name):
 path=P/name;assert not path.exists();r=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);path.write_bytes(r.stdout)
 commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,r.returncode,path)
run([sys.executable,'-m','unittest','discover','-s',str(a.HERE),'-p','test_upton_source_family_exact_subdivision_v1_20261013.py','-v'],'actual-nine-fixture-tests.log')
assert 'Ran 9 tests' in (P/'actual-nine-fixture-tests.log').read_text()and '\nOK\n' in (P/'actual-nine-fixture-tests.log').read_text()
a.save(P/'helper-validation.json',dict(passedTests=9,failedTests=0,exitCode=0,executedCodeRefs=[a.ref(a.HERE/'upton_source_family_exact_subdivision_v1_20261013.py'),a.ref(a.HERE/'test_upton_source_family_exact_subdivision_v1_20261013.py')],actualLog=a.ref(P/'actual-nine-fixture-tests.log'),noWorkerLeaseDBOrCandidate=True))
run([sys.executable,'-c',"import sys;sys.path.insert(0,'source-scripts/city/government-import');import upton_saved_source35676_35677_scoped_subdivision_draft_v1_20261013;print('isolated import PASS; no worker/lease/DB')"],'actual-isolated-import.log')
run([sys.executable,str(Path(a.__file__)),'--schema-only'],'actual-schema-only.log')
s=json.loads((P/'actual-schema-only.log').read_text());assert s['passed']and s['targetOldCandidate']==380 and s['oldCandidateFaces']==11575 and s['protectedWholeCurrentTriplets']==68 and s['sourceAncestorFamily']==[35676,35677]and s['savedAreaRows']==257
for q in refs:a.check(q)
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.prior.prior.prior.prior.CURRENT
assert not a.DOC.exists()and not a.LOCAL.exists()
summary=dict(passed=True,caller=a.ref(Path(a.__file__)),driver=a.ref(Path(__file__)),commands=commands,helperValidation=a.ref(P/'helper-validation.json'),all46Code110InputPinsVerifiedBeforeAndEnd=True,currentManifestSHA256=a.prior.prior.prior.prior.CURRENT,schemaVerbatim=s,noWorkerLeaseDBOrCandidate=True)
a.save(P/'actual-readonly-preparation.json',summary);print(json.dumps(summary,sort_keys=True))
