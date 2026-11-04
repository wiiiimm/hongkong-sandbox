"""Search every indexed source sheet for support at canonical unresolved positions."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-olympian-two-canonical-contacts-v1-20261018';BATCH='government-xl-olympian-two-spatial-support-lookup-v2-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};points=[]
 for row in read(PRIOR/'support-checks.json.gz')['rows']:
  for s in row['unresolved']:
   if s['reason']!='support-above-rim':points.append(dict(uid=row['uid'],point=s['position'],reason=s['reason']))
 excluded={'B347211975601063C0','B347661977401063C0','B348101979201063C0','B348541981101063C0','B347881979902063C1','B348241969002063C0'};hits=[];count=0
 x0=min(s['point'][0]for s in points)-1;x1=max(s['point'][0]for s in points)+1;z0=min(s['point'][2]for s in points)-1;z1=max(s['point'][2]for s in points)+1
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  records=c.execute("""SELECT i.cache_key,i.sheet,r.result_sha,m.value FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') m WHERE i.stage='native-prepare' AND (m.value#>>'{worldBounds,0,0}')::double precision<=%s AND (m.value#>>'{worldBounds,1,0}')::double precision>=%s AND (m.value#>>'{worldBounds,0,2}')::double precision<=%s AND (m.value#>>'{worldBounds,1,2}')::double precision>=%s""",(x1,x0,z1,z0)).fetchall()
  for key,sheet,sha,m in records:
   count+=1;box=m.get('worldBounds');
   if not box or m['modelId']in excluded:continue
   a,b=box;matches=[i for i,s in enumerate(points)if a[0]-.1<=s['point'][0]<=b[0]+.1 and a[2]-.1<=s['point'][2]<=b[2]+.1 and a[1]<=s['point'][1]+.1 and b[1]>=s['point'][1]-1]
   if matches:hits.append(dict(cacheKey=key,sheet=sheet,resultSHA256=sha,model=m,failedPointIndexes=matches))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 save(DOC/'nominations.json',dict(points=points,scannedSpatialMatches=count,models=hits,fullAcceptance=False,qualification='All indexed native-prepare sheets; AABB nomination only, not full government inventory. Canonical failed edge and vertex points, existing one metre upper contact tolerance. No support or identity approval.'))
 summary=[dict(modelId=x['model']['modelId'],sheet=x['sheet'],bounds=x['model'].get('worldBounds'),candidate=x['model'].get('candidate',{}).get('uid'),label=x['model'].get('candidate',{}).get('label'),failedPoints=len(x['failedPointIndexes']))for x in hits];save(DOC/'summary.json',dict(rows=summary));out=module('olympian_spatial_lookup_freeze_v2',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-all-indexed-sheets-canonical-support-nominations-v2',[Path(__file__),PRIOR/'result.json',*[ROOT/p for p in pins]],dict(uids=['landsd/265851:0'],nominations=len(hits),fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],scannedSpatialMatches=count,rows=summary),flush=True)
if __name__=='__main__':main()
