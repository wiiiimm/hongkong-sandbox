"""ROOT-only source/hash/runtime closure schema; no geometry/DB/leases."""
from pathlib import Path
import sys,ast,json,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
import heritage165054_authentic_tin_owned_ordinary_v1_20261014 as a
P=a.PROPOSAL;assert not a.DOC.exists()and not a.LOCAL.exists()and not(P/'draft-pins.json').exists();commands=[]
def run(cmd,name,cwd=ROOT):
    path=P/name;assert not path.exists();r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True);path.write_text(r.stdout+r.stderr);commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,path)
run([sys.executable,'-m','unittest','-v','test_heritage_authentic_tin_owned_ordinary_v1_20261014','test_exact_distinct_evidence_refs_v1_20261014','test_timed_owned_lease_pulse_v1_20261014'],'binding-and-supervisor-fixtures.log',HERE)
run(['node',str(a.old.CLOSURE),str((P/'actual-runtime-literal-explicit-closure.json').relative_to(ROOT))],'literal-runtime-closure.log')
closure=a.read(P/'actual-runtime-literal-explicit-closure.json');assert closure['everyOtherComputedImportRejected']and closure['readOnlyCodeHashingOnly'];codes=[a.ref(Path(__file__))]+[dict(path=p,sha256=h)for p,h in closure['inputHashes'].items()]
folders=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'citywide-source',HERE.parent/'landmark-acquisition',HERE.parent/'island-detail-integration',HERE.parent/'assembly-support-review',ROOT/'docs/astra-city/mui-wo-buildings/review']
todo=[Path(a.__file__),HERE/'run.py',a.old.FREEZER,HERE/'xl-final-script-pass.py',HERE/'acceptance-policy.py',a.HERE/'heritage165054_authentic_tin_nomination_v2_20261014.py',HERE.parent/'shared-modelling/reservations.py',HERE/'test_heritage_authentic_tin_owned_ordinary_v1_20261014.py',HERE/'test_exact_distinct_evidence_refs_v1_20261014.py',HERE/'test_timed_owned_lease_pulse_v1_20261014.py'];seen=set()
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
codes +=[a.ref(a.old.CLOSURE),a.ref(HERE/'exact_existing_validator_runtime_closure_v1_20261014.mjs'),a.ref(HERE.parent/'shared-modelling/branch.json')]
data=a.inputs();pins=dict(caller=a.ref(Path(a.__file__)),codeRefs=a.distinct_refs(codes),inputRefs=data[-1],nominationJob=data[3],canonicalResources=a.resources(data[2]['scope']['allActorsForNominationLease']),currentManifestSHA256=a.CURRENT,currentSnapshot=a.SNAPSHOT,ownedUID=a.UID,sourceFaces15140=True,newPrivateTerrainCandidateBound=True,wholeParentDomainDeltaStillRequired=True)
for q in pins['codeRefs']+pins['inputRefs']:a.check(q)
a.save(P/'draft-pins.json',pins);run([sys.executable,str(Path(a.__file__)),'--schema-only'],'schema-only.log');schema=json.loads((P/'schema-only.log').read_text());assert schema['passed']
refs=[a.ref(P/'METHOD.md'),a.ref(P/'draft-pins.json'),a.ref(P/'actual-runtime-literal-explicit-closure.json')]+[q['log']for q in commands]
for q in pins['codeRefs']+pins['inputRefs']+refs:a.check(q)
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),commands=commands,evidenceRefs=refs,schemaVerbatim=schema,noSourceDecodeGeometryRendererDBLeaseWorker=True));print(json.dumps(dict(passed=True,codePins=len(pins['codeRefs']),inputPins=len(pins['inputRefs']))))
