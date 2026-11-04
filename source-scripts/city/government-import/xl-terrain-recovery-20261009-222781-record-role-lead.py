"""Durable complete original wall lead, raw identity history and provider provenance."""
import json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
BATCH='xl-terrain-recovery-20261009-222781-provider-role';DOC=ROOT/'docs/astra-city/government-import'/BATCH
BASE=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-222781-current-inputs-v2'
CONTEXT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-222781-wall-context/diagnostic.json.gz'
LEASE='/tmp/xl-terrain-recovery-20261009-222781-lease.json'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not (DOC/'result.json').exists();lease=read(LEASE);assert reservations.heartbeat(lease)['ok']
 d=read(CONTEXT);role=read(DOC/'expected-role.json');current=read(BASE/'indexed-preflight.json');assert current['rows'][0]['canStartTerrainWork'] and d['allAffectedWallsHaveRoles'] and not d['otherAffectedFaces']
 refs=d['evidenceRefs']+read(DOC/'original-source-provenance.json')['evidenceRefs']+current['evidenceRefs']
 refs.extend(ref(p) for p in [Path(__file__),DOC/'expected-role.json',DOC/'original-source-provenance.json',CONTEXT,BASE/'check-selection.json.gz',BASE/'context.json.gz',BASE/'indexed-preflight.json',ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-222781-current-inputs/indexed-preflight.json',HERE/'unchanged_authored_crossing_wall_role_20261009.py',HERE/'test_unchanged_authored_crossing_wall_role_20261009.py'])
 refs=sorted({x['path']:x for x in refs}.values(),key=lambda x:x['path']);payload={'uid':d['uid'],'sourceSHA256':d['sourceSHA256'],'evidenceRefs':refs};stage='rooftop-garden-original-exterior-wall-provider-context-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
 result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'wholeSourceFaces':11598,'rawClearanceFailingFaces':role['wallFaces'],'affectedWallFaces':14,'ordinaryAffectedFaces':0,'wholeSourceUncoveredFaces':0,'upwardContinuousMinimumGapM':d['upwardContinuousMinimumGapM'],'originalWindingConflictsPreserved':len(d['originalOpenExteriorPaths']['originalOrientationConflicts']),'originalZeroAreaFacesAccounted':d['originalZeroAreaFaces'],'originalProviderAttributesAndHierarchyEqualPacked':True,'currentRoutedIdentityPassed':True,'legacyEmptyCentroidMatchesRetained':True,'humanStatus':'held-unknown','heldReason':'Fresh complete current physical and source-specific complete foreign wall role checks remain; no existing failure is waived.','nextStep':'Run indexed original terrain/full neighbour/runtime checks under current manifest, then replay the frozen reviewed wall role against fresh complete continuous geometry and independently recomputed current actor scope.','sourceGeometryChanges':0,'newlyInstalled':0,'installationApproved':False,'publication':False,'requiresAI':False,'requiresHumanDecision':False,'sourceEvidenceInterpretationUsedAI':True,'modelGeometryAI':False,'closedSolidCertified':False}
 try:
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for item in refs:assert ref(ROOT/item['path'])==item
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'neonVerified':True,'newlyInstalled':0}),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
