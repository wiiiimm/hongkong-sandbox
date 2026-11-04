"""Fresh exact-original seam diagnostics across saved source/support pairs."""
import json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
BATCH='government-xl-original-contact-seam-batch-20261008';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
EXCLUDED={'landsd/227099:0','landsd/81972:0','landsd/83691:0','landsd/229310:0','landsd/120104:0'}
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def inventory():
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');installed={m['uid'] for u in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/u)['models']};pairs={}
 for path in sorted((ROOT/'docs/astra-city/government-import').glob('*/support-inputs.json')):
  data=read(path)
  if 'sources' not in data or 'pairs' not in data:continue
  src={r['uid']:r for r in data['sources']}
  for pair in data['pairs']:
   a,b=pair['uid'],pair['supportUid']
   if a in installed or {a,b}&EXCLUDED or a not in src or b not in src:continue
   rows=[src[a],src[b]]
   if any(not r.get('candidate',{}).get('path') or not (ROOT/r['candidate']['path']).exists() for r in rows):continue
   key=(a,src[a]['sourceSHA256'],b,src[b]['sourceSHA256']);pairs[key]={'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes()),'pair':pair,'sources':rows}
 return {'pairs':list(pairs.values()),'excludedScope':sorted(EXCLUDED),'publication':False}
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 subprocess.run(['node',str(HERE/'original-contact-seam-batch.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True);assert reservations.owns(lease)
 checks=read(DOC/'checks.json');rows=checks['rows'];refs=[ref(DOC/'inputs.json'),ref(DOC/'checks.json'),ref(Path(__file__))]+[ref(p) for p in sorted((DOC/'pairs').glob('*.json'))]+[{'path':p,'sha256':h} for p,h in checks['inputHashes'].items()];refs=list({r['path']:r for r in refs}.values())
 summary={'pairs':len(rows),'targetUids':len({r['uid'] for r in rows}),'newlyPassingPairs':[{'uid':r['uid'],'supportUid':r['supportUid'],'sourceSHA256':r['sourceSHA256'],'supportSHA256':r['supportSHA256'],'seamCorrections':r['interface']['seamCorrections']} for r in rows if r.get('newlyPasses')],'priorPassingPairs':sum(r.get('rawPassed',False) for r in rows),'errors':sum(bool(r.get('error')) for r in rows)};save(DOC/'summary.json',summary);refs.append(ref(DOC/'summary.json'))
 stage='exact-original-contact-seam-batch-v1';jid=jobs.enqueue(BATCH,stage,summary);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
 result={**summary,'batch':BATCH,'jobId':jid,'evidenceRefs':refs,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'aiGeometryModelling':False,'qualification':'New exact original wall-edge and corner diagnostic only. Raw interface failures preserved. Positive interfaces require fresh identity, complete source/compound foundation, terrain, every neighbour, runtime/browser and guarded publication. No installation or permanent rejection credit.'}
 with connect() as c:
  c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
  for r in refs:assert ref(ROOT/r['path'])==r
  assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
 save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({**summary,'jobId':jid,'neonVerified':True}),flush=True)
def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists() and not LOCAL.exists();inputs=inventory();scope={r['uid'] for p in inputs['pairs'] for r in p['sources']};claim=reservations.claim('codex-exact-seams-'+str(uuid.uuid4()),['building:'+u for u in sorted(scope)],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));save(DOC/'inputs.json',inputs)
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
