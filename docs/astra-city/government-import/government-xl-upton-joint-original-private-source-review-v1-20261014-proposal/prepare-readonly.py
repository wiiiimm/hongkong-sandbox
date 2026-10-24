from pathlib import Path
import sys,ast,json,subprocess
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_joint_original_private_source_review_v1_20261014 as a
P=a.PROPOSAL;assert not a.DOC.exists()and not a.LOCAL.exists()and not(P/'draft-pins.json').exists();commands=[]
def run(cmd,name,cwd=ROOT):
    path=P/name;assert not path.exists();r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True);path.write_text(r.stdout+r.stderr);commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,path)
run([sys.executable,'-m','unittest','-v','test_upton_private_source_review_context_v1_20261014','test_exact_distinct_evidence_refs_v1_20261014'],'context-fixtures.log',a.HERE)
run(['node','--check',str(a.RUNTIME)],'runtime-syntax.log')
run(['node',str(a.RUNTIME),str((P/'literal-app-and-preview-closure.json').relative_to(ROOT)),'--closure-only'],'literal-closure.log')
closures=a.read(P/'literal-app-and-preview-closure.json');codes=[]
for c in closures:
    assert c['completeAuditedLiteralImportClosure']and c['unsupportedDynamicImports']==0
    codes +=[dict(path=path,sha256=h)for path,h in c['inputHashes'].items()]
folders=[a.HERE,a.HERE.parent/'shared-modelling',a.HERE.parent/'citywide-native',a.HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',a.HERE.parent/'assembly-support-review'];todo=[Path(a.__file__)];seen=set()
while todo:
    path=todo.pop().resolve()
    if path in seen:continue
    seen.add(path);codes.append(a.ref(path))
    for n in ast.walk(ast.parse(path.read_text())):
        mods=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[q.name for q in n.names]if isinstance(n,ast.Import)else[]
        for mod in mods:
            for folder in folders:
                q=folder/(mod.replace('.','/')+'.py')
                if q.is_file():todo.append(q)
codes +=[a.ref(Path(__file__)),a.ref(a.HERE/'test_upton_private_source_review_context_v1_20261014.py')]
inputs=[]
for folder in [a.attribution.DOC,a.physical.DOC,a.physical.metadata.capture.DOC]:
    result=a.read(folder/'result.json');v=a.read(folder/'ROOT-VERIFIED.json');assert result['jobId']==v['jobId']and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased'];inputs+=result['evidenceRefs']+[a.ref(folder/'result.json'),a.ref(folder/'ROOT-VERIFIED.json')]
pins=dict(caller=a.ref(Path(a.__file__)),codeRefs=a.distinct_refs(codes),inputRefs=a.distinct_refs(inputs),completedSourceAttributionJob=a.JOB,actualGroundSHA256=a.GROUND,sourceInterpretationOnly=True,strictInterfacePassed=False,physicalAccepted=False)
for q in pins['codeRefs']+pins['inputRefs']:a.check(q)
a.save(P/'draft-pins.json',pins);run([sys.executable,str(Path(a.__file__)),'--schema-only'],'schema-only.log');schema=json.loads((P/'schema-only.log').read_text());assert schema['passed']
refs=[a.ref(P/'METHOD.md'),a.ref(P/'draft-pins.json'),a.ref(P/'literal-app-and-preview-closure.json')]+[q['log']for q in commands]
for q in pins['codeRefs']+pins['inputRefs']+refs:a.check(q)
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),commands=commands,schemaVerbatim=schema,evidenceRefs=refs,noProductionArrayCalculationImagesRendererDBLeaseOrWorker=True));print(json.dumps(dict(passed=True,codePins=len(pins['codeRefs']),inputPins=len(pins['inputRefs']))))
