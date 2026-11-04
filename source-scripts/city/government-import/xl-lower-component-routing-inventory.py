"""Find untested exact-form lower components; metadata routing, never acceptance.

Shared parent/OSM records, recorded elevations and overlapping source footprints
only nominate a physical check. Original source identities, exact meshes and
complete support interfaces remain mandatory. No queues or skip credit.
"""
import argparse
from collections import defaultdict
from pathlib import Path
from shapely.geometry import Polygon
from run import ROOT, read, save, digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--count', required=True)
    p.add_argument('--batch', required=True)
    a = p.parse_args()
    assert Path(a.batch).name == a.batch and a.batch.startswith('government-xl-')
    doc = ROOT / 'docs/astra-city/government-import' / a.batch
    assert not doc.exists()
    count_path = ROOT / a.count
    count = read(count_path)
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest_path.read_bytes()) == count['manifestSHA256']
    manifest = read(manifest_path)
    wanted = {r['uid'] for r in count['rows'] if not r['installedVerified'] and r.get('uid')}
    forms, parents, refs = {}, defaultdict(list), []
    for tile in manifest['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        refs.append({'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())})
        for b in read(path)['buildings']:
            assert b['uid'] not in forms
            forms[b['uid']] = b
            if b.get('parent'):
                parents[b['parent']].append(b)
    checked = set()
    for path in sorted(doc.parent.rglob('support-checks.json.gz')):
        refs.append({'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())})
        for r in read(path).get('rows', []):
            if 'uid' in r and 'supportUid' in r:
                checked.add((r['uid'], r['supportUid']))
    polygons = {}
    def polygon(b):
        if b['uid'] not in polygons:
            polygons[b['uid']] = Polygon(b['rings'][0], b['rings'][1:])
        return polygons[b['uid']]
    candidates, disjoint, invalid = [], 0, []
    for uid in sorted(wanted & forms.keys()):
        b = forms[uid]
        if b.get('baseHeightHKPD') is None or b.get('structureType') not in ('Tower', 'Podium'):
            continue
        for lower in parents[b.get('parent')]:
            pair = (uid, lower['uid'])
            if pair[0] == pair[1] or pair in checked:
                continue
            if lower.get('structureType') not in ('Tower', 'Podium'):
                continue
            if not set(b.get('osmRefs', [])) & set(lower.get('osmRefs', [])):
                continue
            if lower.get('baseHeightHKPD') is None or lower.get('topHeightHKPD') is None:
                continue
            if not (lower['baseHeightHKPD'] < b['baseHeightHKPD'] and
                    lower['topHeightHKPD'] >= b['baseHeightHKPD'] - .5):
                continue
            bp, lp = polygon(b), polygon(lower)
            if not bp.is_valid or not lp.is_valid:
                invalid.append({'uid': uid, 'supportUid': lower['uid']})
                continue
            area = bp.intersection(lp).area
            if area <= 1e-8:
                disjoint += 1
                continue
            candidates.append({'uid': uid, 'supportUid': lower['uid'],
                'name': b.get('name'), 'supportName': lower.get('name'),
                'type': b['structureType'], 'supportType': lower['structureType'],
                'baseHKPD': b['baseHeightHKPD'], 'supportBaseHKPD': lower['baseHeightHKPD'],
                'supportTopHKPD': lower['topHeightHKPD'], 'footprintIntersectionM2': area})
    refs.extend({'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}
                for path in (count_path, manifest_path, Path(__file__)))
    result = {'batch': a.batch, 'indexedRemaining': count['counts']['remaining'],
        'currentFormRemaining': len(wanted & forms.keys()), 'pairs': candidates,
        'disjointMetadataPairs': disjoint, 'invalidPolygons': invalid, 'inputRefs': refs,
        'publication': False, 'newlyInstalled': 0, 'queuesCreated': 0,
        'qualification': 'Novel lower-component lookup candidates only. Parent, elevation and footprint intersection are not source identity or physical support approval. Completed pair checks are not repeated.'}
    save(doc / 'inventory.json', result)
    print({k: v for k, v in result.items() if k not in ('inputRefs', 'pairs')}, flush=True)
    print({'pairs': candidates}, flush=True)


if __name__ == '__main__':
    main()
