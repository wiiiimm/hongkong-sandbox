"""Restore exact original clubhouse from a hash-verified existing source bundle."""
import os,sys,uuid,tarfile
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-inone-clubhouse-restore-v1-20261022';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def main():
 assert not DOC.exists()
 prior=BASE/'government-xl-inone-adjoining-sources-v1-20261022';_,pins=authenticate(prior);p=prior/'sources.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 row=next(r for r in read(p)['rows']if r['model']['modelId']=='B369231905501063C0');m=row['model'];uid=m['candidate']['uid'];assert uid=='landsd/277974:0'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');sha,result=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['cacheKey'],)).fetchone();assert sha==row['resultSha']and m in result['models']
 artifacts=[a for a in result['artifacts']if a['kind']=='original-and-prepared-sheet'];assert len(artifacts)==1
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+uid],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  sys.path.insert(0,str(HERE.parent/'landmark-resume'));sys.path.insert(0,str(HERE.parent/'citywide-native'))
  from r2_snapshot import R2Store,verify_object
  from source_cache import validate_artifact
  from dotenv import dotenv_values
  for k,v in dotenv_values(ROOT/'.env.modelling').items():
   if k.startswith('R2_')and v and v!='[SENSITIVE]':os.environ.setdefault(k,v)
  artifact=validate_artifact(artifacts[0]);bundle=LOCAL/(artifact['sha256']+'.tar.gz');LOCAL.mkdir(parents=True,exist_ok=True)
  verify_object(R2Store('hk-sandbox-assets'),artifact['key'],artifact['sha256'],artifact['bytes'],bundle);assert digest(bundle.read_bytes())==artifact['sha256']
  assetsha=m['asset']['sha256']
  with tarfile.open(bundle,'r:gz')as tar:
   entries=[e for e in tar if Path(e.name).name==assetsha+'.glb.gz'];assert len(entries)==1 and entries[0].isfile();raw=tar.extractfile(entries[0]).read()
  assert digest(raw)==assetsha and len(raw)==m['asset']['bytes'];out=LOCAL/(assetsha+'.glb.gz');out.write_bytes(raw);t=decode_original_world_triangles(raw);assert len(t)==m['triangles']and reservations.owns(lease)
  summary=dict(uids=[uid],restoredOriginals=1,sourceSHA256=assetsha,modelId=m['modelId'],triangles=len(t),assetPath=str(out.relative_to(ROOT)),native=row,artifact=artifact,worldBounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],installationApproved=False,modelGeometryChanges=0)
  save(DOC/'restored.json',summary)
  module('inone_restore_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-clubhouse-component-restoration',[Path(__file__),p,prior/'result.json',bundle,out,HERE/'exact_packed_world_geometry_20261009.py'],summary)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
