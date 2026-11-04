"""Stage bounded 1 m source-TIN refinements; preserve the live 5 m parent.
One-metre spacing is a visualisation sample interval, not surveyed accuracy.
"""
import hashlib,json,math,pathlib,sys
import numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from audit import ROOT,HERE,DOC,OUT,load,sha,terrain_index,fine,plane_values
GROUPS=[['landsd/174150:0'],['landsd/195964:0'],['landsd/206484:0'],['landsd/336510:0'],['landsd/201705:0','landsd/206970:0']]
def source_samples(points,items):
 import shapely
 result=np.full(len(points),-np.inf);hits=np.zeros(len(points),dtype=int)
 for item in items:
  usable,tree=item['usable'],item['tree'];pi,ti=tree.query(shapely.points(points),predicate='covered_by');tri=usable[ti]
  a=tri[:,0,:];v0=tri[:,1,:][:,[0,2]]-a[:,[0,2]];v1=tri[:,2,:][:,[0,2]]-a[:,[0,2]];q=points[pi]-a[:,[0,2]];den=v0[:,0]*v1[:,1]-v0[:,1]*v1[:,0]
  u=(q[:,0]*v1[:,1]-q[:,1]*v1[:,0])/den;v=(v0[:,0]*q[:,1]-v0[:,1]*q[:,0])/den
  y=a[:,1]+u*(tri[:,1,1]-a[:,1])+v*(tri[:,2,1]-a[:,1]);np.maximum.at(result,pi,y);np.add.at(hits,pi,1)
 return result,hits

