"""Freeze explicit government OP relationships, original metrics and follow-up leads."""
from pathlib import Path
import uuid,json,collections
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
BATCH='government-xl-identity-search-op-structures-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;BASE=ROOT/'docs/astra-city/government-import/government-xl-identity-search-20261009';LOCAL=HERE/'local'/BATCH
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not (DOC/'result.json').exists();relationships=read(DOC/'official-op-relationship-research.json.gz');single=read(DOC/'full-original-op-group-measures.json.gz');paired=read(DOC/'paired-original-op-group-recovered-measures.json.gz');recovery=read(DOC/'counterpart-original-recovery.json.gz');assert len(relationships['rows'])==190 and len(single['rows'])==12 and len(paired['rows'])==2
 assert not any(r['diagnosticCandidate'] for r in single['rows']+paired['rows']);current={}
 for t in read(ROOT/'3d-viewer/city/data/manifest.json')['tiles']:
  for b in read(ROOT/'3d-viewer'/t['url'])['buildings']:current[b['uid']]=b
 for r in single['rows']+paired['rows']:assert all(current[b['uid']]==b for b in r['groupForms'])
 for tile,sha in single['sourceTileHashes'].items():assert digest((ROOT/'3d-viewer'/tile).read_bytes())==sha
 for r in recovery['rows']:assert digest((ROOT/r['path']).read_bytes())==r['sourceSHA256']
 input=read(BASE/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(input['jobId'],)).fetchone()==('complete',input)
 save(DOC/'actionable-findings.json.gz',{'sourceScope':190,'rows':relationships['rows'],'newCompleteGroupLeads':single['rows'],'twoPartOriginalMeasures':paired['rows'],'diagnosticPositiveCandidates':0,'newlyInstalled':0,'publication':False,'qualification':'Current explicit provider OP relationships provide new source-group context and improve pipeline investigations, but do not waive complete source ownership or strict spatial/physical thresholds. All originally held sources remain revisitable; primary-source availability/identity is not geometry corruption.'})
 paths=[*sorted(DOC.rglob('*.json')),*sorted(DOC.glob('*.json.gz')),*sorted(HERE.glob('xl-identity-search-op-structures-20261009-*.py')),BASE/'result.json',BASE/'live-georef-research.json.gz',LOCAL/'paired-physical-source-candidates.json.gz']
 refs=[ref(p) for p in sorted(set(paths))]+[ref(ROOT/r['originalPath']) for r in single['rows']]+[ref(ROOT/s['originalPath']) for r in paired['rows'] for s in r['sourceProofs']]+[{'path':'3d-viewer/'+tile,'sha256':sha} for tile,sha in single['sourceTileHashes'].items()]
 for folder in ['government-xl-identity-search-op-structures-20261009-counterparts']:
  refs += [ref(p) for p in sorted((HERE/'local'/folder).glob('*/directory/result.json'))]+[ref(p) for p in sorted((HERE/'local'/folder).glob('*/original/download.json'))]
 claim=reservations.claim('xl-op-identity-checkpoint-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation']
 try:
  stage='official-op-structure-component-investigation-v1';payload={'sourceScope':190,'evidenceRefs':refs,'sourceKeys':[r['sourceKey'] for r in relationships['rows']]};jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'rows':relationships['rows'],'newGroupLeadCount':12,'fullOriginalSingleGroupMeasures':single['rows'],'recoveredOriginalCounterpartCount':2,'fullOriginalPairedGroupMeasures':paired['rows'],'sourceRelationshipRows':len(relationships['sourceRelations']),'uniqueOfficialStructureIds':len({r['BuildingStructureID'] for r in relationships['sourceRelations']}),'allStructureRelationshipRows':len(relationships['allStructureRelations']),'diagnosticPositiveCandidates':0,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'aiGeometryModelling':False,'scriptExternalAICalls':0,'identityAccepted':False,'qualification':'Fresh primary-provider exact-CSUID occupation-structure relationships. Twelve new complete group investigations fail strict full-original bounds; two exact original counterassets recovered without changes and complete paired projections measured. K30/60 pair coverage0.9481896548,extent3.4115m,unrelated0.5361m²;K300/63 paircoverage0.9459880162,extent2.4076m,unrelated1.9011m². No95%/10m/1m²/whole-cell threshold waived; no suppression, UID assignment, permanent rejection or installation credit.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for item in refs:assert ref(ROOT/item['path'])==item
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'newGroupLeads':12,'pairedOriginals':2,'positive':0,'neonVerified':True}),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
