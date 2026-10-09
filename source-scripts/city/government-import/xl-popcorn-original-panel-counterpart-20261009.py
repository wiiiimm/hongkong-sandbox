"""Continuous original side-surface correspondence without snapping or contact credit.

The attempted coplanar counterpart method is recorded and rejected for warped
original pairs. Complete barycentric partitions plus the 1-Lipschitz distance
bound inspect each entire original panel triangle without flattening sources.
"""
from fractions import Fraction
from pathlib import Path
import importlib.util
import numpy as np
from run import ROOT,HERE,read,save

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
d=load('panel_distance',HERE/'xl-popcorn-original-panel-distance-20261009.py')
BATCH='government-xl-popcorn-original-panel-counterpart-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH

def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def hull(points):
 points=sorted(set(points));lower=[];upper=[]
 for p in points:
  while len(lower)>=2 and orient(lower[-2],lower[-1],p)<=0:lower.pop()
  lower.append(p)
 for p in reversed(points):
  while len(upper)>=2 and orient(upper[-2],upper[-1],p)<=0:upper.pop()
  upper.append(p)
 return lower[:-1]+upper[:-1]

def exact_quad(faces):
 t=[[[Fraction(float(v)) for v in p] for p in face] for face in faces]
 vertices=sorted({tuple(p) for face in t for p in face});assert len(vertices)==4
 assert len(set(map(tuple,t[0]))&set(map(tuple,t[1])))==2
 a,b,c=t[0];ab=[b[i]-a[i] for i in range(3)];ac=[c[i]-a[i] for i in range(3)]
 n=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]]
 assert any(n)
 volumes=[sum(n[i]*(p[i]-a[i]) for i in range(3)) for p in vertices]
 if any(volumes):
  return {'exactCoplanar':False,'exactConvexQuad':False,'exactTriangleUnionEqualsConvexHull':False,'exactPlaneVolumeWitnesses':[str(v) for v in volumes],'qualification':'Original counterpart is warped. Coplanar-convex method rejected; no flattening or tolerance waiver.'}
 drop=max(range(3),key=lambda i:abs(n[i]));axes=[i for i in range(3) if i!=drop]
 planar=lambda p:tuple(p[i] for i in axes)
 outline=hull([planar(p) for p in vertices]);assert len(outline)==4
 hull2=abs(sum(outline[i][0]*outline[(i+1)%4][1]-outline[(i+1)%4][0]*outline[i][1] for i in range(4)))
 areas=[abs(orient(*[planar(p) for p in face])) for face in t]
 assert all(x>0 for x in areas) and sum(areas)==hull2
 # Shared diagonal must have opposite-side vertices: interiors do not overlap.
 shared=sorted(set(map(tuple,t[0]))&set(map(tuple,t[1])))
 single=[next(p for p in face if tuple(p) not in shared) for face in t]
 assert orient(planar(shared[0]),planar(shared[1]),planar(single[0]))*orient(planar(shared[0]),planar(shared[1]),planar(single[1]))<0
 return {'exactCoplanar':True,'exactConvexQuad':True,'exactTriangleUnionEqualsConvexHull':True,'projectionAxes':axes,'exactDoubledProjectedArea':str(hull2),'originalVertices':[[str(v) for v in p] for p in vertices]}

