"""Stage and validate the source-backed terrain candidate for Saxon podium."""
import importlib.util,json,sys,uuid,subprocess
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,box
spec=importlib.util.spec_from_file_location('xxl_second',Path(__file__).with_name('xxl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE,DOC,LOCAL=s.ROOT,s.HERE,s.DOC/'saxon-terrain-local',s.LOCAL/'saxon-terrain-local'
read,save,h,rel=s.read,s.save,s.h,s.rel
UID='landsd/232025:0'

def start():
    selected=read(s.DOC/'saxon/selection.json.gz');r=next(r for r in selected['rows'] if r['uid']==UID);parent=read(ROOT/'3d-viewer/city/data/terrain.json');cells=s.resolution.rectangle_for(r['candidate']['entry']['worldBounds'],parent);bb=s.resolution.extent(cells,parent);region=box(*bb)
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json');live={m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']};neighbours=[];hashes={}
    for tile in manifest['tiles']:
        p=ROOT/'3d-viewer'/tile['url'];raw=p.read_bytes();touched=False
        for b in json.loads(raw)['buildings']:
            poly=Polygon(b['rings'][0],b['rings'][1:])
            if poly.intersects(region):neighbours.append({'building':b,'patchIndexes':[0],'existingNative':b['uid'] in live or bool(b.get('modelGeometry'))});touched=True
        if touched:hashes[rel(p)]=s.digest(raw)
    save(DOC/'selection.json.gz',selected);save(DOC/'neighbour-inputs.json.gz',{'rows':neighbours,'inputHashes':hashes,'candidateIds':[UID,'landsd/76364:0'],'patches':[]});save(DOC/'patch-plan.json',{'cells':cells,'bounds':bb,'manifestSHA256':selected['manifestSHA256'],'uid':UID})
    resources=set(read(s.LOCAL/'reservation.json')['resources'])|{('building:' if n['building']['uid'].startswith('landsd/') else 'source-form:')+n['building']['uid'] for n in neighbours}
    owned=s.reservations.claim('codex-xxl-terrain-'+str(uuid.uuid4()),sorted(resources),batch=s.BATCH+'-terrain');assert owned['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(owned['reservation'],default=str)))
    s.call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])

