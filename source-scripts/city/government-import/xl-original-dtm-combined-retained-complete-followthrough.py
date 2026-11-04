"""Fresh full checks for exact original TIN/DTM surface combinations.

Reuse the established parent boundary transition and all existing acceptance
gates. No building, source height, identity or tolerance edits.
"""
import argparse
import importlib.util
import json
import subprocess
import sys
import uuid
import zipfile
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations, connect

BASE = Path('docs/astra-city/government-import/government-xl-original-dtm-next-four-current-inputs-20261007')
SOURCE = Path('references/codex/hongkong-3d-model/data/hk-landsd-5m/Whole_HK_DTM_5m.zip')
SHA = '785718f462ae6de3c9e1fed2bf9fe5affe1c1d739c0a969fd62cf3680b4b33ab'


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def original_faces(bounds):
    assert digest((ROOT / SOURCE).read_bytes()) == SHA
    x0, z0, x1, z1 = bounds
    c0, c1 = int(np.floor((x0 + 34500) / 5)), int(np.ceil((x1 + 34500) / 5))
    r0, r1 = int(np.floor((z0 + 31500) / 5)), int(np.ceil((z1 + 31500) / 5))
    assert 0 <= c0 < c1 < 12751 and 0 <= r0 < r1 < 9601
    values = []
    with zipfile.ZipFile(ROOT / SOURCE) as archive:
        name = next(n for n in archive.namelist() if n.lower().endswith('.asc'))
        with archive.open(name) as stream:
            header = [stream.readline().decode().strip() for _ in range(6)]
            assert header == read(ROOT / 'docs/astra-city/landmark-preflight/terrain-inputs.json')['dtm']['asciiHeader']
            for r in range(r1 + 1):
                line = stream.readline()
                if r >= r0:
                    row = np.fromstring(line.decode(), sep=' ')
                    assert len(row) == 12751
                    values.append(row[c0:c1 + 1])
    grid = np.asarray(values)
    assert np.isfinite(grid).all() and grid.min() > -9999
    faces = []
    for r in range(r1-r0):
        for c in range(c1-c0):
            def v(dc, dr):
                return [-34500 + (c0+c+dc)*5, float(grid[r+dr, c+dc]), -31500 + (r0+r+dr)*5]
            a, b, d, e = v(0, 0), v(1, 0), v(0, 1), v(1, 1)
            faces.extend([[a, d, b], [b, d, e]])
    return np.asarray(faces), {'source': str(SOURCE), 'sourceSHA256': SHA,
        'originalGridBounds': [c0, r0, c1, r1], 'sampleOrigin': [800000, 848000],
        'cellSize': 5, 'diagonal': 'upper-right to lower-left in grid space',
        'triangles': len(faces), 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0}


def select_original_dtm(original, alternative, projection, floor, ceiling):
    """Select unchanged DTM planes only where the old plane misses the rim band."""
    p = module('dtm_combo_planes', 'native_patch_resolution.py')
    clipping = module('dtm_combo_clip', 'xl-green18-original-parent-contact.py')
    dtm_faces = p._faces(alternative)
    dtm_polygons = shapely.polygons(dtm_faces[:, :, [0, 2]])
    tree = shapely.STRtree(dtm_polygons)
    regions = []
    for face in p._faces(original):
        polygon = shapely.Polygon(face[:, [0, 2]])
        if polygon.area <= 1e-10:
            continue
        old_plane = clipping.plane(face)
        for i in tree.query(polygon, predicate='intersects'):
            area = polygon.intersection(dtm_polygons[i])
            if area.area <= 1e-10:
                continue
            plane = clipping.plane(dtm_faces[i])
            coords = list(area.exterior.coords)[:-1]
            for condition in [plane-[0,0,floor], -plane+[0,0,ceiling]]:
                coords = clipping.clip(coords, condition)
                if len(coords)<3:
                    break
            if len(coords)<3:
                continue
            # Two disjoint regions: original surface too low, or too high.
            for condition in [-old_plane+[0,0,floor-1e-5],old_plane-[0,0,ceiling+1e-5]]:
                clipped = clipping.clip(coords, condition)
                if len(clipped)>=3:
                    regions.append(shapely.Polygon(clipped))
    protected = (shapely.union_all(regions) if regions else shapely.Polygon()).intersection(projection)
    return protected


