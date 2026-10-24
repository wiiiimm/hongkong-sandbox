"""All original/current interfaces and exact original graph paths; no support credit."""
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_original_component_contacts_20261009 import exact_component_contacts
BATCH='government-xl-yoho-eight-actual-current-podium-support-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
GRAPH=DOC.parent/'government-xl-yoho-eight-complete-original-component-graph-20261009'
def main():
 assert not (DOC/'result.json').exists();x=read(DOC/'complete-current-rendered-podium-inputs.json.gz');r=x['rows'][0];a=np.asarray(r['position'],float).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];assert digest(a.astype('<f8').tobytes())==r['worldTriangleSHA256'];b=x['currentRendererBody'];body=np.asarray(b['position'],float).reshape(-1,3)[np.asarray(b['index']).reshape(-1,3)]
 for p,h in x['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p
 receipt=read(GRAPH/'result.json')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for ref in receipt['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
 graph=read(GRAPH/'diagnostic.json.gz');assert graph['completeWorldSHA256']==r['worldTriangleSHA256'] and graph['sourceSHA256']==r['sourceSHA256']
 parts=graph['originalComponentOutcomes'];face_to_component={f:q['component'] for q in parts for f in q['originalFaces']};assert sorted(face_to_component)==list(range(len(a))) and sum(len(q['originalFaces']) for q in parts)==len(a)
 zero=np.flatnonzero(np.all(np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0])==0,axis=1)).tolist();bzero=np.flatnonzero(np.all(np.cross(body[:,1]-body[:,0],body[:,2]-body[:,0])==0,axis=1)).tolist()
 all_contacts=exact_component_contacts(a,[i for i in range(len(a)) if i not in set(zero)],body,[i for i in range(len(body)) if i not in set(bzero)],maximum_pairs=1000000)
 seeds={face_to_component[q['sourceFaceA']] for q in all_contacts['contacts'] if q['dimension']>0};reached={i:[i] for i in seeds};edges={tuple(q['originalComponents']) for q in graph['completeExactOriginalInterfaces'] if q['dimension']>0};changed=True
 while changed:
  changed=False
  for i,j in edges:
   if i in reached and j not in reached:reached[j]=reached[i]+[j];changed=True
   elif j in reached and i not in reached:reached[i]=reached[j]+[i];changed=True
 missing=[q['component'] for q in parts if q['component'] not in reached]
 out={'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'completeWorldSHA256':r['worldTriangleSHA256'],'completeOriginalComponents':len(parts),'completeOriginalFaces':len(a),'completeCurrentPodiumFaces':len(body),'currentPodiumUID':x['currentForm']['uid'],'allOriginalFacesAccountedExactlyOnce':True,'allCurrentOriginalInterfaces':all_contacts,'directPositiveCurrentPodiumComponents':sorted(seeds),'completePositivePathsToActualCurrentPodium':{str(k):v for k,v in reached.items()},'remainingComponents':missing,'originalZeroAreaFacesRetainedWithoutContactCredit':zero,'currentZeroAreaFacesRetainedWithoutContactCredit':bzero,'rawAbsentOriginalPodiumPathsNotUsed':True,'physicalSupportAccepted':False,'sourceGeometryChanges':0,'currentActorChanges':0,'collisionExemption':False,'inputHashes':{**x['inputHashes'],str((GRAPH/'diagnostic.json.gz').relative_to(ROOT)):digest((GRAPH/'diagnostic.json.gz').read_bytes()),str((GRAPH/'result.json').relative_to(ROOT)):digest((GRAPH/'result.json').read_bytes()),str((DOC/'complete-current-rendered-podium-inputs.json.gz').relative_to(ROOT)):digest((DOC/'complete-current-rendered-podium-inputs.json.gz').read_bytes())},'qualification':'All positive-area unchanged original/current drawn podium surfaces enumerated with exact rational intersections; point contacts retained but no bridge credit. Every original component retained and complete exact original graph replayed. Neither intersection nor graph path alone establishes load bearing/collision clearance; complete podium rooting, original source physical roles and all runtime/foreign gates remain independent.'}
 save(DOC/'complete-original-to-actual-podium-paths.json.gz',out);save(DOC/'summary.json',{'uid':r['uid'],'originalComponents':len(parts),'positiveActualCurrentPodiumPaths':len(reached),'directPositiveComponents':len(seeds),'remainingOriginalComponents':len(missing),'exactPairs':all_contacts['trianglePairsTested'],'contactCountsByDimension':{str(d):sum(q['dimension']==d for q in all_contacts['contacts']) for d in range(3)},'physicalAccepted':False});print(read(DOC/'summary.json'),flush=True)
if __name__=='__main__':main()
