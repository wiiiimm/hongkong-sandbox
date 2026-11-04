"""Complete original edge-component positive-dimensional paths; no support waiver.

All target original edge components and every original podium component are
enumerated. Original exact point/line/area contacts remain distinct. A path to
the original podium does not by itself prove that particular podium component
has an accepted footing, or approve a rim, terrain, neighbour or runtime gate.
"""
import json,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from source_closed_components import components
from exact_original_component_contacts_20261009 import exact_component_contacts
BATCH='government-xl-miami-complete-edge-attachment-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-miami-original-edge-anchor-20261009/complete-edge-anchor-inputs.json.gz'
def triangles(s):return np.asarray(s['position'],float).reshape(-1,3)[np.asarray(s['index'],int).reshape(-1,3)]
def paths(nodes,edges,seeds):
 reached={i:[i] for i in seeds};changed=True
 while changed:
  changed=False
  for a,b in edges:
   if a in reached and b not in reached:reached[b]=reached[a]+[b];changed=True
   elif b in reached and a not in reached:reached[a]=reached[b]+[a];changed=True
 return reached
def main():
 assert not DOC.exists(),'Fresh diagnostic scope required';x=read(INPUT);original=read(ROOT/x['sourceInputPath']);assert digest((ROOT/x['sourceInputPath']).read_bytes())==x['sourceInputSHA256']
 podium=triangles(x['podium']);assert digest(podium.astype('<f8').tobytes())==x['podium']['worldTriangleSHA256'];pg=components(podium)['components'];powner={f:i for i,g in enumerate(pg) for f in g['faceIndices']};assert sorted(powner)==list(range(len(podium)))
 podium_groups=[{'component':i,'originalFaceIds':g['faceIndices'],'worldBounds':[podium[g['faceIndices']].min(axis=(0,1)).tolist(),podium[g['faceIndices']].max(axis=(0,1)).tolist()],'footingAccepted':False} for i,g in enumerate(pg)]
 save(DOC/'complete-original-podium-edge-components.json.gz',{'uid':x['podium']['uid'],'sourceSHA256':x['podium']['sourceSHA256'],'worldTriangleSHA256':x['podium']['worldTriangleSHA256'],'wholeFaces':len(podium),'allFacesAccountedExactlyOnce':True,'components':podium_groups,'qualification':'Complete original podium component partition. Individual component footing roles remain independent of whole podium diagnostic clearance.'})
 claim=reservations.claim('miami-edge-evidence-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];summary=[]
 try:
  for row in x['rows']:
   s=next(s for s in original['rows'] if s['uid']==row['uid']);t=triangles(s);assert digest(t.astype('<f8').tobytes())==row['worldTriangleSHA256'];groups=row['parts'];ids=[f for p in groups for f in p['originalFaceIds']];assert sorted(ids)==list(range(len(t))) and len(set(ids))==len(t)
   bounds=[(np.asarray(p['worldBounds'][0]),np.asarray(p['worldBounds'][1])) for p in groups];contacts=[];podiumcontacts=[];edges=[];seeds=[]
   for i,p in enumerate(groups):
    lo,hi=bounds[i]
    contact=exact_component_contacts(t,p['originalFaceIds'],podium,list(range(len(podium))),first_only=False)
    for c in contact['contacts']:c['podiumEdgeComponent']=powner[c['sourceFaceB']]
    podiumcontacts.append({'component':i,'originalFaceIds':p['originalFaceIds'],'contact':contact,'reachedPodiumComponents':sorted({c['podiumEdgeComponent'] for c in contact['contacts'] if c['dimension']>=1})})
    if any(c['dimension']>=1 for c in contact['contacts']):seeds.append(i)
    for j in range(i+1,len(groups)):
     qlo,qhi=bounds[j]
     if np.any(hi<qlo) or np.any(qhi<lo):continue
     result=exact_component_contacts(t,p['originalFaceIds'],t,groups[j]['originalFaceIds'],first_only=False)
     if result['contacts']:
      contacts.append({'componentA':i,'componentB':j,'contact':result})
      if any(c['dimension']>=1 for c in result['contacts']):edges.append((i,j))
    if i%20==0:assert reservations.heartbeat(lease,3600)['ok'];print(json.dumps({'uid':row['uid'],'componentsExamined':i+1,'total':len(groups),'positivePodiumComponents':len(seeds)}),flush=True)
   reached=paths(list(range(len(groups))),edges,seeds);result={'uid':row['uid'],'sourceSHA256':s['sourceSHA256'],'worldTriangleSHA256':row['worldTriangleSHA256'],'wholeOriginalFaces':len(t),'allOriginalFacesAccountedExactlyOnce':True,'completeEdgeComponents':[{'component':i,'originalFaceIds':p['originalFaceIds'],'worldBounds':p['worldBounds']} for i,p in enumerate(groups)],'allComponentPairsExamined':True,'exactOriginalPodiumContacts':podiumcontacts,'exactOriginalIntercomponentContacts':contacts,'positiveDimensionalPathsToOriginalPodium':{str(i):route for i,route in reached.items()},'remainingComponentsWithoutPositiveDimensionalPath':[i for i in range(len(groups)) if i not in reached],'physicalSupportAccepted':False,'sourceGeometryChanges':0,'currentActorChanges':0,'qualification':'Complete unmodified original edge-component paths using exact rational positive-dimensional triangle intersections. Original point-only contacts and every isolated component retained. Reached original podium component must independently prove a supported footing before this path can become a source-body/ornament role. No rim, physical, foreign actor, runtime or publication gate waived.'};save(DOC/(row['uid'].split('/')[1].replace(':','-')+'-complete-edge-attachment.json.gz'),result)
   counts={'uid':row['uid'],'edgeComponents':len(groups),'directPositivePodiumComponents':len(seeds),'componentsWithPositiveDimensionalPodiumPath':len(reached),'remainingIsolatedOrPointOnly':len(groups)-len(reached)};summary.append(counts);print(json.dumps(counts),flush=True)
  save(DOC/'summary.json',{'rows':summary,'physicalSupportAccepted':False,'sourceGeometryChanges':0,'nextStep':'Verify exact reached original podium edge components against full drawn source terrain and ownership, then resolve only complete source-authored attached roles with independently accepted footing anchors. Keep isolated/point-only and all raw ordinary rim failures unresolved.'})
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
