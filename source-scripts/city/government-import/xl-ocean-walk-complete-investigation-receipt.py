"""Save Ocean Walk's complete original-source investigation and explicit revisit conditions."""
import json,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-ocean-walk-complete-investigation-20261008';DOC=BASE/BATCH
FOLDERS=['government-xl-ocean-walk-complete-original-tin-diagnostic-20261008','government-xl-ocean-walk-current-terrain-complete-scope-20261008','government-xl-ocean-walk-original-wall-contact-evidence-20261008','government-xl-ocean-walk-complete-source-local-20261008','government-xl-ocean-walk-six-original-component-closures-20261008','government-xl-ocean-walk-eleven-original-component-closures-20261008']
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();prior=[read(BASE/f/'result.json') for f in FOLDERS]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in prior:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for r in prior:
  for v in r['evidenceRefs']:assert ref(ROOT/v['path'])==v
 layers=read(BASE/'government-xl-ocean-walk-all-original-contact-layers-20261008/contact-layers.json')
 basic=read(BASE/'government-xl-ocean-walk-six-basic-interfaces-20261008/diagnostic.json')
 for d in [layers,basic]:
  for path,sha in d['inputHashes'].items():assert ref(ROOT/path)['sha256']==sha
 pairs=[]
 for f in FOLDERS[-2:]:pairs+=read(BASE/f/'support-checks.json.gz')['rows']
 assert len(pairs)==17 and len({p['uid'] for p in pairs})==17
 assert sum(p['interface']['passed'] for p in pairs)==6
 assert len(layers['rows'])==11 and all(r['withOtherOriginalContactLayer']==0 for r in layers['rows'])
 row={'uid':'landsd/81743:0','sourceSHA256':'52e0d6b6341f664cc18ee8a894e1c4c5e5dbc1b05729bb43deb8c109e0fac8cb','modelId':'B146372594202063C0','humanStatus':'held-unknown','needsAIProcessing':None,'needsComputeProcessing':None,'needsHumanDecision':False,'permanentRejection':False,'retainCurrentModel':True,'revisitLater':True,'installationApproved':False,'newlyInstalled':0,'reasons':['original-source-clearance-below-negative-0.5m-limit','six-retained-basic-component-ground-gap-regressions','eleven-original-component-podium-interfaces-unresolved'],'originalComponentCount':17,'originalInterfacesPassed':6,'originalInterfacesUnresolved':11,'basicInterfacesUnresolved':6,'sourceLocalPhysicalJobId':prior[3]['jobId'],'completeContextIdentityPassed':True,'suppressesBuildingUids':[],'otherOriginalSupportLayersResolved':0,'nextStep':'Do not repeat unchanged source acquisition, terrain or these 17 interfaces. Source-specific evidence or a demonstrated contact/visible-surface classifier correction is needed for the raw original wall/TIN burial and unresolved original component contacts. The station/ancillary sources also need their own appropriate terrain/support routing. Every existing numeric, full foundation, retained-neighbour, runtime/browser and publication gate remains. Six passing interfaces alone do not establish a complete installable assembly.'}
 save(DOC/'followup.json',row)
 refs=[ref(Path(__file__)),ref(DOC/'followup.json')]+[ref(BASE/f/'result.json') for f in FOLDERS]
 for f in ['government-xl-ocean-walk-all-original-contact-layers-20261008','government-xl-ocean-walk-six-basic-interfaces-20261008']:
  for p in (BASE/f).iterdir():
   if p.is_file():refs.append(ref(p))
 for d in [layers,basic]:refs += [{'path':p,'sha256':s} for p,s in d['inputHashes'].items()]
 refs=list({r['path']:r for r in refs}.values());claim=reservations.claim('codex-ocean-complete-receipt-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH);assert claim['ok'],claim;lease=claim['reservation'];job=None
 try:
  payload={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'evidenceRefs':refs,'priorJobIds':[r['jobId'] for r in prior]};stage='complete-original-component-investigation-followup-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'rows':[row],'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'terrainGeometryChanges':0,'scriptExternalAICalls':0,'sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'qualification':'All 18 original meshes investigated unchanged. Six component interfaces pass, eleven remain unresolved; no neighbouring original adds a strict contact layer at the failed samples. Numeric policies unchanged. No installation, permanent rejection or inferred AI/human requirement.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for v in refs:assert ref(ROOT/v['path'])==v
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'neonVerified':True,'originalInterfacesPassed':6,'unresolved':11,'newlyInstalled':0}),flush=True)
 except Exception as e:
  if job:assert jobs.finish(job,error=str(e))
  raise
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
