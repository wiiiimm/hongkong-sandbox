"""Fill exact adjacent terrain coverage and retain complete XXL source diagnostics."""
import importlib.util,json,subprocess,sys,uuid
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,box
spec=importlib.util.spec_from_file_location('xxl_second',Path(__file__).with_name('xxl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE,DOC,LOCAL=s.ROOT,s.HERE,s.DOC,s.LOCAL
read,save,h,rel,connect,reservations=s.read,s.save,s.h,s.rel,s.connect,s.reservations

def prepare():
    frozen=read(DOC/'selection.json.gz');diagnostics=read(DOC/'diagnostics.json');assert diagnostics['complete']
    rows={r['modelId']:r for r in frozen['rows']};selected={r['native']['sheet'] for r in rows.values()};index_path=ROOT/'source-scripts/city/landmark-acquisition/index.json';index=read(index_path);extras=set();affected=[]
    assert index['completePagination']
    for r in diagnostics['rows']:
        if 'native-terrain-coverage' not in r['native'].get('reasons',[]):continue
        lo,hi=rows[r['modelId']]['native']['model']['worldBounds'];region=box(lo[0]+834500-30,816500-hi[2]-30,hi[0]+834500+30,816500-lo[2]+30)
        sheets={f['attributes']['SHEETNO'] for f in index['features'] if Polygon(f['geometry']['rings'][0]).intersects(region)}
        extras|=sheets-selected;affected.append(r['modelId'])
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY');metadata=dict(c.execute("SELECT DISTINCT ON(sheet) sheet,result-'models' FROM astra_modelling.city_source_directories WHERE sheet=ANY(%s) ORDER BY sheet,created_at DESC",(sorted(extras),)))
    assert set(metadata)==extras
    plan={'indexPath':rel(index_path),'indexSHA256':h(index_path),'selectionSHA256':h(DOC/'selection.json.gz'),'diagnosticsSHA256':h(DOC/'diagnostics.json'),'extraSheets':sorted(extras),'affectedModels':affected,'manifestSHA256':frozen['manifestSHA256']}
    save(DOC/'adjacent-terrain-plan.json',plan);save(LOCAL/'adjacent-directories.json',metadata)
    resources=read(LOCAL/'reservation.json')['resources']+['terrain-sheet:'+key for key in sorted(extras)]
    claim=reservations.claim('codex-xxl-adjacent-'+str(uuid.uuid4()),resources,batch=s.BATCH+'-adjacent');assert claim['ok'];receipt=json.loads(json.dumps(claim['reservation'],default=str));save(LOCAL/'adjacent-reservation.json',receipt)
    s.call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'adjacent-reservation.json'),'--',sys.executable,__file__,'owned'])

def owned():
    receipt=read(LOCAL/'adjacent-reservation.json');assert reservations.owns(receipt);plan=read(DOC/'adjacent-terrain-plan.json')
    for path,sha in [(ROOT/plan['indexPath'],plan['indexSHA256']),(DOC/'selection.json.gz',plan['selectionSHA256']),(DOC/'diagnostics.json',plan['diagnosticsSHA256']),(ROOT/'3d-viewer/city/data/manifest.json',plan['manifestSHA256'])]:assert h(path)==sha
    retained=defaultdict(list)
    for name in subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g','download.json','source-scripts/city'],cwd=ROOT,text=True).splitlines():
        p=ROOT/name
        try:
            d=read(p)
            if d.get('sheet'):retained[d['sheet']].append((p,d))
        except (ValueError,OSError):pass
    metadata=read(LOCAL/'adjacent-directories.json');sources=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(s.source_sheet,key,[],metadata[key],{},retained[key]) for key in plan['extraSheets']]
        for f in as_completed(futures):sources.append(f.result());print(json.dumps({'adjacentSheetsDone':len(sources),'total':len(futures)}),flush=True)
    all_sources=read(DOC/'recovery.json')['sheets']+sources;native=[]
    for source in all_sources:
        folder=LOCAL/'sheets'/source['sheet']/'terrain'
        for e in source['source']['entries']:
            if e['name'].startswith('TERRAIN') and e['name'].endswith(('.gltf','.bin')):assert h(folder/e['name'])==e['sha256']
        native.extend(s.context.triangles(ROOT/p) for p in source['terrainPaths'])
    native=np.concatenate(native);rows={r['modelId']:r for r in read(DOC/'selection.json.gz')['rows']};out=[]
    for mid in plan['affectedModels']:
        r=rows[mid];tri=s.glb_triangles(r);points,bottom=s.resolution.sample_points({'position':tri.reshape(-1).tolist(),'index':list(range(len(tri)*3))});lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));near=native[(native[:,:,0].max(axis=1)>=lo[0]-1)&(native[:,:,0].min(axis=1)<=hi[0]+1)&(native[:,:,2].max(axis=1)>=lo[2]-1)&(native[:,:,2].min(axis=1)<=hi[2]+1)]
        audit=s.resolution.audit_native(points,bottom,near);out.append({'modelId':mid,'native':audit});save(DOC/'adjacent-terrain-results.json',{'rows':out,'complete':len(out)==len(plan['affectedModels']),'sources':sources,'aiCalls':0,'modelGeometryChanges':0})
        print(json.dumps({'modelId':mid,'native':audit}),flush=True)
    print(json.dumps({'complete':True,'models':len(out),'sourceSheets':len(all_sources),'aiCalls':0}),flush=True)

if __name__=='__main__':owned() if len(sys.argv)>1 else prepare()
