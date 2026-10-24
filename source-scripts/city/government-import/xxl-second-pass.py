"""Bounded XXL source/identity/terrain investigation. No AI or publication."""
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib.util
import json, gzip, shutil, struct, subprocess, sys, uuid, zipfile
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row,NATIVE_RUN
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
import shape_prepare as recovery
from download import acquire,safe
from convert import _convert_one
spec=importlib.util.spec_from_file_location('xxl_resolution',HERE/'resolve-pass.py');resolution=importlib.util.module_from_spec(spec);spec.loader.exec_module(resolution)
context=resolution.context
BATCH='government-xxl-second-20260911';BASE=ROOT/'docs/astra-city/government-import/government-xxl-20260911';DOC=BASE/'second-pass';LOCAL=HERE/'local'/BATCH

def h(p):return digest(Path(p).read_bytes())
def rel(p):return str(Path(p).relative_to(ROOT))
def call(args):subprocess.run(args,cwd=ROOT,check=True)

def projection_metrics(tri,foot):
    polygons=shapely.polygons(tri[:,:,[0,2]]);polygons=polygons[shapely.area(polygons)>1e-10]
    projection=shapely.union_all(polygons);intersection=projection.intersection(foot).area
    return {'footprintArea':foot.area,'projectionArea':projection.area,'footprintCovered':intersection/foot.area,'projectionInsideFootprint':intersection/projection.area,'overlapOfSmaller':intersection/min(foot.area,projection.area),'centroidDistance':projection.centroid.distance(foot.centroid),'hausdorffDistance':projection.hausdorff_distance(foot),'symmetricDifferenceArea':projection.symmetric_difference(foot).area}

def exact_forms(native, forms):
    """Candidates only: exact CSUID/object ID/GeoRef, never nearest-name assignment."""
    possible={ (m['objectId'],m['buildingCSUID']) for m in native['matching']['officialCandidates'] }
    return [s for s in forms if (s['building'].get('objectId'),s['building'].get('buildingCSUID')) in possible and s['building']['buildingCSUID'][:10]==native['modelId'][1:11]]

def prepare():
    assert not (DOC/'selection.json.gz').exists(),'Frozen second pass exists; resume its explicit phase'
    original=read(BASE/'selection.json.gz');final=read(BASE/'final-results.json.gz');held={r['modelId'] for r in final['rows'] if r['humanStatus']=='held-unknown'}
    rows=[r for r in original['rows'] if r['modelId'] in held];assert len(rows)==18
    refs={r['modelId'][1:11] for r in rows};forms=[];manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
    for tile in manifest['tiles']:
        p=ROOT/'3d-viewer'/tile['url'];raw=p.read_bytes()
        for b in json.loads(raw)['buildings']:
            if (b.get('buildingCSUID') or '')[:10] in refs:forms.append({'building':b,'tile':tile['url'],'tileSHA256':digest(raw)})
    for r in rows:r['diagnosticSourceCandidates']=exact_forms(r['native']['model'],forms)
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        actual=dict(c.execute('SELECT r.cache_key,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=ANY(%s)',(NATIVE_RUN,[r['native']['cacheKey'] for r in rows])))
        metadata=dict(c.execute("SELECT DISTINCT ON(sheet) sheet,result-'models' FROM astra_modelling.city_source_directories WHERE sheet=ANY(%s) ORDER BY sheet,created_at DESC",(sorted({r['native']['sheet'] for r in rows}),)))
    assert all(actual[r['native']['cacheKey']]==r['native']['resultSha'] for r in rows)
    frozen={**original,'batch':BATCH,'rows':rows,'manifestSHA256':h(ROOT/'3d-viewer/city/data/manifest.json'),'previousFinalSHA256':h(BASE/'final-results.json.gz'),'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'previousInstalled':4,'aiCalls':0}
    save(DOC/'selection.json.gz',frozen);save(LOCAL/'source-directories.json',metadata)
    print(json.dumps({'selected':len(rows),'exactFormCandidates':[{'modelId':r['modelId'],'count':len(r['diagnosticSourceCandidates'])} for r in rows]}),flush=True)

def run():
    frozen=read(DOC/'selection.json.gz');resources={'native-model:'+r['native']['cacheKey']+':'+r['modelId'] for r in frozen['rows']}
    resources|={'building:'+s['building']['uid'] for r in frozen['rows'] for s in r['diagnosticSourceCandidates']}
    owned=reservations.claim('codex-xxl-second-'+str(uuid.uuid4()),sorted(resources),batch=BATCH);assert owned['ok']
    save(LOCAL/'reservation.json',json.loads(json.dumps(owned['reservation'],default=str)))
    call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])

