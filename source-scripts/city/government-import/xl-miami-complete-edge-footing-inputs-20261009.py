"""Read-only exact reached podium-component footing inputs, all original faces retained."""
import numpy as np
from run import ROOT,read,save,digest
from source_closed_components import components
BATCH='government-xl-miami-complete-edge-footing-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
GRAPH=DOC.parent/'government-xl-miami-complete-edge-attachment-20261009'
INPUT=DOC.parent/'government-xl-miami-original-edge-anchor-20261009/complete-edge-anchor-inputs.json.gz'
def main():
 assert not DOC.exists(),'Fresh scope required'
 x=read(INPUT);p=x['podium'];t=np.asarray(p['position']).reshape(-1,3)[np.asarray(p['index']).reshape(-1,3)];assert digest(t.astype('<f8').tobytes())==p['worldTriangleSHA256']
 groups=components(t)['components'];allfaces=[f for g in groups for f in g['faceIndices']];assert sorted(allfaces)==list(range(len(t)))
 graphrefs=[];reached=set()
 for path in sorted(GRAPH.glob('*-complete-edge-attachment.json.gz')):
  q=read(path);graphrefs.append({'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes()),'uid':q['uid']})
  reached.update(i for c in q['exactOriginalPodiumContacts'] for i in c['reachedPodiumComponents'])
 rows=[]
 for i in sorted(reached):
  g=groups[i];v=t[g['faceIndices']];rows.append({**g,'component':i,'originalFaceIds':g['faceIndices'],'position':v.reshape(-1).tolist(),'index':list(range(len(v)*3)),'bottomHKPD':float(v[:,:,1].min()),'worldBounds':[v.min(axis=(0,1)).tolist(),v.max(axis=(0,1)).tolist()]})
 save(DOC/'complete-reached-original-podium-footing-inputs.json.gz',{'uid':p['uid'],'sourceSHA256':p['sourceSHA256'],'worldTriangleSHA256':p['worldTriangleSHA256'],'wholeOriginalFaces':len(t),'wholeOriginalEdgeComponentCount':len(groups),'allOriginalFacesAccountedExactlyOnce':True,'reachedComponents':rows,'terrain':x['terrain'],'sourceInputPath':str(INPUT.relative_to(ROOT)),'sourceInputSHA256':digest(INPUT.read_bytes()),'graphRefs':graphrefs,'physicalSupportAccepted':False,'sourceGeometryChanges':0})
 print({'reachedPodiumComponents':sorted(reached),'sourceFaces':len(t),'individualFootingsUnresolvedUntilReplay':True})
if __name__=='__main__':main()
