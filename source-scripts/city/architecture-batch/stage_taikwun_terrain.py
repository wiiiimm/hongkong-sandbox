"""HKS-208: narrow native-TIN terrain trial for JC Cube and E Hall.
Reuses existing source decoding, barycentric sampling and exact triangle audits.
All output is staged; native building heights and live terrain stay unchanged.
"""
import hashlib,importlib.util,json,math,pathlib,sys
import numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2];TARGETS=['landsd/330467:0','landsd/114964:0']
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False,default=lambda v:v.item())+'\n')
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
shared=module('architecture_taikwun_terrain',H.parent/'landmark-pass/taio_terrain.py');fine=shared.shared.fine
sys.path.insert(0,str(R/'docs/astra-city/mui-wo-buildings/review'))
from prepare_model_sample import model_geometry

def main():
 parentpath=R/'3d-viewer/city/data/terrain-central.json';parent=read(parentpath);g=parent['meta']['georef'];parenthash=sha(parentpath);oldchildren=parent.get('patches',[]);baseline=fine.DemSampler(parent,rendered=True);rawSampler=fine.DemSampler(parent);catalogue=read(H/'compact/catalogue.json');candidates={m['uid']:m for m in catalogue['models']};proofs={r['uid']:r['proof'] for r in read(H/'report.json')['results'] if 'proof' in r}
 assert all(uid in candidates for uid in TARGETS)
 targetareas=[box(m['worldBounds'][0][0],m['worldBounds'][0][2],m['worldBounds'][1][0],m['worldBounds'][1][2]) for uid,m in candidates.items() if uid in TARGETS];x0,z0,x1,z1=unary_union(targetareas).buffer(10).bounds
 c0=math.floor((x0+834500-g['bE'])/5);c1=math.ceil((x1+834500-g['bE'])/5);r0=math.floor((816500-z0-g['bN'])/-5);r1=math.ceil((816500-z1-g['bN'])/-5)
 assert 0<=c0<c1<parent['w'] and 0<=r0<r1<parent['h']
 x0=g['bE']+c0*5-834500;x1=g['bE']+c1*5-834500;z0=816500-g['bN']+r0*5;z1=816500-g['bN']+r1*5;rect=box(x0,z0,x1,z1)
 assert all(rect.intersection(shared.extent(p)).area<1e-9 for p in oldchildren),'Existing refinement overlaps this candidate'
 folders={(R/proofs[uid]['sourceManifest']).parent for uid in TARGETS};items=[];sources=[]
 for folder in sorted(folders):
  m,s,t,v,usable,tree=shared.shared.terrain_index(folder);items.append({'usable':usable,'tree':tree});sources.append({'manifest':str((folder/'manifest.json').relative_to(R)),'manifestSha256':sha(folder/'manifest.json'),'tile':m['tile'],'revision':m['tileRevision'],'sourceHashes':s['sourceHashes']})
 step=.25;w=round((x1-x0)/step)+1;h=round((z1-z0)/step)+1;xx,zz=np.meshgrid(np.arange(w)*step+x0,np.arange(h)*step+z0);points=np.c_[xx.ravel(),zz.ravel()];native,hits=shared.shared.shared_refine.source_samples(points,items);elev=[];display=[];vegetation=[];water=0
 for i,(x,z) in enumerate(points):
  col=i%w;row=i//w;previous=baseline.ground(x,z);raw=rawSampler.ground(x,z);weight=min(1,min(col,row,w-1-col,h-1-row)*step/5)
  if not np.isfinite(native[i]) or raw<=0:weight=0
  y=float(previous+weight*(native[i]-previous)) if weight else previous;display.append(round(y,6));elev.append(round(float(raw if raw<=0 else y),6));cc=min(parent['w']-1,max(0,round((x+834500-g['bE'])/5)));rr=min(parent['h']-1,max(0,round((816500-z-g['bN'])/-5)));vegetation.append(parent['vegetation'][rr*parent['w']+cc]);water+=raw<=0
 patch={'id':'tai-kwun-jc-cube-e-hall-source-refinement','w':w,'h':h,'cell':step,'elev':elev,'renderedElev':display,'vegetation':vegetation,'coarseCells':[c0,r0,c1,r1],'meta':{'title':'Tai Kwun JC Cube and E Hall native TIN terrain','georef':{'aE':step,'aN':-step,'bE':x0+834500,'bN':816500-z0,'W':w,'H':h},'targetUids':TARGETS,'parentTerrain':'city/data/terrain-central.json','parentSha256':parenthash,'transitionMetres':5,'source':{'provider':'Lands Department / HKSAR Government','crs':'EPSG:2326','verticalDatum':'HKPD','nativeSources':sources,'policy':'Original cached TIN sampled barycentrically at 0.25 m intervals. Five-metre exterior display transition joins exact unchanged 5 m parent terrain; existing raw water mask retained. No building vertices, surveyed heights or offsets modified. Sample spacing is not survey accuracy.'}}}
 newSampler=fine.DemSampler(patch,rendered=True);seams=[(x0+i*.5,z)for i in range(round((x1-x0)*2)+1)for z in(z0,z1)]+[(x,z0+i*.5)for i in range(round((z1-z0)*2)+1)for x in(x0,x1)];seamerror=max(abs(newSampler.ground(x,z)-baseline.ground(x,z))for x,z in seams);assert seamerror<1e-6
 manifest=read(R/'3d-viewer/city/data/manifest.json');live=[];tilehashes=[];models={}
 for t in manifest['tiles']:
  if rect.intersects(box(*t['bounds'])):
   p=R/'3d-viewer'/t['url'];live.extend(read(p)['buildings']);tilehashes.append({'path':str(p.relative_to(R)),'sha256':sha(p)})
 for cat in manifest['officialModelCatalogues']:
  for m in read(R/'3d-viewer'/cat)['models']:
   bounds=m['worldBounds']
   if rect.intersects(box(bounds[0][0],bounds[0][2],bounds[1][0],bounds[1][2])):models[m['uid']]=m
 models.update(candidates);rows=[];regressions=[];targetRows=[]
 for b in live:
  poly=Polygon(b['rings'][0],b['rings'][1:])
  if poly.intersection(rect).area<1e-9:continue
  geom=models.get(b['uid']) or b.get('modelGeometry');roof=geom['worldBounds'][1][1] if geom else b['base']+b['height'];bottom=geom['worldBounds'][0][1] if geom else b['base'];before=shared.extrema(poly,parent,oldchildren);after=shared.extrema(poly,parent,oldchildren+[patch]);flags=lambda d:{'roofWhollyBelowTerrain':roof<d['min']-.1,'roofPartlyBelowTerrain':roof<d['max']-.1,'baseWhollyAboveTerrain':bottom>d['max']+.5};oldFlags=flags(before);newFlags=flags(after)
  row={'uid':b['uid'],'label':b.get('name'),'target':b['uid'] in TARGETS,'candidate':b['uid'] in candidates,'detailedGeometry':bool(geom),'sourceBaseTop':[b.get('baseHeightHKPD'),b.get('topHeightHKPD')],'modelOrFallbackBase':bottom,'roof':roof,'before':before,'after':after,'beforeFlags':oldFlags,'afterFlags':newFlags};rows.append(row);regressions.extend({'uid':b['uid'],'flag':k}for k,v in newFlags.items() if v and not oldFlags[k])
  if b['uid'] in TARGETS:
   model=candidates[b['uid']];folder=(R/proofs[b['uid']]['sourceManifest']).parent;sm=read(folder/'manifest.json');spec=next(s for s in sm['models'] if s['id']==model['modelId']);p=folder/spec['sourceEntry'];positions,_=model_geometry(read(p),lambda u:(p.parent/u).read_bytes());vertices=np.unique(positions,axis=0);near=vertices[:,1]<=vertices[:,1].min()+.5;bottomv=vertices[near];beforeClear=np.array([y-baseline.ground(x,z)for x,y,z in bottomv]);afterClear=np.array([y-newSampler.ground(x,z)for x,y,z in bottomv]);nat,_=shared.shared.shared_refine.source_samples(bottomv[:,[0,2]],items);row['bottomVertexReview']={'vertices':len(bottomv),'beforeClearanceQuantiles':np.quantile(beforeClear,[0,.25,.5,.75,1]).tolist(),'afterClearanceQuantiles':np.quantile(afterClear,[0,.25,.5,.75,1]).tolist(),'nativeClearanceQuantiles':np.quantile(bottomv[:,1]-nat,[0,.25,.5,.75,1]).tolist()};targetRows.append(row)
 bundle={'schemaVersion':1,'kind':'nested-source-terrain-refinements','parentTerrainURL':'city/data/terrain-central.json','parentSha256':parenthash,'patches':[patch],'integration':'Append to parent.patches through shared guarded publisher; preserve parent arrays and existing children. Browser acceptance required.'};save(H/'taikwun-terrain-refinements.json',bundle)
 report={'issue':'HKS-208','stagedOnly':True,'parentSha256':parenthash,'refinementSha256':sha(H/'taikwun-terrain-refinements.json'),'source':sources,'coarseCells':patch['coarseCells'],'bounds':list(rect.bounds),'vertices':w*h,'sourceCoveredVertices':int(np.isfinite(native).sum()),'preservedWaterNodes':int(water),'boundaryChecks':len(seams),'maximumBoundaryErrorMetres':seamerror,'sourceTileHashes':tilehashes,'screenedForms':len(rows),'regressions':regressions,'targets':targetRows,'rows':rows,'limits':['Terrain trial only; current renderer/browser must verify exposed wall and foundation appearance.','Source surveyed/model heights stay unchanged at 1x. No buildings receive estimated base shifts in this proposal.']};save(H/'taikwun-terrain-review.json',report)
 print(json.dumps({k:v for k,v in report.items() if k not in ('rows','sourceTileHashes','source')},indent=2,default=lambda v:v.item()));assert sha(parentpath)==parenthash,'Live parent changed during audit';assert not regressions,'Neighbour regressions require resolution before publication'
if __name__=='__main__':main()
