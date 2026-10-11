"""Fresh full checks for two exact original models on original government DTM.

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
from run import ROOT, HERE, read, save, digest, reservations, connect

BASE = Path('docs/astra-city/government-import/government-xl-original-dtm-two-current-inputs-20261007')
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


def owned(args, doc, local):
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    key = args.uid.split('/')[1].replace(':', '-')
    previous = ROOT / 'docs/astra-city/government-import' / ('government-xl-original-dtm-current-cell-20261007-' + key)
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
    assert 'replaces' not in old
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
        assert not (bb[0] < a[2] and bb[2] > a[0] and bb[1] < a[3] and bb[3] > a[1]), 'DTM root candidate overlaps installed terrain'
    native, proof = original_faces(old['bounds'])
    source = {'provider': 'Lands Department / Hong Kong SAR Government', 'sourceFiles': [{'path': str(SOURCE), 'sha256': SHA}],
        'crs': 'EPSG:2326', 'verticalDatum': 'HKPD', 'url': 'https://www.landsd.gov.hk/landsd_psi_data/SMO/data/Whole_HK_DTM_5m.zip',
        'limitation': 'Archival government 5 m DTM; source building and terrain revisions differ. All fresh physical checks required.'}
    patch = second.resolution.make_patch({'uids': [args.uid], 'cells': old_patch['coarseCells']}, parent, native, [source], terrain_triangle_budget=100000)
    path = local / (patch['id'] + '.json')
    save(path, patch)
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
    p.add_argument('--uid', required=True, choices=['landsd/121143:0', 'landsd/255543:0'])
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
    prev = ROOT / 'docs/astra-city/government-import' / ('government-xl-original-dtm-current-cell-20261007-' + key)
    uids = {r['building']['uid'] for r in read(prev / 'neighbour-inputs.json.gz')['rows']} | {args.uid}
    claim = reservations.claim('codex-xl-original-dtm-' + str(uuid.uuid4()), [('building:' if u.startswith('landsd/') else 'source-form:') + u for u in sorted(uids)], batch=args.batch)
    assert claim['ok'], claim
    save(local / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(local / 'reservation.json'), '--', sys.executable, __file__, '--uid', args.uid, '--batch', args.batch, '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
