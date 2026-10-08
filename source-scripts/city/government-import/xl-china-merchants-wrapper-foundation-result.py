"""Complete China Merchants whole foundation after a separate legacy dependency guard."""
import uuid,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
BATCH='government-xl-china-merchants-wrapper-foundation-result-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists()
 import importlib.util
 import numpy as np
 from shapely.geometry import Polygon
 prior_doc=ROOT/'docs/astra-city/government-import/government-xl-retained-group-central-wrapper-20261009-264206-0'
 prior=read(prior_doc/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
 for v in prior['evidenceRefs']:assert ref(ROOT/v['path'])==v
 local=HERE/'local/government-xl-retained-group-central-wrapper-20261009-264206-0'
 geometry_path=local/'runtime-geometry.json.gz';runtime=read(geometry_path);geometry=runtime['rows'][0]
 expected={v['path']:v['sha256'] for v in prior['evidenceRefs']}
 for path,h in runtime['inputHashes'].items():assert expected[path]==h and ref(ROOT/path)['sha256']==h
 uid='landsd/264206:0';assert geometry['uid']==uid
 row=read(prior_doc/'selection.json.gz')['rows'][0];assert row['uid']==uid and geometry['sourceSHA256']==row['sourceSHA256']
 spec=importlib.util.spec_from_file_location('china_wrapper_foundation',HERE/'xl-final-script-pass.py');final=importlib.util.module_from_spec(spec);spec.loader.exec_module(final)
 triangles=np.asarray(geometry['position']).reshape(-1,3)[np.asarray(geometry['index']).reshape(-1,3)]
 decoder_spec=importlib.util.spec_from_file_location('china_original_decoder',HERE/'xl-second-pass.py');decoder=importlib.util.module_from_spec(decoder_spec);decoder_spec.loader.exec_module(decoder);decoder.LOCAL=local
 original=decoder.glb_triangles(row);assert original.shape==triangles.shape and np.max(np.abs(original-triangles))<.002
 ground=np.asarray(geometry['drawnGroundGeometry']).reshape(-1,3,3);building=row['source']['building']
 foundation=final.foundation_context(triangles,ground,Polygon(building['rings'][0],building['rings'][1:]))
 passed=foundation['completeTerrainTriangles']==foundation['triangles'] and not foundation['fullyBuriedUpwardTriangles'] and foundation['fullyBuriedAreaFraction']==0
 save(DOC/'foundation.json',{'uid':uid,'sourceSHA256':row['sourceSHA256'],'foundation':foundation,'strictFoundationAccepted':passed,'publication':False})
 refs=[ref(Path(__file__)),ref(prior_doc/'result.json'),ref(geometry_path),ref(DOC/'foundation.json'),ref(HERE/'xl-final-script-pass.py'),*prior['evidenceRefs']]
 refs=list({v['path']:v for v in refs}.values())
 rows=[{'uid':uid,'sourceSHA256':row['sourceSHA256'],'foundation':foundation,'strictFoundationAccepted':passed,'humanStatus':'held-unknown','retainCurrentModel':True,'permanentRejection':False,'needsAIProcessing':None,'needsHumanDecision':False,'reasons':['source-clearance-below-negative-0.5m-limit','native-retained-check-stopped-at-legacy-candidate-dependency']+([] if passed else ['whole-source-foundation']),'nextStep':'Original source-local TIN still gives -7.392839m clearance. Preserve every raw face and original source. Full retained checker stops at old already-installed263590 dependency metadata state=candidate for232907; do not rewrite that metadata or infer source corruption. Need a separate unchanged-native preservation proof or proper dependency evidence, plus source-specific subsurface/foundation resolution.'}]
 interpretation={'sourceGeometryUnchanged':True,'sourceEvidenceInterpretationUsedAI':False,'completeCurrentWrapperNeighbourForms':5312,'qualification':'Whole foundation computed from saved hash-bound runtime source and actual drawn ground, despite separate legacy native dependency guard. No terrain rebuild, source changes or acceptance.'}
 payload={'rows':rows,'interpretation':interpretation,'priorPhysicalJobId':prior['jobId'],'evidenceRefs':refs};claim=reservations.claim('codex-china-wrapper-foundation-'+str(uuid.uuid4()),['building:landsd/264206:0','source-context:'+BATCH],batch=BATCH);assert claim['ok'],claim;lease=claim['reservation'];job=None
 try:
  stage='current-wrapper-complete-source-foundation-result-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'batch':BATCH,'jobId':jid,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'aiGeometryModelling':False,'qualification':'Full original source foundation and concrete legacy-checker failure retained as separate diagnostics. No tolerance, position, source, runtime or review modifications; no installation credit.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for v in refs:assert ref(ROOT/v['path'])==v
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'neonVerified':True,'strictFoundationAccepted':passed,'buriedUpwardTriangles':foundation['fullyBuriedUpwardTriangles']}),flush=True)
 except Exception as e:
  if job:assert jobs.finish(job,error=str(e))
  raise
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
