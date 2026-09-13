"""Reconstruct the previously approved Elements terrain bytes from exact source binaries."""
import importlib.util,json,sys,uuid
from pathlib import Path
import numpy as np
import shapely
spec=importlib.util.spec_from_file_location('xxl_second',Path(__file__).with_name('xxl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE,DOC,LOCAL=s.ROOT,s.HERE,s.DOC/'elements',s.LOCAL/'elements'
read,save,h,rel=s.read,s.save,s.h,s.rel

def start():
    claim=s.reservations.claim('codex-xxl-elements-restore-'+str(uuid.uuid4()),['building:landsd/273061:0','building:landsd/204153:0'],batch=s.BATCH+'-elements-restore');assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    s.call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])

def owned():
    assert s.reservations.owns(read(LOCAL/'reservation.json'))
    evidence=read(ROOT/'docs/astra-city/identity-four-native/elements-native-terrain.json');report=read(ROOT/'docs/astra-city/identity-four-native/terrain-patches.json');bundle=report['bundles'][0];expected=bundle['patches'][0];parent=read(ROOT/'3d-viewer'/bundle['parentTerrainURL']);assert h(ROOT/'3d-viewer'/bundle['parentTerrainURL'])==bundle['parentSha256']
    old=s.resolution.terrain.fine.DemSampler(parent,rendered=True);raw=s.resolution.terrain.fine.DemSampler(parent);g=parent['meta']['georef'];cell=abs(g['aE']);c0,r0,c1,r1=expected['coarseCells'];x0=g['bE']+c0*cell-834500;z0=816500-g['bN']+r0*cell;w=round((c1-c0)*cell)+1;hh=round((r1-r0)*cell)+1
    xx,zz=np.meshgrid(np.arange(w)+x0,np.arange(hh)+z0);pts=np.c_[xx.ravel(),zz.ravel()];heights=np.full(len(pts),-np.inf);proof=[]
    for source in evidence['sources']:
        folder=s.LOCAL/'sheets'/source['sheet']/'terrain'
        for f in source['files']:
            if f['path'].endswith('.bin'):
                p=next(folder.rglob(Path(f['path']).name));assert h(p)==f['sha256'];proof.append({'path':rel(p),'sha256':h(p)})
        tri=np.concatenate([s.context.triangles(p) for p in sorted(folder.rglob('*.gltf'))]);polys=shapely.polygons(tri[:,:,[0,2]]);valid=shapely.area(polys)>1e-12;usable=tri[valid];tree=shapely.STRtree(polys[valid]);heights=np.maximum(heights,s.context.shared.samples(pts,usable,tree))
    elev=[];rendered=[];vegetation=[]
    for i,(x,z) in enumerate(pts):
        c=i%w;r=i//w;before=old.ground(x,z);before_raw=raw.ground(x,z);alpha=min(1,min(c,r,w-1-c,hh-1-r)/10)
        if not np.isfinite(heights[i]) or before_raw<=0:alpha=0
        after=float(heights[i]*alpha+before*(1-alpha)) if alpha else before;value=before_raw if before_raw<=0 else after;elev.append(round(value,6));rendered.append(round(after,6));cc=min(parent['w']-1,max(0,round((x+834500-g['bE'])/cell)));rr=min(parent['h']-1,max(0,round((z-816500+g['bN'])/cell)));vegetation.append(parent['vegetation'][rr*parent['w']+cc])
    patch={'id':'support-native-273061-0','w':w,'h':hh,'cell':1,'elev':elev,'renderedElev':rendered,'vegetation':vegetation,'coarseCells':expected['coarseCells'],'meta':{'georef':{'aE':1,'aN':-1,'bE':x0+834500,'bN':816500-z0,'W':w,'H':hh},'parentTerrain':bundle['parentTerrainURL'],'parentSha256':bundle['parentSha256'],'targetUids':['landsd/273061:0'],'source':{'provider':'Lands Department/HKSAR','verticalDatum':'HKPD','crs':'EPSG:2326','nativeSources':evidence['sources'],'policy':'Exact native TIN barycentric sampling at 1m spacing; 10m outer transition to existing parent triangle heights. Raw water mask retained. No building elevation changes. Spacing is not survey accuracy.'}}}
    path=LOCAL/'support-native-273061-0.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(patch,separators=(',',':'))+'\n');matched=h(path)==expected['sha256']
    result={'uid':'landsd/273061:0','path':rel(path),'sha256':h(path),'approvedSHA256':expected['sha256'],'exactApprovedTerrainMatch':matched,'sourceBinaries':proof,'nativeCoveredNodes':int(np.isfinite(heights).sum()),'gridNodes':len(pts),'aiCalls':0,'publication':False}
    save(DOC/'restoration.json',result);print(json.dumps(result),flush=True)
    assert matched,'Reconstruction differs from the approved terrain; no reuse approval'

if __name__=='__main__':owned() if len(sys.argv)>1 else start()
