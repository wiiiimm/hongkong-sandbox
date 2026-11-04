"""Script-only follow-up of the first 200 imports. Diagnostics never grant acceptance."""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
import uuid
import zipfile
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, connect, jobs, reservations, NATIVE_RUN, Jsonb, dict_row
sys.path.insert(0,str(HERE.parent/'citywide-native'))
from download import acquire, safe
from convert import validate_geometry
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from prepare_model_sample import matrix
from bake_model_geometry import decode
spec=importlib.util.spec_from_file_location('pending_native_terrain',HERE.parent/'assembly-support-review/native_terrain.py')
shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
BATCH='government-200-20260911'
PASS=BATCH+'-pending-context-v1'
STAGE='government-pending-context-v1'
DOC=ROOT/'docs/astra-city/government-import'/BATCH/'pending-context'
LOCAL=HERE/'local'/PASS


def triangles(path):
    """Existing decoder and node transforms, without changing source glTF or vertices."""
    data=read(path);validate_geometry(data,path.parent,allow_terrain_textures=True);parts=[]
    def visit(i,parent):
        node=data['nodes'][i];transform=parent@matrix(node)
        if 'mesh' in node:
            for primitive in data['meshes'][node['mesh']]['primitives']:
                v=decode(data,primitive['attributes']['POSITION'],path.parent).astype(float)
                v=(np.c_[v,np.ones(len(v))]@transform.T)[:,:3]
                v+=np.array([-834500,0,816500])
                idx=decode(data,primitive['indices'],path.parent).reshape(-1) if 'indices' in primitive else np.arange(len(v))
                parts.append(v[idx].reshape(-1,3,3))
        for child in node.get('children',[]):visit(child,transform)
    for i in data['scenes'][data.get('scene',0)]['nodes']:visit(i,np.eye(4))
    result=np.concatenate(parts);assert np.isfinite(result).all();return result


def prepare():
    if (DOC/'selection.json.gz').exists():raise ValueError('Frozen pass already exists; use --execute to resume')
    original=read(DOC.parent/'selection.json.gz');manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
    installed={m['uid'] for url in manifest.get('officialModelCatalogues',[]) for m in read(ROOT/'3d-viewer'/url)['models']}
    rows=[r for r in original['rows'] if r['uid'] not in installed]
    assert len(rows)==198 and len(original['rows'])==200
    for r in rows:
        assert digest((ROOT/'3d-viewer'/r['source']['tile']).read_bytes())==r['source']['tileSHA256']
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        native=dict(c.execute('SELECT r.cache_key,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=ANY(%s)',(NATIVE_RUN,sorted({r['native']['cacheKey'] for r in rows}))))
    assert all(native.get(r['native']['cacheKey'])==r['native']['resultSha'] for r in rows)
    frozen={**original,'batch':PASS,'rows':rows,'manifestSHA256':digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()),'parentSelectionSHA256':digest((DOC.parent/'selection.json.gz').read_bytes()),'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'previousInstalled':sorted(set(r['uid'] for r in original['rows'])&installed)}
    claim=reservations.claim('codex-pending-context-'+str(uuid.uuid4()),['building:'+r['uid'] for r in rows],batch=PASS)
    if not claim['ok']:raise ValueError('Source reservation conflict')
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    save(DOC/'selection.json.gz',frozen)
    print(json.dumps({'pending':len(rows),'alreadyInstalled':len(frozen['previousInstalled']),'aiCalls':0}),flush=True)
    return subprocess.call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,str(Path(__file__)),'--execute'],cwd=ROOT)


def source_sheet(sheet,metadata):
    """Acquire only original TIN geometry, pinned to the model's recorded sheet revision."""
    folder=LOCAL/'terrain'/sheet;prior=metadata['directories'][sheet]
    directories=HERE.parent/'enhancement-screening/local/shapes/sheets'/sheet/'directory'
    directory=directories/'zip-directory.bin'
    assert digest(directory.read_bytes())==prior['directorySHA256']
    row={**prior,'models':[]}
    download=acquire(row,directory,folder/'original',include_terrain=True)
    with zipfile.ZipFile(folder/'original'/(sheet+'.zip')) as z:
        for name in z.namelist():
            dest=folder/'decoded'/safe(name);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(name))
    paths=sorted((folder/'decoded').rglob('*.gltf'))
    if not paths:raise ValueError('No original terrain geometry in pinned sheet')
    parts=[triangles(p) for p in paths];tri=np.concatenate(parts)
    polys=shapely.polygons(tri[:,:,[0,2]]);valid=shapely.area(polys)>1e-12
    tri=tri[valid];tree=shapely.STRtree(polys[valid])
    provenance={k:download[k] for k in ['sheet','revisionDate','sourceETag','directorySHA256','sha256','bytes','entries','receivedBytes','newThisInvocationBytes']}
    provenance['triangles']=len(tri)
    return tri,tree,provenance


