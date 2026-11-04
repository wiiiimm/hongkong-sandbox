"""Look up exact cached originals for explicitly selected current adjacent forms."""
import argparse
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'capture', 'scope', 'owner']:
        p.add_argument('--' + k, required=True)
    p.add_argument('--related', action='append', required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    assert len(set(a.related)) == len(a.related) <= 20
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / a.batch
    assert not doc.exists()
    refs, pins = [Path(__file__)], {}
    for batch in [a.capture, a.scope]:
        _, bound = authenticate(base / batch)
        pins.update(bound)
        refs.append(base / batch / 'result.json')

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    source = next(r for r in take(base / a.capture / 'selection.json.gz')['rows'] if r['uid'] == a.owner)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[str(manifest.relative_to(ROOT))];refs.append(manifest)
    items=take(base/a.scope/(a.owner.split('/')[1]+'-forms.json.gz'))
    forms={r['building']['uid']:r['building']for r in items}
    for r in items:
        tile=ROOT/'3d-viewer'/r['tile'];assert digest(tile.read_bytes())==r['tileSHA256']and [f for f in read(tile)['buildings']if f['uid']==r['building']['uid']]==[r['building']];refs.append(tile)
    assert set(a.related) <= set(forms)
    key = source['native']['cacheKey']
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        sha, native = db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s', (key,)).fetchone()
        assert sha == source['native']['resultSha']
    rows = []
    for uid in a.related:
        form = forms[uid]
        matches = [m for m in native['models'] if any(
            r['uid'] == uid and r.get('buildingCSUID') == form.get('buildingCSUID')
            for r in m.get('matching', {}).get('viewerMatches', []))]
        rows.append(dict(uid=uid, currentForm=form, matchedOriginalModels=matches,
                         matchCount=len(matches), identityAccepted=False))
    result = dict(uids=[a.owner], relatedUIDs=a.related, nativeCacheKey=key,
                  nativeResultSHA256=sha, rows=rows, sourceGeometryChanges=0,
                  installationApproved=False, permanentRejection=False,
                  qualification='Exact cached model-to-current UID and CSUID lookup only. Shared map parent, footprint overlap or a matching source record grants no support, ownership, identity acceptance or installation credit.')
    save(doc / 'lookup.json', result)
    module('explicit_adjacent_lookup_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'explicit-adjacent-original-source-lookup', refs, result)
    print([dict(uid=r['uid'], name=r['currentForm'].get('name'), matches=[(m['modelId'], m['triangles']) for m in r['matchedOriginalModels']]) for r in rows], flush=True)


if __name__ == '__main__':
    main()
