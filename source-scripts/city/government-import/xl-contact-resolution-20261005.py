"""Resolve actual XL terrain blockers using pinned original terrain and model bytes.

Fresh continuation; historical diagnostic reports are inputs, never overwritten.
No architectural AI, geometry editing, acceptance bypass or automatic publication.
"""
import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import Polygon, box
from run import ROOT, HERE, read, save, digest, reservations
from dependency_preflight import from_catalogues

BATCH = 'government-xl-contact-resolution-20261005'
BASE = ROOT / 'docs/astra-city/government-import/government-xl-next-100-20261005'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH
SOURCE = HERE / 'local/government-xl-50-second-20260913/sheets/11-NW-19A'
UIDS = ['landsd/228219:0', 'landsd/250559:0']


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def sha(path):
    return digest(Path(path).read_bytes())


def rel(path):
    return str(Path(path).resolve().relative_to(ROOT))


def call(args, allowed=(0,)):
    status = subprocess.run(args, cwd=ROOT).returncode
    assert status in allowed, (args, status)
    assert reservations.owns(read(LOCAL / 'reservation.json')), 'Source ownership lost'


def start():
    rows = [r for r in read(BASE / 'check-selection.json.gz')['rows'] if r['uid'] in UIDS]
    assert len(rows) == len(UIDS)
    claim = reservations.claim('codex-xl-contact-' + str(uuid.uuid4()),
                               ['building:' + u for u in UIDS] + ['terrain-patch:' + u for u in UIDS], batch=BATCH)
    assert claim['ok'], claim
    save(LOCAL / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run',
          '--lease-file', str(LOCAL / 'reservation.json'), '--', sys.executable, __file__, 'owned',
          'lim-por-yen' if len(UIDS)==1 else 'two'], cwd=ROOT, check=True)


