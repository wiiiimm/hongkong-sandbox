"""Complete original podium surface paths; exact zero-area faces retained without credit."""
import uuid,numpy as np
from run import ROOT,read,save,digest,reservations
from source_closed_components import components
from exact_original_component_contacts_20261009 import exact_component_contacts
BATCH='government-xl-miami-three-original-podium-graph-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-miami-fourteen-original-current-diagnostic-20261009/complete-fourteen-original-contact-inputs.json.gz'
UIDS={'landsd/232089:0','landsd/259038:0','landsd/231147:0'}
def main():
 assert not DOC.exists();x=read(INPUT);rows=[];allinputs=[];claim=reservations.claim('miami-podium-graph-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  for source in x['rows']:
   if source['uid'] not in UIDS:continue
   t=np.asarray(source['position'],float).reshape(-1,3,3);assert digest(t.astype('<f8').tobytes())==source['worldTriangleSHA256'];groups=components(t)['components'];zero=set(np.flatnonzero(np.all(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])==0,axis=1)).tolist());out=[];contacts=[]
   for i,p in enumerate(groups):
    ids=p['faceIndices'];v=t[ids];out.append({**p,'component':i,'originalFaceIds':ids,'position':v.reshape(-1).tolist(),'index':list(range(len(v)*3)),'bottomHKPD':float(v[:,:,1].min()),'worldBounds':[v.min(axis=(0,1)).tolist(),v.max(axis=(0,1)).tolist()]});a=[f for f in ids if f not in zero]
    for j in range(i+1,len(groups)):
     b=[f for f in groups[j]['faceIndices'] if f not in zero]
     if not a or not b:continue
     lo,hi=v.min(axis=(0,1)),v.max(axis=(0,1));w=t[b]
     if np.any(hi<w.min(axis=(0,1))) or np.any(w.max(axis=(0,1))<lo):continue
     proof=exact_component_contacts(t,a,t,b,first_only=False)
     if proof['contacts']:contacts.append({'componentA':i,'componentB':j,'contact':proof})
    if i%20==0:assert reservations.heartbeat(lease,3600)['ok'];print({'uid':source['uid'],'componentsExamined':i+1,'total':len(groups)},flush=True)
   allfaces=[f for p in out for f in p['originalFaceIds']];assert sorted(allfaces)==list(range(len(t))) and len(set(allfaces))==len(t)
   row={'uid':source['uid'],'sourceSHA256':source['sourceSHA256'],'worldTriangleSHA256':source['worldTriangleSHA256'],'wholeOriginalFaces':len(t),'completeOriginalComponents':out,'exactPositiveAreaSurfaceComponentContacts':contacts,'retainedOriginalZeroAreaFaceIds':sorted(zero),'zeroAreaFacesGrantContactCredit':False,'allOriginalFacesAccountedExactlyOnce':True,'sourceGeometryChanges':0,'physicalSupportAccepted':False};save(DOC/(source['uid'].split('/')[1].replace(':','-')+'-complete-original-podium-graph.json.gz'),row);rows.append({'uid':source['uid'],'components':len(out),'faces':len(t),'contactComponentPairs':len(contacts),'zeroAreaFacesRetained':len(zero)});allinputs.append({'uid':source['uid'],'sourceSHA256':source['sourceSHA256'],'worldTriangleSHA256':source['worldTriangleSHA256'],'wholeOriginalFaces':len(t),'parts':out});print(rows[-1],flush=True)
  save(DOC/'complete-original-podium-footing-inputs.json.gz',{'rows':allinputs,'terrain':x['terrain'],'sourceInputPath':str(INPUT.relative_to(ROOT)),'sourceInputSHA256':digest(INPUT.read_bytes()),'sourceGeometryChanges':0,'physicalSupportAccepted':False});save(DOC/'summary.json',{'rows':rows,'physicalSupportAccepted':False,'nextStep':'Independently evaluate every complete original podium component against full pinned source TIN, then build paths only to strict supported footing components. Whole source and current actor physical/runtime remain independent.'})
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
