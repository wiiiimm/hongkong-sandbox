"""Freeze original openings, independent FBX and primary role research in Neon."""
import uuid
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
BATCH='government-xl-source-authored-openings-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;PRIOR=ROOT/'docs/astra-city/government-import/government-xl-spatial-surface-roles-20261009'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not (DOC/'result.json').exists();original=read(DOC/'original-opening-diagnostics.json.gz')['rows'];independent=read(DOC/'independent-fbx-opening-comparison.json.gz')['rows'];assert len(original)==len(independent)==2
 for r in independent:assert r['fbxGLTFProjectionSymmetricDifferenceM2']==r['fbxGLTFProjectionHausdorffM']==0 and r['originalWorldTrianglesSHA256']==r['cppOriginalWorldTrianglesSHA256']
 paths=[p for p in DOC.rglob('*') if p.is_file()]+[p for p in LOCAL.rglob('*') if p.is_file()]+list(HERE.glob('xl-source-authored-openings*20261009.py'))+[PRIOR/'result.json',PRIOR/'157125-0.json.gz',PRIOR/'295538-0.json.gz',HERE/'xl-second-pass.py',HERE/'pending-context.py',HERE/'government_georef_cell_identity.py']
 refs=[ref(p) for p in sorted(set(paths))];previous=read(PRIOR/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(previous['jobId'],)).fetchone()==('complete',previous)
 claim=reservations.claim('xl-source-openings-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation']
 try:
  stage='independent-original-source-opening-role-research-v1';payload={'uids':[r['uid'] for r in original],'evidenceRefs':refs};jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'rows':[{'uid':r['uid'],'modelId':r['modelId'],'sourceKey':r['sourceKey'],'sourceSHA256':r['sourceSHA256'],'rawTargetCoverage':r['rawTargetCoverage'],'currentConclusion':('official-pump-house-rectangular-source-hole-visible-role-unresolved' if r['uid']=='landsd/157125:0' else 'exact-station-companion-identified-inside-source-projection-gap'),'nextStep':('Exact visible-surface evidence required; no inferred open courtyard credit.' if r['uid']=='landsd/157125:0' else 'Acquire complete untouched station source and test independent full collection gates.') } for r in original],'independentOriginalFBXSources':2,'newPositiveCandidates':0,'sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'scriptExternalAICalls':0,'newlyInstalled':0,'publication':False,'geometryChanges':0,'identityAccepted':False,'installationApproved':False,'permanentRejection':False,'openingCoverageCreditGranted':False,'currentConclusion':'Neither projection hole may be credited as a courtyard. Exact station companion is a concrete new original-source acquisition lead; unnamed small building is mapped as pump house, not assumed residential courtyard.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for x in refs:assert ref(ROOT/x['path'])==x
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print({'jobId':jid,'neonVerified':True},flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
