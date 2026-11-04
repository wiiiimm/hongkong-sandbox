"""Actual production renderer capture with private source terrain; no acceptance."""
from pathlib import Path
import copy,json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tower6803-private-terrain-capture-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;OLD=BASE/'government-xl-exact-parent-support-sequence-20261006-6803-0';UIDS=['landsd/6803:0','landsd/15047:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();receipt=read(OLD/'result.json');pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};sel=OLD/'selection.json.gz';assert digest(sel.read_bytes())==pins[str(sel.relative_to(ROOT))]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 rows=[copy.deepcopy(r)for r in read(sel)['rows']if r['uid']in UIDS];assert len(rows)==2;mp=ROOT/'3d-viewer/city/data/manifest.json';mh=ref(mp);refs=[Path(__file__),OLD/'result.json',sel,mp]
 for r in rows:
  asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset);target=LOCAL/r['candidate']['entry']['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(asset.read_bytes());r['candidate']['path']=str(target.relative_to(ROOT));refs.append(target)
  tile=ROOT/'3d-viewer'/r['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==r['uid'])==r['source']['building'];r['source']['tileSHA256']=digest(tile.read_bytes());refs.append(tile)
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=mh['sha256']))
 terrainDoc=BASE/'government-xl-tower6803-pair-terrain-candidate-v2-20261020'
 tr=read(terrainDoc/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(tr['jobId'],)).fetchone()==('complete',tr)
 for e in tr['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
 refs.append(terrainDoc/'result.json')
 terrainCandidates=terrainDoc/'terrain-candidates.json'
 save(DOC/'terrain-candidates.json',read(terrainCandidates))
 metrics=HERE/'acceptance-metrics-multi-retained.mjs';attrs=HERE/'tower6803_actual_attributes_v1_20261020.mjs'
 command=['node',str(metrics),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT)),'--terrain-candidates',str(terrainCandidates.relative_to(ROOT))]
 with (DOC/'metrics.log').open('w')as log:subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 report=read(DOC/'metrics.json');assert len(report['rows'])==2 and all(not r.get('error')for r in report['rows'])
 save(DOC/'input.json.gz',dict(currentManifest=mh,currentCatalogueRefs=[ref(ROOT/'3d-viewer'/url)for url in read(mp)['officialModelCatalogues']],evidenceRefs=[ref(DOC/'selection.json.gz')],rows=[dict(uid=r['uid'],entry=r['candidate']['entry'],building=r['source']['building'],path=r['candidate']['path'])for r in rows]))
 subprocess.run(['node',str(attrs),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True);captured=read(DOC/'attributes.json.gz');assert captured['startEndAllInputsVerified']and ref(mp)==mh and reservations.owns(lease)
 for p,h in {**report['inputHashes'],**captured['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([metrics,attrs,LOCAL/'runtime-geometry.json.gz'])
 module('tower6803_capture_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-original-terrain-pair-production-capture',list(dict.fromkeys(refs)),dict(uids=UIDS,completeFaces=23749,rows=report['rows'],installationApproved=False))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
