"""Bounded five-independent-original physical fork; all upstream physical gates retained.
Source identity callback differs; no source meshes/poses or acceptance thresholds change.
Upstream fork: xl-routed-cell-contact-resolution.py, source hash recorded by orchestrator.
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
PARENT_URL = 'city/data/terrain.json'
NESTED_PARENT = False
ADJACENT_SOURCES = []
RETAIN_NATIVE_URL = None
ALLOW_BASIC_TERRAIN_TARGETS = False
RETAIN_NATIVE_MODEL_REGIONS_ONLY = False
OWNED_IDENTITY_PATHS = None


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
    parent_path = ROOT / '3d-viewer' / PARENT_URL
    parent = read(parent_path)
    for r in rows:
        assert r['currentReview'] is None, 'Existing review needs explicit resolution'
        assert sha(ROOT / '3d-viewer' / r['source']['tile']) == r['source']['tileSHA256']
        from tung_sing_flat_two_original_collection_identity_v3_20261010 import verify_files, POLICY
        owned_identity = verify_files(r, context[r['uid']], LOCAL / 'identity-recheck')
        assert owned_identity['passed'], owned_identity['reasons']
        identity_path = (DOC / 'owned-source-identity.json' if OWNED_IDENTITY_PATHS is None
                         else OWNED_IDENTITY_PATHS[r['uid']])
        assert owned_identity == read(identity_path), 'Positive identity proof changed'
        assert owned_identity['policy'] == POLICY
        save(DOC / 'owned-source-identity-contact.json', owned_identity)
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
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
    candidate_dir=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-parent-residual-gap-candidate-20261010'
    candidate_path=candidate_dir/'candidate-single-native-residual-surface.json'
    raw_candidate=read(candidate_path);patch=read(candidate_path)
    diagnostic=read(candidate_dir/'diagnostic.json.gz')
    for path,pinned in diagnostic['inputHashes'].items():assert sha(ROOT/path)==pinned,path
    assert all(r['proof']['exactProjectionCovered'] for r in diagnostic['completeFailedSourceFacetRechecks'])
    assert diagnostic['modelGeometryChanges']==0 and diagnostic['physicalAccepted'] is False
    old_url='city/data/government-native-163705-0.json';old_path=ROOT/'3d-viewer'/old_url;old=read(old_path)
    assert diagnostic['inputHashes'][rel(old_path)]==sha(old_path)
    retained_uids=old['meta']['targetUids'];assert set(patch['meta']['targetUids'])==set(retained_uids)|set(UIDS)
    assert len(patch['nativeMesh']['index'])//3==diagnostic['combinedFacets']<=100000
    assert not patch.get('patches') and not patch.get('hydro')
    parent=read(ROOT/'3d-viewer/city/data/terrain.json');bounds=patches._patch_bounds(patch)
    source_context=read(ROOT/'docs/astra-city/government-import/government-xl-tung-sing-original-pair-source-tin-context-20261010/complete-original-source-tin.json.gz')
    used=[];files=[]
    for source in source_context['completeSourceReceipts']:
        cache=ROOT/source['cache'];proof=read(cache/'original/download.json')
        assert proof['directorySHA256']==source['directorySHA256']==read(cache/'directory/result.json')['directorySHA256']
        sf=[]
        for f in source['terrainFiles']:
            p=cache/'terrain'/f['name'];assert sha(p)==f['sha256']
            sf.append({'path':rel(p),'sha256':sha(p)})
        used.append({'sheet':source['sheet'],'revision':proof['revisionDate'],'sourceETag':proof['sourceETag'],'directorySHA256':proof['directorySHA256'],'sourceFiles':sf});files.extend(sf)
    patch['meta']['source']['nativeSources']=used
    patch['meta']['source']['policy']='Original authenticated terrain core/actual-native-parent transition plus separately bound finite-parent residual candidate; source building bytes/poses unchanged. Complete exact outside parent surface, finite gap, source/current actor and runtime gates independent.'
    patch['nativeMesh']['source']['triangleBudget']=100000
    audit_inputs=[candidate_path,candidate_dir/'diagnostic.json.gz',HERE/'xl-tung-sing-parent-residual-gap-candidate-20261010.py',old_path]
    for p in audit_inputs:files.append({'path':rel(p),'sha256':sha(p)})
    patch_path=LOCAL/'government-native-53800-0-flat.json';save(patch_path,patch)
    remaining=float(patches.projected_context(patch,bounds)[2].area)
    save(DOC/'raw-complete-domain.json',{'bounds':bounds,'rawRemainingAreaM2':remaining,'sourceParentResidualCandidate':rel(candidate_path),'originalRawGapAreaM2':sum(r['rawGapAreaM2'] for r in diagnostic['allRawGapPieceDispositions']),'noGeometryThresholdChanged':True})
    if patches.projected_context(patch,bounds)[3]>1e-8:
        patches.approve_original_overlap(patch,patch_path,DOC/'native-overlap.json',files);patches.finalize_overlap_evidence(patch,DOC/'native-overlap.json')
    second.resolution.validate_patch(patch,parent);save(patch_path,patch)
    assert patch['nativeMesh']['position']==raw_candidate['nativeMesh']['position'] and patch['nativeMesh']['index']==raw_candidate['nativeMesh']['index']
    patch_row={'path':rel(patch_path),'sha256':sha(patch_path),'uids':UIDS,'bounds':bounds,'triangles':len(patch['nativeMesh']['index'])//3,'replaces':{'url':old_url,'sha256':sha(old_path),'retainedUids':retained_uids}}
    save(DOC/'terrain-candidates.json',[patch_row]);save(DOC/'terrain.json',{'patch':patch_row,'sourceFiles':files,'modelGeometryChanges':0,'candidateTerrainTriangulationChanged':True,'governmentMeshGeometryChanged':False,'sourceParentResidualCandidate':rel(candidate_path)})
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
