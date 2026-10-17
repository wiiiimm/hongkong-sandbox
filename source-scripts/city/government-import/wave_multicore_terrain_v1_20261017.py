"""Private multi-core original-terrain constructor; original building bytes untouched."""
import numpy as np
from run import ROOT,HERE,digest
from primrose_compound_foundation_v2_20261015 import module
base=module('wave_multicore_base',HERE/'resolve-pass.py')
extent=base.extent;terrain=base.terrain;exact=base.exact;validate_patch=base.validate_patch

def transition_weight(x,z,cores):
    return max(max(0.,min(1.,min(x-(c[0]-10),(c[2]+10)-x,z-(c[1]-10),(c[3]+10)-z)/10)) for c in cores)

def core_regions(bb,cores):
    xs=sorted(set([bb[0],bb[2]]+[v for c in cores for v in [c[0],c[2]]]))
    zs=sorted(set([bb[1],bb[3]]+[v for c in cores for v in [c[1],c[3]]]))
    return [([a,c,b,d],not any(q[0]<(a+b)/2<q[2] and q[1]<(c+d)/2<q[3] for q in cores)) for a,b in zip(xs,xs[1:]) for c,d in zip(zs,zs[1:])]

def make_patch(group,parent,native,sources,native_core=None,parent_url='city/data/terrain.json',parent_sha256=None,allow_native_below_clamp=False,terrain_triangle_budget=25000):
    bb=extent(group['cells'],parent);cores=native_core
    assert cores and all(bb[0]<c[0]<c[2]<bb[2] and bb[1]<c[1]<c[3]<bb[3] for c in cores)
    sampler=terrain.fine.DemSampler(parent,rendered=True);raw_sampler=terrain.fine.DemSampler(parent)
    # Keep the established 5 m refinement for the territory DEM. A patch
    # nested inside an existing 5 m regional surface needs a finer grid, so
    # divide each parent cell into five deterministic child cells.
    parent_cell=abs(parent['meta']['georef']['aE']);step=min(5,parent_cell/5);w=round((bb[2]-bb[0])/step)+1;h=round((bb[3]-bb[1])/step)+1
    grid=np.array([[bb[0]+c*step,bb[1]+r*step] for r in range(h) for c in range(w)])
    raw=np.array([raw_sampler.ground(x,z) for x,z in grid]);water=raw<=0
    if not allow_native_below_clamp:assert native[:,:,1].min()>=1.2,'native-terrain-near-water-clamp'
    pg=parent['meta']['georef'];cell=pg['aE'];pcells=[]
    c0,r0,c1,r1=group['cells']
    for r in range(r0,r1):
        for c in range(c0,c1):
            a=np.array([pg['bE']+c*cell-834500,816500-pg['bN']+r*cell]);b=a+[cell,0];d=a+[0,cell];e=a+[cell,cell];pcells.extend([np.array([a,b,d]),np.array([b,e,d])])
    regions=core_regions(bb,cores)
    output=[]
    for tri in native:
        for region,transition in regions:
            poly=exact.rect(list(tri),region)
            if len(poly)<3:continue
            for points in ([exact.parent_clip(poly,pt) for pt in pcells] if transition else [poly]):
                if len(points)<3:continue
                vertices=[]
                for v in points:
                    v=v.copy()
                    if transition:
                        alpha=transition_weight(v[0],v[2],cores)
                        v[1]=v[1]*alpha+sampler.ground(v[0],v[2])*(1-alpha)
                    vertices.append(v)
                for i in range(1,len(vertices)-1):
                    face=np.array([vertices[0],vertices[i],vertices[i+1]])
                    if np.linalg.norm(np.cross(face[1]-face[0],face[2]-face[0]))>=1e-8:output.append(face)
    tri=np.asarray(output);assert len(tri)>0,'no-native-facets'
    heights=[sampler.ground(x,z) for x,z in grid]
    elev=[float(before) if masked or after<=0 else float(after) for before,after,masked in zip(raw,heights,water)]
    assert np.array_equal(np.asarray(elev)<=0,water),'parent-water-mask-changed'
    vegetation=[]
    for x,z in grid:
        c=min(parent['w']-1,max(0,round((x+834500-pg['bE'])/cell)));r=min(parent['h']-1,max(0,round((z-816500+pg['bN'])/cell)));vegetation.append(parent['vegetation'][r*parent['w']+c])
    uid=group['uids'][0];patch_id='government-native-'+uid.replace('landsd/','').replace(':','-')
    if parent_sha256 is None:parent_sha256=digest((ROOT/'3d-viewer'/parent_url).read_bytes())
    patch={'id':patch_id,'w':w,'h':h,'cell':step,'elev':elev,'renderedElev':heights,'vegetation':vegetation,'coarseCells':group['cells'],'meta':{'georef':{'aE':step,'aN':-step,'bE':bb[0]+834500,'bN':816500-bb[1],'W':w,'H':h},'parentTerrain':parent_url,'parentSha256':parent_sha256,'targetUids':group['uids'],'source':{'provider':'Lands Department/HKSAR','crs':'EPSG:2326','verticalDatum':'HKPD','nativeSources':sources,'parentWaterMask':{'waterNodes':int(water.sum()),'landNodes':int((~water).sum()),'policy':'Raw parent water/land classification preserved at every refinement node.'},'policy':'Original native terrain facets in the union of complete source cores; 10m outer transition split on original parent triangle boundaries. Parent water mask retained. Source building geometry and elevations unchanged.'}},'nativeMesh':{'position':tri.reshape(-1).tolist(),'index':list(range(len(tri)*3)),'source':{'verticalDatum':'HKPD','verticalScale':1,'policy':'Original source facets with bounded parent-edge transition; no AI geometry.'}}}
    patch['nativeMesh']['source']['protectedSourceCores']=cores
    validate_patch(patch,parent)
    assert len(tri)<=terrain_triangle_budget,'terrain-runtime-budget'
    return patch
