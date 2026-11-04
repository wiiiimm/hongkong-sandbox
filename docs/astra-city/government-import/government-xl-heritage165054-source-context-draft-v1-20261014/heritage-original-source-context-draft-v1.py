"""ROOT-only original source context; no census, acceptance, claim or freezer.

ROOT supplies a maintained canonical lease for the normal command. Import and
preflight use only the standard library and read metadata/literal hashes.
"""
import argparse
import gzip
import hashlib
import json
import struct
import sys
import time
from pathlib import Path

PACKET = Path(__file__).resolve().parent
ROOT = PACKET.parents[3]
HERE = ROOT / 'source-scripts/city/government-import'
CONTRACT = PACKET / 'input-contract.json'
OUTPUT = PACKET / 'source-context-output-v1'
UID = 'landsd/165054:0'
SOURCE = '1a978cdc751afa70933802e2faf090b2435250967e63b68f348ed232aeb1837f'
WORLD = '258ac5cbe505d4f78f8cd334e1b6bbd3e3a56bcd6ef4e1854865f1dade75e8c7'
CURRENT = 'c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def save(path, value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    with path.open('xb') as handle:
        handle.write(gzip.compress(raw, mtime=0) if path.suffix == '.gz' else raw + b'\n')


def fence(contract, contract_sha):
    assert sha(CONTRACT) == contract_sha
    for path, value in contract['filePins'].items():
        assert sha(ROOT / path) == value, path
    assert sha(Path(__file__)) == contract['callerSHA256']
    assert sha(ROOT / '3d-viewer/city/data/manifest.json') == CURRENT


def metadata(contract):
    historical = read(ROOT / contract['historicalRolePath'])
    variant = historical['variants']['direct-shared-OSM']
    assert historical['uid'] == UID and historical['sourceSHA256'] == SOURCE
    assert historical['worldTrianglesSHA256'] == WORLD
    assert historical['identityAccepted'] is False and historical['installationApproved'] is False
    wrappers = read(ROOT / contract['currentFormsPath'])
    forms = {row['form']['uid']: row['form'] for row in wrappers}
    assert set(forms) == {UID, 'landsd/104467:0', 'landsd/57455:0'}
    for row in wrappers:
        tile = read(ROOT / row['sourceTile'])
        matches = [b for b in tile['buildings'] if b['uid'] == row['form']['uid']]
        assert matches == [row['form']]
        assert sha(ROOT / row['sourceTile']) == row['sourceTileSHA256']
    expected = {UID: '3712526467T20050430', 'landsd/104467:0': '3717026380T20071207',
                'landsd/57455:0': '3708726507T20050430'}
    for uid, csuid in expected.items():
        assert forms[uid]['buildingCSUID'] == csuid
        assert forms[uid]['objectId'] == int(uid.split('/')[1].split(':')[0])
    assert len(variant['groupForms']) == 1
    old = variant['groupForms'][0]
    # The complete original provider target, including its courtyard hole.
    for key in ('uid', 'rings', 'buildingCSUID', 'objectId', 'base', 'height', 'structureType'):
        assert forms[UID][key] == old[key], key
    assert len(old['rings']) == 2 and old['structureType'] == 'Tower'
    assert forms['landsd/104467:0']['structureType'] == 'Open-sided Structure'
    assert forms['landsd/57455:0']['name'] == 'Star Mart'
    assert variant['stats']['sourceFacesBeyond10m'] == 462
    assert {r['uid']: r['sourceFaceCount'] for r in variant['overlappingForms']} == {
        'landsd/104467:0': 1106, 'landsd/57455:0': 2}
    return historical, variant, forms


def maintained_lease(contract, path):
    assert path is not None
    sys.path.insert(0, str(HERE))
    from run import reservations
    lease = read(path)
    assert lease['resources'] == contract['canonicalResources']
    assert reservations.owns(lease)
    last = time.monotonic()

    def heartbeat(force=False):
        nonlocal last
        if force or time.monotonic() - last >= 20:
            reply = reservations.heartbeat(lease, ttl=3600)
            assert reply['ok'], reply
            last = time.monotonic()

    heartbeat(True)
    return reservations, lease, heartbeat


