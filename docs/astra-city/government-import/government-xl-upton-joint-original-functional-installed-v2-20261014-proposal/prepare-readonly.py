"""Bind completed local ROOT receipts/images/count/code only; no DB/worker/lease."""
from pathlib import Path
import argparse,sys,ast,json,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
import upton_joint_original_functional_publication_v2_20261014 as a
p=argparse.ArgumentParser();p.add_argument('--stage-job',required=True);p.add_argument('--staged-job',required=True);p.add_argument('--staged-review',required=True);p.add_argument('--polyu-capture-job',required=True);p.add_argument('--previous-count',required=True);p.add_argument('--expected-main-snapshot',required=True);args=p.parse_args();P=a.PROPOSAL;assert not a.INSTALLED.exists()and not(a.HERE/'local'/a.INSTALL_BATCH).exists()and not(P/'actual-readonly-preparation.json').exists()
commands=[]
def run(cmd,name,cwd=ROOT):
    f=P/name;assert not f.exists();r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True);f.write_text(r.stdout+r.stderr);commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(f)));assert r.returncode==0,(cmd,f)
run([sys.executable,'-m','unittest','-v','test_upton_staged_image_review_binding_v1_20261014'],'six-review-count-fixtures.log',HERE)
source=a.verified(a.stage.DOC,args.stage_job);pins,adapted,rows,c,patch=a.stage.load_completed();staged=a.verified(a.STAGED,args.staged_job);acceptance=a.read(a.STAGED/'acceptance.json');assert acceptance['passed']and not acceptance['publication']and acceptance['sourceApplicabilityVerbatim']==adapted;report=a.browser_report(a.STAGED,'staged-browser.json')
images=[a.ref(a.STAGED/v['file'])for v in report['views']if 'time'in v]+[a.ref(a.STAGED/v['file'])for v in report['retainedNativeOwnViews']];review=(ROOT/args.staged_review).resolve();assert review==a.STAGED/'ROOT-IMAGE-INSPECTION.json';decision=a.validate_review(a.read(review),job=args.staged_job,report_ref=a.ref(a.STAGED/'staged-browser.json'),stage_ref=a.ref(a.stage.DOC/'result.json'),functional_ref=pins['acceptedROOTReview'],manifest_sha=a.physical.CURRENT,image_refs=images)
polyu=a.verified(a.POLYU,args.polyu_capture_job);assert a.read(a.POLYU/'input.json.gz')['currentManifestSHA256']==a.physical.CURRENT and a.read(a.POLYU/'actual-runtime-command.json')['exitCode']==0
pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert a.read(pointer)['snapshotId']==args.expected_main_snapshot;manifest=ROOT/'3d-viewer/city/data/manifest.json';assert a.ref(manifest)['sha256']==a.physical.CURRENT;models=a.read(a.stage.STAGE/'catalogue.json')['models'];assert [m['uid']for m in models]==a.stage.OWNED;delta=a.inventory_delta(a.read(ROOT/args.previous_count),models,manifest_sha=a.physical.CURRENT,snapshot=args.expected_main_snapshot);assert delta['returnedModels']==2
codes=[];folders=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',HERE.parent/'assembly-support-review',HERE.parent/'model-review-ledger'];todo=[HERE.parent/'enhancement-screening/screen.py',HERE.parent/'landmark-completion-audit/audit.py',Path(a.__file__),a.PUB,HERE/'integrate.py',HERE.parent/'island-detail-integration/publish.py',HERE.parent/'model-review-ledger/ledger.py',HERE.parent/'building-progress/export.py',HERE/'xl-current-installed-count-audit.py'];seen=set()
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
codes +=[a.ref(ROOT/'3d-viewer/scripts/building-progress'/f)for f in ['generate.mjs','counts.mjs','screening.mjs']]
codes +=[a.ref(Path(__file__)),a.ref(HERE/'test_upton_staged_image_review_binding_v1_20261014.py'),a.ref(ROOT/'3d-viewer/scripts/build_progress.mjs')]
closure=a.read(a.stage.PROPOSAL/'literal-browser-app-closure.json');codes +=[dict(path=p,sha256=h)for p,h in closure['inputHashes'].items()]
inputs=source['evidenceRefs']+staged['evidenceRefs']+polyu['evidenceRefs']+[a.ref(f)for folder in [a.stage.DOC,a.STAGED,a.POLYU]for f in [folder/'result.json',folder/'ROOT-VERIFIED.json']]+images+[a.ref(review),a.ref(ROOT/args.previous_count),a.ref(pointer),a.ref(ROOT/a.read(pointer)['inventory']),a.ref(a.HERE/'local'/a.STAGED_BATCH/'browser-config.json')];inputs +=[a.ref(ROOT/f)for f in sorted(a.MUTABLE_CURRENT)if(ROOT/f).exists()];codes=a.distinct_refs(codes);inputs=a.distinct_refs(inputs)
for q in codes+inputs:a.check(q)
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),codeRefs=codes,inputRefs=inputs,commands=commands,evidenceRefs=[a.ref(P/'METHOD.md')]+[c['log']for c in commands],stageJob=args.stage_job,stagedJob=args.staged_job,stagedImageReview=a.ref(review),completedPolyUCaptureJob=args.polyu_capture_job,previousCount=a.ref(ROOT/args.previous_count),expectedMainSnapshot=args.expected_main_snapshot,sourceScopedApplicabilityVerbatim=adapted,ROOTStagedReviewVerbatim=decision,fixedXLDeltaBinding=delta,orderedGroundUnchangedSHA256=a.stage.old.functional.review.GROUND,orderedGroundFaces=11645,qualifiedMetadataEquivalentTerrain=a.ref(ROOT/a.read(a.stage.STAGE/'plan.json')['topLevelTerrainPatches'][0]['source']),noGeometryBrowserPublicationDBLeaseWorker=True));print(json.dumps(dict(passed=True,codePins=len(codes),inputPins=len(inputs),countDelta=delta)))
