"""Persist original-only Apex/HSBC contact investigations and remaining blockers."""
import json,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
BATCH='government-xl-original-contact-investigations-20261008'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
TOPOLOGY=BASE/'government-xl-hsbc-original-assembly-topology-20261008'
WALL=BASE/'government-xl-hsbc-original-wall-overlap-diagnostic-20261008'
APEX=BASE/'government-xl-apex-lower-profile-contact-diagnostic-v3-20261008'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists()
 old=read(TOPOLOGY/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(old['jobId'],)).fetchone()==('complete',old)
 for item in old['evidenceRefs']:assert ref(ROOT/item['path'])==item
 walls=read(WALL/'interfaces.json');apex=read(APEX/'contact.json');assert len(walls['rows'])==2 and len(apex['rows'])==1
 refs=[ref(Path(__file__)),ref(TOPOLOGY/'result.json'),ref(TOPOLOGY/'topology.json'),ref(WALL/'interfaces.json')]
 for folder in [BASE/'government-xl-apex-lower-profile-contact-diagnostic-20261008',BASE/'government-xl-apex-lower-profile-contact-diagnostic-v2-20261008',APEX]:
  report=read(folder/'contact.json');refs.append(ref(folder/'contact.json'))
  for path,sha in report['inputHashes'].items():assert ref(ROOT/path)['sha256']==sha;refs.append({'path':path,'sha256':sha})
 for path,sha in walls['inputHashes'].items():assert ref(ROOT/path)['sha256']==sha;refs.append({'path':path,'sha256':sha})
 refs=list({r['path']:r for r in refs}.values())
 a=apex['rows'][0];assert len(a['firstContacts'])==a['lowerWithinStrictContact']==215
 steep=[c for c in a['firstContacts'] if abs(c['faceNormalY'])<.15];assert len(steep)==12
 rows=[]
 for w in walls['rows']:
  d=w['diagnostic'];assert not d['geometricIntersectionsComplete'] and not d['acceptanceGranted']
  rows.append({'uid':w['uid'],'sourceSHA256':w['sourceSHA256'],'supportUid':w['supportUid'],'supportSHA256':w['supportSHA256'],'reasons':['original-native-support-interface-unresolved','original-mesh-not-proven-closed-solid'],'samples':d['samples'],'strictContacts':d['strictContacts'],'diagnosticWallIntersectionsWithoutCutoff':d['wallIntersections'],'stillUnresolvedWithoutCutoff':len(d['unresolved']),'nextStep':'Authoritative original component/scene evidence or a demonstrated correction addressing the actual unresolved source faces; the failures persist even in the uncapped intersection diagnostic. Do not expand the 0.5m acceptance allowance or assume closed-solid ownership.'})
 rows.append({'uid':'landsd/265848:0','sourceSHA256':walls['rows'][0]['supportSHA256'],'reasons':['original-upper-tower-support-interfaces-unresolved'],'dependentUids':[w['uid'] for w in walls['rows']],'nextStep':'Retain current basic tower forms and reuse both pinned native originals. All source support, retained terrain/neighbour and publication gates remain; no valid complete original assembly has been established.'})
 rows.append({'uid':a['uid'],'sourceSHA256':a['sourceSHA256'],'reasons':['global-low-rim-contact-unresolved','lower-profile-contacts-not-proven-structural-support'],'lowerProfileContactSamples':215,'contactFaceOrientations':a['contactFaceOrientations'],'steepContactFaceMaximumHeightSpanM':max(c['faceHeightSpanM'] for c in steep),'nextStep':'Source-specific structural/ground-skirt classification is required before claiming a contact-test correction. All 215 lower-profile contacts are outside the old global low rim;194 are upward-facing,9 downward-facing,12 on steep faces with at most0.590m height span. These may be ground/terrace details, not proof of wall support. Preserve existing strict gates and the0.111m global-rim gap; do not substitute minSurfaceGap or count arbitrary surface contacts as acceptance.'})
 for r in rows:r.update(humanStatus='held-unknown',needsAIProcessing=None,needsComputeProcessing=None,needsHumanDecision=False,retainCurrentModel=True,revisitLater=True,permanentRejection=False,newlyInstalled=0,installationApproved=False)
 save(DOC/'followups.json',{'rows':rows,'publication':False,'modelGeometryChanges':0});refs.append(ref(DOC/'followups.json'))
 claim=reservations.claim('codex-original-contact-receipt-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH);assert claim['ok'],claim;lease=claim['reservation'];job=None
 try:
  payload={'uids':[r['uid'] for r in rows],'evidenceRefs':refs,'topologyJobId':old['jobId']};stage='original-contact-topology-interpretation-followups-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'rows':rows,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'qualification':'Original contact/topology investigation only. No acceptance edits, source transformations, thresholds changes, structural ownership claim or installation. Closed solids cannot be assumed from these exact originals. Uncapped wall search is explicitly diagnostic and remains incomplete.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for item in refs:assert ref(ROOT/item['path'])==item
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'sourceFollowups':len(rows),'neonVerified':True}),flush=True)
 except Exception as e:
  if job:assert jobs.finish(job,error=str(e))
  raise
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
