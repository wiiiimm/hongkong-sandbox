"""Recover Block13 unchanged and measure exact neighbouring source projections."""
import os,sys,tarfile,uuid
from pathlib import Path
import shapely
from run import ROOT,HERE,read,save,digest,connect,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-14-companion-projection-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SHA='4505ff294ae47578d47457fe8db4ca687715dd339b0df7c0445f18def7fe9686'
def main():
 assert not DOC.exists() and not LOCAL.exists()
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/253980:0','building:landsd/255260:0'],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];refs=[Path(__file__)]
 try:
  inputs={}
  for batch,name in [('government-xl-next-two-gap-nearby-originals-v1-20261021','nearby-originals.json.gz'),('government-xl-next-three-coverage-gap-types-v1-20261021','gaps.json.gz'),('government-xl-parkview-14-podium-gap-projection-v1-20261021','projection.json.gz')]:
   folder=BASE/batch;_,pins=authenticate(folder);p=folder/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];inputs[name]=read(p);refs.extend([folder/'result.json',p])
  nearby=next(r for r in inputs['nearby-originals.json.gz']['rows']if r['uid']=='landsd/253980:0')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');sha,native=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(nearby['cacheKey'],)).fetchone();assert sha==nearby['resultSHA256'];model=next(m for m in native['models']if m['asset']['sha256']==SHA);assert model['candidate']['uid']=='landsd/255260:0';artifact=native['artifacts'][0]
  save(LOCAL/'native-source.json',dict(cacheKey=nearby['cacheKey'],resultSHA256=sha,model=model,artifact=artifact));refs.append(LOCAL/'native-source.json')
  sys.path.insert(0,str(HERE.parent/'landmark-resume'));sys.path.insert(0,str(HERE.parent/'citywide-native'))
  from r2_snapshot import R2Store,verify_object
  from source_cache import validate_artifact
  from dotenv import dotenv_values
  for key,value in dotenv_values(ROOT/'.env.modelling').items():
   if key.startswith('R2_')and value and value!='[SENSITIVE]':os.environ.setdefault(key,value)
  artifact=validate_artifact(artifact);bundle=LOCAL/(artifact['sha256']+'.tar.gz');verify_object(R2Store('hk-sandbox-assets'),artifact['key'],artifact['sha256'],artifact['bytes'],bundle)
  with tarfile.open(bundle,'r:gz')as archive:
   members=[m for m in archive if Path(m.name).name==SHA+'.glb.gz'];assert len(members)==1 and members[0].isfile();raw=archive.extractfile(members[0]).read()
  assert digest(raw)==SHA and len(raw)==model['asset']['bytes'];asset=LOCAL/'assets'/(SHA+'.glb.gz');asset.parent.mkdir();asset.write_bytes(raw);refs.append(asset)
  tri=decode_original_world_triangles(raw);assert len(tri)==model['triangles'];projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
  gaprow=next(r for r in inputs['gaps.json.gz']['rows']if r['uid']=='landsd/253980:0');gap=shapely.from_wkt(gaprow['exteriorMismatchWKT']);podium=shapely.from_wkt(inputs['projection.json.gz']['coveredWKT']);covered=gap.intersection(projection);residual=gap.difference(podium.union(projection))
  summary=dict(uids=['landsd/253980:0','landsd/255260:0'],sourceSHA256=gaprow['sourceSHA256'],companionSourceSHA256=SHA,companionTriangles=len(tri),exteriorGapAreaM2=gap.area,companionExactProjectionCoversM2=covered.area,podiumAndCompanionCoverM2=gap.area-residual.area,remainingGapM2=residual.area,sourceGeometryChanges=0,installationApproved=False,identityAccepted=False,qualification='Exact original projection diagnostic only. Neighbour projection does not establish ownership, support or identity approval.')
  save(DOC/'projection.json.gz',dict(**summary,companionProjectionWKT=projection.wkt,coveredGapWKT=covered.wkt,residualGapWKT=residual.wkt,companion=dict(uid='landsd/255260:0',assetPath=str(asset.relative_to(ROOT)),candidate=model['candidate'])))
  assert reservations.owns(lease);refs.append(HERE/'exact_packed_world_geometry_20261009.py');receipt=module('parkview14_companion_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-companion-projection',refs,summary);print(dict(summary,jobId=receipt['jobId']),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
