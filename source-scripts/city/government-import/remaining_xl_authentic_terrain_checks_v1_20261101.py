"""Reusable leased private authentic-terrain checks for unfinished XL sources.

Every candidate uses the existing full-TIN builder and unchanged validators.
A failed child remains an investigation. No model or public viewer writes.
"""
import argparse,sys,uuid,subprocess
from run import ROOT,HERE,read,save,digest,reservations
from require_remaining_xl import require_remaining
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['batch','capture','installed','terrain-check']:p.add_argument('--'+key,required=True)
 p.add_argument('--uid',action='append',required=True);p.add_argument('--cover-native',action='append',default=[]);p.add_argument('--builder',choices=['selected_original_local_full_tin_v22_20261101.py','selected_original_source_bounds_full_tin_v1_20261101.py','selected_original_disjoint_grid_child_tin_v1_20261101.py'],default='selected_original_local_full_tin_v22_20261101.py');p.add_argument('--parent-capture');p.add_argument('--grid-parent');p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert a.batch.startswith('government-xl-')and '/'not in a.batch
 assert 0<len(a.uid)==len(set(a.uid))<=40
 assert not a.cover_native or len(a.uid)==1,'Explicit retention is bound to one new source per run'
 assert len(a.cover_native)==len(set(a.cover_native))
 local=HERE/'local'/a.batch;lease=local/'reservation.json'
 _,pins=authenticate(BASE/a.capture);path=BASE/a.capture/'selection.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
 _,cp=authenticate(BASE/a.installed);count=BASE/a.installed/'full-xl-current-count.json';assert digest(count.read_bytes())==cp[str(count.relative_to(ROOT))]
 rows={r['uid']:r for r in read(path)['rows']}
 for uid in a.uid:require_remaining(count,uid,rows[uid]['sourceSHA256'])
 if not a.owned:
  assert not local.exists()
  resources={'building:'+u for u in sorted(a.uid)}|{'terrain:city/data/terrain.json','immutable-source-proof:'+a.batch}
  manifest=read(ROOT/'3d-viewer/city/data/manifest.json');urls={r['url']for r in manifest['terrainPatches']}
  for url in a.cover_native:
   assert url in urls
   terrain=read(ROOT/'3d-viewer'/url);assert terrain.get('nativeMesh')and terrain['meta']['parentTerrain']=='city/data/terrain.json'
   resources.add('terrain:'+url);resources.update('building:'+u for u in terrain['meta']['targetUids'])
  if a.grid_parent:
   assert len(a.uid)==1 and a.grid_parent in urls and a.builder=='selected_original_disjoint_grid_child_tin_v1_20261101.py'
   grid=read(ROOT/'3d-viewer'/a.grid_parent);assert not grid.get('nativeMesh')
   resources.add('terrain:'+a.grid_parent);resources.update('building:'+u for u in grid['meta']['targetUids'])
  resources=sorted(resources)
  c=reservations.claim('remaining-xl-authentic-terrain-'+str(uuid.uuid4()),resources,batch=a.batch,ttl=3600);assert c['ok'],c
  execute_reserved(c['reservation'],lease,[sys.executable,__file__,*sys.argv[1:],'--owned']);return
 outcomes=[]
 for uid in a.uid:
  assert reservations.owns(read(lease));key=uid.split('/')[1].replace(':','-');batch=a.batch+'-'+key
  command=[sys.executable,str(HERE/a.builder),'--batch',batch,'--capture',a.capture,'--terrain-check',a.terrain_check,'--uid',uid,*[v for url in a.cover_native for v in ['--cover-native',url]]]
  if a.grid_parent:command+=['--grid-parent',a.grid_parent]
  if a.parent_capture:command+=['--parent-capture',a.parent_capture]
  with (local/(key+'.log')).open('w')as log:
   proc=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=10800)
  result=dict(uid=uid,batch=batch,exitCode=proc.returncode,installationApproved=False,permanentRejection=False)
  if proc.returncode==0:
   r=read(BASE/batch/'result.json');result['jobId']=r['jobId'];result['terrainResult']=read(BASE/batch/'summary.json')
  outcomes.append(result);save(local/'progress.json',dict(rows=outcomes,installationApproved=False,publication=False));print(dict(uid=uid,exitCode=proc.returncode,jobId=result.get('jobId')),flush=True)
 save(local/'completed.json',dict(rows=outcomes,sourceGeometryChanges=0,publication=False,installationApproved=False))
if __name__=='__main__':main()
