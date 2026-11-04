"""HKS-222: resumable, source-preserving per-sheet native conversion; never publication.

convert_sheet(archive, download, official_path, out) returns a compact summary.
Every BUILDING glTF receives an outcome even when its geometry cannot be packed.
Only explicit viewerUids supplied by the caller can identify a replacement part.
"""
from __future__ import annotations
import argparse
import atexit
import select
from collections import Counter, defaultdict
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import zipfile
import numpy as np
from shapely.geometry import MultiPoint, Polygon

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
REVIEW = ROOT / 'docs/astra-city/mui-wo-buildings/review'
sys.path.insert(0, str(REVIEW))
from prepare_model_sample import model_geometry, matrix, stage
from compare_official import official_shape
from bake_model_geometry import decode
_spec = importlib.util.spec_from_file_location('citywide_existing_packer', ROOT / 'source-scripts/city/central-completion/pack_models.py')
_packer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_packer)
VERSION = 1


def converter_dependencies():
    """Code inputs orchestration can hash to identify a processing version."""
    return [Path(__file__), HERE/'terrain-check.mjs', REVIEW/'prepare_model_sample.py',
            REVIEW/'bake_model_geometry.py', REVIEW/'compare_official.py',
            ROOT/'source-scripts/city/central-completion/pack_models.py',
            ROOT/'3d-viewer/city/geo.js', ROOT/'3d-viewer/city/native-terrain.js',
            ROOT/'3d-viewer/city/official-model-assets.js']


class UnsupportedSource(ValueError):
    pass


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n'
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent, delete=False) as f:
        temporary = Path(f.name)
        f.write(raw)
    temporary.replace(path)


def safe_member(name):
    p = PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name or not name:
        raise UnsupportedSource('Unsafe or external source dependency: ' + name)
    return p


def validate_geometry(data, folder, allow_terrain_textures=False):
    """Check features the unchanged decoder/packer understands, before decoding."""
    prohibited = ('animations', 'skins', 'extensionsRequired', 'extensionsUsed') + (() if allow_terrain_textures else ('images','textures'))
    if any(data.get(k) for k in prohibited):
        raise UnsupportedSource('Textured, skinned, animated or extended source requires its own validated packer')
    buffers = data.get('buffers', [])
    for b in buffers:
        safe_member(b['uri'])
        if (folder / b['uri']).stat().st_size < b['byteLength']:
            raise ValueError('Truncated source buffer')
    for view in data.get('bufferViews', []):
        b = buffers[view['buffer']]
        if view.get('byteOffset', 0) < 0 or view['byteLength'] < 0 or view.get('byteOffset', 0) + view['byteLength'] > b['byteLength']:
            raise ValueError('Buffer view outside declared buffer')
    for a in data.get('accessors', []):
        if a.get('sparse') or a.get('normalized'):
            raise UnsupportedSource('Sparse or normalised accessor unsupported by existing packer')
        sizes = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
        types = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
        if a['type'] not in sizes or a['componentType'] not in types:
            raise UnsupportedSource('Unsupported accessor type')
        width = sizes[a['type']] * types[a['componentType']]
        v = data['bufferViews'][a['bufferView']]
        count = a['count']; offset = a.get('byteOffset', 0); stride = v.get('byteStride', width)
        if count <= 0 or offset < 0 or stride < width or offset + (count - 1) * stride + width > v['byteLength']:
            raise ValueError('Accessor outside buffer view')
    runtime_attributes = True
    for mesh in data['meshes']:
        if mesh.get('weights'):
            raise UnsupportedSource('Morph weights unsupported')
        for p in mesh['primitives']:
            if p.get('mode', 4) != 4 or p.get('targets') or p.get('extensions'):
                raise UnsupportedSource('Non-triangle/morph/extended primitive unsupported')
            pa = data['accessors'][p['attributes']['POSITION']]
            if pa['componentType'] != 5126 or pa['type'] != 'VEC3':
                raise UnsupportedSource('Position must be native float32 VEC3')
            arrays = {k: decode(data, a, folder) for k, a in p['attributes'].items()}
            count = len(arrays['POSITION'])
            runtime_attributes = runtime_attributes and arrays.get('NORMAL',np.empty((0,0))).shape == (count,3) and arrays.get('COLOR_0',np.empty((0,0))).shape in ((count,3),(count,4))
            if any(len(a) != count or not np.isfinite(a).all() for a in arrays.values()):
                raise ValueError('Non-finite or inconsistent primitive attributes')
            if 'indices' in p:
                a = data['accessors'][p['indices']]
                if a['componentType'] not in (5121, 5123, 5125) or a['type'] != 'SCALAR':
                    raise ValueError('Indices must be unsigned scalar')
                indices = decode(data, p['indices'], folder).reshape(-1)
            else:
                indices = np.arange(count)
            if not len(indices) or len(indices) % 3 or int(indices.min()) < 0 or int(indices.max()) >= count:
                raise ValueError('Triangle index range/count invalid')
    nodes = data['nodes']; active = set(); visited = set()
    def visit(index, parent):
        if not isinstance(index, int) or index < 0 or index >= len(nodes) or index in active:
            raise ValueError('Invalid/cyclic scene node reference')
        active.add(index); visited.add(index); node = nodes[index]
        if any(k in node for k in ('translation', 'rotation', 'scale', 'skin', 'weights')):
            raise UnsupportedSource('TRS/skinned/morph node needs explicitly validated decoder support')
        transform = matrix(node)
        if transform.shape != (4, 4) or not np.isfinite(transform).all() or not np.allclose(transform[3], [0, 0, 0, 1], rtol=0, atol=1e-12):
            raise ValueError('Non-finite or non-affine source transform')
        world = parent @ transform
        if not np.isfinite(world).all() or abs(np.linalg.det(world[:3, :3])) < 1e-15:
            raise ValueError('Singular or invalid accumulated transform')
        if 'mesh' in node and not 0 <= node['mesh'] < len(data['meshes']):
            raise ValueError('Node mesh reference invalid')
        for child in node.get('children', []):
            visit(child, world)
        active.remove(index)
    for index in data['scenes'][data.get('scene', 0)]['nodes']:
        visit(index, np.eye(4))
    return {'reachableNodes': len(visited), 'unreachableNodes': len(nodes) - len(visited), 'finiteAttributes': True, 'indexRangesValid': True, 'affineNativeTransforms': True, 'runtimeAttributesCompatible': bool(runtime_attributes)}


