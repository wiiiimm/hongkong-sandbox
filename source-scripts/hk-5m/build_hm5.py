import numpy as np, json
from scipy.ndimage import zoom, gaussian_filter
elev=np.load("l5_elev.npy"); mask=np.load("l5_mask.npy")
e_col0,n_row0,cs,W,Hh=open("lantau5m_meta.txt").read().split(); cs=float(cs)
E0=np.where(mask,elev,0.0)
rows=np.where(mask.any(axis=1))[0]; cols=np.where(mask.any(axis=0))[0]
r0,r1,c0,c1=rows.min(),rows.max(),cols.min(),cols.max()
E=gaussian_filter(E0[r0:r1+1,c0:c1+1],1.0); M=mask[r0:r1+1,c0:c1+1]
TW=560; f=TW/E.shape[1]
Ed=zoom(E,f,order=1); Md=zoom(M.astype(float),f,order=1)>0.4
Ed=np.where(Md,Ed,0.0); h,w=Ed.shape; cell=cs/f
feats=json.load(open("l5_feats.json")); peaks=[]
for ft in feats:
    ci=int(round((ft["col"]-c0)*f)); ri=int(round((ft["row"]-r0)*f))
    if ft["kind"]=="peak":
        rad=int(round(150/cell))
        a=Ed[max(0,ri-rad):ri+rad+1,max(0,ci-rad):ci+rad+1]
        dr,dc=np.unravel_index(np.argmax(a),a.shape); ri=max(0,ri-rad)+int(dr); ci=max(0,ci-rad)+int(dc)
    ci=min(max(ci,0),w-1); ri=min(max(ri,0),h-1)
    peaks.append({"name":ft["name"],"col":int(ci),"row":int(ri),"elev":int(ft["elev"])})
data={"w":w,"h":h,"cell":round(cell,2),"zmax":float(Ed.max()),
      "elev":[int(round(v)) for v in Ed.flatten().tolist()],"peaks":peaks}
json.dump(data,open("heightmap_5m.json","w"))
print("hm5",w,"x",h,"cell",round(cell,1),"m zmax",round(Ed.max()))
