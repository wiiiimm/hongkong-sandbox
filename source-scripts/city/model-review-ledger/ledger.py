"""Source-accounted model review state on the pinned Neon branch.
Review results are fenced by the same live source reservation as the worker.
"""
import argparse, hashlib, json, sys, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'))
from db import connect
import reservations
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

SCHEMA='''
CREATE TABLE IF NOT EXISTS astra_modelling.model_reviews (
 snapshot_id text NOT NULL, uid text NOT NULL, name text, landmark_ids jsonb NOT NULL,
 source_state text NOT NULL, source_sha256 text, initial_evidence jsonb NOT NULL,
 review_state text NOT NULL DEFAULT 'pending', result jsonb,
 updated_at timestamptz NOT NULL DEFAULT clock_timestamp(), PRIMARY KEY(snapshot_id,uid));
CREATE TABLE IF NOT EXISTS astra_modelling.model_review_events (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 snapshot_id text NOT NULL, uid text NOT NULL, owner text NOT NULL, token uuid NOT NULL,
 review_state text NOT NULL, result jsonb NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp());
CREATE OR REPLACE VIEW astra_modelling.model_review_status AS
 SELECT m.*, CASE WHEN m.review_state='pending' AND g.released_at IS NULL
 AND g.lease_until>clock_timestamp() THEN 'in-progress' ELSE m.review_state END AS work_status,
 CASE WHEN g.released_at IS NULL AND g.lease_until>clock_timestamp() THEN g.owner END AS active_owner,
 g.lease_until FROM astra_modelling.model_reviews m
 LEFT JOIN astra_modelling.reservations r ON r.resource='building:'||m.uid
 LEFT JOIN astra_modelling.reservation_groups g ON g.token=r.token;
'''
EFFORT_SCHEMA = """
ALTER TABLE astra_modelling.model_review_events ADD COLUMN IF NOT EXISTS effort jsonb NOT NULL DEFAULT '{"method":"unknown","ai_model":null,"reasoning_effort":"unknown"}'::jsonb;
ALTER TABLE astra_modelling.model_review_events ADD COLUMN IF NOT EXISTS request_id text;
CREATE UNIQUE INDEX IF NOT EXISTS model_review_request_uid ON astra_modelling.model_review_events(request_id,uid) WHERE request_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS model_review_uid_history ON astra_modelling.model_review_events(uid,id);
"""
SCHEMA += EFFORT_SCHEMA
METHODS={'unknown','scripted','lightweight','detailed','manual'}
REASONING={'unknown','none','minimal','low','medium','high','xhigh','max','ultra','not-applicable'}
def effort_metadata(value=None):
 value=dict(value or {})
 allowed={'method','ai_model','reasoning_effort','run_id','job_id','issue','input_tokens','output_tokens','duration_seconds','output_ref'}
 if set(value)-allowed:raise ValueError('Unsupported effort metadata field')
 result={'method':'unknown','ai_model':None,'reasoning_effort':'unknown',**value}
 if result['method'] not in METHODS or result['reasoning_effort'] not in REASONING:raise ValueError('Unsupported modelling method or reasoning effort')
 for key in ('input_tokens','output_tokens','duration_seconds'):
  if key in result and (type(result[key]) is not int or result[key]<0):raise ValueError('Measured usage must be a non-negative integer')
 for key in ('ai_model','run_id','job_id','issue','output_ref'):
  if result.get(key) is not None and (not isinstance(result[key],str) or not result[key].strip()):raise ValueError('Metadata references must be non-empty strings')
 if result['reasoning_effort'] not in ('unknown','not-applicable') and not result['ai_model']:raise ValueError('Known AI effort requires an AI model')
 return result

def migrate_effort():
 with connect() as con:
  con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
  con.execute(EFFORT_SCHEMA)
 return {'effortTracking':'available','historicalEffort':'unknown unless recorded'}

def history(uid):
 with connect() as con:
  con.row_factory=dict_row
  events=con.execute('SELECT id,snapshot_id,uid,owner,review_state,result,effort,created_at FROM astra_modelling.model_review_events WHERE uid=%s ORDER BY id',(uid,)).fetchall()
 return {'uid':uid,'events':events,'qualification':'Review history only; missing effort is unknown, not zero. Script preparation remains in its existing run ledger.'}

STATES={'held','approved-for-integration','installed-verified','source-unavailable','identity-unresolved'}

def seed(report_path, inherit=None):
 report=json.loads(Path(report_path).read_text()); snapshot=report['snapshotId']
 rows=[]
 for p in report['parts']:
  state=p['sourceProgress']; initial='pending' if p['candidate'] else ('existing-detail-unreviewed' if state=='installed' else state)
  rows.append((snapshot,p['uid'],p.get('name'),Jsonb(p['landmarkIds']),state,
   p['candidate']['sha256'] if p['candidate'] else None,
   Jsonb({'classification':p['classification'],'knownHold':p['knownHold'],'objectId':p['objectId']}),initial))
 with connect() as con:
  con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));con.execute(SCHEMA)
  with con.cursor() as cur:
   cur.executemany('''INSERT INTO astra_modelling.model_reviews
    (snapshot_id,uid,name,landmark_ids,source_state,source_sha256,initial_evidence,review_state)
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(snapshot_id,uid) DO NOTHING''',rows)
  if inherit:
   con.execute('''UPDATE astra_modelling.model_reviews n SET review_state=o.review_state,result=o.result
    FROM astra_modelling.model_reviews o WHERE n.snapshot_id=%s AND o.snapshot_id=%s
    AND n.uid=o.uid AND n.source_sha256 IS NOT DISTINCT FROM o.source_sha256
    AND n.source_state=o.source_state AND n.result IS NULL AND o.result IS NOT NULL''',(snapshot,inherit))
  retained=con.execute('SELECT uid,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s',(snapshot,)).fetchall()
  assert dict(retained)=={r[1]:r[5] for r in rows},'Snapshot sources changed; use a new source snapshot'
 return summary(snapshot)

