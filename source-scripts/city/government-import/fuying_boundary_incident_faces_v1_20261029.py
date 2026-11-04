"""Account for every actual face incident to the rejected finite boundary points."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fuying181489-five-boundary-incident-faces-v1-20261029';WITNESS='government-xl-fuying181489-five-boundary-witnesses-v2-20261029';CANDIDATE='government-xl-fuying181489-five-member-boundary-contract-v1-20261029'
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 for batch in [WITNESS,CANDIDATE]:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
 def take(batch,p):assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 summary=take(CANDIDATE,BASE/CANDIDATE/'summary.json');rows=[]
 for member in summary['members']:
  name=member['member'];witness=BASE/WITNESS/(name+'-witnesses.json')
  # Witness output contents are included through its completed result's summary
  # hash list only when explicitly frozen; verify against the stored references.
  ws=read(witness);refs.append(witness);node=take(CANDIDATE,ROOT/member['candidate']['path']);pos=np.asarray(node['nativeMesh']['position'],dtype='float32').astype('float64').reshape(-1,3);idx=np.asarray(node['nativeMesh']['index']).reshape(-1,3);tri=pos[idx];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(cross,axis=1)/2
  for w in ws['witnesses']:
   point=np.asarray(w['point']);ids=np.flatnonzero(np.any(np.all(tri==point,axis=2),axis=1));faces=[]
   for i in ids:
    faces.append(dict(faceIndex=int(i),points=tri[i].tolist(),area3DM2=float(area[i]),areaXZM2=float(abs(cross[i,1])/2),normal=cross[i].tolist(),exactlyOnConstantX=bool(np.all(tri[i,:,0]==point[0])),exactlyOnConstantZ=bool(np.all(tri[i,:,2]==point[2]))))
   rows.append(dict(member=name,point=w['point'],incidentFaces=faces,incidentFaceCount=len(faces),allIncidentFacesNonRendering=bool(len(ids)>0 and np.all(area[ids]==0)),allIncidentFacesProjectedVertical=bool(len(ids)>0 and np.all(cross[ids,1]==0))))
 result=dict(uids=summary['uids'],sourceSHA256ByUid=summary['sourceSHA256ByUid'],witnesses=rows,totalWitnessOccurrences=len(rows),allNonRendering=sum(r['allIncidentFacesNonRendering']for r in rows),allProjectedVertical=sum(r['allIncidentFacesProjectedVertical']for r in rows),sourceGeometryChanges=0,candidateChanges=False,physicalAcceptance=False,terrainValidatorPassed=False,installationApproved=False,publication=False)
 save(out/'summary.json',result);module('fuying_incident_faces_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'all-rejected-boundary-witness-exact-incident-primitive-context',refs,result);print({k:result[k]for k in ['totalWitnessOccurrences','allNonRendering','allProjectedVertical']},flush=True)
if __name__=='__main__':main()
