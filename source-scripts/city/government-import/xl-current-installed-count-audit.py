"""Audit the fixed XL source inventory against current runtime bytes and Neon reviews."""
import argparse,json,sys,uuid
from pathlib import Path
from collections import defaultdict
from run import ROOT,HERE,read,save,digest,connect,jobs,reservations,Jsonb,dict_row,NATIVE_RUN

def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--previous',required=True);p.add_argument('--batch',required=True);a=p.parse_args()
 assert Path(a.batch).name==a.batch and a.batch.startswith('government-xl-')
 doc=ROOT/'docs/astra-city/government-import'/a.batch;assert doc.exists() and not (doc/'full-xl-current-count.json').exists()
 old=read(ROOT/a.previous);assert old['nativeRun']==NATIVE_RUN and len(old['rows'])==old['counts']['total']==521
 manifest=ROOT/'3d-viewer/city/data/manifest.json';pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path)
 runtime=defaultdict(list);refs=[ref(ROOT/a.previous),ref(manifest),ref(pointer_path),ref(Path(__file__))]
 for url in read(manifest)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;refs.append(ref(path))
  for m in read(path)['models']:runtime[m['uid']].append((m,path.parent))
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  reviews={u:(s,sha,result) for u,s,sha,result in c.execute('SELECT uid,review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE snapshot_id=%s',(pointer['snapshotId'],)).fetchall()}
 rows=[]
 for prior in old['rows']:
  uid=prior['uid'];row={**prior,'installedVerified':False,'runtimeSourceSHA256':None}
  review=reviews.get(uid)
  if review and review[0]=='installed-verified':
   matches=[(m,folder) for m,folder in runtime[uid] if m['sha256']==review[1]];assert len(matches)==1,(uid,'Current verified source must have unique runtime asset')
   m,folder=matches[0];asset=folder/m['asset'];assert ref(asset)['sha256']==m['sha256'];refs.append(ref(asset))
   if not prior['installedVerified']:
    assert m.get('placementReviewed') and m.get('publicationApproved') and m.get('sourceIdentityReviewed'),uid
   assert m['sha256']==prior['indexedSourceSHA256'] or prior['installedVerified'] and m['sha256']==prior['runtimeSourceSHA256'],(uid,'New credit requires exact indexed bytes')
   row.update(installedVerified=True,runtimeSourceSHA256=m['sha256'])
  assert not prior['installedVerified'] or row['installedVerified'],(uid,'Previously verified source was lost')
  rows.append(row)
 installed=sum(r['installedVerified'] for r in rows)
 count={'counts':{'total':len(rows),'installedVerified':installed,'remaining':len(rows)-installed},'manifestSHA256':ref(manifest)['sha256'],'snapshotId':pointer['snapshotId'],'nativeRun':NATIVE_RUN,'rows':rows,'qualification':'Fixed 521-source XL inventory; installed credit requires current-snapshot installed-verified review, unique matching current runtime entry and verified runtime asset bytes. New installations additionally require explicit publication/identity/placement flags; historical installed reviews retain their actual legacy flag schema without rewriting it. Previously audited byte-identical gzip-header equivalence retains its recorded source binding. Diagnostics, suppressions and auxiliary sources earn no XL installation credit.'}
 claim=reservations.claim('codex-xl-count-'+str(uuid.uuid4()),['source-count-audit:'+a.batch],batch=a.batch);assert claim['ok'],claim;lease=claim['reservation'];job=None
 try:
  refs=list({r['path']:r for r in refs}.values());payload={'count':count,'evidenceRefs':refs};stage='full-xl-current-runtime-neon-count-v1';jid=jobs.enqueue(a.batch,stage,payload);job=jobs.claim(a.batch,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'scriptExternalAICalls':0}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for item in refs:assert ref(ROOT/item['path'])==item
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(doc/'full-xl-current-count.json',count);save(doc/'full-xl-count-neon-sync.json',{'jobId':jid,'resultVerified':True,'counts':count['counts'],'snapshotId':pointer['snapshotId']});print(json.dumps(count['counts']),flush=True)
 except Exception as e:
  if job:jobs.finish(job,error=str(e))
  raise
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
