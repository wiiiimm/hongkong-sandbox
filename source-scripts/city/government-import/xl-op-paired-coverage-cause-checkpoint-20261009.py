"""Freeze original-source uncovered geometry and raw primary aerial-site evidence."""
from pathlib import Path
import uuid
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
BATCH='government-xl-op-paired-coverage-cause-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;PRIOR=ROOT/'docs/astra-city/government-import/government-xl-identity-search-op-structures-20261009'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not (DOC/'result.json').exists();data=read(DOC/'causal-diagnostics.json.gz');assert len(data['rows'])==2
 observations=[]
 for r in data['rows']:
  assert r['uncoveredBoundaryConnectedAreaM2']/r['uncoveredTargetAreaM2']>.999
  observations.append({'uid':r['uid'],'sourceProofs':r['sourceProofs'],'gps':r['gps'],'targetAreaM2':r['targetAreaM2'],'uncoveredTargetAreaM2':r['uncoveredTargetAreaM2'],'uncoveredBoundaryConnectedAreaM2':r['uncoveredBoundaryConnectedAreaM2'],'uncoveredInteriorAreaM2':r['uncoveredInteriorAreaM2'],'unrelatedOverlapUids':[{'uid':x['uid'],'areaM2':x['areaM2']} for x in r['unrelatedOverlaps']],'currentConclusion':'no-supported-courtyard-exception','sourceVisualReview':'Exact original projected mesh and original vertices show exterior boundary strips. Nearly all uncovered area is boundary-connected; interior residue is negligible and not an authored courtyard. Current government imagery was visually inspected as context; no submetre property/mesh-boundary precision or ownership inferred from photo pixels.','nextStep':'Keep exact original version held. Obtain positive corrected provider polygon/source-version evidence or a more complete original government source format; do not drop the exterior strips or unrelated neighbour forms.'})
 save(DOC/'source-evidence-interpretation.json',{'rows':observations,'sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'geometryChanges':0,'identityAccepted':False,'installationApproved':False})
 paths=[*sorted(DOC.rglob('*.json')),*sorted(DOC.rglob('*.json.gz')),*sorted(DOC.rglob('*.geojson')),*sorted(DOC.rglob('*.png')),HERE/'xl-op-paired-coverage-cause-20261009.py',HERE/'xl-op-paired-coverage-imagery-20261009.py',Path(__file__),PRIOR/'result.json',PRIOR/'paired-original-op-group-recovered-measures.json.gz'];refs=[ref(p) for p in sorted(set(paths))]
 refs += [ref(ROOT/s['originalPath']) for r in data['rows'] for s in r['sourceProofs']]
 prior=read(PRIOR/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
 claim=reservations.claim('xl-paired-causal-source-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation']
 try:
  stage='original-paired-exterior-coverage-causal-research-v1';payload={'uids':[r['uid'] for r in observations],'evidenceRefs':refs};jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'rows':observations,'sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'scriptExternalAICalls':0,'newlyInstalled':0,'publication':False,'geometryChanges':0,'identityAccepted':False,'installationApproved':False,'permanentRejection':False,'currentConclusion':'Both pairs have exterior boundary mismatch, not demonstrated source-authored courtyards or internal openvoids. No95%coverage alternative justified. Exact difference geometries and every surrounding form retained; images context only.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for x in refs:assert ref(ROOT/x['path'])==x
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print({'jobId':jid,'courtyardExceptionSupported':False,'neonVerified':True},flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
