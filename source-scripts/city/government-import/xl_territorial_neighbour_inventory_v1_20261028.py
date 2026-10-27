"""One metadata-only territorial neighbour pass for every unfinished fixed XL key.

No source processing, queues, installation decisions or current-scene approvals.
Null viewer UIDs and unknown native bounds are retained explicitly.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN,Jsonb
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-unfinished-territorial-neighbour-inventory-v1-20261028'
INVENTORY='government-xl-after-ocean-four-unfinished-exact-source-inventory-v1-20261027'
def main():
 out=BASE/BATCH;assert not out.exists();_,pins=authenticate(BASE/INVENTORY);path=BASE/INVENTORY/'summary.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];inventory=read(path);rows=inventory['rows'];assert len(rows)==126 and len({r['sourceKey']for r in rows})==126 and sum(r['uid']is None for r in rows)==2
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  targets=[]
  for row in rows:
   key,mid=row['sourceKey'].split('/',1);record=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert record and record[0]==row['nativeResultSHA256'];model=next(m for m in record[1]['models']if m['modelId']==mid);assert (model.get('candidate')or model['asset'])['sha256']==row['indexedSourceSHA256'];targets.append(dict(**row,worldBounds=model.get('worldBounds')))
  totals=db.execute("SELECT count(*),count(r.cache_key),sum(jsonb_array_length(r.result->'models')) FROM astra_modelling.native_stage_members s LEFT JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE s.run_id=%s",(NATIVE_RUN,)).fetchone();assert totals[0]==totals[1]
  matches=db.execute("""WITH targets AS (SELECT t FROM jsonb_array_elements(%s::jsonb) t),
  units AS MATERIALIZED (SELECT i.sheet,r.cache_key,r.result_sha,n FROM astra_modelling.native_stage_members s JOIN astra_modelling.native_stage_results r USING(cache_key) JOIN astra_modelling.native_stage_inputs i USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') n WHERE s.run_id=%s)
  SELECT t->>'sourceKey',sheet,cache_key,result_sha,n->>'modelId',n->'candidate'->>'uid',coalesce(n->'candidate'->>'sha256',n->'asset'->>'sha256'),n->'worldBounds'
  FROM targets CROSS JOIN units
  WHERE jsonb_typeof(t->'worldBounds')='array' AND jsonb_typeof(n->'worldBounds')='array'
  AND cache_key||'/'||(n->>'modelId')<>t->>'sourceKey'
  AND(n->'worldBounds'->0->>0)::double precision<=(t->'worldBounds'->1->>0)::double precision+2
  AND(n->'worldBounds'->1->>0)::double precision>=(t->'worldBounds'->0->>0)::double precision-2
  AND(n->'worldBounds'->0->>2)::double precision<=(t->'worldBounds'->1->>2)::double precision+2
  AND(n->'worldBounds'->1->>2)::double precision>=(t->'worldBounds'->0->>2)::double precision-2
  ORDER BY t->>'sourceKey',sheet,n->>'modelId'""",(Jsonb(targets),NATIVE_RUN)).fetchall()
  unknown=db.execute("""SELECT i.sheet,count(*) FROM astra_modelling.native_stage_members s JOIN astra_modelling.native_stage_results r USING(cache_key) JOIN astra_modelling.native_stage_inputs i USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') n WHERE s.run_id=%s AND jsonb_typeof(n->'worldBounds')IS DISTINCT FROM'array' GROUP BY i.sheet ORDER BY i.sheet""",(NATIVE_RUN,)).fetchall()
 groups={r['sourceKey']:[]for r in targets}
 for key,sheet,cache,sha,mid,uid,asset,bounds in matches:groups[key].append(dict(sourceKey=cache+'/'+mid,sheet=sheet,nativeResultSHA256=sha,uid=uid,indexedSourceSHA256=asset,worldBounds=bounds))
 result=dict(uids=sorted(r['uid']for r in targets if r['uid']),fixedXLTotal=521,unfinishedSourceKeys=126,unmatchedViewerUIDs=2,nativeRun=NATIVE_RUN,preparedSheets=totals[1],nativeUnitsScanned=totals[2],paddingM=2,unknownBoundsBySheet=[dict(sheet=s,models=n)for s,n in unknown],rows=[dict(**r,nearbyOriginalCandidates=groups[r['sourceKey']],candidateCount=len(groups[r['sourceKey']]))for r in targets],qualification='Source metadata nomination only, no Y filter. All126 exact unfinished keys retained including both null viewerUIDs. Unknown bounds are not excluded by absence of a match. Active North publication does not transfer current scene approval. No source geometry, acceptance state, permanent rejection or installation credit changed.')
 save(out/'summary.json',result);module('xl_territorial_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-unfinished-xl-territorial-original-neighbour-metadata',[Path(__file__),BASE/INVENTORY/'result.json',path],result);print(dict(targets=len(targets),nativeUnits=totals[2],nominations=len(matches)),flush=True)
if __name__=='__main__':main()
