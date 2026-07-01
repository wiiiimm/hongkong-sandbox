import numpy as np, sys, math
from scipy.ndimage import gaussian_filter, zoom, binary_erosion
from PIL import Image, ImageDraw, ImageFont

OW=int(sys.argv[1]) if len(sys.argv)>1 else 4000
SEED=7
CJK="/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
SER="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

# ---------- mountain engraving ----------
tone=np.load("oblique_tone.npy"); E=np.load("oblique_E.npy")
RW,Hc,baseline,VE,TILT,off=np.load("oblique_meta.npy"); Hc=int(Hc)
sc=OW/tone.shape[1]
land=zoom(np.where(np.isnan(tone),0.0,1.0),sc,order=1)>0.5
T=np.clip(zoom(np.nan_to_num(tone,nan=0.0),sc,order=1),0,1)
Ei=zoom(np.nan_to_num(E,nan=0.0),sc,order=1)
H,W=T.shape
Es=gaussian_filter(np.where(land,Ei,0),7.0); dEy,dEx=np.gradient(Es)
fx,fy=-dEx,-dEy; m=np.hypot(fx,fy)+1e-6; fx/=m; fy/=m
fy=fy+0.35; m2=np.hypot(fx,fy)+1e-6; fx/=m2; fy/=m2
rng=np.random.default_rng(SEED); NF=2.6*sc/ (OW/2600)
NF=max(2.2,NF)
nz=rng.random((int(H/NF)+2,int(W/NF)+2)); nz=zoom(nz,(H/nz.shape[0],W/nz.shape[1]),order=1)[:H,:W]
Yg,Xg=np.mgrid[0:H,0:W].astype(np.float32)
def samp(a,px,py):
    px=np.clip(px,0,W-1);py=np.clip(py,0,H-1)
    x0=np.floor(px).astype(int);y0=np.floor(py).astype(int)
    x1=np.minimum(x0+1,W-1);y1=np.minimum(y0+1,H-1);fxp=px-x0;fyp=py-y0
    return (a[y0,x0]*(1-fxp)*(1-fyp)+a[y0,x1]*fxp*(1-fyp)+a[y1,x0]*(1-fxp)*fyp+a[y1,x1]*fxp*fyp)
STEPS=int(16*sc/(OW/2600)); STEPS=max(14,STEPS)
acc=nz.copy();cnt=np.ones_like(nz)
for sgn in (1.0,-1.0):
    px,py=Xg.copy(),Yg.copy()
    for k in range(STEPS):
        vx=samp(fx,px,py);vy=samp(fy,px,py);px+=sgn*vx;py+=sgn*vy;acc+=samp(nz,px,py);cnt+=1
lic=acc/cnt
licm=gaussian_filter(lic,12*sc/(OW/2600)); lics=gaussian_filter((lic-licm)**2,12*sc/(OW/2600))**0.5+1e-3
licn=np.clip(0.5+(lic-licm)/(2.6*lics),0,1)
t=np.clip(T,0,1)**0.95
white=(licn>(1.0-t)*0.96).astype(np.float32); Lm=white.copy(); Lm[t<0.10]=0.0
edge=np.hypot(*np.gradient(gaussian_filter(Ei,1.2)))
Lm[(edge>np.percentile(edge[land],90))&land]=0.0
conv=gaussian_filter(Ei,7.0)-gaussian_filter(Ei,2.0)
Lm[(conv>np.percentile(conv[land],82))&(t>0.45)&land]=1.0
mount=np.ones((H,W),np.float32); mount[land]=Lm[land]
outline=land & ~binary_erosion(land,iterations=max(1,int(round(sc))))
mount[outline]=0.0

# ---------- assemble full canvas ----------
R=OW/2600.0
PAD_TOP=int(360*R); SEA=int(250*R); SIDE=int(40*R)
baseY=int(round(baseline*sc))
Htot=PAD_TOP+H+SEA
canvas=np.ones((Htot,OW),np.float32)
canvas[PAD_TOP:PAD_TOP+H,:]=mount
waterY=PAD_TOP+baseY
# land top per column (canvas y) for anchors
firstland=np.full(W,-1)
for c in range(W):
    col=np.where(land[:,c])[0]
    if len(col): firstland[c]=PAD_TOP+col.min()

img=Image.fromarray((np.clip(canvas,0,1)*255).astype(np.uint8)).convert("RGB")
d=ImageDraw.Draw(img)
BLACK=(0,0,0); GREY=(90,90,90)

# ---------- sea: horizontal wavy hatch + faint reflection ----------
rng2=np.random.default_rng(3)
ncols=W
# faint reflection streaks under mountains
silh=np.where(firstland>=0, firstland, waterY)
for c in range(0,W,max(1,int(2*R))):
    if firstland[c]<0: continue
    h=waterY-firstland[c]
    refl=int(h*0.18)
    if refl>3:
        g=235
        d.line([(c,waterY),(c,waterY+refl)],fill=(g,g,g),width=1)
