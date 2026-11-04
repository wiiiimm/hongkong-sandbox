"""Recover immutable indexed terminal rooftop sources under renewable leases."""
import json,sys,uuid,subprocess
from pathlib import Path
from collections import defaultdict
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-kai-tak-cruise-component-recovery-v1-20261019';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SRC=BASE/'government-xl-kai-tak-cruise-component-sources-v2-20261019'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json'];pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 rows=read(SRC/'sources.json.gz')['rows'];assert len({r['uid']for r in rows})==len(rows)
 grouped=defaultdict(list);cache={}
 for row in rows:
  grouped[row['native']['sheet']].append(row)
  if row['cachePath']:cache[row['sourceSHA256']]=ROOT/row['cachePath']
 helper=module('kai_rooftop_acquire',HERE/'xl-second-pass.py');helper.LOCAL=LOCAL;out=[]
 for sheet,group in sorted(grouped.items()):
  priorpath=HERE/'local/government-xl-next-five-adjoining-ground-v1-20261018/sheets'/sheet/'directory/result.json';refs.append(priorpath)
  helper.source_sheet(sheet,group,read(priorpath),cache,[])
  for row in group:
   p=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');assert digest(p.read_bytes())==row['sourceSHA256'];tri=decode_original_world_triangles(p.read_bytes());assert len(tri)==row['triangles'];row['candidate']=dict(path=str(p.relative_to(ROOT)),entry=dict(row['native']['model']['candidate'],sourceTile=sheet,rootTranslation=[-834500,0,816500]));out.append(dict(uid=row['uid'],triangles=len(tri),worldBounds=[tri.min((0,1)).tolist(),tri.max((0,1)).tolist()],sourceSHA256=row['sourceSHA256']));print(out[-1],flush=True)
  assert reservations.owns(lease)
 save(DOC/'selection.json.gz',dict(rows=rows));save(DOC/'summary.json',dict(rows=out,installationApproved=False))
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');refs.append(HERE/'xl-second-pass.py')
 module('kai_rooftop_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kai-tak-cruise-exact-original-rooftop-recovery',refs,dict(uids=[r['uid']for r in rows],rows=out,installationApproved=False))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();rows=read(SRC/'sources.json.gz')['rows'];claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['native-model:'+r['native']['cacheKey']+':'+r['modelId']for r in rows],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
