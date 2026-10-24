"""Account every unchanged original face by exact authored edge components."""
import numpy as np
from run import ROOT,read,save,digest
from source_closed_components import components
BATCH='government-xl-miami-original-edge-anchor-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-miami-fourteen-original-current-diagnostic-20261009/complete-fourteen-original-contact-inputs.json.gz'
def main():
 assert not (DOC/'result.json').exists(),'Completed stage immutable';original=read(INPUT);wanted={'landsd/202599:0','landsd/203438:0','landsd/203441:0','landsd/203462:0'};rows=[]
 for r in original['rows']:
  if r['uid'] not in wanted:continue
  t=np.asarray(r['position']).reshape(-1,3,3);assert digest(t.astype('<f8').tobytes())==r['worldTriangleSHA256'];top=components(t);parts=[]
  for i,p in enumerate(top['components']):
   faces=p['faceIndices'];v=t[faces];parts.append({**p,'component':i,'originalFaceIds':faces,'position':v.reshape(-1).tolist(),'index':list(range(len(v)*3)),'bottomHKPD':float(v[:,:,1].min()),'worldBounds':[v.min(axis=(0,1)).tolist(),v.max(axis=(0,1)).tolist()]})
  assert sorted(i for p in parts for i in p['originalFaceIds'])==list(range(len(t)));rows.append({'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'worldTriangleSHA256':r['worldTriangleSHA256'],'wholeOriginalFaces':len(t),'parts':parts,'allOriginalFacesAccountedExactlyOnce':True});print({'uid':r['uid'],'exactEdgeComponents':len(parts),'faces':len(t)},flush=True)
 support=next(r for r in original['rows'] if r['uid']=='landsd/232089:0');save(DOC/'complete-edge-anchor-inputs.json.gz',{'rows':rows,'podium':support,'terrain':original['terrain'],'sourceInputPath':str(INPUT.relative_to(ROOT)),'sourceInputSHA256':digest(INPUT.read_bytes()),'sourceGeometryChanges':0,'physicalAccepted':False})
if __name__=='__main__':main()
