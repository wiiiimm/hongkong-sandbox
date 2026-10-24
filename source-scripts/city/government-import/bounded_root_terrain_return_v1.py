"""Return terrain to its exact parent over an explicit outer strip, preserving the core."""
import numpy as np

def transition(faces,bounds,parent_cells,sample,width,clip):
    x0,z0,x1,z1=bounds
    assert np.isfinite(width) and 0<2*width<min(x1-x0,z1-z0)
    core=[x0+width,z0+width,x1-width,z1-width]
    regions=[(core,False),([x0,z0,x1,core[1]],True),([x0,core[3],x1,z1],True),([x0,core[1],core[0],core[3]],True),([core[2],core[1],x1,core[3]],True)]
    pc=np.asarray(parent_cells);pb=np.stack([pc.min(1),pc.max(1)],1);out=[]
    for face in faces:
        # Do not retriangulate any face fully inside the unchanged core.
        xz=face[:,[0,2]]
        if (xz[:,0]>=core[0]).all()and(xz[:,0]<=core[2]).all()and(xz[:,1]>=core[1]).all()and(xz[:,1]<=core[3]).all():out.append(face.copy());continue
        for region,blend in regions:
            poly=clip.rect(list(face),region)
            if len(poly)<3:continue
            if blend:
                q=np.asarray(poly)[:,[0,2]];lo,hi=q.min(0),q.max(0)
                ids=np.flatnonzero((pb[:,0,0]<=hi[0]+1e-8)&(pb[:,1,0]>=lo[0]-1e-8)&(pb[:,0,1]<=hi[1]+1e-8)&(pb[:,1,1]>=lo[1]-1e-8))
                groups=[clip.parent_clip(poly,pc[j])for j in ids]
            else:groups=[poly]
            for points in groups:
                if len(points)<3:continue
                vertices=[]
                for value in points:
                    v=np.asarray(value,dtype=float).copy()
                    if blend:
                        weight=max(0.,min(1.,min(v[0]-x0,x1-v[0],v[2]-z0,z1-v[2])/width))
                        v[1]=v[1]*weight+sample(v[0],v[2])*(1-weight)
                    vertices.append(v)
                for j in range(1,len(vertices)-1):
                    f=np.asarray([vertices[0],vertices[j],vertices[j+1]])
                    if np.linalg.norm(np.cross(f[1]-f[0],f[2]-f[0]))>=1e-8:out.append(f)
    return np.asarray(out)
