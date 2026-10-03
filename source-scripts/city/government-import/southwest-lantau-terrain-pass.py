"""Stage unchanged Shek Pik / Fan Lau / southwest Lantau sources with bounded native terrain."""
from collections import Counter
import gzip,hashlib,importlib.util,json,shutil
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE='government-shek-pik-fan-lau-304-20260917';BATCH='government-shek-pik-fan-lau-compute-20260917'
DOC=ROOT/'docs/astra-city/government-import'/SOURCE;LOCAL=HERE/'local'/SOURCE
TERRAIN=LOCAL/'source-terrain';STAGE=HERE/'accepted'/BATCH
spec=importlib.util.spec_from_file_location('resolve',HERE/'resolve-pass.py');resolve=importlib.util.module_from_spec(spec);spec.loader.exec_module(resolve)
context=resolve.context;terrain_helpers=resolve.terrain

def read(path):
 path=Path(path);raw=path.read_bytes();return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
def save(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);raw=(json.dumps(value,indent=2,sort_keys=True)+'\n').encode();path.write_bytes(gzip.compress(raw,mtime=0) if path.suffix=='.gz' else raw)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rel(path):return str(Path(path).relative_to(ROOT))
def world_extent(data):
 g=data['meta']['georef'];x=g['bE']-834500;z=816500-g['bN'];return [min(x,x+(data['w']-1)*g['aE']),min(z,z-(data['h']-1)*g['aN']),max(x,x+(data['w']-1)*g['aE']),max(z,z-(data['h']-1)*g['aN'])]
def contains(extent,bounds,margin=20):
 lo,hi=bounds;return extent[0]<=lo[0]-margin and extent[1]<=lo[2]-margin and extent[2]>=hi[0]+margin and extent[3]>=hi[2]+margin
def overlaps(a,b):return not(a[2]<=b[0] or a[0]>=b[2] or a[3]<=b[1] or a[1]>=b[3])
def merge(groups):
 changed=True
 while changed:
  changed=False
  for i,a in enumerate(groups):
   for j,b in enumerate(groups[i+1:],i+1):
    if a['parentURL']==b['parentURL'] and terrain_helpers.overlap(a['cells'],b['cells']):
     a['cells']=[min(a['cells'][0],b['cells'][0]),min(a['cells'][1],b['cells'][1]),max(a['cells'][2],b['cells'][2]),max(a['cells'][3],b['cells'][3])];a['uids']+=b['uids'];groups.pop(j);changed=True;break
   if changed:break
 return groups

def sampled_patch(group,parent,triangles,sources,parent_url,parent_sha,patch_id):
 """Use a bounded grid when exact native facets cannot form one runtime-safe patch."""
 bounds=resolve.extent(group['cells'],parent);parent_cell=abs(parent['meta']['georef']['aE']);step=min(5,parent_cell/5)
 w=round((bounds[2]-bounds[0])/step)+1;h=round((bounds[3]-bounds[1])/step)+1
 xx,zz=np.meshgrid(np.arange(w)*step+bounds[0],np.arange(h)*step+bounds[1]);points=np.c_[xx.ravel(),zz.ravel()]
 values=np.full(len(points),-np.inf)
 for tri in triangles:
  polygons=resolve.shapely.polygons(tri[:,:,[0,2]]);valid=resolve.shapely.area(polygons)>1e-12
  if valid.any():values=np.maximum(values,context.shared.samples(points,tri[valid],resolve.shapely.STRtree(polygons[valid])))
 old=terrain_helpers.fine.DemSampler(parent,rendered=True);raw=terrain_helpers.fine.DemSampler(parent);g=parent['meta']['georef'];cell=abs(g['aE']);elev=[];rendered=[];vegetation=[];boundary=0;water_changes=0
 for i,(x,z) in enumerate(points):
  c=i%w;r=i//w;before=old.ground(x,z);before_raw=raw.ground(x,z);alpha=min(1,min(c,r,w-1-c,h-1-r)*step/10)
  if not np.isfinite(values[i]) or before_raw<=0:alpha=0
  after=float(values[i]*alpha+before*(1-alpha)) if alpha else before;value=before_raw if before_raw<=0 else after
  elev.append(round(value,6));rendered.append(round(after,6));cc=min(parent['w']-1,max(0,round((x+834500-g['bE'])/cell)));rr=min(parent['h']-1,max(0,round((z-816500+g['bN'])/cell)));vegetation.append(parent['vegetation'][rr*parent['w']+cc]);water_changes+=int(before_raw<=0 and value>0)
  if c in (0,w-1) or r in (0,h-1):boundary=max(boundary,abs(after-before))
 patch={'id':patch_id,'w':w,'h':h,'cell':step,'elev':elev,'renderedElev':rendered,'vegetation':vegetation,'coarseCells':group['cells'],'meta':{'georef':{'aE':step,'aN':-step,'bE':bounds[0]+834500,'bN':816500-bounds[1],'W':w,'H':h},'parentTerrain':parent_url,'parentSha256':parent_sha,'targetUids':group['uids'],'source':{'provider':'Lands Department/HKSAR','crs':'EPSG:2326','verticalDatum':'HKPD','nativeSources':sources,'policy':'Exact source TIN barycentric sampling; 10m transition to the installed parent, unchanged parent water mask, unchanged building geometry.'}}}
 resolve.validate_patch(patch,parent);assert boundary<1e-5 and water_changes==0;return patch