def source_sheet(sheet,rows,prior,caches,retained):
    folder=LOCAL/'sheets'/sheet
    directory,_=recovery.scan({'SHEETNO':sheet,'Format_glTF':prior['sourceURL'],'REVISIONDATE':prior['revision']},folder/'directory')
    assert directory['etag']==prior['etag'] and directory['directorySHA256']==prior['directorySHA256'],'Pinned source revision changed'
    missing={r['modelId'] for r in rows if r['sourceSHA256'] not in caches}
    directory['models']=[m for m in directory['models'] if m['modelId'] in missing];assert {m['modelId'] for m in directory['models']}==missing
    acquired=acquire(directory,folder/'directory/zip-directory.bin',folder/'original',retained=retained,include_terrain=True)
    packed=folder/'packed';packed.mkdir(exist_ok=True);assets=[]
    with zipfile.ZipFile(folder/'original'/(sheet+'.zip')) as z:
        for name in z.namelist():
            if name.startswith('TERRAIN') and name.endswith(('.gltf','.bin')):
                p=folder/'terrain'/safe(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name))
        for r in rows:
            sha=r['sourceSHA256'];dest=LOCAL/'assets'/(sha+'.glb.gz');dest.parent.mkdir(exist_ok=True)
            if sha in caches:
                raw=recovery.canonical_bytes(caches[sha].read_bytes(),sha);method='local-exact-cache'
            else:
                converted=_convert_one(z,z.getinfo(r['native']['model']['sourceEntry']),folder/'decoded',packed,{}, {'modelId':r['modelId']})
                raw=recovery.canonical_bytes((packed/converted['asset']['asset']).read_bytes(),sha);method='verified-government-recovery'
            assert len(raw)==r['native']['model']['asset']['bytes'];dest.write_bytes(raw);assets.append({'modelId':r['modelId'],'sha256':sha,'method':method,'path':rel(dest)})
    proof={k:v for k,v in acquired.items() if k!='source'};save(folder/'recovery.json',{'assets':assets,'source':proof})
    return {'sheet':sheet,'assets':assets,'source':proof,'terrainPaths':[rel(p) for p in sorted((folder/'terrain').rglob('*.gltf'))]}

def glb_triangles(r):
    raw=gzip.decompress((LOCAL/'assets'/(r['sourceSHA256']+'.glb.gz')).read_bytes());magic,version,length=struct.unpack_from('<III',raw);assert magic==0x46546c67 and version==2 and length==len(raw)
    size,kind=struct.unpack_from('<II',raw,12);assert kind==0x4e4f534a;data=json.loads(raw[20:20+size]);at=20+size;n,kind=struct.unpack_from('<II',raw,at);assert kind==0x004e4942 and at+8+n==len(raw)
    assert len(data['buffers'])==1 and not data['buffers'][0].get('uri')
    folder=LOCAL/'unpacked'/r['modelId'];folder.mkdir(parents=True,exist_ok=True);(folder/'buffer.bin').write_bytes(raw[at+8:]);data['buffers'][0]['uri']='buffer.bin';save(folder/'model.gltf',data)
    tri=context.triangles(folder/'model.gltf');assert len(tri)==r['triangles']
    assert np.max(np.abs(np.array([tri.min(axis=(0,1)),tri.max(axis=(0,1))])-r['native']['model']['worldBounds']))<.002
    return tri

