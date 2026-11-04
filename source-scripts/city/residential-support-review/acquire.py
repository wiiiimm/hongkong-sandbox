"""Bounded exact-source LOHAS assembly acquisition using existing pipeline, no shared writes."""
import importlib.util,json,pathlib,sys,shutil,gzip
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residential-support-review'
def read(p):return json.loads(p.read_bytes())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations
leases=[read(pathlib.Path('/tmp/astra-residential-support-lease.json')),read(pathlib.Path('/tmp/astra-residential-podium-lease.json'))]
assert all(reservations.owns(l) for l in leases),'Source reservation lost'
uids={'landsd/100073:0','landsd/149982:0','landsd/150499:0','landsd/54170:0'};assert {'building:'+u for u in uids}=={r for l in leases for r in l['resources']}
a=load('existing_acquisition',ROOT/'source-scripts/city/landmark-acquisition/acquire.py');a.HERE=HERE;a.DOCS=DOC
for name in ['service.json','index.json']:
 if not (HERE/name).exists():shutil.copyfile(a.BASE/name,HERE/name)
a.write(HERE/'batch.json',{'batchId':'residential-support-review','capBytes':10_000_000})
a.write(HERE/'target-input.json',{'targets':[{'uid':u}for u in sorted(uids)]})
network=a.Network(HERE/'transfer-ledger.json',cap=10_000_000);plan=read(HERE/'plan.json')if(HERE/'plan.json').exists()else a.prepare(network)
print('Exact targets',plan['targetParts'],'sheets',plan['officialTiles'],flush=True)
targets={t['uid']:t for t in plan['targets']};caches=a.retained_caches()
for sheet,tile in plan['tiles'].items():
 assert all(reservations.owns(l) for l in leases)
 state=a.acquire_tile(network,sheet,tile,targets,caches)
 print(sheet,state['status'],len(state['exactGLTFEntries']),flush=True)
r=a.report(plan,network);print(json.dumps({'summary':r['summary'],'bytes':r['transfer']['receivedBytes'],'models':r['nativeModelParts']}))
