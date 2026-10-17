"""Exact named current makeNativeTerrain index transformation, no tolerance.

The renderer converts all POSITION values to Float32 and swaps only b/c where
the complete XZ normal-Y formula is negative. Original sampler indices remain
separate evidence. This does not equate arbitrary permutations or sampled Y.
"""
import hashlib
import numpy as np
def drawn_native_faces(mesh):
 raw=np.asarray(mesh['position'],float);assert raw.ndim==1 and len(raw)%3==0 and np.isfinite(raw).all()
 vertices=raw.astype(np.float32).reshape(-1,3);assert np.isfinite(vertices).all()
 original=np.asarray(mesh['index']);assert original.ndim==1 and len(original)%3==0 and np.issubdtype(original.dtype,np.integer)
 assert original.min()>=0 and original.max()<len(vertices)
 indices=original.astype(np.uint32).reshape(-1,3).copy();swapped=[]
 for i,(a,b,c)in enumerate(indices):
  ax,az=float(vertices[a,0]),float(vertices[a,2]);bx,bz=float(vertices[b,0]),float(vertices[b,2]);cx,cz=float(vertices[c,0]),float(vertices[c,2])
  y=(bz-az)*(cx-ax)-(bx-ax)*(cz-az)
  if y<0:indices[i,1],indices[i,2]=indices[i,2],indices[i,1];swapped.append(i)
 faces=vertices[indices].astype(float)
 return faces,dict(completePOSITIONVertices=len(vertices),unusedPOSITIONVertices=len(vertices)-len(np.unique(original)),completeTriangles=len(indices),onlyRendererRequiredBCSwapFaceIDs=swapped,originalSamplerIndexSHA256=hashlib.sha256(original.astype('<u4').tobytes()).hexdigest(),renderedIndexSHA256=hashlib.sha256(indices.astype('<u4').tobytes()).hexdigest(),unchangedCompleteFloat32POSITIONSHA256=hashlib.sha256(vertices.astype('<f4').tobytes()).hexdigest(),noArbitraryPermutationOrTolerance=True,originalSamplerIndexRemainsSeparatelyBound=True)
