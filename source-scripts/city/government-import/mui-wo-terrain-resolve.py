"""Stage exact native-TIN terrain for the 23-model Mui Wo remainder; no AI."""
import argparse,collections,gzip,hashlib,importlib.util,json,math,urllib.request,zipfile
from pathlib import Path,PurePosixPath
import numpy as np
import shapely
from shapely.geometry import Polygon,box

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BATCH='government-mui-wo-23-20260914';LOCAL=HERE/'local'/BATCH
DOC=ROOT/'docs/astra-city/government-import'/BATCH/'resolution'
NEW=('10-SW-14C','10-SW-19A')
OLD=('10-SW-12A','10-SW-12B','10-SW-13C','10-SW-22B','10-SW-7D')
PROTECTED=('landsd/173368:0','landsd/261651:0')
spec=importlib.util.spec_from_file_location('resolve_pass',HERE/'resolve-pass.py');resolve=importlib.util.module_from_spec(spec);spec.loader.exec_module(resolve)
context=resolve.context;terrain=resolve.terrain

def read(path):
    raw=Path(path).read_bytes();return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)
def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def fetch():
    records=[]
    for sheet in NEW:
        base=LOCAL/'recovered/sheets'/sheet;meta=read(base/'directory/result.json');archive=base/'full'/(sheet+'.zip')
        if not archive.exists() or archive.stat().st_size!=meta['archiveBytes']:
            request=urllib.request.Request(meta['sourceURL'],headers={'User-Agent':'hongkong-sandbox-source-verifier/1.0'})
            with urllib.request.urlopen(request,timeout=180) as response:raw=response.read();etag=response.headers.get('ETag')
            assert len(raw)==meta['archiveBytes'] and (not meta.get('etag') or etag==meta['etag'])
            archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(raw)
        decoded=base/'full/decoded';members=[]
        with zipfile.ZipFile(archive) as source:
            for info in source.infolist():
                parts=PurePosixPath(info.filename).parts
                if info.is_dir() or not parts or not parts[0].startswith('TERRAIN') or Path(info.filename).suffix not in ('.gltf','.bin'):continue
                assert '..' not in parts and not PurePosixPath(info.filename).is_absolute()
                target=decoded.joinpath(*parts);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read(info))
                members.append({'path':str(target.relative_to(ROOT)),'sha256':sha(target),'bytes':target.stat().st_size})
        assert any(row['path'].endswith('.gltf') for row in members) and any(row['path'].endswith('.bin') for row in members)
        records.append({'sheet':sheet,'revision':meta['revision'],'etag':meta['etag'],'directorySHA256':meta['directorySHA256'],'archiveSHA256':sha(archive),'archiveBytes':archive.stat().st_size,'members':members})
    save(DOC/'downloaded-terrain-sources.json',{'sheets':records,'aiCalls':0,'geometryChanges':0})
    print(json.dumps({'downloadedSheets':len(records),'archiveBytes':sum(r['archiveBytes'] for r in records),'terrainMembers':sum(len(r['members']) for r in records),'aiCalls':0}),flush=True)

def sources():
    result={}
    for sheet in OLD:
        folder=HERE.parent/'mui-wo-detail-completion/staged'/sheet;manifest=read(folder/'manifest.json')
        files=sorted(p for p in folder.rglob('*.gltf') if 'TERRAIN' in str(p))
        assert files;result[sheet]={'triangles':np.concatenate([context.triangles(p) for p in files]),'proof':{'sheet':sheet,'revision':manifest['tileRevision'],'sourceCacheSHA256':manifest['sourceCacheSha256'],'sourceFiles':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in files]}}
    downloaded={r['sheet']:r for r in read(DOC/'downloaded-terrain-sources.json')['sheets']}
    for sheet in NEW:
        folder=LOCAL/'recovered/sheets'/sheet/'full/decoded';files=sorted(p for p in folder.rglob('*.gltf') if 'TERRAIN' in str(p));assert files
        result[sheet]={'triangles':np.concatenate([context.triangles(p) for p in files]),'proof':{k:v for k,v in downloaded[sheet].items() if k!='members'}}
    return result

