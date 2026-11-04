"""Rebind Block 1's already accepted basic podium without new model approval."""
from run import ROOT, HERE, read, save, digest, connect

TOWER = 'landsd/34255:0'
PODIUM = 'landsd/264935:0'
LEGACY = ROOT / 'docs/astra-city/government-import/government-xl-remaining-20260923/on-ning-terrain-diagnostic-20260925'


def verify(doc):
    hashes = {}
    def pinned(path):
        hashes[str(path.relative_to(ROOT))] = digest(path.read_bytes())
        return read(path)
    installed = pinned(LEGACY / 'installed-acceptance.json')
    assert installed['geometryChanges'] == installed['aiCalls'] == 0
    assert installed['supportResolutionSHA256'] == digest((LEGACY / 'support-resolution.json').read_bytes())
    support = pinned(LEGACY / 'support-resolution.json')
    assert [r for r in support['rows'] if r['uid'] == TOWER][0]['podiumUid'] == PODIUM
    assert [r for r in support['rows'] if r['uid'] == TOWER][0]['accepted']
    for filename, key in [('live-browser.json', 'liveBrowserSHA256'), ('staged-browser.json', 'stagedBrowserSHA256')]:
        browser = pinned(LEGACY / filename)
        assert hashes[str((LEGACY / filename).relative_to(ROOT))] == installed[key]
        assert browser['passed']
    catalogue = ROOT / '3d-viewer/city/data/official-models/government-xl-on-ning-20260925/catalogue.json'
    models = pinned(catalogue)
    assert digest(catalogue.read_bytes()) == installed['catalogueSHA256']
    tower = next(r for r in models['models'] if r['uid'] == TOWER)
    assert tower['sha256'] == installed['sourceSHA256s'][TOWER]
    assert all(tower.get(k) for k in ['sourceIdentityReviewed', 'identityReviewApproved', 'placementReviewed', 'publicationApproved'])
    asset = catalogue.parent / tower['asset']
    assert digest(asset.read_bytes()) == tower['sha256']
    hashes[str(asset.relative_to(ROOT))] = tower['sha256']
    manifest = pinned(ROOT / '3d-viewer/city/data/manifest.json')
    assert str(catalogue.relative_to(ROOT / '3d-viewer')) in manifest['officialModelCatalogues']
    assert not any(r['uid'] == PODIUM for url in manifest['officialModelCatalogues'] for r in read(ROOT / '3d-viewer' / url)['models'])
    assert not any(PODIUM in r.get('suppressesBuildingUids', []) for url in manifest['officialModelCatalogues'] for r in read(ROOT / '3d-viewer' / url)['models'])
    pointer = pinned(ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json')
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        review = con.execute('SELECT review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s', (pointer['snapshotId'], TOWER)).fetchone()
    assert review and review[:2] == ('installed-verified', tower['sha256'])
    assert (ROOT / review[2]['evidence']).resolve() == LEGACY / 'installed-acceptance.json'
    neighbours = pinned(doc / 'neighbour-inputs.json.gz')
    assert set(neighbours['candidateIds']) <= {'landsd/31718:0', 'landsd/34249:0'}
    current = next(r['building'] for r in neighbours['rows'] if r['building']['uid'] == PODIUM)
    assert current['buildingCSUID'] == '4513719625P20060323'
    original = read(LEGACY / 'neighbour-inputs.json.gz')
    assert current == next(r['building'] for r in original['rows'] if r['building']['uid'] == PODIUM)
    for path, sha in neighbours['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
        hashes[path] = sha
    hashes[str((HERE / 'on_ning_retained_basic_support.py').relative_to(ROOT))] = digest((HERE / 'on_ning_retained_basic_support.py').read_bytes())
    result = {'uid': TOWER, 'supportUid': PODIUM, 'supportCSUID': current['buildingCSUID'], 'towerSHA256': tower['sha256'], 'basicSourceUnchanged': True, 'snapshotId': pointer['snapshotId'], 'inputHashes': hashes, 'publication': False, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0}
    save(doc / 'retained-basic-support-proof.json', result)
    return result
