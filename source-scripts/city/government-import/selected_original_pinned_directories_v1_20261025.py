"""Recover exact historical directory metadata by pinned native source identity."""
import argparse,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','capture']:p.add_argument('--'+k,required=True)
 a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
 assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.capture])and not out.exists()
 _,pins=authenticate(base/a.capture);sp=base/a.capture/'selection.json.gz';assert digest(sp.read_bytes())==pins[str(sp.relative_to(ROOT))]
 selected=read(sp);refs=[Path(__file__),base/a.capture/'result.json',sp];results=[];groups={}
 for r in selected['rows']:groups.setdefault(r['native']['cacheKey'],[]).append(r)
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for key,rows in sorted(groups.items()):
   sheet,source_sha,result_sha=db.execute('SELECT i.sheet,i.source_sha,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s',(key,)).fetchone()
   assert all(r['native']['resultSha']==result_sha and r['native']['sheet']==sheet for r in rows)
   candidates=db.execute("SELECT cache_key,index_sha,result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at",(sheet,)).fetchall();matches=[]
   for directory_key,index_sha,d in candidates:
    if digest(json.dumps([d['sourceURL'],d['etag'],d['directorySHA256']],separators=(',',':')).encode())==source_sha:
     assert d['sheet']==sheet;matches.append(dict(directoryCacheKey=directory_key,indexSHA256=index_sha,directory=d))
   assert matches,(sheet,'Exact historical directory source identity unavailable; do not use newer revision')
   assert len({json.dumps(m['directory'],sort_keys=True)for m in matches})==1
   target=out/(sheet+'-directory.json');save(target,matches[0]['directory'])
   results.append(dict(cacheKey=key,sheet=sheet,sourceSHA256=source_sha,nativeResultSHA256=result_sha,uids=sorted(r['uid']for r in rows),directoryMetadata=matches[0],directoryPath=str(target.relative_to(ROOT)),directorySHA256=digest(target.read_bytes())))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
 result=dict(uids=sorted(r['uid']for r in selected['rows']),rows=results,installationApproved=False,sourceGeometryChanges=0,qualification='Exact historical directory metadata only; computed source identity must equal repository-pinned native_stage_inputs source_sha. Newer revisions never substitute. Recovery/runtime/identity/placement remain separate.')
 save(out/'summary.json',result)
 module('pinned_directories_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-pinned-native-source-directory-metadata',refs,result)
 print([(r['sheet'],r['uids'])for r in results],flush=True)
if __name__=='__main__':main()
