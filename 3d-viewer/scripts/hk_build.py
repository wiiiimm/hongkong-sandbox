import numpy as np, json, pyproj
m=json.load(open("hk5m_meta.json")); GW,GH=m["GW"],m["GH"]; cell=m["cellOut"]
aE,bE,aN,bN=m["aE"],m["bE"],m["aN"],m["bN"]
dtm=np.load("hk5m_grid.npy")
# grid cell centers (HK1980)
cols=np.arange(GW); rows=np.arange(GH)
E=aE*cols+bE; N=aN*rows+bN
EE,NN=np.meshgrid(E,N)
t=pyproj.Transformer.from_crs(2326,4326,always_xy=True)
lon,lat=t.transform(EE.ravel(),NN.ravel()); lon=lon.reshape(GH,GW); lat=lat.reshape(GH,GW)
# sample SRTM mosaic
mos=np.load("hk_srtm_mos.npy"); ext=json.load(open("hk_srtm_ext.json"))
mos=np.clip(np.where((mos<=-100)|(mos>2000),0,mos),0,None)
MW,MH=ext["W"],ext["H"]
fx=(lon-ext["lonL"])/(ext["lonR"]-ext["lonL"])*MW
fy=(ext["latT"]-lat)/(ext["latT"]-ext["latB"])*MH
fx=np.clip(fx,0,MW-1.001); fy=np.clip(fy,0,MH-1.001)
x0=fx.astype(int); y0=fy.astype(int); dx=fx-x0; dy=fy-y0
def g(yy,xx): return mos[yy,xx]
srtm=(g(y0,x0)*(1-dx)+g(y0,x0+1)*dx)*(1-dy)+(g(y0+1,x0)*(1-dx)+g(y0+1,x0+1)*dx)*dy
srtm=np.clip(srtm,0,None).astype(np.float32)
# land mask from DTM (>1m); zero SRTM over DTM-sea to match coastline
land=dtm>1.0
srtm=np.where(land,srtm,0.0)
dtm2=np.where(land,dtm,0.0)
# peaks (lon,lat,elev,name)
P=[("Tai Mo Shan 大帽山",114.1242,22.4108,957),("Lantau Peak 鳳凰山",113.9201,22.2492,934),
   ("Sunset Peak 大東山",113.9529,22.2572,869),("Ma On Shan 馬鞍山",114.2486,22.4017,702),
   ("Pat Sin Leng 八仙嶺",114.2200,22.4767,639),("Kowloon Peak 飛鵝山",114.2206,22.3367,602),
   ("Castle Peak 青山",113.9572,22.3869,583),("Victoria Peak 太平山",114.1455,22.2759,552),
   ("Sharp Peak 蚺蛇尖",114.3667,22.4358,468),("Lo Fu Tau 老虎頭",114.0000,22.2996,465)]
t2=pyproj.Transformer.from_crs(4326,2326,always_xy=True)
peaks=[]
for nm,lo,la,h in P:
    e,n=t2.transform(lo,la); c=int(round((e-bE)/aE)); r=int(round((n-bN)/aN))
    if 0<=c<GW and 0<=r<GH: peaks.append({"name":nm,"col":c,"row":r,"elev":h})
def dump(arr,name):
    json.dump({"w":GW,"h":GH,"cell":round(cell,2),"zmax":float(arr.max()),
               "elev":[int(round(v)) for v in arr.ravel()],"peaks":peaks},
              open(name,"w"),separators=(",",":"))
dump(dtm2,"hk-dtm5m.json"); dump(srtm,"hk-srtm.json")
json.dump({"aE":aE,"bE":bE,"aN":aN,"bN":bN,"W":GW,"H":GH},open("hk_georef.json","w"))
print("5m zmax %.0f  srtm zmax %.0f  peaks %d  grid %dx%d"%(dtm2.max(),srtm.max(),len(peaks),GW,GH))
