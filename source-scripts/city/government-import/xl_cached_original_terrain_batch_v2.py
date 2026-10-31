"""Batch remaining XL foundation checks against byte-verified cached source terrain.
No downloads, geometry edits, automatic acceptance or publication.
"""
import argparse,json,subprocess
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
def main(batch,limit):
 doc=BASE/batch;local=HERE/'local'/batch;assert not (doc/'result.json').exists()
 cap=BASE/'government-xl-remaining-forty-current-terrain-v1-20261021';_,pins=authenticate(cap);refs=[Path(__file__),cap/'result.json']
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 selection=take(cap/'selection.json.gz')['rows'];runtime={r['uid']:r for r in take(HERE/'local'/cap.name/'runtime-geometry.json.gz')['rows']}
 foundations=BASE/'government-xl-remaining-forty-foundations-v1-20261021';_,fp=authenticate(foundations);summary=foundations/'summary.json';assert digest(summary.read_bytes())==fp[str(summary.relative_to(ROOT))];refs.extend([summary,foundations/'result.json']);buried={r['uid']:r.get('fullyBuriedTriangles',0)for r in read(summary)['rows']}
 inv=BASE/'government-xl-scripted-source-inventory-20261022/inventory.json';inventory=read(inv);assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==inventory['manifestSHA256'];remaining={r['uid']for r in inventory['rows']};refs.append(inv)
 # Reuse previous explicit original-terrain results for identical source bytes.
 done=set()
 for p in BASE.glob('*/summary.json'):
  try:x=read(p)
  except (ValueError,OSError):continue
  if not isinstance(x,dict):continue
  for r in ([x] if 'originalTerrainFoundation'in x else x.get('rows',[])):
   if isinstance(r,dict)and ('originalTerrainFoundation'in r or r.get('status')=='cached-original-terrain-missing') and r.get('sourceSHA256'):done.add((r.get('uid')or (r.get('uids')or [None])[0],r['sourceSHA256']))
 selected=[r for r in selection if r['uid']in remaining and buried.get(r['uid'],0)>0 and (r['uid'],r['sourceSHA256'])not in done][:limit]
 assert selected,'No new original-terrain checks selected'
 names=subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g','*.gltf','source-scripts/city'],cwd=ROOT,text=True).splitlines();by_name=defaultdict(list)
 for n in names:by_name[Path(n).name].append(ROOT/n)
 decoder=module('batch_original_terrain',HERE/'xl-second-pass.py');decoder.LOCAL=local;final=module('batch_original_foundation',HERE/'xl-final-script-pass.py');results=[]
 for row in selected:
  uid=row['uid'];native=row['native']
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');sha,stage=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(native['cacheKey'],)).fetchone()
  assert sha==native['resultSha'];m=next(m for m in stage['models']if m['modelId']==row['modelId']);assert m['asset']['sha256']==row['sourceSHA256']
  terrain_records=stage.get('terrain',[]);paths=[]
  for t in terrain_records:
   
   if 'sourceHashes' not in t or 'sourceEntry' not in t:continue
   hashes=t['sourceHashes'];entry=t['sourceEntry'];expected=hashes[entry]
   for candidate in by_name[Path(entry).name]:
    if digest(candidate.read_bytes())!=expected:continue
    members=[]
    for name,h in hashes.items():
     member=candidate.parent/Path(name).name
     if not member.exists()or digest(member.read_bytes())!=h:break
     members.append(member)
    else:paths.append(candidate);refs.extend(members);break
  checkpoint=doc/(uid.split('/')[1]+'.json')
  if checkpoint.exists():
   result=read(checkpoint);assert result['uid']==uid and result['sourceSHA256']==row['sourceSHA256']
   if result['status']=='original-terrain-checked':assert result['sourceTerrainPaths']==[str(p.relative_to(ROOT))for p in paths] and result['nativeResultSHA256']==sha
   results.append(result);print(dict(uid=uid,status='reused-completed-local-checkpoint'),flush=True);continue
  if len(paths)!=len(terrain_records)or not paths:
   result=dict(uid=uid,sourceSHA256=row['sourceSHA256'],status='cached-original-terrain-missing',installationApproved=False)
  else:
   ground=np.concatenate([decoder.terrain_triangles(p)for p in paths]);g=runtime[uid];assert g['sourceSHA256']==row['sourceSHA256'];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];lo,hi=tri.min((0,1)),tri.max((0,1));ground=ground[(ground[:,:,0].max(1)>=lo[0]-10)&(ground[:,:,0].min(1)<=hi[0]+10)&(ground[:,:,2].max(1)>=lo[2]-10)&(ground[:,:,2].min(1)<=hi[2]+10)]
   b=row['source']['building'];f=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));result=dict(uid=uid,sourceSHA256=row['sourceSHA256'],status='original-terrain-checked',priorBuriedTriangles=buried[uid],originalTerrainFoundation=f,sourceTerrainPaths=[str(p.relative_to(ROOT))for p in paths],nativeResultSHA256=sha,installationApproved=False)
  save(doc/(uid.split('/')[1]+'.json'),result);results.append(result);print(dict(uid=uid,status=result['status'],buried=result.get('originalTerrainFoundation',{}).get('fullyBuriedTriangles')),flush=True)
 save(doc/'summary.json',dict(rows=results,installationApproved=False));refs.extend([HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py'])
 module('batch_terrain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'cached-original-terrain-batch',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in selected],rows=results,counts=dict(Counter(r['status']for r in results)),installationApproved=False))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--limit',type=int,default=10);a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch and 1<=a.limit<=40;main(a.batch,a.limit)