def owned(args, doc, local):
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    key = args.uid.split('/')[1].replace(':', '-')
    previous = ROOT / 'docs/astra-city/government-import' / ('government-xl-original-dtm-next-four-retained-cell-20261007-' + key)
    prior, sync = read(previous / 'result.json'), read(previous / 'neon-sync.json')
    assert prior['uid'] == args.uid and sync['resultVerified'] and sync['jobId'] == prior['jobId']
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (prior['jobId'],)).fetchone() == ('complete', prior)
    for ref in prior['evidenceRefs']:
        assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    assert read(previous / 'owned-source-identity.json')['passed']
    selection = read(previous / 'selection.json.gz')
    assert selection['manifestSHA256'] == digest((ROOT / '3d-viewer/city/data/manifest.json').read_bytes())
    old = read(previous / 'terrain-candidates.json')[0]
    assert isinstance(old.get('replaces'),dict)
    assert set(old['replaces'])=={'url','sha256','retainedUids'}
    retained = read(previous/'retained-routing.json')
    assert retained['retainedURL']==old['replaces']['url'] and retained['retainedSHA256']==old['replaces']['sha256']
    assert digest((ROOT/'3d-viewer'/old['replaces']['url']).read_bytes())==retained['retainedSHA256']
    old_patch = read(ROOT / old['path'])
    assert digest((ROOT / old['path']).read_bytes()) == old['sha256']
    second = module('original_dtm_second', 'xl-second-pass.py')
    parent = read(ROOT / '3d-viewer/city/data/terrain.json')
    # A root patch must not replace any installed regional or native terrain.
    for entry in read(ROOT / '3d-viewer/city/data/manifest.json')['terrainPatches']:
        installed = read(ROOT / '3d-viewer' / entry['url'])
        g = installed['meta']['georef']
        bb = [g['bE']-834500, 816500-g['bN'], g['bE']-834500+(installed['w']-1)*g['aE'], 816500-g['bN']-(installed['h']-1)*g['aN']]
        a = old['bounds']
        if entry['url']==old['replaces']['url']:continue
        assert not (bb[0] < a[2] and bb[2] > a[0] and bb[1] < a[3] and bb[3] > a[1]), 'Additional installed terrain requires independent retention'
    native, proof = original_faces(old['bounds'])
    source = {'provider': 'Lands Department / Hong Kong SAR Government', 'sourceFiles': [{'path': str(SOURCE), 'sha256': SHA}],
        'crs': 'EPSG:2326', 'verticalDatum': 'HKPD', 'url': 'https://www.landsd.gov.hk/landsd_psi_data/SMO/data/Whole_HK_DTM_5m.zip',
        'limitation': 'Archival government 5 m DTM; source building and terrain revisions differ. All fresh physical checks required.'}
    alternative = second.resolution.make_patch({'uids': [args.uid], 'cells': old_patch['coarseCells']}, parent, native, [source], terrain_triangle_budget=100000)
    runtime = read(HERE / 'local' / previous.name / 'runtime-geometry.json.gz')['rows'][0]
    assert runtime['sourceSHA256']==prior['sourceSHA256']
    v = np.asarray(runtime['position']).reshape(-1,3)
    faces = v[np.asarray(runtime['index']).reshape(-1,3)]
    projection = shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in faces]).buffer(.001,join_style='mitre')
    bottom = float(v[:,1].min())
    protected = select_original_dtm(old_patch, alternative, projection, bottom-1+1e-5, bottom+.5-1e-5)
    if protected.area<=1e-8:
        save(doc/'original-dtm-selection.json',{**proof,'selectedAreaM2':float(protected.area),'priorJobId':prior['jobId'],
            'priorEvidenceRefs':prior['evidenceRefs'],'retained':old['replaces'],'runnerSHA256':digest(Path(__file__).read_bytes()),
            'sourceSHA256':prior['sourceSHA256'],'qualification':'No distinct original DTM facet in the existing strict band. Prior physical failures and retained-model checks stay authoritative; no installation credit.'})
        module('dtm_retained_no_region_fence','xl-cell-indexed-terrain-continuation.py').finish(args,selection['rows'][0],doc,local,prior['reasons']+['no-distinct-original-dtm-in-contact-band'])
        return
    patches = module('dtm_combo_patch', 'native_patch_resolution.py')
    from rendered_patch_sampler import RenderedPatchSampler
    root_sampler = second.resolution.terrain.fine.DemSampler(parent,rendered=True)
    grid_sampler = second.resolution.terrain.fine.DemSampler(alternative,rendered=True)
    dtm_sampler = RenderedPatchSampler(alternative,root_sampler,grid_sampler)
    patch = old_patch
    proof['selectedAreaM2']=float(protected.area)
    proof['preservation']=patches.preserve_parent_under_projection(patch,old['bounds'],protected,dtm_sampler,edge_sampler=root_sampler)
    patch['meta']['source']['nativeSources'].append(source)
    old_terrain = read(previous/'terrain.json')
    source['sourceFiles'] = old_terrain['sourceFiles'] + source['sourceFiles']
    source['sourceFiles'].append({'path': '3d-viewer/'+old['replaces']['url'], 'sha256':retained['retainedSHA256']})
    for ref in source['sourceFiles']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
    path = local / (patch['id'] + '.json')
    save(path, patch)
    from float32_coverage import approve_roundoff
    _, polygons, _, excess = patches.projected_context(patch,old['bounds'])
    difference=shapely.union_all(polygons).symmetric_difference(shapely.box(*old['bounds'])).area
    if difference>1e-10:save(doc/'float32-coverage.json',approve_roundoff(patch,old['bounds']))
    save(path,patch)
    if excess>1e-8:
        patches.approve_original_overlap(patch,path,doc/'original-dtm-overlap.json',source['sourceFiles'])
        patches.finalize_overlap_evidence(patch,doc/'original-dtm-overlap.json')
    else:patch['nativeMesh'].pop('sourceOverlap',None)
    second.resolution.validate_patch(patch,parent)
    save(path,patch)
    candidate = {**old, 'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes()), 'triangles': len(patch['nativeMesh']['index']) // 3}
    prepared = ROOT / 'docs/astra-city/government-import' / (args.batch + '-prepared')
    assert not prepared.exists()
    for name in ['selection.json.gz', 'neighbour-inputs.json.gz', 'identity-proof.json', 'owned-source-identity.json', 'owned-source-identity-contact.json', 'indexed-preflight.json']:
        save(prepared / name, read(previous / name))
    save(prepared / 'terrain-candidates.json', [candidate])
    save(prepared / 'terrain.json', {'patch': candidate, 'sourceFiles': source['sourceFiles'], 'originalDTM': proof, 'modelGeometryChanges': 0})
    inputs = read(prepared / 'neighbour-inputs.json.gz')
    inputs['patches'] = [candidate]
    save(prepared / 'neighbour-inputs.json.gz', inputs)
    save(prepared / 'original-dtm.json', {**proof, 'priorJobId': prior['jobId'], 'runnerSHA256': digest(Path(__file__).read_bytes()), 'source': source,
        'policy': 'Unchanged original 5 m sample heights and facets in model core; established bounded parent boundary transition. No building edits or acceptance exceptions.'})
    for name in ['catalogue.json', 'catalogue-index.json', 'source-forms.json']:
        save(HERE / 'local' / prepared.name / name, read(HERE / 'local' / previous.name / name))
    module('original_dtm_full_recheck', 'xl-cell-installation-recheck.py').owned(
        SimpleNamespace(previous=str(prepared.relative_to(ROOT)), batch=args.batch, base=BASE), doc, local)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--uid', required=True, choices=['landsd/252988:0','landsd/265848:0','landsd/228219:0'])
    p.add_argument('--batch', required=True)
    p.add_argument('--owned', action='store_true')
    args = p.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    doc, local = ROOT / 'docs/astra-city/government-import' / args.batch, HERE / 'local' / args.batch
    if args.owned:
        owned(args, doc, local)
        return
    assert not doc.exists()
    key = args.uid.split('/')[1].replace(':', '-')
    prev = ROOT / 'docs/astra-city/government-import' / ('government-xl-original-dtm-next-four-retained-cell-20261007-' + key)
    uids = {r['building']['uid'] for r in read(prev / 'neighbour-inputs.json.gz')['rows']} | {args.uid}
    claim = reservations.claim('codex-xl-original-dtm-' + str(uuid.uuid4()), [('building:' if u.startswith('landsd/') else 'source-form:') + u for u in sorted(uids)], batch=args.batch)
    assert claim['ok'], claim
    save(local / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(local / 'reservation.json'), '--', sys.executable, __file__, '--uid', args.uid, '--batch', args.batch, '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
