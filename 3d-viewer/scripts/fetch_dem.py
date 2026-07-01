import os, urllib.request, time
from PIL import Image
Z=14; X0,X1=13372,13382; Y0,Y1=7148,7155
base="https://elevation-tiles-prod.s3.amazonaws.com/terrarium/{z}/{x}/{y}.png"
os.makedirs("tiles",exist_ok=True)
def ok(p):
    try:
        im=Image.open(p); im.load(); return im.size==(256,256)
    except Exception: return False
todo=[(tx,ty) for ty in range(Y0,Y1+1) for tx in range(X0,X1+1)]
done=0
for tx,ty in todo:
    p=f"/tmp/lantau/tiles/{Z}_{tx}_{ty}.png"
    if os.path.exists(p) and ok(p): done+=1; continue
    if os.path.exists(p): os.remove(p)
    for a in range(5):
        try:
            urllib.request.urlretrieve(base.format(z=Z,x=tx,y=ty),p)
            if ok(p): done+=1; break
            os.remove(p)
        except Exception: time.sleep(0.4*(a+1))
print("valid tiles:",done,"/",len(todo))
