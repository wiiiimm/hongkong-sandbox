"""Freeze source identity/support/adjacent-podium evidence with fenced Neon receipts."""
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
from popcorn_original_ancillary_identity_20261009 import verify_collection,POLICY
BASE=ROOT/'docs/astra-city/government-import'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def freeze(batch,stage,paths,result):
 doc=BASE/batch
 if (doc/'result.json').exists():
  old=read(doc/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(old['jobId'],)).fetchone()==('complete',old)
  return old
 paths+=[p for p in doc.rglob('*') if p.is_file()]+[Path(__file__)];refs=[ref(p) for p in sorted(set(paths))];claim=reservations.claim('popcorn-source-checkpoint-'+str(uuid.uuid4()),['source-context:'+batch],batch=batch,ttl=1800);assert claim['ok'],claim;lease=claim['reservation']
 try:
  payload={'uids':result['uids'],'evidenceRefs':refs};jid=jobs.enqueue(batch,stage,payload);job=jobs.claim(batch,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,**result,'jobId':jid,'batch':batch,'stage':stage,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'terrainGeometryChanges':0,'scriptExternalAICalls':0,'aiGeometryModelling':False,'installationApproved':False,'permanentRejection':False}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for r in refs:assert ref(ROOT/r['path'])==r
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(doc/'result.json',result);save(doc/'neon-sync.json',{'jobId':jid,'resultVerified':True});print({'batch':batch,'jobId':jid,'neonVerified':True},flush=True);return result
 finally:assert reservations.release(lease)['ok']
def main():
 h='government-xl-popcorn-source-access-ownership-20261009';pair='government-xl-popcorn-complete-original-current-pair-20261009';lineage='government-xl-popcorn-current-gltf-source-lineage-20261009';proof=verify_collection();paths=[]
 for b in [pair,lineage]:paths +=[p for p in (BASE/b).rglob('*') if p.is_file()]+[p for p in (HERE/'local'/b).rglob('*') if p.is_file()]
 paths+=list(HERE.glob('xl-popcorn-source-access-ownership*20261009.py'))+[HERE/'popcorn_original_ancillary_identity_20261009.py',HERE/'xl-popcorn-complete-original-current-pair-20261009.py',HERE/'xl-popcorn-current-gltf-source-lineage-20261009.py',HERE/'xl-second-pass.py',HERE/'government_georef_cell_identity.py']
 for b in ['government-xl-source-authored-openings-20261009','government-xl-popcorn-station-collection-20261009']:
  paths+=[BASE/b/'result.json'];paths +=[p for p in (HERE/'local'/b/'raw-fbx').rglob('*') if p.is_file()]+[p for p in (HERE/'local'/b/'blender-inspection/cpp').rglob('*') if p.is_file()]
 paths +=[BASE/'government-xl-source-authored-openings-20261009/primary/mtr-tseung-kwan-o-railway-protection-plan.pdf',BASE/'government-xl-source-authored-openings-20261009/primary/mtr-tseung-kwan-o-railway-protection-plan.pdf.request.json']+[ROOT/'3d-viewer'/url for url in proof['retainedOtherTileSHA256s']]
 freeze(h,'exact-original-ancillary-stair-source-identity-v1',paths,{'uids':sorted(['landsd/295538:0','landsd/295539:0']),'identityAccepted':True,'sourceIdentityReviewUsedAI':True,'identityPolicy':POLICY,'identityProof':proof,'xlIdentityCasesAdvanced':1,'scriptFullAcceptancePassed':False,'currentHeldReason':'complete-original-station-support-and-unattached-original-side-panel-role-unresolved','nextStep':'Complete source shell/component support and preserve all physical/runtime/browser/publisher gates independently.'})
 i='government-xl-popcorn-original-pair-interface-20261009';paths=list(HERE.glob('xl-popcorn-original-pair*20261009.py'))+list(HERE.glob('xl-popcorn-original-pair*20261009.mjs'))+[BASE/h/'result.json',BASE/'government-xl-popcorn-complete-original-source-terrain-20261009/result.json'];paths+=[ROOT/p for p in read(BASE/i/'exact-original-interface-diagnostic.json.gz')['inputHashes']];paths+=[ROOT/p for p in read(BASE/i/'original-visuals/render.json')['inputHashes']]
 diagnostic=read(BASE/i/'exact-original-interface-diagnostic.json.gz');freeze(i,'complete-original-pair-support-source-components-v1',paths,{'uids':['landsd/295538:0','landsd/295539:0'],'identityAccepted':False,'scriptFullAcceptancePassed':False,'supportAccepted':False,'rawSupportDiagnostic':diagnostic['rows'],'remainingReasonGroups':{'noVerticalSupport':223,'supportAboveRim':104,'rimAboveSupport':13},'nextStep':'Complete all9source component attachment paths and positive open-shell source support interpretation; no arbitrary rim/contact waiver.'})
 j='government-xl-identity-block37-adjacent-podium-20261009';packet=BASE/'government-xl-terrain-recovery-block37-current-inputs-20261009/block-j-excess-context.json.gz';x=read(packet);freeze(j,'current-adjacent-active-podium-provider-context-v1',[HERE/'xl-identity-block37-adjacent-podium-20261009.py',packet],{'uids':['landsd/228547:0','landsd/230175:0'],'sourceSHA256':x['sourceSHA256'],'identityAccepted':False,'scriptFullAcceptancePassed':False,'rawUnrelatedOverlapM2':x['sourceExcessCoveredByOtherM2'],'remainingReason':'adjacent-active-podium-source-overlap-ownership-not-established','nextStep':'Original neighbouring source/roof interface and primary precise source ownership evidence; keep exact recorded8faces and all original geometry.'})
if __name__=='__main__':main()
