"""Recover local receipt only after exact read-only verification of a completed job.

No job is enqueued, rerun, mutated or accepted by this utility.
"""
import argparse
from run import ROOT,read,save,digest,connect

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--stage',required=True);a=p.parse_args()
 assert a.batch.startswith('government-xl-')and '/'not in a.batch
 out=ROOT/'docs/astra-city/government-import'/a.batch;assert not(out/'result.json').exists()
 summary=read(out/'summary.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  rows=db.execute('SELECT id,status,result,owner,token,lease_until FROM astra_modelling.jobs WHERE batch=%s AND stage=%s',(a.batch,a.stage)).fetchall()
  assert len(rows)==1
  jid,status,result,owner,token,lease=rows[0]
  assert status=='complete'and owner is None and token is None and lease is None
  assert result['jobId']==jid and result['batch']==a.batch and result['stage']==a.stage
  assert all(result[k]==v for k,v in summary.items()),'Database result does not match the saved JSON-native summary'
  for ref in result['evidenceRefs']:
   path=(ROOT/ref['path']).resolve();assert path.is_relative_to(ROOT.resolve())and digest(path.read_bytes())==ref['sha256']
 save(out/'result.json',result)
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',read(out/'result.json'))
 save(out/'neon-sync.json',dict(jobId=jid,resultVerified=True,localReceiptRecoveredFromExactCompletedReadback=True,noDatabaseWrites=True))
 print(dict(jobId=jid,resultVerified=True,completeEvidenceRefsVerified=len(result['evidenceRefs']),databaseWrites=0),flush=True)

if __name__=='__main__':main()
