"""Fence the new source role/support and current identity checkpoint; no acceptance."""
import json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
BATCH='xl-terrain-recovery-20261009-garden-terrace-wall-context';DOC=ROOT/'docs/astra-city/government-import'/BATCH
CURRENT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-garden-terrace-current-inputs'
INTERFACES=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-garden-terrace-component-interfaces'
COMBINED=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-garden-terrace-combined-support'
LEASE='/tmp/xl-terrain-recovery-20261009-garden-terrace-lease.json'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not (DOC/'result.json').exists();lease=read(LEASE);assert reservations.heartbeat(lease)['ok']
 wall=read(DOC/'diagnostic.json.gz');interfaces=read(INTERFACES/'diagnostic.json.gz');combined=read(COMBINED/'diagnostic.json.gz');preflight=read(CURRENT/'indexed-preflight.json')
 assert wall['allAffectedWallsHaveRoles'] and not wall['otherAffectedFaces'] and wall['wholeSourceUncoveredFaces']==0
 assert all(r['canStartTerrainWork'] for r in preflight['rows'])
 refs=wall['evidenceRefs']+preflight['evidenceRefs']
 for report in [interfaces,combined]:refs.extend({'path':p,'sha256':sha} for p,sha in report['inputHashes'].items())
 refs.extend(ref(p) for p in [Path(__file__),DOC/'README.md',DOC/'diagnostic.json.gz',INTERFACES/'source-inputs.json',INTERFACES/'diagnostic.json.gz',COMBINED/'diagnostic.json.gz',CURRENT/'check-selection.json.gz',CURRENT/'context.json.gz',CURRENT/'indexed-preflight.json'])
 refs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path']);stage='garden-original-wall-complete-component-current-identity-v1';payload={'uids':['landsd/162285:0','landsd/21894:0'],'evidenceRefs':refs}
 jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
 result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'sourceSHA256s':{r['uid']:r['sourceSHA256'] for r in read(INTERFACES/'source-inputs.json')['sources']},'podiumWholeFaces':1418,'podiumAffectedWallFaces':29,'podiumOrdinaryAffectedFaces':0,'podiumUpwardContinuousMinimumGapM':wall['upwardContinuousMinimumGapM'],'towerWholeFaces':10670,'towerOriginalComponents':259,'mainTowerPodiumOnlyInterface':{k:interfaces['rows'][0]['interface']['strictLowRim'][k] for k in ['samples','contacts','missing','minGap','maxGap']},'mainTowerPartialExportCombinedSupport':{k:combined['rows'][0]['interface']['strictLowRim'][k] for k in ['samples','contacts','missing','minGap','maxGap']},'currentIdentityPassed':True,'manifestSHA256':preflight['manifestSHA256'],'humanStatus':'held-unknown','heldReason':'Complete current tower ground/support and source-specific podium wall/foreign interactions remain; historical full terrain caused a basic tower gap regression.','nextStep':'Refresh complete routed current physical context; preserve all strict support, foreign, neighbour and runtime gates.','sourceGeometryChanges':0,'newlyInstalled':0,'publication':False,'installationApproved':False,'requiresAI':False,'requiresHumanDecision':False,'sourceEvidenceInterpretationUsedAI':True,'modelGeometryAI':False,'qualification':'Historical full-face wall role evidence and original support diagnostics do not certify current ground support or installation; raw failures and incomplete exported-ground scope retained.'}
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
