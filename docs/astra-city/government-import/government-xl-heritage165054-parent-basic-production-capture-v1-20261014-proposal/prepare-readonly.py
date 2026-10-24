"""Hash/schema/module-closure preparation only; no renderer or DB/lease."""
from pathlib import Path
import sys,ast,json,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
import heritage165054_parent_basic_production_capture_v1_20261014 as a
P=a.PROPOSAL;assert not a.DOC.exists()and not a.LOCAL.exists()and not(P/'draft-pins.json').exists()
files=[Path(__file__),Path(a.__file__),HERE/'heritage_parent_capture_scope_binding_v1_20261014.py',HERE/'test_heritage_parent_capture_scope_binding_v1_20261014.py',P/'METHOD.md']
for f in files:
 if f.suffix=='.py':ast.parse(f.read_text())
log=P/'scope-fixtures.log';assert not log.exists();cmd=[sys.executable,'-m','unittest','-v','test_heritage_parent_capture_scope_binding_v1_20261014'];r=subprocess.run(cmd,cwd=HERE,capture_output=True,text=True);log.write_text(r.stdout+r.stderr);assert r.returncode==0,log
runtime=a.RUNTIME;cmd2=['node','--check',str(runtime)];r=subprocess.run(cmd2,cwd=ROOT,capture_output=True,text=True);assert r.returncode==0,r.stderr
script="import {snapshotModuleClosure} from './source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=new URL('./',import.meta.url);console.log(JSON.stringify(["+','.join("snapshotModuleClosure(new URL("+json.dumps(str(f.relative_to(ROOT)))+",root),root)"for f in [runtime,HERE/'check-neighbours.mjs'])+"]));"
cmd3=['node','--input-type=module','-e',script];r=subprocess.run(cmd3,cwd=ROOT,capture_output=True,text=True);clog=P/'literal-runtime-closure.log';assert not clog.exists();clog.write_text(r.stdout+r.stderr);assert r.returncode==0,clog;closures=json.loads(r.stdout)
for c in closures:assert c['completeAuditedLiteralImportClosure']and c['computedImportsRejected']and c['unsupportedDynamicImports']==0
prior=a.read(a.bounds.PROPOSAL/'draft-pins.json');data,actors,refs=a.inputs();codes=a.distinct_refs(prior['codeRefs']+[a.ref(f)for f in files]+[dict(path=p,sha256=h)for c in closures for p,h in c['inputHashes'].items()])
for q in codes+refs:a.check(q)
a.save(P/'draft-pins.json',dict(caller=a.ref(Path(a.__file__)),codeRefs=codes,inputRefs=refs,canonicalResources=a.resources(actors),currentManifestSHA256=a.CURRENT,currentSnapshot=a.SNAPSHOT,currentBASICActorsIncludingOwnedMuseum=23,otherBASICActors=22,exactActorUIDs=actors,wholeNativeOutsideCertificateJob=a.JOB))
cmd4=[sys.executable,str(Path(a.__file__)),'--schema-only'];r=subprocess.run(cmd4,cwd=ROOT,capture_output=True,text=True);slog=P/'schema-only.log';assert not slog.exists();slog.write_text(r.stdout+r.stderr);assert r.returncode==0,slog;schema=json.loads(r.stdout);assert schema['passed']and len(schema['canonicalResources'])==47
outs=[a.ref(P/p)for p in ['METHOD.md','draft-pins.json','scope-fixtures.log','literal-runtime-closure.log','schema-only.log']]
for q in codes+refs+outs:a.check(q)
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),evidenceRefs=outs,commands=[dict(command=cmd,exitCode=0,fixtures=5),dict(command=cmd2,exitCode=0),dict(command=cmd3,exitCode=0,log=a.ref(clog)),dict(command=cmd4,exitCode=0,log=a.ref(slog))],schemaVerbatim=schema,noSourceGeometryRendererDBLeaseWorker=True));print(json.dumps(dict(passed=True,codePins=len(codes),inputPins=len(refs),actors=len(actors),canonicalResources=len(a.resources(actors)))))
