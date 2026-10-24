"""One-metre source sampling for a gentle site crossing quantised sheet edges."""
import json
from pathlib import Path
import numpy as np
import native_terrain as n
import terrain_patches as t
h=Path(__file__).resolve().parent;p=n.read(h/'terrain-patches/support-native-22089-0.json');parent=n.read(n.ROOT/'3d-viewer'/p['meta']['parentTerrain']);bb=t.bounds(p);w=p['w'];hh=p['h'];xx,zz=np.meshgrid(np.arange(w)+bb[0],np.arange(hh)+bb[1]);pts=np.c_[xx.ravel(),zz.ravel()];ys=np.full(len(pts),-np.inf)
for s in p['meta']['source']['nativeSources']:
 assert n.sha(n.ROOT/s['manifest'])==s['manifestSha256']
 for f in s['files']:assert n.sha(n.ROOT/f['path'])==f['sha256']
 _,_,_,_,usable,tree=n.terrain_index((n.ROOT/s['manifest']).parent);ys=np.maximum(ys,n.samples(pts,usable,tree))
assert np.isfinite(ys).all(),'Source coverage missing at grid nodes';old=t.fine.DemSampler(parent,rendered=True);raw=t.fine.DemSampler(parent);errors=[]
for i,(x,z) in enumerate(pts):
 c=i%w;r=i//w;before=old.ground(x,z);vraw=raw.ground(x,z);alpha=min(1,min(c,r,w-1-c,hh-1-r)/10);after=ys[i]*alpha+before*(1-alpha) if vraw>0 else before;p['renderedElev'][i]=float(after);p['elev'][i]=float(after) if vraw>0 else vraw
 if c in [0,w-1] or r in [0,hh-1]:errors.append(abs(after-before))
p['id']='support-grid-hkdi-22089-0';p['meta']['source']['policy']='All 1m grid nodes sample verified native source triangles from four adjoining sheets. Interpolation between samples bridges a3cm source-edge quantisation gap;1m spacing is not survey accuracy.10m boundary transition to unchanged parent. Raw water mask preserved. No building shifts.';folder=h/'grid-hkdi';folder.mkdir(exist_ok=True);path=folder/(p['id']+'.json');path.write_text(json.dumps(p,separators=(',',':'))+'\n');d={'issue':'HKS-214','patches':[{'path':str(path.relative_to(n.ROOT)),'sha256':n.sha(path),'parentTerrainURL':p['meta']['parentTerrain'],'parentSha256':n.sha(n.ROOT/'3d-viewer'/p['meta']['parentTerrain']),'coarseCells':p['coarseCells'],'gridNodes':len(pts),'nativeCoveredNodes':int(np.isfinite(ys).sum()),'boundaryMaxError':max(errors),'estimatedNodeHeights':0,'interpolation':'1m native sampled grid, not exact source mesh','publicationApproved':False}]};(n.OUT/'grid-hkdi.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d['patches'][0]))
