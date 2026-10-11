"""Read-only fixed XL inventory audit; no queue, acceptance or source edits."""
import json
from pathlib import Path
from collections import Counter
from run import ROOT, read, save, digest, connect, NATIVE_RUN

BATCH='government-xl-current-fixed-inventory-audit-v1-20261012'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
QUERY="""SELECT s.cache_key,s.model_id,s.viewer_uid,s.triangles,s.source_state,
 s.source_hold_reason,s.source_error,s.source_result_sha,r.result_sha,
 x->'asset'->>'sha256',x->>'state',x->'candidate'->>'uid'
 FROM astra_modelling.native_model_sizes s
 JOIN astra_modelling.native_stage_results r USING(cache_key)
 CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') x
 WHERE s.run_id=%s AND s.size_group='xl' AND x->>'modelId'=s.model_id
 ORDER BY s.triangles DESC,s.cache_key,s.model_id"""

def main():
 assert not DOC.exists()
 manifest=ROOT/'3d-viewer/city/data/manifest.json';pins={str(manifest.relative_to(ROOT)):digest(manifest.read_bytes()),str(Path(__file__).relative_to(ROOT)):digest(Path(__file__).read_bytes())};installed={};by_uid={}
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;pins[str(p.relative_to(ROOT))]=digest(p.read_bytes())
  for e in read(p)['models']:
   k=(e['uid'],e['modelId'],e['sha256']);installed.setdefault(k,[]).append(dict(catalogue=str(p.relative_to(ROOT)),entry=e));by_uid.setdefault(e['uid'],[]).append(k)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  db_time=c.execute('SELECT transaction_timestamp()').fetchone()[0].isoformat()
  rows=c.execute(QUERY,(NATIVE_RUN,)).fetchall();assert len(rows)==521 and len({(r[0],r[1])for r in rows})==521
  uids=sorted({r[2]for r in rows if r[2]})
  reviews=c.execute("SELECT DISTINCT ON(uid) uid,name,source_sha256,review_state,result,updated_at FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC,snapshot_id DESC",(uids,)).fetchall()
 latest={r[0]:dict(name=r[1],sourceSHA256=r[2],state=r[3],resultVerbatim=r[4],updatedAt=r[5].isoformat())for r in reviews};out=[]
 for r in rows:
  cache,model,uid,tri,initial_state,hold,error,source_result,current_result,sha,current_state,candidate_uid=r
  assert source_result==current_result and sha and len(sha)==64
  review=latest.get(uid);exact=installed.get((uid,model,sha),[])
  out.append(dict(cacheKey=cache,modelId=model,uid=uid,triangles=tri,sourceSHA256=sha,nativeResultSHA256=current_result,sourceState=initial_state,sourceHoldReason=hold,sourceError=error,currentNativeState=current_state,candidateUID=candidate_uid,
   exactSourcePresentInManifest=bool(exact),exactManifestBindings=exact,
   sameUIDWithDifferentSourcePresent=bool(by_uid.get(uid))and not exact,
   latestReviewVerbatim=review,latestReviewMatchesExactSource=bool(review and review['sourceSHA256']==sha),
   auditDisposition='installed-catalogue-source'if exact else'needs-exact-source-disposition',
   noNewAcceptance=True))
 for p,sha in pins.items():assert digest((ROOT/p).read_bytes())==sha
 counts=dict(Counter(r['auditDisposition']for r in out));remaining=[r for r in out if not r['exactSourcePresentInManifest']]
 report=dict(batch=BATCH,nativeRun=NATIVE_RUN,database=dict(projectId='billowing-surf-67227217',branchId='br-icy-silence-b3wjwz0q',database='neondb',schema='astra_modelling',readOnlyTransactionTimestamp=db_time),inputHashes=pins,query=QUERY,rows=out,totalExactNativeSources=len(out),counts=counts,remainingLatestReviewStates=dict(Counter((r['latestReviewVerbatim']or{}).get('state','no-review')for r in remaining)),remainingSourceStates=dict(Counter(r['currentNativeState']for r in remaining)),queueCreated=False,jobCreated=False,reviewWrites=0,newAcceptance=False,sourceGeometryChanges=0,qualification='Exact catalogue membership audit, not a fresh acceptance proof. Latest UID review is historical context unless its source SHA matches; completed diagnostics and historical reason fields are not installation credit. No permanent rejection inferred.')
 save(DOC/'inventory.json.gz',report);save(DOC/'summary.json',{k:v for k,v in report.items()if k not in ['rows','inputHashes','query']})
 print(json.dumps(dict(counts=counts,remainingLatestReviewStates=report['remainingLatestReviewStates'],remainingSourceStates=report['remainingSourceStates'],output=str((DOC/'inventory.json.gz').relative_to(ROOT))),indent=2),flush=True)

if __name__=='__main__':main()
