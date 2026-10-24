"""Record exact official market component/terrain diagnostics without acceptance."""
from pathlib import Path
import json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
BATCH='government-xl-market-official-group-context-receipt-20261008'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
CONTEXT=ROOT/'docs/astra-city/government-import/government-xl-market-official-group-context-20261008'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 refs=[ref(p) for p in sorted(CONTEXT.iterdir()) if p.is_file()]
 refs += [ref(HERE/f) for f in ['xl-market-official-group-context.py','original-source-clearance-diagnostic.mjs','original-terrain-clearance-diagnostic.mjs','market_complete_source_identity.py']]+[ref(Path(__file__))]
 context=read(CONTEXT/'context.json');assert len(context['rows'])==7
 assert all(r['officialFound'] and r['uniquePolygon'] and r['hausdorffDistanceM']<.002 for r in context['rows'])
 terrain=read(CONTEXT/'complete-original-tin-clearance.json')
 payload={'evidenceRefs':refs,'componentForms':7,'uids':['landsd/113733:0','landsd/138091:0']}
 stage='official-complete-market-source-context-diagnostic-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
 result={**payload,'jobId':jid,'batch':BATCH,'officialContextVerified':True,'completeOriginalTerrainDiagnostic':terrain,'publication':False,'newlyInstalled':0,'sourceIdentityReviewUsedAI':True,'scriptExternalAICalls':0,'modelGeometryChanges':0,'qualification':'Exact active official CSUID component records and original indexed terrain diagnostics. Intermediate primary-sheet-only terrain report is incomplete and superseded by complete indexed sheet coverage. This receipt provides provenance, not physical acceptance or installation credit.'}
 try:
  with connect() as con:
   con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
   for item in refs:assert ref(ROOT/item['path'])==item
   assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as con:
   con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'neonVerified':True}),flush=True)
 except Exception as e:jobs.finish(job,error=str(e));raise
if __name__=='__main__':
 if '--owned' in sys.argv:owned()
 else:
  assert not DOC.exists() and not LOCAL.exists()
  claim=reservations.claim('codex-market-context-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH);assert claim['ok'],claim
  save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
  subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
