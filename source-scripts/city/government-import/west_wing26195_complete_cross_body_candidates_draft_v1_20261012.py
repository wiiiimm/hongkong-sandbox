"""Closed 3D binary-coordinate AABB exclusion only; no contact or support inference."""
import numpy as np,shapely

def candidates(world,components):
 w=np.asarray(world,dtype='<f8');assert w.ndim==3 and w.shape[1:]==(3,3)and np.isfinite(w).all();assert components and all(c for c in components)
 flat=[i for c in components for i in c];assert all(type(i)is int and 0<=i<len(w)for i in flat)and sorted(flat)==list(range(len(w)))
 labels=np.empty(len(w),int)
 for k,ids in enumerate(components):labels[ids]=k
 lo=w.min(1);hi=w.max(1);tree=shapely.STRtree(shapely.box(lo[:,0],lo[:,2],hi[:,0],hi[:,2]));result=[]
 for i in range(len(w)):
  js=tree.query(shapely.box(lo[i,0],lo[i,2],hi[i,0],hi[i,2]));js=js[(js>i)&(labels[js]!=labels[i])&(hi[js,1]>=lo[i,1])&(lo[js,1]<=hi[i,1])]
  result.extend((i,int(j))for j in sorted(js))
 assert len(result)==len(set(result));return result,labels
