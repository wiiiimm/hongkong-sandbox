"""Prep-only API correction; reuse completed4 fixtures, no source calculations."""
from pathlib import Path
import sys,ast,json,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
import heritage165054_saved_current_native_bounds_reconciliation_v1_20261014 as a
P=a.PROPOSAL;assert not a.DOC.exists()and not a.LOCAL.exists()and not(P/'draft-pins.json').exists()
def missing_namespace_attributes(path,name,module):
    missing=set()
    for node in ast.walk(ast.parse(path.read_text())):
        if not isinstance(node,ast.Attribute):continue
        chain=[];n=node
        while isinstance(n,ast.Attribute):chain.append(n.attr);n=n.value
        if not isinstance(n,ast.Name)or n.id!=name:continue
        value=module
        for attr in reversed(chain):
            if not hasattr(value,attr):missing.add(name+'.'+'.'.join(reversed(chain)));break
            value=getattr(value,attr)
    return sorted(missing)
old=P/'prepare-readonly.py';assert a.ref(old)['sha256']=='4b45b3fd88fc9cfedb521b986a48f34c83ef62cfbd475b333df76994bc56c51c'
terminal=P/'ROOT-preflight-v1-terminal.json';t=a.read(terminal);assert t['execSession']==5634 and t['exitCode']==1 and t['completedFixtures']==4 and t['draftPinsWritten']is False and t['databaseOrLeaseClaimStarted']is False
log=P/'saved-finalization-fixtures.log';assert a.ref(log)['sha256']=='65d301aeca4cbae34c6ec46ff354ed02f0b7e2e66fef05dc01837714ae313482'and 'Ran 4 tests'in log.read_text()and '\nOK\n'in log.read_text()
assert missing_namespace_attributes(old,'a',a)==['a.SNAPSHOT']
assert missing_namespace_attributes(Path(__file__),'a',a)==[]
assert missing_namespace_attributes(Path(a.__file__),'source',a.source)==[]
files=[Path(__file__),old,Path(a.__file__),HERE/'test_heritage_saved_native_bounds_binding_v1_20261014.py',HERE/'heritage_saved_native_bounds_binding_v1_20261014.py']
for f in files:ast.parse(f.read_text())
prior=a.read(a.source.PROPOSAL/'draft-pins.json');data=a.inputs();refs=a.distinct_refs(data[-1]+[a.ref(terminal),a.ref(log)]);codes=a.distinct_refs(prior['codeRefs']+[a.ref(f)for f in files])
pins=dict(caller=a.ref(Path(a.__file__)),codeRefs=codes,inputRefs=data[-1],canonicalResources=a.resources(),cached6653WholeUnusedBoundsOnly=True,noSourceDecodeOrGeographicBoundsArithmeticInPreparation=True,currentManifestSHA256=a.CURRENT,currentSnapshot=a.source.SNAPSHOT)
for q in codes+refs:a.check(q)
a.save(P/'draft-pins.json',pins)
cmd=[sys.executable,str(Path(a.__file__)),'--schema-only'];r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);slog=P/'schema-only-v2.log';assert not slog.exists();slog.write_text(r.stdout+r.stderr);assert r.returncode==0,slog;schema=json.loads(r.stdout);assert schema['passed']
outputs=[a.ref(P/'development-metadata-schema-observations.json'),a.ref(P/'METHOD.md'),a.ref(P/'draft-pins.json'),a.ref(log),a.ref(terminal),a.ref(old),a.ref(slog)]
for q in codes+refs+outputs:a.check(q)
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),evidenceRefs=outputs,commands=[dict(completedFixturesReused=True,fixtures=4,log=a.ref(log),actualFailedPrep=a.ref(terminal)),dict(command=cmd,exitCode=0,log=a.ref(slog))],boundedActualImportedNamespaceFixturePassed=True,oldMissingNamespaceAttributes=['a.SNAPSHOT'],schemaVerbatim=schema,noModelChecksRendererDBLeaseWorker=True));print(json.dumps(dict(passed=True,codePins=len(codes),inputPins=len(data[-1]),canonicalResources=a.resources(),completedFourFixturesReused=True)))
