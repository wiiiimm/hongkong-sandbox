"""Rebind an explicit bounded set of cached originals to unchanged current forms."""
import argparse
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--capture', required=True)
    p.add_argument('--uid', action='append', required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    wanted = set(a.uid)
    assert 0 < len(wanted) == len(a.uid) <= 40
    base = ROOT / 'docs/astra-city/government-import'
    doc, prior = base / a.batch, base / a.capture
    assert not doc.exists()
    _, pins = authenticate(prior)
    selection = prior / 'selection.json.gz'
    assert digest(selection.read_bytes()) == pins[str(selection.relative_to(ROOT))]
    rows = [r for r in read(selection)['rows'] if r['uid'] in wanted]
    assert len(rows) == len(wanted) and {r['uid'] for r in rows} == wanted
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_sha = digest(manifest.read_bytes())
    tiles = {t['url'] for t in read(manifest)['tiles']}
    refs = [Path(__file__), prior / 'result.json', selection, manifest]
    sources = {}
    for row in rows:
        uid = row['uid']
        asset = ROOT / row['candidate']['path']
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == row['candidate']['entry']['sha256']
        assert row['candidate']['entry']['uid'] == uid and row['source']['tile'] in tiles
        assert digest(tile.read_bytes()) == row['source']['tileSHA256']
        assert [b for b in read(tile)['buildings'] if b['uid'] == uid] == [row['source']['building']]
        sources[uid] = row['sourceSHA256']
        refs.extend([asset, tile])
    assert digest(manifest.read_bytes()) == manifest_sha
    output = doc / 'selection.json.gz'
    save(output, dict(rows=rows, manifestSHA256=manifest_sha))
    refs.append(output)
    result = dict(uids=sorted(wanted), sourceSHA256ByUid=sources, sourceSelectionOnly=True,
                  installationApproved=False, publication=False, newlyInstalled=0,
                  qualification='Exact historical source bytes, complete current tile hashes and unchanged form tuples rebound for immediate checks. No historical current-scene, terrain, physical, neighbour or publication approval transfers.')
    save(doc / 'summary.json', result)
    module('current_sources_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'current-exact-original-source-selection', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
