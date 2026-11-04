"""Nominate nearby original supports for the exact failed source points; no acceptance."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-olympian-two-original-tower-contacts-v1-20261018';BATCH='government-xl-olympian-two-spatial-support-lookup-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};points=[]
 for row in read(PRIOR/'summary.json')['rows']:
  for s in read(PRIOR/(row['uid'].split('/')[1]+'-samples.json.gz'))['points']:
   if s['gap']is None or s['gap']>.1:points.append(dict(uid=row['uid'],point=s['point']))
 excluded={'B347211975601063C0','B347661977401063C0','B348101979201063C0','B348541981101063C0','B347881979902063C1'};hits=[];count=0
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for key,sheet,sha,result in c.execute("SELECT i.cache_key,i.sheet,r.result_sha,r.result FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.stage='native-prepare' AND i.sheet IN ('11-NW-19A','11-NW-19C')").fetchall():
   for m in result.get('models',[]):
    count+=1;box=m.get('worldBounds')or m.get('candidate',{}).get('worldBounds')
    if not box or m['modelId']in excluded:continue
    a,b=box;matches=[i for i,s in enumerate(points)if a[0]-.1<=s['point'][0]<=b[0]+.1 and a[2]-.1<=s['point'][2]<=b[2]+.1 and a[1]<=s['point'][1]+.1 and b[1]>=s['point'][1]-.1]
    if matches:hits.append(dict(cacheKey=key,sheet=sheet,resultSHA256=sha,model=m,failedPointIndexes=matches))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 save(DOC/'nominations.json',dict(points=points,scannedModels=count,models=hits,fullAcceptance=False,qualification='AABB and vertical-height nomination only. No identity/support approval. Existing indexed models on19A/19C; excludes known podium/four towers.'))
 summary=[dict(modelId=x['model']['modelId'],sheet=x['sheet'],bounds=x['model'].get('worldBounds'),candidate=x['model'].get('candidate',{}).get('uid'),label=x['model'].get('candidate',{}).get('label'),failedPoints=len(x['failedPointIndexes']))for x in hits];save(DOC/'summary.json',dict(rows=summary));out=module('olympian_spatial_lookup_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-exact-failed-points-nearby-source-support-nominations-v1',[Path(__file__),PRIOR/'result.json',*[ROOT/p for p in pins]],dict(uids=['landsd/265851:0'],nominations=len(hits),fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],scannedModels=count,rows=summary),flush=True)
if __name__=='__main__':main()
