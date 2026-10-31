"""Freeze recovered exact original station collection and remaining typed-role hold."""
import uuid
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
BATCH='government-xl-popcorn-station-collection-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;PRIOR=ROOT/'docs/astra-city/government-import/government-xl-source-authored-openings-20261009';PRIORLOCAL=HERE/'local/government-xl-source-authored-openings-20261009'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not (DOC/'result.json').exists();r=read(DOC/'complete-original-popcorn-station-measures.json.gz');roles=read(DOC/'full-original-extra-role-diagnostics.json.gz');assert r['completeCollectionMeasures']['targetCoverage']>.99 and not r['strictSpatialDiagnosticPass'];assert roles['farFaceCount']==311 and len(roles['rows'])==2
 for source in r['sourceProofs']:
  s=source['source'];base=LOCAL if s['uid']=='landsd/295539:0' else PRIORLOCAL;cpp=read(base/'blender-inspection/cpp'/s['modelId']/'inspection.json');assert cpp['fullWorldTrianglesSHA256']==source['worldTrianglesSHA256'];assert digest((ROOT/s['sourcePath']).read_bytes())==s['sourceSHA256']
 paths=[p for p in DOC.rglob('*') if p.is_file()]+[p for p in LOCAL.rglob('*') if p.is_file()]+list(HERE.glob('xl-popcorn-station-collection*20261009.py'))+[PRIOR/'result.json',PRIOR/'popcorn-gap-official-buildings.json',PRIOR/'popcorn-gap-official-buildings.request.json',PRIOR/'popcorn-gap-official-building-candidates.json.gz',PRIOR/'295538-0/opening-diagnostics.json.gz',PRIOR/'primary/mtr-tseung-kwan-o-railway-protection-plan.pdf',PRIOR/'primary/mtr-tseung-kwan-o-railway-protection-plan.pdf.request.json',HERE/'xl-final-script-pass.py',HERE/'government_georef_cell_identity.py']+[p for p in (PRIORLOCAL/'raw-fbx/B447991877202063C0').rglob('*') if p.is_file()]
 refs=[ref(p) for p in sorted(set(paths))];previous=read(PRIOR/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(previous['jobId'],)).fetchone()==('complete',previous)
 claim=reservations.claim('xl-popcorn-collection-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation']
 try:
  stage='independent-original-station-companion-collection-v1';payload={'uids':['landsd/295538:0','landsd/295539:0'],'evidenceRefs':refs};jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'rows':[{'uid':r['uid'],'name':r['name'],'sourcePins':[{'modelId':s['source']['modelId'],'sourceSHA256':s['source']['sourceSHA256'],'originalWorldTrianglesSHA256':s['worldTrianglesSHA256']} for s in r['sourceProofs']],'previousSingleCoverage':r['rawStrictSingleSourceCoverage'],'completeOriginalCollectionMeasures':r['completeCollectionMeasures'],'allOriginalGeoRefCellsPass':all(c['wholeCellInsideOriginalProjection'] and c['wholeCellInsideExactTarget'] for c in r['originalCells']),'coverageFailureRecovered':True,'spatialAccepted':False,'remainingReason':'original-PopCorn-two-exterior-access-component-ownership-unresolved-maximum-extent-23.198m','nextStep':'Independently review complete source-backed exterior-access role and ownership; then fresh full support/contact, physical, runtime and browser gates without suppressing faces or waiving raw thresholds.'}],'coverageFailuresRecovered':1,'newPositiveCompleteCandidates':0,'sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'scriptExternalAICalls':0,'newlyInstalled':0,'publication':False,'geometryChanges':0,'identityAccepted':False,'installationApproved':False,'permanentRejection':False,'currentConclusion':'Exact original station companion restores complete target coverage to 99.4604%. Previous original PopCorn exterior extent remains, localized to two source-authored curved access ends. Source-based typed role investigation is pending; raw strict spatial acceptance remains false.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for x in refs:assert ref(ROOT/x['path'])==x
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print({'jobId':jid,'coverageFailuresRecovered':1,'newCompleteCandidates':0,'neonVerified':True},flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
