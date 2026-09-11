"""Finish deterministic native-source checks and stage bounded terrain repairs; never AI."""
from collections import Counter,defaultdict
import importlib.util
import gzip,json,math,sys,time
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import box,Polygon
from run import ROOT,HERE,read,save,digest
spec=importlib.util.spec_from_file_location('pending_context',HERE/'pending-context.py');context=importlib.util.module_from_spec(spec);spec.loader.exec_module(context)
sys.path.insert(0,str(HERE.parent/'assembly-support-review'))
import exact_tin as exact
import terrain_patches as terrain
sys.path.insert(0,str(HERE.parent/'island-detail-integration'))
from native_terrain_validation import validate_native_mesh
from publish import validate_patch
BATCH='government-200-20260911';DOC=ROOT/'docs/astra-city/government-import'/BATCH/'resolution';LOCAL=HERE/'local'/('government-198-resolution-20260911')
PREV=DOC.parent/'pending-context';OLD=HERE/'local'/(BATCH+'-pending-context-v1')

def sample_points(geometry):
    v=np.asarray(geometry['position']).reshape(-1,3);idx=np.asarray(geometry['index']).reshape(-1,3);faces=v[idx]
    points=[v,faces.mean(axis=1)];bottom=v[:,1].min()
    for face in faces:
        for a,b in zip(face,np.roll(face,-1,axis=0)):
            if max(a[1],b[1])>bottom+.35:continue
            n=math.ceil(np.linalg.norm((a-b)[[0,2]]))
            if n>1:points.append(a[None,:]+(b-a)[None,:]*np.arange(1,n)[:,None]/n)
    return np.concatenate(points),bottom


def audit_native(points,bottom,tri):
    polys=shapely.polygons(tri[:,:,[0,2]]);valid=shapely.area(polys)>1e-12
    if not valid.any():return {'covered':0,'checks':len(points),'passed':False,'reason':'native-terrain-coverage'}
    heights=context.shared.samples(points[:,[0,2]],tri[valid],shapely.STRtree(polys[valid]));covered=np.isfinite(heights);low=points[:,1]<=bottom+.35;gaps=points[:,1]-heights
    def bounds(a):return [float(a.min()),float(a.max())] if len(a) else None
    gap=bounds(gaps[covered]);rim=bounds(gaps[covered&low]);reasons=[]
    if not covered.all():reasons.append('native-terrain-coverage')
    if gap and gap[0]<-.5:reasons.append('native-source-below-grade')
    if not rim or rim[0]>.1 or rim[1]>1:reasons.append('native-ground-contact')
    return {'checks':len(points),'covered':int(covered.sum()),'lowRimChecks':int(low.sum()),'gapRange':gap,'lowRimGapRange':rim,'passed':not reasons,'reasons':reasons}


def rectangle_for(bounds,parent):
    lo,hi=bounds;g=parent['meta']['georef'];cell=g['aE']
    return [math.floor((lo[0]-20+834500-g['bE'])/cell),math.floor((lo[2]-20-816500+g['bN'])/cell),math.ceil((hi[0]+20+834500-g['bE'])/cell),math.ceil((hi[2]+20-816500+g['bN'])/cell)]


def extent(cells,parent):
    g=parent['meta']['georef'];c0,r0,c1,r1=cells
    return [g['bE']+c0*g['aE']-834500,816500-g['bN']-r0*g['aN'],g['bE']+c1*g['aE']-834500,816500-g['bN']-r1*g['aN']]


