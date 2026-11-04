"""Acquire untouched INFRASTRUCTURE source units omitted by BUILDING-only staging."""
import argparse
import gzip
import json
import shutil
import sys
import uuid
import zipfile
from pathlib import Path, PurePosixPath
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-southside-original-infrastructure-recovery-v1-20261028'
DOC, LOCAL = BASE/BATCH, HERE/'local'/BATCH
LEASE = LOCAL/'reservation.json'
PROVENANCE = BASE/'government-xl-southside-source-gap-provenance-v1-20261028'
GROUND = BASE/'government-xl-la-marina-southside-original-terrain-v1-20261028'
MASK = BASE/'government-xl-southside-source-bound-terrain-mask-v1-20261028'


def owned():
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists() and shutil.disk_usage(ROOT).free >= 2*1024**3
    refs, pins = [Path(__file__)], {}
    for batch in [PROVENANCE, GROUND, MASK]:
        _, bound = authenticate(batch)
        refs.append(batch/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    census = take(PROVENANCE/'summary.json')
    inputs = take(GROUND/'source-inputs.json')['inputs']
    mask = take(MASK/'summary.json')
    projection = shapely.from_wkt(mask['sourceProjectionWKT'])
    acquisition = module('southside_original_infrastructure_download', HERE.parent/'citywide-native/download.py')
    conversion = module('southside_original_infrastructure_convert', HERE.parent/'citywide-native/convert.py')
    context = module('southside_original_infrastructure_context', HERE/'pending-context.py')
    refs.extend([Path(acquisition.__file__), Path(acquisition.ac.__file__), Path(conversion.__file__),
                 Path(conversion._packer.__file__), Path(context.__file__)])
    rows, errors, sheets = [], [], []
    for record in census['archiveCategoryCensus']:
        sheet = record['sheet']
        assert 'source-infrastructure:' + sheet in lease['resources'] and reservations.owns(lease)
        directory = ROOT/record['directory']['path']
        assert digest(directory.read_bytes()) == record['directory']['sha256'] == inputs[sheet]['directory']['directorySHA256']
        refs.append(directory)
        entries, _ = acquisition.ac.parse_directory(directory.read_bytes())
        selected = [name for name in record['otherGeometryEntries'] if name.upper().startswith('INFRASTRUCTURE/')]
        assert len(selected) == record['glTFByTopLevelCategory'].get('INFRASTRUCTURE', 0)
        models = []
        for name in selected:
            prefix = str(PurePosixPath(name).parent) + '/'
            members = [e for e in entries if e.filename.startswith(prefix) and e.filename.lower().endswith(('.gltf', '.bin'))]
            models.append(dict(modelId=PurePosixPath(name).stem, members=[dict(name=e.filename, crc32=e.CRC,
                               headerOffset=e.header_offset, compressedBytes=e.compress_size, decodedBytes=e.file_size) for e in members]))
        compressed = sum(m['compressedBytes'] for model in models for m in model['members'])
        assert compressed <= 32*1024**2, 'Infrastructure source batch exceeds bounded acquisition budget'
        row = {**inputs[sheet]['directory'], 'models': models}
        folder = LOCAL/'sheets'/sheet
        folder.mkdir(parents=True)
        save(folder/'source-directory-selection.json', row)
        print(dict(sheet=sheet, infrastructureUnits=len(models), selectedCompressedBytes=compressed), flush=True)
        try:
            downloaded = acquisition.acquire(row, directory, folder/'original')
        except Exception as error:
            errors.append(dict(sheet=sheet, type=type(error).__name__, reason=str(error)[:250]))
            continue
        sheets.append(dict(sheet=sheet, receivedBytes=downloaded['newThisInvocationBytes'], archiveSHA256=downloaded['sha256']))
        archive = folder/'original'/(sheet + '.zip')
        with zipfile.ZipFile(archive) as sourcezip:
            for name in selected:
                model_id = PurePosixPath(name).stem
                source_key = 'infrastructure:' + record['directory']['sha256'] + '/' + model_id
                data = json.loads(sourcezip.read(name))
                paths = [name] + [acquisition.safe(str(PurePosixPath(name).parent/b['uri'])) for b in data['buffers']]
                for member in paths:
                    dest = folder/'decoded'/acquisition.safe(member)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(sourcezip.read(member))
                    refs.append(dest)
                gltf = folder/'decoded'/name
                try:
                    tri = context.triangles(gltf)
                    assert np.isfinite(tri).all()
                    low, high = tri.min((0, 1)), tri.max((0, 1))
                    bounds = shapely.box(low[0], low[2], high[0], high[2])
                    item = dict(sourceUnitKey=source_key, sourceKind='INFRASTRUCTURE', modelId=model_id, sheet=sheet,
                                sourceDirectorySHA256=record['directory']['sha256'], sourceEntry=name,
                                rawGLTF=dict(path=str(gltf.relative_to(ROOT)), sha256=digest(gltf.read_bytes())),
                                completeFaces=len(tri), originalWorldSHA256=digest(tri.astype('<f8').tobytes()),
                                worldBounds=[low.tolist(), high.tolist()],
                                boundsTouchProject=not bounds.disjoint(projection),
                                boundingProjectOverlapM2=bounds.intersection(projection).area,
                                viewerBuildingUid=None, identityAccepted=False, supportAccepted=False, installationApproved=False)
                    try:
                        glb, stats = conversion._packer.pack(gltf)
                        assert stats['triangles'] == len(tri)
                        packed = gzip.compress(glb, mtime=0)
                        asset = folder/'packed/assets'/(digest(packed) + '.glb.gz')
                        asset.parent.mkdir(parents=True, exist_ok=True); asset.write_bytes(packed)
                        refs.append(asset)
                        item['packedOriginal'] = dict(path=str(asset.relative_to(ROOT)), sha256=digest(packed), bytes=len(packed),
                                                      glbBytes=len(glb), triangles=stats['triangles'])
                    except Exception as error:
                        item['packingError'] = dict(type=type(error).__name__, reason=str(error)[:250])
                    rows.append(item)
                except Exception as error:
                    errors.append(dict(sourceUnitKey=source_key, type=type(error).__name__, reason=str(error)[:250]))
                assert reservations.owns(lease)
        refs.extend(p for p in (folder/'original').rglob('*') if p.is_file() and p.suffix not in ['.zip', '.bin'])
        refs.append(folder/'source-directory-selection.json')
    result = dict(uids=['landsd/315025:0'], expectedInfrastructureUnits=15, originalUnits=rows, errors=errors,
                  recoveredUnits=len(rows), packedUnits=sum('packedOriginal' in r for r in rows), sourceTransfers=sheets,
                  boundsTouchingProject=[r['sourceUnitKey'] for r in rows if r['boundsTouchProject']],
                  sourceGeometryChanges=0, physicalAccepted=False, identityAccepted=False, installationApproved=False,
                  qualification='Exact pinned original INFRASTRUCTURE glTF/buffer members, official archive CRC/range checks through the unchanged acquisition helper, complete scene-node transforms and geometry-only packing. Source-unit keys are typed archive identities, never invented Building UIDs. Bounds are nominations only; no infrastructure role, source-model support, current-map placement, runtime/browser or publication acceptance. No AI geometry generation, vertex/pose edits or optimisation work.')
    save(DOC/'summary.json', result)
    assert reservations.owns(lease)
    module('southside_original_infrastructure_recovery_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'original-government-infrastructure-layer-acquisition-diagnostic', list(dict.fromkeys(refs)), result)
    print(dict(recovered=len(rows), packed=result['packedUnits'], boundsTouching=len(result['boundsTouchingProject']), errors=errors), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    if args.owned:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    authenticate(PROVENANCE)
    records = read(PROVENANCE/'summary.json')['archiveCategoryCensus']
    claim = reservations.claim('southside-original-infrastructure-' + str(uuid.uuid4()),
                               ['source-infrastructure:' + r['sheet'] for r in records], batch=BATCH, ttl=3600)
    assert claim['ok']
    execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])


if __name__ == '__main__':
    main()
