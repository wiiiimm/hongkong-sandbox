"""Bounded exact-source Elements native support acquisition using existing pipeline, no shared writes."""
import importlib.util,json,pathlib,sys,shutil,gzip
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent/'elements-support';DOC=ROOT/'docs/astra-city/identity-four-native/elements-support';HERE.mkdir(parents=True,exist_ok=True);DOC.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(p.read_bytes())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations
leases=[read(pathlib.Path('/tmp/astra-identity-four-elements-lease.json'))]
assert all(reservations.owns(l) for l in leases),'Source reservation lost'
uids={'landsd/273061:0'};assert {'building:'+u for u in uids}=={r for l in leases for r in l['resources']}
a=load('existing_acquisition',ROOT/'source-scripts/city/landmark-acquisition/acquire.py');a.HERE=HERE;a.DOCS=DOC
for name in ['service.json','index.json']:
 if not (HERE/name).exists():shutil.copyfile(a.BASE/name,HERE/name)
a.write(HERE/'batch.json',{'batchId':'identity-four-elements-support','capBytes':10_000_000})
a.write(HERE/'target-input.json',{'targets':[{'uid':u}for u in sorted(uids)]})
network=a.Network(HERE/'transfer-ledger.json',cap=10_000_000);plan=read(HERE/'plan.json')if(HERE/'plan.json').exists()else a.prepare(network)
print('Exact targets',plan['targetParts'],'sheets',plan['officialTiles'],flush=True)
targets={t['uid']:t for t in plan['targets']};caches=a.retained_caches()
for sheet,tile in plan['tiles'].items():
 assert all(reservations.owns(l) for l in leases)
 state=a.acquire_tile(network,sheet,tile,targets,caches)
 print(sheet,state['status'],len(state['exactGLTFEntries']),flush=True)
r=a.report(plan,network);print(json.dumps({'summary':r['summary'],'bytes':r['transfer']['receivedBytes'],'models':r['nativeModelParts']}))
