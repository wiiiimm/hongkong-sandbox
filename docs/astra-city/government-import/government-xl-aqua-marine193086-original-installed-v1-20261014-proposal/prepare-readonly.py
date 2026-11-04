from pathlib import Path
import sys,ast,subprocess,json
ROOT=Path(__file__).resolve().parents[4];HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
import aqua_marine193086_original_live_install_v1_20261014 as a
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--stage-job',required=True);parser.add_argument('--staged-job',required=True);parser.add_argument('--previous-count',required=True);parser.add_argument('--expected-main-snapshot',required=True);parser.add_argument('--staged-review',required=True);args=parser.parse_args()
cli=['--stage-job',args.stage_job,'--staged-job',args.staged_job,'--previous-count',args.previous_count,'--expected-main-snapshot',args.expected_main_snapshot,'--staged-review',args.staged_review]
P=a.PROPOSAL;assert not a.DOC.exists()and not a.LOCAL.exists()and not(P/'actual-readonly-preparation.json').exists();commands=[]
def command(cmd,name,cwd=ROOT):
    p=P/name;assert not p.exists();r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True);p.write_text(r.stdout+r.stderr);commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(p)));assert r.returncode==0,(cmd,p)
command([sys.executable,'-m','unittest','-v','test_aqua_original_image_review_binding_v1_20261014'],'five-image-review-and-fixed521-fixtures.log',HERE)
command(['node','--check',str(a.stage.BROWSER)],'browser-syntax-only.log')
closure=P/'literal-runtime-closure.json';command(['node',str(HERE/'aqua_original_live_literal_closure_v1_20261014.mjs'),str(closure.relative_to(ROOT))],'literal-runtime-closure.log')
command([sys.executable,str(Path(a.__file__)),'--schema-only',*cli],'actual-saved-schema-only.log');schema=json.loads((P/'actual-saved-schema-only.log').read_text());assert schema['passed']
data,stage_result,staged_result,adapted,accepted,decision,previous,pointer,models,delta,inputs=a.load(args);codes=[];folders=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',HERE.parent/'assembly-support-review',HERE.parent/'model-review-ledger',HERE.parent/'building-progress',HERE.parent/'landmark-completion-audit',ROOT/'docs/astra-city/mui-wo-buildings/review'];todo=[Path(a.__file__),a.A.prior.FREEZER,a.stage.PUB,HERE.parent/'island-detail-integration/publish.py',HERE/'test_aqua_original_image_review_binding_v1_20261014.py',HERE/'integrate.py',HERE/'publication_lock.py',HERE/'xl-current-installed-count-audit.py',HERE.parent/'building-progress/export.py',HERE.parent/'model-review-ledger/ledger.py'];seen=set()
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
codes=a.distinct_refs(codes+[a.ref(Path(__file__)),a.ref(HERE/'aqua_original_live_literal_closure_v1_20261014.mjs')]);inputs=a.distinct_refs(inputs);codes=a.distinct_refs(codes+[dict(path=p,sha256=h)for p,h in a.read(closure)['inputHashes'].items()])
for q in codes+inputs:a.check(q)
a.save(P/'actual-readonly-preparation.json',dict(passed=True,stageJob=args.stage_job,stagedJob=args.staged_job,stagedImageReview=a.ref(ROOT/args.staged_review),previousCount=a.ref(ROOT/args.previous_count),expectedMainSnapshot=args.expected_main_snapshot,caller=a.ref(Path(a.__file__)),codeRefs=codes,inputRefs=inputs,evidenceRefs=[a.ref(P/'METHOD.md'),a.ref(closure)]+[c['log']for c in commands],commands=commands,schemaVerbatim=schema,noSourceDecodeGeometryNumericalRenderDBLeaseWorker=True));print(json.dumps(dict(passed=True,codePins=len(codes),inputPins=len(inputs))))