def source_array(contract, heartbeat):
    import numpy as np
    from xl_source_stream_binding_20261009 import source_stream_binding
    raw = (ROOT / contract['originalAssetPath']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE
    binding = source_stream_binding(raw)
    assert binding['sourceSHA256'] == SOURCE
    assert binding['rootMatrix'] == contract['originalRootMatrix']
    existing = contract['existingCompleteArray']
    if existing is not None:
        path = ROOT / existing['path']
        assert sha(path) == existing['sha256']
        saved = read(path)
        assert saved['uid'] == UID and saved['sourceSHA256'] == SOURCE
        assert saved['worldTrianglesSHA256'] == WORLD
        assert saved['completeSourceStreamBinding'] == binding
        tri = np.asarray(saved['completeOrderedOriginalTriangles'], dtype='<f8')
        origin = {'kind': 'reused-complete-original-array', **existing}
    else:
        from exact_packed_world_geometry_20261009 import decode_original_world_triangles
        tri = decode_original_world_triangles(raw)
        origin = {'kind': 'single-cached-original-decode', 'path': contract['originalAssetPath'],
                  'sha256': SOURCE, 'decoderSHA256': sha(HERE / 'exact_packed_world_geometry_20261009.py')}
    assert tri.shape == (15140, 3, 3) and np.isfinite(tri).all()
    world = hashlib.sha256(tri.astype('<f8').tobytes()).hexdigest()
    # Save complete lineage before any attribution/rendering assertion.
    save(OUTPUT / 'complete-original-array.json.gz', {
        'uid': UID, 'sourceSHA256': SOURCE, 'worldTrianglesSHA256': world,
        'completeSourceStreamBinding': binding, 'completeOrderedOriginalTriangles': tri.tolist(),
        'completeOriginalFaceCount': len(tri), 'arrayOrigin': origin,
        'sourceGeometryChanges': 0, 'sourcePoseChanges': 0})
    assert world == WORLD
    heartbeat(True)
    return tri, binding, origin


def attribution(tri, variant, forms, heartbeat):
    import numpy as np
    import shapely
    from shapely.geometry import Polygon, mapping
    foot = Polygon(forms[UID]['rings'][0], forms[UID]['rings'][1:])
    assert foot.is_valid
    facep = shapely.polygons(tri[:, :, [0, 2]])
    positive = shapely.area(facep) > 1e-10
    # Exact unchanged historical GEOS selection recipe, not an acceptance test.
    projection = shapely.union_all(facep[positive])
    excess = projection.difference(foot)
    distances = shapely.distance(shapely.points(tri[:, :, [0, 2]].reshape(-1, 2)), foot).reshape(-1, 3)
    far = np.flatnonzero(distances.max(axis=1) > 10).tolist()
    assert len(far) == 462
    assert [tri[far].min(axis=(0, 1)).tolist(), tri[far].max(axis=(0, 1)).tolist()] == variant['stats']['farSourceBounds']
    overlaps = []
    for prior in variant['overlappingForms']:
        heartbeat()
        uid = prior['uid']
        rings = forms[uid]['rings']
        other = Polygon(rings[0], rings[1:])
        assert other.is_valid
        region = excess.intersection(other)
        ids = np.flatnonzero(positive & shapely.intersects(facep, region)).tolist()
        assert len(ids) == prior['sourceFaceCount']
        assert [float(tri[ids, :, 1].min()), float(tri[ids, :, 1].max())] == prior['sourceYRange']
        overlaps.append({'uid': uid, 'currentFormVerbatim': forms[uid], 'priorRecordVerbatim': prior,
                         'actualExcessIntersectionGeometry': mapping(region), 'actualAreaM2': float(region.area),
                         'completeAttributedOriginalFaceIds': ids,
                         'projectedIntersectionLoci': [{'face': f, 'geometry': mapping(facep[f].intersection(region))} for f in ids],
                         'qualification': 'Historical positive-XZ-area whole-facet nomination; projected touch retained. Not 3D collision/contact or ownership.'})
    heartbeat(True)
    wanted = sorted(set(far).union(*(r['completeAttributedOriginalFaceIds'] for r in overlaps)))
    return {'farOriginalFaceIds': far, 'farVertexDistancesM': distances[far].tolist(),
            'actualMaximumVertexDistanceM': float(distances.max()),
            'projectedAreaAtMostHistorical1eMinus10FaceIdsRetained': np.flatnonzero(~positive).tolist(),
            'overlaps': overlaps,
            'selectedOriginalTrianglesABC': [{'face': f, 'A': tri[f, 0].tolist(), 'B': tri[f, 1].tolist(), 'C': tri[f, 2].tolist()} for f in wanted]}


def exports(tri, account, forms, heartbeat):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    from shapely.geometry import shape
    far = account['farOriginalFaceIds']
    actor_colors = {'landsd/104467:0': '#e87800', 'landsd/57455:0': '#00a0b0', UID: '#0033cc'}
    def rings(ax):
        for uid, form in forms.items():
            for ring in form['rings']:
                p = np.asarray(ring + [ring[0]])
                ax.plot(p[:, 0], p[:, 1], color=actor_colors[uid], linewidth=1.2)
    def plan(ax, ids, color, alpha):
        ax.add_collection(PolyCollection(tri[ids][:, :, [0, 2]], facecolor=color,
                                        edgecolor=color, alpha=alpha, linewidth=.2))
        ax.autoscale_view(); ax.set_aspect('equal', adjustable='datalim')
        ax.set_xlabel('X original world (m)'); ax.set_ylabel('Z original world (m)')
    def oblique(ax, ids, highlights, title, azimuth):
        mesh = tri[ids][:, :, [0, 2, 1]]
        ax.add_collection3d(Poly3DCollection(mesh, facecolor='#aaaaaa', edgecolor='#777777', alpha=.22, linewidth=.12))
        for selected, color in highlights:
            ax.add_collection3d(Poly3DCollection(tri[selected][:, :, [0, 2, 1]], facecolor=color, edgecolor=color, alpha=.8, linewidth=.35))
        low = mesh.min(axis=(0, 1)); high = mesh.max(axis=(0, 1))
        ax.set_xlim(low[0], high[0]); ax.set_ylim(low[1], high[1]); ax.set_zlim(low[2], high[2])
        ax.set_box_aspect(np.maximum(high-low, .01)); ax.view_init(elev=28, azim=azimuth)
        ax.set_xlabel('X (m)'); ax.set_ylabel('Z (m)'); ax.set_zlabel('Y (m)'); ax.set_title(title)
    footer = ('Original source coordinates only; diagnostic colours, not GPU visibility or primary-plan registration. '
              'Blue: Museum target incl courtyard hole; orange:104467; cyan:Star Mart57455. No role/ownership/physical acceptance.')
    names = []
    def close(fig, name):
        fig.text(.025, .025, footer, fontsize=8)
        fig.subplots_adjust(bottom=.12, top=.9, wspace=.3, hspace=.3)
        fig.savefig(OUTPUT/name); plt.close(fig); names.append(name); heartbeat(True)
    fig = plt.figure(figsize=(15, 9), dpi=200); ax = fig.add_subplot(111)
    plan(ax, list(range(len(tri))), '#888888', .18); plan(ax, far, '#e000c0', .8); rings(ax)
    ax.set_title('Complete15,140 original facets; far462 magenta; unchanged original provider rings')
    close(fig, 'whole-original-plan-3000x1800.png')
    fig = plt.figure(figsize=(15, 9), dpi=200)
    oblique(fig.add_subplot(121, projection='3d'), list(range(len(tri))), [(far, '#e000c0')], 'Whole source + far462, oblique A', -55)
    oblique(fig.add_subplot(122, projection='3d'), far, [(far, '#e000c0')], 'Far462 isolated, original axes; oblique B', 130)
    close(fig, 'far462-original-oblique-3000x1800.png')
    fig = plt.figure(figsize=(15, 9), dpi=200)
    for slot, row in enumerate(account['overlaps']):
        ids = row['completeAttributedOriginalFaceIds']; uid = row['uid']
        ax = fig.add_subplot(2, 2, slot*2+1)
        plan(ax, ids, actor_colors[uid], .4); rings(ax)
        locus = shape(row['actualExcessIntersectionGeometry'])
        parts = [locus] if locus.geom_type == 'Polygon' else list(locus.geoms)
        for part in parts:
            assert part.geom_type == 'Polygon'
            for ring in [part.exterior, *part.interiors]:
                xy = list(ring.coords)
                ax.plot([p[0] for p in xy], [p[1] for p in xy], color='#111111', linewidth=1.8)
        lo_x, lo_z, hi_x, hi_z = locus.bounds
        # Explicit camera-only zoom. Whole facets remain in the companion oblique
        # and complete ABC records; neither geometry nor source arrays are clipped.
        ax.set_xlim(lo_x-2, hi_x+2); ax.set_ylim(lo_z-2, hi_z+2)
        ax.set_title('Museum facets vs '+uid+': black projected locus; 2m view margin')
        ax = fig.add_subplot(2, 2, slot*2+2, projection='3d')
        oblique(ax, ids, [(ids, actor_colors[uid])], 'Museum whole nominated facets over '+uid, -55)
    close(fig, 'independent-actors-source-attribution-3000x1800.png')
    result = []
    for name in names:
        path = OUTPUT/name; raw = path.read_bytes()
        assert raw[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', raw[16:24]) == (3000, 1800)
        result.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'dimensions': [3000, 1800]})
    return result


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--preflight-only', action='store_true')
    group.add_argument('--export-original-source-context-only', action='store_true')
    parser.add_argument('--lease-file', type=Path)
    args = parser.parse_args(); contract = read(CONTRACT); cs = sha(CONTRACT)
    fence(contract, cs); historical, variant, forms = metadata(contract)
    assert not OUTPUT.exists(), 'No overwrite/restart of a previous attempt'
    if args.preflight_only:
        assert args.lease_file is None
        fence(contract, cs)
        print(json.dumps({'passed': True, 'originalFacesDeclared': 15140, 'farExpected': 462,
                          'independentOverlapFaceCounts': [1106, 2], 'canonicalResources': contract['canonicalResources'],
                          'noDecode': True, 'noGeometryCalculation': True, 'noDB': True, 'noLease': True}))
        return
    reservations, lease, heartbeat = maintained_lease(contract, args.lease_file)
    OUTPUT.mkdir()
    try:
        tri, binding, origin = source_array(contract, heartbeat)
        account = attribution(tri, variant, forms, heartbeat)
        record = {'uids': [UID], 'uid': UID, 'sourceSHA256': SOURCE, 'worldTrianglesSHA256': WORLD,
                  'completeOriginalFaces': len(tri), 'completeSourceStreamBinding': binding, 'arrayOrigin': origin,
                  'completeOriginalArray': {'path': str((OUTPUT/'complete-original-array.json.gz').relative_to(ROOT)),
                                            'sha256': sha(OUTPUT/'complete-original-array.json.gz')},
                  'historicalRoleRecordVerbatim': historical, 'currentThreeFormsVerbatim': forms,
                  'attribution': account, 'allInputHashes': contract['filePins'],
                  'sourceGeometryChanges': 0, 'sourcePoseChanges': 0, 'componentCensusPerformed': False,
                  'sourceRoleAccepted': False, 'identityAccepted': False, 'physicalAccepted': False,
                  'currentAcceptance': False, 'installationApproved': False, 'primaryImagesNotRegistered': True}
        save(OUTPUT/'context-before-render.json.gz', record)
        record['actualExports'] = exports(tri, account, forms, heartbeat)
        heartbeat(True); fence(contract, cs); assert reservations.owns(lease)
        save(OUTPUT/'context.json.gz', record)
        summary = {'uids': [UID], 'uid': UID, 'complete': True, 'sourceSHA256': SOURCE,
                   'worldTrianglesSHA256': WORLD, 'completeOriginalFaces': len(tri),
                   'farFaces': 462, 'independentOverlapCounts': [1106, 2],
                   'completeArrayRef': record['completeOriginalArray'],
                   'contextRef': {'path': str((OUTPUT/'context.json.gz').relative_to(ROOT)),
                                  'sha256': sha(OUTPUT/'context.json.gz')},
                   'actualExports': record['actualExports'], 'allInputHashes': contract['filePins'],
                   'sourceRoleAccepted': False, 'identityAccepted': False, 'physicalAccepted': False,
                   'currentAcceptance': False, 'installationApproved': False, 'newlyInstalled': 0,
                   'geometryChanges': 0, 'sourcePoseChanges': 0}
        save(OUTPUT/'result.json', summary)
        save(OUTPUT/'terminal.json', {'complete': True, 'resultSHA256': sha(OUTPUT/'result.json'),
                                      'contextSHA256': sha(OUTPUT/'context.json.gz'),
                                      'contractSHA256': cs, 'callerSHA256': sha(Path(__file__)),
                                      'allInputHashesUnchanged': True, 'actualExports': record['actualExports'],
                                      'newlyInstalled': 0, 'currentAcceptance': False,
                                      'externalSupervisorMustReleaseAfterChildExit': True})
        print(json.dumps({'complete': True, 'originalFaces': len(tri), 'farFaces': 462,
                          'overlapCounts': [len(x['completeAttributedOriginalFaceIds']) for x in account['overlaps']],
                          'contextSHA256': sha(OUTPUT/'context.json.gz'), 'actualExports': record['actualExports']}), flush=True)
    except BaseException as error:
        save(OUTPUT/'failure.json', {'complete': False, 'errorType': type(error).__name__, 'error': str(error),
                                    'callerSHA256': sha(Path(__file__)), 'contractSHA256': cs,
                                    'sourceCorruptionInferred': False, 'currentAcceptance': False})
        raise
    # Caller never releases while running; ROOT's maintained supervisor owns cleanup.


if __name__ == '__main__':
    main()
