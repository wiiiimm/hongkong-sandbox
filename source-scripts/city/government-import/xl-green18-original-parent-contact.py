"""Retain suitable unchanged root facets beneath Green18's original low rim.

No model/elevation/tolerance edits. Parent facets must be higher than the native
terrain and within the existing low-rim clearance interval. Every complete fresh
physical, identity, neighbour and runtime gate remains mandatory.
"""
import argparse
import importlib.util
import json
import subprocess
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations, connect

PREVIOUS = 'government-xl-distinct-three-cell-terrain-20261007-6462-0'
BASE = Path('docs/astra-city/government-import/government-xl-distinct-three-source-current-inputs-20261007')
UID = 'landsd/6462:0'


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def plane(face):
    normal = np.cross(face[1] - face[0], face[2] - face[0])
    assert abs(normal[1]) > 1e-10
    ax, az = -normal[0] / normal[1], -normal[2] / normal[1]
    return np.array([ax, az, face[0, 1] - ax * face[0, 0] - az * face[0, 2]])


def clip(coords, coefficients):
    """Clip a convex original-facet intersection to coefficient dot XY1 >=0."""
    output = []
    for a, b in zip(coords, coords[1:] + coords[:1]):
        da, db = np.dot(coefficients, [*a, 1]), np.dot(coefficients, [*b, 1])
        if da >= 0:
            output.append(a)
        if (da >= 0) != (db >= 0):
            t = da / (da - db)
            output.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return output


def select(patch, bounds, projection, sampler, floor, ceiling):
    patches = load('contact_parent_planes', 'native_patch_resolution.py')
    protected = projection.intersection(shapely.box(*bounds))
    assert protected.area > 0
    parents = np.asarray(patches.grid_surface_faces(sampler, protected))
    polygons = shapely.polygons(parents[:, :, [0, 2]])
    tree = shapely.STRtree(polygons)
    selected = []
    pairs = 0
    for native in patches._faces(patch):
        polygon = shapely.Polygon(native[:, [0, 2]])
        if polygon.area <= 1e-10 or not polygon.intersects(protected):
            continue
        native_plane = plane(native)
        for i in tree.query(polygon, predicate='intersects'):
            region = polygon.intersection(polygons[i])
            if region.area <= 1e-10:
                continue
            parent_plane = plane(parents[i])
            coords = list(region.exterior.coords)[:-1]
            conditions = [parent_plane - native_plane - [0, 0, 1e-8],
                          parent_plane - [0, 0, floor],
                          -parent_plane + [0, 0, ceiling]]
            for condition in conditions:
                coords = clip(coords, condition)
                if len(coords) < 3:
                    break
            pairs += 1
            if len(coords) >= 3:
                for x, z in coords:
                    height = np.dot(parent_plane, [x, z, 1])
                    assert floor - 1e-7 <= height <= ceiling + 1e-7
                selected.append(shapely.Polygon(coords))
    result = shapely.union_all(selected) if selected else shapely.Polygon()
    return result, {'areaM2': result.area, 'planePairs': pairs,
                    'parentHeightInterval': [floor, ceiling],
                    'policy': 'Retain unchanged higher root facets only within the existing low-rim contact band under the original source projection. No invented heights.'}


