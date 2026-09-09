"""Extend the ship terrain patch with cached native TIN, preserving every installed node."""
import json,sys,math,hashlib,importlib.util
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent;DOC=ROOT/'docs/astra-city/whampoa-high';sys.path.insert(0,str(HERE.parent/'assembly-support-review'));import native_terrain as native
spec=importlib.util.spec_from_file_location('fine',HERE.parent/'mui-wo-buildings/fine_terrain_audit.py');fine=importlib.util.module_from_spec(spec);spec.loader.exec_module(fine)
read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parentPath=ROOT/'3d-viewer/city/data/terrain.json';oldPath=ROOT/'3d-viewer/city/data/terrain-whampoa-ship.json';parent=read(parentPath);old=read(oldPath);g=parent['meta']['georef'];cell=g['aE'];cat=read(HERE/'candidates/catalogue.json');bb=[min(m['worldBounds'][0][0]for m in cat['models'])-20,min(m['worldBounds'][0][2]for m in cat['models'])-20,max(m['worldBounds'][1][0]for m in cat['models'])+20,max(m['worldBounds'][1][2]for m in cat['models'])+20]
a,b,c,d=old['coarseCells'];c0=min(a,math.floor((bb[0]+834500-g['bE'])/cell));r0=min(b,math.floor((bb[1]-816500+g['bN'])/cell));c1=max(c,math.ceil((bb[2]+834500-g['bE'])/cell));r1=max(d,math.ceil((bb[3]-816500+g['bN'])/cell));x0=g['bE']+c0*cell-834500;z0=816500-g['bN']+r0*cell;w=round((c1-c0)*cell)+1;h=round((r1-r0)*cell)+1
xx,zz=np.meshgrid(np.arange(w)+x0,np.arange(h)+z0);pts=np.c_[xx.ravel(),zz.ravel()];heights=np.full(len(pts),-np.inf);sources=[]
for sh in ['11-NE-21A','11-NE-21C']:
 mp=next((HERE/'local'/sh/'converted/native-terrain').glob('*/manifest.json'));m,t,_,_,usable,tree=native.terrain_index(mp.parent);heights=np.maximum(heights,native.samples(pts,usable,tree));sources.append({'sheet':sh,'manifest':str(mp.relative_to(ROOT)),'manifestSha256':sha(mp),'worldBounds':t['worldBounds'],'sourceHashes':t['sourceHashes']})
raw=fine.DemSampler(parent);render=fine.DemSampler(parent,rendered=True);oldSampler=fine.DemSampler(old,rendered=True);og=old['meta']['georef'];ox=og['bE']-834500;oz=816500-og['bN'];ox1=ox+old['w']-1;oz1=oz+old['h']-1
elev=[];draw=[];veg=[];preserved=0;missing=0;transition=0
for i,(x,z)in enumerate(pts):
 col=i%w;row=i//w
 if ox<=x<=ox1 and oz<=z<=oz1:
  j=round(z-oz)*old['w']+round(x-ox);elev.append(old['elev'][j]);draw.append(old.get('renderedElev',old['elev'])[j]);veg.append(old['vegetation'][j]);preserved+=1;continue
 before=render.ground(x,z);rawBefore=raw.ground(x,z);outer=min(1,min(col,row,w-1-col,h-1-row)/10);distance=math.hypot(max(ox-x,0,x-ox1),max(oz-z,0,z-oz1));alpha=min(outer,distance/10,1)
 if not np.isfinite(heights[i]):missing+=1;alpha=0
 if rawBefore<=0:alpha=0
 v=float(heights[i]*alpha+before*(1-alpha)) if alpha else before
 if 0<alpha<1:transition+=1
 elev.append(rawBefore if rawBefore<=0 else round(v,6));draw.append(round(v,6));cc=round((x+834500-g['bE'])/cell);rr=round((z-816500+g['bN'])/cell);veg.append(parent['vegetation'][rr*parent['w']+cc])
assert preserved==old['w']*old['h'];assert missing==0
patch={'id':'whampoa-estates-native','w':w,'h':h,'cell':1,'coarseCells':[c0,r0,c1,r1],'elev':elev,'renderedElev':draw,'vegetation':veg,'meta':{'georef':{'aE':1,'aN':-1,'bE':x0+834500,'bN':816500-z0,'W':w,'H':h},'parentTerrain':'city/data/terrain.json','parentSha256':sha(parentPath),'targetUids':sorted({m['uid']for m in cat['models']}|set(old['meta'].get('targetUids',[]))),'source':{'provider':'Lands Department/HKSAR','verticalDatum':'HKPD','crs':'EPSG:2326','sources':sources,'policy':'Native TIN at 1m spacing; 10m transition to parent and preserved ship patch. Existing nodes/water/vegetation retained. No building elevation changes.'}}}
if 'hydro'in old:patch['hydro']=old['hydro']
path=HERE/'terrain-extension.json';path.write_text(json.dumps(patch,separators=(',',':'))+'\n');report={'issue':'HKS-226','nodes':len(pts),'nativeCoveredNodes':len(pts)-missing,'preservedOldNodes':preserved,'transitionNodes':transition,'replaces':{'url':'city/data/terrain-whampoa-ship.json','sha256':sha(oldPath)},'sha256':sha(path),'source':str(path.relative_to(ROOT)),'destination':'city/data/terrain-whampoa-estates.json','resolution':1,'area':'Whampoa ship and estate native ground','nativeSources':sources}
(DOC/'terrain.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['nodes','nativeCoveredNodes','preservedOldNodes','transitionNodes']}))
plan=read(HERE/'plan.json');plan['topLevelTerrainPatches']=[{k:report[k]for k in ['source','sha256','destination','resolution','area','replaces']}];(HERE/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
