"""Current viewer metrics and existing neighbour policies for private West Wing terrain."""
import json,sys,uuid,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-runtime-checks-v3-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
NAMES=['government-xl-west-wing-nested-terrain-v2-20261018','government-xl-west-wing-native-scope-v2-20261018','government-xl-west-wing-group-four-world-v1-20261018'];UIDS=['landsd/26195:0','landsd/322270:0','landsd/315069:0','landsd/319534:0']
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);pins={};refs=[Path(__file__),HERE/'west_wing_runtime_checks_v1_20261018.py',BASE/'government-xl-west-wing-runtime-checks-v1-20261018/worker-0.log']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(BASE/NAMES[2]/'selection.json.gz')['rows'];assert [r['uid']for r in rows]==UIDS
 for r in rows:
  source=ROOT/r['candidate']['path'];raw=source.read_bytes();assert digest(raw)==r['sourceSHA256'];target=LOCAL/r['candidate']['entry']['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);r['candidate']['path']=str(target.relative_to(ROOT));refs.append(target)
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())));save(LOCAL/'catalogue.json',dict(models=[r['candidate']['entry']for r in rows]));save(LOCAL/'catalogue-index.json',dict(models=len(rows),catalogues=['catalogue.json']))
 patches=read(BASE/NAMES[0]/'terrain-candidates.json');scope=read(BASE/NAMES[1]/'scope.json');touch=set(scope['touchingNativeUids']);patches[0]['replaces']['retainedUids']=sorted(touch-set(UIDS));save(DOC/'terrain-candidates.json',patches)
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');forms={};native={}
 for tile in manifest['tiles']:
  p=ROOT/'3d-viewer'/tile['url']
  for b in read(p)['buildings']:forms[b['uid']]=(b,tile['url'])
 for url in manifest['officialModelCatalogues']:
  for e in read(ROOT/'3d-viewer'/url)['models']:native[e['uid']]=e
 final=module('west_runtime_forms',HERE/'xl-final-script-pass.py');near={b['uid']for b,_,_ in final.load_forms(scope['changedParentExtent'])};required=near|touch
 for u in touch:
  required.update(d['uid']for d in native[u].get('supportDependencies',[]))
 for u in list(required):
  parent=forms[u][0].get('parent')
  if parent:required.update(v for v in native if forms[v][0].get('parent')==parent)
 inputs={str((ROOT/'3d-viewer'/forms[u][1]).relative_to(ROOT)):digest((ROOT/'3d-viewer'/forms[u][1]).read_bytes())for u in required}
 save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=forms[u][0],patchIndexes=[0],existingNative=u in native)for u in sorted(required)],patches=patches,candidateIds=UIDS,inputHashes=inputs))
 commands=[['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],['node',str(HERE/'check-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/'],['node',str(HERE/'check-native-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/']]
 for i,cmd in enumerate(commands):
  with(DOC/f'worker-{i}.log').open('w')as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 assert reservations.owns(lease);refs.extend(ROOT/p for p in pins);refs.extend(ROOT/p for p in inputs);refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');refs.extend(HERE/n for n in ['acceptance-metrics-multi-retained.mjs','check-neighbours.mjs','check-native-neighbours.mjs'])
 out=module('west_runtime_checks_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'west-wing-current-runtime-metrics-and-neighbour-checks-v1',list(dict.fromkeys(refs)),dict(uids=UIDS,neighbourForms=len(required),requiredNativeChecks=sorted(touch-set(UIDS)),fullAcceptance=False,publication=False));print(out['jobId'],flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();scope=read(BASE/NAMES[1]/'scope.json');keys={'building:'+u for u in scope['touchingNativeUids']}|{'terrain:city/data/terrain.json'};claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