def terrain_diagnostic(geometry,tri,tree):
    v=np.array(geometry['position']).reshape(-1,3);ground=np.array(geometry['drawnGround'],dtype=float)
    native=shared.samples(v[:,[0,2]],tri,tree);covered=np.isfinite(native);low=v[:,1]<=v[:,1].min()+.35
    gaps=v[:,1]-native;delta=ground-native
    def extent(values):return [float(values.min()),float(values.max())] if len(values) else None
    return {'vertices':len(v),'nativeCoveredVertices':int(covered.sum()),'currentCoveredVertices':int(np.isfinite(ground).sum()),'lowRimVertices':int(low.sum()),'nativeCoveredLowRim':int((covered&low).sum()),'nativeSurfaceGapRange':extent(gaps[covered]),'nativeLowRimGapRange':extent(gaps[covered&low]),'currentMinusNativeTerrainRange':extent(delta[covered&np.isfinite(ground)]),'belowNativeTerrainBy05m':int((covered&(gaps<-.5)).sum()),'belowCurrentTerrainBy05m':int((v[:,1]-ground<-.5).sum()),'currentBurialAbsentAgainstNativeVertices':bool(covered.all() and (gaps>=-.5).all() and (v[:,1]-ground<-.5).any()),'qualification':'All decoded source vertices against original TIN triangles. Vertex diagnostics only; not surface/contact acceptance or a terrain publication plan.'}


