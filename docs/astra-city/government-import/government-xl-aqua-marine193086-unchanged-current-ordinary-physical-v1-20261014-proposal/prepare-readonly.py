from pathlib import Path
import sys,json,subprocess,ast
ROOT=Path(__file__).resolve().parents[4];HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
import aqua_marine193086_current_ordinary_physical_v1_20261014 as a
P=a.PROPOSAL;assert not a.DOC.exists()and not a.LOCAL.exists()and not(P/'actual-readonly-preparation.json').exists();commands=[]
def command(cmd,name,cwd=ROOT):
    p=P/name;assert not p.exists();r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True);p.write_text(r.stdout+r.stderr);commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(p)));assert r.returncode==0,(cmd,p)
command([sys.executable,'-m','unittest','-v','test_aqua_marine193086_current_identity_reuse_v1_20261014'],'six-source-setup-fixtures.log',HERE)
command(['node',str(HERE/'aqua_marine193086_ordinary_runtime_closure_v1_20261014.mjs'),str((P/'literal-runtime-closure.json').relative_to(ROOT))],'literal-runtime-closure.log')
command([sys.executable,str(Path(a.__file__)),'--schema-only'],'actual-schema-only.log');schema=json.loads((P/'actual-schema-only.log').read_text());assert schema['passed']
row,context,capture,saved,source,pins,receipts,inputs,historical,native,retain,scope=a.load();closure=a.read(P/'literal-runtime-closure.json');codes=[dict(path=p,sha256=h)for p,h in closure['inputHashes'].items()];folders=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',HERE.parent/'assembly-support-review',ROOT/'docs/astra-city/mui-wo-buildings/review'];todo=[Path(a.__file__),HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',HERE/'acceptance-policy.py',a.FREEZER];seen=set()
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
codes +=[a.ref(Path(__file__)),a.ref(HERE/'test_aqua_marine193086_current_identity_reuse_v1_20261014.py'),a.ref(HERE/'aqua_marine193086_ordinary_runtime_closure_v1_20261014.mjs')];codes=a.distinct_refs(codes)
for q in codes+inputs:a.check(q)
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),codeRefs=codes,inputRefs=inputs,evidenceRefs=[a.ref(P/'METHOD.md'),a.ref(P/'literal-runtime-closure.json')]+[r['log']for r in commands],commands=commands,schemaVerbatim=schema,currentManifestSHA256=a.CURRENT,currentSnapshot=a.SNAPSHOT,historicalOldManifestRefs=historical,canonicalUIDScope=scope,noSourceDecodeGeometryNumericalDBLeaseWorker=True));print(json.dumps(dict(passed=True,codePins=len(codes),inputPins=len(inputs),canonicalUIDs=len(scope))))
