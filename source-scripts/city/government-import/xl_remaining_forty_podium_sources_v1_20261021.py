"""Locate immutable original podium stages; no source acceptance or publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,connect,NATIVE_RUN
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-remaining-forty-podium-sources-v1-20261021';DOC=ROOT/'docs/astra-city/government-import'/BATCH
uids=['landsd/203884:0', 'landsd/23296:0', 'landsd/233771:0', 'landsd/235018:0', 'landsd/258737:0', 'landsd/259604:0', 'landsd/277890:0', 'landsd/290878:0', 'landsd/292042:0']
assert not DOC.exists()
with connect() as db:
 db.execute('SET TRANSACTION READ ONLY')
 rows=db.execute("""SELECT r.cache_key,r.result_sha,m.value
 FROM astra_modelling.native_stage_results r
 JOIN astra_modelling.native_stage_members n USING(cache_key)
 CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') m(value)
 WHERE n.run_id=%s AND (m.value->'candidate'->>'uid'=ANY(%s)
 OR EXISTS(SELECT 1 FROM jsonb_array_elements(COALESCE(m.value->'matching'->'viewerMatches','[]'::jsonb)) v WHERE v->>'uid'=ANY(%s)))""",(NATIVE_RUN,uids,uids)).fetchall()
result=[dict(cacheKey=key,resultSha=sha,model=model)for key,sha,model in rows]
save(DOC/'sources.json.gz',dict(requestedUids=uids,nativeRun=NATIVE_RUN,rows=result,installationApproved=False))
summary=dict(uids=uids,matchedSourceCount=len(rows),models=[dict(modelId=r['model']['modelId'],triangles=r['model']['triangles'],assetSHA256=r['model']['asset']['sha256'])for r in result],installationApproved=False,newlyInstalled=0)
module('next_twenty_podium_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'missing-original-podium-stage-discovery',[Path(__file__),HERE/'run.py'],summary);print(summary,flush=True)