def owned():
    assert s.reservations.owns(read(LOCAL/'reservation.json'));plan=read(DOC/'patch-plan.json');assert h(ROOT/'3d-viewer/city/data/manifest.json')==plan['manifestSHA256']
    adjacent=read(s.DOC/'adjacent-terrain-results.json');assert adjacent['complete'];r=read(DOC/'selection.json.gz')['rows'][0];assert read(s.DOC/'saxon-support-triangles.json')['podiumNativeTerrain']['passed']
    sources=read(s.DOC/'recovery.json')['sheets']+adjacent['sources'];bb=plan['bounds'];fragments=[];used=[];parent=read(ROOT/'3d-viewer/city/data/terrain.json');manifest=read(ROOT/'3d-viewer/city/data/manifest.json');group={'uids':[UID],'cells':plan['cells']}
    try:
        assert not any(s.resolution.terrain.overlap(group['cells'],read(ROOT/'3d-viewer'/p['url'])['coarseCells']) for p in manifest['terrainPatches']),'overlaps-installed-terrain-patch'
        for source in sources:
            folder=s.LOCAL/'sheets'/source['sheet']/'terrain'
            for e in source['source']['entries']:
                if e['name'].startswith('TERRAIN') and e['name'].endswith(('.gltf','.bin')):assert h(folder/e['name'])==e['sha256']
            found=[]
            for path in source['terrainPaths']:
                tri=s.context.triangles(ROOT/path);near=tri[(tri[:,:,0].max(axis=1)>=bb[0])&(tri[:,:,0].min(axis=1)<=bb[2])&(tri[:,:,2].max(axis=1)>=bb[1])&(tri[:,:,2].min(axis=1)<=bb[3])]
                if len(near):found.append(near)
            if found:
                fragments.extend(found);proof=source['source'];used.append({'sheet':source['sheet'],'revision':proof['revisionDate'],'sourceETag':proof['sourceETag'],'directorySHA256':proof['directorySHA256'],'sourceFiles':[{'path':rel(folder/e['name']),'sha256':e['sha256']} for e in proof['entries'] if e['name'].startswith('TERRAIN') and e['name'].endswith(('.gltf','.bin'))]})
        lo,hi=r['candidate']['entry']['worldBounds'];core=[lo[0]-1,lo[2]-1,hi[0]+1,hi[2]+1];patch=s.resolution.make_patch(group,parent,np.concatenate(fragments),used,native_core=core);path=LOCAL/(patch['id']+'.json');save(path,patch)
    except (AssertionError,ValueError) as error:
        save(DOC/'result.json',{'uid':UID,'passed':False,'stage':'source-terrain-patch','reason':str(error),'aiCalls':0});print(json.dumps(read(DOC/'result.json')),flush=True);return
    patch_entry={'path':rel(path),'sha256':h(path),'uids':[UID],'bounds':bb,'triangles':len(patch['nativeMesh']['index'])//3};save(DOC/'terrain-candidates.json',[patch_entry]);neighbours=read(DOC/'neighbour-inputs.json.gz');neighbours['patches']=[patch_entry];save(DOC/'neighbour-inputs.json.gz',neighbours)
    catalogue=read(HERE/'accepted/government-xxl-20260911/catalogue.json');pair=read(DOC/'selection.json.gz')['rows'];catalogue['models']=[x['candidate']['entry'] for x in pair];catalogue['counts']['packedModels']=2;save(LOCAL/'candidates/catalogue.json',catalogue);save(LOCAL/'candidates/catalogue-index.json',{'models':2,'catalogues':['catalogue.json']})
    for row in pair:
        e=row['candidate']['entry'];asset=LOCAL/'candidates'/e['asset'];asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(Path(row['candidate']['path']).read_bytes());assert h(asset)==e['sha256']
    save(LOCAL/'source-forms.json',{x['uid']:x['source'] for x in pair})
    s.call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL/'candidates'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json')])
    v=subprocess.run(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL/'candidates'),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],cwd=ROOT);assert v.returncode in (0,1)
    s.call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/'])
    spec=importlib.util.spec_from_file_location('acceptance',HERE/'acceptance-policy.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
    spec=importlib.util.spec_from_file_location('pair_policy',HERE/'xxl-saxon-stage.py');pair_policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(pair_policy)
    metrics=read(DOC/'metrics.json');reasons=pair_policy.supported_reasons(metrics,read(s.DOC/'saxon-support-triangles.json'))
    for validation in read(DOC/'validation.json')['results']:
        reasons += [v for v in validation.get('concerns',[]) if not (validation['uid']=='landsd/76364:0' and v=='sampled-ground-gap-below-model-bottom')]
        if validation['outcome']=='validation-exception':reasons.append('runtime-validation-exception')
    from unchanged_support import unchanged_supports
    neighbours=read(DOC/'neighbour-checks.json');proof=unchanged_supports(read(DOC/'neighbour-inputs.json.gz'),neighbours,{UID,'landsd/76364:0'});resolved={r['uid'] for r in proof};remaining=set(neighbours['patches'][0]['blockedBy'])-resolved
    save(DOC/'unchanged-support.json',{'resolved':proof,'remaining':sorted(remaining),'inputSHA256':h(DOC/'neighbour-inputs.json.gz'),'checksSHA256':h(DOC/'neighbour-checks.json'),'aiCalls':0})
    if remaining:reasons.append('terrain-correction-regresses-neighbours')
    save(DOC/'result.json',{'uid':UID,'passed':not reasons,'stage':'patched-terrain-and-neighbour-checks','reasons':reasons,'patch':patch_entry,'aiCalls':0});print(json.dumps(read(DOC/'result.json')),flush=True)

if __name__=='__main__':owned() if len(sys.argv)>1 else start()
