import numpy as np
from scipy.ndimage import gaussian_filter1d

def load_profile():
    sky=np.load("skyline_raw.npy")
    x0,x1,lonL,lonR,W,H,emax=open("skymeta.txt").read().split()
    x0,x1,W=int(x0),int(x1),int(W); lonL,lonR=float(lonL),float(lonR)
    seg=sky[x0:x1+1].astype(float)
    # anchor coastal ends to sea level for a clean island silhouette
    seg[0]=0; seg[-1]=0
    return seg,(x0,x1,lonL,lonR,W)

def resample(seg,N):
    xs=np.linspace(0,1,len(seg))
    xn=np.linspace(0,1,N)
    return xn,np.interp(xn,xs,seg)

def rdp(pts,eps):
    # pts: Nx2
    def _rdp(p):
        if len(p)<3: return p
        a,b=p[0],p[-1]
        ab=b-a; L=np.hypot(*ab)
        if L==0: d=np.hypot(*(p-a).T)
        else: d=np.abs(np.cross(ab,p-a))/L
        i=np.argmax(d)
        if d[i]>eps:
            return np.vstack([_rdp(p[:i+1])[:-1],_rdp(p[i:])])
        return np.vstack([a,b])
    return _rdp(np.asarray(pts,float))
