import math, os, urllib.request, time, numpy as np, json
from PIL import Image
Z=12
# HK bbox
W,E,S,N=113.80,114.48,22.13,22.58
def lon2x(lon): return (lon+180)/360*2**Z
def lat2y(lat):
    r=math.radians(lat); return (1-math.log(math.tan(r)+1/math.cos(r))/math.pi)/2*2**Z
x0=int(lon2x(W)); x1=int(lon2x(E)); y0=int(lat2y(N)); y1=int(lat2y(S))
print("tiles x",x0,x1,"y",y0,y1,"=",(x1-x0+1)*(y1-y0+1),"tiles")
base="https://elevation-tiles-prod.s3.amazonaws.com/terrarium/{z}/{x}/{y}.png"
os.makedirs("st",exist_ok=True)
TILE=256; nx=x1-x0+1; ny=y1-y0+1
mos=np.zeros((ny*TILE,nx*TILE),np.float32)
for j,ty in enumerate(range(y0,y1+1)):
    for i,tx in enumerate(range(x0,x1+1)):
        p=f"st/{tx}_{ty}.png"
        for a in range(4):
            try:
                if not os.path.exists(p): urllib.request.urlretrieve(base.format(z=Z,x=tx,y=ty),p)
                im=np.asarray(Image.open(p).convert("RGB")).astype(np.float32); break
            except Exception: time.sleep(0.4)
        e=(im[:,:,0]*256+im[:,:,1]+im[:,:,2]/256)-32768
        mos[j*TILE:(j+1)*TILE,i*TILE:(i+1)*TILE]=e
def x2lon(x): return x/2**Z*360-180
def y2lat(y):
    n=math.pi-2*math.pi*y/2**Z; return math.degrees(math.atan(math.sinh(n)))
ext={"lonL":x2lon(x0),"lonR":x2lon(x1+1),"latT":y2lat(y0),"latB":y2lat(y1+1),"W":nx*TILE,"H":ny*TILE}
np.save("hk_srtm_mos.npy",mos); json.dump(ext,open("hk_srtm_ext.json","w"))
print("mosaic",mos.shape,"zmax",round(float(mos.max())))
