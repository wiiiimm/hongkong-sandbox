from pathlib import Path
import sys,subprocess,json,ast
ROOT=Path(__file__).resolve().parents[4];HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
import upton_joint_original_dimension_private_stage_v2_20261014 as a
P=a.PROPOSAL;assert not a.DOC.exists()and not a.STAGE.exists()and not a.LOCAL.exists()and not(P/'actual-readonly-preparation.json').exists();commands=[]
def command(cmd,name,cwd=ROOT):
    p=P/name;assert not p.exists();r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True);p.write_text(r.stdout+r.stderr);commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(p)));assert r.returncode==0,(cmd,p)
command([sys.executable,'-m','unittest','-v','test_upton_georef_dimensions_metadata_v1_20261014'],'seven-metadata-setup-fixtures.log',HERE)
command(['node','--check',str(a.BROWSER)],'browser-syntax.log')
command(['node',str(HERE/'upton_dimension_joint_browser_closure_v2_20261014.mjs'),str((P/'literal-browser-app-closure.json').relative_to(ROOT))],'literal-browser-closure.log')
closure=a.read(P/'literal-browser-app-closure.json');codes=[dict(path=p,sha256=h)for p,h in closure['inputHashes'].items()]
folders=[HERE,HERE.parent/'shared-modelling',HERE.parent/'model-review-ledger',HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',HERE.parent/'assembly-support-review'];todo=[Path(a.__file__),HERE/'upton_joint_original_dimension_staged_browser_v2_20261014.py',HERE/'upton_slot_preserving_guarded_publish_v2_20261014.py',HERE.parent/'island-detail-integration/publish.py'];seen=set()
while todo:
    path=todo.pop().resolve()
    if path in seen:continue
    seen.add(path);codes.append(a.ref(path))
    for n in ast.walk(ast.parse(path.read_text())):
        mods=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
        for mod in mods:
            for folder in folders:
                candidate=folder/(mod.replace('.','/')+'.py')
                if candidate.is_file():todo.append(candidate)
codes +=[a.ref(Path(__file__)),a.ref(HERE/'test_upton_georef_dimensions_metadata_v1_20261014.py'),a.ref(HERE/'upton_dimension_joint_browser_closure_v2_20261014.mjs')]
result=a.read(a.old.DOC/'result.json');inputs=result['evidenceRefs']+[a.ref(a.old.DOC/'result.json'),a.ref(a.old.DOC/'ROOT-VERIFIED.json'),a.ref(ROOT/'docs/astra-city/government-import/government-xl-upton-joint-original-functional-staged-browser-v1-20261014/command-000.json'),a.ref(ROOT/'docs/astra-city/government-import/government-xl-upton-joint-original-functional-staged-browser-v1-20261014/ROOT-TERMINAL.json')]
command([sys.executable,str(Path(a.__file__)),'--schema-only'],'actual-saved-schema-only.log');schema=json.loads((P/'actual-saved-schema-only.log').read_text());assert schema['passed']
codes=a.distinct_refs(codes);inputs=a.distinct_refs(inputs)
for q in codes+inputs:a.check(q)
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),codeRefs=codes,inputRefs=inputs,commands=commands,schemaVerbatim=schema,evidenceRefs=[a.ref(P/'METHOD.md'),a.ref(P/'literal-browser-app-closure.json')]+[c['log']for c in commands],noGeometryTransformBrowserDBLeaseWorker=True));print(json.dumps(dict(passed=True,codePins=len(codes),inputPins=len(inputs))))