def main():
 exact=read(DOC/'exact-pass-results.json.gz');selection={r['uid']:r for r in read(DOC/'check-selection.json.gz')['rows']};candidates={r['uid']:r for r in exact['rows'] if r['publicationCandidate']};assert len(candidates)==265
 prior=read(DOC/'terrain-pass.json') if (DOC/'terrain-pass.json').exists() else {'held':{}};fallback_uids={uid for uid,reason in prior['held'].items() if reason.startswith('terrain-patch:')}
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');global_path=ROOT/'3d-viewer/city/data/terrain.json';global_parent=read(global_path)
 parents={'city/data/terrain.json':{'data':global_parent,'path':global_path,'extent':world_extent(global_parent),'top':True}}
 regional=set();installed_top=[]
 for entry in manifest.get('terrainPatches',[]):
  path=ROOT/'3d-viewer'/entry['url'];data=read(path);installed_top.append({'url':entry['url'],'data':data,'extent':world_extent(data)})
  if entry['url'] in regional:parents[entry['url']]={'data':data,'path':path,'extent':world_extent(data),'top':False}
 groups=[];held={}
 for uid in sorted(candidates):
  bounds=selection[uid]['candidate']['entry']['worldBounds'];inside=[(url,p) for url,p in parents.items() if url!='city/data/terrain.json' and contains(p['extent'],bounds)]
  if inside:url,parent=min(inside,key=lambda x:(x[1]['extent'][2]-x[1]['extent'][0])*(x[1]['extent'][3]-x[1]['extent'][1]))
  else:
   url='city/data/terrain.json';parent=parents[url];expanded=[bounds[0][0]-20,bounds[0][2]-20,bounds[1][0]+20,bounds[1][2]+20];collision=next((x['url'] for x in installed_top if overlaps(expanded,x['extent'])),None)
   if collision:held[uid]='terrain-parent-boundary-or-installed-patch-overlap:'+collision;continue
  groups.append({'uids':[uid],'cells':resolve.rectangle_for(bounds,parent['data']),'parentURL':url})
 groups=merge(groups);proofs={r['sheet']:r for r in read(DOC/'source-terrain.json')['sheets']};terrains={};terrain_bounds={}
 for sheet in sorted(proofs):
  tri=np.concatenate([context.triangles(p) for p in sorted((TERRAIN/sheet/'decoded').rglob('*.gltf'))]);terrains[sheet]=tri;terrain_bounds[sheet]=[float(tri[:,:,0].min()),float(tri[:,:,2].min()),float(tri[:,:,0].max()),float(tri[:,:,2].max())]
 STAGE.mkdir(parents=True,exist_ok=True);nested={url:[] for url in regional};top=[];patch_rows=[];accepted=set()
 for number,group in enumerate(groups,1):
  parent=parents[group['parentURL']]
  if any(terrain_helpers.overlap(group['cells'],child['coarseCells']) for child in parent['data'].get('patches',[])):
   held.update({uid:'terrain-group-overlaps-installed-child' for uid in group['uids']});continue
  try:
   bounds=resolve.extent(group['cells'],parent['data']);pieces=[];sheets=[]
   for sheet,tri in terrains.items():
    if not overlaps(bounds,terrain_bounds[sheet]):continue
    hit=tri[(tri[:,:,0].max(axis=1)>=bounds[0])&(tri[:,:,0].min(axis=1)<=bounds[2])&(tri[:,:,2].max(axis=1)>=bounds[1])&(tri[:,:,2].min(axis=1)<=bounds[3])]
    if len(hit):pieces.append(hit);sheets.append(sheet)
   if not pieces:raise ValueError('no-source-terrain-facets')
   source=[{k:proofs[s][k] for k in ('sheet','revisionDate','sourceETag','directorySHA256','compactArchiveSHA256')} for s in sheets]
   patch_id=f'government-southwest-lantau-{number:03d}'
   try:
    if set(group['uids'])&fallback_uids:raise ValueError('use-sampled-fallback')
    patch=resolve.make_patch(group,parent['data'],np.concatenate(pieces),source,parent_url=group['parentURL'],parent_sha256=sha(parent['path']),allow_native_below_clamp=True,terrain_triangle_budget=50000)
   except (AssertionError,ValueError):patch=sampled_patch(group,parent['data'],pieces,source,group['parentURL'],sha(parent['path']),patch_id)
   patch['id']=patch_id
   if parent['top']:
    path=STAGE/'terrain'/(patch['id']+'.json');save(path,patch);top.append({'source':rel(path),'sha256':sha(path),'destination':'city/data/'+patch['id']+'.json','resolution':patch['cell'],'area':'Shek Pik / Fan Lau / southwest Lantau government buildings'})
   else:nested[group['parentURL']].append(patch)
   accepted.update(group['uids']);patch_rows.append({'id':patch['id'],'parentURL':group['parentURL'],'uids':sorted(group['uids']),'coarseCells':group['cells'],'sourceSheets':sheets,'triangles':len(patch.get('nativeMesh',{}).get('index',[]))//3,'sampledGrid':not bool(patch.get('nativeMesh'))})
  except (AssertionError,ValueError) as error:held.update({uid:'terrain-patch:'+str(error) for uid in group['uids']})
  if number%25==0:print(json.dumps({'terrainGroups':number,'totalGroups':len(groups),'patchedModels':len(accepted)}),flush=True)
 bundles=[];metric=[]
 for url,patches in nested.items():
  if not patches:continue
  parent=parents[url];bundle_path=STAGE/'terrain'/(Path(url).stem+'-children.json');save(bundle_path,{'parentTerrainURL':url,'parentSha256':sha(parent['path']),'patches':patches,'aiCalls':0,'modelGeometryChanges':0});bundles.append(rel(bundle_path))
  wrapper={**parent['data'],'patches':parent['data'].get('patches',[])+patches};wrapper_path=LOCAL/'metric-terrain'/(Path(url).stem+'.json');save(wrapper_path,wrapper);metric.append({'path':rel(wrapper_path),'sha256':sha(wrapper_path),'replaces':{'url':url,'sha256':sha(parent['path'])}})
 metric += [{'path':x['source'],'sha256':x['sha256']} for x in top]
 models=[];forms=[]
 for uid in sorted(accepted):
  row=selection[uid];proof=candidates[uid];entry=dict(row['candidate']['entry']);entry.update(priority='detail',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,publicationApproved=False,proceduralWindows=False,placementReview='Exact unchanged Lands Department source matched by object ID and Building CSUID. Full-face same-revision source terrain and bounded native terrain refinement pass. No AI review, remodelling, simplification or geometry edit.')
  if proof['suppressesBuildingUids']:entry['suppressesBuildingUids']=proof['suppressesBuildingUids']
  asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(row['candidate']['path'],asset);assert sha(asset)==entry['sha256'];models.append(entry);form=dict(row['source']['building']);form['tile']=Path(row['source']['tile']).stem;forms.append(form)
 base=read(HERE.parent/'kai-tak-port/staged/catalogue.json');catalogue={k:v for k,v in base.items() if k not in ('models','counts','area')};catalogue.update(area='Shek Pik / Fan Lau / southwest Lantau original government buildings',loadingPolicy='Lazy progressive loading after deterministic source, terrain, runtime and browser checks',counts={'packedModels':len(models)},models=models)
 save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':len(models),'catalogues':['catalogue.json']});save(STAGE/'source-forms.json',forms);save(DOC/'terrain-candidates.json',metric)
 report={'sourceCandidates':len(candidates),'terrainAccepted':len(accepted),'terrainHeld':len(candidates)-len(accepted),'held':held,'reasonCounts':dict(Counter(held.values())),'groups':patch_rows,'nestedTerrainBundles':bundles,'topLevelTerrainPatches':top,'metricTerrainCandidates':metric,'aiCalls':0,'modelGeometryChanges':0,'publication':False};save(DOC/'terrain-pass.json',report)
 save(STAGE/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':f'city/data/official-models/{BATCH}/catalogue.json','terrain':bundles}],'topLevelTerrainPatches':top})
 print(json.dumps({'sourceCandidates':len(candidates),'terrainAccepted':len(accepted),'terrainHeld':len(candidates)-len(accepted),'groups':len(patch_rows),'nestedBundles':len(bundles),'topLevelPatches':len(top),'reasonCounts':dict(Counter(held.values())),'aiCalls':0}),flush=True)
if __name__=='__main__':main()
