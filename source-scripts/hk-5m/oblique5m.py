import numpy as np, json
from scipy.ndimage import gaussian_filter
elev=np.load("l5_elev.npy"); mask=np.load("l5_mask.npy")
E0=np.where(mask,elev,0.0)
rows=np.where(mask.any(axis=1))[0]; cols=np.where(mask.any(axis=0))[0]
r0,r1,c0,c1=rows.min(),rows.max(),cols.min(),cols.max()
E=E0[r0:r1+1,c0:c1+1].copy(); M=mask[r0:r1+1,c0:c1+1].copy()
RH,RW=E.shape
print("island bbox rows",r0,r1,"cols",c0,c1,"-> RH,RW",RH,RW)
# taper ends into the sea (full-grid cols -> local). West past Tai O, east past Discovery Bay.
def loc(fc): return fc-c0
wc,wf = loc(360),loc(470)      # west fade  (full grid cols)
ef,ec = loc(3900),loc(3990)    # east fade  (just past Discovery Bay col3872)
ix=np.arange(RW); fac=np.ones(RW)
fac=np.where(ix<wf,0.5-0.5*np.cos(np.pi*np.clip((ix-wc)/(wf-wc),0,1)),fac)
fac=np.where(ix>ef,0.5+0.5*np.cos(np.pi*np.clip((ix-ef)/(ec-ef),0,1)),fac)
fac=np.clip(fac,0,1); E=E*fac[None,:]; M=M&(fac[None,:]>0.03); E=np.where(M,E,0.0)
Es=gaussian_filter(E,2.0)
px=5.0; gy,gx=np.gradient(Es,px,px)
slope=np.arctan(np.hypot(gx,gy)); aspect=np.arctan2(-gx,gy)
hs=np.clip(np.sin(np.radians(38))*np.cos(slope)+np.cos(np.radians(38))*np.sin(slope)*np.cos(np.radians(300)-aspect),0,1)
tone=np.clip(0.25+0.75*hs,0,1)
VE=0.82; TILT=150.0/RH; depth=(RH-1-np.arange(RH))[:,None]
syrel=-E*VE-depth*TILT; off=70.0-syrel.min(); SY=syrel+off; baseline=off
Hc=int(np.ceil(SY.max()))+1; Yg=np.arange(Hc); INF=1e9
toneimg=np.full((Hc,RW),np.nan,np.float32); Eimg=np.full((Hc,RW),np.nan,np.float32)
for c in range(RW):
    land=M[:,c]
    if not land.any(): continue
    sy=SY[:,c].copy(); sy[~land]=INF
    m=np.minimum.accumulate(sy[::-1]); mr=m[::-1]
    pos=np.searchsorted(mr,Yg,side='right')-1; valid=pos>=0
    k=(len(m)-1)-pos; tn=tone[:,c][::-1]; en=E[:,c][::-1]; kk=k[valid]
    toneimg[valid,c]=tn[kk]; Eimg[valid,c]=en[kk]
np.save("oblique_tone.npy",toneimg); np.save("oblique_E.npy",Eimg)
np.save("oblique_meta.npy",np.array([RW,Hc,baseline,VE,TILT,off]))
# remember crop origin for label mapping
open("oblique5m_crop.txt","w").write(f"{c0} {r0} {RW} {Hc}\n")
from PIL import Image
img=np.where(np.isnan(toneimg),1.0,toneimg)
Image.fromarray((img*255).astype(np.uint8)).save("oblique5m_gray.png")
print("oblique 5m", toneimg.shape, "baseline", round(baseline,1))