def sampled_patch(group,parent,native_tri,proofs,parent_url,parent_sha,patch_id):
    """Build the same seam-safe sampled TIN child already used by Mui Wo."""
    c0,r0,c1,r1=group['cells'];assert 0<=c0<c1<parent['w'] and 0<=r0<r1<parent['h']
    bb=resolve.extent(group['cells'],parent);step=1;w=round(bb[2]-bb[0])+1;h=round(bb[3]-bb[1])+1
    xx,zz=np.meshgrid(np.arange(w)+bb[0],np.arange(h)+bb[1]);points=np.c_[xx.ravel(),zz.ravel()]
    polys=shapely.polygons(native_tri[:,:,[0,2]]);valid=shapely.area(polys)>1e-12
    native_values=context.shared.samples(points,native_tri[valid],shapely.STRtree(polys[valid]))
    # A rectangular terrain child can cover unrelated basic forms. Retain the
    # current parent under every non-target footprint and blend outward for 3 m.
    region=box(*bb);target=set(group['uids']);protected=[];protected_uids=[];manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
    for tile in manifest['tiles']:
        for building in read(ROOT/'3d-viewer'/tile['url'])['buildings']:
            if building['uid'] in target or building['uid'] not in PROTECTED:continue
            polygon=Polygon(building['rings'][0],building['rings'][1:])
            if polygon.intersects(region):protected.append(polygon);protected_uids.append(building['uid'])
    if protected:
        protected_shape=shapely.union_all(protected);protect_alpha=np.clip((shapely.distance(shapely.points(points),protected_shape)-3)/3,0,1)
    else:protect_alpha=np.ones(len(points))
    old=terrain.fine.DemSampler(parent,rendered=True);raw=terrain.fine.DemSampler(parent);pg=parent['meta']['georef'];cell=abs(pg['aE'])
    elev=[];rendered=[];vegetation=[];boundary_error=0;water_changes=0
    for i,(x,z) in enumerate(points):
        c=i%w;r=i//w;before=old.ground(x,z);before_raw=raw.ground(x,z);alpha=min(1,min(c,r,w-1-c,h-1-r)/10)*protect_alpha[i]
        if not np.isfinite(native_values[i]) or before_raw<=0:alpha=0
        after=float(native_values[i]*alpha+before*(1-alpha)) if alpha else before
        value=before_raw if before_raw<=0 else after;elev.append(round(value,6));rendered.append(round(after,6))
        cc=min(parent['w']-1,max(0,round((x+834500-pg['bE'])/cell)));rr=min(parent['h']-1,max(0,round((z-816500+pg['bN'])/cell)));vegetation.append(parent['vegetation'][rr*parent['w']+cc])
        water_changes+=int(before_raw<=0 and value>0)
        if c in (0,w-1) or r in (0,h-1):boundary_error=max(boundary_error,abs(after-before))
    assert boundary_error<1e-6 and water_changes==0
    patch={'id':patch_id,'w':w,'h':h,'cell':step,'elev':elev,'renderedElev':rendered,'vegetation':vegetation,'coarseCells':group['cells'],'meta':{'georef':{'aE':1,'aN':-1,'bE':bb[0]+834500,'bN':816500-bb[1],'W':w,'H':h},'parentTerrain':parent_url,'parentSha256':parent_sha,'targetUids':group['uids'],'source':{'provider':'Lands Department/HKSAR','verticalDatum':'HKPD','crs':'EPSG:2326','nativeSources':proofs,'protectedBasicBuildingUids':sorted(protected_uids),'policy':'Exact native TIN barycentric sampling at 1m spacing; 10m outer transition to existing parent triangle heights. Current parent terrain is retained under non-target basic-building footprints with a 3m retained collar and 3m outward transition. Raw water mask retained. No building elevation changes. Spacing is not survey accuracy.'}}}
    resolve.validate_patch(patch,parent)
    return patch,{'gridNodes':len(points),'nativeCoveredNodes':int(np.isfinite(native_values).sum()),'protectedBasicBuildings':len(protected_uids),'boundaryMaximumError':boundary_error,'waterMaskChanges':water_changes}

