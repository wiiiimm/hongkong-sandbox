import urllib.request, zipfile, os, numpy as np, time, json
t0=time.time()
if not os.path.exists("dtm.zip"):
    urllib.request.urlretrieve("https://www.landsd.gov.hk/landsd_psi_data/SMO/data/Whole_HK_DTM_5m.zip","dtm.zip")
z=zipfile.ZipFile("dtm.zip"); asc=z.namelist()[0]
f=z.open(asc)
H={}
for _ in range(6):
    k,v=f.readline().split(); H[k.decode()]=float(v)
ncols=int(H['ncols']); nrows=int(H['nrows']); cs=H['cellsize']; xll=H['xllcorner']; yll=H['yllcorner']
FAC=14; GW=ncols//FAC; GH=nrows//FAC
out=np.zeros((GH,GW),np.float32); acc=np.zeros(GW,np.float64); cnt=0; orow=0
useC=GW*FAC
for i in range(nrows):
    line=f.readline()
    if orow>=GH: break
    row=np.frombuffer(bytearray(line),dtype=np.uint8)  # placeholder
    vals=np.fromstring(line, sep=' ', dtype=np.float32)
    vals=np.where(vals<=-100,0,vals)[:useC].reshape(GW,FAC).mean(axis=1)
    acc+=vals; cnt+=1
    if cnt==FAC:
        out[orow]=acc/FAC; acc[:]=0; cnt=0; orow+=1
out=np.clip(out,0,None)
np.save("hk5m_grid.npy", out)
# georef of downsampled grid (HK1980): cell center
cellOut=cs*FAC
e0=xll+cellOut/2; n_top=yll+(nrows-0.5)*cs  # north of original
# downsampled row0 covers original rows 0..FAC-1 (top=north). center northing:
n0=yll+(nrows-FAC/2)*cs
meta={"GW":GW,"GH":GH,"cellOut":cellOut,"e0":e0,"n0":n0,
      "aE":cellOut,"bE":e0,"aN":-cellOut,"bN":n0,
      "xll":xll,"yll":yll,"ncols":ncols,"nrows":nrows,"cs":cs,"FAC":FAC}
json.dump(meta,open("hk5m_meta.json","w"))
print("done %.0fs grid %dx%d cellOut %.0fm zmax %.0f"%(time.time()-t0,GW,GH,cellOut,out.max()))
