from pathlib import Path
import sys,ast,json,subprocess
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_joint_original_functional_private_stage_v1_20261014 as a
P=a.PROPOSAL;assert not a.DOC.exists()and not a.STAGE.exists()and not a.LOCAL.exists()and not(P/'draft-pins.json').exists();commands=[]
def run(cmd,name,cwd=ROOT):
    path=P/name;assert not path.exists();r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True);path.write_text(r.stdout+r.stderr);commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,path)
run([sys.executable,'-m','unittest','-v','test_upton_original_functional_applicability_adapter_v1_20261014','test_exact_distinct_evidence_refs_v1_20261014'],'adapter-setup-order-fixtures.log',a.HERE)
run(['node','--check',str(a.BROWSER)],'browser-syntax.log')
run(['node',str(a.HERE/'upton_functional_joint_browser_closure_v1_20261014.mjs'),str((P/'literal-browser-app-closure.json').relative_to(ROOT))],'literal-browser-closure.log')
closure=a.read(P/'literal-browser-app-closure.json');assert closure['computedImportsRejected']and len(closure['explicitExistingServerRoutes'])==1;codes=[dict(path=p,sha256=h)for p,h in closure['inputHashes'].items()]
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
codes +=[a.ref(Path(__file__)),a.ref(a.HERE/'upton_functional_joint_browser_closure_v1_20261014.mjs'),a.ref(a.HERE/'test_upton_original_functional_applicability_adapter_v1_20261014.py'),a.ref(a.HERE/'upton_preserve_replacement_slot_v1_20261014.py'),a.ref(a.HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs')]
inputs=[]
for folder in [a.functional.DOC,a.display.DOC,a.physical.DOC]:
    result=a.read(folder/'result.json');v=a.read(folder/'ROOT-VERIFIED.json');assert result['jobId']==v['jobId']and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased'];inputs+=result['evidenceRefs']+[a.ref(folder/'result.json'),a.ref(folder/'ROOT-VERIFIED.json')]
accepted=a.ref(a.functional.DOC/'ROOT-FUNCTIONAL-REVIEW.json');inputs +=[accepted,a.ref(a.display.DOC/'ROOT-IMAGE-INSPECTION.json')]
pins=dict(caller=a.ref(Path(a.__file__)),codeRefs=a.distinct_refs(codes),inputRefs=a.distinct_refs(inputs),completedFunctionalJob=a.FUNCTIONAL_JOB,completedDisplayV2Job='a63f3a97ae19de21251fcc5d1f0a383617b69cd968a67d23d9cb7e926420c749',acceptedROOTReview=accepted,strictInterfacePassed=False,publication=False)
for q in pins['codeRefs']+pins['inputRefs']:a.check(q)
a.save(P/'draft-pins.json',pins);run([sys.executable,str(Path(a.__file__)),'--schema-only'],'schema-only.log');schema=json.loads((P/'schema-only.log').read_text());assert schema['passed']
refs=[a.ref(P/'METHOD.md'),a.ref(P/'draft-pins.json'),a.ref(P/'literal-browser-app-closure.json')]+[q['log']for q in commands]
for q in pins['codeRefs']+pins['inputRefs']+refs:a.check(q)
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),commands=commands,schemaVerbatim=schema,evidenceRefs=refs,noGeometryStageCopyBrowserDBLeaseOrWorker=True));print(json.dumps(dict(passed=True,codePins=len(pins['codeRefs']),inputPins=len(pins['inputRefs']))))
