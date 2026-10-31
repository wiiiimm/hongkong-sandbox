"""Bind two unchanged recovered originals to the current installed scene.

Historical selection is source provenance only; no acceptance transfers.
"""
from copy import deepcopy
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BATCH = 'government-xl-nam-cheong-after-island-selection-v1-20261023'
PRIOR = 'government-xl-nam-cheong-fu-yun-joint-current-v1-20261023-runtime'
EXPECTED = {'landsd/268867:0': 'ad26b1580c54a6700733a28643862ea7939f84c0254de9a2371f5aec91cae12d',
            'landsd/270874:0': '159453e8bc40543eb211dd9e0e2081e9796651051f430c935359e29b03ea31eb'}


def main():
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / BATCH
    assert not doc.exists()
    _, pins = authenticate(base / PRIOR)
    oldpath = base / PRIOR / 'selection.json.gz'
    assert digest(oldpath.read_bytes()) == pins[str(oldpath.relative_to(ROOT))]
    old = read(oldpath)
    rows = deepcopy(old['rows'])
    assert len(rows) == len(EXPECTED) and {r['uid'] for r in rows} == set(EXPECTED)
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    manifestsha = digest(manifestpath.read_bytes())
    manifest = read(manifestpath)
    refs = [Path(__file__), base / PRIOR / 'result.json', oldpath, manifestpath]
    installed = set()
    for url in manifest['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        installed.update(m['uid'] for m in read(path)['models'])
        refs.append(path)
    assert not installed & set(EXPECTED)
    for row in rows:
        assert row['sourceSHA256'] == EXPECTED[row['uid']]
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256']
        assert row['candidate']['entry']['sha256'] == row['sourceSHA256']
        assert row['candidate']['entry']['uid'] == row['uid']
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert digest(tile.read_bytes()) == pins[str(tile.relative_to(ROOT))]
        assert [b for b in read(tile)['buildings'] if b['uid'] == row['uid']] == [row['source']['building']]
        refs.extend([asset, tile])
    assert digest(manifestpath.read_bytes()) == manifestsha
    save(doc / 'selection.json.gz', dict(rows=rows, manifestSHA256=manifestsha))
    result = dict(uids=sorted(EXPECTED), sourceSHA256ByUid=EXPECTED,
                  priorManifestSHA256=old['manifestSHA256'], currentManifestSHA256=manifestsha,
                  unchangedCurrentForms=True, historicalApprovalTransferred=False,
                  qualification='Source provenance and exact current form/asset binding only. All current physical, identity, support, runtime, device and publication checks remain required.')
    save(doc / 'summary.json', result)
    module('nam_after_island_selection_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'unchanged-original-current-selection-rebind', refs, result)


if __name__ == '__main__':
    main()
