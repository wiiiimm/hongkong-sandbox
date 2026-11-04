"""Preserve freshly acquired government terrain as new source identities only."""
from pathlib import Path
import zipfile
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from urllib.parse import urlsplit

BASE = ROOT / 'docs/astra-city/government-import'
B = 'government-xl-fresh-terrain-candidates-v1-20261023'
D, LOCAL = BASE / B, HERE / 'local' / B
N = {v: 'government-xl-missing-original-terrain-restore-v' + str(v) + '-20261023' for v in [3, 4]}


def main():
    assert not D.exists()
    refs, pins = [Path(__file__)], {}
    for v, name in N.items():
        _, pins[v] = authenticate(BASE / name)
        refs.append(BASE / name / 'result.json')
    def take(v, path):
        assert digest(path.read_bytes()) == pins[v][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    prior = take(3, BASE / N[3] / 'summary.json')
    updates = {r['cacheKey']: r for r in take(4, BASE / N[4] / 'summary.json')['rows']}
    rootname = 'government-xl-recovered-terrain-root-check-v1-20261023'
    _, rootpins = authenticate(BASE / rootname)
    rp = BASE / rootname / 'summary.json'
    assert digest(rp.read_bytes()) == rootpins[str(rp.relative_to(ROOT))]
    refs += [BASE / rootname / 'result.json', rp]
    root = read(rp)
    outcomes = []
    for row in prior['rows']:
        if row['error'] is None:
            continue
        key, sheet = row['cacheKey'], row['sheet']
        v = 4 if key in updates else 3
        oldfolder = HERE / 'local' / N[v] / key
        record = take(v, oldfolder / 'download/download.json')
        directory = take(v, oldfolder / 'directory/result.json')
        archive = oldfolder / 'download' / (sheet + '.zip')
        assert digest(archive.read_bytes()) == record['sha256'] == pins[v][str(archive.relative_to(ROOT))]
        assert record['sourceETag'] == directory['etag'] and record['directorySHA256'] == directory['directorySHA256']
        assert urlsplit(record['source']).hostname == 'download.map.gov.hk' and urlsplit(record['source']).scheme == 'https'
        assert record['terrainGeometryIncluded'] and record['dependencyScanVersion'] == 1
        refs.append(archive)
        files, error = {}, None
        try:
            members = [r for r in record['entries'] if r['name'].startswith('TERRAIN') and Path(r['name']).suffix in ['.gltf', '.bin']]
            assert members
            with zipfile.ZipFile(archive) as z:
                names = z.namelist()
                for member in members:
                    name = member['name']
                    assert not Path(name).is_absolute() and '..' not in Path(name).parts and '\\' not in name
                    assert names.count(name) == 1 and z.getinfo(name).file_size == member['bytes'] < 100_000_000
                    raw = z.read(name)
                    assert digest(raw) == member['sha256']
                    path = LOCAL / key / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(raw)
                    files[name] = dict(path=str(path.relative_to(ROOT)), sha256=member['sha256'])
                    refs.append(path)
            for name, q in files.items():
                if not name.endswith('.gltf'):
                    continue
                path = ROOT / q['path']
                for buffer in read(path).get('buffers', []):
                    binary = (path.parent / buffer['uri']).resolve()
                    assert binary.is_relative_to((LOCAL / key).resolve())
                    assert str(binary.relative_to(LOCAL / key)) in files
        except Exception as exc:
            error = dict(type=type(exc).__name__, reason=str(exc))
        result = dict(cacheKey=key, sheet=sheet, sourceETag=directory['etag'], sourceDirectorySHA256=directory['directorySHA256'], files=files, error=error, status='fresh-government-terrain-source-candidate' if error is None else 'fresh-terrain-parse-investigation', oldTerrainAcceptanceTransferred=False, installationApproved=False)
        save(D / (key + '.json'), result)
        outcomes.append(result)
        print(dict(sheet=sheet, files=len(files), error=error), flush=True)
    keys = {r['cacheKey'] for r in outcomes}
    selected = [r for r in root['rows'] if r['nativeCacheKey'] in keys]
    assert len(selected) == root['heldModels']
    summary = dict(uids=sorted(r['uid'] for r in selected), rows=outcomes, selectedModels=len(selected), sourceSheets=len(outcomes), candidateSheets=sum(r['error'] is None for r in outcomes), sourceGeometryChanges=0, newlyInstalled=0, installationApproved=False, qualification='Untouched original government terrain from current revision-fenced archive downloads. Fresh hashes/ETags/directories are new terrain source identities, not restoration or approval of historical terrain. Original building assets/pose remain unchanged. Compatibility with each old building/current neighbour/rendered scene remains unproven and requires all normal checks.')
    save(D / 'summary.json', summary)
    module('fresh_terrain_candidates_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B, 'fresh-government-terrain-source-candidates', refs, summary)


if __name__ == '__main__':
    main()
