import numpy as np, pyproj
from scipy.ndimage import label, gaussian_filter
out=np.load("lantau5m.npy")
e_col0,n_row0,cs,W,Hh=open("lantau5m_meta.txt").read().split()
e_col0,n_row0,cs=float(e_col0),float(n_row0),float(cs); W=int(W);Hh=int(Hh)
elev=np.clip(np.where(out<=-100,0,out),0,None)
land=elev>5.0
lab,n=label(land)
pi,pj=np.unravel_index(np.argmax(elev),elev.shape)
lantau=lab==lab[pi,pj]
print("components",n,"Lantau px",int(lantau.sum()),"max",float(elev.max()))
np.save("l5_elev.npy",elev.astype(np.float32))
np.save("l5_mask.npy",lantau)
# feature -> local (col,row)
t=pyproj.Transformer.from_crs(4326,2326,always_xy=True)
feats=[("Tai O 大澳","Tai O",113.8625,22.252,4),
       ("Lantau Peak 鳳凰山","Lantau Peak",113.9095,22.2545,934),
       ("Sunset Peak 大東山","Sunset Peak",113.9535,22.2589,869),
       ("Yi Tung Shan 二東山","Yi Tung Shan",113.9625,22.255,747),
       ("Lin Fa Shan 蓮花山","Lin Fa Shan",113.9745,22.258,766),
       ("Mui Wo 梅窩","Mui Wo",113.9985,22.266,6),
       ("Lo Fu Tau 老虎頭","Lo Fu Tau",114.0125,22.283,465),
       ("Discovery Bay 愉景灣","Discovery Bay",114.0225,22.295,12)]
rows=[]
for nm,en,lon,lat,h in feats:
    E,N=t.transform(lon,lat); c=(E-e_col0)/cs; r=(n_row0-N)/cs
    rows.append((nm,lon,lat,h,c,r))
    print(f"{en:14s} col{c:6.0f} row{r:6.0f}")
import json
json.dump([{"name":nm,"lon":lon,"lat":lat,"elev":h,"col":c,"row":r} for nm,lon,lat,h,c,r in rows],
          open("l5_feats.json","w"))
