"""Complete exact original component contact graph; no structural approval."""
import importlib.util,json,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from exact_original_component_contacts_20261009 import exact_component_contacts
BATCH='government-xl-miami-elevated-original-contact-graph-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/government-xl-miami-nine-original-contact-20261009/all-original-source-contact-inputs.json.gz'
CENSUS=ROOT/'docs/astra-city/government-import/government-xl-miami-neighbour-source-overlap-20261009/whole-source-neighbour-cause-and-elevated-census.json.gz'

def main():
 assert not (DOC/'result.json').exists(),'Completed checkpoint immutable'
 source=read(INPUT);census=read(CENSUS)['elevatedSources'];geometry={r['uid']:np.asarray(r['position'],float).reshape(-1,3,3) for r in source['rows']};podium=geometry['landsd/232089:0'];rows=[]
 claim=reservations.claim('miami-elevated-original-contact-'+str(uuid.uuid4()),['building:'+r['uid'] for r in census]+['building:landsd/232089:0'],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation']
 try:
  for r in census:
   t=geometry[r['uid']];assert digest(t.astype('<f8').tobytes())==r['worldTriangleSHA256'];all_ids=[i for p in r['components'] for i in p['originalFaceIds']];assert sorted(all_ids)==list(range(len(t))) and len(set(all_ids))==len(t)
   main_part=r['components'][0];main_faces=main_part['originalFaceIds'];body_podium=exact_component_contacts(t,main_faces,podium,list(range(len(podium))));save(DOC/(r['uid'].split('/')[1].replace(':','-')+'-main-body-podium-all-exact-contacts.json.gz'),body_podium)
   other=[]
   for p in r['components'][1:]:
    main_contact=exact_component_contacts(t,p['originalFaceIds'],t,main_faces,first_only=True);other.append({'component':p['component'],'faces':p['faces'],'originalFaceIds':p['originalFaceIds'],'worldBounds':p['worldBounds'],'mainBodyContact':main_contact});assert reservations.heartbeat(lease)['ok']
   record={**r,'mainBodyToPodium':body_podium,'remainingComponentsToMainBody':other,'allOriginalFacesAccountedExactlyOnce':True,'noSnappingOrWelding':True,'physicalSupportAccepted':False,'installationApproved':False};save(DOC/(r['uid'].split('/')[1].replace(':','-')+'-whole-component-contact-graph.json.gz'),record)
   row={'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'faces':len(t),'components':len(r['components']),'mainBodyFaces':len(main_faces),'mainBodyPodiumContacts':len(body_podium['contacts']),'mainBodyPodiumPositiveDimensionalContacts':sum(c['dimension']>0 for c in body_podium['contacts']),'remainingComponents':len(other),'remainingWithExactMainBodyContact':sum(bool(p['mainBodyContact']['contacts']) for p in other),'sourceGeometryChanges':0,'physicalSupportAccepted':False};rows.append(row);print(json.dumps(row),flush=True)
  save(DOC/'summary.json',{'rows':rows,'sourceGeometryChanges':0,'physicalSupportAccepted':False,'installationApproved':False})
  spec=importlib.util.spec_from_file_location('miami_elevated_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.freeze(BATCH,'complete-original-miami-elevated-source-contact-graph-v1',[Path(__file__),INPUT,CENSUS,HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py'],{'uids':[r['uid'] for r in census],'rows':rows,'humanStatus':'held-unknown','requiresMoreComputeOrSourceEvidence':True,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'sourceOnlyDiagnostic':True,'currentDrawnTerrainAcceptance':False,'remainingReason':'original-elevated-body-support-and-detached-component-roles-require-complete-source-proof','nextStep':'Use exact contacts and complete face accounting to resolve original wall/roof/ornamental component roles; contact alone is not structural acceptance. Preserve all ordinary support failures, current actors and original poses.'})
 finally:assert reservations.release(lease)['ok']

if __name__=='__main__':main()