def make_patch(group,parent,native,sources):
    bb=extent(group['cells'],parent);core=[bb[0]+10,bb[1]+10,bb[2]-10,bb[3]-10]
    sampler=terrain.fine.DemSampler(parent,rendered=True);raw_sampler=terrain.fine.DemSampler(parent)
    step=5;w=round((bb[2]-bb[0])/step)+1;h=round((bb[3]-bb[1])/step)+1
    grid=np.array([[bb[0]+c*step,bb[1]+r*step] for r in range(h) for c in range(w)])
    raw=np.array([raw_sampler.ground(x,z) for x,z in grid]);assert (raw>0).all(),'parent-water-mask'
    assert native[:,:,1].min()>=1.2,'native-terrain-near-water-clamp'
    pg=parent['meta']['georef'];cell=pg['aE'];pcells=[]
    c0,r0,c1,r1=group['cells']
    for r in range(r0,r1):
        for c in range(c0,c1):
            a=np.array([pg['bE']+c*cell-834500,816500-pg['bN']+r*cell]);b=a+[cell,0];d=a+[0,cell];e=a+[cell,cell];pcells.extend([np.array([a,b,d]),np.array([b,e,d])])
    regions=[(core,False),([bb[0],bb[1],bb[2],core[1]],True),([bb[0],core[3],bb[2],bb[3]],True),([bb[0],core[1],core[0],core[3]],True),([core[2],core[1],bb[2],core[3]],True)]
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
                        alpha=max(0,min(1,min(v[0]-bb[0],bb[2]-v[0],v[2]-bb[1],bb[3]-v[2])/10))
                        v[1]=v[1]*alpha+sampler.ground(v[0],v[2])*(1-alpha)
                    vertices.append(v)
                for i in range(1,len(vertices)-1):
                    face=np.array([vertices[0],vertices[i],vertices[i+1]])
                    if np.linalg.norm(np.cross(face[1]-face[0],face[2]-face[0]))>=1e-8:output.append(face)
    tri=np.asarray(output);assert len(tri)>0,'no-native-facets'
    heights=[sampler.ground(x,z) for x,z in grid]
    vegetation=[]
    for x,z in grid:
        c=min(parent['w']-1,max(0,round((x+834500-pg['bE'])/cell)));r=min(parent['h']-1,max(0,round((z-816500+pg['bN'])/cell)));vegetation.append(parent['vegetation'][r*parent['w']+c])
    uid=group['uids'][0];patch_id='government-native-'+uid.replace('landsd/','').replace(':','-')
    patch={'id':patch_id,'w':w,'h':h,'cell':step,'elev':heights,'renderedElev':heights,'vegetation':vegetation,'coarseCells':group['cells'],'meta':{'georef':{'aE':step,'aN':-step,'bE':bb[0]+834500,'bN':816500-bb[1],'W':w,'H':h},'parentTerrain':'city/data/terrain.json','parentSha256':digest((ROOT/'3d-viewer/city/data/terrain.json').read_bytes()),'targetUids':group['uids'],'source':{'provider':'Lands Department/HKSAR','crs':'EPSG:2326','verticalDatum':'HKPD','nativeSources':sources,'policy':'Original native terrain facets in the core; 10m outer transition split on original parent triangle boundaries. Parent water mask retained. Source building geometry and elevations unchanged.'}},'nativeMesh':{'position':tri.reshape(-1).tolist(),'index':list(range(len(tri)*3)),'source':{'verticalDatum':'HKPD','verticalScale':1,'policy':'Original source facets with bounded parent-edge transition; no AI geometry.'}}}
    validate_patch(patch,parent)
    assert len(tri)<=25000,'terrain-runtime-budget'
    return patch


