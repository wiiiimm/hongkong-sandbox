"""Cache-only Opus/Peak terrain candidates via established 5m DTM/TIN tooling.
No live assets, surveyed elevations or building geometry are edited.
"""
import hashlib,importlib.util,json,math,pathlib,sys,time
import numpy as np
from pyproj import Transformer
from shapely.geometry import Polygon,box
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2];B=H.parent/'architecture-batch';DOC=R/'docs/astra-city/architecture-followup'
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,allow_nan=False,default=lambda x:x.item())+'\n')
shared=module('followup_shared_terrain',H.parent/'landmark-pass/taio_terrain.py');builder=module('followup_shared_dtm',H.parent/'terrain-detail/build.py')
sys.path.insert(0,str(H.parent/'mui-wo-models'));from terrain_mosaic import blend_sources
sys.path.insert(0,str(R/'docs/astra-city/mui-wo-buildings/review'));from prepare_model_sample import model_geometry

def main():
 began=time.monotonic();manifest=read(R/'3d-viewer/city/data/manifest.json');rootpath=R/'3d-viewer/city/data/terrain.json';root=read(rootpath);rootsha=sha(rootpath);g=root['meta']['georef'];base=shared.shared.fine.DemSampler(root,rendered=True);children=[read(R/'3d-viewer'/p['url'])for p in manifest['terrainPatches']];candidates={m['uid']:m for m in read(B/'compact/catalogue.json')['models']};proofs={r['uid']:r['proof']for r in read(B/'report.json')['results']if r.get('proof')};records=read(H/'input-records.json');inventory=records['nearbyRecords'];project=Transformer.from_crs(2326,4326,always_xy=True);summaries=[]
 for uid,label in [('landsd/322573:0','opus'),('landsd/248218:0','peak-tower')]:
  model=candidates[uid];bounds=model['worldBounds'];west,south=project.transform(bounds[0][0]+834500-20,816500-bounds[1][2]-20);east,north=project.transform(bounds[1][0]+834500+20,816500-bounds[0][2]+20);path=H/'terrain'/('terrain-'+label+'.json');evidence=H/'terrain'/label;evidence.mkdir(parents=True,exist_ok=True)
  patch,_=builder.build_patch(bbox=[west,south,east,north],output=path,detail_paths=[],evidence=evidence,area=label,rendered_transition=True)
  # Peak lies just outside the south boundary of the current Central patch.
  # Trim its candidate to that shared root-cell boundary, never overlay two patches.
  for old in children:
   a,b,c,d=old['coarseCells'];x0,z0,x1,z1=patch['coarseCells']
   if x1<=a or x0>=c or z1<=b or z0>=d:continue
   assert old['meta']['title'].startswith('Central') or old['coarseCells']==[468,434,516,473],'Unexpected patch overlap'
   assert z0<d<z1 and bounds[0][2]>816500-g['bN']+d*70,'Cannot trim without losing the target'
   trim=(d-z0)*14;w=patch['w'];patch['h']-=trim;patch['coarseCells'][1]=d;patch['meta']['georef']['bN']-=trim*5;patch['meta']['georef']['H']=patch['h']
   for key in ('elev','vegetation','renderedElev'):
    if key in patch:patch[key]=patch[key][trim*w:]
  pg=patch['meta']['georef'];pw=patch['w'];ph=patch['h'];sourceFolder=(R/proofs[uid]['sourceManifest']).parent;sourceManifest=read(sourceFolder/'manifest.json');nativeSource=None
  if sourceManifest.get('terrain'):
   sm,ss,t,v,usable,tree=shared.shared.terrain_index(sourceFolder);world=ss['worldBounds'];cc0=max(0,math.ceil((world[0][0]+834500-pg['bE'])/5));cc1=min(pw-1,math.floor((world[1][0]+834500-pg['bE'])/5));rr0=max(0,math.ceil((816500-world[0][2]-pg['bN'])/-5));rr1=min(ph-1,math.floor((816500-world[1][2]-pg['bN'])/-5));w=cc1-cc0+1;h=rr1-rr0+1;xx,zz=np.meshgrid(pg['bE']+np.arange(cc0,cc1+1)*5-834500,816500-pg['bN']+np.arange(rr0,rr1+1)*5);points=np.c_[xx.ravel(),zz.ravel()];values,_=shared.shared.shared_refine.source_samples(points,[{'usable':usable,'tree':tree}]);nativeSource={'provider':'Lands Department / HKSAR Government','tile':sm['tile'],'tileRevision':sm['tileRevision'],'manifest':str((sourceFolder/'manifest.json').relative_to(R)),'manifestSha256':sha(sourceFolder/'manifest.json'),'sourceHashes':ss['sourceHashes'],'crs':'EPSG:2326','verticalDatum':'HKPD'};gridpath=evidence/'native-grid.json';save(gridpath,{'w':w,'h':h,'elev':[float(v)if np.isfinite(v)else None for v in values],'meta':{'georef':{'aE':5,'aN':-5,'bE':pg['bE']+cc0*5,'bN':pg['bN']-rr0*5}},'source':nativeSource});fine=np.array(patch['elev']).reshape(ph,pw);sources,mosaic=blend_sources(fine,pg['bE'],pg['bN'],[gridpath],R);patch['elev']=np.round(fine,6).ravel().tolist();patch['meta']['detailSources']=sources;save(evidence/'terrain-mosaic.json',mosaic)
  # Rebuild exact rendered transition after trim/source blend; surveyed/raw values
  # are retained separately and the outer boundary always equals original root.
  display=[None]*(pw*ph)
  for row in range(ph):
   for col in range(pw):
    weight=min(1,min(row,col,pw-1-col,ph-1-row)/14)
    if weight==1:continue
    x=pg['bE']+col*5-834500;z=816500-pg['bN']+row*5;e=patch['elev'][row*pw+col];current=max(1.2,e)if e>0 else-4;display[row*pw+col]=round(base.ground(x,z)*(1-weight)+current*weight,6)
  patch['renderedElev']=display;patch['meta']['parentSha256']=rootsha;patch['meta']['sourceProcessing']='Existing DTM builder; optional retained native-TIN mosaic; disjoint root-cell trim and rendered transition only. No building adjustments.';save(path,patch);new=shared.shared.fine.DemSampler(patch,rendered=True);extent=shared.extent(patch);existing=[c for c in children if extent.intersection(shared.extent(c)).area>1e-9];assert not existing,'Candidate overlaps an existing top-level patch'
  rows=[];regressions=[];estimates=[]
  for b in inventory.values():
   rings=json.loads(b['rings_json']);poly=Polygon(rings[0],rings[1:])
   if poly.intersection(extent).area<1e-9:continue
   geom=candidates.get(b['uid']);roof=geom['worldBounds'][1][1]if geom else b['base']+b['height'];bottom=geom['worldBounds'][0][1]if geom else b['base'];before=shared.extrema(poly,root,children);after=shared.extrema(poly,root,children+[patch]);flags=lambda d:{'roofWhollyBelowTerrain':bool(roof<d['min']-.1),'roofPartlyBelowTerrain':bool(roof<d['max']-.1),'baseWhollyAboveTerrain':bool(bottom>d['max']+.5)};oldflags=flags(before);newflags=flags(after);row={'uid':b['uid'],'label':b['name'],'target':b['uid']==uid,'sourceBaseTop':[b['source_base'],b['source_top']],'base':bottom,'roof':roof,'before':before,'after':after,'beforeFlags':oldflags,'afterFlags':newflags};rows.append(row);regressions.extend({'uid':b['uid'],'flag':k}for k,v in newflags.items()if v and not oldflags[k])
  p=sourceFolder/next(s['sourceEntry']for s in sourceManifest['models']if s['id']==model['modelId']);vertices,_=model_geometry(read(p),lambda u:(p.parent/u).read_bytes());vertices=np.unique(vertices,axis=0);bottomv=vertices[vertices[:,1]<=vertices[:,1].min()+.5];beforeClear=np.array([y-base.ground(x,z)for x,y,z in bottomv]);afterClear=np.array([y-new.ground(x,z)for x,y,z in bottomv]);target=next(row for row in rows if row['uid']==uid);target['bottomVertexClearance']={'vertices':len(bottomv),'before':np.quantile(beforeClear,[0,.25,.5,.75,1]).tolist(),'after':np.quantile(afterClear,[0,.25,.5,.75,1]).tolist()}
  seamPoints=[(pg['bE']-834500+c*5,816500-pg['bN']+r*5)for c in range(pw)for r in (0,ph-1)]+[(pg['bE']-834500+c*5,816500-pg['bN']+r*5)for r in range(ph)for c in(0,pw-1)];error=max(abs(new.ground(x,z)-base.ground(x,z))for x,z in seamPoints);assert error<1e-5
  report={'uid':uid,'stagedOnly':True,'networkBytes':0,'aiCalls':0,'candidate':str(path.relative_to(R)),'candidateSha256':sha(path),'rootTerrainSha256':rootsha,'nativeSource':nativeSource,'dtmSource':patch['meta']['source'],'coarseCells':patch['coarseCells'],'gridVertices':pw*ph,'triangles':2*(pw-1)*(ph-1),'sampleSpacingMetres':5,'maximumBoundaryErrorMetres':error,'candidateBytes':path.stat().st_size,'target':target,'neighbourRows':rows,'regressions':regressions,'outcome':'held-neighbour-regression'if regressions else'held-full-patch-and-browser-review','limits':['Five-metre terrain sampling may still omit steep retaining edges and substructures.','Neighbour audit currently covers retained120m neighbourhood records; whole patch coverage must be checked before publication.','No live integration or source/model height changes.']};save(evidence/'review.json',report);summaries.append(report);print(uid,report['outcome'],target['bottomVertexClearance'],flush=True)
 save(H/'terrain-report.json',{'issue':'HKS-209','stagedOnly':True,'networkRequests':0,'networkBytes':0,'aiCalls':0,'scriptSeconds':round(time.monotonic()-began,3),'rows':summaries});save(DOC/'terrain-report.json',read(H/'terrain-report.json'))
if __name__=='__main__':main()
