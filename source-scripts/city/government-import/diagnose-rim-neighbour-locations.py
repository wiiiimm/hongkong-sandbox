"""Read-only location comparison; proximity never grants support or identity credit."""
import argparse
from pathlib import Path
from shapely.geometry import Polygon, Point, MultiPoint
from run import ROOT, read, save, digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rim', required=True); p.add_argument('--neighbours', required=True)
    p.add_argument('--uid', action='append', required=True); p.add_argument('--out', required=True)
    args = p.parse_args()
    rim_path, neighbours_path = ROOT / args.rim, ROOT / args.neighbours
    data, neighbours = read(rim_path), read(neighbours_path)
    for path, pinned in data['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == pinned, path
    forms = {r['building']['uid']: r['building'] for r in neighbours['rows'] if r['building']['uid'] in args.uid}
    assert set(forms) == set(args.uid)
    polygons = {uid: Polygon(b['rings'][0], b['rings'][1:]) for uid, b in forms.items()}
    for row in data['rows']:
        for q in row['points']:
            point = Point(q['point'][0], q['point'][2])
            q['neighbourDistancesM'] = {uid: point.distance(poly) for uid, poly in polygons.items()}
        row['failed'] = [q for q in row['points'] if q['candidateGap'] > 1 or q['candidateGap'] < -.5]
        failed = row['failed']
        row['summary'] = {'failedSamples': len(failed), 'forms': {
            uid: {'bounds': list(poly.bounds), 'areaM2': poly.area,
                  'minRimDistanceM': min(q['neighbourDistancesM'][uid] for q in row['points']),
                  'minFailedDistanceM': min((q['neighbourDistancesM'][uid] for q in failed), default=None)}
            for uid, poly in polygons.items()},
            'failedPointBounds': list(MultiPoint([(q['point'][0], q['point'][2]) for q in failed]).bounds) if failed else None,
            'failedCurrentGapRange': [min(q['currentGap'] for q in failed), max(q['currentGap'] for q in failed)] if failed else None}
    inputs = {str(path.relative_to(ROOT)): digest(path.read_bytes()) for path in [rim_path, neighbours_path, Path(__file__).resolve()]}
    save(ROOT / args.out, {'rows': data['rows'], 'inputHashes': inputs, 'publication': False, 'modelGeometryChanges': 0,
                          'scriptExternalAICalls': 0, 'qualification': 'Exact point-to-footprint distances only; no support, identity or installation credit.'})
    print([r['summary'] for r in data['rows']])


if __name__ == '__main__':
    main()
