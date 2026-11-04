"""Complete exact original interfaces for two named small PopCorn parts.

Points, lines and area contacts remain separate geometric evidence. This does
not classify ownership, grant support or waive any current foreign-actor gate.
"""
import importlib.util,uuid,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from source_closed_components import components
from exact_original_component_contacts_20261009 import exact_component_contacts
BATCH='government-xl-popcorn-two-original-podium-contacts-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
PARTS=DOC.parent/'government-xl-popcorn-current-overlapping-original-recovery-20261009/selection.json.gz'
PODIUM=DOC.parent/'government-xl-popcorn-original-pair-interface-20261009/exact-original-contact-inputs.json.gz'
UIDS={'landsd/295421:0','landsd/295425:0'}
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists();claim=reservations.claim('popcorn-two-original-contact-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 paths=[Path(__file__),PARTS,PODIUM,HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'source_closed_components.py'];results=[]
 try:
  mall=next(r for r in read(PODIUM)['rows'] if r['uid']=='landsd/295538:0');ground=np.asarray(mall['position'],dtype='<f8').reshape(-1,3,3);assert digest(ground.tobytes())==mall['worldTriangleSHA256'];assert len(ground)==mall['triangles'];zero_mall=np.all(np.cross(ground[:,1]-ground[:,0],ground[:,2]-ground[:,0])==0,axis=1);mall_faces=np.flatnonzero(~zero_mall)
  decoder=module('two_original_podium_decoder','xl-second-pass.py');decoder.LOCAL=LOCAL;(LOCAL/'assets').mkdir(parents=True)
  for row in read(PARTS)['rows']:
   if row['uid'] not in UIDS:continue
   assert reservations.heartbeat(lease)['ok'];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];(LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz')).write_bytes(raw);row['triangles']=row['native']['model']['triangles'];t=decoder.glb_triangles(row);stem=row['uid'].split('/')[1].replace(':','-')
   bound=read(DOC.parent/'government-xl-popcorn-primary-excess-ownership-v2-20261009'/(stem+'-identity.json'));assert digest(t.astype('<f8').tobytes())==bound['worldTrianglesSHA256'];parts=components(t)['components'];zero=np.all(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])==0,axis=1);records=[]
   for i,part in enumerate(parts):
    faces=[f for f in part['faceIndices'] if not zero[f]];contact=exact_component_contacts(t,faces,ground,mall_faces,first_only=False) if faces else {'contacts':[],'allPairsExamined':True,'zeroAreaOnly':True}
    records.append({'component':i,'originalFaces':part['faceIndices'],'bounds':part['bounds'] if 'bounds' in part else [t[part['faceIndices']].min(axis=(0,1)).tolist(),t[part['faceIndices']].max(axis=(0,1)).tolist()],'exactOriginalPodiumContacts':contact,'positiveDimensionalContacts':sum(c['dimension']>0 for c in contact['contacts'])})
   allfaces=[f for p in records for f in p['originalFaces']];assert sorted(allfaces)==list(range(len(t))) and len(set(allfaces))==len(t)
   item={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'worldTrianglesSHA256':bound['worldTrianglesSHA256'],'completeOriginalFaces':len(t),'podiumUID':mall['uid'],'podiumSourceSHA256':mall['sourceSHA256'],'podiumWorldTrianglesSHA256':mall['worldTriangleSHA256'],'completeOriginalPodiumFaces':len(ground),'components':records,'zeroAreaOriginalFacesRetained':np.flatnonzero(zero).tolist(),'ownershipAccepted':False,'physicalSupportAccepted':False,'sourceGeometryChanges':0};save(DOC/(stem+'-contacts.json.gz'),item);results.append({'uid':row['uid'],'faces':len(t),'components':len(parts),'contactsByDimension':{str(d):sum(c['dimension']==d for p in records for c in p['exactOriginalPodiumContacts']['contacts']) for d in [0,1,2]}});paths += [ROOT/row['candidate']['path']];print(results[-1],flush=True)
  assert {x['uid'] for x in results}==UIDS;save(DOC/'summary.json',{'rows':results,'ownershipAccepted':False,'physicalSupportAccepted':False,'installationApproved':False,'sourceGeometryChanges':0})
 finally:assert reservations.release(lease)['ok']
 module('two_original_podium_contact_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-complete-original-podium-interfaces-v1',paths,{'uids':sorted(UIDS),'identityAccepted':False,'physicalAccepted':False,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'source-specific-podium-ownership-and-grounded-component-paths-pending','nextStep':'Interpret exact unchanged source interfaces with primary compound provenance; all foreign/physical/runtime gates remain required.'})
if __name__=='__main__':main()
