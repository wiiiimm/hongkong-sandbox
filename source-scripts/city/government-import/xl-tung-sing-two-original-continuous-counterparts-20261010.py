"""Whole original eight-face pieces versus actual original body surfaces."""
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-two-original-continuous-counterparts-20261010'
PRIOR=DOC.parent/'government-xl-tung-sing-two-detached-original-context-20261010/diagnostic.json.gz'
def distances(points,triangles):
 out=[]
 for a,b,c in triangles:
  ab,ac=b-a,c-a;n=np.cross(ab,ac);n2=np.dot(n,n);assert n2>0;q=points-n*((points-a)@n/n2)[:,None];d00,d01,d11=np.dot(ab,ab),np.dot(ab,ac),np.dot(ac,ac);den=d00*d11-d01*d01;assert den>0;d20,d21=(q-a)@ab,(q-a)@ac;u=(d11*d20-d01*d21)/den;v=(d00*d21-d01*d20)/den;parts=[np.where((u>=0)&(v>=0)&(u+v<=1),np.sum((q-points)**2,axis=1),np.inf)]
  for start,end in [(a,b),(b,c),(c,a)]:
   edge=end-start;l=np.dot(edge,edge);assert l>0;k=np.clip((points-start)@edge/l,0,1);candidate=start+k[:,None]*edge;parts.append(np.sum((candidate-points)**2,axis=1))
  out.append(np.sqrt(np.min(parts,axis=0)))
 return np.min(out,axis=0)
def main():
 assert not DOC.exists();d=read(PRIOR);source=next(ROOT/k for k in d['inputHashes'] if k.endswith('.glb.gz'));t=decode_original_world_triangles(source.read_bytes());assert digest(t.astype('<f8').tobytes())==d['wholeSourceWorldSHA256'];n=128;bary=np.asarray([(a/n,b/n) for a in range(n+1) for b in range(n+1-a)]);rows=[]
 for part in d['rows']:
  ids=sorted({q['mainbodyOriginalFace'] for q in part['wholeOriginalVertexWitnesses']});counterpart=t[ids];faces=[]
  for i in part['allOriginalFaces']:
   f=t[i];points=f[0]+bary[:,0,None]*(f[1]-f[0])+bary[:,1,None]*(f[2]-f[0]);sample=float(distances(points,counterpart).max());diameter=float(max(np.linalg.norm(f[a]-f[b]) for a,b in [(0,1),(1,2),(2,0)])/n);faces.append({'originalFace':i,'originalFaceSHA256':digest(f.astype('<f8').tobytes()),'completeBarycentricPartition':n,'partitionVertices':len(points),'maximumEvaluatedDistanceToOriginalWitnessFacetsM':sample,'maximumCellDiameterM':diameter,'continuousWholeFacetDistanceUpperBoundM':sample+diameter})
  rows.append({'originalComponent':part['component'],'allOriginalPartFaces':part['allOriginalFaces'],'actualOriginalMainbodyCounterpartFaceIds':ids,'actualOriginalMainbodyCounterpartFaces':counterpart.tolist(),'allWholeOriginalFacetBounds':faces,'completeOriginalPartContinuousDistanceUpperBoundM':max(q['continuousWholeFacetDistanceUpperBoundM'] for q in faces)})
 result={'uid':d['uid'],'sourceSHA256':d['sourceSHA256'],'wholeSourceWorldSHA256':d['wholeSourceWorldSHA256'],'completeOriginalDetachedFacetCount':sum(len(r['allOriginalPartFaces']) for r in rows),'rows':rows,'exactNoContactFailurePreserved':True,'sourceGeometryChanges':0,'physicalAccepted':False,'inputHashes':d['inputHashes']|{str(PRIOR.relative_to(ROOT)):digest(PRIOR.read_bytes())},'qualification':'All16 unchanged original facets fully partitioned. Distance-to-union of finite original witness triangles is1-Lipschitz; every partition point is within one cell diameter of a sampled vertex. This continuous upper bound remains conservative for distance to the complete mainbody. No coplanar flattening, contact/mounting/load-bearing interpretation or source edits.'};save(DOC/'diagnostic.json.gz',result);print({'facets':result['completeOriginalDetachedFacetCount'],'continuousBoundsM':[r['completeOriginalPartContinuousDistanceUpperBoundM'] for r in rows]},flush=True)
if __name__=='__main__':main()