def owned():
    assert reservations.owns(read(LOCAL / 'reservation.json'))
    selected = read(BASE / 'check-selection.json.gz')
    assert sha(ROOT / '3d-viewer/city/data/manifest.json') == selected['manifestSHA256']
    context = {r['uid']: r for r in read(BASE / 'context.json.gz')['rows']}
    rows = [r for r in selected['rows'] if r['uid'] in UIDS]
    direct = module('contact_identity', 'xl-remaining-direct.py')
    second = module('contact_terrain', 'xl-second-pass.py')
    second.LOCAL = LOCAL
    patches = module('contact_patch', 'native_patch_resolution.py')
    final = module('contact_foundation', 'xl-final-script-pass.py')
    parent = read(ROOT / '3d-viewer/city/data/terrain.json')
    for r in rows:
        assert r['currentReview'] is None, 'Existing review needs explicit resolution'
        assert sha(ROOT / '3d-viewer' / r['source']['tile']) == r['source']['tileSHA256']
        assert direct.identity_clear(context[r['uid']]['identity'])
        for path, pinned in context[r['uid']]['neighbourTileHashes'].items():
            assert sha(ROOT / '3d-viewer' / path) == pinned
        raw = (ROOT / r['candidate']['path']).read_bytes()
        assert digest(raw) == r['sourceSHA256']
        dest = LOCAL / 'assets' / (r['sourceSHA256'] + '.glb.gz')
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
        r['candidate']['path'] = rel(dest)
    catalogue = read(HERE / 'accepted/government-xxl-20260911/catalogue.json')
    catalogue.update(area=BATCH, models=[r['candidate']['entry'] for r in rows], counts={'packedModels':len(rows)})
    save(LOCAL / 'catalogue.json', catalogue)
    save(LOCAL / 'catalogue-index.json', {'models':len(rows), 'catalogues':['catalogue.json']})
    save(LOCAL / 'source-forms.json', {r['uid']:r['source'] for r in rows})
    save(DOC / 'selection.json.gz', {**selected, 'batch':BATCH, 'rows':rows})
    dependencies = from_catalogues(ROOT / '3d-viewer/city/data/manifest.json', [LOCAL / 'catalogue.json'])
    save(DOC / 'dependency-preflight.json', dependencies)
    assert not any(r['blockers'] for r in dependencies['rows'])
    world = [r['native']['model']['worldBounds'] for r in rows]
    rects = [second.resolution.rectangle_for(b, parent) for b in world]
    cells = [min(r[0] for r in rects),min(r[1] for r in rects),max(r[2] for r in rects),max(r[3] for r in rects)]
    bounds = second.resolution.extent(cells, parent)
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    overlaps = [p['url'] for p in manifest['terrainPatches']
                if second.resolution.terrain.overlap(cells, read(ROOT / '3d-viewer' / p['url'])['coarseCells'])]
    assert not overlaps, ('Requires retained native patch handling', overlaps)
    proof = read(SOURCE / 'original/download.json')
    assert proof['directorySHA256'] == read(SOURCE / 'directory/result.json')['directorySHA256']
    files = []
    for entry in proof['entries']:
        if entry['name'].startswith('TERRAIN') and entry['name'].endswith(('.gltf','.bin')):
            p = SOURCE / 'terrain' / entry['name']
            assert sha(p) == entry['sha256']
            files.append({'path':rel(p),'sha256':sha(p)})
    native = np.concatenate([second.terrain_triangles(p) for p in sorted((SOURCE / 'terrain').rglob('*.gltf'))])
    native = native[(native[:,:,0].max(axis=1)>=bounds[0])&(native[:,:,0].min(axis=1)<=bounds[2])&
                    (native[:,:,2].max(axis=1)>=bounds[1])&(native[:,:,2].min(axis=1)<=bounds[3])]
    assert len(native)
    models = {r['uid']:second.glb_triangles(r) for r in rows}
    projection = shapely.union_all([shapely.union_all(shapely.polygons(t[:,:,[0,2]])) for t in models.values()])
    low = native[:,:,1].min(axis=1) < 1.2
    low_under_model = (float(shapely.union_all(shapely.polygons(native[low][:,:,[0,2]])).intersection(projection).area)
                       if low.any() else 0.0)
    # Existing source-terrain policy: omit only peripheral below-clamp facets.
    # If they intersect a source model, preserve them and keep every terrain gate.
    if low.any() and low_under_model < 1e-6:
        native = native[~low]
    retain_below = bool(low.any() and low_under_model >= 1e-6)
    core = [min(b[0][0] for b in world)-1,min(b[0][2] for b in world)-1,
            max(b[1][0] for b in world)+1,max(b[1][2] for b in world)+1]
    used = [{'sheet':'11-NW-19A','revision':proof['revisionDate'],'sourceETag':proof['sourceETag'],
             'directorySHA256':proof['directorySHA256'],'sourceFiles':files}]
    validator = second.resolution.validate_patch
    second.resolution.validate_patch = lambda *_: None
    try:
        patch = second.resolution.make_patch({'uids':UIDS,'cells':cells},parent,native,used,
                    native_core=core,terrain_triangle_budget=100000,allow_native_below_clamp=retain_below)
    finally:
        second.resolution.validate_patch = validator
    patch_path = LOCAL / (patch['id'] + '.json')
    sampler = second.resolution.terrain.fine.DemSampler(parent,rendered=True)
    protected_gap = patches.projected_context(patch,bounds)[2].intersection(projection)
    fill = (patches.fill_narrow_source_seam(patch,bounds,projection,sampler,tolerance=.02)
            if protected_gap.area > 1e-6 else patches.fill_parent_only_holes(patch,parent,bounds,projection,sampler))
    remaining = float(patches.projected_context(patch,bounds)[2].area)
    maximum = max(.25,(bounds[2]-bounds[0])*(bounds[3]-bounds[1])*1e-3)
    assert remaining <= maximum
    if remaining > 1e-8:
        patch['nativeMesh']['source']['numericalCoverageGap'] = {'policy':'parent-grid-fallback',
                'measuredAreaM2':remaining,'maximumAreaM2':maximum,'maximumFraction':1e-3}
    patch['nativeMesh']['source']['finalBoundarySnap'] = patches.snap_boundary_to_parent(patch,bounds,sampler)
    save(patch_path,patch)
    if patches.projected_context(patch,bounds)[3] > 1e-8:
        patches.approve_original_overlap(patch,patch_path,DOC/'native-overlap.json',files)
        patches.finalize_overlap_evidence(patch,DOC/'native-overlap.json')
    validator(patch,parent)
    save(patch_path,patch)
    patch_row = {'path':rel(patch_path),'sha256':sha(patch_path),'uids':UIDS,'bounds':bounds,
                 'triangles':len(patch['nativeMesh']['index'])//3}
    save(DOC/'terrain-candidates.json',[patch_row])
    save(DOC/'terrain.json',{'patch':patch_row,'parentHoleFill':fill,'sourceFiles':files,
        'lowSourceIntersectionWithModelM2':low_under_model,'retainSourceBelowClamp':retain_below,'modelGeometryChanges':0})
    live = {e['uid'] for url in manifest['officialModelCatalogues'] for e in read(ROOT/'3d-viewer'/url)['models']}
    neighbours = final.load_forms(bounds)
    save(DOC/'neighbour-inputs.json.gz',{'rows':[{'building':b,'patchIndexes':[0],
                'existingNative':b['uid'] in live or bool(b.get('modelGeometry'))} for b,_,_ in neighbours],
        'inputHashes':{rel(ROOT/'3d-viewer'/url):sha(ROOT/'3d-viewer'/url) for _,_,url in neighbours},
        'candidateIds':UIDS,'patches':[patch_row]})
    call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),
          '--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),
          '--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
    call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),
          '--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),
          '--out',rel(DOC/'validation.json')],(0,1))
    call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/'])
    call(['node',str(HERE/'check-native-neighbours.mjs'),rel(DOC)+'/'])
    runtime = {r['uid']:r for r in read(LOCAL/'runtime-geometry.json.gz')['rows']}
    foundations = []
    for r in rows:
        geometry = runtime[r['uid']]
        triangles = np.asarray(geometry['position']).reshape(-1,3)[np.asarray(geometry['index']).reshape(-1,3)]
        terrain = np.asarray(geometry['drawnGroundGeometry']).reshape(-1,3,3)
        b = r['source']['building']
        f = final.foundation_context(triangles,terrain,Polygon(b['rings'][0],b['rings'][1:]))
        foundations.append({'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'foundation':f,
            'strictFoundationAccepted':f['completeTerrainTriangles']==f['triangles'] and
                not f['fullyBuriedUpwardTriangles'] and f['fullyBuriedAreaFraction']==0})
    save(DOC/'foundation.json',{'rows':foundations,'modelGeometryChanges':0})
    print(json.dumps({'foundations':[{k:r[k] for k in ('uid','strictFoundationAccepted')} for r in foundations],
                      'neighbours':len(neighbours),'installed':0}),flush=True)


