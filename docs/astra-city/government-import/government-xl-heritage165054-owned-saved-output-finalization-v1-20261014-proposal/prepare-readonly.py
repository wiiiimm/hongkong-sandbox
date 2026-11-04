"""Saved-output/hash/schema preparation only; no geometry checks or DB/lease."""
from pathlib import Path
import sys,ast,json,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
import heritage165054_owned_saved_output_finalization_v1_20261014 as a
P=a.PROPOSAL;assert not a.DOC.exists() and not a.LOCAL.exists() and not(P/'draft-pins.json').exists()
files=[Path(__file__),Path(a.__file__),HERE/'test_heritage_owned_saved_finalization_v1_20261014.py']
for p in files:ast.parse(p.read_text())
log=P/'saved-finalization-fixtures.log';assert not log.exists();cmd=[sys.executable,'-m','unittest','-v','test_heritage_owned_saved_finalization_v1_20261014'];r=subprocess.run(cmd,cwd=HERE,capture_output=True,text=True);log.write_text(r.stdout+r.stderr);assert r.returncode==0,log
prior=a.read(a.prior.PROPOSAL/'draft-pins.json');data,refs=a.inputs();codes=a.distinct_refs(prior['codeRefs']+[a.ref(p) for p in files])
pins=dict(caller=a.ref(Path(a.__file__)),codeRefs=codes,inputRefs=refs,canonicalResources=a.resources(),noNodeModelFoundationOrTerrainRerun=True,currentManifestSHA256=a.CURRENT,currentSnapshot=a.SNAPSHOT)
for q in codes+refs:a.check(q)
a.save(P/'draft-pins.json',pins)
cmd2=[sys.executable,str(Path(a.__file__)),'--schema-only'];r2=subprocess.run(cmd2,cwd=ROOT,capture_output=True,text=True);slog=P/'schema-only.log';assert not slog.exists();slog.write_text(r2.stdout+r2.stderr);assert r2.returncode==0,slog;schema=json.loads(r2.stdout);assert schema['passed']
outputs=[a.ref(P/'METHOD.md'),a.ref(P/'draft-pins.json'),a.ref(log),a.ref(slog)]
for q in codes+refs+outputs:a.check(q)
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),evidenceRefs=outputs,commands=[dict(command=cmd,exitCode=0,log=a.ref(log)),dict(command=cmd2,exitCode=0,log=a.ref(slog))],schemaVerbatim=schema,noModelChecksRendererDBLeaseWorker=True));print(json.dumps(dict(passed=True,codePins=len(codes),inputPins=len(refs),canonicalResources=a.resources())))
