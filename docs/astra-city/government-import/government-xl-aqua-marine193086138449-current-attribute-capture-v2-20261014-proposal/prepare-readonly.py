from pathlib import Path
import sys,ast,subprocess,json
ROOT=Path(__file__).resolve().parents[4];HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
import aqua_marine193086138449_current_attribute_capture_v2_20261014 as a
P=a.PROPOSAL;assert not a.DOC.exists()and not a.LOCAL.exists()and not(P/'actual-readonly-preparation.json').exists();commands=[]
def command(cmd,name,cwd=ROOT):
    p=P/name;assert not p.exists();r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True);p.write_text(r.stdout+r.stderr);commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(p)));assert r.returncode==0,(cmd,p)
command([sys.executable,'-m','unittest','-v','test_aqua_two_source_runtime_delta_v2_20261014'],'three-exact-source-namespace-fixtures.log',HERE)
from aqua_two_source_runtime_delta_v2_20261014 import assert_exact_delta
assert_exact_delta((HERE/'aqua_marine193086138449_current_actual_attributes_v1_20261014.mjs').read_text(),a.RUNTIME.read_text())
a.save(P/'exact-runtime-namespace-scanner-delta.json',dict(passed=True,oldRuntime=a.ref(HERE/'aqua_marine193086138449_current_actual_attributes_v1_20261014.mjs'),newRuntime=a.ref(a.RUNTIME),onlyNamespaceAndReviewedScannerChanged=True,sourceCaptureArithmeticUnchanged=True))
command(['node','--check',str(a.RUNTIME)],'runtime-syntax-only.log')
closure=P/'literal-runtime-closure.json';command(['node',str(HERE/'aqua_two_source_attribute_literal_closure_v2_20261014.mjs'),str(closure.relative_to(ROOT))],'literal-runtime-closure.log')
command([sys.executable,str(Path(a.__file__)),'--schema-only'],'actual-saved-schema-only.log');schema=json.loads((P/'actual-saved-schema-only.log').read_text());assert schema['passed']
data,result,packet,foreign,form,inputs=a.load();codes=[];folders=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',HERE.parent/'assembly-support-review',ROOT/'docs/astra-city/mui-wo-buildings/review'];todo=[Path(a.__file__),a.A.prior.FREEZER,HERE/'aqua_two_source_runtime_delta_v2_20261014.py',HERE/'test_aqua_two_source_runtime_delta_v2_20261014.py'];seen=set()
while todo:
    path=todo.pop().resolve()
    if path in seen:continue
    seen.add(path);codes.append(a.ref(path))
    for n in ast.walk(ast.parse(path.read_text())):
        mods=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
        for mod in mods:
            for folder in folders:
                q=folder/(mod.replace('.','/')+'.py')
                if q.is_file():todo.append(q)
codes=a.distinct_refs(codes+[a.ref(Path(__file__)),a.ref(HERE/'aqua_two_source_attribute_literal_closure_v2_20261014.mjs')]);inputs=a.distinct_refs(inputs);codes=a.distinct_refs(codes+[dict(path=p,sha256=h)for p,h in a.read(closure)['inputHashes'].items()])
for q in codes+inputs:a.check(q)
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),codeRefs=codes,inputRefs=inputs,evidenceRefs=[a.ref(P/'METHOD.md'),a.ref(closure),a.ref(P/'exact-runtime-namespace-scanner-delta.json')]+[c['log']for c in commands],commands=commands,schemaVerbatim=schema,noSourceDecodeGeometryNumericalRenderDBLeaseWorker=True));print(json.dumps(dict(passed=True,codePins=len(codes),inputPins=len(inputs))))
