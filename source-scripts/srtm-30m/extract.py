import numpy as np
from scipy import ndimage
elev=np.load("elev.npy")
lonL,lonR,latT,latB,W,H,Z=open("extent.txt").read().split()
lonL,lonR,latT,latB=map(float,(lonL,lonR,latT,latB)); W=int(W);H=int(H)
elev=np.where(elev<-50,0,elev)           # kill nodata/bathymetry artefacts
elev=np.clip(elev,0,None)
land=elev>5.0
lab,n=ndimage.label(land)
# Lantau = component containing the global max (Lantau Peak)
yi,xi=np.unravel_index(np.argmax(elev),elev.shape)
lid=lab[yi,xi]
lantau=lab==lid
print("components",n,"| Lantau px area",int(lantau.sum()))
emasked=np.where(lantau,elev,0.0)
# south-facing orthographic skyline: per longitude column, max elevation over all latitudes(depth)
sky=emasked.max(axis=0)                    # length W
cols=np.where(lantau.any(axis=0))[0]
x0,x1=cols.min(),cols.max()
def lon2x(lon): return (lon-lonL)/(lonR-lonL)*W
print("island x px range",x0,x1,"width px",x1-x0)
print("island lon range %.4f..%.4f"%(lonL+x0/W*(lonR-lonL),lonL+x1/W*(lonR-lonL)))
# landmark check
marks={"Tai O":113.860,"Lantau Pk":113.910,"Sunset Pk":113.943,"Yi Tung":113.952,
       "Lin Fa":113.962,"Mui Wo":113.998,"Lo Fu Tau":114.012,"Disco Bay":114.018}
print("\nlandmark   lon      x-px   skyline_m(±窗)")
for k,lon in marks.items():
    x=int(round(lon2x(lon)))
    w=sky[max(0,x-6):x+7]
    print(f"{k:10s} {lon:.3f}  {x:5d}   {w.max():6.1f}")
np.save("skyline_raw.npy",sky)
np.save("lantau_mask.npy",lantau)
open("skymeta.txt","w").write(f"{x0} {x1} {lonL} {lonR} {W} {H} {float(elev.max())}\n")
