"""Chunked COPY and atomic existing-job fencing; no writes to model review/geometry tables."""
import hashlib,json,pathlib,sys,uuid
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'shared-modelling'))
from db import connect
from jobs import encode,claim
from psycopg.types.json import Jsonb
STAGE='citywide-source-audit-v1'

def migrate():
 with connect()as con:
  con.execute('SELECT pg_advisory_xact_lock(22120260909)');con.execute((HERE/'schema.sql').read_text())

def register(meta,rows,label,chunk_size=8192):
 if chunk_size<1:raise ValueError('Positive chunk size required')
 rows=sorted(rows,key=lambda r:r['uid'])
 if len({r['uid']for r in rows})!=len(rows)or len(rows)!=meta['buildings']:raise ValueError('Invalid complete source inventory')
 with connect()as con:
  con.execute('SELECT pg_advisory_xact_lock(22120260909)')
  old=con.execute('SELECT plan_sha,expected_count FROM astra_modelling.city_audit_runs WHERE run_id=%s',(meta['runId'],)).fetchone()
  if old:
   if old!=(meta['planSha'],len(rows)):raise ValueError('Run identity conflict')
   con.execute('UPDATE astra_modelling.city_audit_runs SET labels=ARRAY(SELECT DISTINCT unnest(labels||ARRAY[%s])) WHERE run_id=%s',(label,meta['runId']))
  else:
   con.execute('INSERT INTO astra_modelling.city_audit_runs VALUES(%s,%s,%s,%s,%s,%s,clock_timestamp())',(meta['runId'],meta['planSha'],meta['pipelineSha'],len(rows),meta['tiles'],[label]))
   with con.cursor().copy('COPY astra_modelling.city_audit_members(run_id,uid,cache_key,chunk_id) FROM STDIN')as copy:
    for i,r in enumerate(rows):copy.write_row((meta['runId'],r['uid'],r['cacheKey'],i//chunk_size))
  found=con.execute('SELECT m.uid,m.cache_key,m.chunk_id,c.cache_key IS NOT NULL FROM astra_modelling.city_audit_members m LEFT JOIN astra_modelling.city_audit_cache c USING(cache_key) WHERE m.run_id=%s ORDER BY m.uid',(meta['runId'],)).fetchall()
  if len(found)!=len(rows)or any((u,k)!=(r['uid'],r['cacheKey'])for(u,k,_,_),r in zip(found,rows)):raise ValueError('Immutable membership changed')
  cached={u for u,_,_,yes in found if yes};chunks=sorted({ch for _,_,ch,yes in found if not yes});batch='city-audit-'+meta['runId'];jobs=[]
  for ch in chunks:
   payload={'runId':meta['runId'],'chunk':ch,'planSha':meta['planSha']};identity=hashlib.sha256(encode([batch,STAGE,payload]).encode()).hexdigest();jobs.append((identity,batch,STAGE,Jsonb(payload)))
  con.execute('CREATE TEMP TABLE audit_jobs_stage(id text,batch text,stage text,payload jsonb) ON COMMIT DROP')
  with con.cursor().copy('COPY audit_jobs_stage FROM STDIN')as copy:
   for row in jobs:copy.write_row(row)
  con.execute('INSERT INTO astra_modelling.jobs(id,batch,stage,payload) SELECT * FROM audit_jobs_stage ON CONFLICT DO NOTHING')
 return{'cached':cached,'chunks':chunks,'batch':batch,'members':found}

def ownership_arrays(jobs):
 return([j['id']for j in jobs],[j['owner']for j in jobs],[j['token']for j in jobs])

def heartbeat_many(jobs,seconds=300):
 if not jobs:return True
 with connect()as con:
  n=con.execute("UPDATE astra_modelling.jobs j SET lease_until=clock_timestamp()+make_interval(secs=>%s),updated_at=clock_timestamp() FROM unnest(%s::text[],%s::text[],%s::uuid[]) e(id,owner,token) WHERE j.id=e.id AND j.owner=e.owner AND j.token=e.token AND j.status='running' AND j.lease_until>clock_timestamp()",(seconds,*ownership_arrays(jobs))).rowcount
  if n!=len(jobs):raise ValueError('Chunk ownership lost')
 return True

def finish_group(jobs,results):
 # Every owned chunk is locked and fenced in this one bounded COPY transaction.
 if not jobs or len({j['id']for j in jobs})!=len(jobs):raise ValueError('Distinct owned chunks required')
 with connect()as con:
  live=con.execute("SELECT j.id,j.payload FROM astra_modelling.jobs j JOIN unnest(%s::text[],%s::text[],%s::uuid[]) e(id,owner,token) ON j.id=e.id AND j.owner=e.owner AND j.token=e.token WHERE j.status='running' AND j.lease_until>clock_timestamp() FOR UPDATE OF j",ownership_arrays(jobs)).fetchall()
  if len(live)!=len(jobs):raise ValueError('Stale chunk owner')
  runs={p['runId']for _,p in live}
  if len(runs)!=1:raise ValueError('One frozen run per result group')
  run=runs.pop();chunks=[p['chunk']for _,p in live]
  members=con.execute('SELECT uid,cache_key,chunk_id FROM astra_modelling.city_audit_members WHERE run_id=%s AND chunk_id=ANY(%s)',(run,chunks)).fetchall();expected={u:k for u,k,_ in members}
  if any(hashlib.sha256(encode([r['uid'],r['sourceSha'],r['modelSha'],r['pipelineSha'],r['terrainSha']]).encode()).hexdigest()!=r['cacheKey']for r in results):raise ValueError('Result fingerprint mismatch')
  if len({r['uid']for r in results})!=len(results)or any(expected.get(r['uid'])!=r['cacheKey']for r in results):raise ValueError('Result outside frozen chunk')
  con.execute('CREATE TEMP TABLE audit_results_stage (LIKE astra_modelling.city_audit_cache INCLUDING DEFAULTS) ON COMMIT DROP')
  with con.cursor().copy('COPY audit_results_stage(cache_key,uid,source_sha,model_sha,pipeline_sha,terrain_sha,result) FROM STDIN')as copy:
   for r in results:copy.write_row((r['cacheKey'],r['uid'],r['sourceSha'],r['modelSha'],r['pipelineSha'],r['terrainSha'],Jsonb(r['result'])))
  conflict=con.execute('SELECT 1 FROM audit_results_stage n JOIN astra_modelling.city_audit_cache c USING(cache_key) WHERE n.result<>c.result OR n.uid<>c.uid OR n.source_sha<>c.source_sha OR n.model_sha<>c.model_sha OR n.pipeline_sha<>c.pipeline_sha OR n.terrain_sha<>c.terrain_sha LIMIT 1').fetchone()
  if conflict:raise ValueError('Immutable audit result disagreement')
  con.execute('INSERT INTO astra_modelling.city_audit_cache SELECT * FROM audit_results_stage ON CONFLICT DO NOTHING')
  if con.execute('SELECT 1 FROM audit_results_stage n JOIN astra_modelling.city_audit_cache c USING(cache_key) WHERE n.result<>c.result LIMIT 1').fetchone():raise ValueError('Concurrent immutable result disagreement')
  missing=con.execute('SELECT count(*) FROM astra_modelling.city_audit_members m LEFT JOIN astra_modelling.city_audit_cache c USING(cache_key) WHERE m.run_id=%s AND m.chunk_id=ANY(%s) AND c.cache_key IS NULL',(run,chunks)).fetchone()[0]
  if missing:raise ValueError('Incomplete chunk')
  # Final clock check covers each chunk; any stale owner rolls back ALL cache inserts.
  n=con.execute("UPDATE astra_modelling.jobs j SET status='complete',result=jsonb_build_object('stage',%s::text,'complete',true),owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() FROM unnest(%s::text[],%s::text[],%s::uuid[]) e(id,owner,token) WHERE j.id=e.id AND j.owner=e.owner AND j.token=e.token AND j.status='running' AND j.lease_until>clock_timestamp()",(STAGE,*ownership_arrays(jobs))).rowcount
  if n!=len(jobs):raise ValueError('Chunk expired during COPY')
 return len(results)

def finish_chunk(job,results):return finish_group([job],results)

def report(run_id):
 with connect()as con:
  totals=con.execute('SELECT count(*),count(c.cache_key) FROM astra_modelling.city_audit_members m LEFT JOIN astra_modelling.city_audit_cache c USING(cache_key) WHERE run_id=%s',(run_id,)).fetchone()
  flags=dict(con.execute("SELECT flag,count(*) FROM astra_modelling.city_audit_members m JOIN astra_modelling.city_audit_cache c USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements_text(c.result->'flags') flag WHERE m.run_id=%s GROUP BY flag ORDER BY flag",(run_id,)))
  detail=dict(con.execute("SELECT result->>'detail',count(*) FROM astra_modelling.city_audit_members m JOIN astra_modelling.city_audit_cache c USING(cache_key) WHERE run_id=%s GROUP BY 1",(run_id,)))
  terrain=dict(con.execute("SELECT result->'terrain'->>'state',count(*) FROM astra_modelling.city_audit_members m JOIN astra_modelling.city_audit_cache c USING(cache_key) WHERE run_id=%s GROUP BY 1",(run_id,)))
 return{'runId':run_id,'expected':totals[0],'cached':totals[1],'missing':totals[0]-totals[1],'flags':flags,'detail':detail,'terrain':terrain}
