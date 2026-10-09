"""Complete original upper-source component paths to the original grounded Marina podium."""
import uuid,numpy as np
from run import ROOT,read,save,digest,reservations
from source_closed_components import components
from exact_original_component_contacts_20261009 import exact_component_contacts
BATCH='government-xl-miami-four-marina-upper-original-graph-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-miami-fourteen-original-current-diagnostic-20261009/complete-fourteen-original-contact-inputs.json.gz';UIDS={'landsd/176571:0','landsd/179052:0','landsd/201643:0','landsd/37001:0'}
def main():
 assert not DOC.exists();x=read(INPUT);p=next(r for r in x['rows'] if r['uid']=='landsd/231147:0');podium=np.asarray(p['position'],float).reshape(-1,3,3);assert digest(podium.astype('<f8').tobytes())==p['worldTriangleSHA256'];pg=components(podium)['components'];powner={f:i for i,g in enumerate(pg) for f in g['faceIndices']};summary=[];claim=reservations.claim('marina-upper-graph-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  for r in x['rows']:
   if r['uid'] not in UIDS:continue
   t=np.asarray(r['position'],float).reshape(-1,3,3);assert digest(t.astype('<f8').tobytes())==r['worldTriangleSHA256'];parts=components(t)['components'];zero=set(np.flatnonzero(np.all(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])==0,axis=1)).tolist());contacts=[];edges=[];nodes=[];pcontacts=[];seeds=[]
   for i,g in enumerate(parts):
    ids=g['faceIndices'];a=[f for f in ids if f not in zero];v=t[ids];nodes.append({'component':i,'originalFaceIds':ids,'worldBounds':[v.min(axis=(0,1)).tolist(),v.max(axis=(0,1)).tolist()]});proof=exact_component_contacts(t,a,podium,list(range(len(podium))),first_only=False) if a else {'contacts':[],'allPairsExamined':True}
    for q in proof['contacts']:q['originalPodiumEdgeComponent']=powner[q['sourceFaceB']]
    pcontacts.append({'component':i,'contact':proof});
    if any(q['dimension']>=1 for q in proof['contacts']):seeds.append(i)
    for j in range(i+1,len(parts)):
     b=[f for f in parts[j]['faceIndices'] if f not in zero]
     if not a or not b:continue
     w=t[b]
     if np.any(v.max(axis=(0,1))<w.min(axis=(0,1))) or np.any(w.max(axis=(0,1))<v.min(axis=(0,1))):continue
     q=exact_component_contacts(t,a,t,b,first_only=False)
     if q['contacts']:contacts.append({'componentA':i,'componentB':j,'contact':q})
     if any(c['dimension']>=1 for c in q['contacts']):edges.append((i,j))
    if i%20==0:assert reservations.heartbeat(lease,3600)['ok'];print({'uid':r['uid'],'componentsExamined':i+1,'total':len(parts)},flush=True)
   reached={i:[i] for i in seeds};changed=True
   while changed:
    changed=False
    for a,b in edges:
     if a in reached and b not in reached:reached[b]=reached[a]+[b];changed=True
     elif b in reached and a not in reached:reached[a]=reached[b]+[a];changed=True
   ids=[f for g in parts for f in g['faceIndices']];assert sorted(ids)==list(range(len(t))) and len(set(ids))==len(t);out={'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'worldTriangleSHA256':r['worldTriangleSHA256'],'wholeOriginalFaces':len(t),'completeOriginalComponents':nodes,'exactOriginalComponentContacts':contacts,'exactOriginalPodiumContacts':pcontacts,'positiveOriginalPodiumPaths':{str(i):route for i,route in reached.items()},'remainingComponents':[i for i in range(len(parts)) if i not in reached],'retainedOriginalZeroAreaFaceIds':sorted(zero),'allOriginalFacesAccountedExactlyOnce':True,'sourceGeometryChanges':0,'physicalAccepted':False,'originalPodiumSourceSHA256':p['sourceSHA256'],'originalPodiumWorldTriangleSHA256':p['worldTriangleSHA256'],'qualification':'Complete unchanged original EDGE component paths to the actual original Marina podium. Exact point-only and zero-area faces receive no contact credit. Podium must be present and independently grounded at runtime; all own-source/current ownership/foreign/full physical gates remain.'};save(DOC/(r['uid'].split('/')[1].replace(':','-')+'-complete-original-upper-graph.json.gz'),out);counts={'uid':r['uid'],'components':len(parts),'wholeFaces':len(t),'positiveDimensionalOriginalPodiumPaths':len(reached),'remainingComponents':len(parts)-len(reached)};summary.append(counts);print(counts,flush=True)
  save(DOC/'summary.json',{'rows':summary,'sourceInputPath':str(INPUT.relative_to(ROOT)),'sourceInputSHA256':digest(INPUT.read_bytes()),'physicalAccepted':False})
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
