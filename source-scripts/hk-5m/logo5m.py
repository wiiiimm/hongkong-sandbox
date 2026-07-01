import numpy as np, sys
from scipy.ndimage import gaussian_filter1d
import cairosvg
elev=np.load("l5_elev.npy"); mask=np.load("l5_mask.npy")
E=np.where(mask,elev,0.0)
cols=np.where(mask.any(axis=0))[0]; x0,x1=cols.min(),cols.max()
sky=E.max(axis=0)[x0:x1+1].astype(float); sky[0]=0; sky[-1]=0
N=2600; xs=np.linspace(0,1,len(sky)); xn=np.linspace(0,1,N); h=np.interp(xn,xs,sky)
SIG=float(sys.argv[1]) if len(sys.argv)>1 else 34
PEAK=float(sys.argv[2]) if len(sys.argv)>2 else 430
hs=gaussian_filter1d(h,SIG); hs=gaussian_filter1d(hs,SIG*0.5); hs[0]=0;hs[-1]=0;hs=np.clip(hs,0,None)
scale=PEAK/hs.max()
Wv=2000.0;PAD=46.0;TOP=46.0;baseY=PEAK+TOP;Hv=baseY;drawW=Wv-2*PAD
X=PAD+xn*drawW; Y=baseY-hs*scale
def rdp(p,eps):
    def f(p):
        if len(p)<3:return p
        a,b=p[0],p[-1];ab=b-a;L=np.hypot(*ab)
        d=np.abs(np.cross(ab,p-a))/L if L else np.hypot(*(p-a).T)
        i=np.argmax(d)
        if d[i]>eps:return np.vstack([f(p[:i+1])[:-1],f(p[i:])])
        return np.vstack([a,b])
    return f(np.asarray(p,float))
P=rdp(np.column_stack([X,Y]),1.3)
def cat(P,baseY,xl,xr):
    n=len(P);d="M %.2f %.2f L %.2f %.2f "%(xl,baseY,P[0,0],P[0,1])
    for i in range(n-1):
        p0=P[i-1] if i>0 else P[i];p1=P[i];p2=P[i+1];p3=P[i+2] if i+2<n else P[i+1]
        c1=p1+(p2-p0)/6;c2=p2-(p3-p1)/6
        d+="C %.2f %.2f %.2f %.2f %.2f %.2f "%(c1[0],c1[1],c2[0],c2[1],p2[0],p2[1])
    d+="L %.2f %.2f Z"%(xr,baseY);return d
dd=cat(P,baseY,PAD,Wv-PAD)
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 {Hv:.0f}" width="2000" height="{Hv:.0f}"><path d="{dd}" fill="#000"/></svg>'
open("logo5m.svg","w").write(svg)
cairosvg.svg2png(bytestring=svg.encode(),write_to="logo5m_8000.png",output_width=8000,background_color=None)
cairosvg.svg2png(bytestring=svg.encode(),write_to="logo5m_prev.png",output_width=1600,background_color="#eeeeee")
print("logo5m verts",len(P))
