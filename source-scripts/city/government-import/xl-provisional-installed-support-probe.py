"""Probe five exact provisional XL originals against already installed supports.

Bounding-box matches are lookup only. Full unchanged-source interface checks decide
compatibility; this phase grants no acceptance, publication or installation credit.
"""
import argparse,json,subprocess,sys,time,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,dict_row,Jsonb,NATIVE_RUN
from provisional_original_review import verify
PAIRS={
 'landsd/204143:0':'landsd/273061:0','landsd/204145:0':'landsd/273061:0',
 'landsd/78828:0':'landsd/283035:0','landsd/78915:0':'landsd/283035:0',
 'landsd/79318:0':'landsd/224399:0'}
BASE=ROOT/'docs/astra-city/government-import/government-xl-twelve-provisional-original-inputs-20261007'
BATCH='government-xl-five-provisional-installed-supports-20261007'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
AFTER=ROOT/'docs/astra-city/government-import/government-xl-provisional-physical-sequence-20261007/commands.json'

def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 rows={r['uid']:r for r in read(BASE/'check-selection.json.gz')['rows'] if r['uid'] in PAIRS}
 assert len(rows)==len(PAIRS)
 manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=digest(manifest_path.read_bytes());manifest=read(manifest_path)
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path)
 refs={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [manifest_path,pointer_path,BASE/'check-selection.json.gz',BASE/'context.json.gz',Path(__file__),HERE/'provisional_original_review.py',HERE/'test_provisional_original_review.py']}
 sources=dict(rows);expected={}
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY')
  for uid,row in rows.items():
   verify(con,uid,row['sourceSHA256'],row['currentReview'])
   actual=con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()
   assert actual==(row['native']['resultSha'],)
  for uid in sorted(set(PAIRS.values())):
   matches=[]
   for url in manifest['officialModelCatalogues']:
    path=ROOT/'3d-viewer'/url;cat=read(path)
    for entry in cat['models']:
     if entry['uid']==uid:matches.append((entry,cat,path))
   assert len(matches)==1;entry,cat,path=matches[0]
   assert entry['publicationApproved'] and entry['sourceIdentityReviewed']
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
   sources[uid]=source;expected[uid]=entry['sha256']
   for p in [path,asset,ROOT/'3d-viewer'/forms[0]['tile']]:refs[str(p.relative_to(ROOT))]=digest(p.read_bytes())
 save(DOC/'support-inputs.json',{'pairs':[{'uid':u,'supportUid':s} for u,s in PAIRS.items()],'sources':list(sources.values())})
 subprocess.run(['node',str(HERE/'original-support-closure-interfaces.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
 checks=read(DOC/'support-checks.json.gz');assert {r['uid'] for r in checks['rows']}==set(PAIRS)
 refs.update(checks['inputHashes'])
 for p in [DOC/'support-inputs.json',DOC/'support-checks.json.gz']:refs[str(p.relative_to(ROOT))]=digest(p.read_bytes())
 for path,sha in refs.items():assert digest((ROOT/path).read_bytes())==sha
 assert reservations.owns(lease) and read(pointer_path)==pointer
 payload={'evidenceRefs':[{'path':p,'sha256':s} for p,s in sorted(refs.items())],'uids':list(PAIRS)}
 stage='exact-current-provisional-installed-support-interface-v1';jobid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jobid
 result={**payload,'jobId':jobid,'batch':BATCH,'rows':checks['rows'],'passedInterfaces':sum(r['interface']['passed'] for r in checks['rows']),
  'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'activeWorkers':0,'queuedFollowups':0}
 with connect() as con:
  con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
  for uid,row in rows.items():verify(con,uid,row['sourceSHA256'],row['currentReview'])
  for uid,sha in expected.items():assert con.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(pointer['snapshotId'],uid)).fetchone()==('installed-verified',sha)
  con.row_factory=dict_row;assert reservations._current(con,lease)
  assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jobid,job['owner'],job['token'])).rowcount==1
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()[0]==result
 save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jobid,'resultVerified':True})
 print(json.dumps({'jobId':jobid,'interfacesPassed':result['passedInterfaces'],'checked':len(PAIRS),'newlyInstalled':0,'neonVerified':True}),flush=True)

def main():
 if '--owned' in sys.argv:owned();return
 assert not DOC.exists(),'Fresh explicit probe only'
 while not AFTER.exists():time.sleep(10)
 assert read(AFTER)['activeWorkers']==read(AFTER)['queuedFollowups']==0
 claim=reservations.claim('codex-xl-provisional-supports-'+str(uuid.uuid4()),['building:'+u for u in sorted(set(PAIRS)|set(PAIRS.values()))],batch=BATCH);assert claim['ok'],claim
 save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