def main():
 baseline=OUT/'terrain-mui-wo.json';parent=load(baseline);g=parent['meta']['georef'];parentSampler=fine.DemSampler(parent,rendered=True);cases={r['uid']:r for r in load(DOC/'exact-source-audit.json')['cases']};patches=[];plans=[]
 for n,uids in enumerate(GROUPS):
  area=unary_union([Polygon(cases[u]['rings'][0],cases[u]['rings'][1:]) for u in uids]);padding=2 if uids==['landsd/195964:0'] else 20;transition=padding/2;x0,z0,x1,z1=area.buffer(padding).bounds
  c0=math.floor((x0+834500-g['bE'])/5);r0=math.floor((816500-z0-g['bN'])/-5);c1=math.ceil((x1+834500-g['bE'])/5);r1=math.ceil((816500-z1-g['bN'])/-5)
  x0=g['bE']+c0*5-834500;z0=816500-g['bN']+r0*5;x1=g['bE']+c1*5-834500;z1=816500-g['bN']+r1*5;extent=box(x0,z0,x1,z1);w=round(x1-x0)+1;h=round(z1-z0)+1
  items=[]
  folders=[ROOT/'docs/astra-city/mui-wo-buildings/review/model-sample',*sorted((HERE.parent/'mui-wo-models/staged').iterdir()),*sorted((HERE.parent/'mui-wo-completion/staged').iterdir()),*sorted((HERE/'staged').iterdir())]
  for folder in folders:
   path=folder/'manifest.json'
   if not path.exists():continue
   m=load(path);b=m['terrain']['worldBounds']
   if not extent.intersects(box(b[0][0],b[0][2],b[1][0],b[1][2])):continue
   m,s,t,v,usable,tree=terrain_index(folder);items.append({'manifest':str(path.relative_to(ROOT)),'tile':m['tile'],'revision':m['tileRevision'],'hashes':s['sourceHashes'],'usable':usable,'tree':tree})
  xx,zz=np.meshgrid(np.arange(w)+x0,np.arange(h)+z0);points=np.c_[xx.reshape(-1),zz.reshape(-1)];native,hits=source_samples(points,items);elev=[];vegetation=[];edgeError=0;waterChanged=0;blendWeights=[]
  for i,(x,z) in enumerate(points):
   c=i%w;r=i//w;old=parentSampler.ground(x,z);alpha=min(1,min(c,r,w-1-c,h-1-r)/transition);raw=fine.DemSampler(parent).ground(x,z)
   # Existing water semantics remain authoritative; do not infer hydrology from the source TIN.
   if not np.isfinite(native[i]) or raw<=0:alpha=0
   y=float(native[i]*alpha+old*(1-alpha)) if alpha else old;elev.append(round(y,6));blendWeights.append(alpha)
   cc=min(parent['w']-1,max(0,round((x+834500-g['bE'])/5)));rr=min(parent['h']-1,max(0,round((816500-z-g['bN'])/-5)));vegetation.append(parent['vegetation'][rr*parent['w']+cc])
   if c in [0,w-1] or r in [0,h-1]:edgeError=max(edgeError,abs(y-old))
   if raw<=0 and y>0:waterChanged+=1
  source=[{'manifest':i['manifest'],'tile':i['tile'],'revision':i['revision'],'sourceHashes':i['hashes']} for i in items];name='mui-wo-refinement-'+str(n+1)
  patch={'id':name,'w':w,'h':h,'cell':1,'elev':elev,'vegetation':vegetation,'coarseCells':[c0,r0,c1,r1],'meta':{'title':'Mui Wo · source TIN refinement','georef':{'aE':1,'aN':-1,'bE':x0+834500,'bN':816500-z0,'W':w,'H':h},'source':{'provider':'Lands Department / HKSAR Government','crs':'EPSG:2326','verticalDatum':'HKPD','nativeSources':source,'policy':f'Actual original TIN barycentric samples on a 1 m grid, with a {transition:g} m outer transition to the unmodified parent rendered terrain. 1 m is sample spacing, not surveyed accuracy. No source roof, foundation or recorded elevation adjustment.'},'targetUids':uids,'parentTerrain':'city/data/terrain-mui-wo.json','parentSha256':sha(baseline),'transitionMetres':transition}}
  nativePayload={'w':w,'h':h,'meta':{'georef':patch['meta']['georef']},'source':source,'elev':[float(v) if np.isfinite(v) else None for v in native],'valid':[bool(np.isfinite(v)) for v in native],'method':'Exact native TIN sampling before display transition. Maximum source height when triangles overlap; absent coverage stays null.'}
  target=HERE/'source-grids';target.mkdir(exist_ok=True);(target/(name+'.json')).write_text(json.dumps(nativePayload,separators=(',',':'))+'\n')
  sampler=fine.DemSampler(patch,rendered=True);results=[]
  for uid in uids:
   row=cases[uid];p=Polygon(row['rings'][0],row['rings'][1:]);t=sampler.extrema(p);results.append({'uid':uid,'highestRoof':row['highestRenderRoof'],'before':row['currentTerrain'],'after':t,'stillPartial':row['highestRenderRoof']<t['max']-.1})
  patches.append(patch);plans.append({'id':name,'targetUids':uids,'bounds':[x0,z0,x1,z1],'parentCells':[c0,r0,c1,r1],'w':w,'h':h,'gridVertices':w*h,'sourceCovered':int(np.isfinite(native).sum()),'missingSource':int((~np.isfinite(native)).sum()),'boundaryMaximumError':edgeError,'waterNodesChanged':waterChanged,'sources':source,'cases':results});print(name,json.dumps(results),flush=True)
 bundle={'schemaVersion':1,'kind':'nested-source-terrain-refinements','parentTerrainURL':'city/data/terrain-mui-wo.json','parentSha256':sha(baseline),'patches':patches,'integration':'Attach these patches to the existing Mui Wo parent data.patches. Parent elevations and source building fields stay byte-equivalent. Parent-cell bounds use the parent 5 m lattice. Shared renderer must omit these parent cells and render each child exactly once.'}
 (HERE/'terrain-refinements.json').write_text(json.dumps(bundle,separators=(',',':'))+'\n');report={'stagedOnly':True,'refinementSha256':sha(HERE/'terrain-refinements.json'),'bytes':(HERE/'terrain-refinements.json').stat().st_size,'parentSha256':sha(baseline),'patches':plans,'cases':sum(len(p['cases']) for p in plans),'resolvedHighestRoofFlags':sum(not r['stillPartial'] for p in plans for r in p['cases']),'gridVertices':sum(p['gridVertices'] for p in plans),'liveDataChanged':False,'originalSourceFieldsChanged':False,'remainingAcceptance':['Nested renderer integration and actual browser review remain pending.','Neighbour/seam and continuous-route checks are recorded separately; detailed per-roof-face occlusion remains pending.']}
 (DOC/'refinement-staging.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='patches'},indent=2))
if __name__=='__main__':main()
