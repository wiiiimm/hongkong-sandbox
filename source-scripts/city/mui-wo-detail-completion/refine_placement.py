"""Reuse narrow native-TIN refinement method; two additional source-grid seams.
Also reference the existing b90c15f5 patch5 instead of rebuilding that correction.
"""
import math,sys
import numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from run import HERE,ROOT,DOC,load,dump,sha,existing_folders
from placement import fine,terrain_index,grid_triangles,surface_contacts,upper_envelope
sys.path.insert(0,str(HERE.parent/'mui-wo-final-review'))
from refine import source_samples
from bake_model_geometry import bake

def main():
 parentPath=ROOT/'3d-viewer/city/data/terrain-mui-wo.json';parent=load(parentPath);g=parent['meta']['georef'];sampler=fine.DemSampler(parent,rendered=True);rawSampler=fine.DemSampler(parent)
 prior=load(HERE.parent/'mui-wo-final-review/terrain-refinements.json');assert prior['parentSha256']==sha(parentPath.read_bytes());patches=[p for p in prior['patches'] if p['id']=='mui-wo-refinement-5'];report=[]
 entries={e['uid']:e for e in load(HERE/'compact/catalogue.json')['models']};buildings={b['uid']:b for b in load(ROOT/'3d-viewer/city/data/mui-wo-buildings.json')['buildings']}
 folders={load(p/'manifest.json')['tile']:p for p in existing_folders()};folders.update({p.name:p for p in (HERE/'staged').iterdir()})
 for uid in ['landsd/202951:0','landsd/208041:0']:
  e=entries[uid];b=buildings[uid];footprint=Polygon(b['rings'][0],b['rings'][1:]);bounds=e['worldBounds'];area=footprint.union(box(bounds[0][0],bounds[0][2],bounds[1][0],bounds[1][2]));x0,z0,x1,z1=area.buffer(10).bounds
  c0=math.floor((x0+834500-g['bE'])/5);c1=math.ceil((x1+834500-g['bE'])/5);r0=math.floor((816500-z0-g['bN'])/-5);r1=math.ceil((816500-z1-g['bN'])/-5)
  x0=g['bE']+5*c0-834500;x1=g['bE']+5*c1-834500;z0=816500-g['bN']+5*r0;z1=816500-g['bN']+5*r1;extent=box(x0,z0,x1,z1);w=round(x1-x0)+1;h=round(z1-z0)+1;items=[]
  for tile,folder in folders.items():
   m=load(folder/'manifest.json');a=m['terrain']['worldBounds']
   if not extent.intersects(box(a[0][0],a[0][2],a[1][0],a[1][2])):continue
   _,s,_,_,usable,tree=terrain_index(folder);items.append({'manifest':str((folder/'manifest.json').relative_to(ROOT)),'tile':tile,'revision':m['tileRevision'],'hashes':s['sourceHashes'],'usable':usable,'tree':tree})
  xx,zz=np.meshgrid(np.arange(w)+x0,np.arange(h)+z0);points=np.c_[xx.reshape(-1),zz.reshape(-1)];native,hits=source_samples(points,items);elev=[];vegetation=[];waterChanged=0
  for i,(x,z) in enumerate(points):
   c=i%w;r=i//w;old=sampler.ground(x,z);raw=rawSampler.ground(x,z);weight=min(1,min(c,r,w-1-c,h-1-r)/5)
   if not np.isfinite(native[i]) or raw<=0:weight=0
   y=float(native[i]*weight+old*(1-weight)) if weight else old;elev.append(round(y,6));waterChanged+=raw<=0 and y>0
   cc=min(parent['w']-1,max(0,round((x+834500-g['bE'])/5)));rr=min(parent['h']-1,max(0,round((816500-z-g['bN'])/-5)));vegetation.append(parent['vegetation'][rr*parent['w']+cc])
  sources=[{'manifest':i['manifest'],'tile':i['tile'],'revision':i['revision'],'sourceHashes':i['hashes']} for i in items];name='mui-wo-model-refinement-'+uid.split('/')[1].split(':')[0]
  patch={'id':name,'w':w,'h':h,'cell':1,'elev':elev,'vegetation':vegetation,'coarseCells':[c0,r0,c1,r1],'meta':{'title':'Mui Wo · source terrain at detailed model','georef':{'aE':1,'aN':-1,'bE':x0+834500,'bN':816500-z0,'W':w,'H':h},'source':{'provider':'Lands Department / HKSAR Government','crs':'EPSG:2326','verticalDatum':'HKPD','nativeSources':sources,'policy':'Exact original native TIN samples on1m grid;5m outer transition to unchanged parent. Sampling spacing is not surveyed accuracy. No model or original footprint elevation alteration.'},'targetUids':[uid],'parentTerrain':'city/data/terrain-mui-wo.json','parentSha256':sha(parentPath.read_bytes()),'transitionMetres':5}}
  dump(HERE/'source-grids'/(name+'.json'),{'meta':{'georef':patch['meta']['georef']},'w':w,'h':h,'elev':[float(n) if np.isfinite(n) else None for n in native],'source':sources});patches.append(patch);report.append({'id':name,'uid':uid,'vertices':w*h,'sourceCovered':int(np.isfinite(native).sum()),'waterNodesChanged':int(waterChanged)})
 bundle={'schemaVersion':1,'kind':'nested-source-terrain-refinements','parentTerrainURL':'city/data/terrain-mui-wo.json','parentSha256':sha(parentPath.read_bytes()),'patches':patches,'reusedPriorPatch':{'file':'source-scripts/city/mui-wo-final-review/terrain-refinements.json','id':'mui-wo-refinement-5','sha256':sha((HERE.parent/'mui-wo-final-review/terrain-refinements.json').read_bytes())},'dependentEstimatedBaseUpdates':'source-scripts/city/mui-wo-detail-completion/building-estimate-updates.json','integration':'Attach children once, remove corresponding parent cells, preserve all parent/source elevations; apply original guarded estimated-base updates together. Do not duplicate patch5 when integrating the full original b90c15f5 bundle.'}
 dump(HERE/'terrain-refinements.json',bundle);updates=load(HERE.parent/'mui-wo-final-review/building-estimate-updates.json');updates['originalSourcePayload']='source-scripts/city/mui-wo-final-review/building-estimate-updates.json';updates['originalRefinementSha256']=updates['refinementSha256'];updates['refinementSha256']=sha((HERE/'terrain-refinements.json').read_bytes());dump(HERE/'building-estimate-updates.json',updates);dump(DOC/'placement-refinements.json',{'parentSha256':bundle['parentSha256'],'reusedPatch':'mui-wo-refinement-5','newPatches':report,'gridVertices':sum(p['w']*p['h'] for p in patches),'bytes':(HERE/'terrain-refinements.json').stat().st_size,'published':False});print(report)
if __name__=='__main__':main()