def owned():
    receipt=read(LOCAL/'reservation.json');assert reservations.owns(receipt)
    frozen=read(DOC/'selection.json.gz');assert h(ROOT/'3d-viewer/city/data/manifest.json')==frozen['manifestSHA256'];rows=frozen['rows']
    for r in rows:
        for s in r['diagnosticSourceCandidates']:assert h(ROOT/'3d-viewer'/s['tile'])==s['tileSHA256']
    wanted={r['sourceSHA256'] for r in rows};caches={};retained=defaultdict(list)
    paths=subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g','*.glb.gz','-g','download.json','source-scripts/city','3d-viewer/city/data'],cwd=ROOT,text=True).splitlines()
    for name in paths:
        p=ROOT/name
        if p.name=='download.json':
            try:
                d=read(p)
                if d.get('sheet'):retained[d['sheet']].append((p,d))
            except (ValueError,OSError):pass
        elif p.name.removesuffix('.glb.gz') in wanted and h(p)==p.name.removesuffix('.glb.gz'):caches[p.name.removesuffix('.glb.gz')]=p
    grouped=defaultdict(list)
    for r in rows:grouped[r['native']['sheet']].append(r)
    metadata=read(LOCAL/'source-directories.json');sources=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(source_sheet,s,rs,metadata[s],caches,retained[s]) for s,rs in grouped.items()]
        for future in as_completed(futures):
            sources.append(future.result());print(json.dumps({'sourceSheets':len(sources),'total':len(grouped)}),flush=True)
    save(DOC/'recovery.json',{'sheets':sources,'aiCalls':0,'r2':'not-configured; retained local caches checked first'})
    all_native=[]
    for source in sources:
        pieces=[context.triangles(ROOT/p) for p in source['terrainPaths']]
        if pieces:all_native.append(np.concatenate(pieces))
    all_native=np.concatenate(all_native);results=[];runtime_rows=[]
    for r in rows:
        tri=glb_triangles(r);lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));native=all_native[(all_native[:,:,0].max(axis=1)>=lo[0]-1)&(all_native[:,:,0].min(axis=1)<=hi[0]+1)&(all_native[:,:,2].max(axis=1)>=lo[2]-1)&(all_native[:,:,2].min(axis=1)<=hi[2]+1)]
        unique=np.unique(tri.reshape(-1,3),axis=0);geometry={'position':tri.reshape(-1).tolist(),'index':list(range(len(tri)*3))}
        points,bottom=resolution.sample_points(geometry);audit=resolution.audit_native(points,bottom,native)
        matches=[]
        for s in r['diagnosticSourceCandidates']:
            rings=s['building']['rings'];foot=Polygon(rings[0],rings[1:]);assert foot.is_valid
            fit=projection_metrics(tri,foot);matches.append({'uid':s['building']['uid'],'name':s['building'].get('name'),'csuid':s['building']['buildingCSUID'],'metrics':fit})
        result={'modelId':r['modelId'],'uid':r['uid'],'name':r['name'],'sha256':r['sourceSHA256'],'native':audit,'projectionCandidates':matches,'previousReasons':r['reasons'],'triangles':r['triangles'],'sourceSheet':r['native']['sheet'],'aiCalls':0,'identityAccepted':False,'publication':False}
        results.append(result);save(DOC/'diagnostics.json',{'rows':results,'complete':len(results)==18,'aiCalls':0,'geometryChanges':0})
        if r['source']:
            entry={**r['native']['model']['candidate'],'rootTranslation':[-834500,0,816500],'sourceTile':r['native']['sheet']};runtime_rows.append({'uid':r['uid'],'source':r['source'],'candidate':{'path':str(LOCAL/'assets'/(r['sourceSHA256']+'.glb.gz')),'entry':entry},'native':r['native']})
        print(json.dumps({'modelId':r['modelId'],'nativeReasons':audit.get('reasons'),'projection':[{'uid':m['uid'],'coverage':round(m['metrics']['footprintCovered'],4),'inside':round(m['metrics']['projectionInsideFootprint'],4),'centroid':round(m['metrics']['centroidDistance'],3)} for m in matches]}),flush=True)
    selection={**frozen,'rows':runtime_rows};save(DOC/'runtime-selection.json.gz',selection)
    call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'runtime-selection.json.gz'),'--candidates',rel(LOCAL),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
    print(json.dumps({'finishedDiagnosticModels':len(results),'currentRuntimeModels':len(runtime_rows),'aiCalls':0}),flush=True)

if __name__=='__main__':{'prepare':prepare,'run':run,'owned':owned}[sys.argv[1]]()