def main():
    start=time.monotonic();DOC.mkdir(parents=True,exist_ok=True);LOCAL.mkdir(parents=True,exist_ok=True)
    source=read(PREV/'selection.json.gz');context_report=read(PREV/'results.json.gz');geometries={r['uid']:r for r in read(OLD/'geometry.json.gz')['rows']}
    previous={r['uid']:r for r in context_report['rows']};metrics={r['uid']:r for r in read(PREV/'metrics.json')['rows']}
    parent=read(ROOT/'3d-viewer/city/data/terrain.json');manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
    assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==source['manifestSHA256']
    rows=source['rows'];assert len(rows)==198
    save(DOC/'selection.json.gz',{**source,'batch':'government-198-resolution-20260911'})
    # Collect only triangles covering each candidate's potential parent-cell rectangle.
    regions={r['uid']:extent(rectangle_for(r['candidate']['entry']['worldBounds'],parent),parent) for r in rows}
    fragments=defaultdict(list);used=defaultdict(list)
    for n,proof in enumerate(context_report['nativeSources'],1):
        sheet=proof['sheet'];folder=OLD/'terrain'/sheet/'decoded'
        for entry in proof['entries']:assert digest((folder/entry['name']).read_bytes())==entry['sha256'],'native cache changed'
        native=np.concatenate([context.triangles(p) for p in sorted(folder.rglob('*.gltf'))]);x0=native[:,:,0].min(axis=1);x1=native[:,:,0].max(axis=1);z0=native[:,:,2].min(axis=1);z1=native[:,:,2].max(axis=1)
        for uid,bb in regions.items():
            hits=native[(x1>=bb[0])&(x0<=bb[2])&(z1>=bb[1])&(z0<=bb[3])]
            if len(hits):fragments[uid].append(hits);used[uid].append({'sheet':sheet,'revision':proof['revisionDate'],'sourceETag':proof['sourceETag'],'directorySHA256':proof['directorySHA256'],'sourceFiles':[{'path':str((folder/e['name']).relative_to(ROOT)),'sha256':e['sha256']} for e in proof['entries']]})
        if n%20==0:print(json.dumps({'nativeSheetsChecked':n}),flush=True)
    registry={c['uid'] for r in read(ROOT/'docs/astra-city/landmark-registry/inventory-candidates.json')['rows'] for c in r['candidates']}
    with context.connect() as c:
        c.execute('SET TRANSACTION READ ONLY');reviews=dict(c.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC',([r['uid'] for r in rows],)))
    outcomes=[];eligible=[]
    for r in rows:
        uid=r['uid'];e=r['candidate']['entry'];native=np.concatenate(fragments[uid]) if fragments[uid] else np.empty((0,3,3));points,bottom=sample_points(geometries[uid]);audit=audit_native(points,bottom,native)
        reasons=[]
        if e['overlapOfSmallerFootprint']<.98 or e['footprintCentroidDistanceMetres']>1:reasons.append('source-part-identity-not-proven-by-current-contract')
        if uid in registry:reasons.append('landmark-component-scope')
        if reviews.get(uid) in ('held','source-unavailable','identity-unresolved','installed-verified'):reasons.append('existing-source-review-requires-resolution')
        reasons.extend(audit.get('reasons',['native-terrain-coverage']) if not audit['passed'] else [])
        outcomes.append({'uid':uid,'sourceSHA256':e['sha256'],'native':audit,'reasons':reasons,'sourceSheets':[s['sheet'] for s in used[uid]],'humanStatus':'held-unknown' if reasons else 'in-process','nextStep':'Investigate the specific source identity, coverage or native-ground contact blocker' if reasons else 'Validate a source-backed terrain correction'})
        if not reasons:eligible.append(r)
    groups=[]
    for r in eligible:groups.append({'uids':[r['uid']],'cells':rectangle_for(r['candidate']['entry']['worldBounds'],parent)})
    changed=True
    while changed:
        changed=False
        for i,a in enumerate(groups):
            for j,b in enumerate(groups[i+1:],i+1):
                if terrain.overlap(a['cells'],b['cells']):
                    a['cells']=[min(a['cells'][0],b['cells'][0]),min(a['cells'][1],b['cells'][1]),max(a['cells'][2],b['cells'][2]),max(a['cells'][3],b['cells'][3])];a['uids']+=b['uids'];groups.pop(j);changed=True;break
            if changed:break
    installed_patches=[read(ROOT/'3d-viewer'/p['url']) for p in manifest['terrainPatches']];by_uid={r['uid']:r for r in outcomes};patches=[]
    # Merged rectangles need complete native sources across the rectangle, not only point samples.
    for i,group in enumerate(groups):
        try:
            assert not any(terrain.overlap(group['cells'],p['coarseCells']) for p in installed_patches),'overlaps-installed-terrain-patch'
            bb=extent(group['cells'],parent);source_map={s['sheet']:s for uid in group['uids'] for s in used[uid]};pieces=[]
            for sheet in source_map:
                alltri=np.concatenate([context.triangles(p) for p in sorted((OLD/'terrain'/sheet/'decoded').rglob('*.gltf'))]);hits=alltri[(alltri[:,:,0].max(axis=1)>=bb[0])&(alltri[:,:,0].min(axis=1)<=bb[2])&(alltri[:,:,2].max(axis=1)>=bb[1])&(alltri[:,:,2].min(axis=1)<=bb[3])];pieces.append(hits)
            patch=make_patch(group,parent,np.concatenate(pieces),list(source_map.values()));path=LOCAL/'terrain-patches'/(patch['id']+'.json');save(path,patch)
            patches.append({'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes()),'uids':group['uids'],'bounds':bb,'triangles':len(patch['nativeMesh']['index'])//3})
            for uid in group['uids']:by_uid[uid]['terrainPatch']=str(path.relative_to(ROOT))
        except (AssertionError,ValueError) as error:
            for uid in group['uids']:by_uid[uid]['reasons'].append('terrain-patch: '+str(error));by_uid[uid]['humanStatus']='held-unknown';by_uid[uid]['nextStep']='Resolve native terrain coverage, boundary or overlap constraint before another import attempt'
        if (i+1)%10==0:print(json.dumps({'terrainGroupsChecked':i+1,'groups':len(groups),'patches':len(patches)}),flush=True)
    result={'models':198,'originalBatch':200,'previousInstalled':2,'patches':patches,'rows':outcomes,'reasonCounts':dict(Counter(reason for row in outcomes for reason in row['reasons'])),'stagedModels':sum(len(p['uids']) for p in patches),'aiCalls':0,'modelGeometryChanges':0,'publication':False,'seconds':round(time.monotonic()-start,3)}
    save(DOC/'source-resolution.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','patches')}),flush=True)

if __name__=='__main__':main()
