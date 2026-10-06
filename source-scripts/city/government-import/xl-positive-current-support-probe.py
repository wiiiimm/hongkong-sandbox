"""Probe four exact unreviewed positive-identity XL originals against already installed supports.

Bounding-box matches are lookup only. Full unchanged-source interface checks decide
compatibility; this phase grants no acceptance, publication or installation credit.
"""
import argparse,json,subprocess,sys,time,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,dict_row,Jsonb,NATIVE_RUN
from government_georef_cell_identity import verify_files
from installed_source_identity import installed_identity
PAIRS={
 'landsd/256319:0':'landsd/254491:0','landsd/256114:0':'landsd/254491:0',
 'landsd/222073:0':'landsd/262871:0','landsd/204141:0':'landsd/273061:0'}
BASES=[ROOT/'docs/astra-city/government-import'/n for n in ['government-xl-sustained-100-inputs-20261006','government-xl-sustained-131-inputs-20261006']]
BATCH='government-xl-four-positive-current-support-receipts-20261007'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH


def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 rows={r['uid']:r for base in BASES for r in read(base/'check-selection.json.gz')['rows'] if r['uid'] in PAIRS}
 contexts={r['uid']:r for base in BASES for r in read(base/'context.json.gz')['rows'] if r['uid'] in PAIRS}
 assert len(rows)==len(PAIRS)
 manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=digest(manifest_path.read_bytes());manifest=read(manifest_path)
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path)
 refs={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [manifest_path,pointer_path,*[base/n for base in BASES for n in ['check-selection.json.gz','context.json.gz']],Path(__file__),HERE/'government_georef_cell_identity.py']}
 sources=dict(rows);expected={};legacy_acceptances=[]
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY')
  for uid,row in rows.items():
   assert row['currentReview'] is None
   assert con.execute('SELECT 1 FROM astra_modelling.model_reviews WHERE uid=%s LIMIT 1',(uid,)).fetchone() is None
   actual=con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()
   assert actual==(row['native']['resultSha'],)
  for uid in sorted(set(PAIRS.values())):
   matches=[]
   for url in manifest['officialModelCatalogues']:
    path=ROOT/'3d-viewer'/url;cat=read(path)
    for entry in cat['models']:
     if entry['uid']==uid:matches.append((entry,cat,path))
   assert len(matches)==1;entry,cat,path=matches[0]
   assert entry['sourceIdentityReviewed'] and entry['identityReviewApproved'] and entry['placementReviewed']
   assert cat['rootTranslation']==[-834500,0,816500] and entry.get('verticalPlacementOffsetHKPD',0)==0
   assert con.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(pointer['snapshotId'],uid)).fetchone()==('installed-verified',entry['sha256'])
   asset=(path.parent/entry['asset']).resolve();assert asset.is_relative_to(ROOT/'3d-viewer') and digest(asset.read_bytes())==entry['sha256']
   forms=[]
   for tile in manifest['tiles']:
    lo,hi=entry['worldBounds'];l,t,r,b=tile['bounds'];x=(lo[0]+hi[0])/2;z=(lo[2]+hi[2])/2
    if l<=x<=r and t<=z<=b:
     tp=ROOT/'3d-viewer'/tile['url'];forms += [{'building':f,'tile':tile['url'],'tileSHA256':digest(tp.read_bytes())} for f in read(tp)['buildings'] if f['uid']==uid]
   assert len(forms)==1
   source={'uid':uid,'sourceSHA256':entry['sha256'],'source':forms[0],
      'candidate':{'path':str(asset.relative_to(ROOT)),'entry':{**entry,'rootTranslation':cat['rootTranslation']}}}
   if not entry['publicationApproved']:
    proof=installed_identity(source,manifest);assert proof and proof['identityAccepted']
    legacy_acceptances.append(proof)
    for evidence in proof['evidenceRefs']:refs[evidence['path']]=evidence['sha256']
    for helper in ['installed_source_identity.py','accepted_source_identity.py']:
     refs[str((HERE/helper).relative_to(ROOT))]=digest((HERE/helper).read_bytes())
   sources[uid]=source;expected[uid]=entry['sha256']
   for p in [path,asset,ROOT/'3d-viewer'/forms[0]['tile']]:refs[str(p.relative_to(ROOT))]=digest(p.read_bytes())
 identities=[]
 for uid,row in rows.items():
  assert digest((ROOT/row['candidate']['path']).read_bytes())==row['sourceSHA256']
  assert digest((ROOT/'3d-viewer'/row['source']['tile']).read_bytes())==row['source']['tileSHA256']
  for tile,sha in contexts[uid]['neighbourTileHashes'].items():assert digest((ROOT/'3d-viewer'/tile).read_bytes())==sha
  positive=verify_files(row,contexts[uid],LOCAL/('identity-'+uid.split('/')[1].replace(':','-')))
  assert positive['passed'],positive['reasons']
  identities.append({'uid':uid,'positive':positive})
 save(DOC/'check-selection.json.gz',{'rows':list(rows.values()),'batch':BATCH,'manifestSHA256':manifest_sha})
 save(DOC/'context.json.gz',{'rows':list(contexts.values())})
 save(DOC/'owned-source-identities.json',{'rows':identities})
 save(DOC/'legacy-installed-identity-reuse.json',{'rows':legacy_acceptances,'publication':False,'qualification':'Retain original publication flags. Exact current installed ledger and original acceptance/form/catalogue bytes verified; identity reuse only, no import approval.'})
 save(DOC/'support-inputs.json',{'pairs':[{'uid':u,'supportUid':s} for u,s in PAIRS.items()],'sources':list(sources.values())})
 subprocess.run(['node',str(HERE/'original-support-closure-interfaces.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
 checks=read(DOC/'support-checks.json.gz');assert {r['uid'] for r in checks['rows']}==set(PAIRS)
 refs.update(checks['inputHashes'])
 for p in [DOC/'support-inputs.json',DOC/'support-checks.json.gz',DOC/'check-selection.json.gz',DOC/'context.json.gz',DOC/'owned-source-identities.json',DOC/'legacy-installed-identity-reuse.json']:refs[str(p.relative_to(ROOT))]=digest(p.read_bytes())
 for path,sha in refs.items():assert digest((ROOT/path).read_bytes())==sha
 assert reservations.owns(lease) and read(pointer_path)==pointer
 payload={'evidenceRefs':[{'path':p,'sha256':s} for p,s in sorted(refs.items())],'uids':list(PAIRS)}
 stage='exact-current-positive-original-support-interface-v1';jobid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jobid
 result={**payload,'jobId':jobid,'batch':BATCH,'rows':checks['rows'],'passedInterfaces':sum(r['interface']['passed'] for r in checks['rows']),
  'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'activeWorkers':0,'queuedFollowups':0}
 with connect() as con:
  con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
  for uid,row in rows.items():
   assert con.execute('SELECT 1 FROM astra_modelling.model_reviews WHERE uid=%s LIMIT 1',(uid,)).fetchone() is None
  for uid,sha in expected.items():assert con.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(pointer['snapshotId'],uid)).fetchone()==('installed-verified',sha)
  con.row_factory=dict_row;assert reservations._current(con,lease)
  assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jobid,job['owner'],job['token'])).rowcount==1
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()[0]==result
 save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jobid,'resultVerified':True})
 print(json.dumps({'jobId':jobid,'interfacesPassed':result['passedInterfaces'],'checked':len(PAIRS),'newlyInstalled':0,'neonVerified':True}),flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):owned()
  return
 assert not DOC.exists(),'Fresh exact installed support probe only'
 claim=reservations.claim('codex-xl-positive-current-supports-'+str(uuid.uuid4()),['building:'+u for u in sorted(set(PAIRS)|set(PAIRS.values()))],batch=BATCH);assert claim['ok'],claim
 save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
