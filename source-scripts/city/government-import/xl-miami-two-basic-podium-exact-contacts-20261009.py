"""Complete exact geometric contacts with retained current basic podium; no waiver."""
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_original_component_contacts_20261009 import exact_component_contacts
DOC=ROOT/'docs/astra-city/government-import/government-xl-miami-two-original-staged-20261009'
def main():
 p=DOC/'basic-podium-original-contact-inputs.json.gz';x=read(p)
 for f,h in x['inputHashes'].items():assert digest((ROOT/f).read_bytes())==h,f
 b=x['currentRendererBody'];t=np.asarray(b['position'],dtype=float).reshape(-1,3)[np.asarray(b['index'],dtype=int).reshape(-1,3)];rows=[]
 for s in x['rows']:
  a=np.asarray(s['position'],dtype=float).reshape(-1,3)[np.asarray(s['index'],dtype=int).reshape(-1,3)];assert digest(a.astype('<f8').tobytes())==s['worldTriangleSHA256']
  result=exact_component_contacts(a,list(range(len(a))),t,list(range(len(t))),first_only=False)
  row={'uid':s['uid'],'sourceSHA256':s['sourceSHA256'],'worldTriangleSHA256':s['worldTriangleSHA256'],'allOriginalFaces':len(a),'completeBasicFaces':len(t),'currentPodiumUID':x['currentForm']['uid'],'currentPodiumBaseHKPD':x['currentForm']['base'],'currentPodiumTopHKPD':x['currentForm']['base']+x['currentForm']['height'],'result':result,'countsByDimension':{str(d):sum(c['dimension']==d for c in result['contacts']) for d in range(3)}};rows.append(row);print({k:row[k] for k in ['uid','countsByDimension','allOriginalFaces','completeBasicFaces']},flush=True)
 save(DOC/'basic-podium-exact-original-contacts.json.gz',{'rows':rows,'inputHashes':{**x['inputHashes'],str(p.relative_to(ROOT)):digest(p.read_bytes()),str((HERE/'exact_original_component_contacts_20261009.py').relative_to(ROOT)):digest((HERE/'exact_original_component_contacts_20261009.py').read_bytes()),str((HERE/'exact_original_shell_intersections_20261009.py').relative_to(ROOT)):digest((HERE/'exact_original_shell_intersections_20261009.py').read_bytes())},'geometryChanges':0,'allCurrentActorsRetained':True,'diagnosticOnly':True,'physicalSupportAccepted':False,'collisionExemption':False,'qualification':'Exact unpadded complete original/current renderer triangle interfaces. Shared original podium ownership is independently pinned; contact dimensions do not grant load-bearing, source modification, current actor removal or collision/runtime exemptions. All raw contacts are retained for review.'})
if __name__=='__main__':main()
