"""Exact cached neighbour originals and complete projected surface comparison; diagnostic only."""
from pathlib import Path
import gzip,uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citic-neighbour-originals-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/234783:0','landsd/123871:0','landsd/256427:0']
def main():
 assert not DOC.exists();refs=[Path(__file__)]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  rows=c.execute("SELECT p.viewer_uid,p.cache_key,p.source_result_sha,p.sheet,x FROM astra_modelling.native_model_sizes p JOIN astra_modelling.native_stage_results r USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') x WHERE p.run_id=%s AND p.viewer_uid=ANY(%s) AND x->>'modelId'=p.model_id",(NATIVE_RUN,UIDS)).fetchall()
  prev=read(BASE/'government-xl-citic-current-assembly-v1-20261017/result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prev['jobId'],)).fetchone()==('complete',prev)
 assert len(rows)==3
 claim=reservations.claim('citic-neighbours-'+str(uuid.uuid4()),['building:'+u for u in UIDS+['landsd/232579:0']],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();LOCAL.mkdir();decoder=module('citic_original_decoder',HERE/'xl-second-pass.py');decoder.LOCAL=LOCAL
  pins={x['path']:x['sha256'] for x in prev['evidenceRefs']}
  p=BASE/'government-xl-citic-current-assembly-v1-20261017/support-inputs.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
  refs.extend([p,BASE/'government-xl-citic-current-assembly-v1-20261017/result.json'])
  podium=next(x for x in read(p)['sources'] if x['uid']=='landsd/232579:0');podium.update(modelId=podium['candidate']['entry']['modelId'],triangles=1762)
  asset=ROOT/podium['candidate']['path'];assert digest(asset.read_bytes())==podium['sourceSHA256'];refs.append(asset)
  dest=LOCAL/'assets'/asset.name;dest.parent.mkdir();dest.write_bytes(asset.read_bytes());refs.append(dest)
  pt=decoder.glb_triangles(podium);pp=[Polygon(f[:,[0,2]]) for f in pt];output=[];saved=[]
  for uid,key,resultsha,sheet,m in rows:
   sha=m['asset']['sha256'];dest=LOCAL/'assets'/(sha+'.glb.gz')
   cached=ROOT/'3d-viewer/city/data/official-models/tourist-trial-000'/dest.name
   if cached.exists():raw=cached.read_bytes();refs.append(cached)
   else:
    src=HERE.parent/'central-completion/staged'/sheet/'BUILDING'/m['modelId']/(m['modelId']+'.gltf')
    glb,stats=decoder._convert_one.__globals__['_packer'].pack(src)
    raw=decoder.recovery.canonical_bytes(gzip.compress(glb,mtime=0),sha)
    refs.append(src);refs.extend(src.parent/b['uri'] for b in read(src)['buffers'])
   assert digest(raw)==sha and len(raw)==m['asset']['bytes'];dest.write_bytes(raw);refs.append(dest)
   row=dict(uid=uid,modelId=m['modelId'],triangles=m['triangles'],sourceSHA256=sha,native=dict(cacheKey=key,resultSha=resultsha,sheet=sheet,model=m));saved.append(row)
   nt=decoder.glb_triangles(row);pairs=[]
   for j,n in enumerate(nt):
    npoly=Polygon(n[:,[0,2]])
    if npoly.area==0:continue
    nb=npoly.bounds
    for i,(p,poly) in enumerate(zip(pt,pp)):
     if poly.area==0:continue
     pb=poly.bounds
     if pb[2]<nb[0] or nb[2]<pb[0] or pb[3]<nb[1] or nb[3]<pb[1]:continue
     hit=poly.intersection(npoly)
     if hit.area<=0:continue
     assert hit.geom_type=='Polygon'
     coords=np.asarray(hit.exterior.coords);mat=np.c_[coords,np.ones(len(coords))]
     a=np.linalg.solve(np.c_[p[:,[0,2]],np.ones(3)],p[:,1]);b=np.linalg.solve(np.c_[n[:,[0,2]],np.ones(3)],n[:,1]);delta=mat@(a-b)
     pairs.append(dict(podiumFace=i,neighbourFace=j,areaM2=hit.area,minVerticalDelta=float(delta.min()),maxVerticalDelta=float(delta.max())))
   output.append(dict(uid=uid,sourceSHA256=sha,completeSourceFaces=len(nt),positiveAreaProjectionPairs=pairs,signCrossingPairs=sum(x['minVerticalDelta']<=0<=x['maxVerticalDelta'] for x in pairs)))
   print(dict(uid=uid,pairs=len(pairs),crossings=output[-1]['signCrossingPairs']),flush=True);assert reservations.heartbeat(lease)['ok']
  save(DOC/'source-records.json',saved);save(DOC/'surface-comparison.json.gz',dict(rows=output,completePodiumFaces=len(pt),qualification='Floating-point surface diagnostic, not collision or identity acceptance; all original geometry unchanged.',installationApproved=False))
  refs.extend([HERE/'xl-second-pass.py',HERE.parent/'citywide-native/convert.py'])
  for p in LOCAL.rglob('*'):
   if p.is_file():refs.append(p)
  result=module('citic_neighbours_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'citic-three-exact-original-neighbour-surface-diagnostic-v1',list(dict.fromkeys(refs)),dict(uids=UIDS+['landsd/232579:0'],rows=[dict(uid=r['uid'],sourceFaces=r['completeSourceFaces'],surfaceCrossingPairs=r['signCrossingPairs']) for r in output],newlyInstalled=0,installationApproved=False))
  print(dict(jobId=result['jobId']),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
