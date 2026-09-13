"""Stage seam-safe native-TIN children for verified rim/terrain discrepancies, never edit runtime."""
import json,math,hashlib,sys,collections,functools,importlib.util
from pathlib import Path
import numpy as np
import native_terrain as native
ROOT=native.ROOT;HERE=Path(__file__).resolve().parent;OUT=ROOT/'docs/astra-city/assembly-support-review';read=native.read;sha=native.sha
spec=importlib.util.spec_from_file_location('support_dem',ROOT/'source-scripts/city/mui-wo-buildings/fine_terrain_audit.py');fine=importlib.util.module_from_spec(spec);spec.loader.exec_module(fine)
def bounds(data):
 g=data['meta']['georef'];return[g['bE']-834500,816500-g['bN'],g['bE']+(data['w']-1)*g['aE']-834500,816500-g['bN']+(data['h']-1)*abs(g['aN'])]
def overlap(a,b):return a[0]<b[2] and b[0]<a[2] and a[1]<b[3] and b[1]<a[3]
@functools.lru_cache(maxsize=2)
def load_native(path):
 _,_,_,_,usable,tree=native.terrain_index((ROOT/path).parent);return usable,tree

def main():
 evidence=read(OUT/'native-terrain.json');source_report=read(OUT/'report.json');models={p['uid']:p for p in source_report['rows']};mf=read(ROOT/'3d-viewer/city/data/manifest.json');parents={'city/data/terrain.json':read(ROOT/'3d-viewer/city/data/terrain.json')}
 for p in mf['terrainPatches']:parents[p['url']]=read(ROOT/'3d-viewer'/p['url'])
 targets=sorted({p['uid'] for p in evidence['sourceGridProposals']});grouped=collections.defaultdict(list);held=[]
 for uid in targets:
  points=np.array([p['position'] for p in models[uid]['rim']]);bb=[float(points[:,0].min()-20),float(points[:,2].min()-20),float(points[:,0].max()+20),float(points[:,2].max()+20)]
  available=[(url,p) for url,p in parents.items() if bounds(p)[0]<=bb[0] and bounds(p)[1]<=bb[1] and bounds(p)[2]>=bb[2] and bounds(p)[3]>=bb[3]]
  if not available:held.append({'uid':uid,'reason':'no single containing terrain parent'});continue
  url,p=min(available,key=lambda q:abs(q[1]['meta']['georef']['aE']));g=p['meta']['georef'];cell=abs(g['aE']);c0=math.floor((bb[0]+834500-g['bE'])/cell);r0=math.floor((bb[1]-816500+g['bN'])/cell);c1=math.ceil((bb[2]+834500-g['bE'])/cell);r1=math.ceil((bb[3]-816500+g['bN'])/cell);grouped[url].append({'uids':[uid],'cells':[c0,r0,c1,r1]})
 # Merge intersecting same-parent rectangles, avoiding double-rendered terrain triangles.
 for groups in grouped.values():
  changed=True
  while changed:
   changed=False
   for i,a in enumerate(groups):
    for j,b in enumerate(groups[i+1:],i+1):
     if overlap(a['cells'],b['cells']):
      c=a['cells'];d=b['cells'];a['cells']=[min(c[0],d[0]),min(c[1],d[1]),max(c[2],d[2]),max(c[3],d[3])];a['uids']+=b['uids'];groups.pop(j);changed=True;break
    if changed:break
 bundles=[];allrows=[];folder=HERE/'terrain-patches';folder.mkdir(exist_ok=True)
 for url,groups in grouped.items():
  p=parents[url];g=p['meta']['georef'];cell=abs(g['aE']);old=fine.DemSampler(p,rendered=True);raw=fine.DemSampler(p);patches=[]
  for group in groups:
   if any(overlap(group['cells'],child['coarseCells']) for child in p.get('patches',[])):
    held.append({'uids':group['uids'],'reason':'overlaps existing nested terrain; requires explicit merge'});continue
   c0,r0,c1,r1=group['cells'];x0=g['bE']+c0*cell-834500;z0=816500-g['bN']+r0*cell;x1=g['bE']+c1*cell-834500;z1=816500-g['bN']+r1*cell;w=round(x1-x0)+1;h=round(z1-z0)+1
   xs=np.arange(w)+x0;zs=np.arange(h)+z0;xx,zz=np.meshgrid(xs,zs);pts=np.c_[xx.ravel(),zz.ravel()];heights=np.full(len(pts),-np.inf);sources=[]
   for src in evidence['sources']:
    b=src['worldBounds'];bb=[b[0][0],b[0][2],b[1][0],b[1][2]]
    if not overlap([x0,z0,x1,z1],bb):continue
    assert sha(ROOT/src['manifest'])==src['manifestSha256'];usable,tree=load_native(src['manifest']);heights=np.maximum(heights,native.samples(pts,usable,tree));sources.append(src)
   elev=[];rendered=[];vegetation=[];boundary_error=0;water_changes=0
   for i,(x,z) in enumerate(pts):
    c=i%w;r=i//w;before=old.ground(x,z);before_raw=raw.ground(x,z);alpha=min(1,min(c,r,w-1-c,h-1-r)/10)
    if not np.isfinite(heights[i]) or before_raw<=0:alpha=0
    after=float(heights[i]*alpha+before*(1-alpha)) if alpha else before
    value=before_raw if before_raw<=0 else after;elev.append(round(value,6));rendered.append(round(after,6));cc=min(p['w']-1,max(0,round((x+834500-g['bE'])/cell)));rr=min(p['h']-1,max(0,round((z-816500+g['bN'])/cell)));vegetation.append(p['vegetation'][rr*p['w']+cc]);water_changes+=int(before_raw<=0 and value>0)
    if c in (0,w-1) or r in (0,h-1):boundary_error=max(boundary_error,abs(after-before))
   patch={'id':'support-native-'+group['uids'][0].replace('landsd/','').replace(':','-'),'w':w,'h':h,'cell':1,'elev':elev,'renderedElev':rendered,'vegetation':vegetation,'coarseCells':group['cells'],'meta':{'georef':{'aE':1,'aN':-1,'bE':x0+834500,'bN':816500-z0,'W':w,'H':h},'parentTerrain':url,'parentSha256':sha(ROOT/'3d-viewer'/url),'targetUids':group['uids'],'source':{'provider':'Lands Department/HKSAR','verticalDatum':'HKPD','crs':'EPSG:2326','nativeSources':sources,'policy':'Exact native TIN barycentric sampling at 1m spacing; 10m outer transition to existing parent triangle heights. Raw water mask retained. No building elevation changes. Spacing is not survey accuracy.'}}}
   new=fine.DemSampler(patch,rendered=True);rows=[]
   for uid in group['uids']:
    gaps=[s['position'][1]-new.ground(s['position'][0],s['position'][2]) for s in models[uid]['rim']];rows.append({'uid':uid,'samples':len(gaps),'within2m':sum(abs(v)<=2 for v in gaps),'gapRange':[min(gaps),max(gaps)]})
   path=folder/(patch['id']+'.json');path.write_text(json.dumps(patch,separators=(',',':'))+'\n');patches.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'uids':group['uids'],'coarseCells':group['cells']});allrows.append({'patch':str(path.relative_to(ROOT)),'rows':rows,'gridNodes':len(pts),'nativeCoveredNodes':int(np.isfinite(heights).sum()),'boundaryError':boundary_error,'waterMaskChanges':water_changes,'eligibleForBrowserValidation':all(r['within2m']==r['samples'] for r in rows)});assert boundary_error<1e-6 and water_changes==0
  bundles.append({'parentTerrainURL':url,'parentSha256':sha(ROOT/'3d-viewer'/url),'patches':patches})
 result={'issue':'HKS-214','staged':True,'bundles':bundles,'checks':allrows,'held':held,'inputReportSha256':sha(OUT/'report.json'),'nativeEvidenceSha256':sha(OUT/'native-terrain.json'),'integration':'Append children only to hash-matched existing parent. Root coarse children must be manifest terrain patches, not overwritten by app terrainPatches assignment. Parent renderer omits coarseCells exactly once. Run combined roof/foundation and browser checks before publication.','publicationApproved':False};(OUT/'terrain-patches.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'patches':len(allrows),'parts':sum(len(r['rows']) for r in allrows),'held':held,'nodes':sum(r['gridNodes'] for r in allrows)}))
if __name__=='__main__':main()