def summary(snapshot):
 with connect() as con:
  states=dict(con.execute('SELECT work_status,count(*) FROM astra_modelling.model_review_status WHERE snapshot_id=%s GROUP BY work_status',(snapshot,)))
  owners=con.execute('SELECT active_owner,count(*) FROM astra_modelling.model_review_status WHERE snapshot_id=%s AND active_owner IS NOT NULL GROUP BY active_owner',(snapshot,)).fetchall()
 return {'snapshot':snapshot,'states':states,'activeOwners':dict(owners),'qualification':'Source parts, not whole landmark readiness. Installed means feature-branch viewer only; not production.'}

def record_many(snapshot, receipt_path, entries, *, effort=None, request_id=None):
 effort=effort_metadata(effort)
 request_id=request_id or str(uuid.uuid4())
 if not entries:raise ValueError('At least one review entry is required')
 prepared=[]
 for entry in entries:
  uid,state,evidence_path,observation,commit=entry
  if state not in STATES:raise ValueError('Unsupported review state')
  evidence=Path(evidence_path).resolve()
  if not evidence.is_relative_to(ROOT) or not evidence.is_file():raise ValueError('Evidence must be a repository file')
  if not observation.strip():raise ValueError('A source-aware review observation is required')
  result={'evidence':str(evidence.relative_to(ROOT)),'sha256':hashlib.sha256(evidence.read_bytes()).hexdigest(),
   'observation':observation,'commit':commit,'productionPublished':False,'wholeLandmarkComplete':False,'effort':effort}
  prepared.append((uid,state,result))
 uids=[p[0] for p in prepared]
 if len(set(uids))!=len(uids):raise ValueError('Duplicate source review entry')
 receipt=json.loads(Path(receipt_path).read_text())
 with connect() as con:
  con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
  group=reservations._current(con,receipt)
  if not group or not {'building:'+uid for uid in uids}<=set(group['resources']):raise ValueError('Live matching source reservation required')
  rows=con.execute('SELECT uid,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s) FOR UPDATE',(snapshot,uids)).fetchall()
  sources={r['uid']:r['source_sha256'] for r in rows}
  if set(sources)!=set(uids):raise ValueError('Unplanned model source')
  for uid,state,_ in prepared:
   if state in ('approved-for-integration','installed-verified') and not sources[uid]:raise ValueError('No prepared source asset for integration')
  existing=con.execute('SELECT snapshot_id,uid,review_state,result,effort FROM astra_modelling.model_review_events WHERE request_id=%s',(request_id,)).fetchall()
  for uid,state,result in prepared:result['source_sha256']=sources[uid]
  if existing:
   expected={uid:(snapshot,state,result,effort) for uid,state,result in prepared}
   actual={r['uid']:(r['snapshot_id'],r['review_state'],r['result'],r['effort']) for r in existing}
   if actual!=expected:raise ValueError('Request ID already used with different review data')
   return [{'uid':uid,'state':state,'recorded':True,'reused':True} for uid,state,_ in prepared]
  with con.cursor() as cur:
   cur.executemany('UPDATE astra_modelling.model_reviews SET review_state=%s,result=%s,updated_at=clock_timestamp() WHERE snapshot_id=%s AND uid=%s',[(state,Jsonb(result),snapshot,uid) for uid,state,result in prepared])
   cur.executemany('INSERT INTO astra_modelling.model_review_events(snapshot_id,uid,owner,token,review_state,result,effort,request_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',[(snapshot,uid,group['owner'],group['token'],state,Jsonb(result),Jsonb(effort),request_id) for uid,state,result in prepared])
 return [{'uid':uid,'state':state,'recorded':True} for uid,state,_ in prepared]

def record(snapshot, receipt_path, uid, state, evidence_path, observation, commit=None, *, effort=None, request_id=None):
 return record_many(snapshot,receipt_path,[(uid,state,evidence_path,observation,commit)],effort=effort,request_id=request_id)[0]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['seed','status','record','history','migrate-effort']);p.add_argument('--snapshot',default=json.loads((ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json').read_text())['snapshotId']);p.add_argument('--inherit',help='Explicit prior review snapshot; inherit decisions only for unchanged UID, source state and SHA');p.add_argument('--report',default=str(ROOT/'docs/astra-city/landmark-preflight/report.json'));p.add_argument('--receipt');p.add_argument('--uid');p.add_argument('--state',choices=sorted(STATES));p.add_argument('--evidence');p.add_argument('--observation');p.add_argument('--commit');p.add_argument('--effort-json',help='Private or repository JSON metadata file');p.add_argument('--request-id',help='Stable ID for safe retries');a=p.parse_args()
 if a.command=='migrate-effort':result=migrate_effort()
 elif a.command=='history':
  if not a.uid:p.error('history requires uid')
  result=history(a.uid)
 elif a.command=='seed':result=seed(a.report,a.inherit)
 elif a.command=='status':result=summary(a.snapshot)
 else:
  if not all((a.receipt,a.uid,a.state,a.evidence,a.observation)):p.error('record requires receipt, uid, state, evidence and observation')
  result=record(a.snapshot,a.receipt,a.uid,a.state,a.evidence,a.observation,a.commit,effort=json.loads(Path(a.effort_json).read_text()) if a.effort_json else None,request_id=a.request_id)
 print(json.dumps(result,default=str,indent=2))
if __name__=='__main__':main()