def preserve_start():
    inputs = read(DOC/'neighbour-inputs.json.gz')
    failed = [r['uid'] for r in read(DOC/'neighbour-checks.json')['rows'] if r['reasons']]
    assert UIDS == ['landsd/250559:0'] and failed == ['landsd/270705:0']
    claim = reservations.claim('codex-xl-contact-preserve-'+str(uuid.uuid4()),
        ['building:'+u for u in UIDS+failed]+['terrain-patch:'+u for u in UIDS],batch=BATCH)
    assert claim['ok'],claim
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run',
        '--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,
        'preserve-owned','lim-por-yen'],cwd=ROOT,check=True)


def preserve_owned():
    assert reservations.owns(read(LOCAL/'reservation.json'))
    second = module('preserve_terrain','xl-second-pass.py')
    patches = module('preserve_native','native_patch_resolution.py')
    final = module('preserve_foundation','xl-final-script-pass.py')
    second.LOCAL=LOCAL
    selection=read(DOC/'selection.json.gz');row=selection['rows'][0]
    assert sha(ROOT/'3d-viewer/city/data/manifest.json')==selection['manifestSHA256']
    original=read(DOC/'terrain.json')['patch'];assert sha(ROOT/original['path'])==original['sha256']
    patch=read(ROOT/original['path']);bounds=original['bounds'];parent=read(ROOT/'3d-viewer/city/data/terrain.json')
    inputs=read(DOC/'neighbour-inputs.json.gz')
    for path,pinned in inputs['inputHashes'].items():assert sha(ROOT/path)==pinned
    b=next(r['building'] for r in inputs['rows'] if r['building']['uid']=='landsd/270705:0')
    protected=Polygon(b['rings'][0],b['rings'][1:]).buffer(.01,join_style='mitre')
    model=second.glb_triangles(row)
    projection=shapely.union_all(shapely.polygons(model[:,:,[0,2]]))
    assert protected.intersection(projection).area<1e-8,'Neighbour intersects source'
    sampler=second.resolution.terrain.fine.DemSampler(parent,rendered=True)
    proof=patches.preserve_parent_under_projection(patch,bounds,protected,sampler)
    proof.update(uid=b['uid'],distanceFromSourceM=float(protected.distance(projection)))
    patches.fill_parent_only_holes(patch,parent,bounds,projection,sampler)
    patch['nativeMesh']['source']['finalBoundarySnap']=patches.snap_boundary_to_parent(patch,bounds,sampler)
    target=LOCAL/'neighbour-protected'/Path(original['path']).name
    save(target,patch)
    if patches.projected_context(patch,bounds)[3]>1e-8:
        patches.approve_original_overlap(patch,target,DOC/'protected-overlap.json',read(DOC/'terrain.json')['sourceFiles'])
        patches.finalize_overlap_evidence(patch,DOC/'protected-overlap.json')
    else:patch['nativeMesh'].pop('sourceOverlap',None)
    second.resolution.validate_patch(patch,parent);save(target,patch)
    revised={**original,'path':rel(target),'sha256':sha(target),'triangles':len(patch['nativeMesh']['index'])//3}
    save(DOC/'neighbour-preservation.json',{'originalPatch':original,'finalPatch':revised,
        'proof':proof,'sourceProjectionIntersectionM2':0,'modelGeometryChanges':0,'scriptExternalAICalls':0})
    save(DOC/'terrain-candidates.json',[revised]);inputs['patches']=[revised];save(DOC/'neighbour-inputs.json.gz',inputs)
    call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),
        '--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),
        '--out',rel(DOC/'protected-metrics.json'),'--geometry-out',rel(LOCAL/'protected-runtime-geometry.json.gz')])
    call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),
        '--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),
        '--out',rel(DOC/'protected-validation.json')],(0,1))
    call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/'])
    call(['node',str(HERE/'check-native-neighbours.mjs'),rel(DOC)+'/'])
    runtime=read(LOCAL/'protected-runtime-geometry.json.gz')['rows'][0]
    tri=np.asarray(runtime['position']).reshape(-1,3)[np.asarray(runtime['index']).reshape(-1,3)]
    terrain=np.asarray(runtime['drawnGroundGeometry']).reshape(-1,3,3)
    b=row['source']['building'];f=final.foundation_context(tri,terrain,Polygon(b['rings'][0],b['rings'][1:]))
    save(DOC/'protected-foundation.json',{'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'foundation':f,
        'strictFoundationAccepted':f['completeTerrainTriangles']==f['triangles'] and
            not f['fullyBuriedUpwardTriangles'] and f['fullyBuriedAreaFraction']==0})
    print(json.dumps({'neighbourPreserved':proof['uid'],'distanceFromSourceM':proof['distanceFromSourceM'],
                      'fullyBuriedTriangles':f['fullyBuriedTriangles']}),flush=True)


if __name__ == '__main__':
    if 'lim-por-yen' in sys.argv:
        BATCH += '-lim-por-yen'
        DOC = DOC / 'lim-por-yen'
        LOCAL = LOCAL / 'lim-por-yen'
        UIDS = ['landsd/250559:0']
    if 'preserve-owned' in sys.argv:preserve_owned()
    elif 'preserve' in sys.argv:preserve_start()
    else:owned() if 'owned' in sys.argv else start()
