"""Inspect every original detached-panel vertex against complete original sources.

Distances are floating-point diagnostic witnesses, never contact/role approval.
The earlier exact rational no-contact proof remains authoritative and unchanged.
"""
import importlib.util
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest

BATCH='government-xl-popcorn-original-panel-context-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-pair-interface-20261009/exact-original-contact-inputs.json.gz'
PRIOR=ROOT/'docs/astra-city/government-import/government-xl-popcorn-source-access-ownership-20261009/every-far-access-component-exact-attachments.json.gz'

def closest(point,triangles):
 """Nearest point on each complete triangle, including exact degenerate edges."""
 a,b,c=triangles[:,0],triangles[:,1],triangles[:,2]
 ab,ac=b-a,c-a;n=np.cross(ab,ac);n2=np.einsum('ij,ij->i',n,n)
 safe=np.where(n2>0,n2,1.)
 q=point-n*(np.einsum('ij,ij->i',point-a,n)/safe)[:,None]
 aq=q-a;d00=np.einsum('ij,ij->i',ab,ab);d01=np.einsum('ij,ij->i',ab,ac);d11=np.einsum('ij,ij->i',ac,ac)
 d20=np.einsum('ij,ij->i',aq,ab);d21=np.einsum('ij,ij->i',aq,ac);den=d00*d11-d01*d01
 safe_den=np.where(den!=0,den,1.)
 u=(d11*d20-d01*d21)/safe_den;v=(d00*d21-d01*d20)/safe_den
 inside=(n2>0)&(den!=0)&(u>=0)&(v>=0)&(u+v<=1)
 options=[q];dist=[np.where(inside,np.sum((q-point)**2,axis=1),np.inf)]
 for start,end in [(a,b),(b,c),(c,a)]:
  edge=end-start;length=np.sum(edge*edge,axis=1)
  t=np.clip(np.sum((point-start)*edge,axis=1)/np.where(length>0,length,1),0,1)
  candidate=start+edge*t[:,None];options.append(candidate);dist.append(np.sum((candidate-point)**2,axis=1))
 distances=np.stack(dist);which=np.argmin(distances,axis=0);points=np.stack(options)[which,np.arange(len(triangles))]
 return np.sqrt(distances[which,np.arange(len(triangles))]),points

def main():
 assert not (DOC/'result.json').exists(),'Completed evidence is immutable'
 inp=read(INPUT);prior=read(PRIOR)
 part=next(c for c in prior['separateOriginalSourceComponents'] if c['component']==13033)
 ids=part['allOriginalFaceIndices'];assert ids==list(range(13033,13045))
 assert not part['exactContactToOtherOriginalComponent'] and not part['exactDirectMainBodyContact']
 mall=next(r for r in inp['rows'] if r['uid']=='landsd/295538:0')
 station=next(r for r in inp['rows'] if r['uid']=='landsd/295539:0')
 tri=np.array(mall['position']).reshape(-1,3,3);panel=tri[ids]
 norms=np.cross(panel[:,1]-panel[:,0],panel[:,2]-panel[:,0]);assert np.all(norms[:,1]==0)
 remaining_ids=np.setdiff1d(np.arange(len(tri)),ids);other=tri[remaining_ids];upper=np.array(station['position']).reshape(-1,3,3)
 vertices=np.unique(panel.reshape(-1,3),axis=0);rows=[]
 for point in vertices:
  distances,witnesses=closest(point,other);i=int(np.argmin(distances))
  upper_distances,upper_witnesses=closest(point,upper);j=int(np.argmin(upper_distances))
  rows.append({'originalPanelVertex':point.tolist(),'originalMallFace':int(remaining_ids[i]),'nearestMallSurface':witnesses[i].tolist(),'distanceToMallM':float(distances[i]),'originalStationFace':j,'nearestStationSurface':upper_witnesses[j].tolist(),'distanceToStationM':float(upper_distances[j])})
 paired=[]
 for x,z in sorted(set((p[0],p[2]) for p in vertices)):
  ys=sorted(p[1] for p in vertices if p[0]==x and p[2]==z);assert len(ys)==2
  paired.append({'x':float(x),'z':float(z),'bottom':float(ys[0]),'top':float(ys[1]),'height':float(ys[1]-ys[0])})
 result={'uid':mall['uid'],'sourceSHA256':mall['sourceSHA256'],'originalPanelFaces':ids,'panelTriangles':len(ids),'panelVertices':len(vertices),'panelWorldBounds':[panel.min((0,1)).tolist(),panel.max((0,1)).tolist()],'allFacesStrictlyVertical':True,'originalVerticalEdgePairs':paired,'allOriginalVerticesNearestCompleteSource':rows,'minimumVertexToMallDistanceM':min(r['distanceToMallM'] for r in rows),'maximumVertexToMallDistanceM':max(r['distanceToMallM'] for r in rows),'exactNoContactPriorRetained':True,'supportAccepted':False,'installationApproved':False,'qualification':'Whole original mall excluding only the separately diagnosed panel, plus the entire original station, inspected at every exact panel vertex. Floating-point closest-surface witnesses are diagnostic only; they cannot replace the preserved complete exact rational no-contact result or establish a structural/decorative source role.'}
 save(DOC/'original-panel-nearest-complete-sources.json.gz',result)
 spec=importlib.util.spec_from_file_location('popcorn_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 out=m.freeze(BATCH,'complete-original-panel-vertex-source-context-v1',[Path(__file__),INPUT,PRIOR],{'uids':[mall['uid'],station['uid']],'sourceSHA256':mall['sourceSHA256'],'humanStatus':'held-unknown','requiresMoreComputeOrSourceEvidence':True,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'exactNoContactPriorRetained':True,'all12OriginalPanelFacesStrictlyVertical':True,'minimumVertexToMallDistanceM':result['minimumVertexToMallDistanceM'],'maximumVertexToMallDistanceM':result['maximumVertexToMallDistanceM'],'remainingReason':'original-detached-side-panel-role-and-complete-physical-acceptance-unresolved','nextStep':'Use complete original panel location, primary imagery and exact continuous component interfaces to establish a source-bound nonstructural role if evidence supports it. Retain all original faces and independent physical/runtime/browser gates.'})
 print({k:out[k] for k in ['jobId','minimumVertexToMallDistanceM','maximumVertexToMallDistanceM']},flush=True)

if __name__=='__main__':main()
