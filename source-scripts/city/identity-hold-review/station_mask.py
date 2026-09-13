"""Source-backed station land-mask correction; stage a replacement, never edit runtime."""
import json,hashlib,sys,importlib.util,pathlib
import numpy as np
import shapely
ROOT=pathlib.Path(__file__).resolve().parents[3]; HERE=pathlib.Path(__file__).resolve().parent; OUT=ROOT/'docs/astra-city/identity-hold-review/station-mask'
sys.path.insert(0,str(ROOT/'source-scripts/city/assembly-support-review'))
import native_terrain as native
sp=importlib.util.spec_from_file_location('fine',ROOT/'source-scripts/city/mui-wo-buildings/fine_terrain_audit.py'); fine=importlib.util.module_from_spec(sp);sp.loader.exec_module(fine)
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 oldpath=ROOT/'3d-viewer/city/data/support-native-297401-0.json'; old=read(oldpath);patch=json.loads(json.dumps(old));g=old['meta']['georef'];extension=140;x0=g['bE']-834500-extension;z0=816500-g['bN'];w,h=old['w']+extension,old['h'];xs=x0+np.arange(w);zs=z0+np.arange(h);xx,zz=np.meshgrid(xs,zs);points=np.c_[xx.ravel(),zz.ravel()]
 parent=read(ROOT/'3d-viewer/city/data/terrain.json');parentraw=fine.DemSampler(parent);parentrendered=fine.DemSampler(parent,rendered=True);pg=parent['meta']['georef'];baseRaw=[];baseRendered=[];vegetation=[]
 for i,(x,z) in enumerate(points):
  c=i%w;r=i//w
  if c>=extension:
   oi=r*old['w']+c-extension;baseRaw.append(old['elev'][oi]);baseRendered.append(old['renderedElev'][oi]);vegetation.append(old['vegetation'][oi])
  else:
   baseRaw.append(parentraw.ground(x,z));baseRendered.append(parentrendered.ground(x,z));cc=round((x+834500-pg['bE'])/pg['aE']);rr=round((816500-z-pg['bN'])/pg['aN']);vegetation.append(parent['vegetation'][rr*parent['w']+cc])
 patch.update(w=w,h=h,vegetation=vegetation,coarseCells=[498,420,503,425]);patch['meta']['georef'].update(bE=x0+834500,W=w)
 building_path=ROOT/'3d-viewer/city/data/tiles/0_-1.json';b=next(b for b in read(building_path)['buildings'] if b['uid']=='landsd/297401:0');poly=shapely.Polygon(b['rings'][0],b['rings'][1:]);assert poly.is_valid
 # One diagonal grid-cell collar ensures all interpolation triangles under the verified footprint have valid land vertices.
 collar=poly.buffer(2**.5);in_site=shapely.covers(collar,shapely.points(points))
 src=next(s for s in old['meta']['source']['nativeSources'] if s['sheet']=='11-NW-24C');assert sha(ROOT/src['manifest'])==src['manifestSha256']
 for f in src['files']:assert sha(ROOT/f['path'])==f['sha256']
 _,_,_,_,triangles,tree=native.terrain_index((ROOT/src['manifest']).parent);nativeY=native.samples(points,triangles,tree)
 raw=np.array(baseRaw);rendered=np.array(baseRendered);edge=(xx.ravel()==xs[0])|(xx.ravel()==xs[-1])|(zz.ravel()==zs[0])|(zz.ravel()==zs[-1]);mask=in_site&(raw<=0)&np.isfinite(nativeY)&(nativeY>0)&~edge
 raw[mask]=np.round(nativeY[mask],6);rendered[mask]=np.round(nativeY[mask],6);patch['elev']=raw.tolist();patch['renderedElev']=rendered.tolist();patch['id']='support-native-297401-0-station-land-v2';patch['meta']['source']['policy']='Native TIN at 1x HKPD. Supersedes the earlier child only at source-positive masked grid nodes inside LandsD station footprint and one diagonal 1m-cell interpolation collar. Replacement child outer boundary and all other mask nodes unchanged. No building geometry or height edits.';patch['meta']['source']['maskRepair']={'uid':b['uid'],'footprintFile':str(building_path.relative_to(ROOT)),'footprintFileSHA256':sha(building_path),'previousPatch':str(oldpath.relative_to(ROOT)),'previousPatchSHA256':sha(oldpath),'collarMetres':2**.5,'changedNodes':int(mask.sum())}
 newpath=HERE/'terrain-patches'/f"{patch['id']}.json";newpath.write_text(json.dumps(patch,separators=(',',':'))+'\n')
 # Full footprint census, including the west wing outside this existing child.
 minx,minz,maxx,maxz=poly.bounds;ax=np.arange(np.floor(minx),np.ceil(maxx)+1);az=np.arange(np.floor(minz),np.ceil(maxz)+1);a,bz=np.meshgrid(ax,az);allpoints=np.c_[a.ravel(),bz.ravel()];allpoints=allpoints[shapely.covers(poly,shapely.points(allpoints))];ys=native.samples(allpoints,triangles,tree)
 ps=fine.DemSampler(parent);new=fine.DemSampler(patch,rendered=True);oldsample=fine.DemSampler(old,rendered=True)
 inside=(allpoints[:,0]>=xs[0])&(allpoints[:,0]<=xs[-1])&(allpoints[:,1]>=zs[0])&(allpoints[:,1]<=zs[-1]);outside_water=[p.tolist() for p in allpoints[~inside] if ps.ground(*p)<=0]
 centre=next(q for q in read(building_path)['buildings'] if q['uid']=='landsd/297401:0')['centre'];centre_native=float(native.samples(np.array([centre]),triangles,tree)[0]);edge_error=float(np.abs(rendered[edge]-np.array(baseRendered)[edge]).max())
 report={'issue':'HKS-214','uid':'landsd/297401:0','finding':'Inherited coarse water mask suppressed source-confirmed reclaimed land underneath the station. Previous rim-only visual/CPU acceptance missed the interior hole.','source':src,'sourceVerified':True,'supersededPatch':str(oldpath.relative_to(ROOT)),'supersededSHA256':sha(oldpath),'replacementPatch':str(newpath.relative_to(ROOT)),'replacementSHA256':sha(newpath),'sourcePositiveMaskedNodesInFootprintCollar':int((in_site&(np.array(baseRaw)<=0)&np.isfinite(nativeY)&(nativeY>0)).sum()),'changedNodes':int(mask.sum()),'boundaryChangeMetres':edge_error,'coarseCells':patch['coarseCells'],'previousCoarseCells':old['coarseCells'],'extensionWestMetres':extension,'changedNativeHeightRange':[float(nativeY[mask].min()),float(nativeY[mask].max())],'outsideCorrectionNodesChanged':int((~mask&(raw!=np.array(baseRaw))).sum()),'fullFootprintGrid':{'samples':len(allpoints),'nativeCovered':int(np.isfinite(ys).sum()),'nativeHeightRange':[float(ys.min()),float(ys.max())],'outsideReplacementChild':int((~inside).sum()),'outsideReplacementCoarseWaterSamples':len(outside_water),'outsideChildCoarseWaterExamples':outside_water[:20]},'centre':{'xz':centre,'sourceTIN':centre_native,'oldChildRendered':oldsample.ground(*centre),'newChildRendered':new.ground(*centre)},'verticalScale':1,'published':False,'approval':'Await final scene ray/triangle and architectural surface checks.'}
 assert edge_error==0 and report['outsideCorrectionNodesChanged']==0
 report['probes']=[{'xz':p.tolist(),'sourceTIN':float(y),'stagedGround':new.ground(*p)} for p,y in zip(allpoints[::200],ys[::200])]
 changes={'columns':['oldIndex','replacementIndex','x','z','oldElevation','oldRenderedElevation','newElevation','newRenderedElevation','sourceTIN'],'rows':[[int((i//w)*old['w']+(i%w)-extension) if i%w>=extension else None,int(i),float(points[i,0]),float(points[i,1]),float(baseRaw[i]),float(baseRendered[i]),float(raw[i]),float(rendered[i]),float(nativeY[i])] for i in np.flatnonzero(mask)],'supersededSHA256':sha(oldpath),'replacementSHA256':sha(newpath),'scope':'Exact source-reviewed changed-node allowlist; null oldIndex identifies new western extension nodes relative to unchanged coarse-parent interpolation.'}
 save(OUT/'changed-nodes.json',changes);report['changedNodeEvidence']={'path':str((OUT/'changed-nodes.json').relative_to(ROOT)),'sha256':sha(OUT/'changed-nodes.json'),'existingChildNodes':sum(r[0] is not None for r in changes['rows']),'newWesternExtensionNodes':sum(r[0] is None for r in changes['rows'])}
 save(OUT/'report.json',report);print(json.dumps(report,indent=2))
if __name__=='__main__':main()
