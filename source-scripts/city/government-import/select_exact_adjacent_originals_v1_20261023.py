"""Select an original source and recovered adjacent originals, without approval."""
import argparse
from copy import deepcopy
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'capture', 'acquire']:
        p.add_argument('--' + k, required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / a.batch
    assert not doc.exists()
    refs, pins = [Path(__file__)], {}
    for batch in [a.capture, a.acquire]:
        _, bound = authenticate(base / batch)
        pins.update(bound)
        refs.append(base / batch / 'result.json')

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = deepcopy(take(base / a.capture / 'selection.json.gz'))
    recovered = take(base / a.acquire / 'summary.json')
    assert recovered['sourceRecovered']
    rows = selection['rows']
    assert rows and all(r['native']['cacheKey'] == recovered['nativeCacheKey'] for r in rows)
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifestpath.read_bytes()) == selection['manifestSHA256']
    manifest = read(manifestpath)
    refs.append(manifestpath)
    tiles = {t['id']: t['url'] for t in manifest['tiles']}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        sha, native = db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s', (recovered['nativeCacheKey'],)).fetchone()
        assert sha == recovered['nativeResultSHA256']
        sheet = db.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s', (recovered['nativeCacheKey'],)).fetchone()[0]
    for recovered_row in recovered['rows']:
        form = recovered_row['currentForm']
        tileurl = tiles[form['tile']]
        tile = ROOT / '3d-viewer' / tileurl
        assert [f for f in read(tile)['buildings'] if f['uid'] == form['uid']] == [form]
        refs.append(tile)
        model = next(m for m in native['models'] if m['modelId'] == recovered_row['model']['modelId'])
        assert model == recovered_row['model']
        entry = deepcopy(model['candidate'])
        assert entry['uid'] == form['uid'] and entry['sha256'] == recovered_row['sourceSHA256']
        assert not any(entry.get(k) for k in ['identityReviewApproved', 'placementReviewed', 'publicationApproved'])
        entry.update(proceduralWindows=False, rootTranslation=[-834500, 0, 816500], sourceTile=sheet,
                     sourceBaseHeight=form['baseHeightHKPD'], sourceTopHeight=form['topHeightHKPD'])
        rows.append(dict(uid=form['uid'], modelId=model['modelId'], triangles=model['triangles'],
                         sourceSHA256=entry['sha256'], originalGeometryOnly=True,
                         source=dict(building=form, tile=tileurl, tileSHA256=digest(tile.read_bytes())),
                         native=dict(cacheKey=recovered['nativeCacheKey'], resultSha=sha, model=model),
                         candidate=dict(path=recovered_row['asset']['path'], entry=entry)))
    assert len({r['uid'] for r in rows}) == len(rows)
    for row in rows:
        path = ROOT / row['candidate']['path']
        assert digest(path.read_bytes()) == row['sourceSHA256']
        refs.append(path)
    for url in manifest['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        assert not {r['uid'] for r in rows} & {m['uid'] for m in read(path)['models']}
        refs.append(path)
    save(doc / 'selection.json.gz', selection)
    result = dict(uids=[r['uid'] for r in rows], sourceSHA256ByUid={r['uid']: r['sourceSHA256'] for r in rows},
                  sourceGeometryChanges=0, installationApproved=False, identityAccepted=False)
    module('select_exact_adjacent_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'exact-adjacent-original-assembly-selection', refs, result)


if __name__ == '__main__':
    main()
