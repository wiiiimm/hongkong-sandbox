"""Freeze independent unchanged FBX originals, raw transforms and strict diagnostics."""
from pathlib import Path
import uuid
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
BATCH='government-xl-source-format-comparison-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=ROOT/'docs/astra-city/government-import/government-xl-identity-search-op-structures-20261009'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not (DOC/'result.json').exists();data=read(DOC/'complete-source-format-comparison.json.gz');assert len(data['rows'])==2
 rows=[]
 for r in data['rows']:
  a=r['variants']['raw-fbx'];b=r['variants']['blender-inspection/cpp'];assert a==b;assert a['gltfSymmetricDifferenceAreaM2']==0 and a['gltfHausdorffM']==0 and not a['diagnosticPass'];assert r['geometryChanges']==0
  for source in r['fbxOriginalProofs']:
   cpp=read(LOCAL/'blender-inspection/cpp'/source['source']['modelId']/'inspection.json');assert source['worldTrianglesSHA256']==cpp['fullWorldTrianglesSHA256'];assert source['source']['sourceSHA256']==digest((ROOT/source['source']['sourcePath']).read_bytes())
  rows.append({'uid':r['uid'],'structureIds':r['structureIds'],'fbxSourcePins':[{'modelId':s['source']['modelId'],'sourceSHA256':s['source']['sourceSHA256'],'worldTrianglesSHA256':s['worldTrianglesSHA256'],'sourcePath':s['source']['sourcePath'],'triangles':s['triangleCount']} for s in r['fbxOriginalProofs']],'measures':a['measures'],'gltfSymmetricDifferenceAreaM2':0,'currentConclusion':'exact-original-FBX-same-projected-boundary-as-original-glTF','nextStep':'Positive corrected provider boundary lineage or genuinely revised original government source; no format-only repair or threshold waiver.'})
 paths=[p for p in DOC.rglob('*') if p.is_file()]+[p for p in LOCAL.rglob('*') if p.is_file()]+[HERE/f for f in ['source-format-comparison-20261009-acquire.py','source-format-comparison-20261009-blender-inspect.py','source-format-comparison-20261009-raw-fbx.py','source-format-comparison-20261009-measures.py','source-format-comparison-checkpoint-20261009.py']]+[PRIOR/'result.json',PRIOR/'paired-original-op-group-recovered-measures.json.gz']
 refs=[ref(p) for p in sorted(set(paths))];prior=read(PRIOR/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
 claim=reservations.claim('xl-source-format-research-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation']
 try:
  stage='independent-original-FBX-format-coverage-research-v1';payload={'uids':[r['uid'] for r in rows],'evidenceRefs':refs};jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'rows':rows,'originalFBXSources':4,'newPositiveCandidates':0,'sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'scriptExternalAICalls':0,'newlyInstalled':0,'publication':False,'geometryChanges':0,'identityAccepted':False,'installationApproved':False,'permanentRejection':False,'currentConclusion':'Both complete independent pinned original FBX pairs match original glTF projected boundaries exactly. No missing boundary geometry supplied by source-format route; strict identity checks remain held.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for x in refs:assert ref(ROOT/x['path'])==x
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print({'jobId':jid,'independentOriginalFBXSources':4,'newPositiveCandidates':0,'neonVerified':True},flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