def execute():
    start=time.monotonic();frozen=read(DOC/'selection.json.gz');receipt=read(LOCAL/'reservation.json')
    if not reservations.owns(receipt):raise ValueError('Live source ownership required')
    subprocess.run(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'geometry.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
    metrics=read(DOC/'metrics.json');by_metric={r['uid']:r for r in metrics['rows']};geometries={r['uid']:r for r in read(LOCAL/'geometry.json.gz')['rows']}
    metadata=read(HERE.parent/'enhancement-screening/local/shapes/source-metadata.json')
    grouped=defaultdict(list)
    for r in frozen['rows']:grouped[r['native']['sheet']].append(r)
    source_results={};sources=[];source_errors={}
    with ThreadPoolExecutor(max_workers=4) as pool:
        def work(sheet,items):
            tri,tree,provenance=source_sheet(sheet,metadata)
            return provenance,{r['uid']:terrain_diagnostic(geometries[r['uid']],tri,tree) for r in items if r['uid'] in geometries}
        futures={pool.submit(work,s,items):s for s,items in grouped.items()}
        for n,f in enumerate(as_completed(futures),1):
            sheet=futures[f]
            try:
                provenance,results=f.result();sources.append(provenance);source_results.update(results)
            except Exception as error:source_errors[sheet]=type(error).__name__+': '+str(error).split('?')[0][:200]
            if n%10==0 or n==len(futures):print(json.dumps({'terrainSheetsDone':n,'sheets':len(futures),'modelsWithNativeContext':len(source_results),'sourceErrors':len(source_errors)}),flush=True)
    # Nearby footprint overlap is a dependency hint, never triangle-level support approval.
    target_polys={r['uid']:Polygon(r['source']['building']['rings'][0],r['source']['building']['rings'][1:]) for r in frozen['rows']}
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json');neighbours=defaultdict(list)
    targets=list(target_polys);tree=shapely.STRtree([target_polys[u] for u in targets])
    for tile in manifest['tiles']:
        raw=(ROOT/'3d-viewer'/tile['url']).read_bytes()
        for b in json.loads(raw)['buildings']:
            poly=Polygon(b['rings'][0],b['rings'][1:])
            for i in tree.query(poly):
                uid=targets[i]
                if uid==b['uid'] or not poly.is_valid or not target_polys[uid].is_valid:continue
                area=poly.intersection(target_polys[uid]).area
                if area>.01:neighbours[uid].append({'uid':b['uid'],'targetFootprintCoverage':area/target_polys[uid].area,'sourceBase':b.get('baseHeightHKPD'),'sourceTop':b.get('topHeightHKPD'),'embeddedGeometry':bool(b.get('modelGeometry'))})
    previous={r['uid']:r for r in read(DOC.parent/'results.json.gz')['rows']};rows=[]
    for r in frozen['rows']:
        uid=r['uid'];m=by_metric[uid];n=source_results.get(uid);e=r['candidate']['entry'];reasons=[]
        if m.get('error'):reasons.append('runtime-metrics-error')
        else:
            if m['missingTerrain']:reasons.append('drawn-terrain-coverage')
            if m['minSurfaceGap']<-.5:reasons.append('terrain-intersection')
            if m['minLowGap']>.1 or m['maxLowGap']>1:reasons.append('ground-contact')
            if m['maxSamplerDelta']>.004:reasons.append('sampler-renderer-disagreement')
            if e['overlapOfSmallerFootprint']<.98 or e['footprintCentroidDistanceMetres']>1:reasons.append('strict-identity-fit')
        if not n:route='native-terrain-unavailable'
        elif n['nativeCoveredVertices']<n['vertices']:route='native-terrain-incomplete'
        elif n['currentBurialAbsentAgainstNativeVertices']:route='viewer-terrain-refinement-investigation'
        elif n['belowNativeTerrainBy05m']:route='source-below-grade-context'
        elif n['nativeLowRimGapRange'][0]>.1 or n['nativeLowRimGapRange'][1]>1:route='native-ground-contact-or-support'
        elif 'strict-identity-fit' in reasons:route='identity-fit-investigation'
        else:route='remaining-current-runtime-placement-checks'
        rows.append({'uid':uid,'sourceSHA256':e['sha256'],'sourceTile':e['sourceTile'],'previousState':previous[uid]['state'],'currentReasons':reasons,'route':route,'nativeTerrain':n,'overlappingFootprintHints':neighbours[uid],'supportProven':False,'state':'retained-pending','published':False,'aiCalls':0})
    for path,expected in metrics['inputHashes'].items():
        if digest((ROOT/path).read_bytes())!=expected:raise ValueError('Input changed during context pass: '+path)
    payload={'selectionSHA256':digest((DOC/'selection.json.gz').read_bytes()),'metricsSHA256':digest((DOC/'metrics.json').read_bytes()),'scriptSHA256':digest(Path(__file__).read_bytes())}
    job_id=jobs.enqueue(PASS,STAGE,payload);job=jobs.claim(PASS,receipt['owner'],[STAGE],lease_seconds=1800)
    assert job and job['id']==job_id
    report={'batch':BATCH,'pass':PASS,'jobId':job_id,'models':len(rows),'alreadyInstalledFromBatch':len(frozen['previousInstalled']),'newlyInstalled':0,'remaining':len(rows),'routes':dict(Counter(r['route'] for r in rows)),'reasonCounts':dict(Counter(reason for r in rows for reason in r['currentReasons'])),'rows':rows,'nativeSources':sorted(sources,key=lambda s:s['sheet']),'sourceErrors':source_errors,'inputHashes':metrics['inputHashes'],'pipeline':payload,'seconds':round(time.monotonic()-start,3),'aiCalls':0,'geometryChanges':0,'publication':False,'qualification':'Diagnostic pass only. Original source TIN compared with current rendered terrain; overlapping footprints are hints, not accepted support. No acceptance thresholds relaxed or review/progress credit granted.'}
    save(DOC/'results.json.gz',report)
    evidence={'path':str((DOC/'results.json.gz').relative_to(ROOT)),'sha256':digest((DOC/'results.json.gz').read_bytes())};stored_result={**report,'evidence':evidence}
    with connect() as c:
        c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));group=reservations._current(c,receipt)
        assert group and {'building:'+r['uid'] for r in rows}<=set(group['resources'])
        count=c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(stored_result),job_id,job['owner'],job['token'])).rowcount
        assert count==1
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY');stored=c.execute("SELECT result FROM astra_modelling.jobs WHERE id=%s AND status='complete'",(job_id,)).fetchone()[0]
    assert stored==stored_result
    save(DOC/'neon-sync.json',{'jobId':job_id,'verifiedRows':len(rows),'exactResultMatch':True,'sourceReservationFenced':True,'modelReviewWrites':0})
    summary={k:v for k,v in report.items() if k not in ('rows','nativeSources','inputHashes')};save(DOC/'summary.json',summary);print(json.dumps(summary),flush=True)
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true');args=parser.parse_args();sys.exit(execute() if args.execute else prepare())
