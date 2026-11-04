"""Attribute seven unresolved rim witnesses to exact unchanged source facets.

Source-only diagnostic: no terrain sampling, embedding-policy change or approval.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-elegant-garden-seven-witness-contacts-v1-20261027'
OLD='government-xl-elegant-garden-block2-four-world-support-v1-20261027'
UID,SUPPORT='landsd/173532:0','landsd/236170:0'

def main():
 p=argparse.ArgumentParser();p.add_argument('--lease',required=True);a=p.parse_args();lease=read(Path(a.lease))
 assert reservations.owns(lease)and {'building:'+u for u in [UID,SUPPORT]}<=set(lease['resources'])
 out=BASE/BATCH;assert not out.exists();_,pins=authenticate(BASE/OLD);refs=[Path(__file__),BASE/OLD/'result.json']
 def take(path):
  assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
 summary=take(BASE/OLD/'summary.json');assert summary['supportedUid']==UID and summary['supportUid']==SUPPORT
 rows=[]
 for original in summary['rows']:
  assert reservations.owns(lease)
  mode=original['mode'];data=take(BASE/OLD/mode/'input.json.gz');assert len(data['rows'])==1 and data['rows'][0]['uid']==UID
  g=data['rows'][0];tri=np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];podium=np.asarray(data['podium'],dtype='<f8')
  assert digest(tri.tobytes())==original['sourceWorldSHA256ByUid'][UID]and digest(podium.tobytes())==original['sourceWorldSHA256ByUid'][SUPPORT]
  failures=original['support']['unresolved'];assert len(failures)==7 and original['support']['strictContacts']==112
  lo,hi=tri.min(1),tri.max(1);targets=[];all_ids=set()
  for witness in failures:
   point=np.asarray(witness['position']);broad=np.flatnonzero(np.all(lo<=point+.001,axis=1)&np.all(hi>=point-.001,axis=1))
   ids=[int(i)for i in broad if np.linalg.norm(np.cross(tri[i,1]-tri[i,0],tri[i,2]-tri[i,0]))>0 and np.linalg.norm(closest(point,tri[i])-point)<=.001]
   assert ids;all_ids.update(ids);targets.append(dict(witness=witness,incidentSourceFaces=ids))
  proof=exact_finite_contacts(tri,sorted(all_ids),podium,list(range(len(podium))))
  for target in targets:
   contacts=[c for c in proof['contacts']if c['sourceFaceA']in target['incidentSourceFaces']and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and c['dimension']>0]
   target['positiveContactCount']=len(contacts);target['contactSourceFaces']=sorted({c['sourceFaceA']for c in contacts})
  result=dict(mode=mode,rawSupportPassed=original['passed'],unresolvedWitnesses=7,strictContacts=112,incidentSourceFaces=sorted(all_ids),witnessesWithFiniteOriginalContacts=sum(t['positiveContactCount']>0 for t in targets))
  save(out/(mode+'.json.gz'),dict(**result,targets=targets,proof=proof));rows.append(result);print(result,flush=True)
 result=dict(uids=[UID,SUPPORT],sourceSHA256ByUid=summary['sourceSHA256ByUid'],rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,physicalSupportAccepted=False,installationApproved=False,qualification='Exact original incident-face contacts at the existing seven failed witnesses in all four representations. Raw support negatives and embedding limits unchanged. Contacts are not physical approval or a closed-solid/clearance claim.')
 save(out/'summary.json',result);assert reservations.owns(lease)
 refs.extend([HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'pool_incident_wall_contacts_v1_20261017.py'])
 module('elegant_seven_witness_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-seven-witness-original-face-contacts',refs,result)
if __name__=='__main__':main()
