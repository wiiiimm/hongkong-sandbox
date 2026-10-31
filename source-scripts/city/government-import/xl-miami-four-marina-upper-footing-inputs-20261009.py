"""Every original Marina upper component versus the separately grounded original podium."""
import numpy as np
from run import ROOT,read,save,digest
DOC=ROOT/'docs/astra-city/government-import/government-xl-miami-four-marina-upper-original-graph-20261009'
INPUT=DOC.parent/'government-xl-miami-fourteen-original-current-diagnostic-20261009/complete-fourteen-original-contact-inputs.json.gz'
def main():
 assert not (DOC/'result.json').exists();x=read(INPUT);podium=next(r for r in x['rows'] if r['uid']=='landsd/231147:0');rows=[]
 for path in sorted(DOC.glob('*-complete-original-upper-graph.json.gz')):
  g=read(path);source=next(r for r in x['rows'] if r['uid']==g['uid']);t=np.asarray(source['position'],float).reshape(-1,3,3);assert digest(t.astype('<f8').tobytes())==g['worldTriangleSHA256'];parts=[]
  for p in g['completeOriginalComponents']:
   v=t[p['originalFaceIds']];parts.append({**p,'position':v.reshape(-1).tolist(),'index':list(range(len(v)*3)),'bottomHKPD':float(v[:,:,1].min())})
  rows.append({'uid':g['uid'],'sourceSHA256':g['sourceSHA256'],'worldTriangleSHA256':g['worldTriangleSHA256'],'wholeOriginalFaces':len(t),'parts':parts})
 save(DOC/'complete-upper-original-podium-footing-inputs.json.gz',{'rows':rows,'originalPodium':podium,'sourceInputPath':str(INPUT.relative_to(ROOT)),'sourceInputSHA256':digest(INPUT.read_bytes()),'physicalAccepted':False,'sourceGeometryChanges':0})
if __name__=='__main__':main()
