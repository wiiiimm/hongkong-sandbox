import math, numpy as np
from PIL import Image
Z=14; X0,X1=13372,13382; Y0,Y1=7148,7155; TILE=256
nx=X1-X0+1; ny=Y1-Y0+1; W=nx*TILE; H=ny*TILE
elev=np.zeros((H,W),dtype=np.float32)
for j,ty in enumerate(range(Y0,Y1+1)):
    for i,tx in enumerate(range(X0,X1+1)):
        im=np.asarray(Image.open(f"tiles/{Z}_{tx}_{ty}.png").convert("RGB")).astype(np.float32)
        e=(im[:,:,0]*256.0+im[:,:,1]+im[:,:,2]/256.0)-32768.0
        elev[j*TILE:(j+1)*TILE,i*TILE:(i+1)*TILE]=e
def tlon(x): return x/2**Z*360-180
def tlat(y): return math.degrees(math.atan(math.sinh(math.pi-2*math.pi*y/2**Z)))
lonL,lonR=tlon(X0),tlon(X1+1); latT,latB=tlat(Y0),tlat(Y1+1)
np.save("elev.npy",elev)
open("extent.txt","w").write(f"{lonL} {lonR} {latT} {latB} {W} {H} {Z}\n")
print("grid",elev.shape,"elev",round(float(elev.min()),1),round(float(elev.max()),1))
print("extent lon %.4f..%.4f lat %.4f..%.4f"%(lonL,lonR,latB,latT))
# sanity: highest point location
yi,xi=np.unravel_index(np.argmax(elev),elev.shape)
plon=lonL+(xi+0.5)/W*(lonR-lonL)
plat=latT+(yi+0.5)/H*(latB-latT)
print("max elev %.1f m at lon %.4f lat %.4f (Lantau Peak ~113.910,22.254)"%(elev.max(),plon,plat))
