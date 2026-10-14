"""Exact original archive metadata/code/input preparation only; no network/geometry/DB/lease."""
from pathlib import Path
import ast,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[4]; HERE=ROOT/'source-scripts/city/government-import'; sys.path.insert(0,str(HERE))
import heritage165054_south20b_terrain_acquisition_v3_20261014 as a
P=a.PROPOSAL; assert not a.DOC.exists() and not a.LOCAL.exists() and not (P/'draft-pins.json').exists(); commands=[]
def run(cmd,name,cwd=ROOT):
    log=P/name; assert not log.exists(); r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True); log.write_text(r.stdout+r.stderr); commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(log))); assert r.returncode==0,(cmd,log)
run([sys.executable,'-m','unittest','-v','test_heritage_authentic_terrain_acquisition_v1_20261014','test_heritage_south20b_terrain_acquisition_v1_20261014','test_heritage_south20b_source_only_resources_v2_20261014','test_exact_distinct_evidence_refs_v1_20261014','test_timed_owned_lease_pulse_v1_20261014'],'metadata-and-supervisor-fixtures.log',HERE)
folders=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'citywide-source',HERE.parent/'landmark-acquisition',HERE.parent/'island-detail-integration',HERE.parent/'assembly-support-review',ROOT/'docs/astra-city/mui-wo-buildings/review']
todo=[Path(a.__file__),Path(__file__),a.DOWNLOADER,a.PARSER,a.FREEZER,HERE/'run.py',HERE.parent/'shared-modelling/reservations.py',HERE/'test_heritage_authentic_terrain_acquisition_v1_20261014.py',HERE/'test_heritage_south20b_terrain_acquisition_v1_20261014.py',HERE/'test_heritage_south20b_source_only_resources_v2_20261014.py',HERE/'test_exact_distinct_evidence_refs_v1_20261014.py',HERE/'test_timed_owned_lease_pulse_v1_20261014.py']; seen=set(); codes=[]
while todo:
    p=todo.pop().resolve()
    if p in seen: continue
    seen.add(p); codes.append(a.ref(p))
    for n in ast.walk(ast.parse(p.read_text())):
        mods=[n.module] if isinstance(n,ast.ImportFrom) and n.module else [q.name for q in n.names] if isinstance(n,ast.Import) else []
        for mod in mods:
            for folder in folders:
                q=folder/(mod.replace('.','/')+'.py')
                if q.is_file(): todo.append(q)
codes.append(a.ref(HERE.parent/'shared-modelling/branch.json'))
data=a.inputs(); resources=a.canonical_resources(data[1]); pins=dict(caller=a.ref(Path(a.__file__)),codeRefs=a.distinct_refs(codes),inputRefs=data[2],currentManifestSHA256=a.CURRENT,currentSnapshot=a.SNAPSHOT,archiveRevision=a.PIN,exactTerrainMembers=a.MEMBERS,buildingModelsRequested=0,canonicalResources=resources,noGeometryDecode=True)
for q in pins['codeRefs']+pins['inputRefs']: a.check(q)
a.save(P/'draft-pins.json',pins); run([sys.executable,str(Path(a.__file__)),'--schema-only'],'schema-only.log'); schema=json.loads((P/'schema-only.log').read_text()); assert schema['passed']
refs=[a.ref(P/'METHOD.md'),a.ref(P/'preserved-V1-no-owned-lease-conflict.json'),a.ref(P/'V2-to-V3.patch'),a.ref(P/'preserved-V2-preparation-fence-failure.json'),a.ref(P/'draft-pins.json')]+[q['log'] for q in commands]
for q in pins['codeRefs']+pins['inputRefs']+refs: a.check(q)
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),commands=commands,evidenceRefs=refs,schemaVerbatim=schema,noNetworkGeometryDecodeRendererDBLeaseWorker=True)); print(json.dumps(dict(passed=True,codePins=len(pins['codeRefs']),inputPins=len(pins['inputRefs']),canonicalResources=len(resources))))
