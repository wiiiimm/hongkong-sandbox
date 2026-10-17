"""Narrow original-TIN terrain corrections for two verified Tai O source models.
Reuse the existing exact triangle extrema and source decoder; no live publication.
"""
import collections,gzip,importlib.util,json,math,sys
import numpy as np
import shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from audit import HERE,ROOT,OLD,DOC,dump,sha
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from resample_model_terrain import terrain_index
spec=importlib.util.spec_from_file_location('shared_fine_terrain',HERE.parent/'mui-wo-buildings/fine_terrain_audit.py');fine=importlib.util.module_from_spec(spec);spec.loader.exec_module(fine)
TARGETS=[['landsd/14899:0'],['landsd/211618:0']]

def polys(g):
 if g.is_empty:return
 if g.geom_type=='Polygon':yield g
 elif hasattr(g,'geoms'):
  for child in g.geoms:yield from polys(child)

def source_samples(points,items):
 # Same barycentric/max-of-covered-triangles policy as existing Mui Wo refinements.
 result=np.full(len(points),-np.inf)
 for item in items:
  triangles,tree=item['usable'],item['tree'];pi,ti=tree.query(shapely.points(points),predicate='covered_by');tri=triangles[ti]
  a=tri[:,0,:];v0=tri[:,1,:][:,[0,2]]-a[:,[0,2]];v1=tri[:,2,:][:,[0,2]]-a[:,[0,2]];q=points[pi]-a[:,[0,2]];den=v0[:,0]*v1[:,1]-v0[:,1]*v1[:,0]
  u=(q[:,0]*v1[:,1]-q[:,1]*v1[:,0])/den;v=(v0[:,0]*q[:,1]-v0[:,1]*q[:,0])/den;y=a[:,1]+u*(tri[:,1,1]-a[:,1])+v*(tri[:,2,1]-a[:,1]);np.maximum.at(result,pi,y)
 return result

