"""Source-accounted model review state on the pinned Neon branch.
Review results are fenced by the same live source reservation as the worker.
"""
import argparse, hashlib, json, sys
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
STATES={'held','approved-for-integration','installed-verified','source-unavailable','identity-unresolved'}

def seed(report_path):
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
  retained=con.execute('SELECT uid,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s',(snapshot,)).fetchall()
  assert dict(retained)=={r[1]:r[5] for r in rows},'Snapshot sources changed; use a new source snapshot'
 return summary(snapshot)

def summary(snapshot):
 with connect() as con:
  states=dict(con.execute('SELECT work_status,count(*) FROM astra_modelling.model_review_status WHERE snapshot_id=%s GROUP BY work_status',(snapshot,)))
  owners=con.execute('SELECT active_owner,count(*) FROM astra_modelling.model_review_status WHERE snapshot_id=%s AND active_owner IS NOT NULL GROUP BY active_owner',(snapshot,)).fetchall()
 return {'snapshot':snapshot,'states':states,'activeOwners':dict(owners),'qualification':'Source parts, not whole landmark readiness. Installed means feature-branch viewer only; not production.'}

def record_many(snapshot, receipt_path, entries):
 if not entries:raise ValueError('At least one review entry is required')
 prepared=[]
 for entry in entries:
  uid,state,evidence_path,observation,commit=entry
  if state not in STATES:raise ValueError('Unsupported review state')
  evidence=Path(evidence_path).resolve()
  if not evidence.is_relative_to(ROOT) or not evidence.is_file():raise ValueError('Evidence must be a repository file')
  if not observation.strip():raise ValueError('A source-aware review observation is required')
  result={'evidence':str(evidence.relative_to(ROOT)),'sha256':hashlib.sha256(evidence.read_bytes()).hexdigest(),
   'observation':observation,'commit':commit,'productionPublished':False,'wholeLandmarkComplete':False}
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
  with con.cursor() as cur:
   cur.executemany('UPDATE astra_modelling.model_reviews SET review_state=%s,result=%s,updated_at=clock_timestamp() WHERE snapshot_id=%s AND uid=%s',[(state,Jsonb(result),snapshot,uid) for uid,state,result in prepared])
   cur.executemany('INSERT INTO astra_modelling.model_review_events(snapshot_id,uid,owner,token,review_state,result) VALUES(%s,%s,%s,%s,%s,%s)',[(snapshot,uid,group['owner'],group['token'],state,Jsonb(result)) for uid,state,result in prepared])
 return [{'uid':uid,'state':state,'recorded':True} for uid,state,_ in prepared]

def record(snapshot, receipt_path, uid, state, evidence_path, observation, commit=None):
 return record_many(snapshot,receipt_path,[(uid,state,evidence_path,observation,commit)])[0]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['seed','status','record']);p.add_argument('--snapshot',default='3887f2f23fbad306');p.add_argument('--report',default=str(ROOT/'docs/astra-city/landmark-preflight/report.json'));p.add_argument('--receipt');p.add_argument('--uid');p.add_argument('--state',choices=sorted(STATES));p.add_argument('--evidence');p.add_argument('--observation');p.add_argument('--commit');a=p.parse_args()
 if a.command=='seed':result=seed(a.report)
 elif a.command=='status':result=summary(a.snapshot)
 else:
  if not all((a.receipt,a.uid,a.state,a.evidence,a.observation)):p.error('record requires receipt, uid, state, evidence and observation')
  result=record(a.snapshot,a.receipt,a.uid,a.state,a.evidence,a.observation,a.commit)
 print(json.dumps(result,default=str,indent=2))
if __name__=='__main__':main()
