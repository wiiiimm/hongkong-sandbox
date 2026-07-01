import numpy as np
from scipy.ndimage import gaussian_filter

elev=np.load("elev.npy"); elev=np.where(elev<-50,0,elev); elev=np.clip(elev,0,None)
mask=np.load("lantau_mask.npy")
x0,x1=239,2793
rows=np.where(mask.any(axis=1))[0]; r0,r1=rows.min(),rows.max()
E=elev[r0:r1+1, x0:x1+1].astype(float)
M=mask[r0:r1+1, x0:x1+1]
E=np.where(M,E,0.0)
Es=gaussian_filter(E,1.2)
RH,RW=E.shape
print("island grid RH,RW",RH,RW)

# ---- hillshade (light from upper-left of the view: WSW, high) ----
px=8.8  # m per pixel approx
gy,gx=np.gradient(Es,px,px)          # gy=d/d(row=north-south), gx=d/d(col=east-west)
slope=np.arctan(np.hypot(gx,gy))
aspect=np.arctan2(-gx, gy)           # orient
az=np.radians(300.0); alt=np.radians(38.0)  # light azimuth/altitude
hs=(np.sin(alt)*np.cos(slope)+np.cos(alt)*np.sin(slope)*np.cos(az-aspect))
hs=np.clip(hs,0,1)
# emphasize south-face modelling: combine with downslope-southness
tone=0.25+0.75*hs                    # 0..1 lit
tone=np.clip(tone,0,1)

# ---- oblique projection params ----
VE  =0.62          # px per metre (vertical)
TILT=130.0/RH      # px per row of depth (recession)
depth=(RH-1-np.arange(RH))[:,None]            # 0 at south(near, r=RH-1)
syrel = -E*VE - depth*TILT                    # negative = up
# canvas
TOPMARG=70.0
off = TOPMARG - syrel.min()
SY = syrel+off                                # screen y per (r,c), land
baseline = (0.0+off)                          # sea-level near edge (elev0,depth0)
Hout=int(np.ceil(SY.max()))+1
Hcanvas=int(baseline)+1
print("Hout(land top..) baseline",Hout,round(baseline,1))

# ---- per-column hidden-surface fill (nearest covering sample wins) ----
INF=1e9
toneimg=np.full((Hcanvas,RW),np.nan,dtype=np.float32)
Ygrid=np.arange(Hcanvas)
for c in range(RW):
    land=M[:,c]
    sy=SY[:,c].copy()
    sy[~land]=INF
    # near->far : r descending
    sy_ntf=sy[::-1]; tone_ntf=tone[:,c][::-1]
    m=np.minimum.accumulate(sy_ntf)           # non-increasing
    mr=m[::-1]                                  # non-decreasing
    # last index in mr with mr<=y  -> pos-1
    pos=np.searchsorted(mr, Ygrid, side='right')-1   # index into mr (=reversed m)
    valid=pos>=0
    korig=(len(m)-1)-pos                        # original near-index k0
    col=np.full(Hcanvas,np.nan,dtype=np.float32)
    kk=korig[valid]
    col[valid]=tone_ntf[kk]
    toneimg[:,c]=col

np.save("oblique_tone.npy",toneimg)
np.save("oblique_meta.npy",np.array([RW,Hcanvas,baseline,VE,TILT,off]))
# quick grayscale preview
from PIL import Image
img=np.where(np.isnan(toneimg),1.0,toneimg)
Image.fromarray((img*255).astype(np.uint8)).save("oblique_gray.png")
print("saved oblique_gray.png", img.shape)