# horizontal water lines, sparser downward
y=waterY+int(4*R); i=0
while y<Htot-2:
    i+=1
    gap=int((3+ i*0.9)*R)
    amp=2.0*R; ph=rng2.random()*6.28; freq=0.012/R
    xs=np.arange(SIDE,OW-SIDE,2)
    ys=y+amp*np.sin(freq*xs+ph)
    pts=list(zip(xs.tolist(),ys.tolist()))
    shade=int(120+min(110,i*7))
    d.line(pts,fill=(shade,shade,shade),width=1)
    y+=gap

# ---------- town clusters ----------
cc0,rr0,RWc,Hcc=[int(float(v)) for v in open("oblique5m_crop.txt").read().split()]
def screenx(fcol): return (fcol - cc0)*sc
def town(cx, kind):
    rng3=np.random.default_rng(11 if kind=='low' else 23)
    cx=int(cx)
    span=int((30 if kind=='low' else 34)*R)
    # white base halo to lift buildings off the dark slope
    d.rectangle([cx-span//2-int(4*R),waterY-int(6*R),cx+span//2+int(4*R),waterY+int(2*R)],fill=(255,255,255))
    n= 12 if kind=='low' else 15
    x=cx-span//2
    for k in range(n):
        w=int((2.0 if kind=='low' else 2.4)*R*(0.8+rng3.random()*0.7))
        hh=int((4+rng3.random()*6)*R) if kind=='low' else int((7+rng3.random()*20)*R)
        x2=x+w; y1=waterY-hh
        d.rectangle([x,y1,x2,waterY],fill=(255,255,255),outline=(55,55,55),width=1)
        for wy in range(y1+int(2.5*R),waterY-int(1.5*R),max(3,int(4*R))):
            d.line([(x+int(1*R),wy),(x2-int(1*R),wy)],fill=(150,150,150),width=1)
        x=x2+int(1.6*R)
        if x>cx+span//2: break
    d.line([(cx-span//2-int(4*R),waterY),(cx+span//2+int(4*R),waterY)],fill=(40,40,40),width=1)
town(screenx(3377),'low')     # Mui Wo
town(screenx(3872),'high')    # Discovery Bay

# ---------- labels ----------
fz_zh=int(34*R); fz_en=int(23*R); fz_el=int(21*R)
F_zh=ImageFont.truetype(CJK,fz_zh); F_en=ImageFont.truetype(SER,fz_en); F_el=ImageFont.truetype(SER,fz_el)
def tw(dr,s,f): b=dr.textbbox((0,0),s,font=f); return b[2]-b[0],b[3]-b[1]
feats=[
 (573,"大澳","Tai O","4 m","coast", -12, 0.60),
 (1760,"鳳凰山","Lantau Peak","934 m","peak", 0, 0.0),
 (2436,"大東山","Sunset Peak","869 m","peak", -6, 0.13),
 (2663,"二東山","Yi Tung Shan","747 m","peak", 6, 0.32),
 (2804,"蓮花山","Lin Fa Shan","766 m","peak", 26, 0.12),
 (3377,"梅窩","Mui Wo","6 m","coast", -64, 0.50),
 (3408,"老虎頭","Lo Fu Tau","465 m","peak", 40, 0.30),
 (3872,"愉景灣","Discovery Bay","12 m","coast", 14, 0.62),
]
for lon,zh,en,el,kind,nudge,ylevel in feats:
    ax=int(screenx(lon))
    if kind=="peak":
        c0=max(0,ax-int(8*R)); c1=min(W,ax+int(8*R))
        seg=firstland[c0:c1]; segv=seg[seg>=0]
        ay=int(segv.min()) if len(segv) else waterY
        loc=np.where(firstland[c0:c1]==ay)[0]
        if len(loc): ax=c0+int(loc[0])
    else:
        ay=waterY-int(13*R)        # sit dot on the town rooftops
    tx=ax+int(nudge*R)
    ty=int(40*R+ylevel*(PAD_TOP-120*R))
    w1,h1=tw(d,zh,F_zh); w2,h2=tw(d,en,F_en); w3,h3=tw(d,el,F_el)
    d.text((tx-w1/2,ty),zh,font=F_zh,fill=BLACK)
    d.text((tx-w2/2,ty+h1+int(8*R)),en,font=F_en,fill=BLACK)
    d.text((tx-w3/2,ty+h1+h2+int(16*R)),el,font=F_el,fill=(70,70,70))
    leadtop=ty+h1+h2+h3+int(26*R)
    def haloline(p0,p1):
        d.line([p0,p1],fill=(255,255,255),width=max(3,int(3*R)))
        d.line([p0,p1],fill=(60,60,60),width=1)
    haloline((tx,leadtop),(tx,ay-int(15*R)))
    if abs(tx-ax)>2:
        haloline((tx,ay-int(15*R)),(ax,ay-int(4*R)))
    r=int(2.4*R)
    d.ellipse([ax-r-2,ay-r-2,ax+r+2,ay+r+2],fill=(255,255,255))
    d.ellipse([ax-r,ay-r,ax+r,ay+r],fill=BLACK)

img.save("compose_preview.png")
print("canvas",img.size,"sc",round(sc,2),"waterY",waterY)