def owned(args, doc, local):
    assert reservations.owns(read(local / 'reservation.json'))
    previous = ROOT / 'docs/astra-city/government-import' / PREVIOUS
    prior = read(previous / 'result.json')
    sync = read(previous / 'neon-sync.json')
    assert sync['resultVerified'] and sync['jobId'] == prior['jobId']
    assert prior['uid'] == UID and set(prior['reasons']) == {'ground-contact-unresolved', 'sampled-ground-gap-below-model-bottom'}
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                           (prior['jobId'],)).fetchone() == ('complete', prior)
    for ref in prior['evidenceRefs']:
        assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    selection = read(previous / 'selection.json.gz')
    assert digest((ROOT / '3d-viewer/city/data/manifest.json').read_bytes()) == selection['manifestSHA256']
    assert len(selection['rows']) == 1 and selection['rows'][0]['uid'] == UID
    original = read(previous / 'terrain-candidates.json')[0]
    assert 'replaces' not in original
    assert digest((ROOT / original['path']).read_bytes()) == original['sha256']
    runtime = read(HERE / 'local' / PREVIOUS / 'runtime-geometry.json.gz')
    for path, sha in runtime['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
    r = runtime['rows'][0]
    assert r['uid'] == UID and r['sourceSHA256'] == prior['sourceSHA256']
    vertices = np.asarray(r['position']).reshape(-1, 3)
    triangles = vertices[np.asarray(r['index']).reshape(-1, 3)]
    bottom = vertices[:, 1].min()
    low = vertices[vertices[:, 1] <= bottom + .35, 1]
    floor, ceiling = float(low.max() - 1 + 1e-5), float(bottom + .5 - 1e-5)
    assert floor <= ceiling
    projection = shapely.union_all([shapely.MultiPoint(f[:, [0, 2]]).convex_hull for f in triangles]).buffer(.001, join_style='mitre')
    second = load('contact_parent_source', 'xl-second-pass.py')
    patches = load('contact_parent_patches', 'native_patch_resolution.py')
    parent_path = ROOT / '3d-viewer/city/data/terrain.json'
    parent = read(parent_path)
    sampler = second.resolution.terrain.fine.DemSampler(parent, rendered=True)
    patch = read(ROOT / original['path'])
    protected, proof = select(patch, original['bounds'], projection, sampler, floor, ceiling)
    evidence = {'uid': UID, 'sourceSHA256': prior['sourceSHA256'], 'priorJobId': prior['jobId'],
                'parent': {'path': str(parent_path.relative_to(ROOT)), 'sha256': digest(parent_path.read_bytes())},
                'selection': proof, 'lowRimMinimumY': float(bottom), 'lowRimMaximumY': float(low.max()),
                'runnerSHA256': digest(Path(__file__).read_bytes()), 'modelGeometryChanges': 0,
                'scriptExternalAICalls': 0, 'publication': False}
    if protected.area <= 1e-8:
        save(doc / 'original-parent-contact.json', evidence)
        load('contact_parent_fence', 'xl-cell-indexed-terrain-continuation.py').finish(
            args, selection['rows'][0], doc, local, prior['reasons'] + ['no-original-parent-in-contact-band'])
        return
    evidence['preservation'] = patches.preserve_parent_under_projection(patch, original['bounds'], protected, sampler)
    path = local / Path(original['path']).name
    terrain = read(previous / 'terrain.json')
    for source in terrain['sourceFiles']:
        assert digest((ROOT / source['path']).read_bytes()) == source['sha256']
    save(path, patch)
    if patches.projected_context(patch, original['bounds'])[3] > 1e-8:
        patches.approve_original_overlap(patch, path, doc / 'original-overlap.json', terrain['sourceFiles'])
        patches.finalize_overlap_evidence(patch, doc / 'original-overlap.json')
    else:
        patch['nativeMesh'].pop('sourceOverlap', None)
    second.resolution.validate_patch(patch, parent)
    save(path, patch)
    candidate = {**original, 'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes()),
                 'triangles': len(patch['nativeMesh']['index']) // 3}
    assert candidate['triangles'] <= 100000
    prepared = ROOT / 'docs/astra-city/government-import' / (args.batch + '-prepared')
    assert not prepared.exists()
    for name in ['selection.json.gz', 'neighbour-inputs.json.gz', 'identity-proof.json',
                 'owned-source-identity.json', 'owned-source-identity-contact.json', 'indexed-preflight.json']:
        save(prepared / name, read(previous / name))
    save(prepared / 'terrain-candidates.json', [candidate])
    save(prepared / 'terrain.json', {**terrain, 'patch': candidate})
    neighbours = read(prepared / 'neighbour-inputs.json.gz')
    neighbours['patches'] = [candidate]
    save(prepared / 'neighbour-inputs.json.gz', neighbours)
    save(prepared / 'original-parent-contact.json', evidence)
    for name in ['catalogue.json', 'catalogue-index.json', 'source-forms.json']:
        save(HERE / 'local' / prepared.name / name, read(HERE / 'local' / PREVIOUS / name))
    load('contact_parent_full_checks', 'xl-cell-installation-recheck.py').owned(
        SimpleNamespace(previous=str(prepared.relative_to(ROOT)), batch=args.batch, base=BASE), doc, local)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    local = HERE / 'local' / args.batch
    if args.owned:
        owned(args, doc, local)
        return
    assert not doc.exists()
    previous = ROOT / 'docs/astra-city/government-import' / PREVIOUS
    uids = {r['building']['uid'] for r in read(previous / 'neighbour-inputs.json.gz')['rows']} | {UID}
    claim = reservations.claim('codex-xl-green18-contact-parent-' + str(uuid.uuid4()),
        [('building:' if u.startswith('landsd/') else 'source-form:') + u for u in sorted(uids)], batch=args.batch)
    assert claim['ok'], claim
    save(local / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run',
                    '--lease-file', str(local / 'reservation.json'), '--', sys.executable, __file__,
                    '--batch', args.batch, '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
