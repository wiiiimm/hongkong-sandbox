"""Resolve actual XL terrain blockers using pinned original terrain and model bytes.

Fresh continuation; historical diagnostic reports are inputs, never overwritten.
Positive original government ownership/GeoRef identity replaces the roof area ratio.
All terrain, foundation, neighbour and runtime guards are preserved. No automatic publication.
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
PARENT_URL = 'city/data/terrain-government-xl-caine-road-original-pair-installed-v2-20261010.json'
NESTED_PARENT = True
ADJACENT_SOURCES = []
RETAIN_NATIVE_URLS = []
ALLOW_BASIC_TERRAIN_TARGETS = False
RETAIN_NATIVE_MODEL_REGIONS_ONLY = False


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
    accelerated=module('source_local_exact_builder','resolve-pass-indexed-parent-clipping.py')
    second.resolution.make_patch=accelerated.make_patch
    second.LOCAL = LOCAL
    patches = module('contact_patch', 'native_patch_resolution.py')
    final = module('contact_foundation', 'xl-final-script-pass.py')
    parent_path = ROOT / '3d-viewer' / PARENT_URL
    parent = read(parent_path)
    from copy import deepcopy
    original_parent=deepcopy(parent)
    from one_peking_specific_parent_census_v4_20261010 import census,reconstructed_numeric_equal
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
    assert sum(p['url']==PARENT_URL for p in manifest['terrainPatches'])==1
    all_catalogue_rows=[];preflight_hashes={rel(parent_path):sha(parent_path),rel(ROOT/'3d-viewer/city/data/manifest.json'):sha(ROOT/'3d-viewer/city/data/manifest.json')}
    for url in manifest['officialModelCatalogues']:
        catalogue_path=ROOT/'3d-viewer'/url;catalogue=read(catalogue_path)
        preflight_hashes[rel(catalogue_path)]=sha(catalogue_path)
        for entry in catalogue['models']:
            if entry['uid'] in __import__('one_peking_specific_parent_census_v4_20261010').EXPECTED_TARGETS:
                asset=catalogue_path.parent/entry['asset'];assert sha(asset)==entry['sha256']
                preflight_hashes[rel(asset)]=sha(asset)
            all_catalogue_rows.append(entry)
    parent_forms=final.load_forms(patches._patch_bounds(original_parent))
    for _,_,url in parent_forms:preflight_hashes[rel(ROOT/'3d-viewer'/url)]=sha(ROOT/'3d-viewer'/url)
    target_census=census(original_parent,all_catalogue_rows,[b for b,_,_ in parent_forms])
    old_proposal_doc=ROOT/'docs/astra-city/government-import/government-xl-one-peking-two-original-retained-hullett-child-current-physical-v3-20261010'
    old_proposal_row=read(old_proposal_doc/'terrain-candidates.json')[0]
    comparison_proposal_path=ROOT/old_proposal_row['path'];assert comparison_proposal_path.is_file() and sha(comparison_proposal_path)==old_proposal_row['sha256']
    comparison_proposal=read(comparison_proposal_path)
    preflight_hashes[rel(comparison_proposal_path)]=sha(comparison_proposal_path)
    preflight_hashes[rel(old_proposal_doc/'terrain-candidates.json')]=sha(old_proposal_doc/'terrain-candidates.json')
    for source in [SOURCE,*ADJACENT_SOURCES]:
        download=source/'original/download.json';directory=source/'directory/result.json'
        proof=read(download);assert proof['directorySHA256']==read(directory)['directorySHA256']
        preflight_hashes[rel(download)]=sha(download);preflight_hashes[rel(directory)]=sha(directory)
        for item in proof['entries']:
            if item['name'].startswith('TERRAIN') and item['name'].endswith(('.gltf','.bin')):
                source_file=source/'terrain'/item['name'];assert sha(source_file)==item['sha256']
                preflight_hashes[rel(source_file)]=sha(source_file)
    save(DOC/'complete-parent-prerequisite-census.json',dict(target_census,inputHashes=preflight_hashes,missingNeighbourInputWillBeReconstructed=True,oldV2ProposalNotHistoricallyReceiptBound=True))
    old_children=[c for c in parent.get('patches',[]) if c['id']=='government-native-central-hullett-house']
    assert len(old_children)==1 and old_children[0]['meta']['targetUids']==['landsd/73140:0']
    old_child=deepcopy(old_children[0]);assert old_child.get('nativeMesh') and not old_child.get('patches')
    assert len(old_child['nativeMesh']['index'])//3==10675
    parent['patches']=[c for c in parent['patches'] if c['id']!=old_child['id']]
    assert len(parent['patches'])==9
    old_child_path=LOCAL/'exact-before-hullett-child.json';save(old_child_path,old_child)
    for r in rows:
        assert r['currentReview'] is None, 'Existing review needs explicit resolution'
        assert sha(ROOT / '3d-viewer' / r['source']['tile']) == r['source']['tileSHA256']
        from one_peking_pair_current_identity_v3_20261010 import verify_files, POLICY
        owned_identity = verify_files(r, context[r['uid']], LOCAL / 'identity-recheck')
        assert owned_identity['passed'], owned_identity['reasons']
        assert owned_identity == next(p for p in read(DOC / 'owned-source-identity.json')['rows'] if p['uid']==r['uid']), 'Positive identity proof changed'
        assert owned_identity['policy'] == POLICY
        save(DOC / ('owned-source-identity-contact-'+r['uid'].split('/')[1].replace(':','-')+'.json'), owned_identity)
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
    retained_patches=[]
    assert sorted(UIDS)==['landsd/233985:0','landsd/240487:0'] and not RETAIN_NATIVE_URLS and NESTED_PARENT
    old_cells=old_child['coarseCells'];cells=[min(cells[0],old_cells[0]),min(cells[1],old_cells[1]),max(cells[2],old_cells[2]),max(cells[3],old_cells[3])]
    retained_patches=[(rel(old_child_path),old_child)]
    for retained_url in RETAIN_NATIVE_URLS:
        retained_patch=read(ROOT/retained_url)
        assert retained_patch.get('nativeMesh') and not retained_patch.get('patches')
        retained_patches.append((retained_url,retained_patch))
        old_cells=retained_patch['coarseCells']
        cells=[min(cells[0],old_cells[0]),min(cells[1],old_cells[1]),
               max(cells[2],old_cells[2]),max(cells[3],old_cells[3])]
    for i,(_,old) in enumerate(retained_patches):
        for _,other in retained_patches[i+1:]:
            assert box(*patches._patch_bounds(old)).intersection(box(*patches._patch_bounds(other))).area<1e-8, 'Overlapping retained parents require a separate precedence proof'
    if NESTED_PARENT:
        cells=[max(0,cells[0]),max(0,cells[1]),min(parent['w']-1,cells[2]),min(parent['h']-1,cells[3])]
        assert 0<=cells[0]<cells[2]<parent['w'] and 0<=cells[1]<cells[3]<parent['h']
        assert not any(second.resolution.terrain.overlap(cells,c['coarseCells']) for c in parent.get('patches',[]))
    bounds = second.resolution.extent(cells, parent)
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    overlaps = []
    for p in manifest['terrainPatches']:
        if NESTED_PARENT and p['url']==PARENT_URL:continue
        if p['url'] in RETAIN_NATIVE_URLS:continue
        other=read(ROOT/'3d-viewer'/p['url']);g=other['meta']['georef']
        other_bounds=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(other['w']-1)*g['aE'],816500-g['bN']-(other['h']-1)*g['aN']]
        if box(*bounds).intersection(box(*other_bounds)).area>1e-8:overlaps.append(p['url'])
    assert not overlaps, ('Requires retained native patch handling', overlaps)
    proof = read(SOURCE / 'original/download.json')
    assert proof['directorySHA256'] == read(SOURCE / 'directory/result.json')['directorySHA256']
    files = []
    for entry in proof['entries']:
        if entry['name'].startswith('TERRAIN') and entry['name'].endswith(('.gltf','.bin')):
            p = SOURCE / 'terrain' / entry['name']
            assert sha(p) == entry['sha256']
            files.append({'path':rel(p),'sha256':sha(p)})
    used = [{'sheet':SOURCE.name,'revision':proof['revisionDate'],'sourceETag':proof['sourceETag'],
             'directorySHA256':proof['directorySHA256'],'sourceFiles':list(files)}]
    fragments=[second.terrain_triangles(p) for p in sorted((SOURCE / 'terrain').rglob('*.gltf'))]
    for adjacent in ADJACENT_SOURCES:
        adjacent_proof=read(adjacent/'original/download.json')
        assert adjacent_proof['directorySHA256']==read(adjacent/'directory/result.json')['directorySHA256']
        adjacent_files=[]
        for entry in adjacent_proof['entries']:
            if entry['name'].startswith('TERRAIN') and entry['name'].endswith(('.gltf','.bin')):
                path=adjacent/'terrain'/entry['name'];assert sha(path)==entry['sha256']
                adjacent_files.append({'path':rel(path),'sha256':sha(path)})
        fragments.extend(second.terrain_triangles(p) for p in sorted((adjacent/'terrain').rglob('*.gltf')))
        used.append({'sheet':adjacent.name,'revision':adjacent_proof['revisionDate'],
            'sourceETag':adjacent_proof['sourceETag'],'directorySHA256':adjacent_proof['directorySHA256'],
            'sourceFiles':adjacent_files})
        files.extend(adjacent_files)
    native = np.concatenate(fragments)
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
    if NESTED_PARENT:
        core=[max(bounds[0]+1,core[0]),max(bounds[1]+1,core[1]),min(bounds[2]-1,core[2]),min(bounds[3]-1,core[3])]
    validator = second.resolution.validate_patch
    second.resolution.validate_patch = lambda *_: None
    accelerated.validate_patch = second.resolution.validate_patch
    try:
        patch = second.resolution.make_patch({'uids':UIDS,'cells':cells},parent,native,used,
                    native_core=core,terrain_triangle_budget=1000000,allow_native_below_clamp=retain_below,
                    parent_url=PARENT_URL,parent_sha256=sha(parent_path))
    finally:
        second.resolution.validate_patch = validator
        accelerated.validate_patch = validator
    patch_path = LOCAL / (patch['id'] + '.json')
    sampler = second.resolution.terrain.fine.DemSampler(parent,rendered=True)
    intermediate_triangles=len(patch['nativeMesh']['index'])//3
    # Compute-only intermediate, never staged as a runtime candidate. Keep the
    # original source TIN beneath the full model projection plus a 1m margin.
    # Everywhere else use exact existing parent planes, then restore each
    # declared installed native patch's exact rendered facets below.
    current_region=box(*bounds).difference(projection.buffer(1,join_style='mitre'))
    assert current_region.intersection(projection).area<1e-8
    parent_preservation=patches.preserve_parent_under_projection(patch,bounds,current_region,sampler)
    parent_preservation.update(sourceProjectionIntersectionM2=float(current_region.intersection(projection).area),
        intermediateTriangles=intermediate_triangles,intermediateComputeCap=1000000,finalRuntimeCap=100000,
        sourceTerrainMarginM=1,modelGeometryChanges=0,publication=False)
    save(DOC/'source-local-parent-preservation.json',parent_preservation)
    retained_proofs=[]
    retained_replacements=[]
    all_declared_uids=set(UIDS)
    for retained_url,retained_patch in retained_patches:
        from rendered_patch_sampler import RenderedPatchSampler
        old_bounds=patches._patch_bounds(retained_patch)
        protected=box(*old_bounds).difference(projection.buffer(.1,join_style='mitre'))
        old_sampler=RenderedPatchSampler(retained_patch,sampler,
            second.resolution.terrain.fine.DemSampler(retained_patch,rendered=True))
        declared_uids=retained_patch['meta']['targetUids']
        entries={m['uid']:m for url in manifest['officialModelCatalogues']
                 for m in read(ROOT/'3d-viewer'/url)['models'] if m['uid'] in declared_uids}
        scope=None
        if ALLOW_BASIC_TERRAIN_TARGETS:
            from retained_terrain_scope import retained_scope
            scope=retained_scope(declared_uids,entries,[b for b,_,_ in final.load_forms(bounds)])
            retained_uids=scope['nativeUids']
            assert set(entries)==set(retained_uids)
        else:
            retained_uids=declared_uids
            assert set(entries)==set(retained_uids)
        if RETAIN_NATIVE_MODEL_REGIONS_ONLY:
            # Candidate only: preserve exact old terrain around every declared
            # installed mesh, then subject the fresh original TIN everywhere
            # else to all basic/native neighbour and complete source gates.
            protected=shapely.union_all([box(m['worldBounds'][0][0],m['worldBounds'][0][2],
                m['worldBounds'][1][0],m['worldBounds'][1][2]).buffer(.02,join_style='mitre')
                for m in entries.values()])
            assert protected.intersection(projection).area<1e-8, 'Retained source region overlaps new model'
        from exact_packed_world_geometry_20261009 import decode_original_world_triangles
        native_projections=[];native_refs=[]
        for entry in entries.values():
            catalogues=[ROOT/'3d-viewer'/url for url in manifest['officialModelCatalogues'] if any(m['uid']==entry['uid'] for m in read(ROOT/'3d-viewer'/url)['models'])]
            assert len(catalogues)==1;catalogue=catalogues[0];asset=catalogue.parent/entry['asset'];raw=asset.read_bytes();assert digest(raw)==entry['sha256']
            whole_native=decode_original_world_triangles(raw);assert len(whole_native)==entry['triangles']
            native_projections.append(shapely.union_all(shapely.polygons(whole_native[:,:,[0,2]])));native_refs.extend([{'path':rel(catalogue),'sha256':sha(catalogue)},{'path':rel(asset),'sha256':sha(asset)}])
        native_projection=shapely.union_all(native_projections);assert box(*old_bounds).covers(native_projection), 'Complete installed foreign source extends outside retained child'
        protected=protected.union(native_projection)
        save(DOC/'complete-installed-hullett-protected-projection.json',{'uid':'landsd/73140:0','completeOriginalFaces':32635,'sourceProjection':json.loads(shapely.to_geojson(native_projection)),'protectedProjection':json.loads(shapely.to_geojson(protected)),'sourceOriginalOverlapM2':float(native_projection.intersection(projection).area),'oldSourceRegionOverlapM2':float(protected.intersection(projection).area),'evidenceRefs':native_refs,'physicalAccepted':False,'qualification':'Actual entire installed foreign source silhouette retained within exact old child. Genuine new-source intersection remains explicit; no disjointness, ownership, collision or support exemption.'})
        preservation=patches.preserve_parent_under_projection(patch,bounds,protected,old_sampler,edge_sampler=sampler)
        preservation.update(supersededURL=retained_url,
            supersededSHA256=sha(ROOT/retained_url),retainedUids=retained_uids,
            sourceProjectionIntersectionM2=float(protected.intersection(projection).area),
            boundsOfEveryRetainedModelInsideProtectedProjection=True)
        if scope:preservation['declaredTargetScope']=scope
        preservation['retentionMode']='installed-model-regions' if RETAIN_NATIVE_MODEL_REGIONS_ONLY else 'complete-existing-terrain-outside-new-source'
        assert preservation['sourceProjectionIntersectionM2']>=0
        retained_proofs.append(preservation)
        retained_replacements.append({'url':retained_url,'sha256':sha(ROOT/retained_url),'retainedUids':retained_uids})
        for old_source in retained_patch['meta']['source']['nativeSources']:
            for source_file in old_source['sourceFiles']:
                assert sha(ROOT/source_file['path'])==source_file['sha256']
                if source_file not in files:files.append(source_file)
        all_declared_uids.update(declared_uids)
    patch['meta']['targetUids']=sorted(all_declared_uids)
    patch['nativeMesh']['source']['protectedParentProjections']=retained_proofs
    save(DOC/'retained-native-proof.json',{'parents':retained_proofs,'modelGeometryChanges':0,'publication':False})
    protected_gap = patches.projected_context(patch,bounds)[2].intersection(projection)
    save(LOCAL/'unfilled-patch.json',patch)
    source_union=shapely.union_all(shapely.polygons(native[:,:,[0,2]]))
    missing_source=projection.intersection(box(*bounds)).difference(source_union)
    save(DOC/'coverage-diagnostic.json',{'bounds':bounds,'core':core,
        'protectedGapM2':float(protected_gap.area),'sourceMissingUnderModelM2':float(missing_source.area),
        'protectedGapGeoJSON':json.loads(shapely.to_geojson(protected_gap)),
        'sourceMissingGeoJSON':json.loads(shapely.to_geojson(missing_source)),
        'publication':False,'modelGeometryChanges':0})
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
    final_triangles=len(patch['nativeMesh']['index'])//3
    save(DOC/'final-terrain-budget.json',{'intermediateTriangles':intermediate_triangles,
        'finalTriangles':final_triangles,'maximumTriangles':100000,'passed':final_triangles<=100000,
        'runtimeBudgetChanged':False,'modelGeometryChanges':0,'publication':False})
    assert final_triangles<=100000,'final-terrain-runtime-budget'
    validator(patch,parent)
    save(patch_path,patch)
    patch_row = {'path':rel(patch_path),'sha256':sha(patch_path),'uids':UIDS,'bounds':bounds,
                 'triangles':len(patch['nativeMesh']['index'])//3}
    from retained_original_nonheight_terrain_facets_20261010 import inventory,append_omitted
    original_inventory=inventory(old_child);patch,literal_retention=append_omitted(patch,old_child,original_inventory['completeRenderedWorldSHA256']);save(DOC/'literal-retained-hullett-nonheight-facets.json',literal_retention)
    save(patch_path,patch)
    if literal_retention['literalRetainedFaceDispositions'] and patches.projected_context(patch,bounds)[3]>1e-8:
        patch['nativeMesh'].pop('sourceOverlap',None)
        patches.approve_original_overlap(patch,patch_path,DOC/'native-overlap-after-literal-retention.json',files);patches.finalize_overlap_evidence(patch,DOC/'native-overlap-after-literal-retention.json')
    validator(patch,parent);save(patch_path,patch);patch_row.update(sha256=sha(patch_path),triangles=len(patch['nativeMesh']['index'])//3)
    final_triangles=len(patch['nativeMesh']['index'])//3
    save(DOC/'final-terrain-budget-after-literal-retention.json',{'finalTriangles':final_triangles,'maximumTriangles':100000,'passed':final_triangles<=100000,'afterLiteralRetentionAndOverlapAudit':True,'runtimeBudgetChanged':False,'modelGeometryChanges':0,'publication':False})
    assert final_triangles<=100000,'final-terrain-runtime-budget-after-literal-retention'
    assert len(retained_replacements)==1
    if NESTED_PARENT:
        nested=module('contact_nested_parent','xl-stage-central-nested.py');nested.DOC=DOC
        wrapper=nested.parent_with_nested(parent,patch)
        retained_audits=[]
        for original,retained in zip(parent.get('patches',[]),wrapper['patches']):
            assert original.get('elev')==retained.get('elev') and original.get('renderedElev')==retained.get('renderedElev')
            for key in ('position','index'):assert original.get('nativeMesh',{}).get(key)==retained.get('nativeMesh',{}).get(key)
            approval=retained.get('nativeMesh',{}).get('sourceOverlap')
            if approval:
                audit=read(approval['evidencePath'])
                for source_file in audit['source']['files']:assert sha(ROOT/source_file['path'])==source_file['sha256']
                actual_excess=patches.projected_context(retained,patches._patch_bounds(retained))[3]
                if abs(actual_excess-approval['measuredProjectedExcessM2'])>=1e-6:
                    before=approval['measuredProjectedExcessM2']
                    retained['nativeMesh'].pop('sourceOverlap')
                    raw_path=LOCAL/('retained-'+retained['id']+'.json');save(raw_path,retained)
                    fresh_audit=DOC/('float32-retained-'+retained['id']+'-native-overlap.json')
                    patches.approve_original_overlap(retained,raw_path,fresh_audit,audit['source']['files'])
                    patches.finalize_overlap_evidence(retained,fresh_audit)
                    retained_audits.append({'id':retained['id'],'oldProjectedExcessM2':before,
                        'float32ProjectedExcessM2':actual_excess,'evidence':rel(fresh_audit),
                        'positionsAndIndicesUnchanged':True,'toleranceChanged':False})
        assert wrapper['elev']==original_parent['elev'] and wrapper.get('renderedElev')==original_parent.get('renderedElev')
        assert len(wrapper['patches'])==10 and len(parent['patches'])==9
        validator(wrapper,read(ROOT/'3d-viewer/city/data/terrain.json'))
        wrapper_path=LOCAL/'terrain-central-with-sun-yat-sen.json';save(wrapper_path,wrapper)
        old_batch='government-xl-one-peking-two-original-retained-hullett-child-current-physical-v2-20261010'
        def verify_renewed_audit(before_child,after_child):
            audits=[]
            for child_value in [before_child,after_child]:
                approval=child_value['nativeMesh']['sourceOverlap'];audit_path=ROOT/approval['evidencePath']
                assert sha(audit_path)==approval['evidenceSHA256'];audit=read(audit_path)
                unapproved=deepcopy(child_value);unapproved['nativeMesh'].pop('sourceOverlap')
                staged=digest((json.dumps(unapproved,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode())
                assert audit['stagedGeometrySha256']==staged
                for item in audit['source']['files']:assert sha(ROOT/item['path'])==item['sha256']
                audit.pop('stagedGeometrySha256');audits.append(audit)
            def normalized(value):
                if isinstance(value,str):return value.replace(old_batch,BATCH)
                if isinstance(value,list):return [normalized(v) for v in value]
                if isinstance(value,dict):return {k:normalized(v) for k,v in value.items()}
                return value
            assert normalized(audits[0])==audits[1],'Changed renewed overlap source/metrics/role'
        comparison=reconstructed_numeric_equal(comparison_proposal,wrapper,old_batch=old_batch,new_batch=BATCH,audit_hash_verifier=verify_renewed_audit)
        comparison.update(previousUnfencedProposalPath=rel(comparison_proposal_path),previousProposalSHA256=sha(comparison_proposal_path),reconstructedProposalPath=rel(wrapper_path),reconstructedProposalSHA256=sha(wrapper_path),sourceReconstructedIndependently=True,metadataPathsMayDiffer=True,historicalV2ReceiptProvenanceClaimed=False)
        save(DOC/'independent-complete-numeric-reconstruction.json',comparison)
        patch_row.update(path=rel(wrapper_path),sha256=sha(wrapper_path),replaces={'url':PARENT_URL,'sha256':sha(parent_path),'retainedUids':target_census['installedNativeUids']})
        save(DOC/'retained-parent-proof.json',{'parentURL':PARENT_URL,'parentSHA256':sha(parent_path),
            'retainedChildren':[c['id'] for c in parent.get('patches',[])],
            'gridAndOtherNineChildCoordinatesAndIndicesUnchanged':True,'replacedChildExactBeforeSHA256':sha(old_child_path),'replacedChildOriginalFacets':10675,'retainedChildFullSurfaceEquivalenceAccepted':False,'replacedExistingChild':'government-native-central-hullett-house','newChild':patch['id'],
            'renewedRetainedFloat32Audits':retained_audits,
            'nativeRegionBounds':bounds,'sourceOutsideRegionRetainsExistingTerrain':True,
            'modelGeometryChanges':0,'publication':False})
    save(DOC/'terrain-candidates.json',[patch_row])
    save(DOC/'terrain.json',{'patch':patch_row,'parentHoleFill':fill,'sourceFiles':files,
        'lowSourceIntersectionWithModelM2':low_under_model,'retainSourceBelowClamp':retain_below,'modelGeometryChanges':0})
    live = {e['uid'] for url in manifest['officialModelCatalogues'] for e in read(ROOT/'3d-viewer'/url)['models']}
    nearby = final.load_forms(bounds)
    complete={b['uid']:(b,p,url) for b,p,url in nearby}
    assert len(complete)==len(nearby),'Ambiguous changed-child current forms'
    for b,p,url in parent_forms:
        if b['uid'] in target_census['allTargetUids']:
            if b['uid'] in complete:assert complete[b['uid']][0]==b
            complete[b['uid']]=(b,p,url)
    neighbours=[complete[u] for u in sorted(complete)]
    assert set(target_census['allTargetUids']).issubset(complete)
    assert all(sha(ROOT/p)==pinned for p,pinned in preflight_hashes.items()),'Prerequisite bytes changed during reconstruction'
    save(DOC/'neighbour-inputs.json.gz',{'rows':[{'building':b,'patchIndexes':[0],
                'existingNative':b['uid'] in live or bool(b.get('modelGeometry'))} for b,_,_ in neighbours],
        'inputHashes':{**preflight_hashes,**{rel(ROOT/'3d-viewer'/url):sha(ROOT/'3d-viewer'/url) for _,_,url in neighbours}},'retainedTargetCensus':target_census,
        'candidateIds':UIDS,'patches':[patch_row]})
    call(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',rel(DOC/'selection.json.gz'),
          '--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),
          '--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
    call(['node',str(HERE.parent/'building-batch/validate_candidates_multi_retained.mjs'),'--candidates',rel(LOCAL),
          '--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),
          '--out',rel(DOC/'validation.json')],(0,1))
    call(['node',str(HERE/'check-neighbours-multi-retained.mjs'),rel(DOC)+'/'])
    call(['node',str(HERE/'check-native-neighbours-multi-retained.mjs'),rel(DOC)+'/'])
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
    call(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',rel(DOC/'selection.json.gz'),
        '--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),
        '--out',rel(DOC/'protected-metrics.json'),'--geometry-out',rel(LOCAL/'protected-runtime-geometry.json.gz')])
    call(['node',str(HERE.parent/'building-batch/validate_candidates_multi_retained.mjs'),'--candidates',rel(LOCAL),
        '--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),
        '--out',rel(DOC/'protected-validation.json')],(0,1))
    call(['node',str(HERE/'check-neighbours-multi-retained.mjs'),rel(DOC)+'/'])
    call(['node',str(HERE/'check-native-neighbours-multi-retained.mjs'),rel(DOC)+'/'])
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