def match_source(positions, model_id, by_ref):
    """Same conservative source screen as prepare_model_sample.stage, no UID invention."""
    hull = MultiPoint(positions[:, [0, 2]]).convex_hull
    candidates = []; matches = []; viewer = []
    for f, shape in by_ref.get(model_id[1:11], []):
        attrs = f['attributes']
        overlap = hull.intersection(shape).area / max(.001, min(hull.area, shape.area))
        distance = hull.centroid.distance(shape.centroid)
        row = {'objectId': attrs['OBJECTID'], 'buildingCSUID': attrs.get('BuildingCSUID'), 'overlapOfSmallerFootprint': overlap, 'footprintCentroidDistanceMetres': distance, 'sourceBaseHeight': attrs.get('BaseHeight'), 'sourceTopHeight': attrs.get('TopHeight')}
        candidates.append(row)
        if overlap < .5 or distance > 10:
            continue
        matches.append(row)
        for part in f.get('viewerUids', []):
            rings = part['rings']
            polygon = Polygon(rings[0], rings[1:]).buffer(0)
            if polygon.is_empty or polygon.area<=0:
                continue
            part_overlap = hull.intersection(polygon).area / max(.001, min(hull.area, polygon.area))
            part_distance = hull.centroid.distance(polygon.centroid)
            if part_overlap >= .5 and part_distance <= 10:
                viewer.append({'uid': part['uid'], 'buildingCSUID': attrs.get('BuildingCSUID'), 'objectId': attrs['OBJECTID'], 'overlapOfSmallerFootprint': part_overlap, 'footprintCentroidDistanceMetres': part_distance, 'recordedBaseHeight': attrs.get('BaseHeight'), 'recordedTopHeight': attrs.get('TopHeight'), 'label': attrs.get('BuildingNameEN') or model_id})
    # Duplicate records for the same source part are not duplicate identities.
    unique = {v['uid']: v for v in viewer}
    return {'policy': 'Exact GeoRefNo, hull overlap >=0.5 of smaller footprint, centroid <=10m; same gates again for explicit viewer polygon parts', 'officialCandidates': candidates, 'officialMatches': matches, 'viewerMatches': list(unique.values())}