def main():
 assert not (DOC/'result.json').exists(),'Completed evidence is immutable'
 mall=next(r for r in read(d.INPUT)['rows'] if r['uid']=='landsd/295538:0');tri=np.array(mall['position']).reshape(-1,3,3)
 prior=read(d.PRIOR);part=next(c for c in prior['separateOriginalSourceComponents'] if c['component']==13063)
 assert part['allOriginalFaceIndices']==list(range(13063,13075)) and part['exactDirectMainBodyContact']
 rows=[]
 for i in range(6):
  source_ids=[13033+2*i,13034+2*i];other_ids=[13063+2*i,13064+2*i];quad=tri[other_ids];proof=exact_quad(quad)
  faces=[];subdivisions=256
  bary=np.array([(a/subdivisions,b/subdivisions) for a in range(subdivisions+1) for b in range(subdivisions+1-a)])
  for fi in source_ids:
   ds=np.array([d.closest(p,quad)[0] for p in tri[fi]]);vertex_distances=ds.min(1)
   face=tri[fi];points=face[0]+bary[:,0,None]*(face[1]-face[0])+bary[:,1,None]*(face[2]-face[0])
   # Evaluate nearest points to both actual original counterpart triangles.
   distances=[]
   for triangle in quad:
    a,b,c=triangle;ab=b-a;ac=c-a;n=np.cross(ab,ac);n2=np.dot(n,n);assert n2>0
    q=points-n*((points-a)@n/n2)[:,None]
    d00=np.dot(ab,ab);d01=np.dot(ab,ac);d11=np.dot(ac,ac);den=d00*d11-d01*d01;assert den>0
    d20=(q-a)@ab;d21=(q-a)@ac;u=(d11*d20-d01*d21)/den;v=(d00*d21-d01*d20)/den
    candidates=[np.where((u>=0)&(v>=0)&(u+v<=1),np.sum((q-points)**2,axis=1),np.inf)]
    for start,end in [(a,b),(b,c),(c,a)]:
     edge=end-start;length=np.dot(edge,edge);assert length>0
     t=np.clip((points-start)@edge/length,0,1);p=start+t[:,None]*edge;candidates.append(np.sum((p-points)**2,axis=1))
    distances.append(np.sqrt(np.min(candidates,axis=0)))
   sampled=float(np.min(distances,axis=0).max())
   diameter=float(max(np.linalg.norm(face[a]-face[b]) for a,b in [(0,1),(1,2),(2,0)])/subdivisions)
   # Uniform barycentric vertices cover the entire triangle. Every partition
   # point is within this exact cell-edge bound of at least one sample. Distance
   # to any nonempty closed surface set is 1-Lipschitz, including warped pairs.
   faces.append({'originalPanelFace':fi,'distanceAtEveryOriginalVertexM':vertex_distances.tolist(),'completeBarycentricPartitionSubdivisions':subdivisions,'partitionVertices':len(points),'maximumEvaluatedSurfaceDistanceM':sampled,'partitionCellDiameterBoundM':diameter,'continuousDistanceUpperBoundM':sampled+diameter})
  rows.append({'originalPanelFaces':source_ids,'originalAttachedCounterpartFaces':other_ids,'counterpartConvexity':proof,'wholeOriginalPanelTriangles':faces})
 result={'uid':mall['uid'],'sourceSHA256':mall['sourceSHA256'],'all12OriginalPanelFacesAccounted':sum(len(r['originalPanelFaces']) for r in rows)==12,'originalCounterpartExactMainBodyAttachment':part['contactWitness'],'sixWholeOriginalFacetCorrespondences':rows,'rejectedGlobalCoplanarCounterpartMethod':any(not r['counterpartConvexity']['exactCoplanar'] for r in rows),'wholePanelContinuousDistanceUpperBoundM':max(f['continuousDistanceUpperBoundM'] for r in rows for f in r['wholeOriginalPanelTriangles']),'exactNoContactResultPreserved':True,'supportAccepted':False,'installationApproved':False,'sourceGeometryChanges':0,'qualification':'Complete barycentric partitions plus the 1-Lipschitz distance-to-surface bound cover each entire original panel triangle. Original warped counterpart triangles remain intact; the coplanar shortcut is explicitly rejected wherever exact rational planarity fails. Reported distances use floating-point evaluation and are not exact contact or support credit. Original panel is not snapped, thickened, suppressed or deleted. A source-specific authored ancillary-surface role and all independent physical gates remain required.'}
 save(DOC/'complete-original-panel-counterpart.json.gz',result)
 helper=load('panel_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py')
 out=helper.freeze(BATCH,'complete-original-panel-warped-counterpart-distance-v1',[Path(__file__),HERE/'xl-popcorn-original-panel-distance-20261009.py',d.INPUT,d.PRIOR,d.DOC/'result.json',ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-panel-visual-20261009/render.json'],{'uids':[mall['uid']],'sourceSHA256':mall['sourceSHA256'],'humanStatus':'held-unknown','requiresMoreComputeOrSourceEvidence':True,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'all12OriginalPanelFacesAccounted':result['all12OriginalPanelFacesAccounted'],'wholePanelContinuousDistanceUpperBoundM':result['wholePanelContinuousDistanceUpperBoundM'],'sourceEvidenceInterpretationUsedAI':True,'remainingReason':'ancillary-offset-rail-face-role-and-independent-physical-gates-unresolved','nextStep':'Source-bound primary image/plan interpretation may distinguish original decorative side-surface from structural anchor. Keep full original geometry, raw exact no-contact evidence and strict independent terrain/foundation/foreign/runtime/browser checks.'})
 print({'jobId':out['jobId'],'wholePanelContinuousDistanceUpperBoundM':out['wholePanelContinuousDistanceUpperBoundM']},flush=True)

if __name__=='__main__':main()
