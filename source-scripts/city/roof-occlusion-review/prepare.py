"""Prepare bounded native-TIN candidates using established sampler/transition helpers."""
import math
from audit import *
from shapely.geometry import box

def main():
 audit=read(D/'audit.json');rootpath=R/'3d-viewer/city/data/terrain.json';root=read(rootpath);g=root['meta']['georef'];manifest=read(R/'3d-viewer/city/data/manifest.json');children=[read(R/'3d-viewer'/x['url'])for x in manifest['terrainPatches']];old=shared.shared.fine.DemSampler(root,rendered=True);raw=shared.shared.fine.DemSampler(root);patches=[];reports=[]
 for case in audit['rows']:
  uid=case['uid'];p=Polygon(case['buildingRecord']['rings'][0]);x0,z0,x1,z1=p.buffer(20).bounds;c0=math.floor((x0+834500-g['bE'])/70);c1=math.ceil((x1+834500-g['bE'])/70);r0=math.floor((816500-z0-g['bN'])/-70);r1=math.ceil((816500-z1-g['bN'])/-70);x0=g['bE']+c0*70-834500;x1=g['bE']+c1*70-834500;z0=816500-g['bN']+r0*70;z1=816500-g['bN']+r1*70;extent=box(x0,z0,x1,z1)
  assert all(extent.intersection(shared.extent(c)).area<1e-9 for c in children),'Existing patch overlap requires a reviewed replacement'
  folder=(R/case['terrainManifest']).parent;_,spec,_,_,usable,tree=shared.shared.terrain_index(folder);w=round(x1-x0)+1;h=round(z1-z0)+1;xx,zz=np.meshgrid(np.arange(w)+x0,np.arange(h)+z0);points=np.c_[xx.ravel(),zz.ravel()];native,hits=shared.shared.shared_refine.source_samples(points,[{'usable':usable,'tree':tree}]);elev=[];display=[];vegetation=[];boundary=0
  for i,(x,z)in enumerate(points):
   row=i//w;col=i%w;previous=old.ground(x,z);before=raw.ground(x,z);weight=min(1,min(row,col,w-1-col,h-1-row)/10)
   if not np.isfinite(native[i]) or before<=0:weight=0
   value=float(previous+(native[i]-previous)*weight)if weight else previous;display.append(round(value,6));elev.append(round(before if before<=0 else value,6));cc=min(root['w']-1,max(0,round((x+834500-g['bE'])/70)));rr=min(root['h']-1,max(0,round((816500-z-g['bN'])/-70)));vegetation.append(root['vegetation'][rr*root['w']+cc])
   if row in(0,h-1)or col in(0,w-1):boundary=max(boundary,abs(value-previous))
  patch={'id':'roof-review-'+uid.split('/')[1].replace(':','-'),'w':w,'h':h,'cell':1,'elev':elev,'renderedElev':display,'vegetation':vegetation,'coarseCells':[c0,r0,c1,r1],'meta':{'title':case['name']+' · staged native TIN','georef':{'aE':1,'aN':-1,'bE':x0+834500,'bN':816500-z0,'W':w,'H':h},'targetUids':[uid],'parentTerrain':'city/data/terrain.json','parentSha256':sha(rootpath),'transitionMetres':10,'source':{'provider':'Lands Department / HKSAR Government','crs':'EPSG:2326','verticalDatum':'HKPD','manifest':case['terrainManifest'],'manifestSha256':case['terrainManifestSha256'],'sourceHashes':case['terrainSourceHashes'],'policy':'Exact retained native TIN barycentric samples at 1m intervals; interval is not surveyed accuracy. 10m outer display transition to existing parent triangles; absent source and existing water retain prior terrain. Model elevations unchanged.'}}}
  path=H/(patch['id']+'.json');path.write_text(json.dumps(patch,separators=(',',':'),allow_nan=False)+'\n');new=shared.shared.fine.DemSampler(patch,rendered=True);neighbours=[];regressions=[]
  for tile in manifest['tiles']:
   if not extent.intersects(box(*tile['bounds'])):continue
   for b in read(R/'3d-viewer'/tile['url'])['buildings']:
    poly=Polygon(b['rings'][0],b['rings'][1:]);clip=poly.intersection(extent)
    if clip.area<1e-9:continue
    before=shared.extrema(poly,root,children);after=shared.extrema(poly,root,children+[patch]);roof=b['base']+b['height'];flags=lambda t:{'roofWhollyBelow':roof<t['min']-.1,'roofPartlyBelow':roof<t['max']-.1,'baseWhollyAbove':b['base']>t['max']+.5};a,bf=flags(before),flags(after);row={'uid':b['uid'],'name':b['name'],'recordedBase':b['base'],'recordedRoof':roof,'before':before,'after':after,'newFlags':[key for key in bf if bf[key]and not a[key]]};neighbours.append(row)
    if row['newFlags']:regressions.append(row)
  after=new.extrema(p);roof=case['modelBounds'][1][1];reports.append({'uid':uid,'candidate':str(path.relative_to(R)),'sha256':sha(path),'bytes':path.stat().st_size,'gridVertices':w*h,'bounds':[x0,z0,x1,z1],'sourceCoveredNodes':int(np.isfinite(native).sum()),'missingSourceNodes':int((~np.isfinite(native)).sum()),'boundaryMaximumErrorMetres':boundary,'targetBefore':case['currentRenderedTerrain'],'targetAfter':after,'targetNativeRoof':roof,'highestRoofFlagResolved':roof>=after['max']-.1,'neighbours':neighbours,'regressions':regressions,'outcome':'hold-neighbour-context'if regressions else'candidate-awaiting-browser-review','published':False});patches.append(patch);print(uid,reports[-1]['outcome'],after,'neighbours',len(neighbours),flush=True)
 save(D/'patch-review.json',{'issue':'HKS-214','published':False,'verticalScale':1,'parentSha256':sha(rootpath),'rows':reports,'qualification':'Full candidate-extent footprint checks use basic source base/roof envelopes; new flags need model/support context before acceptance.'})
if __name__=='__main__':main()