def samples(positions, limit=512):
    low = np.flatnonzero(positions[:, 1] <= positions[:, 1].min() + .35)
    def select(ids):
        return ids[np.linspace(0, len(ids) - 1, min(limit, len(ids)), dtype=int)] if len(ids) else ids
    ids = np.unique(np.r_[select(np.arange(len(positions))), select(low)])
    return {'position': positions[ids].tolist(), 'sourceVertices': len(positions), 'sampledVertices': len(ids), 'sourceLowRimVertices': len(low), 'sampledLowRimVertices': int(np.isin(ids, low).sum()), 'lowRimSampleMask': np.isin(ids, low).tolist(), 'method': 'Deterministic source-order stratified sample, up to 512 whole-model plus 512 low-rim vertices; no full-triangle burial or support acceptance'}


def _convert_one(z, entry, source_dir, out, by_ref, row):
    name = entry.filename; model_id = PurePosixPath(name).stem
    raw = z.read(entry); row['sourceHashes'] = {name: hashlib.sha256(raw).hexdigest()}
    data = json.loads(raw)
    safe_member(name); folder = PurePosixPath(name).parent
    p = source_dir / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(raw)
    for b in data.get('buffers', []):
        path = str(folder / safe_member(b['uri']))
        safe_member(path)
        payload = z.read(path)
        dest = source_dir / path; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(payload)
        row['sourceHashes'][path] = hashlib.sha256(payload).hexdigest()
    row['geometryChecks'] = validate_geometry(data, p.parent)
    positions, triangles = model_geometry(data, lambda uri: (p.parent / uri).read_bytes())
    if not len(positions) or not np.isfinite(positions).all():
        raise ValueError('Empty/non-finite transformed positions')
    row.update(worldBounds=[positions.min(axis=0).tolist(), positions.max(axis=0).tolist()], triangles=triangles, vertices=len(positions), terrainSamples=samples(positions))
    row['matching'] = match_source(positions, model_id, by_ref)
    glb, stats = _packer.pack(p)
    if stats['triangles'] != triangles:
        raise UnsupportedSource('Mesh instancing/unreferenced meshes need a scene-aware packer triangle contract')
    compressed = gzip.compress(glb, mtime=0); sha = hashlib.sha256(compressed).hexdigest()
    dest = out / 'assets' / (sha + '.glb.gz'); dest.parent.mkdir(exist_ok=True); dest.write_bytes(compressed)
    row['asset'] = {'asset': str(dest.relative_to(out)), 'sha256': sha, 'encoding': 'gzip', 'bytes': len(compressed), 'glbBytes': len(glb), 'decodedGeometryBytes': stats['decodedGeometryBytes'], 'indexedVertices': stats['vertices']}
    row['bitPreservation'] = stats['primitives']
    row['runtimeFormatChecks'] = {'requiredAttributes':row['geometryChecks']['runtimeAttributesCompatible'], 'positiveBounds':all(a<b for a,b in zip(*row['worldBounds'])), 'compressedBytesWithinLimit':len(compressed)<=32*1024*1024, 'decodedBytesWithinLimit':len(glb)<=128*1024*1024}
    if not all(row['runtimeFormatChecks'].values()):
        row.update(state='unsupported-source',holdReason='Native asset packed unchanged but current viewer format/size constraints require further work')
        return row
    matches = row['matching']['viewerMatches']
    unique_source = {m['buildingCSUID'] for m in row['matching']['officialMatches']}
    unique_match = len(matches) == 1 and len(unique_source) == 1 and None not in unique_source
    row['state'] = 'packed-needs-placement-review' if unique_match else 'source-match-held'
    if unique_match:
        row['candidate'] = {**matches[0], **row['asset'], 'modelId': model_id, 'worldBounds': row['worldBounds'], 'triangles': triangles, 'priority': 'unreviewed', 'placementReviewed': False, 'publicationApproved': False}
    else:
        row['holdReason'] = 'No unique explicit viewer polygon match; packed geometry retained without assigning a replacement UID'
    return row