def stage():
    DOC.mkdir(parents=True,exist_ok=True);parent_path=ROOT/'3d-viewer/city/data/terrain-mui-wo.json';parent=read(parent_path);parent_sha=sha(parent_path)
    selection=read(ROOT/'docs/astra-city/government-import'/BATCH/'check-selection.json.gz');geometries={r['uid']:r for r in read(LOCAL/'geometry.json.gz')['rows']};native=sources();rows=[];eligible=[];east_eligible=[]
    pg=parent['meta']['georef'];east_edge=pg['bE']+(parent['w']-1)*pg['aE']-834500
    for row in selection['rows']:
        uid=row['uid'];entry=row['candidate']['entry'];sheet=row['native']['sheet'];cells=resolve.rectangle_for(entry['worldBounds'],parent);bb=resolve.extent(cells,parent);tri=native[sheet]['triangles'];hits=tri[(tri[:,:,0].max(axis=1)>=bb[0])&(tri[:,:,0].min(axis=1)<=bb[2])&(tri[:,:,2].max(axis=1)>=bb[1])&(tri[:,:,2].min(axis=1)<=bb[3])]
        points,bottom=resolve.sample_points(geometries[uid]);audit=resolve.audit_native(points,bottom,hits);reasons=[] if audit['passed'] else audit.get('reasons',['native-terrain-coverage'])
        result={'uid':uid,'sheet':sheet,'native':audit,'cells':cells,'reasons':list(reasons),'identityConcerns':row.get('selectionConcerns',[]),'humanStatus':'in-process' if not reasons else 'held-unknown'};rows.append(result)
        if not reasons:
            item={'uids':[uid],'cells':cells,'sheet':sheet,'entry':entry}
            if 0<=cells[0]<cells[2]<parent['w'] and 0<=cells[1]<cells[3]<parent['h']:eligible.append(item)
            elif entry['worldBounds'][0][0]>=east_edge:east_eligible.append(item)
            else:result['reasons'].append('terrain-patch: no single containing terrain parent');result['humanStatus']='held-unknown'
    groups=[]
    for item in eligible:
        merged=False
        for group in groups:
            if terrain.overlap(group['cells'],item['cells']):
                group['cells']=[min(group['cells'][0],item['cells'][0]),min(group['cells'][1],item['cells'][1]),max(group['cells'][2],item['cells'][2]),max(group['cells'][3],item['cells'][3])];group['uids']+=item['uids'];group['sheets'].add(item['sheet']);merged=True;break
        if not merged:groups.append({'uids':list(item['uids']),'cells':list(item['cells']),'sheets':{item['sheet']}})
    changed=True
    while changed:
        changed=False
        for i,a in enumerate(groups):
            for j,b in enumerate(groups[i+1:],i+1):
                if terrain.overlap(a['cells'],b['cells']):
                    a['cells']=[min(a['cells'][0],b['cells'][0]),min(a['cells'][1],b['cells'][1]),max(a['cells'][2],b['cells'][2]),max(a['cells'][3],b['cells'][3])];a['uids']+=b['uids'];a['sheets']|=b['sheets'];groups.pop(j);changed=True;break
            if changed:break
    patches=[];existing=parent.get('patches',[]);by_uid={r['uid']:r for r in rows}
    for group in groups:
        try:
            assert not any(terrain.overlap(group['cells'],p['coarseCells']) for p in existing),'overlaps-existing-mui-wo-child'
            bb=resolve.extent(group['cells'],parent);pieces=[]
            for sheet in group['sheets']:
                tri=native[sheet]['triangles'];pieces.append(tri[(tri[:,:,0].max(axis=1)>=bb[0])&(tri[:,:,0].min(axis=1)<=bb[2])&(tri[:,:,2].max(axis=1)>=bb[1])&(tri[:,:,2].min(axis=1)<=bb[3])])
            proofs=[native[s]['proof'] for s in sorted(group['sheets'])]
            patch=resolve.make_patch(group,parent,np.concatenate(pieces),proofs,parent_url='city/data/terrain-mui-wo.json',parent_sha256=parent_sha)
            patches.append(patch)
            for uid in group['uids']:by_uid[uid]['terrainPatch']=patch['id']
        except (AssertionError,ValueError) as error:
            for uid in group['uids']:by_uid[uid]['reasons'].append('terrain-patch: '+str(error));by_uid[uid]['humanStatus']='held-unknown'
    wrapper={**parent,'patches':existing+patches};wrapper_path=LOCAL/'terrain-mui-wo-with-remainder.json';save(wrapper_path,wrapper)
    candidates=[{'path':str(wrapper_path.relative_to(ROOT)),'sha256':sha(wrapper_path),'replaces':{'url':'city/data/terrain-mui-wo.json','sha256':parent_sha}}];sampled=[]
    if east_eligible:
        global_path=ROOT/'3d-viewer/city/data/terrain.json';global_parent=read(global_path);global_sha=sha(global_path);items=[]
        for item in east_eligible:items.append({'uids':item['uids'],'cells':resolve.rectangle_for(item['entry']['worldBounds'],global_parent)})
        group={'uids':[u for item in items for u in item['uids']],'cells':[min(i['cells'][0] for i in items),min(i['cells'][1] for i in items),max(i['cells'][2] for i in items),max(i['cells'][3] for i in items)]}
        # The regional Mui Wo patch owns global cells through its exclusive east edge.
        group['cells'][0]=max(group['cells'][0],parent['coarseCells'][2]);assert group['cells'][0]<group['cells'][2]
        manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
        for entry in manifest['terrainPatches']:
            if entry['url']=='city/data/terrain-mui-wo.json':continue
            other=read(ROOT/'3d-viewer'/entry['url'])
            if other.get('coarseCells'):assert not terrain.overlap(group['cells'],other['coarseCells']),'overlaps-existing-top-level-child'
        tri=native['10-SW-19A']['triangles'];patch,check=sampled_patch(group,global_parent,tri,[native['10-SW-19A']['proof']],'city/data/terrain.json',global_sha,'government-native-mui-wo-east-remainder')
        path=LOCAL/'terrain-mui-wo-east-remainder.json';save(path,patch);candidates.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path)})
        sampled.append({'path':str(path.relative_to(ROOT)),'uids':group['uids'],'coarseCells':group['cells'],**check})
        for uid in group['uids']:by_uid[uid]['terrainPatch']=patch['id'];by_uid[uid]['humanStatus']='in-process'
    save(DOC/'terrain-candidates.json',candidates)
    report={'models':len(rows),'nativeGroundPass':sum(r['native']['passed'] for r in rows),'patches':len(patches)+len(sampled),'patchedModels':sum('terrainPatch' in r for r in rows),'sampledPatches':sampled,'rows':rows,'aiCalls':0,'modelGeometryChanges':0,'publication':False}
    save(DOC/'source-resolution.json',report);print(json.dumps({k:v for k,v in report.items() if k!='rows'}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('phase',choices=('fetch','stage'));globals()[p.parse_args().phase]()
