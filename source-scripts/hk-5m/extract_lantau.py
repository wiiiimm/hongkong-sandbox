import numpy as np, time
H={}
f=open("Whole_HK_DTM_5m.asc")
for _ in range(6):
    k,v=f.readline().split(); H[k]=float(v)
ncols=int(H['ncols']); nrows=int(H['nrows']); cs=H['cellsize']
xll=H['xllcorner']; yll=H['yllcorner']
# crop window (HK1980 metres)
E0,E1=801000,821800; N0,N1=805500,819500
c0=int(round((E0-xll)/cs)); c1=int(round((E1-xll)/cs))      # column slice
# row i from TOP: northing_center = yll + (nrows-0.5)*cs - i*cs
ntop=yll+(nrows-0.5)*cs
i0=int(round((ntop-N1)/cs)); i1=int(round((ntop-N0)/cs))    # rows (top->bottom)
print("rows",i0,i1,"cols",c0,c1,"-> shape",(i1-i0+1,c1-c0+1))
t=time.time()
out=np.empty((i1-i0+1, c1-c0+1), np.float32)
i=0; r=0
for line in f:
    if i<i0: i+=1; continue
    if i>i1: break
    row=np.fromstring(line, sep=' ', dtype=np.float32)
    out[r]=row[c0:c1+1]; r+=1; i+=1
print("parsed in %.1fs"%(time.time()-t), "rows filled", r)
out=np.where(out<=-100, 0.0, out)     # NODATA -> sea
np.save("lantau5m.npy", out)
# geo meta: easting of local col0 center, northing of local row0(top) center
e_col0=xll+(c0+0.5)*cs
n_row0=ntop-i0*cs
open("lantau5m_meta.txt","w").write(f"{e_col0} {n_row0} {cs} {out.shape[1]} {out.shape[0]}\n")
print("elev min/max", float(out.min()), float(out.max()))
# check Lantau Peak vicinity
pe,pn=809842,812880
pj=int(round((pe-e_col0)/cs)); pi=int(round((n_row0-pn)/cs))
print("Lantau Peak local px (row,col)",pi,pj,"elev~",float(out[max(0,pi-2):pi+3, max(0,pj-2):pj+3].max()))
