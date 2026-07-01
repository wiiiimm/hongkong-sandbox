import numpy as np, sys
from scipy.ndimage import gaussian_filter, zoom, binary_erosion
from PIL import Image

tone=np.load("oblique_tone.npy"); E=np.load("oblique_E.npy")
RW,Hc,baseline,VE,TILT,off=np.load("oblique_meta.npy")
OW   =int(sys.argv[1]) if len(sys.argv)>1 else 2600
STEPS=int(sys.argv[2]) if len(sys.argv)>2 else 16
GAM  =float(sys.argv[3]) if len(sys.argv)>3 else 0.95
NF   =float(sys.argv[4]) if len(sys.argv)>4 else 2.6   # noise grain px
sc=OW/tone.shape[1]
land=zoom(np.where(np.isnan(tone),0.0,1.0),sc,order=1)>0.5
T=np.clip(zoom(np.nan_to_num(tone,nan=0.0),sc,order=1),0,1)
Ei=zoom(np.nan_to_num(E,nan=0.0),sc,order=1)
H,W=T.shape

# fall-line vector field (down-slope on screen), heavily smoothed for coherent strokes
Es=gaussian_filter(np.where(land,Ei,0),7.0)
dEy,dEx=np.gradient(Es)
fx,fy=-dEx,-dEy
mag=np.hypot(fx,fy)+1e-6
fx/=mag; fy/=mag
# bias slightly downward so flat tops still get vertical strokes
fy=fy+0.35; m2=np.hypot(fx,fy)+1e-6; fx/=m2; fy/=m2

# low-frequency noise -> clean line width
rng=np.random.default_rng(7)
nz=rng.random((int(H/NF)+2,int(W/NF)+2))
nz=zoom(nz,(H/nz.shape[0],W/nz.shape[1]),order=1)
nz=nz[:H,:W]

def sample(a,px,py):
    px=np.clip(px,0,W-1); py=np.clip(py,0,H-1)
    x0=np.floor(px).astype(int); y0=np.floor(py).astype(int)
    x1=np.minimum(x0+1,W-1); y1=np.minimum(y0+1,H-1)
    fxp=px-x0; fyp=py-y0
    return (a[y0,x0]*(1-fxp)*(1-fyp)+a[y0,x1]*fxp*(1-fyp)
           +a[y1,x0]*(1-fxp)*(1-fyp+0)*0+a[y1,x0]*(1-fxp)*fyp+a[y1,x1]*fxp*fyp)

Y,X=np.mgrid[0:H,0:W].astype(np.float32)
acc=nz.copy(); cnt=np.ones_like(nz)
for sgn in (1.0,-1.0):
    px,py=X.copy(),Y.copy()
    for k in range(STEPS):
        vx=sample(fx,px,py); vy=sample(fy,px,py)
        px=px+sgn*vx; py=py+sgn*vy
        acc+=sample(nz,px,py); cnt+=1
lic=acc/cnt
# local normalize for contrast
licm=gaussian_filter(lic,12); lics=gaussian_filter((lic-licm)**2,12)**0.5+1e-3
licn=np.clip(0.5+(lic-licm)/(2.6*lics),0,1)

t=np.clip(T,0,1)**GAM
th=1.0-t                                  # lit -> low threshold -> more white
white=(licn>th).astype(np.float32)
L=white.copy()
L[t<0.10]=0.0                             # deep shadow solid

# occlusion edges (depth jumps) -> black
edge=np.hypot(*np.gradient(gaussian_filter(Ei,1.2)))
L[(edge>np.percentile(edge[land],90))&land]=0.0
# lit ridge crests -> white highlight
conv=gaussian_filter(Ei,7.0)-gaussian_filter(Ei,2.0)   # >0 at crests
hi=(conv>np.percentile(conv[land],82))&(t>0.45)&land
L[hi]=1.0

out=np.ones((H,W),np.float32); out[land]=L[land]
outline=land & ~binary_erosion(land,iterations=max(1,int(round(sc))))
out[outline]=0.0
Image.fromarray((np.clip(out,0,1)*255).astype(np.uint8)).save("scratch_preview.png")
print("ok",out.shape,"sc",round(sc,2))
