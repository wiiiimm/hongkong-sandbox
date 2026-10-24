"""Audit and stage non-overlapping native terrain around Tai O hotel components.
Reuses the retained TIN decoder, source piece audit and terrain sampling helpers.
Never edits live terrain or building elevations.
"""
import importlib.util,json,math,pathlib,sys,hashlib
import numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def load(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
shared=module('taio_landmark_shared',HERE.parent/'pui-o-detail-completion/terrain.py')
TARGETS=['landsd/170271:0','landsd/170357:0','landsd/239278:0','landsd/67478:0']
def extent(data):
 g=data['meta']['georef'];x=g['bE']-834500;z=816500-g['bN'];return box(x,z,x+(data['w']-1)*g['aE'],z-(data['h']-1)*g['aN'])
def pieces(p):
 if p.is_empty:return
 if p.geom_type=='Polygon':yield p
 elif hasattr(p,'geoms'):
  for q in p.geoms:yield from pieces(q)
def extrema(poly,parent,children):
 remaining=poly;values=[]
 for child in children:
  region=extent(child);inside=remaining.intersection(region)
  for p in pieces(inside):
   if p.area>1e-9:values.append(shared.fine.DemSampler(child,rendered=True).extrema(p))
  remaining=remaining.difference(region)
 for p in pieces(remaining):
  if p.area>1e-9:values.append(shared.fine.DemSampler(parent,rendered=True).extrema(p))
 return {'min':min(x['min'] for x in values),'max':max(x['max'] for x in values)}
def main():
 parentpath=ROOT/'3d-viewer/city/data/terrain-tai-o.json';parent=load(parentpath);models={m['uid']:m for m in load(HERE/'compact-existing/catalogue.json')['models'] if m['uid'] in TARGETS};buildings={};manifest=load(ROOT/'3d-viewer/city/data/manifest.json')
 for tile in manifest['tiles']:
  if not box(*tile['bounds']).intersects(box(-31610,3710,-31510,3800)):continue
  for b in load(ROOT/'3d-viewer'/tile['url'])['buildings']:
   if b['uid'] in TARGETS:buildings[b['uid']]=b
 assert set(buildings)==set(TARGETS)
 folder=HERE/'staged-existing/9-SW-22B';m,s,tri,valid,usable,tree=shared.terrain_index(folder);children=parent.get('patches',[]);rows=[]
 for uid in TARGETS:
  b=buildings[uid];poly=Polygon(b['rings'][0],b['rings'][1:]);roof=models[uid]['worldBounds'][1][1];native,_,_=shared.shared_audit.source_piece_audit(poly,roof,(usable,tree));current=extrema(poly,parent,children)
  rows.append({'uid':uid,'nativeModelBounds':models[uid]['worldBounds'],'surveyedBase':b.get('baseHeightHKPD'),'surveyedTop':b.get('topHeightHKPD'),'footprintArea':poly.area,'currentRenderedTerrain':current,'nativeTerrain':native,'overlappingExistingChildren':[p['id'] for p in children if extent(p).intersection(poly).area>1e-9],'roofPartlyBelowCurrent':roof<current['max']-.1,'roofPartlyBelowNative':native['areaAboveHighestRoofPlusTolerance']>1e-6})
 report={'stagedOnly':True,'parentTerrainURL':'city/data/terrain-tai-o.json','parentSha256':sha(parentpath),'sourceManifest':str((folder/'manifest.json').relative_to(ROOT)),'sourceManifestSha256':sha(folder/'manifest.json'),'sourceTile':m['tile'],'sourceRevision':m['tileRevision'],'sourceHashes':s['sourceHashes'],'publicationStatus':'held-existing-child-overlap','newPatches':0,'reason':'Both terrain defects intersect existing child refinement-2; adding disjoint sibling patches cannot fix its interior transition. Native source also exceeds outbuilding 239278 highest roof by 0.226m over 6.663 square metres. A reviewed replacement of the existing child is required; no ground or model heights are invented.','existingChildren':[{'id':p['id'],'coarseCells':p['coarseCells'],'bounds':list(extent(p).bounds)} for p in children],'rows':rows}
 save(HERE/'taio-terrain-audit.json',report);print(json.dumps(rows,indent=2))

def build_replacement():
 parentpath=ROOT/'3d-viewer/city/data/terrain-tai-o.json';parent=load(parentpath);g=parent['meta']['georef'];oldchild=next(p for p in parent['patches'] if p['id']=='tai-o-source-refinement-2');oldchildren=parent['patches'];oldarea=extent(oldchild);oldSampler=shared.fine.DemSampler(parent,rendered=True);rawSampler=shared.fine.DemSampler(parent)
 manifest=load(ROOT/'3d-viewer/city/data/manifest.json');live=[];tilehashes=[];models={}
 for cat in manifest['officialModelCatalogues']:
  for m in load(ROOT/'3d-viewer'/cat)['models']:
   b=m['worldBounds']
   if b[0][0]<-31470 and b[1][0]>-31630 and b[0][2]<3820 and b[1][2]>3690:models[m['uid']]=m
 models.update({m['uid']:m for m in load(HERE/'compact-existing/catalogue.json')['models'] if m['uid'] in TARGETS})
 targets=set(TARGETS)|set(oldchild['meta']['targetUids'])
 for t in manifest['tiles']:
  if not box(*t['bounds']).intersects(box(-31630,3690,-31470,3820)):continue
  p=ROOT/'3d-viewer'/t['url'];live.extend(load(p)['buildings']);tilehashes.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p)})
 byuid={b['uid']:b for b in live};assert targets<=set(byuid)
 # Include the original corrected rectangle and complete candidate model bounds,
 # keeping every target away from the ten-metre exterior transition.
 targetareas=[oldarea]+[Polygon(byuid[u]['rings'][0],byuid[u]['rings'][1:]) for u in targets]
 targetareas += [box(m['worldBounds'][0][0],m['worldBounds'][0][2],m['worldBounds'][1][0],m['worldBounds'][1][2]) for u,m in models.items() if u in targets]
 x0,z0,x1,z1=unary_union(targetareas).buffer(20).bounds
 c0=math.floor((x0+834500-g['bE'])/5);c1=math.ceil((x1+834500-g['bE'])/5);r0=math.floor((816500-z0-g['bN'])/-5);r1=math.ceil((816500-z1-g['bN'])/-5)
 x0=g['bE']+c0*5-834500;x1=g['bE']+c1*5-834500;z0=816500-g['bN']+r0*5;z1=816500-g['bN']+r1*5;rect=box(x0,z0,x1,z1)
 assert all(p is oldchild or rect.intersection(extent(p)).area<1e-9 for p in oldchildren),'Replacement intersects unrelated child'
 folder=HERE/'staged-existing/9-SW-22B';m,s,tri,valid,usable,tree=shared.terrain_index(folder);items=[{'usable':usable,'tree':tree}];w=round(x1-x0)+1;h=round(z1-z0)+1;xx,zz=np.meshgrid(np.arange(w)+x0,np.arange(h)+z0);points=np.c_[xx.ravel(),zz.ravel()];native,hits=shared.shared_refine.source_samples(points,items)
 childsamplers=[(extent(p),shared.fine.DemSampler(p,rendered=True)) for p in oldchildren]
 def oldground(x,z):
  from shapely.geometry import Point
  for area,sampler in childsamplers:
   if area.covers(Point(x,z)):return sampler.ground(x,z)
  return oldSampler.ground(x,z)
 elev=[];display=[];vegetation=[];boundary=0;water=0
 for i,(x,z) in enumerate(points):
  col=i%w;row=i//w;previous=oldground(x,z);raw=rawSampler.ground(x,z);weight=min(1,min(col,row,w-1-col,h-1-row)/10)
  if not np.isfinite(native[i]) or raw<=0:weight=0
  y=float(previous+weight*(native[i]-previous)) if weight else previous;display.append(round(y,6));elev.append(round(float(raw if raw<=0 else y),6))
  cc=min(parent['w']-1,max(0,round((x+834500-g['bE'])/5)));rr=min(parent['h']-1,max(0,round((816500-z-g['bN'])/-5)));vegetation.append(parent['vegetation'][rr*parent['w']+cc])
  if raw<=0:water+=1
  if col in (0,w-1) or row in (0,h-1):boundary=max(boundary,abs(y-previous))
 source={'manifest':str((folder/'manifest.json').relative_to(ROOT)),'manifestSha256':sha(folder/'manifest.json'),'tile':m['tile'],'revision':m['tileRevision'],'sourceHashes':s['sourceHashes']}
 oldhash=hashlib.sha256((json.dumps(oldchild,ensure_ascii=False,separators=(',',':'))+'\n').encode()).hexdigest()
 patch={'id':oldchild['id'],'w':w,'h':h,'cell':1,'coarseCells':[c0,r0,c1,r1],'elev':elev,'renderedElev':display,'vegetation':vegetation,'meta':{'title':'Tai O hotel original TIN terrain refinement','georef':{'aE':1,'aN':-1,'bE':x0+834500,'bN':816500-z0,'W':w,'H':h},'targetUids':sorted(targets),'parentTerrain':'city/data/terrain-tai-o.json','parentSha256':sha(parentpath),'replacesChildSha256':oldhash,'transitionMetres':10,'source':{'provider':'Lands Department / HKSAR Government','crs':'EPSG:2326','verticalDatum':'HKPD','nativeSources':[source],'policy':'Native TIN barycentric samples at 1m intervals; ten-metre exterior transition to exact previous rendered terrain. Existing raw water mask retained. Native model/survey elevations untouched. Sample interval is not survey accuracy. Extends the previous child, retaining the original target.'}}}
 replacementSampler=shared.fine.DemSampler(patch,rendered=True);seamPoints=[(x0+i*.5,z) for i in range((w-1)*2+1) for z in [z0,z1]]+[(x,z0+i*.5) for i in range((h-1)*2+1) for x in [x0,x1]]
 boundary=max(abs(replacementSampler.ground(x,z)-oldground(x,z)) for x,z in seamPoints);assert boundary<1e-6,'Stored replacement must preserve original rendered boundary'
 others=[p for p in oldchildren if p is not oldchild];afterchildren=others+[patch];rows=[];regressions=[];estimates=[]
 for b in live:
  poly=Polygon(b['rings'][0],b['rings'][1:])
  if poly.intersection(rect).area<1e-8:continue
  geom=models.get(b['uid']) or b.get('modelGeometry');roof=geom['worldBounds'][1][1] if geom else b['base']+b['height'];bottom=geom['worldBounds'][0][1] if geom else b['base'];before=extrema(poly,parent,oldchildren);after=extrema(poly,parent,afterchildren)
  flags=lambda ground:{'roofWhollyBelowTerrain':roof<ground['min']-.1,'roofPartlyBelowTerrain':roof<ground['max']-.1,'baseWhollyAboveTerrain':bottom>ground['max']+.5}
  oldflags=flags(before);newflags=flags(after)
  row={'uid':b['uid'],'target':b['uid'] in targets,'candidate':b['uid'] in TARGETS,'roof':roof,'modelOrFallbackBase':bottom,'surveyedBase':b.get('baseHeightHKPD'),'surveyedTop':b.get('topHeightHKPD'),'before':before,'after':after,'beforeFlags':oldflags,'afterFlags':newflags}
  if newflags['baseWhollyAboveTerrain'] and not oldflags['baseWhollyAboveTerrain'] and not geom and b.get('baseHeightHKPD') is None and b.get('topHeightHKPD') is None and b.get('heightSource')=='estimated' and b.get('baseSource')=='terrain-estimated':
   estimate=after['min'];row['afterTerrainOnlyFlags']=dict(newflags);row['estimatedBaseAfter']=estimate;newflags={'roofWhollyBelowTerrain':estimate+b['height']<after['min']-.1,'roofPartlyBelowTerrain':estimate+b['height']<after['max']-.1,'baseWhollyAboveTerrain':False};row['afterFlags']=newflags
   estimates.append({'uid':b['uid'],'objectId':b['objectId'],'buildingCSUID':b['buildingCSUID'],'previousBase':b['base'],'base':estimate,'height':b['height'],'baseSource':b['baseSource'],'heightSource':b['heightSource'],'sourceBaseHeightHKPD':None,'sourceTopHeightHKPD':None,'reason':'Existing null-source terrain-estimated base follows corrected terrain minimum. Height remains unchanged; never edit surveyed elevations or native models.'})
  rows.append(row);regressions.extend({'uid':b['uid'],'flag':flag} for flag,value in newflags.items() if value and not oldflags[flag])
 bundle={'schemaVersion':1,'kind':'nested-source-terrain-refinements','parentTerrainURL':'city/data/terrain-tai-o.json','parentSha256':sha(parentpath),'patches':[patch],'integration':'Explicit guarded replacement of child by ID and canonical encoded SHA256. Preserve parent arrays and all other children.'}
 save(HERE/'taio-terrain-original-child.json',oldchild);save(HERE/'taio-terrain-replacement.json',bundle)
 save(HERE/'taio-terrain-estimates.json',{'stagedOnly':True,'parentSha256':sha(parentpath),'refinementSha256':sha(HERE/'taio-terrain-replacement.json'),'buildings':estimates,'policy':'Only with this exact terrain bundle, unchanged UID/objectId/CSUID, unchanged prior base/height, null surveyed elevations and no detailed model; preserve 3m estimated height.'})
 report={'stagedOnly':True,'parentSha256':sha(parentpath),'oldChildId':oldchild['id'],'oldChildSha256':oldhash,'replacementSha256':sha(HERE/'taio-terrain-replacement.json'),'parentCoarseCells':patch['coarseCells'],'bounds':list(rect.bounds),'sampleSpacing':1,'transitionMetres':10,'vertices':w*h,'nativeCoveredNodes':int(np.isfinite(native).sum()),'retainedWaterMaskNodes':water,'maximumBoundaryErrorMetres':boundary,'boundaryChecks':len(seamPoints),'source':[source],'sourceTileHashes':tilehashes,'screenedForms':len(rows),'dependentEstimatedBaseUpdates':len(estimates),'regressions':regressions,'rows':rows,'limits':['Native source terrain has a small corner above outbuilding 239278 roof; retained as source geometry discrepancy, no artificial ground flattening.','Staged only; actual browser check remains required.']}
 save(HERE/'taio-terrain-replacement-audit.json',report);save(HERE/'taio-terrain-replacement-plan.json',{'bundle':str((HERE/'taio-terrain-replacement.json').relative_to(ROOT)),'oldChildId':oldchild['id'],'oldChildSha256':oldhash})
 print(json.dumps({k:v for k,v in report.items() if k not in ('rows','sourceTileHashes','source')},indent=2));print(json.dumps([r for r in rows if r['target']],indent=2));assert not regressions,'Neighbour/source placement regressions need review'

if __name__=='__main__':main();build_replacement()
