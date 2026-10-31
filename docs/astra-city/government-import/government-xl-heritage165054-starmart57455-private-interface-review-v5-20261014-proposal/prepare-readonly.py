"""ROOT-only code/pin/schema preparation; no production imports or calculations."""
from pathlib import Path
import sys,ast,json,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
import heritage165054_starmart57455_private_interface_review_v5_20261014 as a
P=a.PROPOSAL;assert not a.DOC.exists()and not a.LOCAL.exists()and not(P/'draft-pins.json').exists();commands=[]
def run(cmd,name,cwd=ROOT):
    path=P/name;assert not path.exists();r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True);path.write_text(r.stdout+r.stderr);commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,path)
run([sys.executable,'-m','unittest','-v','test_heritage_saved_interface_schema_v1_20261014','test_heritage_saved_export_refs_v1_20261014','test_exact_distinct_evidence_refs_v1_20261014','test_timed_owned_lease_pulse_v1_20261014'],'saved-schema-and-supervisor-fixtures.log',HERE)
run(['node',str(HERE/'test_upton_private_indexed_source_framing_v1_20261014.mjs')],'unchanged-framing-fixtures.log')
run(['node',str(HERE/'test_heritage_source_pair_runtime_contract_v1_20261014.mjs')],'raw-source-api-and-saved-runtime-fixtures.log')
run(['node',str(HERE/'test_heritage_private_interface_catalogue_v1_20261014.mjs')],'actual-catalogue-schema-fixtures.log')
run(['node',str(HERE/'test_heritage_private_source_scheduler_v1_20261014.mjs')],'private-loader-scheduler-fixtures.log')
run(['node','--check',str(a.RUNTIME)],'runtime-syntax.log')
run(['node',str(a.RUNTIME),str((P/'literal-app-preview-closure.json').relative_to(ROOT)),'--closure-only'],'literal-closure.log')
codes=[a.ref(Path(__file__))];closures=a.read(P/'literal-app-preview-closure.json')
for c in closures:
    assert c['completeAuditedLiteralImportClosure']and c['unsupportedDynamicImports']==0 and c['computedImportsRejected']
    codes +=[dict(path=p,sha256=h)for p,h in c['inputHashes'].items()]
folders=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'citywide-source',HERE.parent/'landmark-acquisition',HERE.parent/'island-detail-integration',HERE.parent/'assembly-support-review',ROOT/'docs/astra-city/mui-wo-buildings/review']
todo=[Path(a.__file__),HERE/'run.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py',HERE.parent/'shared-modelling/reservations.py',HERE/'timed_owned_lease_pulse_v1_20261014.py',HERE/'test_heritage_saved_interface_schema_v1_20261014.py',HERE/'test_heritage_saved_export_refs_v1_20261014.py',HERE/'test_exact_distinct_evidence_refs_v1_20261014.py',HERE/'test_timed_owned_lease_pulse_v1_20261014.py'];seen=set()
while todo:
    p=todo.pop().resolve()
    if p in seen:continue
    seen.add(p);codes.append(a.ref(p))
    for n in ast.walk(ast.parse(p.read_text())):
        mods=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[q.name for q in n.names]if isinstance(n,ast.Import)else[]
        for mod in mods:
            for folder in folders:
                q=folder/(mod.replace('.','/')+'.py')
                if q.is_file():todo.append(q)
codes +=[a.ref(HERE/'test_heritage_source_pair_runtime_contract_v1_20261014.mjs'),a.ref(HERE/'test_heritage_private_interface_catalogue_v1_20261014.mjs'),a.ref(HERE/'test_heritage_private_source_scheduler_v1_20261014.mjs'),a.ref(HERE/'test_upton_private_indexed_source_framing_v1_20261014.mjs'),a.ref(HERE.parent/'shared-modelling/branch.json')]
data,inputs=a.source_inputs();pins=dict(caller=a.ref(Path(a.__file__)),codeRefs=a.distinct_refs(codes),inputRefs=a.distinct_refs(inputs),currentManifestSHA256=a.CURRENT,currentSnapshot=a.SNAPSHOT,sourceInterpretationOnly=True)
for q in pins['codeRefs']+pins['inputRefs']:a.check(q)
a.save(P/'draft-pins.json',pins);run([sys.executable,str(Path(a.__file__)),'--schema-only'],'schema-only.log');schema=json.loads((P/'schema-only.log').read_text());assert schema['passed']
refs=[a.ref(P/'METHOD.md'),a.ref(P/'draft-pins.json'),a.ref(P/'literal-app-preview-closure.json')]+[q['log']for q in commands]
for q in pins['codeRefs']+pins['inputRefs']+refs:a.check(q)
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),commands=commands,evidenceRefs=refs,schemaVerbatim=schema,noProductionArraysDecodeGeometryKernelRendererDBLeaseWorker=True));print(json.dumps(dict(passed=True,codePins=len(pins['codeRefs']),inputPins=len(pins['inputRefs']))))
