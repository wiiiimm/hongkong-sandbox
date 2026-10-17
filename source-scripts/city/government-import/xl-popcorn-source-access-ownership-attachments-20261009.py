"""Exact original far-stair rail attachments, preserving every source face."""
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
DOC=ROOT/'docs/astra-city/government-import/government-xl-popcorn-source-access-ownership-20261009';r=read(DOC/'source-bound-ancillary-step-identity-proposal.json.gz');raw=np.load(HERE/'local/government-xl-source-authored-openings-20261009/raw-fbx/B447991877202063C0/full-world-triangles.npz')['triangles'];tri=np.stack([raw[:,:,0]-834500,raw[:,:,2],816500-raw[:,:,1]],axis=2);components={c['exactVertexEdgeConnectedComponent']:c for role in r['rows'] for c in role['completeOriginalComponents']};main=max(components,key=lambda k:components[k]['totalOriginalFaceCount']);bodyids=np.array(components[main]['allOriginalFaceIndices']);body=tri[bodyids];lo=body.min(axis=1);hi=body.max(axis=1);cache={};rows=[]
for lab,c in components.items():
 if lab==main:continue
 witness=None;tests=0
 for fi in c['allOriginalFaceIndices']:
  t=tri[fi];hits=np.flatnonzero(np.all(hi>=t.min(axis=0),axis=1)&np.all(lo<=t.max(axis=0),axis=1));rt=rational_face(t)
  for j in hits:
   j=int(j);tests+=1
   if j not in cache:cache[j]=rational_face(body[j])
   pts=intersection_points(rt,cache[j])
   if pts:witness={'sourceFace':fi,'mainBodySourceFace':int(bodyids[j]),'exactIntersectionPoints':[[str(a) for a in p] for p in sorted(pts)]};break
  if witness:break
 rows.append({'component':lab,'allOriginalFaceIndices':c['allOriginalFaceIndices'],'farOriginalFaceIndices':c['farOriginalFaceIndices'],'exactDirectMainBodyContact':bool(witness),'contactWitness':witness,'exactTrianglePairsTested':tests});print({'component':lab,'contact':bool(witness),'pairs':tests},flush=True)

alllo=tri.min(axis=1);allhi=tri.max(axis=1)
for row in rows:
 if row['exactDirectMainBodyContact']:continue
 witness=None;tests=0;own=set(row['allOriginalFaceIndices'])
 for fi in row['allOriginalFaceIndices']:
  t=tri[fi];hits=np.flatnonzero(np.all(allhi>=t.min(axis=0),axis=1)&np.all(alllo<=t.max(axis=0),axis=1));rt=rational_face(t)
  for j in hits:
   j=int(j)
   if j in own:continue
   tests+=1;pts=intersection_points(rt,rational_face(tri[j]))
   if pts:witness={'sourceFace':fi,'otherOriginalSourceFace':j,'otherAccountedComponent':next((k for k,c in components.items() if j in c['allOriginalFaceIndices']),None),'exactIntersectionPoints':[[str(a) for a in p] for p in sorted(pts)]};break
  if witness:break
 row['exactContactToOtherOriginalComponent']=bool(witness);row['otherOriginalContactWitness']=witness;row['otherOriginalExactPairsTested']=tests;print({'component':row['component'],'otherContact':witness,'tests':tests},flush=True)
save(DOC/'every-far-access-component-exact-attachments.json.gz',{'sourceWorldTriangleSHA256':digest(tri.astype('<f8').tobytes()),'mainOriginalBodyComponent':main,'mainOriginalBodyFaceIndices':bodyids.tolist(),'mainBodyFarFacesByRole':[{'role':role['roleIndex'],'faceIndices':next(c['farOriginalFaceIndices'] for c in role['completeOriginalComponents'] if c['exactVertexEdgeConnectedComponent']==main)} for role in r['rows']],'separateOriginalSourceComponents':rows,'everyFarFaceAccounted':True,'geometryChanges':0,'installationApproved':False,'physicalSupportAccepted':False,'qualification':'Exact rational original surface contact witnesses. Main body is a single exact-vertex-edge-connected authored component including both stairs. Separate rails/parts remain owned by exact original provider root; missing contact witnesses are not invented and must remain explicit for physical review.'})
