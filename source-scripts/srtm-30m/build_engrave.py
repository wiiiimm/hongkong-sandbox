import numpy as np, sys
import geom, cairosvg
from scipy.ndimage import gaussian_filter1d

elev=np.load("elev.npy"); elev=np.where(elev<-50,0,elev); elev=np.clip(elev,0,None)
mask=np.load("lantau_mask.npy"); em=np.where(mask,elev,0.0)
x0,x1,lonL,lonR,W,H,emax=open("skymeta.txt").read().split()
x0,x1,W,H=int(x0),int(x1),int(W),int(H)
rows=np.where(mask.any(axis=1))[0]; r0,r1=rows.min(),rows.max()
em=em[r0:r1+1, x0:x1+1]; mk=mask[r0:r1+1, x0:x1+1]
RH,RW=em.shape

NB     =int(sys.argv[1]) if len(sys.argv)>1 else 18
PEAK   =float(sys.argv[2]) if len(sys.argv)>2 else 560.0
STEP   =float(sys.argv[3]) if len(sys.argv)>3 else 10.0
ISMOOTH=float(sys.argv[4]) if len(sys.argv)>4 else 18.0
THRESH =float(sys.argv[5]) if len(sys.argv)>5 else 12.0
OUTW   =int(sys.argv[6]) if len(sys.argv)>6 else 1800

scale=PEAK/em.max()
Wv=2000.0; PAD=46.0; MT=50.0
drawW=Wv-2*PAD
Xn=PAD+np.arange(RW)/(RW-1)*drawW
edges=np.linspace(0,RH,NB+1).astype(int)

raw=[]
for k in range(NB):
    ra,rb=edges[k],edges[k+1]
    if rb<=ra: continue
    sub=em[ra:rb,:]; subm=mk[ra:rb,:]
    prof=gaussian_filter1d(sub.max(axis=0),ISMOOTH)
    sig=np.where(prof>THRESH)[0]
    if len(sig)<3: continue
    lo,hi=sig.min(),sig.max()
    raw.append((k,prof,lo,hi))

ys=[ (k*STEP - prof*scale) for k,prof,lo,hi in raw]
gmin=min(y[lo:hi+1].min() for (k,p,lo,hi),y in zip(raw,ys))
shift=MT-gmin
Ybase=(NB-1)*STEP+shift
Hv=Ybase+16

parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wv:.0f} {Hv:.0f}" width="{Wv:.0f}" height="{Hv:.0f}">']
parts.append(f'<rect width="{Wv:.0f}" height="{Hv:.0f}" fill="#ffffff"/>')
for (k,prof,lo,hi),y in zip(raw,ys):
    yy=y+shift; base=k*STEP+shift
    xs=Xn[lo:hi+1]; yv=yy[lo:hi+1]
    d="M %.2f %.2f "%(xs[0],base)+"".join("L %.2f %.2f "%(p,q) for p,q in zip(xs,yv))+"L %.2f %.2f Z"%(xs[-1],base)
    parts.append(f'<path d="{d}" fill="#ffffff"/>')
    t=k/(NB-1); w=0.55+1.85*t; op=0.42+0.58*t
    parts.append('<path d="M '+" L ".join("%.2f %.2f"%(p,q) for p,q in zip(xs,yv))+
                 f'" fill="none" stroke="#0a0a0a" stroke-width="{w:.2f}" stroke-linejoin="round" stroke-linecap="round" opacity="{op:.2f}"/>')
cols=np.where(mk.any(axis=0))[0]
parts.append(f'<path d="M {Xn[cols[0]]:.2f} {Ybase:.2f} L {Xn[cols[-1]]:.2f} {Ybase:.2f}" stroke="#0a0a0a" stroke-width="1.0"/>')
parts.append("</svg>")
svg="\n".join(parts); open("engrave.svg","w").write(svg)
cairosvg.svg2png(bytestring=svg.encode(),write_to="engrave_preview.png",output_width=OUTW,background_color="#ffffff")
print("bands",len(raw),"viewBox 0 0 %.0f %.0f aspect %.2f"%(Wv,Hv,Wv/Hv))