# Each orchestration process reuses one Node sampler across sequential sheets.
# No per-model process launch; no DB/renderer state is mutated by this worker.
_terrain_worker = None

def _close_terrain_worker():
    global _terrain_worker
    if _terrain_worker is not None:
        _terrain_worker.kill()
        _terrain_worker.wait(timeout=5)
        _terrain_worker = None

atexit.register(_close_terrain_worker)

def _terrain_check(node, points, report):
    global _terrain_worker
    if _terrain_worker is None or _terrain_worker.poll() is not None:
        _terrain_worker = subprocess.Popen([node, str(HERE/'terrain-check.mjs'), '--server'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
    try:
        _terrain_worker.stdin.write(json.dumps({'input':str(points.resolve()),'output':str(report.resolve())})+'\n')
        _terrain_worker.stdin.flush()
        if not select.select([_terrain_worker.stdout], [], [], 300)[0]:
            raise TimeoutError('Batched terrain sampler exceeded 300 seconds')
        line = _terrain_worker.stdout.readline()
        response = json.loads(line) if line else {'ok':False,'error':'Terrain sampler exited before replying'}
        if not response.get('ok'):
            raise RuntimeError(response.get('error','Terrain sampler failed'))
        return json.loads(report.read_text())
    except Exception:
        _close_terrain_worker()
        raise


def _stage_terrain(z, download, official_path, out, key):
    """Reuse the exact existing geometry-only terrain preparer, one source at a time."""
    rows=[]; entries=[e for e in z.infolist() if not e.is_dir() and e.filename.startswith('TERRAIN') and e.filename.lower().endswith('.gltf')]
    counts=Counter(e.filename for e in z.infolist())
    for ordinal,entry in enumerate(sorted(entries,key=lambda e:e.filename)):
        rid=hashlib.sha256((str(ordinal)+':'+entry.filename).encode()).hexdigest()[:24]
        dest=out/'native-terrain'/rid; checkpoint=dest/'outcome.json'
        previous=json.loads(checkpoint.read_text()) if checkpoint.exists() else None
        valid=previous and previous.get('inputKey')==key
        if valid:
            for item in previous.get('preparedFiles',[]):
                path=dest/item['path']
                if not path.is_file() or digest(path)!=item['sha256']:
                    valid=False;break
        if valid:
            rows.append(previous);continue
        row={'sourceEntry':entry.filename,'inputKey':key,'state':'failed','photosOmitted':True,'terrainPublished':False}
        try:
            safe_member(entry.filename)
            if counts[entry.filename]!=1:raise ValueError('Duplicate terrain source entry')
            data=json.loads(z.read(entry));folder=PurePosixPath(entry.filename).parent
            paths=[entry.filename]+[str(folder/safe_member(b['uri'])) for b in data.get('buffers',[])]
            if any(counts[p]!=1 for p in paths):raise ValueError('Missing/duplicate terrain binary dependency')
            dest.mkdir(parents=True,exist_ok=True)
            # Derived archive is an isolation mechanism only. Provenance points to
            # the retained original compact cache, whose selected member bytes match.
            with tempfile.TemporaryDirectory(prefix='terrain-stage-',dir=out) as temp:
                subset=Path(temp)/'terrain.zip'
                with zipfile.ZipFile(subset,'w',zipfile.ZIP_STORED) as selected:
                    for path in paths:
                        value=z.read(path);selected.writestr(path,value)
                        local=Path(temp)/path;local.parent.mkdir(parents=True,exist_ok=True);local.write_bytes(value)
                validate_geometry(data,(Path(temp)/entry.filename).parent,allow_terrain_textures=True)
                manifest=stage(subset,download,official_path,dest)
            if not manifest['terrain']:raise ValueError('Existing preparer returned no terrain')
            terrain=manifest['terrain'];prepared=[]
            for path in ['manifest.json',terrain['url']]+[p for p in terrain['sourceHashes'] if p.endswith('.bin')]:
                prepared.append({'path':path,'sha256':digest(dest/path),'bytes':(dest/path).stat().st_size})
            row.update(state='prepared-geometry-only',manifest='manifest.json',sourceHashes=terrain['sourceHashes'],worldBounds=terrain['worldBounds'],triangles=terrain['triangles'],vertices=terrain['vertices'],omittedPhotoEntries=terrain['omittedPhotoEntries'],preparedFiles=prepared)
        except Exception as e:
            row['error']=f'{type(e).__name__}: {e}'
        write(checkpoint,row);rows.append(row)
    write(out/'terrain-outcomes.json',{'rows':rows,'counts':dict(Counter(r['state'] for r in rows)),'sourceTerrainModels':len(rows),'terrainPublished':False})
    return rows


def convert_sheet(archive: Path, download: dict, official_path: Path, out: Path) -> dict:
    archive, official_path, out = map(Path, (archive, official_path, out))
    out.mkdir(parents=True, exist_ok=True)
    archive_hash = digest(archive)
    if download.get('sha256') and archive_hash != download['sha256']:
        raise ValueError('Compact archive SHA differs from supplied download record')
    raw = official_path.read_bytes(); raw = gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw
    official = json.loads(raw); by_ref = defaultdict(list); official_errors = []
    for i, f in enumerate(official['features']):
        try:
            shape = official_shape(f)
            if shape.is_empty or shape.area<=0:
                raise ValueError('Empty/zero-area official footprint')
            by_ref[str(f['attributes'].get('GeoRefNo', ''))].append((f, shape))
        except Exception as e:
            official_errors.append({'featureIndex': i, 'objectId': f.get('attributes', {}).get('OBJECTID'), 'error': f'{type(e).__name__}: {e}'})
    code_paths = converter_dependencies()
    fingerprint = {'archiveSHA256': archive_hash, 'officialSHA256': hashlib.sha256(raw).hexdigest(), 'codeSHA256': {p.name: digest(p) for p in code_paths}, 'version': VERSION, 'download': download}
    key = hashlib.sha256(json.dumps(fingerprint, sort_keys=True).encode()).hexdigest()
    rows = []; reused = 0
    with zipfile.ZipFile(archive) as z:
        entries = sorted([i for i in z.infolist() if not i.is_dir() and i.filename.upper().startswith('BUILDING/') and i.filename.lower().endswith('.gltf')], key=lambda i: i.filename)
        multiplicity = Counter(i.filename for i in z.infolist())
        for ordinal, entry in enumerate(entries):
            rid = hashlib.sha256((str(ordinal) + ':' + entry.filename).encode()).hexdigest()[:24]
            checkpoint = out/'models'/(rid+'.json')
            previous = json.loads(checkpoint.read_text()) if checkpoint.exists() else None
            valid = previous and previous.get('inputKey') == key
            if valid and previous.get('asset'):
                asset = out/previous['asset']['asset']; valid = asset.exists() and digest(asset) == previous['asset']['sha256']
            if valid:
                row = previous; reused += 1
            else:
                row = {'sourceEntry': entry.filename, 'sourceZipCRC32': entry.CRC, 'sourceBytes': entry.file_size, 'modelId': PurePosixPath(entry.filename).stem, 'state': 'failed', 'placementReviewed': False, 'publicationApproved': False}
                try:
                    if multiplicity[entry.filename] != 1:
                        raise ValueError('Duplicate source ZIP entry')
                    # Dependency duplicates cannot be resolved by zipfile's last-entry behaviour.
                    data = json.loads(z.read(entry))
                    folder = PurePosixPath(entry.filename).parent
                    for b in data.get('buffers', []):
                        if multiplicity[str(folder/safe_member(b['uri']))] != 1:
                            raise ValueError('Missing/duplicate source buffer entry')
                    with tempfile.TemporaryDirectory(prefix='native-model-', dir=out) as temp:
                        row = _convert_one(z, entry, Path(temp), out, by_ref, row)
                except Exception as e:
                    row.update(state='unsupported-source' if isinstance(e, UnsupportedSource) else 'failed', error=f'{type(e).__name__}: {e}')
                row.update(inputKey=key, outcomeId=rid, sourceTile=download['sheet'], sourceTileRevision=download.get('revisionDate'))
                write(checkpoint, row)
            rows.append(row)
        terrain_sources = _stage_terrain(z, download, official_path, out, key)
    # Two same-sheet native models must not silently race for one fallback part.
    by_uid = defaultdict(list)
    for row in rows:
        if row.get('candidate'):
            by_uid[row['candidate']['uid']].append(row)
    for group in by_uid.values():
        if len(group) > 1:
            for row in group:
                row.update(state='source-match-held', holdReason='Multiple native entries target the same viewer UID; assembly review required')
                row['candidate']['publicationApproved'] = False
    # One actual runtime sampler invocation for the sheet, never one process/model.
    points = out/'terrain-samples.jsonl'
    with points.open('w') as f:
        for row in rows:
            if row.get('terrainSamples'):
                f.write(json.dumps({'outcomeId':row['outcomeId'], **row['terrainSamples']}, separators=(',', ':'))+'\n')
    node = os.environ.get('CITYWIDE_NODE') or shutil.which('node')
    terrain_report = out/'terrain-check.json'
    terrain = {'status': 'unavailable', 'reason': 'Node runtime unavailable', 'rows': []}
    if node:
        try:
            terrain = _terrain_check(node, points, terrain_report)
        except Exception as e:
            terrain = {'status':'unavailable', 'reason':f'{type(e).__name__}: {e}', 'rows':[]}
    write(terrain_report, terrain); terrain_rows = {r['outcomeId']:r for r in terrain.get('rows', [])}
    for row in rows:
        row['terrainCheck'] = terrain_rows.get(row['outcomeId'], {'status':'not-checked', 'reason':terrain.get('reason', 'Model geometry was not available')})
        write(out/'models'/(row['outcomeId']+'.json'), row)
    with (out/'outcomes.jsonl').open('w') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n')
    models = [{**r['candidate'], 'sourceTile':download['sheet'], 'sourceTileRevision':download.get('revisionDate')} for r in rows if r['state']=='packed-needs-placement-review']
    catalogue = {'schemaVersion':1, 'kind':'staged-official-model-catalogue', 'area':download['sheet'], 'datasetId':'landsd_rcd_1742809441342_98380', 'crs':'EPSG:2326', 'verticalDatum':'Hong Kong Principal Datum', 'rootTranslation':[-834500,0,816500], 'coordinatePolicy':'Unchanged native source nodes/float bits; one city translation, no terrain draping or vertical multiplier', 'loadingPolicy':'Mechanical candidates only; source/terrain/browser review required before publication', 'counts':{'packedModels':len(models)}, 'models':models}
    write(out/'catalogue.json', catalogue)
    expected = download.get('expectedModels')
    summary = {'expectedModels':expected, 'modelCountMatchesExpected':expected is None or expected == len(rows), 'schemaVersion':1, 'sheet':download['sheet'], 'inputKey':key, 'inputs':fingerprint, 'sourceModels':len(rows), 'sourceTerrainModels':len(terrain_sources), 'terrainOutcomes':dict(Counter(r['state'] for r in terrain_sources)), 'outcomes':dict(Counter(r['state'] for r in rows)), 'reusedModels':reused, 'candidateModels':len(models), 'packedAssets':sum(bool(r.get('asset')) for r in rows), 'compressedBytes':sum(r.get('asset', {}).get('bytes',0) for r in rows), 'officialFeatureErrors':official_errors, 'terrainStatus':terrain['status'], 'terrainReportSHA256':digest(terrain_report), 'outcomesSHA256':digest(out/'outcomes.jsonl'), 'catalogueSHA256':digest(out/'catalogue.json'), 'published':False, 'placementApproved':False, 'verticalScale':1}
    assert sum(summary['outcomes'].values()) == summary['sourceModels']
    write(out/'summary.json', summary)
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('archive',type=Path); p.add_argument('download',type=Path); p.add_argument('official',type=Path); p.add_argument('out',type=Path)
    a=p.parse_args(); s=convert_sheet(a.archive,json.loads(a.download.read_text()),a.official,a.out)
    print(json.dumps({k:v for k,v in s.items() if k not in ('inputs','officialFeatureErrors')}))

if __name__ == '__main__':
    main()
