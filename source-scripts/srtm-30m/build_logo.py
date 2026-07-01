import numpy as np, sys
import geom, cairosvg

seg,(x0,x1,lonL,lonR,W)=geom.load_profile()
N=2400
xn,h=geom.resample(seg,N)

SIGMA=float(sys.argv[1]) if len(sys.argv)>1 else 30.0
PEAK =float(sys.argv[2]) if len(sys.argv)>2 else 430.0
EPS  =float(sys.argv[3]) if len(sys.argv)>3 else 1.4
OUTW =int(sys.argv[4]) if len(sys.argv)>4 else 1600

# heavy smoothing -> broad rounded subtropical ridges
hs=geom.gaussian_filter1d(h,SIGMA)
hs=geom.gaussian_filter1d(hs,SIGMA*0.5)
hs[0]=0; hs[-1]=0; hs=np.clip(hs,0,None)
scale=PEAK/hs.max()

Wv=2000.0; PAD=46.0; TOP=46.0
drawW=Wv-2*PAD
X=PAD+xn*drawW
Y=PEAK+TOP-hs*scale
baseY=PEAK+TOP; Hv=baseY
pts=np.column_stack([X,Y])
simp=geom.rdp(pts,EPS)
P=simp

def catmull_path(P,baseY,x_left,x_right):
    # smooth closed-ish silhouette via Catmull-Rom -> cubic bezier on the top edge
    n=len(P)
    d="M %.2f %.2f L %.2f %.2f "%(x_left,baseY,P[0,0],P[0,1])
    for i in range(n-1):
        p0=P[i-1] if i>0 else P[i]
        p1=P[i]; p2=P[i+1]
        p3=P[i+2] if i+2<n else P[i+1]
        c1=p1+(p2-p0)/6.0
        c2=p2-(p3-p1)/6.0
        d+="C %.2f %.2f %.2f %.2f %.2f %.2f "%(c1[0],c1[1],c2[0],c2[1],p2[0],p2[1])
    d+="L %.2f %.2f Z"%(x_right,baseY)
    return d

d=catmull_path(P,baseY,PAD,Wv-PAD)
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wv:.0f} {Hv:.0f}" width="{Wv:.0f}" height="{Hv:.0f}">
<path d="{d}" fill="#000000"/></svg>'''
open("logo.svg","w").write(svg)
cairosvg.svg2png(bytestring=svg.encode(),write_to="logo_preview.png",output_width=OUTW,background_color=None)
print("RDP verts",len(P),"viewBox 0 0 %.0f %.0f"%(Wv,Hv),"aspect %.2f"%(Wv/Hv))