def read(p):return json.loads(p.read_text())
def main():
 parentPath=ROOT/'3d-viewer/city/data/terrain-tai-o.json';parent=read(parentPath);g=parent['meta']['georef'];baseline=fine.DemSampler(parent,rendered=True);rawParent=fine.DemSampler(parent);manifest=read(ROOT/'3d-viewer/city/data/manifest.json');base=read(ROOT/'3d-viewer/city/data/terrain.json');hydro=base.get('hydro',{});water=unary_union([Polygon(w['rings'][0],w['rings'][1:]) for w in hydro.get('water',[])])
 catalogue=read(HERE/'compact/catalogue.json');newModels={m['uid']:m for m in catalogue['models']};selection={b['uid']:b for b in json.loads(gzip.decompress((OLD/'building-selection.json.gz').read_bytes()))['buildings']};patches=[];plans=[]
 folders=[*sorted((OLD/'staged').iterdir()),*sorted((HERE/'staged').iterdir())]
 for i,uids in enumerate(TARGETS):
  area=unary_union([Polygon(selection[u]['rings'][0],selection[u]['rings'][1:]) for u in uids]);x0,z0,x1,z1=area.buffer(20).bounds
  c0=math.floor((x0+834500-g['bE'])/5);c1=math.ceil((x1+834500-g['bE'])/5);r0=math.floor((816500-z0-g['bN'])/-5);r1=math.ceil((816500-z1-g['bN'])/-5)
  x0=g['bE']+c0*5-834500;x1=g['bE']+c1*5-834500;z0=816500-g['bN']+r0*5;z1=816500-g['bN']+r1*5;rect=box(x0,z0,x1,z1);assert 0<=c0<c1<parent['w'] and 0<=r0<r1<parent['h'];assert rect.intersection(water).area==0,'Correction must not alter mapped water';items=[]
  for folder in folders:
   m=read(folder/'manifest.json');b=m['terrain']['worldBounds']
   if not rect.intersects(box(b[0][0],b[0][2],b[1][0],b[1][2])):continue
   m,s,_,_,usable,tree=terrain_index(folder);items.append({'usable':usable,'tree':tree,'manifest':str((folder/'manifest.json').relative_to(ROOT)),'tile':m['tile'],'revision':m['tileRevision'],'sourceHashes':s['sourceHashes']})
  w=round(x1-x0)+1;h=round(z1-z0)+1;xx,zz=np.meshgrid(np.arange(w)+x0,np.arange(h)+z0);points=np.c_[xx.ravel(),zz.ravel()];native=source_samples(points,items);elev=[];vegetation=[];zeroMask=0;blend=[]
  for k,(x,z) in enumerate(points):
   c=k%w;r=k//w;old=baseline.ground(x,z);raw=rawParent.ground(x,z);alpha=min(1,min(c,r,w-1-c,h-1-r)/10)
   if raw<=0 or not np.isfinite(native[k]):alpha=0;zeroMask+=1
   value=old+alpha*(native[k]-old) if alpha else old;elev.append(round(float(value),6));blend.append(alpha)
   cc=min(parent['w']-1,max(0,round((x+834500-g['bE'])/5)));rr=min(parent['h']-1,max(0,round((816500-z-g['bN'])/-5)));vegetation.append(parent['vegetation'][rr*parent['w']+cc])
  id='tai-o-source-refinement-'+str(i+1);source=[{k:v for k,v in item.items() if k not in ('usable','tree')} for item in items]
  patch={'id':id,'w':w,'h':h,'cell':1,'elev':elev,'vegetation':vegetation,'coarseCells':[c0,r0,c1,r1],'meta':{'title':'Tai O original TIN ground correction','georef':{'aE':1,'aN':-1,'bE':x0+834500,'bN':816500-z0,'W':w,'H':h},'parentTerrain':'city/data/terrain-tai-o.json','parentSha256':sha(parentPath.read_bytes()),'transitionMetres':10,'targetUids':uids,'source':{'provider':'Lands Department / HKSAR Government','crs':'EPSG:2326','verticalDatum':'HKPD','nativeSources':source,'policy':'Original TIN barycentric samples at 1 m spacing; 10 m exterior transition to exact parent rendered terrain. Native model elevations unchanged. Sample interval does not imply survey accuracy.'}}}
  patches.append(patch);dump(HERE/'source-grids'/(id+'.json'),{'w':w,'h':h,'meta':{'georef':patch['meta']['georef']},'elev':[float(v) if np.isfinite(v) else None for v in native],'source':source,'blendWeights':blend,'method':'Original source TIN values before outer display transition.'});plans.append({'id':id,'targetUids':uids,'bounds':[x0,z0,x1,z1],'parentCells':patch['coarseCells'],'w':w,'h':h,'vertices':w*h,'sourceCoveredNodes':int(np.isfinite(native).sum()),'maskedSourceMissingOrExistingWater':zeroMask,'mappedWaterIntersectionArea':rect.intersection(water).area,'source':source})
 bundle={'schemaVersion':1,'kind':'nested-source-terrain-refinements','parentTerrainURL':'city/data/terrain-tai-o.json','parentSha256':sha(parentPath.read_bytes()),'patches':patches,'integration':'Attach children to existing Tai O parent.patches. coarseCells indexes parent5m lattice; omit parent cells and render children once. Preserve parent arrays, source building fields and existing base hydro.'}
 (HERE/'terrain-refinements.json').write_text(json.dumps(bundle,separators=(',',':'))+'\n')
 children=[];seams=0;edgeError=0
 for p,plan in zip(patches,plans):
  rect=box(*plan['bounds']);s=fine.DemSampler(p,rendered=True);children.append((rect,s,p));x0,z0,x1,z1=plan['bounds']
  for x,z in [(x0+i*.5,z) for i in range((p['w']-1)*2+1) for z in [z0,z1]]+[(x,z0+i*.5) for i in range((p['h']-1)*2+1) for x in [x0,x1]]:
   error=abs(s.ground(x,z)-baseline.ground(x,z));edgeError=max(edgeError,error);seams+=1;assert error<1e-6
 union=unary_union([r for r,s,p in children]);assert sum(r.area for r,s,p in children)==union.area
 def extrema(p):
  values=[]
  for rect,s,patch in children:
   for q in polys(rect.intersection(p)):values.append(s.extrema(q))
  for q in polys(p.difference(union)):values.append(baseline.extrema(q))
  return {'min':min(v['min'] for v in values),'max':max(v['max'] for v in values)}
 live=[];liveHashes=[]
 for tile in manifest['tiles']:
  if not box(*tile['bounds']).intersects(union):continue
  path=ROOT/'3d-viewer'/tile['url'];data=read(path);liveHashes.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())});live.extend(data['buildings'])
 rows=[];estimates=[]
 for b in live:
  p=Polygon(b['rings'][0],b['rings'][1:])
  if not p.intersects(union) and b['uid'] not in newModels:continue
  geom=newModels.get(b['uid']) or b.get('modelGeometry');top=geom['worldBounds'][1][1] if geom else b['base']+b['height'];bottom=geom['worldBounds'][0][1] if geom else b['base'];before=baseline.extrema(p);after=extrema(p)
  flags=lambda t:{'roofWhollyBelowTerrain':top<t['min']-.1,'roofPartlyBelowTerrain':top<t['max']-.1,'baseWhollyAboveTerrain':bottom>t['max']+.5}
  oldFlags=flags(before);newFlags=flags(after);row={'uid':b['uid'],'candidateNewModel':b['uid'] in newModels,'modelId':geom.get('modelId') if geom else None,'highestRoof':top,'modelOrFallbackBase':bottom,'sourceBase':b.get('baseHeightHKPD'),'sourceTop':b.get('topHeightHKPD'),'before':before,'after':after,'beforeFlags':oldFlags,'afterTerrainOnlyFlags':newFlags,'afterFlags':dict(newFlags),'previousTerrainAudit':b.get('terrainAudit')}
  if newFlags['baseWhollyAboveTerrain'] and not oldFlags['baseWhollyAboveTerrain'] and not geom and b.get('baseHeightHKPD') is None and b.get('topHeightHKPD') is None and b.get('heightSource')=='estimated' and b.get('baseSource')=='terrain-estimated':
   baseEstimate=after['min'];newTop=baseEstimate+b['height'];newFlags={'roofWhollyBelowTerrain':newTop<after['min']-.1,'roofPartlyBelowTerrain':newTop<after['max']-.1,'baseWhollyAboveTerrain':False};row['afterFlags']=newFlags;row['estimatedBaseAfter']=baseEstimate;estimates.append({'uid':b['uid'],'objectId':b['objectId'],'buildingCSUID':b['buildingCSUID'],'tile':b['tile'],'previousBase':b['base'],'base':baseEstimate,'height':b['height'],'baseSource':b['baseSource'],'heightSource':b['heightSource'],'sourceBaseHeightHKPD':None,'sourceTopHeightHKPD':None,'reason':'Derived null-source estimated base follows corrected ground minimum; never modify recorded source elevations.'})
  rows.append(row)
 regressions=[{'uid':r['uid'],'flag':k} for r in rows for k,v in r['afterFlags'].items() if v and not r['beforeFlags'][k]]
 dump(HERE/'building-estimate-updates.json',{'stagedOnly':True,'parentSha256':bundle['parentSha256'],'refinementSha256':sha((HERE/'terrain-refinements.json').read_bytes()),'buildings':estimates,'policy':'Apply only with terrain and UID/previousbase/nullsource/no detailedmodel guards; preserve footprint, original elevations and fallback height.'})
 dump(HERE/'diagnostic-updates.json',{'stagedOnly':True,'parentSha256':bundle['parentSha256'],'byBuildingUid':{r['uid']:r['afterFlags'] for r in rows if r['previousTerrainAudit']!=r['afterFlags']},'policy':'Derived terrainAudit flags only after corresponding terrain and model publication.'})
 report={'stagedOnly':True,'bytes':(HERE/'terrain-refinements.json').stat().st_size,'refinementSha256':sha((HERE/'terrain-refinements.json').read_bytes()),'parentSha256':bundle['parentSha256'],'baseHydroSha256':sha(json.dumps(hydro,sort_keys=True,separators=(',',':')).encode()),'patches':plans,'boundaryChecks':seams,'maximumBoundaryErrorMetres':edgeError,'sourceTileHashes':liveHashes,'screenedForms':len(rows),'dependentEstimatedBaseUpdates':len(estimates),'regressions':regressions,'rows':rows,'limits':['Staged nested grids; actual nested renderer and browser acceptance remains with root.','Source building elevations untouched. Highest-roof extrema diagnostics are not per-roof-face architecture acceptance.']};dump(DOC/'terrain-integration-candidate.json',report)
 print(json.dumps({k:v for k,v in report.items() if k not in ('rows','patches','sourceTileHashes')},indent=2));print(json.dumps([{k:v for k,v in r.items() if k not in ('previousTerrainAudit',)} for r in rows if r['candidateNewModel']],indent=2));assert not regressions,'Source/estimated foundation regressions require resolution before handoff'
if __name__=='__main__':main()
