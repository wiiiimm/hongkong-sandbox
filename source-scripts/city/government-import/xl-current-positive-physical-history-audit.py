"""Read all Neon positive placement flags for current uninstalled XL originals.

Check both top-level results and embedded batch rows. Never assumes an identity,
loader or diagnostic pass is full physical/publication acceptance.
"""
import json,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,jobs,reservations,Jsonb,dict_row
BATCH='government-xl-current-positive-physical-history-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
SOURCE=ROOT/'docs/astra-city/government-import/government-xl-current-320-blocker-families-20261009/dispositions.json.gz'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists(),'Fresh audit only'
 source=read(SOURCE);rows=source['rows'];assert len(rows)==320
 sha={r['uid']:r['sourceSHA256'] for r in rows if r['uid']};uids=sorted(sha)
 manifest=ROOT/'3d-viewer/city/data/manifest.json'
 assert digest(manifest.read_bytes())==source['manifestSHA256']
 top_sql="""SELECT id,batch,stage,result->'uids',result->>'uid',result->'sourceSHA256s',result->>'sourceSHA256',result->>'scriptChecksPassed',result->>'installationApproved',result->>'placementChecksPassed' FROM astra_modelling.jobs WHERE status='complete' AND (result->>'scriptChecksPassed'='true' OR result->>'installationApproved'='true' OR result->>'placementChecksPassed'='true') AND (result->>'uid'=ANY(%s) OR result->'uids' ?| %s)"""
 embedded_sql="""SELECT j.id,j.batch,j.stage,x->>'uid',x->>'sourceSHA256',x->>'scriptChecksPassed',x->>'installationApproved',x->>'placementChecksPassed' FROM astra_modelling.jobs j CROSS JOIN LATERAL jsonb_array_elements(CASE WHEN jsonb_typeof(j.result->'rows')='array' THEN j.result->'rows' ELSE '[]'::jsonb END) x WHERE j.status='complete' AND j.batch LIKE 'government-xl-%%' AND x->>'uid'=ANY(%s) AND (x->>'scriptChecksPassed'='true' OR x->>'installationApproved'='true' OR x->>'placementChecksPassed'='true')"""
 with connect() as c:
  c.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
  top=c.execute(top_sql,(uids,uids)).fetchall();embedded=c.execute(embedded_sql,(uids,)).fetchall()
  active=c.execute("SELECT id,batch,stage,status FROM astra_modelling.jobs WHERE batch LIKE 'government-xl-%%' AND status IN ('pending','running')").fetchall()
 positives=[]
 for j,b,st,us,u,ss,s,sc,ia,pc in top:
  targets=[x for x in (us or [u]) if x in sha and ((ss or {}).get(x)==sha[x] or (x==u and s==sha[x]))]
  if targets:positives.append({'jobId':j,'batch':b,'stage':st,'uids':targets,'scriptChecksPassed':sc,'installationApproved':ia,'placementChecksPassed':pc})
 for j,b,st,u,s,sc,ia,pc in embedded:
  if sha[u]==s:positives.append({'jobId':j,'batch':b,'stage':st,'uid':u,'sourceSHA256':s,'scriptChecksPassed':sc,'installationApproved':ia,'placementChecksPassed':pc})
 assert not active,active
 # A nonempty frontier is saved truthfully and requires investigation; it is
 # never discarded merely because a later report calls the source held.
 save(DOC/'positive-frontier.json',{'rows':positives,'topLevelRawMatches':len(top),'embeddedRawMatches':len(embedded),'activeWorkers':active,'sourceScope':320,'uidScope':len(uids),'unmatchedSourceIdentities':320-len(uids),'manifestSHA256':source['manifestSHA256'],'snapshotId':source['snapshotId'],'topLevelSQL':top_sql,'embeddedSQL':embedded_sql,'qualification':'Historical database query for three positive physical/placement/publication flags only. A positive result would need all current input, foundation, neighbour, browser and publication gates; query absence is not permanent impossibility.'})
 refs=[ref(p) for p in [SOURCE,Path(__file__),manifest,DOC/'positive-frontier.json']]
 claim=reservations.claim('codex-xl-positive-history-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation'];job=None
 try:
  payload={'sourceKeys':[r['sourceKey'] for r in rows],'evidenceRefs':refs};stage='current-uninstalled-xl-positive-physical-history-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'positiveResults':len(positives),'topLevelRawMatches':len(top),'embeddedRawMatches':len(embedded),'sourceScope':320,'activeWorkers':0,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'aiGeometryModelling':False,'manifestSHA256':source['manifestSHA256'],'snapshotId':source['snapshotId']}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for item in refs:assert ref(ROOT/item['path'])==item
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'positiveResults':len(positives),'remainingSources':320}),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
