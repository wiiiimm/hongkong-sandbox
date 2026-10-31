"""Durable fenced source diagnosis; no import or installation credit."""
import sys,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
uid=sys.argv[1];batch='xl-terrain-recovery-20261009-'+uid+'-exact-coverage-probe';doc=ROOT/'docs/astra-city/government-import'/batch;lease=read('/tmp/xl-terrain-recovery-20261009-'+uid+'-role-lease.json');assert reservations.heartbeat(lease)['ok'];d=read(doc/'diagnostic.json.gz')
assert 'building:'+d['uid'] in lease['resources'] and d['everyPriorFloatingResidueExactlyCoveredWithSameGround'] and d['rawPriorUncoveredFaces']==len(d['rows'])
refs=d['evidenceRefs']+[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in [doc/'diagnostic.json.gz',Path(__file__)]]
payload={'uid':d['uid'],'sourceSHA256':d['sourceSHA256'],'evidenceRefs':refs};stage='same-original-ground-exact-coverage-diagnosis-v1';jid=jobs.enqueue(batch,stage,payload);job=jobs.claim(batch,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
result={**payload,'jobId':jid,'batch':batch,'rawPriorFloatingCoverageFailuresRetained':d['rawPriorUncoveredFaces'],'exactSameOriginalGroundAllCovered':True,'arbitraryPositiveAreaOrIntervalGapsRemainRejected':True,'humanStatus':'held-unknown','heldReason':'Fresh whole current physical checks and remaining original wall role verification are required; numerical seam coverage errors are now causally diagnosed with exact same-ground proof.','nextStep':('Complete three original wholly below-grade wall segments context, fresh whole physical/provider/runtime gates.' if uid=='195849' else 'Complete fresh original positive-dimensional wall/roof graph and physical/provider/runtime gates.'),'newlyInstalled':0,'sourceGeometryChanges':0,'aiGeometryModelling':False,'sourceEvidenceInterpretationUsedAI':True,'requiresAI':False,'needsComputeProcessing':True,'requiresHumanDecision':False,'publication':False,'installationApproved':False}
with connect() as con:
 con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
 for r in refs:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
with connect() as con:
 con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
save(doc/'result.json',result);save(doc/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'uid':d['uid'],'jobId':jid,'neonVerified':True}))
