"""Freeze all 179 new complete-source topology records and primary lead research."""
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
BATCH='government-xl-spatial-surface-roles-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
OLD=ROOT/'docs/astra-city/government-import/government-xl-identity-search-20261009'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not (DOC/'result.json').exists();rank=read(DOC/'research-ranking.json.gz');data=read(DOC/'topological-failure-ranking.json.gz');assert len(rank['rows'])==len(data['rows'])==179;assert len(rank['opGroups'])==12
 for r in data['rows']:
  assert r['identityAccepted'] is False and r['installationApproved'] is False and r['geometryChanges']==0
  if r.get('originalPath'):assert digest((ROOT/r['originalPath']).read_bytes())==r['sourceSHA256']
  for tile,sha in r.get('sourceTileHashes',{}).items():assert digest((ROOT/'3d-viewer'/tile).read_bytes())==sha
 paths=[p for p in DOC.rglob('*') if p.is_file()]+[p for p in LOCAL.rglob('*') if p.is_file()]+[p for p in HERE.glob('xl-spatial-surface-*20261009.py')]+[OLD/'result.json',OLD/'actionable-dispositions.json.gz',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',HERE/'pending-context.py',ROOT/'docs/astra-city/government-import/government-xl-identity-search-op-structures-20261009/full-original-op-group-measures.json.gz',ROOT/'docs/astra-city/government-import/government-xl-322-complete-footprint-group-scan-v2-20261008/outcomes.json.gz']
 refs=[ref(p) for p in sorted(set(paths))];prior=read(OLD/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
 claim=reservations.claim('xl-surface-role-checkpoint-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation']
 try:
  stage='complete-source-topology-visible-surface-role-research-v1';payload={'uids':[r['uid'] for r in rank['rows']],'evidenceRefs':refs};jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'rows':rank['rows'],'familyCountsOverlap':rank['familyCountsOverlap'],'officialOPVariants':12,'sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'scriptExternalAICalls':0,'newlyInstalled':0,'publication':False,'geometryChanges':0,'identityAccepted':False,'installationApproved':False,'permanentRejection':False,'newPositiveAcceptanceProofs':0,'currentConclusion':'All179 exact unresolved identity sources accounted; new topology/surface-role families select evidence investigations, not unchanged acceptance retries. Two internal-opening candidates and two source-authored external-access leads preserved; no courtyard/overhang credit yet. SiuHoWan restoration excluded.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for x in refs:assert ref(ROOT/x['path'])==x
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print({'jobId':jid,'all179Accounted':True,'newPositiveAcceptanceProofs':0,'neonVerified':True},flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
