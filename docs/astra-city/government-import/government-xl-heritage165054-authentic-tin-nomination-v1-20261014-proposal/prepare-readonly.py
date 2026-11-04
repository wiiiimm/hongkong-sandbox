"""Metadata/code/source hash preflight only; never decode or construct source geometry."""
from pathlib import Path
import ast,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[4]; HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
import heritage165054_authentic_tin_nomination_v1_20261014 as a
P=a.PROPOSAL;assert not a.DOC.exists() and not a.LOCAL.exists() and not(P/'draft-pins.json').exists();commands=[]
def run(cmd,name,cwd=ROOT):
    log=P/name;assert not log.exists();r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True);log.write_text(r.stdout+r.stderr);commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(log)));assert r.returncode==0,(cmd,log)
run([sys.executable,'-m','unittest','-v','test_heritage_authentic_tin_nomination_v1_20261014','test_exact_distinct_evidence_refs_v1_20261014','test_timed_owned_lease_pulse_v1_20261014'],'scope-and-supervisor-fixtures.log',HERE)
folders=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'citywide-source',HERE.parent/'landmark-acquisition',HERE.parent/'island-detail-integration',HERE.parent/'assembly-support-review',HERE.parent/'mui-wo-buildings',ROOT/'docs/astra-city/mui-wo-buildings/review']
todo=[Path(a.__file__),Path(__file__),a.source.FREEZER,HERE/'run.py',HERE/'resolve-pass.py',HERE/'pending-context.py',HERE.parent/'assembly-support-review/native_terrain.py',HERE.parent/'mui-wo-buildings/fine_terrain_audit.py',HERE.parent/'shared-modelling/reservations.py',HERE/'test_heritage_authentic_tin_nomination_v1_20261014.py',HERE/'test_exact_distinct_evidence_refs_v1_20261014.py',HERE/'test_timed_owned_lease_pulse_v1_20261014.py'];seen=set();codes=[]
while todo:
    p=todo.pop().resolve()
    if p in seen:continue
    seen.add(p);codes.append(a.ref(p))
    tree=ast.parse(p.read_text())
    for n in ast.walk(tree):
        mods=[n.module] if isinstance(n,ast.ImportFrom) and n.module else [q.name for q in n.names] if isinstance(n,ast.Import) else []
        for mod in mods:
            for folder in folders:
                q=folder/(mod.replace('.','/')+'.py')
                if q.is_file():todo.append(q)
        if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value.endswith('.py'):
            for q in [ROOT/n.value,*[folder/n.value for folder in folders]]:
                if q.is_file():todo.append(q)
codes.append(a.ref(HERE.parent/'shared-modelling/branch.json'))
data,refs=a.inputs();pins=dict(caller=a.ref(Path(a.__file__)),codeRefs=a.distinct_refs(codes),inputRefs=refs,currentManifestSHA256=a.CURRENT,currentSnapshot=a.SNAPSHOT,acquisitionJob=a.ACQUISITION_JOB,cells=data['cells'],region=data['region'],canonicalActors=data['scope']['allActorsForNominationLease'],fullCurrentAcceptanceStillRequired=True)
for q in pins['codeRefs']+pins['inputRefs']:a.check(q)
a.save(P/'draft-pins.json',pins);run([sys.executable,str(Path(a.__file__)),'--schema-only'],'schema-only.log');schema=json.loads((P/'schema-only.log').read_text());assert schema['passed']
refs=[a.ref(P/'METHOD.md'),a.ref(P/'draft-pins.json')]+[q['log'] for q in commands]
for q in pins['codeRefs']+pins['inputRefs']+refs:a.check(q)
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),commands=commands,evidenceRefs=refs,schemaVerbatim=schema,noNetworkGeometryDecodeTerrainConstructionRendererDBLeaseWorker=True));print(json.dumps(dict(passed=True,codePins=len(pins['codeRefs']),inputPins=len(pins['inputRefs']),canonicalActors=len(pins['canonicalActors']))))
