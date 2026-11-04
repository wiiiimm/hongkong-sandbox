"""Complete current contacts v2: exact zero-area faces retained without contact credit."""
import numpy as np
from run import ROOT,read,save,digest
from exact_original_component_contacts_20261009 import exact_component_contacts
DOC=ROOT/'docs/astra-city/government-import/government-xl-miami-three-current-rendered-podium-20261009'
GRAPH=DOC.parent/'government-xl-miami-complete-edge-attachment-20261009'
def paths(edges,seeds):
 reached={i:[i] for i in seeds};changed=True
 while changed:
  changed=False
  for a,b in edges:
   if a in reached and b not in reached:reached[b]=reached[a]+[b];changed=True
   elif b in reached and a not in reached:reached[a]=reached[b]+[a];changed=True
 return reached
def main():
 assert not (DOC/'result.json').exists();p=DOC/'complete-current-rendered-podium-inputs.json.gz';x=read(p)
 for f,h in x['inputHashes'].items():assert digest((ROOT/f).read_bytes())==h,f
 b=x['currentRendererBody'];body=np.asarray(b['position'],float).reshape(-1,3)[np.asarray(b['index']).reshape(-1,3)];rows=[];body_zero=np.flatnonzero(np.all(np.cross(body[:,1]-body[:,0],body[:,2]-body[:,0])==0,axis=1)).tolist();body_surface=[i for i in range(len(body)) if i not in set(body_zero)]
 for s in x['rows']:
  a=np.asarray(s['position'],float).reshape(-1,3)[np.asarray(s['index']).reshape(-1,3)];assert digest(a.astype('<f8').tobytes())==s['worldTriangleSHA256'];gpath=GRAPH/(s['uid'].split('/')[1].replace(':','-')+'-complete-edge-attachment.json.gz');g=read(gpath);assert g['worldTriangleSHA256']==s['worldTriangleSHA256'];records=[];seeds=[];zero=np.flatnonzero(np.all(np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0])==0,axis=1)).tolist()
  for c in g['completeEdgeComponents']:
   surface_faces=[i for i in c['originalFaceIds'] if i not in set(zero)];proof=exact_component_contacts(a,surface_faces,body,body_surface,first_only=False) if surface_faces else {'contacts':[],'allPairsExamined':True};proof['domain']='Every positive-area original/current triangle surface; original zero-area faces separately retained with no contact credit'
   records.append({'component':c['component'],'originalFaceIds':c['originalFaceIds'],'contact':proof})
   if any(q['dimension']>=1 for q in proof['contacts']):seeds.append(c['component'])
  edges=[(q['componentA'],q['componentB']) for q in g['exactOriginalIntercomponentContacts'] if any(c['dimension']>=1 for c in q['contact']['contacts'])];reached=paths(edges,seeds)
  out={'uid':s['uid'],'sourceSHA256':s['sourceSHA256'],'worldTriangleSHA256':s['worldTriangleSHA256'],'wholeOriginalFaces':len(a),'completeCurrentPodiumFaces':len(body),'currentPodiumUID':x['currentForm']['uid'],'allOriginalFacesAccountedExactlyOnce':True,'originalGraphPath':str(gpath.relative_to(ROOT)),'originalGraphSHA256':digest(gpath.read_bytes()),'retainedOriginalZeroAreaFaceIds':zero,'retainedCurrentZeroAreaFaceIds':body_zero,'zeroAreaFaceContactCredit':False,'currentPodiumContacts':records,'positiveDimensionalCurrentPodiumPaths':{str(k):v for k,v in reached.items()},'componentsWithoutPositiveCurrentPodiumPath':[c['component'] for c in g['completeEdgeComponents'] if c['component'] not in reached],'physicalSupportAccepted':False,'sourceGeometryChanges':0,'currentActorChanges':0,'qualification':'Full exact component contacts to the actual current rendered retained podium, using complete original line/area attachment paths. No path through an absent original podium grants runtime support. Complete current footing, full source foundation, foreign/identity/runtime gates remain independent.'};save(DOC/(s['uid'].split('/')[1].replace(':','-')+'-complete-current-podium-paths-v2.json.gz'),out)
  count={'uid':s['uid'],'edgeComponents':len(g['completeEdgeComponents']),'directCurrentPodiumPositiveComponents':len(seeds),'positiveCurrentPodiumPaths':len(reached),'remaining':len(g['completeEdgeComponents'])-len(reached)};rows.append(count);print(count,flush=True)
 save(DOC/'summary-v2.json',{'rows':rows,'inputSHA256':digest(p.read_bytes()),'physicalAccepted':False,'publication':False})
if __name__=='__main__':main()
